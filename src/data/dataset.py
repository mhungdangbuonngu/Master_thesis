"""Load oneil.pt, derive 3-class labels, leave-combo split."""
from pathlib import Path

import numpy as np
import torch

PATH = Path(__file__).parent / "processed" / "oneil.pt"
ANT, ADD, SYN = 0, 1, 2  # ordinal, so QWK makes sense


def load(path=PATH):
    return torch.load(path)


def labels(scores, threshold):
    y = torch.full_like(scores, ADD, dtype=torch.long)
    y[scores < -threshold] = ANT
    y[scores > threshold] = SYN
    return y


def leave_combo_split(triples, fold, seed, n_folds=5, val_frac=0.1, split_seed=0):
    """Test pairs (A,B) never appear in train/val under any cell line.

    The fold partition is fixed by split_seed so all seeds share the same test sets;
    the validation pairs are drawn from the remaining pairs with the run seed.
    """
    pairs, inv = np.unique(triples[:, :2].numpy(), axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    fold_of = np.random.default_rng(split_seed).permutation(len(pairs)) % n_folds
    rest = np.flatnonzero(fold_of != fold)
    val_pairs = np.random.default_rng(seed).choice(rest, int(round(val_frac * len(rest))), replace=False)
    is_test = fold_of[inv] == fold
    is_val = np.isin(inv, val_pairs)
    idx = np.arange(len(triples))
    return idx[~is_test & ~is_val], idx[is_val], idx[is_test]
