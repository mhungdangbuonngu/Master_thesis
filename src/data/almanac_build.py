"""Featurise ALMANAC and assemble the external test set -> data/processed/almanac.pt.

    python -m src.data.almanac_build

Nothing here may differ from the training features, or the external number measures the
feature pipeline instead of the model:
  * atom features, Morgan fingerprints, RDKit descriptors and BRICS fragments come from
    src.data.featurize, the same functions that built drugs.pt
  * the gene list is taken from cells.pt verbatim, in the same ORDER, so the gene-token
    budget `gene_order()` picks the same genes and the frozen node2vec rows still line up
  * expression stays raw log2(TPM+1); the z-score is applied at scoring time with the mean
    and sd of the O'Neil TRAINING cells of the run being scored (src.eval.external)

Three overlap flags per triple decide what "external" means for a given row:
  seen_drug_a / seen_drug_b   this drug is an O'Neil drug (same InChIKey, not same name)
  seen_pair                   this exact drug pair was in the O'Neil modelling table
  seen_cell                   this cell line is one of the 37 O'Neil cells (same DepMap id)
ALMANAC and O'Neil share 9 cell lines and 23 compounds, so the headline external number has
to be reported on the unseen subsets too.
"""
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdFingerprintGenerator

from src.data.cell import expression
from src.data.featurize import ATOM_DIM, DESCRIPTORS, atom_features, brics_fragments

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"
SCORES = ["loewe", "bliss", "zip", "hsa"]


def featurise(smiles_df):
    mg2 = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    mg3 = rdFingerprintGenerator.GetMorganGenerator(radius=3, fpSize=2048)
    drugs, graphs, fp2, fp3, desc = [], {}, [], [], []
    for _, r in smiles_df.iterrows():
        m = Chem.MolFromSmiles(r.smiles)
        x = torch.tensor([atom_features(a) for a in m.GetAtoms()], dtype=torch.float32)
        src, dst = [], []
        for b in m.GetBonds():
            i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
            src += [i, j]
            dst += [j, i]
        ei = torch.tensor([src, dst], dtype=torch.long) if src else torch.zeros(2, 0, dtype=torch.long)
        fid, nf = brics_fragments(m)
        graphs[r.drug] = {"x": x, "edge_index": ei, "frag": torch.tensor(fid), "n_frag": nf,
                          "smiles": r.smiles}
        drugs.append(r.drug)
        fp2.append(np.array(mg2.GetFingerprint(m), dtype=np.float32))
        fp3.append(np.array(mg3.GetFingerprint(m), dtype=np.float32))
        desc.append([getattr(Descriptors, d)(m) for d in DESCRIPTORS])
    de = np.nan_to_num(np.array(desc, dtype=np.float32), posinf=0, neginf=0)
    return {"drugs": drugs, "graphs": graphs, "fp2": torch.tensor(np.stack(fp2)),
            "fp3": torch.tensor(np.stack(fp3)), "desc": torch.tensor(de),
            "desc_names": DESCRIPTORS, "atom_dim": ATOM_DIM}


