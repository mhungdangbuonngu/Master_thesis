"""Molecule graphs, fingerprints and BRICS fragments -> data/processed/drugs.pt  (planner 4.1).

    python -m src.data.featurize

Atom features are the 78-dim vector of GraphDRP / DeepDDS, which DTSyn also uses, so the
drug branch is comparable to those papers:
    symbol one-hot (44) + degree (11) + total H (11) + implicit valence (11) + aromatic (1)
Also saved, for the baselines and for XAI:
    Morgan fingerprints r=2 and r=3 (2048 bits)  -> XGBoost, DeepSynergy-style features
    RDKit descriptor vector                      -> DeepSynergy-style features
    BRICS fragment id per atom                   -> fragment masks for Fid+ and attribution
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from rdkit import Chem, RDLogger
from rdkit.Chem import BRICS, Descriptors, rdFingerprintGenerator

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"

SYMBOLS = ["C", "N", "O", "S", "F", "Si", "P", "Cl", "Br", "Mg", "Na", "Ca", "Fe", "As", "Al",
           "I", "B", "V", "K", "Tl", "Yb", "Sb", "Sn", "Ag", "Pd", "Co", "Se", "Ti", "Zn", "H",
           "Li", "Ge", "Cu", "Au", "Ni", "Cd", "In", "Mn", "Zr", "Cr", "Pt", "Hg", "Pb", "Unknown"]
ATOM_DIM = len(SYMBOLS) + 11 + 11 + 11 + 1          # 78
DESCRIPTORS = ["MolWt", "MolLogP", "NumHAcceptors", "NumHDonors", "TPSA", "NumRotatableBonds",
               "RingCount", "FractionCSP3", "HeavyAtomCount", "NumAromaticRings",
               "NumSaturatedRings", "NHOHCount", "NOCount", "MolMR", "BalabanJ", "BertzCT"]


def onehot(x, allowed):
    v = [0.0] * len(allowed)
    v[allowed.index(x) if x in allowed else len(allowed) - 1] = 1.0
    return v


def atom_features(a):
    return (onehot(a.GetSymbol(), SYMBOLS)
            + onehot(a.GetDegree(), list(range(11)))
            + onehot(a.GetTotalNumHs(), list(range(11)))
            + onehot(a.GetImplicitValence(), list(range(11)))
            + [float(a.GetIsAromatic())])


def brics_fragments(mol):
    """Fragment id per atom from BRICS bonds; a molecule with no BRICS bond is one fragment."""
    bonds = [b[0] for b in BRICS.FindBRICSBonds(mol)]
    if not bonds:
        return np.zeros(mol.GetNumAtoms(), dtype=np.int64), 1
    ids = [mol.GetBondBetweenAtoms(i, j).GetIdx() for i, j in bonds]
    frag = Chem.FragmentOnBonds(mol, ids, addDummies=False)
    groups = Chem.GetMolFrags(frag)
    out = np.zeros(mol.GetNumAtoms(), dtype=np.int64)
    for k, g in enumerate(groups):
        for a in g:
            if a < mol.GetNumAtoms():
                out[a] = k
    return out, len(groups)


def main():
    s = pd.read_csv(OUT / "smiles.csv")
    s = s[s.smiles.notna() & (s.rdkit == "ok")].reset_index(drop=True)
    mg2 = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    mg3 = rdFingerprintGenerator.GetMorganGenerator(radius=3, fpSize=2048)

    drugs, graphs, fp2, fp3, desc, nfrag = [], {}, [], [], [], []
    for _, r in s.iterrows():
        m = Chem.MolFromSmiles(r.smiles)
        x = torch.tensor([atom_features(a) for a in m.GetAtoms()], dtype=torch.float32)
        src, dst = [], []
        for b in m.GetBonds():                       # undirected -> store both directions
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
        nfrag.append(nf)

    d = np.array(desc, dtype=np.float32)
    d = np.nan_to_num(d, posinf=0, neginf=0)
    obj = {"drugs": drugs, "graphs": graphs,
           "fp2": torch.tensor(np.stack(fp2)), "fp3": torch.tensor(np.stack(fp3)),
           "desc": torch.tensor(d), "desc_names": DESCRIPTORS, "atom_dim": ATOM_DIM}
    torch.save(obj, OUT / "drugs.pt")

    rep = {"drugs": len(drugs), "atom_dim": ATOM_DIM,
           "atoms_min": int(min(g["x"].shape[0] for g in graphs.values())),
           "atoms_max": int(max(g["x"].shape[0] for g in graphs.values())),
           "atoms_median": float(np.median([g["x"].shape[0] for g in graphs.values()])),
           "frags_min": int(min(nfrag)), "frags_max": int(max(nfrag)),
           "frags_median": float(np.median(nfrag)),
           "fp2_bits_on_median": float(np.median([f.sum() for f in fp2]))}
    (OUT / "provenance_drugs.json").write_text(json.dumps(rep, indent=1))
    print(f"{len(drugs)} drugs  atoms {rep['atoms_min']}-{rep['atoms_max']} (med {rep['atoms_median']})  "
          f"BRICS frags {rep['frags_min']}-{rep['frags_max']} (med {rep['frags_median']})")
    return obj


if __name__ == "__main__":
    main()
