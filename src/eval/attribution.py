"""Ba cấp attribution trên biểu hiện gene, là lõi của phương án A.

  (i)   "logit"       : giải thích z_cls, cách literature đang làm
  (ii)  "contrast"    : giải thích Δ = z_cls - z_add, "vì sao chọn lớp cls thay vì additive"
  (iii) "interaction" : giải thích phần TƯƠNG TÁC của Δ, đã loại bỏ hiệu ứng chính của từng thuốc:
          Δ(A,B) - E_r[Δ(A,r)] - E_r[Δ(r,B)] + E_{r,r'}[Δ(r,r')]
        trong đó r, r' là thuốc tham chiếu (functional ANOVA bậc 2 theo trục thuốc).
        Nếu thuốc A "hiệp đồng với mọi đối tác", phần đó nằm cả trong Δ(A,B) lẫn E_r[Δ(A,r)] nên bị trừ đi.

Vì Integrated Gradients (IG) tuyến tính theo hàm cần giải thích, IG của tổng = tổng IG từng hạng tử.
"""
import torch

from src.model.gnn import ADD

LEVELS = ("logit", "contrast", "interaction")


def target_terms(model, a, b, cls, level, ref_drugs=()):
    """Phân rã đại lượng cần giải thích thành tổng có trọng số: f(x) = sum_i w_i * g_i(x).

    Tách thành từng hạng tử để IG lấy gradient từng hạng tử rồi cộng lại (IG tuyến tính theo f),
    tránh giữ cùng lúc 1 + 3R đồ thị tính toán trên GPU (gây hết bộ nhớ ở cấp interaction).

    Args:
        model: SynergyGNN ở chế độ eval.
        a, b: (B,) chỉ số thuốc.
        cls: lớp cần giải thích (SYN = 2 hoặc ANT = 0).
        level: một trong LEVELS.
        ref_drugs: danh sách chỉ số thuốc tham chiếu, bắt buộc với level "interaction".
    Returns:
        list các cặp (w, g) với g: (B, N) -> (B,).
    """
    def delta(a_, b_):
        return lambda x: (lambda z: z[:, cls] - z[:, ADD])(model(a_, b_, x))

    if level == "logit":
        return [(1.0, lambda x: model(a, b, x)[:, cls])]
    if level == "contrast":
        return [(1.0, delta(a, b))]
    assert level == "interaction" and len(ref_drugs) > 1
    R = len(ref_drugs)
    terms = [(1.0, delta(a, b))]
    for i, r in enumerate(ref_drugs):
        r1 = torch.full_like(a, r)
        r2 = torch.full_like(a, ref_drugs[(i + 1) % R])
        terms += [(-1 / R, delta(a, r1)), (-1 / R, delta(r1, b)), (1 / R, delta(r1, r2))]
    return terms


def target_fn(model, a, b, cls, level, ref_drugs=()):
    """Hàm f(x) -> (B,) gộp từ target_terms (dùng để kiểm tra completeness và in giá trị)."""
    terms = target_terms(model, a, b, cls, level, ref_drugs)
    return lambda x: sum(w * g(x) for w, g in terms)


def integrated_gradients(terms, x, steps=32):
    """Integrated Gradients với baseline = 0 (biểu hiện trung bình, vì expr đã z-score).

    IG_g = x_g * mean_k  df/dx_g (k/steps * x),  k = 1..steps  (tổng Riemann bên phải)
    Tính chất completeness: sum_g IG_g ~ f(x) - f(0).

    Args:
        terms: list (w, g) từ target_terms, hoặc một hàm f: (B, N) -> (B,).
        x: (B, N) đầu vào.
    Returns:
        (B, N) điểm attribution cho từng gene.
    """
    if callable(terms):
        terms = [(1.0, terms)]
    total = torch.zeros_like(x)
    for k in range(1, steps + 1):
        for w, g in terms:
            xi = (k / steps * x).detach().requires_grad_(True)
            total += w * torch.autograd.grad(g(xi).sum(), xi)[0]
    return x * total / steps


def attribute(model, data, idx, cls, level, ref_drugs, steps=32, bs=64, device="cpu"):
    """Tính attribution cấp `level` cho các bộ ba `idx`. Trả về tensor (len(idx), N) trên CPU."""
    model.eval()
    out = []
    for s in range(0, len(idx), bs):
        t = data["triplets"][idx[s:s + bs]].to(device)
        x = data["expr"].to(device)[t[:, 2]]
        terms = target_terms(model, t[:, 0], t[:, 1], cls, level, ref_drugs)
        out.append(integrated_gradients(terms, x, steps).cpu())
    return torch.cat(out)