def main():
    trip = pd.read_csv(OUT / "almanac_triples.csv")
    s = pd.read_csv(OUT / "almanac_smiles.csv")
    s = s[s.smiles.notna() & (s.rdkit == "ok")].reset_index(drop=True)
    # two ALMANAC names can be the same compound (ADM HYDROCHLORIDE and DOXORUBICIN); the
    # modelling table must hold one index per compound, or the "unseen drug" subsets lie
    s = s.sort_values("drug").drop_duplicates("inchikey", keep="first").reset_index(drop=True)
    o = pd.read_csv(OUT / "smiles.csv")
    ce = torch.load(OUT / "cells.pt", weights_only=False)
    cmap = pd.read_csv(ROOT / "src" / "data" / "cell_line_map_almanac.csv")

    dr = featurise(s)
    key = dict(zip(s.drug, s.inchikey))
    oneil_keys = set(o[o.smiles.notna()].inchikey.dropna())
    oneil_pairs = set()
    ot = pd.read_csv(OUT / "triples.csv")
    okey = dict(zip(o.drug, o.inchikey))
    for a, b in zip(ot.drug_a, ot.drug_b):
        ka, kb = okey.get(a), okey.get(b)
        if isinstance(ka, str) and isinstance(kb, str):
            oneil_pairs.add(tuple(sorted((ka, kb))))

    t = trip[trip.drug_a.isin(dr["drugs"]) & trip.drug_b.isin(dr["drugs"])].reset_index(drop=True)
    cells = sorted(t.cell_line_name.unique())
    mid = dict(zip(cmap.drugcomb_name, cmap.model_id))
    model_ids = [mid[c] for c in cells]

    e = expression(model_ids)
    genes = ce["genes"]                                  # same list, same order as training
    missing = [g for g in genes if g not in e.columns]
    assert not missing, f"genes absent from the expression table: {missing[:5]}"
    expr = torch.tensor(e.loc[model_ids, genes].values.astype(np.float32))

    di = {d: i for i, d in enumerate(dr["drugs"])}
    ci = {c: i for i, c in enumerate(cells)}
    idx = torch.tensor(np.stack([t.drug_a.map(di), t.drug_b.map(di),
                                 t.cell_line_name.map(ci)], 1))

    y, score = {}, {}
    for sc in SCORES:
        score[sc] = torch.tensor(t[sc].values, dtype=torch.float32)
        y[f"bin_gap_{sc}"] = torch.tensor(t[f"bin_gap_{sc}"].values, dtype=torch.float32)
        y[f"bin_all_{sc}"] = torch.tensor(t[f"bin_all_{sc}"].values, dtype=torch.long)
        y[f"ord3_{sc}"] = torch.tensor(t[f"ord3_{sc}"].values, dtype=torch.long)
        for alt in (5, 20):
            y[f"ord3_{sc}_t{alt}"] = torch.tensor(t[f"ord3_{sc}_t{alt}"].values, dtype=torch.long)

    ka = t.drug_a.map(key)
    kb = t.drug_b.map(key)
    seen_a = torch.tensor(ka.isin(oneil_keys).values)
    seen_b = torch.tensor(kb.isin(oneil_keys).values)
    seen_pair = torch.tensor([tuple(sorted((x, z))) in oneil_pairs for x, z in zip(ka, kb)])
    oneil_models = set(ce["model_ids"])
    seen_cell = torch.tensor([mid[c] in oneil_models for c in t.cell_line_name])

    # Triples the two studies measured BOTH: same compound pair (by InChIKey, so ADM
    # HYDROCHLORIDE meets DOXORUBICIN) and the same DepMap cell line. These carry O'Neil's own
    # label as well, which makes them the control that separates a broken scoring pipeline
    # from a target that does not replicate: a model can be checked against the label it was
    # trained on and against ALMANAC's label for the same experiment.
    omid = dict(zip(pd.read_csv(ROOT / "src" / "data" / "cell_line_map.csv").drugcomb_name,
                    pd.read_csv(ROOT / "src" / "data" / "cell_line_map.csv").model_id))
    # dataset.pt row of each O'Neil triple, so a scored run can say whether it was trained on
    # that row: the row index is the position in triples.csv AFTER the same drug/cell filter
    # src.data.build applies, which is what dataset.pt is indexed by
    od = torch.load(OUT / "dataset.pt", weights_only=False)
    okept = ot[ot.drug_a.isin(od["drugs"]) & ot.drug_b.isin(od["drugs"])
               & ot.cell_line_name.isin(od["cells"])].reset_index(drop=True)
    assert len(okept) == len(od["idx"]), "triples.csv no longer lines up with dataset.pt"
    o_key = {}
    for i, r in okept.iterrows():
        kka, kkb = okey.get(r.drug_a), okey.get(r.drug_b)
        if not (isinstance(kka, str) and isinstance(kkb, str)):
            continue
        o_key[(*sorted((kka, kkb)), omid.get(r.cell_line_name))] = (r.ord3_loewe, r.loewe, i,
                                                                      r.loewe_iqr, r.n_replicates)
    hit = [o_key.get((*sorted((x, z)), mid[c])) for x, z, c in zip(ka, kb, t.cell_line_name)]
    oneil_ord3 = torch.tensor([-1 if h is None else int(h[0]) for h in hit], dtype=torch.long)
    oneil_loewe = torch.tensor([float("nan") if h is None else float(h[1]) for h in hit],
                               dtype=torch.float32)
    oneil_row = torch.tensor([-1 if h is None else int(h[2]) for h in hit], dtype=torch.long)
    # O'Neil's own spread on that triple: the cross-dataset ceiling can then be read on the
    # triples where at least ONE of the two studies measured tightly. ALMANAC has no such
    # column to offer - its triples are a single block (median 1 replicate), so there is
    # nothing to take an IQR over.
    oneil_iqr = torch.tensor([float("nan") if h is None else float(h[3]) for h in hit],
                             dtype=torch.float32)
    oneil_reps = torch.tensor([0 if h is None else int(h[4]) for h in hit], dtype=torch.long)

    obj = {**dr, "cells": cells, "model_ids": model_ids, "genes": genes, "expr": expr,
           "idx": idx, "y": y, "score": score, "tissue": t.tissue.tolist(),
           "n_replicates": torch.tensor(t.n_replicates.values),
           "loewe_iqr": torch.tensor(t.loewe_iqr.values, dtype=torch.float32),
           "seen_drug_a": seen_a, "seen_drug_b": seen_b, "seen_pair": seen_pair,
           "seen_cell": seen_cell, "oneil_ord3_loewe": oneil_ord3, "oneil_loewe": oneil_loewe,
           "oneil_row": oneil_row, "oneil_loewe_iqr": oneil_iqr,
           "oneil_n_replicates": oneil_reps}
    torch.save(obj, OUT / "almanac.pt")

    shared_drugs = sorted(s.drug[s.inchikey.isin(oneil_keys)])
    rep = {"date": str(date.today()), "triples": len(t), "triples_before_smiles": len(trip),
           "drugs": len(dr["drugs"]), "cells": len(cells), "genes": len(genes),
           "pairs": int(idx[:, :2].unique(dim=0).shape[0]),
           "shared_drugs_with_oneil": shared_drugs,
           "shared_cells_with_oneil": [c for c in cells if mid[c] in oneil_models],
           "n_seen_pair": int(seen_pair.sum()), "n_seen_cell": int(seen_cell.sum()),
           "n_both_drugs_seen": int((seen_a & seen_b).sum()),
           "n_unseen_pair_and_cell": int((~seen_pair & ~seen_cell).sum()),
           "n_measured_by_both_studies": int((oneil_ord3 >= 0).sum()),
           "ord3_loewe_counts": torch.bincount(y["ord3_loewe"], minlength=3).tolist(),
           "expr_mean": float(expr.mean()), "expr_std": float(expr.std())}
    (OUT / "provenance_almanac_build.json").write_text(json.dumps(rep, indent=1))
    print(f"almanac.pt: {len(t)} triples  {len(dr['drugs'])} drugs  {len(cells)} cells  "
          f"{rep['pairs']} pairs")
    print(f"  shares {len(shared_drugs)} compounds and {len(rep['shared_cells_with_oneil'])} "
          f"cells with O'Neil")
    print(f"  seen pair {rep['n_seen_pair']}  seen cell {rep['n_seen_cell']}  "
          f"neither {rep['n_unseen_pair_and_cell']}  "
          f"measured by both studies {rep['n_measured_by_both_studies']}")
    print(f"  ord3_loewe ant/add/syn {rep['ord3_loewe_counts']}")
    return obj


if __name__ == "__main__":
    main()
