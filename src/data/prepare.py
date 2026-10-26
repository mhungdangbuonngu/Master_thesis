"""Chuyển 4 file CSV thô thành một file tensor duy nhất (.pt) cho training.

Đầu vào trong <raw>/ (dữ liệu thật hoặc từ make_synthetic.py):
  combos.csv      drug_row, drug_col, cell_line_name, <cột score, ví dụ synergy_loewe>
                  (đúng tên cột của bảng summary DrugComb)
  expression.csv  hàng = dòng tế bào (trùng tên cell_line_name), cột = gene
  targets.csv     drug, gene
  ppi.csv         gene1, gene2

Chạy:  python -m src.data.prepare --raw data/raw_synth --out data/synth.pt
"""
import argparse

import numpy as np
import pandas as pd
import torch


def to_labels(score, thr):
    """Synergy score -> nhãn 3 lớp có thứ tự: 0 = antagonistic, 1 = additive, 2 = synergistic."""
    return np.where(score > thr, 2, np.where(score < -thr, 0, 1))


def print_label_distribution(combos):
    """In phân bố 3 lớp cho mọi cột synergy_* x ngưỡng 5/10/20 (dùng cho Gate 1)."""
    for col in [c for c in combos.columns if c.startswith("synergy_")]:
        s = combos[col].dropna().to_numpy()
        for thr in (5, 10, 20):
            n = np.bincount(to_labels(s, thr), minlength=3)
            print(f"{col:16s} thr=+-{thr:<3d} ant/add/syn = {n.tolist()}  ({np.round(n / n.sum() * 100, 1).tolist()} %)")


def normalized_adjacency(genes, ppi):
    """Ma trận kề chuẩn hóa kiểu GCN: D^-1/2 (A + I) D^-1/2, trả về sparse tensor (N, N)."""
    idx = {g: i for i, g in enumerate(genes)}
    n = len(genes)
    A = torch.eye(n)
    for u, v in zip(ppi.gene1, ppi.gene2):
        if u in idx and v in idx:
            A[idx[u], idx[v]] = A[idx[v], idx[u]] = 1.0
    d = A.sum(1).rsqrt()
    return (d[:, None] * A * d[None, :]).to_sparse()


def build(raw, out, score_col="synergy_loewe", thr=10.0, max_genes=1000):
    """Đọc CSV thô, lọc và ghép, rồi lưu dict tensor ra `out`.

    Các khóa của file .pt đầu ra:
      genes, drugs, cells : list tên
      adj     : sparse (N, N), ma trận kề PPI đã chuẩn hóa
      expr    : (C, N) biểu hiện gene đã z-score theo từng gene
      targets : (D, N) ma trận 0/1, thuốc d có target là gene g
      triplets: (M, 3) chỉ số [drug_a, drug_b, cell]
      score   : (M,) synergy score (trung bình nếu bộ ba lặp lại)
      y       : (M,) nhãn 3 lớp

    Chọn gene: giao giữa expression và PPI; luôn giữ gene target, phần còn lại lấy theo phương sai cao nhất.
    """
    combos = pd.read_csv(f"{raw}/combos.csv")
    expr = pd.read_csv(f"{raw}/expression.csv", index_col=0)
    tg = pd.read_csv(f"{raw}/targets.csv")
    ppi = pd.read_csv(f"{raw}/ppi.csv")

    print_label_distribution(combos)
    combos = combos.dropna(subset=[score_col])
    combos = combos[combos.cell_line_name.isin(expr.index)]

    ppi_genes = set(ppi.gene1) | set(ppi.gene2)
    genes = [g for g in expr.columns if g in ppi_genes]
    target_genes = [g for g in genes if g in set(tg.gene)]
    by_var = [g for g in expr[genes].var().sort_values(ascending=False).index if g not in set(target_genes)]
    genes = sorted(target_genes + by_var[:max(0, max_genes - len(target_genes))])
    gidx = {g: i for i, g in enumerate(genes)}

    drugs = sorted(set(combos.drug_row) | set(combos.drug_col))
    didx = {d: i for i, d in enumerate(drugs)}
    cells = sorted(combos.cell_line_name.unique())
    cidx = {c: i for i, c in enumerate(cells)}

    targets = torch.zeros(len(drugs), len(genes))
    for d, g in zip(tg.drug, tg.gene):
        if d in didx and g in gidx:
            targets[didx[d], gidx[g]] = 1.0

    e = expr.loc[cells, genes].to_numpy(dtype=np.float32)
    e = (e - e.mean(0)) / (e.std(0) + 1e-8)

    # Gộp bộ ba trùng (A,B,c) và (B,A,c) bằng trung bình score
    a = combos.drug_row.map(didx).to_numpy()
    b = combos.drug_col.map(didx).to_numpy()
    df = pd.DataFrame({"a": np.minimum(a, b), "b": np.maximum(a, b),
                       "c": combos.cell_line_name.map(cidx).to_numpy(), "s": combos[score_col].to_numpy()})
    df = df[df.a != df.b].groupby(["a", "b", "c"], as_index=False).s.mean()

    data = {
        "genes": genes, "drugs": drugs, "cells": cells,
        "adj": normalized_adjacency(genes, ppi),
        "expr": torch.tensor(e),
        "targets": targets,
        "triplets": torch.tensor(df[["a", "b", "c"]].to_numpy(), dtype=torch.long),
        "score": torch.tensor(df.s.to_numpy(), dtype=torch.float32),
        "y": torch.tensor(to_labels(df.s.to_numpy(), thr), dtype=torch.long),
        "meta": {"score_col": score_col, "thr": thr},
    }
    torch.save(data, out)
    print(f"saved {out}: {len(df)} triplets, {len(drugs)} drugs, {len(cells)} cells, {len(genes)} genes, "
          f"label counts ant/add/syn = {torch.bincount(data['y'], minlength=3).tolist()}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--raw", default="data/raw_synth")
    p.add_argument("--out", default="data/synth.pt")
    p.add_argument("--score", default="synergy_loewe")
    p.add_argument("--thr", type=float, default=10.0)
    p.add_argument("--max_genes", type=int, default=1000)
    a = p.parse_args()
    build(a.raw, a.out, a.score, a.thr, a.max_genes)
