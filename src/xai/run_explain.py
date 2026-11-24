"""Explain one trained SynGT -> runs/<run>/explain.pt  (planner 6.1-6.3).

    python -m src.xai.run_explain --run syngt_ord3_loewe_leave_combo_f0_s0 [--n 50]

Explained triples: `n` true-syn and `n` true-ant triples of that run's TEST fold, drawn with
an rng fixed by (split, fold) so every seed and every ablation explains the same triples -
a precondition for the stability metric (planner 6.3).

Per triple it records, for each of the three attribution targets (logit / contrast / ant):
  * IG over the 944 gene masks and over the BRICS fragment masks, with the completeness gap
  * Fid+ and Fid- at two sparsity levels, each with 20 matched random deletions as the null
  * the single-unit deletion effect of every top-k unit, which the Faithfulness Violation
    Test compares against the attribution
and once per triple:
  * the exact second-order fragment-pair interaction matrix (contrast target)
  * fine-transformer atom<->gene attention and coarse attention, averaged over heads/layers
  * a GNNExplainer-style optimised fragment mask, as a second explainer
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from src.data.batching import MolStore, permute_molecules
from src.model.corn import CornHead
from src.train import RUNS, build_model, load_all, parse as parse_train, standardise
from src.xai import masks as K

PROC = Path(__file__).resolve().parents[2] / "data" / "processed"
K_GENE = [0.10, 0.25]          # Fid+ sparsity levels on genes
K_FRAG = [1, 2]                # fragments switched off
N_RAND = 10                    # random deletions per level (the Fid null)
FVT_TOPK = 10                  # units probed one at a time for the violation test


def load_run(run, device):
    cfg = json.loads((RUNS / run / "config.json").read_text())
    a = parse_train(["--model", cfg["model"], "--setting", cfg["setting"],
                     "--split", cfg["split"], "--fold", str(cfg["fold"]),
                     "--seed", str(cfg["seed"])])
    for k in ("d", "gnn_layers", "fine_layers", "coarse_layers", "heads", "ff", "dropout",
              "gnn", "no_fine", "no_coarse", "no_gene_emb", "gene_emb", "loss",
              "n_gene_tokens", "permute_smiles", "readout", "att_dropout",
              "head_hidden", "no_drug_fp"):
        if k in cfg:
            setattr(a, k, cfg[k])
    d, dr, ce, sp = load_all(device)
    tr_i, va_i, te_i = sp["splits"][a.split][a.fold]
    train_cells = torch.unique(d["idx"][tr_i][:, 2])
    expr = standardise(ce["expr"], train_cells)[:, :a.n_gene_tokens].to(device)
    gene_emb = (ce["gene_emb"] if a.gene_emb == "real" else ce["gene_emb_rewired"])
    gene_emb = gene_emb[:a.n_gene_tokens].to(device)
    model = build_model(a, d, dr, ce, device, gene_emb)
    model.load_state_dict(torch.load(RUNS / run / "model.pt", map_location=device))
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    # The store is built here, not by the caller, so that a permuted-SMILES run is explained
    # with the molecules it was TRAINED on. Both callers used to build their own unpermuted
    # store, which would have silently attributed the real chemistry of a model that never saw
    # it. model=None: `drug_fp` is a persistent buffer and came back permuted from the
    # checkpoint above, so permuting it again here would undo the control.
    store = MolStore(dr, device)
    if a.permute_smiles:
        permute_molecules(store, None)
    return a, cfg, model, d, dr, ce, expr, store, (tr_i, va_i, te_i)


# Stable per-split offsets for the triple-sampling rng. This used to be `hash(split) % 1000`,
# which looks deterministic but is not: Python salts string hashes per process unless
# PYTHONHASHSEED is set, and it was not set anywhere. Every `run_explain` invocation is its own
# process, so each one drew a DIFFERENT sample of triples. Seeds 0/1/2 of the same fold ended up
# sharing 0 to 2 triples out of 40, which silently turned the cross-seed and cross-convention
# stability tables into comparisons between explanations of unrelated triples.
SPLIT_RNG_OFFSET = {"random": 0, "leave_combo": 1, "leave_drug": 2,
                    "leave_cell": 3, "leave_tumor": 4}


def pick_triples(d, te_i, setting, n, split, fold):
    """n true-syn and n true-ant test triples, drawn with an rng keyed by (split, fold).

    `setting` decides which labels define "syn" and "ant". Passing a REFERENCE setting here
    (--ref-setting) instead of the run's own makes every label convention explain the same
    triples, which is what the cross-convention stability comparison of RQ5 needs: otherwise
    each convention samples from its own class membership and the two samples barely overlap.

    The rng must therefore depend on (split, fold) and on NOTHING ELSE, process-local state
    included - see SPLIT_RNG_OFFSET for how that was broken.
    """
    y = d["y"][setting]
    rng = np.random.default_rng(10_000 + 97 * fold + 1000 * SPLIT_RNG_OFFSET[split])
    out = {}
    for name, cls in (("syn", 2), ("ant", 0)):
        cand = te_i[(y[te_i] == cls)].numpy()
        out[name] = np.sort(rng.choice(cand, min(n, len(cand)), replace=False)) if len(cand) else np.array([])
    return out


def gnn_explainer_fragments(model, batch, store, which="contrast", steps=200, lam=0.05, lr=0.1):
    """GNNExplainer in spirit: optimise a soft fragment mask to keep the target high and sparse."""
    fa, nf, _, _ = K.fragment_layout(batch, store)
    p = torch.zeros(nf, device=batch["expr"].device, requires_grad=True)
    opt = torch.optim.Adam([p], lr=lr)
    with torch.no_grad():
        f1 = float(K.target_scalar(model, model(batch), which))
    for _ in range(steps):
        mu = torch.sigmoid(p)
        out = K.target_scalar(model, model(batch, mu_atom=mu[fa]), which).sum()
        loss = -out + lam * mu.mean() + lam * (-mu * (mu + 1e-9).log()).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return torch.sigmoid(p).detach(), f1


def explain_one(model, store, batch, rng, device, light=False):
    """All attributions and fidelity numbers for a single triple."""
    rec = {}
    n_gene = batch["expr"].shape[1]
    fa, nf, nf_per_mol, off = K.fragment_layout(batch, store)

    with torch.no_grad():
        logits = model(batch)
        probs = CornHead.probs(logits.float()) if model.head_kind == "corn" else logits.softmax(1)
    rec["pred"] = int(probs.argmax())
    rec["prob"] = probs[0].cpu()
    rec["n_frag"] = [int(nf_per_mol[0]), int(nf_per_mol[1])]

    for which in K.TARGETS:
        g_attr, g1, g0, g_gap = K.ig(model, batch, which, "gene", steps=32)
        f_attr, a1, a0, f_gap = K.ig(model, batch, which, "frag", steps=32, store=store)
        rec[f"gene_attr_{which}"] = g_attr.cpu().half()
        rec[f"frag_attr_{which}"] = f_attr.cpu()
        rec[f"gap_{which}"] = {"gene": g_gap, "frag": f_gap, "f1": g1, "f0": g0}

        # ---- Fid+ / Fid- with matched random nulls
        for lvl in K_GENE:
            k = max(1, int(lvl * n_gene))
            with torch.no_grad():
                top = float(K.target_scalar(model, K.delete_topk(model, batch, g_attr, k, "gene"), which))
                keep = float(K.target_scalar(model, K.delete_topk(model, batch, g_attr, k, "gene", keep=True), which))
                rnd = [float(K.target_scalar(model, K.delete_random(model, batch, k, "gene", rng), which))
                       for _ in range(N_RAND)]
            rec[f"fid_gene_{which}_{lvl}"] = {"full": g1, "del_top": top, "keep_top": keep,
                                              "del_rand": rnd}
        for k in K_FRAG:
            if k >= nf:
                continue
            with torch.no_grad():
                top = float(K.target_scalar(model, K.delete_topk(model, batch, f_attr, k, "frag", store), which))
                rnd = [float(K.target_scalar(model, K.delete_random(model, batch, k, "frag", rng, store), which))
                       for _ in range(N_RAND)]
            rec[f"fid_frag_{which}_{k}"] = {"full": a1, "del_top": top, "del_rand": rnd}

        # ---- single-unit deletion effects for the Faithfulness Violation Test
        topk = torch.topk(g_attr, min(FVT_TOPK, n_gene)).indices
        eff = []
        with torch.no_grad():
            for i in topk.tolist():
                mu = torch.ones(n_gene, device=device)
                mu[i] = 0.0
                eff.append(g1 - float(K.target_scalar(model, model(batch, mu_gene=mu), which)))
        rec[f"fvt_{which}"] = {"idx": topk.cpu(), "attr": g_attr[topk].cpu(),
                               "effect": torch.tensor(eff)}

    # ---- graph vs fingerprint branch (the main model has both; planner 6.1)
    if K.has_fp(model):
        rec["graph_vs_fp"] = {w: K.graph_vs_fp(model, batch, store, w) for w in K.TARGETS}

    # ---- pair-level mechanism: exact second-order fragment interaction
    phi, f_all, fi, fj = K.fragment_interaction(model, batch, store, "contrast")
    rec["frag_phi"] = phi
    rec["frag_single"] = (fi, fj)

    # ---- attention (the thing DTSyn, MD-Syn and AttenSyn present as the explanation)
    with torch.no_grad():
        _, w = model(batch, need_weights=True)
    if w["fine"]:
        a0_, a1_ = model.last_atom_slice
        g0_, g1_ = model.last_gene_slice
        att = torch.stack([x[0].mean(0) for x in w["fine"]]).mean(0)      # mean over heads+layers
        rec["att_atom_gene"] = att[a0_:a1_, g0_:g1_].cpu().half()
        rec["att_cls_gene"] = att[0, g0_:g1_].cpu()
        rec["att_cls_atom"] = att[0, a0_:a1_].cpu()
    if w["coarse"]:
        rec["att_coarse"] = torch.stack([x[0].mean(0) for x in w["coarse"]]).mean(0).cpu()

    # ---- second explainer (skipped in --light mode)
    if not light:
        ge_mask, _ = gnn_explainer_fragments(model, batch, store, "contrast")
        rec["gnnexp_frag"] = ge_mask.cpu()
    return rec


def main(a):
    t0 = time.time()
    torch.set_num_threads(2)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg_a, cfg, model, d, dr, ce, expr, store, (tr_i, va_i, te_i) = load_run(a.run, device)
    trip = d["idx"].to(device)
    label_setting = a.ref_setting or cfg["setting"]
    sel = pick_triples(d, te_i, label_setting, a.n, cfg["split"], cfg["fold"])

    out = {"run": a.run, "config": cfg, "label_setting": label_setting,
           "idx": {k: v.tolist() for k, v in sel.items()},
           "genes": ce["genes"], "drugs": d["drugs"], "cells": d["cells"], "records": {}}
    rng = np.random.default_rng(cfg["seed"])
    n_done = 0
    for cls, ids in sel.items():
        recs = []
        for i in ids:
            b = store.collate(trip[int(i)][None], expr[trip[int(i)][None][:, 2]])
            recs.append(explain_one(model, store, b, rng, device, a.light))
            n_done += 1
            if n_done % 20 == 0:
                print(f"  {n_done} triples, {time.time() - t0:.0f}s", flush=True)
        out["records"][cls] = recs
    out["seconds"] = time.time() - t0
    fname = "explain_ref.pt" if a.ref_setting and a.ref_setting != cfg["setting"] else "explain.pt"
    torch.save(out, RUNS / a.run / fname)
    print(f"{a.run}: explained {n_done} triples in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--n", type=int, default=40)
    p.add_argument("--light", action="store_true", help="skip GNNExplainer (cheaper)")
    p.add_argument("--ref-setting", default="",
                   help="pick the explained triples by THIS setting's labels (RQ5 cross-"
                        "convention); output goes to explain_ref.pt instead of explain.pt")
    main(p.parse_args())
