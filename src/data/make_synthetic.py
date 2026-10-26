"""Sinh bộ dữ liệu BÁN TỔNG HỢP có ground truth cài sẵn (benchmark §2.5 trong danh_gia_kha_thi_thesis.md).

Mục đích:
  1. Chạy thử toàn bộ pipeline khi chưa có dữ liệu thật.
  2. Kiểm chứng explainer: biết trước gene nào gây hiệp đồng / đối kháng / chỉ là hiệu ứng chính,
     từ đó đo được explainer có "tìm đúng" hay không.

Đầu ra (cùng định dạng với dữ liệu thật mà prepare.py đọc):
  <out>/combos.csv        drug_row, drug_col, cell_line_name, synergy_loewe
  <out>/expression.csv    hàng = dòng tế bào, cột = gene
  <out>/targets.csv       drug, gene
  <out>/ppi.csv           gene1, gene2
  <out>/ground_truth.json gene và nhóm thuốc được cài sẵn

Chạy:  python -m src.data.make_synthetic --out data/raw_synth
"""
import argparse
import json
import os

import numpy as np
import pandas as pd


def generate(out, n_genes=300, n_cells=300, n_drugs=24, seed=0):
    """Sinh dữ liệu và ghi ra thư mục `out`.

    Quy tắc tạo synergy score (score > 10 là hiệp đồng, < -10 là đối kháng):
      - Tương tác hiệp đồng : A thuộc S_A và B thuộc S_B -> +30 * relu(mean expr[Z])
      - Tương tác đối kháng : A thuộc S_A và B thuộc S_C -> -30 * relu(mean expr[W])
      - Hiệu ứng chính      : mỗi thuốc thuộc S_M        -> +20 * mean expr[M]
        (thuốc "hiệp đồng với mọi đối tác": KHÔNG phải tương tác, explainer cấp tương tác phải bỏ qua M)
      - Nhiễu Gauss N(0, 4)

    Args:
        out: thư mục ghi file.
        n_genes, n_cells, n_drugs: kích thước dữ liệu (n_drugs >= 20, n_genes >= 12).
        seed: hạt ngẫu nhiên.
    """
    assert n_drugs >= 20 and n_genes >= 12
    rng = np.random.default_rng(seed)
    genes = [f"G{i}" for i in range(n_genes)]
    drugs = [f"D{i}" for i in range(n_drugs)]
    cells = [f"C{i}" for i in range(n_cells)]
    Z, W, M = [0, 1, 2], [3, 4, 5], [6, 7, 8]  # gene cài sẵn
    S_A, S_B, S_C = set(range(0, 6)), set(range(6, 12)), set(range(12, 16))
    # S_M giao một phần với S_A, S_B: cặp có tương tác thật cũng mang hiệu ứng chính -> explainer phải tách được 2 loại
    S_M = {4, 5, 10, 11, 16, 17, 18, 19}

    expr = rng.standard_normal((n_cells, n_genes))
    # PPI ngẫu nhiên: mỗi gene nối tới 4 gene khác
    edges = {(i, int(j)) for i in range(n_genes) for j in rng.choice(n_genes, 4, replace=False) if i != j}
    # Mỗi thuốc có 3 target, không trùng gene cài sẵn (để explainer không "ăn gian" qua target)
    targets = [(d, genes[g]) for d in drugs for g in rng.choice(np.arange(9, n_genes), 3, replace=False)]

    z = np.maximum(expr[:, Z].mean(1), 0)
    w = np.maximum(expr[:, W].mean(1), 0)
    m = expr[:, M].mean(1)
    rows = []
    for c in range(n_cells):
        for a in range(n_drugs):
            for b in range(a + 1, n_drugs):
                def pair(s1, s2):
                    return (a in s1 and b in s2) or (a in s2 and b in s1)
                s = (30 * pair(S_A, S_B) * z[c] - 30 * pair(S_A, S_C) * w[c]
                     + 20 * ((a in S_M) + (b in S_M)) * m[c] + rng.normal(0, 4))
                rows.append((drugs[a], drugs[b], cells[c], s))

    os.makedirs(out, exist_ok=True)
    pd.DataFrame(rows, columns=["drug_row", "drug_col", "cell_line_name", "synergy_loewe"]).to_csv(
        f"{out}/combos.csv", index=False)
    pd.DataFrame(expr, index=cells, columns=genes).to_csv(f"{out}/expression.csv")
    pd.DataFrame(targets, columns=["drug", "gene"]).to_csv(f"{out}/targets.csv", index=False)
    pd.DataFrame([(genes[i], genes[j]) for i, j in edges], columns=["gene1", "gene2"]).to_csv(
        f"{out}/ppi.csv", index=False)
    names = lambda idx: [drugs[i] for i in sorted(idx)]
    gt = {"syn_genes": [genes[i] for i in Z], "ant_genes": [genes[i] for i in W],
          "main_genes": [genes[i] for i in M],
          "S_A": names(S_A), "S_B": names(S_B), "S_C": names(S_C), "S_M": names(S_M)}
    with open(f"{out}/ground_truth.json", "w") as f:
        json.dump(gt, f, indent=2)
    print(f"wrote {len(rows)} triplets to {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/raw_synth")
    p.add_argument("--genes", type=int, default=300)
    p.add_argument("--cells", type=int, default=300)  # 40 cell thì model chỉ nhớ danh tính cell, không học gene Z
    p.add_argument("--drugs", type=int, default=24)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()
    generate(a.out, a.genes, a.cells, a.drugs, a.seed)
