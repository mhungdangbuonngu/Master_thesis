"""Invariant checks. Run: python -m pytest src/tests -q   (or python -m src.tests.test_all)

Pending until src/explain exists: IG completeness, interaction = 0 for an additive model.
"""
import tempfile

import networkx as nx
import numpy as np
import torch

from src.data.dataset import labels, leave_combo_split
from src.data.rewire import rewire
from src.model.gnn import SynergyGNN, norm_adj, propagate


def toy(n=30, n_drugs=6, n_cells=4, seed=0):
    g = nx.gnm_random_graph(n, 80, seed=seed)
    edges = torch.tensor(list(g.edges())).T
    gen = torch.Generator().manual_seed(seed)
    expr = torch.randn(n_cells, n, generator=gen)
    targets = (torch.rand(n_drugs, n, generator=gen) < 0.15).float()
    return expr, targets, edges


def test_symmetry_a_b():
    expr, targets, edges = toy()
    model = SynergyGNN(expr, targets, edges, proj=2, mlp=8).eval()
    trip = torch.tensor([[0, 1, 0], [2, 5, 3], [3, 4, 1]])
    assert torch.allclose(model(trip), model(trip[:, [1, 0, 2]]), atol=1e-6)


def test_mask_one_matches_dense_gcn():
    expr, _, edges = toy()
    n = expr.shape[1]
    a = torch.zeros(n, n)
    a[edges[0], edges[1]] = a[edges[1], edges[0]] = 1
    a += torch.eye(n)
    d = a.sum(1).rsqrt()
    dense = d[:, None] * a * d[None, :]
    h = torch.randn(3, n, 5)
    got = propagate(norm_adj(edges, torch.ones(edges.shape[1]), n), h)
    assert torch.allclose(got, dense @ h, atol=1e-5)


def test_mask_zero_is_identity():
    expr, _, edges = toy()
    n = expr.shape[1]
    adj = norm_adj(edges, torch.zeros(edges.shape[1]), n).to_dense()
    assert torch.allclose(adj, torch.eye(n))


def test_split_no_leak():
    rng = np.random.default_rng(0)
    a, b = rng.integers(0, 10, 2000), rng.integers(0, 10, 2000)
    trip = torch.tensor(np.c_[np.minimum(a, b), np.maximum(a, b), rng.integers(0, 5, 2000)])
    pair = lambda idx: {tuple(p) for p in trip[idx, :2].tolist()}
    seen_test = set()
    for fold in range(5):
        tr, va, te = leave_combo_split(trip, fold, seed=3)
        assert len(tr) + len(va) + len(te) == len(trip)
        assert not pair(tr) & pair(te) and not pair(va) & pair(te) and not pair(tr) & pair(va)
        seen_test |= set(te.tolist())
    assert len(seen_test) == len(trip)  # folds partition the data


def test_rewiring_keeps_degree():
    _, _, edges = toy()
    new = rewire(edges, seed=1, cache_dir=tempfile.mkdtemp())
    deg = lambda e: torch.bincount(e.flatten(), minlength=30)
    assert torch.equal(deg(edges), deg(new))
    assert {tuple(sorted(x)) for x in new.T.tolist()} != {tuple(sorted(x)) for x in edges.T.tolist()}


def test_labels():
    y = labels(torch.tensor([-11.0, -10.0, 0.0, 10.0, 10.5]), 10)
    assert y.tolist() == [0, 1, 1, 1, 2]


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f()
            print("ok", k)
