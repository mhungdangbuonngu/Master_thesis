"""O'Neil combinations from DrugComb v1.4 -> data/processed/triples.csv  (planner 3.1, 4.3).

    python -m src.data.oneil

DrugComb v1.4 has no study_name column. O'Neil is the first study in the file: block_id
1..92208 (the next block starts the KBM-7 study). Each triple appears as several blocks
(replicates, and both drug orders), so blocks are collapsed to one row per
(drug_a, drug_b, cell) with the MEDIAN of each synergy score, keeping the spread so the
thesis can report label noise.

Writes the four synergy scores and the three label settings of planner 3.3:
  (a) bin_gap   score > 10 -> 1, score < 0 -> 0, 0 <= score <= 10 -> NA   (DTSyn's protocol)
  (b) bin_all   score > 10 -> 1, else 0                                   (keeps everything)
  (c) ord3      score > 10 -> 2 syn, -10..10 -> 1 add, score < -10 -> 0 ant
"""
import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "src" / "data" / "raw"
OUT = ROOT / "data" / "processed"

ONEIL_LAST_BLOCK = 92208
SCORES = ["loewe", "bliss", "zip", "hsa"]
COLS = ["block_id", "drug_row", "drug_col", "cell_line_name", "css"] + [f"synergy_{s}" for s in SCORES]
ANT, ADD, SYN = 0, 1, 2


def labels(score, thr=10.0):
    """The three label settings on one synergy score column."""
    bin_gap = pd.Series(np.where(score > thr, 1.0, np.where(score < 0, 0.0, np.nan)), index=score.index)
    bin_all = (score > thr).astype(int)
    ord3 = pd.Series(np.where(score > thr, SYN, np.where(score < -thr, ANT, ADD)), index=score.index)
    return bin_gap, bin_all, ord3


def main(thr=10.0):
    cmap = pd.read_csv(ROOT / "src" / "data" / "cell_line_map.csv")
    cmap = cmap[cmap.match != "none"]
    keep_cells = set(cmap.drugcomb_name)

    chunks = pd.read_csv(RAW / "summary_table_v1.4.csv", usecols=COLS, chunksize=500_000,
                         dtype={"drug_row": str, "drug_col": str}, low_memory=False)
    parts = []
    n_block_raw = 0
    for c in chunks:                                    # 193 MB file, 50 GiB RAM cap -> stream
        c = c[c.block_id <= ONEIL_LAST_BLOCK]
        if c.empty:
            continue
        n_block_raw += len(c)
        parts.append(c)
    d = pd.concat(parts, ignore_index=True)
    rep = {"blocks_in_oneil": int(n_block_raw)}

    d = d[d.drug_col.notna()]                           # drop monotherapy blocks
    rep["blocks_combination"] = len(d)
    d = d[d.css.notna()]                                # quality filter (planner 4.3.5)
    rep["blocks_with_css"] = len(d)

    # canonical pair order so (A,B) and (B,A) land in the same triple
    a = np.minimum(d.drug_row, d.drug_col)
    b = np.maximum(d.drug_row, d.drug_col)
    d = d.assign(drug_a=a, drug_b=b)
    rep["cells_before_map"] = d.cell_line_name.nunique()
    d = d[d.cell_line_name.isin(keep_cells)]
    rep["cells_after_map"] = int(d.cell_line_name.nunique())

    g = d.groupby(["drug_a", "drug_b", "cell_line_name"])
    t = g[[f"synergy_{s}" for s in SCORES]].median()
    t.columns = SCORES
    t["n_replicates"] = g.size()
    t["loewe_iqr"] = g["synergy_loewe"].quantile(0.75) - g["synergy_loewe"].quantile(0.25)
    t = t.reset_index()

    for s in SCORES:
        t[f"bin_gap_{s}"], t[f"bin_all_{s}"], t[f"ord3_{s}"] = labels(t[s], thr)
        for alt in (5.0, 20.0):                         # sensitivity grid (planner 3.3)
            t[f"ord3_{s}_t{alt:g}"] = labels(t[s], alt)[2]

    drugs = sorted(set(t.drug_a) | set(t.drug_b))
    cells = sorted(t.cell_line_name.unique())
    # tissue for the leave-tumor-out split: DepMap OncotreeLineage via the curated cell map
    mod = pd.read_csv(RAW / "Model.csv", usecols=["ModelID", "OncotreeLineage"])
    lin = dict(zip(mod.ModelID, mod.OncotreeLineage))
    t["model_id"] = t.cell_line_name.map(dict(zip(cmap.drugcomb_name, cmap.model_id)))
    t["tissue"] = t.model_id.map(lin).fillna("unknown")

    OUT.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT / "triples.csv", index=False)

    rep.update({
        "date": str(date.today()), "threshold": thr,
        "triples": len(t), "drugs": len(drugs), "cells": len(cells),
        "replicates_per_triple_median": float(t.n_replicates.median()),
        "loewe_iqr_median": float(t.loewe_iqr.median()),
        "source": "DrugComb v1.4 summary_table (zenodo 11102665), block_id <= 92208",
        "drug_list": drugs, "cell_list": cells,
    })
    for s in SCORES:
        n_gap = int(t[f"bin_gap_{s}"].notna().sum())
        rep[f"labels_{s}"] = {
            "bin_gap_kept": n_gap,
            "bin_gap_dropped": len(t) - n_gap,
            "bin_gap_dropped_pct": round(100 * (len(t) - n_gap) / len(t), 1),
            "bin_gap_pos": int((t[f"bin_gap_{s}"] == 1).sum()),
            "bin_all_pos": int(t[f"bin_all_{s}"].sum()),
            "ord3": {k: int(v) for k, v in t[f"ord3_{s}"].value_counts().sort_index().items()},
            "ord3_pct": {int(k): round(100 * v, 1)
                         for k, v in t[f"ord3_{s}"].value_counts(normalize=True).sort_index().items()},
        }
    (OUT / "provenance_oneil.json").write_text(json.dumps(rep, indent=1))

    print(f"triples {len(t)}  drugs {len(drugs)}  cells {len(cells)}  tissues {t.tissue.nunique()}")
    for s in SCORES:
        r = rep[f"labels_{s}"]
        print(f"  {s:6s} ord3 ant/add/syn % {r['ord3_pct']}   "
              f"bin_gap drops {r['bin_gap_dropped']} ({r['bin_gap_dropped_pct']}%)")
    return t


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--thr", type=float, default=10.0)
    main(p.parse_args().thr)
