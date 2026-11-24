"""Five evaluation scenarios -> data/processed/splits.pt  (planner 3.4).

    python -m src.data.splits

    random      5-fold over triples                      (comparable to DeepDDS' random CV)
    leave_combo 5-fold over unique drug pairs             (DTSyn: leave-combination-out)
    leave_drug  5 clusters of drugs by structural similarity; a test triple contains at
                least one held-out drug                   (DTSyn: leave-drug-out)
    leave_cell  5-fold over cell lines                    (DTSyn: leave-cell-out)
    leave_tumor one fold per tissue (7)                   (DTSyn: leave-tumor-out)

The validation set is always carved out of the training part BY THE SAME UNIT as the outer
split (a held-out drug cluster for leave_drug, held-out cells for leave_cell, ...). Using a
random validation split inside a grouped outer split leaks and picks the wrong model; there
is a unit test for this.
"""
import json
from pathlib import Path

import numpy as np
import torch
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed"
SPLITS = ["random", "leave_combo", "leave_drug", "leave_cell", "leave_tumor"]


def tanimoto_distance(fp):
    f = fp.numpy().astype(bool)
    inter = f @ f.T
    size = f.sum(1)
    union = size[:, None] + size[None, :] - inter
    return 1.0 - inter / np.maximum(union, 1)


def drug_clusters(fp, k=5):
    """Structure-aware AND balanced drug folds for the leave-drug protocol.

    Cutting the Tanimoto dendrogram into k clusters is degenerate on these 36 drugs: they are
    chemically diverse with no analogue series, so average linkage returns one 25-32 drug
    cluster plus singletons, which would put 91% of the triples into a single test fold.
    Instead the dendrogram's LEAF ORDER is cut into k contiguous blocks of equal size:
    neighbouring leaves are the most similar pairs, so chemically close drugs still share a
    fold, while every fold gets 7-8 drugs. Reported in the thesis as a deviation.
    """
    d = tanimoto_distance(fp)
    order = leaves_list(linkage(squareform(d, checks=False), method="average"))
    fold = np.zeros(len(order), dtype=int)
    per = int(np.ceil(len(order) / k))
    for pos, drug in enumerate(order):
        fold[drug] = min(pos // per, k - 1)
    return fold


def group_folds(group_of_item, n_folds, seed=0):
    """Assign each distinct group to a fold, then map back to items."""
    groups = np.unique(group_of_item)
    rng = np.random.default_rng(seed)
    fold_of_group = rng.permutation(len(groups)) % n_folds
    m = dict(zip(groups, fold_of_group))
    return np.array([m[g] for g in group_of_item])


def make(unit, n_folds, seed=0):
    """unit: array (n_triples,) of the grouping key. Returns a list of (train, val, test)."""
    fold = group_folds(unit, n_folds, seed)
    out = []
    for f in range(n_folds):
        test = np.flatnonzero(fold == f)
        rest = np.flatnonzero(fold != f)
        # validation = one of the remaining folds, same unit -> no leakage, no random carve
        vfold = (f + 1) % n_folds
        val = np.flatnonzero(fold == vfold)
        train = np.setdiff1d(rest, val)
        out.append((torch.tensor(train), torch.tensor(val), torch.tensor(test)))
    return out


def main(seed=0):
    d = torch.load(OUT / "dataset.pt", weights_only=False)
    dr = torch.load(OUT / "drugs.pt", weights_only=False)
    idx, pair = d["idx"].numpy(), d["pair"].numpy()
    n = len(idx)

    cl = drug_clusters(dr["fp2"], 5)
    # a triple's leave-drug group is the pair of its drugs' clusters: held out if EITHER drug is
    drug_group = np.array([f"{min(cl[a], cl[b])}" if cl[a] == cl[b] else f"{min(cl[a], cl[b])}-{max(cl[a], cl[b])}"
                           for a, b in pair])

    splits = {}
    splits["random"] = make(np.arange(n) % 5, 5, seed)
    splits["leave_combo"] = make(np.array([f"{a}_{b}" for a, b in pair]), 5, seed)
    splits["leave_cell"] = make(idx[:, 2].astype(str), 5, seed)
    splits["leave_tumor"] = make(np.array(d["tissue"]), len(set(d["tissue"])), seed)

    # leave_drug: hold out a drug cluster; test = triples touching it, train = triples touching
    # neither the test nor the validation cluster (so a test drug never appears in training)
    ld = []
    for f in range(5):
        vf = (f + 1) % 5
        in_test = np.array([cl[a] == f or cl[b] == f for a, b in pair])
        in_val = np.array([cl[a] == vf or cl[b] == vf for a, b in pair])
        test = np.flatnonzero(in_test)
        val = np.flatnonzero(in_val & ~in_test)
        train = np.flatnonzero(~in_test & ~in_val)
        ld.append((torch.tensor(train), torch.tensor(val), torch.tensor(test)))
    splits["leave_drug"] = ld

    torch.save({"splits": splits, "drug_cluster": cl.tolist(), "seed": seed}, OUT / "splits.pt")

    rep = {"seed": seed, "triples": n,
           "drug_cluster_sizes": np.bincount(cl).tolist(),
           "drug_clusters": {str(c): [dr["drugs"][i] for i in np.flatnonzero(cl == c)]
                             for c in range(5)}}
    for k, v in splits.items():
        rep[k] = [{"train": len(tr), "val": len(va), "test": len(te)} for tr, va, te in v]
    (OUT / "provenance_splits.json").write_text(json.dumps(rep, indent=1))
    for k, v in splits.items():
        sizes = [f"{len(te)}" for _, _, te in v]
        print(f"  {k:12s} {len(v)} folds, test sizes {' '.join(sizes)}")
    print(f"  drug clusters {rep['drug_cluster_sizes']}")
    return splits


if __name__ == "__main__":
    main()
