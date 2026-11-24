"""Train one run -> runs/<name>/{config,metrics}.json + model.pt + pred.npz  (planner 5.2).

    python -m src.train --model syngt --setting ord3_loewe --split leave_combo --fold 0 --seed 0

Everything a run needs is in its config.json, which is the reproducibility contract the
planner asks for. Expression is standardised per fold on TRAINING CELLS ONLY; validation is
the neighbouring fold of the same split unit, so model selection never sees a test drug or
test cell. Early stopping watches QWK (3-class) or AUPRC (binary), never loss or accuracy.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn

from src.data.batching import MolStore, permute_molecules
from src.eval import metrics as M
from src.model.corn import (CornHead, corn_loss, corn_loss_smooth, cost_loss, nominal_loss,
                            soft_targets)
from src.model.syngt import SynGT
from src.repro import baselines as B

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RUNS = ROOT / "runs"


def parse(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="syngt",
                   choices=["syngt", "deepdds", "deepsynergy", "onehot", "cell_only",
                            "drug_only", "majority"])
    p.add_argument("--setting", default="ord3_loewe")       # ord3_* | bin_gap_* | bin_all_*
    p.add_argument("--split", default="leave_combo")
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--loss", default="corn",
                   choices=["corn", "nominal", "cost", "corn_smooth"])
    p.add_argument("--tau", type=float, default=5.0, help="label-smoothing width, score units")
    # SynGT ablations (planner 5.3)
    p.add_argument("--gnn", default="gin", choices=["gin", "gcn"])
    p.add_argument("--no-fine", action="store_true")
    p.add_argument("--no-coarse", action="store_true")
    p.add_argument("--no-gene-emb", action="store_true")
    p.add_argument("--gene-emb", default="real", choices=["real", "rewired"])
    p.add_argument("--permute-smiles", action="store_true")
    p.add_argument("--n-gene-tokens", type=int, default=978)
    # Final SynGT (chosen on VALIDATION QWK of leave_combo folds 0-2, runs_diag/): skip
    # readout, no attention-probability dropout, Morgan-FP branch. Flags below switch them off.
    p.add_argument("--readout", default="skip", choices=["cls", "skip"])
    p.add_argument("--att-dropout", type=float, default=0.0)
    p.add_argument("--head-hidden", default="512,128")
    p.add_argument("--no-drug-fp", action="store_true", help="ablation: graph-only drugs")
    # optimisation
    p.add_argument("--d", type=int, default=128)
    p.add_argument("--gnn-layers", type=int, default=3)
    p.add_argument("--fine-layers", type=int, default=2)
    p.add_argument("--coarse-layers", type=int, default=2)
    p.add_argument("--heads", type=int, default=4)
    p.add_argument("--ff", type=int, default=256)
    p.add_argument("--dropout", type=float, default=0.3)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--wd", type=float, default=1e-4)
    p.add_argument("--batch", type=int, default=128)
    p.add_argument("--epochs", type=int, default=120)
    p.add_argument("--patience", type=int, default=20)
    p.add_argument("--no-class-weight", action="store_true")
    p.add_argument("--name", default="")
    p.add_argument("--amp", default="bf16", choices=["bf16", "off"])
    return p.parse_args(argv)


def run_name(a):
    bits = [a.model, a.setting, a.split, f"f{a.fold}", f"s{a.seed}"]
    if a.loss != "corn":
        bits.append(a.loss)
    for flag, tag in ((a.no_fine, "nofine"), (a.no_coarse, "nocoarse"),
                      (a.no_gene_emb, "nogeneemb"), (a.permute_smiles, "permsmiles")):
        if flag:
            bits.append(tag)
    if a.gnn != "gin":
        bits.append(a.gnn)
    if a.gene_emb != "real":
        bits.append("rewired")
    if a.model == "syngt" and a.readout != "skip":
        bits.append("clsreadout")
    if a.model == "syngt" and a.no_drug_fp:
        bits.append("nofp")
    return a.name or "_".join(bits)


def load_all(device):
    d = torch.load(PROC / "dataset.pt", weights_only=False)
    dr = torch.load(PROC / "drugs.pt", weights_only=False)
    ce = torch.load(PROC / "cells.pt", weights_only=False)
    sp = torch.load(PROC / "splits.pt", weights_only=False)
    return d, dr, ce, sp


def gene_order(ce, n):
    """Indices of the n most variable landmark genes (variance over all DepMap models)."""
    g = ce["expr"].shape[1]
    if n >= g:
        return torch.arange(g)
    return torch.sort(torch.topk(ce["gene_var_all_models"], n).indices).values


def standardise(expr, train_cells):
    """z-score per gene, fitted on training cells only (planner 4.2.3)."""
    mu = expr[train_cells].mean(0, keepdim=True)
    sd = expr[train_cells].std(0, keepdim=True).clamp_min(1e-6)
    return (expr - mu) / sd


def build_model(a, d, dr, ce, device, gene_emb):
    n_genes = gene_emb.shape[0]
    # corn_smooth is CORN with soft targets, so it keeps the 2-logit cumulative head
    head = ("binary" if a.setting.startswith("bin")
            else ("corn" if a.loss.startswith("corn") else "nominal"))
    if a.model == "syngt":
        m = SynGT(gene_emb, atom_dim=dr["atom_dim"], d=a.d, gnn_layers=a.gnn_layers, gnn=a.gnn,
                  fine_layers=a.fine_layers, coarse_layers=a.coarse_layers, heads=a.heads,
                  ff=a.ff, dropout=a.dropout, head=head,
                  use_fine=not a.no_fine, use_coarse=not a.no_coarse,
                  use_gene_emb=not a.no_gene_emb, readout=a.readout,
                  att_dropout=a.att_dropout,
                  head_hidden=tuple(int(v) for v in a.head_hidden.split(",")),
                  drug_fp=None if a.no_drug_fp else dr["fp2"])
    elif a.model == "deepdds":
        m = B.DeepDDS(dr["atom_dim"], n_genes, head=head, d=a.d, dropout=a.dropout)
    elif a.model == "deepsynergy":
        m = B.DeepSynergy(dr["fp3"], dr["desc"], n_genes, head=head, dropout=0.5)
    elif a.model == "onehot":
        m = B.OneHot(len(d["drugs"]), len(d["cells"]), head=head, dropout=a.dropout)
    elif a.model == "cell_only":
        m = B.CellOnly(n_genes, head=head, dropout=a.dropout)
    elif a.model == "drug_only":
        m = B.DrugOnly(dr["fp2"], head=head, dropout=a.dropout)
    else:
        m = B.Majority(head=head)
    return m.to(device)


def evaluate(model, store, expr, trip, y, idx, setting, batch, device, head_kind):
    model.eval()
    logits = []
    with torch.no_grad():
        for s in idx.split(batch):
            b = store.collate(trip[s], expr[trip[s][:, 2]])
            logits.append(model(b).float().cpu())
    lg = torch.cat(logits)
    yt = y[idx].cpu()
    if setting.startswith("bin"):
        prob = torch.sigmoid(lg[:, 0]).numpy()
        return M.binary(yt.numpy(), prob), {"prob": prob}
    prob = (CornHead.probs(lg) if head_kind == "corn" else lg.softmax(1)).numpy()
    pred = prob.argmax(1)
    return M.ord3(yt.numpy(), pred, prob), {"prob": prob, "pred": pred}


def main(a):
    t0 = time.time()
    torch.set_num_threads(2)   # many runs share 16 CPUs
    torch.manual_seed(a.seed)
    np.random.seed(a.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    d, dr, ce, sp = load_all(device)
    out = RUNS / run_name(a)
    out.mkdir(parents=True, exist_ok=True)

    trip = d["idx"].to(device)
    tr_i, va_i, te_i = sp["splits"][a.split][a.fold]
    y_all = d["y"][a.setting]

    # bin_gap drops the neutral band: those rows are NaN and must leave every subset
    if a.setting.startswith("bin_gap"):
        ok = ~torch.isnan(y_all)
        tr_i, va_i, te_i = [i[ok[i]] for i in (tr_i, va_i, te_i)]
        y = torch.nan_to_num(y_all).long()
    else:
        y = y_all.long()
    y = y.to(device)
    tr_i, va_i, te_i = tr_i.to(device), va_i.to(device), te_i.to(device)

    train_cells = torch.unique(trip[tr_i][:, 2]).cpu()
    # Gene-token budget: the fine transformer attends over (atoms + genes), so cost grows with
    # the gene count. When fewer tokens are asked for, keep the most variable genes ranked by
    # variance across ALL DepMap models - external to our 37 cells, so no leakage either way.
    gsel = gene_order(ce, a.n_gene_tokens)
    expr = standardise(ce["expr"], train_cells)[:, gsel].to(device)
    gene_emb = (ce["gene_emb"] if a.gene_emb == "real" else ce["gene_emb_rewired"])
    gene_emb = gene_emb[gsel].to(device)

    store = MolStore(dr, device)
    model = build_model(a, d, dr, ce, device, gene_emb)
    if a.permute_smiles:                     # null control: identity kept, chemistry destroyed
        permute_molecules(store, model)      # graphs AND the fingerprint buffer, one permutation
    head_kind = getattr(model, "head_kind", "corn")

    if a.setting.startswith("bin"):
        pos = y[tr_i].float().mean().clamp(1e-3, 1 - 1e-3)
        pw = ((1 - pos) / pos).to(device)
        def loss_fn(lg, yy, rows=None):
            return F.binary_cross_entropy_with_logits(lg[:, 0], yy.float(), pos_weight=pw)
        cw = None
    else:
        cnt = torch.bincount(y[tr_i], minlength=3).float()
        cw = None if a.no_class_weight else (cnt.sum() / (3 * cnt.clamp_min(1))).to(device)
        soft_all = None
        if a.loss == "corn_smooth":
            # thresholds of this setting, read off its name: ord3_<score>[_t5|_t20] -> +-5/10/20
            thr = 20.0 if a.setting.endswith("_t20") else (5.0 if a.setting.endswith("_t5") else 10.0)
            sc = d["score"][a.setting.split("_")[1]].to(device)
            soft_all = soft_targets(sc, [-thr, thr], a.tau)

            def loss_fn(lg, yy, rows):
                return corn_loss_smooth(lg, yy, cw, soft_all[rows])
        else:
            base = {"corn": corn_loss, "nominal": nominal_loss, "cost": cost_loss}[a.loss]

            def loss_fn(lg, yy, rows=None):
                return base(lg, yy, cw)

    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.wd)
    steps = max(1, -(-len(tr_i) // a.batch))                 # ceil; last batch may be partial
    total = a.epochs * steps
    warm = max(1, int(0.05 * total))

    def lr_at(step):                                         # warmup then cosine, no step cap
        if step < warm:
            return (step + 1) / warm
        p = min(1.0, (step - warm) / max(1, total - warm))
        return 0.5 * (1 + np.cos(np.pi * p))

    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_at)
    amp = torch.autocast("cuda", dtype=torch.bfloat16) if (a.amp == "bf16" and device == "cuda") \
        else torch.autocast("cpu", enabled=False)
    key = M.main_metric(a.setting)
    best, best_ep, bad, log = -1e9, -1, 0, []
    g = torch.Generator(device="cpu").manual_seed(a.seed)

    for ep in range(a.epochs):
        model.train()
        order = tr_i[torch.randperm(len(tr_i), generator=g).to(device)]
        tot = 0.0
        for s in order.split(a.batch):
            if len(s) < 2:
                continue
            b = store.collate(trip[s], expr[trip[s][:, 2]])
            with amp:
                lg = model(b)
                loss = loss_fn(lg.float(), y[s], s)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            tot += float(loss.detach()) * len(s)
        vm, _ = evaluate(model, store, expr, trip, y, va_i, a.setting, 512, device, head_kind)
        log.append({"epoch": ep, "train_loss": tot / max(len(tr_i), 1), f"val_{key}": vm[key]})
        if vm[key] > best:
            best, best_ep, bad = vm[key], ep, 0
            torch.save(model.state_dict(), out / "model.pt")
        else:
            bad += 1
            if bad >= a.patience:
                break

    model.load_state_dict(torch.load(out / "model.pt", map_location=device))
    test, extra = evaluate(model, store, expr, trip, y, te_i, a.setting, 512, device, head_kind)
    val, _ = evaluate(model, store, expr, trip, y, va_i, a.setting, 512, device, head_kind)

    np.savez_compressed(out / "pred.npz", test_idx=te_i.cpu().numpy(),
                        y=y[te_i].cpu().numpy(), **{k: v for k, v in extra.items()})
    cfg = {**vars(a), "run": out.name, "n_params": sum(p.numel() for p in model.parameters()),
           "n_train": len(tr_i), "n_val": len(va_i), "n_test": len(te_i),
           "train_cells": len(train_cells), "best_epoch": best_ep, "epochs_run": len(log),
           "class_weight": None if cw is None else cw.tolist(), "seconds": time.time() - t0,
           "device": device, "gene_tokens": int(expr.shape[1])}
    (out / "config.json").write_text(json.dumps(cfg, indent=1))
    (out / "metrics.json").write_text(json.dumps({"test": test, "val": val, "log": log}, indent=1))
    print(f"{out.name}  val_{key} {val[key]:.4f}  test_{key} {test[key]:.4f}  "
          f"({len(log)} ep, {time.time() - t0:.0f}s)")
    return test


if __name__ == "__main__":
    main(parse())
