"""SynergyGNN: 2-layer GCN on the PPI with an edge mask m in the forward pass."""
import torch
from torch import nn


def node_features(expr, targets, trip):
    """[expr_c(g), tA(g)+tB(g), tA(g)*tB(g)] -> (B, n_gen, 3); symmetric in A <-> B."""
    ta, tb = targets[trip[:, 0]], targets[trip[:, 1]]
    return torch.stack([expr[trip[:, 2]], ta + tb, ta * tb], dim=-1)


def norm_adj(edge_index, m, n):
    """D^-1/2 (A_m + I) D^-1/2 as a sparse matrix; degrees are taken after masking.

    edge_index holds each undirected edge once, m has one weight per undirected edge.
    At m = 0 this is the identity: every gene keeps only its self-loop.
    """
    src, dst = edge_index
    loop = torch.arange(n, device=m.device)
    row = torch.cat([src, dst, loop])
    col = torch.cat([dst, src, loop])
    w = torch.cat([m, m, torch.ones(n, device=m.device)])
    deg = torch.zeros(n, device=m.device).index_add(0, row, w)
    val = w * deg[row].rsqrt() * deg[col].rsqrt()
    return torch.sparse_coo_tensor(torch.stack([row, col]), val, (n, n), check_invariants=False)


def propagate(adj, h):
    """adj (N,N) sparse @ h (B,N,F), batched by folding B into the feature axis."""
    b, n, f = h.shape
    out = torch.sparse.mm(adj, h.transpose(0, 1).reshape(n, b * f))
    return out.reshape(n, b, f).transpose(0, 1)


class SynergyGNN(nn.Module):
    def __init__(self, expr, targets, edge_index, hidden=16, proj=2, mlp=64, dropout=0.4):
        super().__init__()
        self.register_buffer("expr", expr)
        self.register_buffer("targets", targets)
        self.register_buffer("edge_index", edge_index)
        n = expr.shape[1]
        self.w1 = nn.Linear(3, hidden, bias=False)
        self.w2 = nn.Linear(hidden, hidden, bias=False)
        self.proj = nn.Linear(hidden, proj)  # shared across genes, then flatten keeps gene identity
        # BatchNorm on the flattened vector: after GCN smoothing the per-gene signal is ~0.1
        # on top of a shared proj bias, and without it training collapses to a constant class.
        self.mlp = nn.Sequential(nn.Flatten(), nn.BatchNorm1d(n * proj), nn.Linear(n * proj, mlp),
                                 nn.ReLU(), nn.Dropout(dropout), nn.Linear(mlp, 3))

    def forward(self, trip, m=None):
        # ponytail: m is shared across the batch; per-sample edge-IG runs one triple per call
        if m is None:
            m = torch.ones(self.edge_index.shape[1], device=self.expr.device)
        adj = norm_adj(self.edge_index, m, self.expr.shape[1])
        h = node_features(self.expr, self.targets, trip)
        h = torch.relu(propagate(adj, self.w1(h)))
        h = torch.relu(propagate(adj, self.w2(h)))
        return self.mlp(self.proj(h))
