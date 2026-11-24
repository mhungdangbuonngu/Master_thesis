"""NCI-ALMANAC combinations from DrugComb v1.4 -> data/processed/almanac_triples.csv.

    python -m src.data.almanac

The external test set of planner 5.3 / 7.2. ALMANAC is taken from the SAME DrugComb v1.4
summary table as O'Neil rather than from the raw NCI release
(`ComboDrugGrowth_Nov2017.zip`), because the labels have to be comparable: DrugComb runs one
SynergyFinder pipeline over every study, so `synergy_loewe` here means exactly what it means
in the training labels. Recomputing Loewe from the raw percent-growth matrices would compare
our model against a different definition of the target.

DrugComb v1.4 has no study_name column, so the study is identified by its block range. The
60 NCI-60 cell lines and the 102 ALMANAC drugs are the only ones in blocks
132369..432467 (300,099 combination blocks, no monotherapy blocks); the range was found by
taking the cell and drug vocabulary of the middle of the study and growing the longest
contiguous run of blocks that uses nothing else.

Collapse, quality filter, canonical pair order and the three label settings are the same code
path as src.data.oneil, so a triple's label here is produced the same way as in training.
"""
import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.oneil import COLS, SCORES, labels

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "src" / "data" / "raw"
OUT = ROOT / "data" / "processed"

ALMANAC_FIRST_BLOCK = 132369
ALMANAC_LAST_BLOCK = 432467


def main(thr=10.0):
    cmap = pd.read_csv(ROOT / "src" / "data" / "cell_line_map_almanac.csv")
    usable = cmap[cmap.match != "none"]
    keep_cells = set(usable.drugcomb_name)

    parts, n_block_raw = [], 0
    for c in pd.read_csv(RAW / "summary_table_v1.4.csv", usecols=COLS, chunksize=500_000,
                         dtype={"drug_row": str, "drug_col": str}, low_memory=False):
        c = c[(c.block_id >= ALMANAC_FIRST_BLOCK) & (c.block_id <= ALMANAC_LAST_BLOCK)]
        if c.empty:
            continue
        n_block_raw += len(c)
        parts.append(c)
    d = pd.concat(parts, ignore_index=True)
    rep = {"blocks_in_almanac": int(n_block_raw)}

    d = d[d.drug_col.notna()]
    rep["blocks_combination"] = len(d)
    d = d[d.css.notna()]
    rep["blocks_with_css"] = len(d)

    a = np.minimum(d.drug_row, d.drug_col)
    b = np.maximum(d.drug_row, d.drug_col)
    d = d.assign(drug_a=a, drug_b=b)
    rep["cells_before_map"] = int(d.cell_line_name.nunique())
    rep["drugs_before_map"] = int(len(set(d.drug_a) | set(d.drug_b)))
    d = d[d.cell_line_name.isin(keep_cells)]
    rep["cells_after_map"] = int(d.cell_line_name.nunique())
    rep["cells_dropped"] = cmap[cmap.match == "none"].drugcomb_name.tolist()

    g = d.groupby(["drug_a", "drug_b", "cell_line_name"])
    t = g[[f"synergy_{s}" for s in SCORES]].median()
    t.columns = SCORES
    t["n_replicates"] = g.size()
    t["loewe_iqr"] = g["synergy_loewe"].quantile(0.75) - g["synergy_loewe"].quantile(0.25)
    t = t.reset_index()

    for s in SCORES:
        t[f"bin_gap_{s}"], t[f"bin_all_{s}"], t[f"ord3_{s}"] = labels(t[s], thr)
        for alt in (5.0, 20.0):
            t[f"ord3_{s}_t{alt:g}"] = labels(t[s], alt)[2]

    drugs = sorted(set(t.drug_a) | set(t.drug_b))
    cells = sorted(t.cell_line_name.unique())
    mod = pd.read_csv(RAW / "Model.csv", usecols=["ModelID", "OncotreeLineage"])
    lin = dict(zip(mod.ModelID, mod.OncotreeLineage))
    t["model_id"] = t.cell_line_name.map(dict(zip(cmap.drugcomb_name, cmap.model_id)))
    t["tissue"] = t.model_id.map(lin).fillna("unknown")

    OUT.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT / "almanac_triples.csv", index=False)

    rep.update({
        "date": str(date.today()), "threshold": thr,
        "triples": len(t), "drugs": len(drugs), "cells": len(cells),
        "pairs": int(t.groupby(["drug_a", "drug_b"]).ngroups),
        "replicates_per_triple_median": float(t.n_replicates.median()),
        "loewe_iqr_median": float(t.loewe_iqr.median()),
        "source": f"DrugComb v1.4 summary_table (zenodo 11102665), block_id "
                  f"{ALMANAC_FIRST_BLOCK}..{ALMANAC_LAST_BLOCK}",
        "drug_list": drugs, "cell_list": cells,
    })
    for s in SCORES:
        n_gap = int(t[f"bin_gap_{s}"].notna().sum())
        rep[f"labels_{s}"] = {
            "bin_gap_kept": n_gap, "bin_gap_dropped": len(t) - n_gap,
            "bin_gap_dropped_pct": round(100 * (len(t) - n_gap) / len(t), 1),
            "bin_gap_pos": int((t[f"bin_gap_{s}"] == 1).sum()),
            "bin_all_pos": int(t[f"bin_all_{s}"].sum()),
            "ord3": {int(k): int(v) for k, v in t[f"ord3_{s}"].value_counts().sort_index().items()},
            "ord3_pct": {int(k): round(100 * v, 1) for k, v in
                         t[f"ord3_{s}"].value_counts(normalize=True).sort_index().items()},
        }
    (OUT / "provenance_almanac.json").write_text(json.dumps(rep, indent=1))

    print(f"ALMANAC blocks {rep['blocks_in_almanac']} -> {rep['blocks_with_css']} usable")
    print(f"triples {len(t)}  drugs {len(drugs)}  cells {len(cells)}/{rep['cells_before_map']}  "
          f"pairs {rep['pairs']}  tissues {t.tissue.nunique()}")
    for s in SCORES:
        r = rep[f"labels_{s}"]
        print(f"  {s:6s} ord3 ant/add/syn % {r['ord3_pct']}")
    return t


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--thr", type=float, default=10.0)
    main(p.parse_args().thr)
