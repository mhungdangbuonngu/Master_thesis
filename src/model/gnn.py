"""Model GNN trên mạng PPI dự đoán hiệp đồng thuốc 3 lớp (viết bằng torch thuần, không cần PyG)."""
import torch
from torch import nn

ANT, ADD, SYN = 0, 1, 2


class SynergyGNN(nn.Module):
    """GCN trên đồ thị PPI dùng chung cho mọi bộ ba (A, B, c).

    Đặc trưng của node gene g với bộ ba (A, B, c):
        [expr_c(g), tA(g) + tB(g), tA(g) * tB(g)]
    trong đó tA(g) = 1 nếu g là target của A. Tổng và tích đều đối xứng theo A và B,
    nên f(A, B, c) = f(B, A, c) được đảm bảo ngay từ thiết kế.

    Luồng tính:
        node features -> n_layers x GCN (ReLU) -> chiếu mỗi gene còn gene_dim chiều -> flatten
        (flatten giữ được danh tính từng gene; mean-pooling sẽ làm mất danh tính này)
        ghép với [eA + eB, eA * eB] (embedding thuốc, cũng đối xứng) -> MLP -> 3 logit (ant, add, syn)
    """

    def __init__(self, adj, targets, hidden=32, gene_dim=4, drug_dim=16, n_layers=2, dropout=0.2):
        """
        Args:
            adj: sparse (N, N), ma trận kề PPI đã chuẩn hóa (từ prepare.py).
            targets: (D, N) ma trận target 0/1 của thuốc.
            hidden: số chiều ẩn của GCN.
            gene_dim: số chiều giữ lại cho mỗi gene trước khi flatten.
            drug_dim: số chiều embedding thuốc.
            n_layers: số lớp GCN.
            dropout: dropout trong MLP đầu ra.
        """
        super().__init__()
        self.register_buffer("adj", adj.coalesce())
        self.register_buffer("targets", targets)
        n_genes, n_drugs = adj.shape[0], targets.shape[0]
        dims = [3] + [hidden] * n_layers
        self.gcn = nn.ModuleList(nn.Linear(i, o) for i, o in zip(dims[:-1], dims[1:]))
        self.gene_out = nn.Linear(hidden, gene_dim)
        self.drug_emb = nn.Embedding(n_drugs, drug_dim)
        self.head = nn.Sequential(
            nn.Linear(n_genes * gene_dim + 2 * drug_dim, 128), nn.ReLU(), nn.Dropout(dropout), nn.Linear(128, 3))

    def propagate(self, h):
        """Một bước lan truyền GCN: adj @ h cho cả batch. h: (B, N, F) -> (B, N, F)."""
        B, N, F = h.shape
        h = torch.sparse.mm(self.adj, h.permute(1, 0, 2).reshape(N, B * F))
        return h.reshape(N, B, F).permute(1, 0, 2)

    def forward(self, a, b, expr):
        """
        Args:
            a, b: (B,) chỉ số thuốc A và thuốc B.
            expr: (B, N) biểu hiện gene của dòng tế bào. Truyền riêng tensor này để có thể lấy gradient
                  theo expr khi tính attribution.
        Returns:
            (B, 3) logit theo thứ tự [antagonistic, additive, synergistic].
        """
        ta, tb = self.targets[a], self.targets[b]
        h = torch.stack([expr, ta + tb, ta * tb], -1)
        for lin in self.gcn:
            h = torch.relu(self.propagate(lin(h)))
        g = self.gene_out(h).flatten(1)
        ea, eb = self.drug_emb(a), self.drug_emb(b)
        return self.head(torch.cat([g, ea + eb, ea * eb], 1))
