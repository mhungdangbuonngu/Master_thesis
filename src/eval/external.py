"""Zero-shot scoring of a trained run on NCI-ALMANAC  (planner 5.3, 7.2).

    python -m src.eval.external --run syngt_ord3_loewe_random_f0_s0
    python -m src.eval.external --all "syngt_ord3_loewe_random_f*_s0" --workers 3

Nothing is retrained and nothing is fitted on ALMANAC. The run's own checkpoint is loaded and
the external triples are pushed through it, which is the only honest reading of "external":
  * the z-score for ALMANAC expression uses the mean and sd of the O'NEIL TRAINING cells of
    this run's fold, never ALMANAC's own statistics
  * the gene-token subset is `gene_order()` on the O'Neil variance vector, as in training
  * the drug-indexed buffers (Morgan fp for SynGT, fp3 + descriptors for DeepSynergy) are
    swapped for ALMANAC's AFTER load_state_dict, so the checkpoint still loads with the
    shapes it was saved with
Models with a drug or cell lookup table (onehot, drug_only) cannot transfer and are refused.

Metrics are reported on the whole external set and on the subsets that remove the overlap
with O'Neil: ALMANAC shares 9 cell lines and 23 compounds with it. `syn_vs_rest` is the
binary view for comparison with DTSyn's published external BACC.
"""
import argparse
import fnmatch
import json
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import torch

from src.data.batching import MolStore
from src.eval import metrics as M
from src.model.corn import CornHead
from src.train import RUNS, build_model, gene_order, load_all, parse as train_parse

PROC = Path(__file__).resolve().parents[2] / "data" / "processed"
CANNOT_TRANSFER = ("onehot", "drug_only", "majority")


def cfg_namespace(cfg):
    """config.json -> the Namespace build_model expects (defaults fill keys added later)."""
    a = train_parse([])
    for k, v in cfg.items():
        if hasattr(a, k):
            setattr(a, k, v)
    return a


def subsets(ext, y, ok):
    """Named row masks. `ok` already drops rows this setting has no label for."""
    seen_pair, seen_cell = ext["seen_pair"], ext["seen_cell"]
    both = ext["seen_drug_a"] & ext["seen_drug_b"]
    return {"all": ok,
            "unseen_pair": ok & ~seen_pair,
            "unseen_cell": ok & ~seen_cell,
            "unseen_pair_and_cell": ok & ~seen_pair & ~seen_cell,
            "new_chemistry": ok & ~both,          # at least one drug absent from O'Neil
            # the control subset: both studies ran this exact experiment
            "measured_by_both": ok & (ext["oneil_ord3_loewe"] >= 0)}


