"""Baselines, all sharing SynGT's trainer so the comparison is apples to apples (planner 5.3).

  majority    always the biggest class                      - 69.9% of O'Neil is `additive`
  cell_only   expression only, drug identity removed        - "is the model learning the pair?"
  drug_only   drugs only, cell line removed
  onehot      one-hot(drug A)+one-hot(drug B)+one-hot(cell) - the identity baseline that beat a
                                                              PPI-GNN in this repo's earlier run
  deepsynergy Preuer et al. 2018: ECFP6-like Morgan r=3 + descriptors + expression -> 3x MLP
  deepdds     Wang et al. 2022: GCN on the molecule graph + MLP on expression -> concat -> MLP
Every model returns raw logits with the same head sizes as SynGT (2 for CORN, 3 nominal,
1 binary), so losses, metrics and early stopping are identical across the table.
"""
import torch
from torch import nn

from src.model.corn import CornHead
from src.model.syngt import MolEncoder

HEAD_OUT = {"corn": 2, "nominal": 3, "binary": 1}


def make_head(d_in, head):
    return CornHead(d_in, 3) if head == "corn" else nn.Linear(d_in, HEAD_OUT[head])


class _Base(nn.Module):
    def __init__(self, head):
        super().__init__()
        self.head_kind = head

    def class_logits(self, logits):
        return CornHead.class_logits(logits) if self.head_kind == "corn" else logits

    def contrast(self, logits, which="syn"):
        z = self.class_logits(logits)
        return z[:, 2] - z[:, 1] if which == "syn" else z[:, 0] - z[:, 1]


class Majority(_Base):
    def __init__(self, head="corn", prior=None):
        super().__init__(head)
        self.bias = nn.Parameter(torch.zeros(HEAD_OUT[head]) if prior is None else prior)

    def forward(self, batch):
        return self.bias[None].expand(batch["expr"].shape[0], -1)


class MLPOn(_Base):
    """MLP on a fixed feature vector assembled by `features(batch)`."""

    def __init__(self, d_in, head="corn", hidden=(512, 256), dropout=0.3):
        super().__init__(head)
        layers, d = [], d_in
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU(), nn.Dropout(dropout)]
            d = h
        self.body = nn.Sequential(*layers)
        self.out = make_head(d, head)

    def forward(self, batch):
        return self.out(self.body(self.features(batch)))


class CellOnly(MLPOn):
    def __init__(self, n_genes, **kw):
        super().__init__(n_genes, **kw)

    def features(self, batch):
        return batch["expr"]


class OneHot(MLPOn):
    def __init__(self, n_drugs, n_cells, **kw):
        super().__init__(n_drugs + n_cells, **kw)
        self.n_drugs, self.n_cells = n_drugs, n_cells

    def features(self, batch):
        t = batch["trip"]
        b = t.shape[0]
        d = torch.zeros(b, self.n_drugs, device=t.device)
        d.scatter_(1, t[:, :2], 1.0)                      # symmetric: a multi-hot of the pair
        c = torch.zeros(b, self.n_cells, device=t.device)
        c.scatter_(1, t[:, 2:3], 1.0)
        return torch.cat([d, c], 1)


class DrugOnly(MLPOn):
    def __init__(self, fp, **kw):
        super().__init__(fp.shape[1], **kw)
        self.register_buffer("fp", fp)

    def features(self, batch):
        t = batch["trip"]
        return self.fp[t[:, 0]] + self.fp[t[:, 1]]        # symmetric sum


class DeepSynergy(_Base):
    """Preuer et al. 2018. Drug features: Morgan r=3 (ECFP6-like) + RDKit descriptors."""

    def __init__(self, fp, desc, n_genes, head="corn", hidden=(2048, 1024), dropout=0.5):
        super().__init__(head)
        self.register_buffer("fp", fp)
        self.register_buffer("desc", desc)
        d_in = 2 * (fp.shape[1] + desc.shape[1]) + n_genes
        self.norm = nn.BatchNorm1d(d_in)                  # Preuer normalise inputs; BN stands in
        self.body = nn.Sequential(nn.Linear(d_in, hidden[0]), nn.ReLU(), nn.Dropout(dropout),
                                  nn.Linear(hidden[0], hidden[1]), nn.ReLU(), nn.Dropout(dropout),
                                  nn.Linear(hidden[1], 256), nn.ReLU())
        self.out = make_head(256, head)

    def forward(self, batch):
        t = batch["trip"]
        a = torch.cat([self.fp[t[:, 0]], self.desc[t[:, 0]]], 1)
        b = torch.cat([self.fp[t[:, 1]], self.desc[t[:, 1]]], 1)
        # drug order is arbitrary, so feed the symmetric (sum, |difference|) encoding
        x = torch.cat([a + b, (a - b).abs(), batch["expr"]], 1)
        return self.out(self.body(self.norm(x)))


class DeepDDS(_Base):
    """Wang et al. 2022: GCN per molecule + MLP on expression, concatenated, then an MLP."""

    def __init__(self, atom_dim, n_genes, head="corn", d=128, dropout=0.3):
        super().__init__(head)
        self.mol = MolEncoder(atom_dim, d, layers=2, kind="gcn", dropout=dropout)
        self.cell = nn.Sequential(nn.Linear(n_genes, 512), nn.ReLU(), nn.Dropout(dropout),
                                  nn.Linear(512, d), nn.ReLU())
        self.body = nn.Sequential(nn.Linear(3 * d, 512), nn.ReLU(), nn.Dropout(dropout),
                                  nn.Linear(512, 128), nn.ReLU())
        self.out = make_head(128, head)
        self.d = d

    def forward(self, batch):
        h = self.mol(batch["x"], batch["edge_index"])
        b = batch["n_mol"] // 2
        pooled = torch.zeros(batch["n_mol"], self.d, device=h.device)
        pooled.index_add_(0, batch["mol_batch"], h)
        cnt = torch.zeros(batch["n_mol"], device=h.device).index_add_(
            0, batch["mol_batch"], torch.ones_like(batch["mol_batch"], dtype=h.dtype))
        pooled = pooled / cnt[:, None].clamp_min(1)
        pa, pb = pooled[0::2], pooled[1::2]
        x = torch.cat([pa + pb, (pa - pb).abs(), self.cell(batch["expr"])], 1)
        return self.out(self.body(x))
