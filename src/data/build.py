"""Assemble the modelling table -> data/processed/dataset.pt  (planner 3.3, 4.3).

    python -m src.data.build

Keeps only triples whose BOTH drugs have a standardised structure, encodes drugs and cells
as integer ids, and carries every label variant: 4 synergy scores x {bin_gap, bin_all, ord3}
plus ord3 at thresholds 5 and 20. Nothing is dropped for a label being NA here; the training
loop masks NA rows, so every setting runs on the same index space and the splits are shared.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"
SCORES = ["loewe", "bliss", "zip", "hsa"]


def main():
    trip = pd.read_csv(OUT / "triples.csv")
    dr = torch.load(OUT / "drugs.pt", weights_only=False)
    ce = torch.load(OUT / "cells.pt", weights_only=False)
    drugs, cells = dr["drugs"], ce["cells"]

    t = trip[trip.drug_a.isin(drugs) & trip.drug_b.isin(drugs) & trip.cell_line_name.isin(cells)]
    t = t.reset_index(drop=True)
    di = {d: i for i, d in enumerate(drugs)}
    ci = {c: i for i, c in enumerate(cells)}
    idx = torch.tensor(np.stack([t.drug_a.map(di), t.drug_b.map(di), t.cell_line_name.map(ci)], 1))

    y, score = {}, {}
    for s in SCORES:
        score[s] = torch.tensor(t[s].values, dtype=torch.float32)
        y[f"bin_gap_{s}"] = torch.tensor(t[f"bin_gap_{s}"].values, dtype=torch.float32)  # NaN = drop
        y[f"bin_all_{s}"] = torch.tensor(t[f"bin_all_{s}"].values, dtype=torch.long)
        y[f"ord3_{s}"] = torch.tensor(t[f"ord3_{s}"].values, dtype=torch.long)
        for alt in (5, 20):
            y[f"ord3_{s}_t{alt}"] = torch.tensor(t[f"ord3_{s}_t{alt}"].values, dtype=torch.long)

    obj = {"idx": idx, "y": y, "score": score, "drugs": drugs, "cells": cells,
           "pair": torch.tensor(np.stack([t.drug_a.map(di), t.drug_b.map(di)], 1)),
           "tissue": t.tissue.tolist(), "n_replicates": torch.tensor(t.n_replicates.values),
           "loewe_iqr": torch.tensor(t.loewe_iqr.values, dtype=torch.float32)}
    torch.save(obj, OUT / "dataset.pt")

    rep = {"triples": len(t), "drugs": len(drugs), "cells": len(cells),
           "pairs": int(obj["pair"].unique(dim=0).shape[0]),
           "tissues": sorted(set(obj["tissue"]))}
    for s in SCORES:
        n_ok = int(~torch.isnan(y[f"bin_gap_{s}"]).sum().item() * 0 + (~torch.isnan(y[f"bin_gap_{s}"])).sum())
        rep[s] = {"bin_gap_rows": n_ok, "bin_gap_dropped_pct": round(100 * (len(t) - n_ok) / len(t), 1),
                  "ord3_counts": torch.bincount(y[f"ord3_{s}"], minlength=3).tolist()}
    (OUT / "provenance_dataset.json").write_text(json.dumps(rep, indent=1))
    print(f"dataset: {len(t)} triples, {len(drugs)} drugs, {rep['pairs']} pairs, {len(cells)} cells")
    for s in SCORES:
        print(f"  {s:6s} ord3 {rep[s]['ord3_counts']}  bin_gap keeps {rep[s]['bin_gap_rows']} "
              f"(drops {rep[s]['bin_gap_dropped_pct']}%)")
    return obj


if __name__ == "__main__":
    main()