def score_one(run, device="cpu", batch=512):
    t0 = time.time()
    out = RUNS / run
    cfg = json.loads((out / "config.json").read_text())
    if cfg["model"] in CANNOT_TRANSFER:
        raise SystemExit(f"{run}: model '{cfg['model']}' has a drug/cell lookup table, "
                         f"so it has nothing to say about unseen drugs or cells")
    if cfg.get("permute_smiles"):
        raise SystemExit(f"{run}: permuted-SMILES control, not a model to validate")
    a = cfg_namespace(cfg)
    torch.set_num_threads(2)

    d, dr, ce, sp = load_all(device)
    ext = torch.load(PROC / "almanac.pt", weights_only=False)

    tr_i = sp["splits"][a.split][a.fold][0]
    train_cells = torch.unique(d["idx"][tr_i][:, 2])
    mu = ce["expr"][train_cells].mean(0, keepdim=True)
    sd = ce["expr"][train_cells].std(0, keepdim=True).clamp_min(1e-6)
    gsel = gene_order(ce, a.n_gene_tokens)
    expr = (((ext["expr"] - mu) / sd)[:, gsel]).to(device)
    gene_emb = (ce["gene_emb"] if a.gene_emb == "real" else ce["gene_emb_rewired"])[gsel].to(device)

    model = build_model(a, d, dr, ce, device, gene_emb)
    model.load_state_dict(torch.load(out / "model.pt", map_location=device))
    # drug-indexed buffers must become ALMANAC's, and only after the checkpoint is in
    if getattr(model, "drug_fp", None) is not None:
        model.drug_fp = ext["fp2"].float().to(device)
    if cfg["model"] == "deepsynergy":
        model.fp = ext["fp3"].float().to(device)
        model.desc = ext["desc"].float().to(device)
    model.eval()
    head_kind = getattr(model, "head_kind", "corn")

    store = MolStore(ext, device)
    trip = ext["idx"].to(device)
    y_all = ext["y"][a.setting]
    ok = ~torch.isnan(y_all) if a.setting.startswith("bin_gap") else torch.ones(len(trip), dtype=torch.bool)
    y = torch.nan_to_num(y_all).long()

    logits = []
    with torch.no_grad():
        for s in torch.arange(len(trip)).split(batch):
            b = store.collate(trip[s], expr[trip[s][:, 2]])
            logits.append(model(b).float().cpu())
    lg = torch.cat(logits)

    res = {"run": run, "model": cfg["model"], "loss": cfg["loss"], "setting": a.setting,
           "split": a.split, "fold": a.fold, "seed": a.seed, "n_external": int(len(trip)),
           "seconds": round(time.time() - t0, 1)}
    if a.setting.startswith("bin"):
        prob = torch.sigmoid(lg[:, 0]).numpy()
        extra = {"prob": prob}
        for name, m in subsets(ext, y, ok).items():
            i = m.numpy()
            res[name] = {"n": int(i.sum()), **M.binary(y.numpy()[i], prob[i])}
    else:
        prob = (CornHead.probs(lg) if head_kind == "corn" else lg.softmax(1)).numpy()
        pred = prob.argmax(1)
        extra = {"prob": prob, "pred": pred}
        yn = y.numpy()
        sub = subsets(ext, y, ok)
        for name, m in sub.items():
            i = m.numpy()
            r = {"n": int(i.sum()), **M.ord3(yn[i], pred[i], prob[i])}
            syn, hit = yn[i] == 2, pred[i] == 2
            tp, fn = int((syn & hit).sum()), int((syn & ~hit).sum())
            tn, fp = int((~syn & ~hit).sum()), int((~syn & hit).sum())
            r["syn_vs_rest"] = {**M.binary(syn.astype(int), prob[i][:, 2]),
                                "bacc_argmax": 0.5 * (tp / max(tp + fn, 1) + tn / max(tn + fp, 1))}
            res[name] = r
        # The control: on the triples both studies ran, score the SAME predictions against
        # O'Neil's label instead of ALMANAC's. A pipeline that scores near zero here is
        # broken; a pipeline that scores well here and near zero against ALMANAC's label is
        # measuring how little the two studies agree about the same experiment.
        i = sub["measured_by_both"].numpy()
        yo = ext["oneil_ord3_loewe"].numpy()[i]
        res["measured_by_both_vs_oneil_label"] = {"n": int(i.sum()),
                                                  **M.ord3(yo, pred[i], prob[i])}
    np.savez_compressed(out / "pred_almanac.npz", **extra)
    (out / "external_almanac.json").write_text(json.dumps(res, indent=1))
    k = M.main_metric(a.setting)
    print(f"{run:52s} almanac_{k} {res['all'][k]:.4f}  "
          f"unseen_pair {res['unseen_pair'][k]:.4f}  ({res['seconds']:.0f}s)")
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", default="")
    p.add_argument("--all", default="", help="glob over runs/ (quote it)")
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--batch", type=int, default=512)
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = p.parse_args()
    if a.run:
        score_one(a.run, a.device, a.batch)
        return
    runs = sorted(r.name for r in RUNS.iterdir()
                  if r.is_dir() and (r / "model.pt").exists() and fnmatch.fnmatch(r.name, a.all))
    print(f"{len(runs)} runs")
    if a.workers <= 1:
        for r in runs:
            score_one(r, a.device, a.batch)
        return
    # spawn, not fork: a forked child cannot re-initialise CUDA ("Cannot re-initialize CUDA
    # in forked subprocess") once the parent has touched the GPU
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(a.workers, mp_context=ctx) as ex:
        list(ex.map(score_one, runs, [a.device] * len(runs), [a.batch] * len(runs)))


if __name__ == "__main__":
    main()
