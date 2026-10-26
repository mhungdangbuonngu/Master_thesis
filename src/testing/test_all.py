"""Các kiểm tra nhỏ, chạy nhanh trên CPU, không cần framework test.

Chạy:  python -m src.testing.test_all
"""
import numpy as np
import torch

from src.data.dataset import make_split
from src.eval.attribution import integrated_gradients, target_fn
from src.eval.metrics import classification_metrics
from src.model.gnn import SYN, SynergyGNN


def toy_data(n_genes=20, n_drugs=6, n_cells=5, seed=0):
    """Tạo dict dữ liệu nhỏ ngẫu nhiên cùng định dạng với prepare.py."""
    g = torch.Generator().manual_seed(seed)
    A = (torch.rand(n_genes, n_genes, generator=g) < 0.2).float()
    A = ((A + A.T + torch.eye(n_genes)) > 0).float()
    d = A.sum(1).rsqrt()
    trip = torch.tensor([(a, b, c) for a in range(n_drugs) for b in range(a + 1, n_drugs) for c in range(n_cells)])
    return {"adj": (d[:, None] * A * d[None, :]).to_sparse(),
            "targets": (torch.rand(n_drugs, n_genes, generator=g) < 0.2).float(),
            "expr": torch.randn(n_cells, n_genes, generator=g),
            "triplets": trip, "y": torch.randint(0, 3, (len(trip),), generator=g)}


def test_symmetry():
    """Model phải cho cùng logit với (A, B, c) và (B, A, c)."""
    d = toy_data()
    m = SynergyGNN(d["adj"], d["targets"]).eval()
    t = d["triplets"]
    x = d["expr"][t[:, 2]]
    assert torch.allclose(m(t[:, 0], t[:, 1], x), m(t[:, 1], t[:, 0], x), atol=1e-5)


def test_split_no_leak():
    """Leave-combination-out không được để cặp thuốc của test lọt vào train/val; tương tự với leave-cell-out."""
    d = toy_data()
    t = d["triplets"].numpy()
    tr, va, te = make_split(d, "combo", fold=0)
    pairs = lambda idx: {(a, b) for a, b in t[idx, :2]}
    assert len(te) > 0 and not (pairs(te) & pairs(np.concatenate([tr, va])))
    tr, va, te = make_split(d, "cell", fold=0)
    assert len(te) > 0 and not (set(t[te, 2]) & set(t[np.concatenate([tr, va]), 2]))
    assert len(tr) + len(va) + len(te) == len(t)


def test_ig_completeness():
    """Tổng IG phải xấp xỉ f(x) - f(0) (tiên đề completeness)."""
    d = toy_data()
    m = SynergyGNN(d["adj"], d["targets"]).eval()
    t = d["triplets"][:8]
    x = d["expr"][t[:, 2]]
    f = target_fn(m, t[:, 0], t[:, 1], SYN, "contrast")
    ig = integrated_gradients(f, x, steps=256)
    gap = (ig.sum(1) - (f(x) - f(torch.zeros_like(x)))).abs().max().item()
    assert gap < 0.05, gap


class AdditiveModel(torch.nn.Module):
    """Model giả không có tương tác: logit = u[A] * x + u[B] * x, tức hiệu ứng riêng của từng thuốc cộng lại."""

    def __init__(self, n_drugs, n_genes):
        super().__init__()
        self.u = torch.nn.Parameter(torch.randn(n_drugs, 3, n_genes))

    def forward(self, a, b, x):
        return torch.einsum("bkn,bn->bk", self.u[a] + self.u[b], torch.tanh(x))


def test_interaction_kills_main_effects():
    """Với model thuần cộng tính, attribution cấp interaction phải bằng 0, còn cấp contrast thì không."""
    d = toy_data()
    m = AdditiveModel(6, 20)
    t = d["triplets"][:8]
    x = d["expr"][t[:, 2]]
    inter = integrated_gradients(target_fn(m, t[:, 0], t[:, 1], SYN, "interaction", list(range(6))), x)
    contr = integrated_gradients(target_fn(m, t[:, 0], t[:, 1], SYN, "contrast"), x)
    assert inter.abs().max() < 1e-4 and contr.abs().max() > 1e-2


def test_metrics():
    """QWK = 1 khi đoán đúng hết; polar_error đếm đúng lỗi syn <-> ant."""
    y = np.array([0, 1, 2, 2])
    assert classification_metrics(y, y)["qwk"] == 1.0
    assert classification_metrics(y, np.array([2, 1, 2, 0]))["polar_error"] == 0.5


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
