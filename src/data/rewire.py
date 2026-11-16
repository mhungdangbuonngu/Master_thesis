"""Degree-preserving rewiring of the filtered network, cached per seed."""
from pathlib import Path

import networkx as nx
import torch

CACHE = Path(__file__).parent / "processed"


def rewire(edge_index, seed, swaps_per_edge=10, cache_dir=CACHE):
    path = Path(cache_dir) / f"rewired_{edge_index.shape[1]}_{seed}.pt"
    if path.exists():
        return torch.load(path)
    g = nx.Graph(edge_index.T.tolist())
    n = swaps_per_edge * g.number_of_edges()
    nx.double_edge_swap(g, nswap=n, max_tries=20 * n, seed=seed)
    out = torch.tensor(list(g.edges())).T
    torch.save(out, path)
    return out
