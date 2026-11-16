"""Prediction baselines: one-hot MLP (identity only) and DeepSynergy-style MLP (no network)."""
import torch
from torch import nn

from src.model.gnn import node_features


def mlp(n_in, hidden, dropout):
    return nn.Sequential(nn.Linear(n_in, hidden), nn.ReLU(), nn.Dropout(dropout),
                         nn.Linear(hidden, hidden // 2), nn.ReLU(), nn.Dropout(dropout),
                         nn.Linear(hidden // 2, 3))


class OneHotMLP(nn.Module):
    def __init__(self, n_drugs, n_cells, hidden=256, dropout=0.4):
        super().__init__()
        self.n_drugs, self.n_cells = n_drugs, n_cells
        self.net = mlp(n_drugs + n_cells, hidden, dropout)

    def forward(self, trip):
        oh = nn.functional.one_hot
        drugs = oh(trip[:, 0], self.n_drugs) + oh(trip[:, 1], self.n_drugs)  # sum: symmetric in A <-> B
        return self.net(torch.cat([drugs, oh(trip[:, 2], self.n_cells)], 1).float())


class DeepSynergyMLP(nn.Module):
    """Same node features as SynergyGNN, flattened, no message passing."""

    def __init__(self, expr, targets, hidden=256, dropout=0.4):
        super().__init__()
        self.register_buffer("expr", expr)
        self.register_buffer("targets", targets)
        self.net = nn.Sequential(nn.Flatten(), mlp(3 * expr.shape[1], hidden, dropout))

    def forward(self, trip):
        return self.net(node_features(self.expr, self.targets, trip))
