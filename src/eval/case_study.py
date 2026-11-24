"""Positive-control case studies, chosen BEFORE any explanation was run (planner 6.4).

    python -m src.eval.case_study

The pairs, the cell lines and the expected KEGG pathways below are fixed in this file and
must not be edited after looking at results - that is the whole point of declaring them up
front. The first pair is DTSyn's own worked example, so its explanation can be compared
against what that paper published for the same pair and the same two cell lines.

Each (pair, cell) is explained with the 3 seeds of the fold whose TEST set holds the pair,
so no model being interrogated ever saw that drug combination in training. Scored on:
  own targets   are the two drugs' known target genes in the top-k?
  KEGG          is the declared pathway enriched in the top-k? (hypergeometric)
  null          random gene sets matched on expression decile
  DTSyn genes   rank of the five genes DTSyn highlighted for ETOPOSIDE + MK-2206
A failure is reported as a failure: the planner requires at least one.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from src.eval import xai_metrics as X
from src.train import RUNS
from src.xai.run_explain import explain_one, load_run

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "tables"
K = 50

# (drug A, drug B, cells of interest, expected KEGG pathways, note)
PAIRS = [
    ("ETOPOSIDE", "MK-2206", ["CAOV3", "NCIH23"],
     ["hsa04151", "hsa04110"],
     "DTSyn's worked example (their Fig. 6-7): syn in CAOV3, ant in NCIH23. "
     "MK-2206 inhibits AKT (PI3K-Akt), etoposide poisons TOP2A (cell cycle / DNA damage)."),
    ("MK-2206", "MK-8669", ["A2058", "A2780"],
     ["hsa04151", "hsa04150"],
     "MD-Syn's worked example (they highlight PAK6). AKT + mTOR, two nodes of one pathway."),
    ("PD325901", "MK-2206", ["A2058", "A375"],
     ["hsa04010", "hsa04151"],
     "MEK + AKT, the textbook vertical-pathway combination; syn in 10 cells and ant in 4, "
     "so synergy and antagonism can be compared inside one pair (RQ6)."),
    ("AZD1775", "MK-8776", ["A2058", "SW-620"],
     ["hsa04110"],
     "WEE1 + CHK1, both cell-cycle checkpoint kinases; the most consistently synergistic "
     "pair in O'Neil (28 of 37 cell lines)."),
]

# The five genes DTSyn reported as having high interaction coefficients for pair 1.
DTSYN_GENES = ["SNAP25", "GALE", "PRKCD", "PIK3R3", "DDIT4"]
CLASS_NAME = {0: "antagonistic", 1: "additive", 2: "synergistic"}


def fold_of_pair(d, sp, ia, ib):
    """The leave_combo fold whose TEST set contains this pair."""
    pair = d["pair"]
    m = (pair[:, 0] == ia) & (pair[:, 1] == ib)
    rows = torch.nonzero(m).flatten()
    for f, (_, _, te) in enumerate(sp["splits"]["leave_combo"]):
        if len(set(rows.tolist()) & set(te.tolist())):
            return f
    return None


def main(seeds=(0, 1, 2), k=K):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sets, pw_names = X.kegg_sets()
    tg = X.drug_targets()
    rows, gene_rows = [], []

    sp = torch.load(ROOT / "data" / "processed" / "splits.pt", weights_only=False)
    d0 = torch.load(ROOT / "data" / "processed" / "dataset.pt", weights_only=False)
    drugs, cells = d0["drugs"], d0["cells"]
    y = d0["y"]["ord3_loewe"]

    for a_name, b_name, cell_names, pws, note in PAIRS:
        if a_name not in drugs or b_name not in drugs:
            rows.append({"pair": f"{a_name} + {b_name}", "status": "drug missing"})
            continue
        ia, ib = sorted([drugs.index(a_name), drugs.index(b_name)])
        fold = fold_of_pair(d0, sp, ia, ib)
        if fold is None:
            rows.append({"pair": f"{a_name} + {b_name}", "status": "pair in no test fold"})
            continue
        want = set().union(*(sets.get(p, set()) for p in pws))
        targets = tg.get(a_name, set()) | tg.get(b_name, set())

        for cell_name in cell_names:
            if cell_name not in cells:
                continue
            ic = cells.index(cell_name)
            sel = torch.nonzero((d0["idx"][:, 0] == ia) & (d0["idx"][:, 1] == ib)
                                & (d0["idx"][:, 2] == ic)).flatten()
            if not len(sel):
                continue
            row_id = int(sel[0])
            label = int(y[row_id])

            per_seed = []
            for seed in seeds:
                run = f"syngt_ord3_loewe_leave_combo_f{fold}_s{seed}"
                if not (RUNS / run / "model.pt").exists():
                    continue
                a, cfg, model, d, dr, ce, expr, store, _ = load_run(run, device)
                trip = d["idx"].to(device)
                b = store.collate(trip[row_id][None], expr[trip[row_id][None][:, 2]])
                rec = explain_one(model, store, b, np.random.default_rng(seed), device, light=True)
                per_seed.append((rec, ce["genes"], expr.cpu().numpy()))
            if not per_seed:
                continue

            genes = per_seed[0][1]
            attr = np.mean([np.asarray(r["gene_attr_contrast"], dtype=float) for r, _, _ in per_seed], 0)
            order = np.argsort(-attr)[:k]
            top = [genes[i] for i in order]
            preds = [CLASS_NAME[r["pred"]] for r, _, _ in per_seed]

            p_kegg, hit_kegg = X.enrichment(top, want, genes)
            p_tgt, hit_tgt = X.enrichment(top, targets, genes)
            # null: expression-decile matched random sets
            expr_m = per_seed[0][2].mean(0)
            dec = np.digitize(expr_m, np.quantile(expr_m, np.linspace(0.1, 0.9, 9)))
            rng = np.random.default_rng(0)
            null_p = []
            for _ in range(200):
                pick = [int(rng.choice(np.flatnonzero(dec == dd))) for dd in dec[order]]
                null_p.append(X.enrichment([genes[i] for i in pick], want, genes)[0])
            phi = np.mean([np.asarray(r["frag_phi"]) for r, _, _ in per_seed], 0)

            rows.append({
                "pair": f"{a_name} + {b_name}", "cell": cell_name, "fold": fold,
                "label": CLASS_NAME[label], "predicted": "/".join(preds),
                "correct": all(p == CLASS_NAME[label] for p in preds),
                "kegg": "+".join(pws), "kegg_genes_on_panel": len(want & set(genes)),
                "kegg_hits_in_top": hit_kegg, "kegg_p": p_kegg,
                "kegg_p_null_median": float(np.median(null_p)),
                "beats_null": bool(p_kegg < np.percentile(null_p, 5)),
                "targets_on_panel": len(targets & set(genes)),
                "target_hits_in_top": hit_tgt, "target_p": p_tgt,
                "frag_phi_max": float(np.abs(phi).max()),
                "frag_phi_mean_abs": float(np.abs(phi).mean()),
                "n_seeds": len(per_seed), "note": note})
            for rank, i in enumerate(order[:15]):
                gene_rows.append({"pair": f"{a_name} + {b_name}", "cell": cell_name,
                                  "rank": rank + 1, "gene": genes[i], "attr": float(attr[i]),
                                  "in_kegg": genes[i] in want, "is_target": genes[i] in targets,
                                  "dtsyn_reported": genes[i] in DTSYN_GENES})
            if a_name == "ETOPOSIDE":        # direct comparison with DTSyn's published genes
                ranks = {g: (int(np.flatnonzero(np.argsort(-attr) == genes.index(g))[0]) + 1
                             if g in genes else None) for g in DTSYN_GENES}
                rows[-1]["dtsyn_gene_ranks"] = json.dumps(ranks)

    OUT.mkdir(parents=True, exist_ok=True)
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "case_study.csv", index=False)
    pd.DataFrame(gene_rows).to_csv(OUT / "case_genes.csv", index=False)
    cols = [c for c in ["pair", "cell", "label", "predicted", "correct", "kegg_hits_in_top",
                        "kegg_p", "kegg_p_null_median", "beats_null", "target_hits_in_top"]
            if c in t]
    print(t[cols].to_string(index=False) if len(t) else "no case studies produced")
    return t


if __name__ == "__main__":
    main()
