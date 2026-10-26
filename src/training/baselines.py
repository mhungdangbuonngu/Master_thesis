"""Baseline bắt buộc cho Gate 2: model GNN phải thắng các baseline này trên CÙNG một split.

  majority  : luôn đoán lớp đa số của tập train
  cell_only : Logistic Regression chỉ dùng biểu hiện gene của dòng tế bào (bỏ qua thuốc).
              Nếu GNN không thắng baseline này thì model chưa học được gì về cặp thuốc.
  mlp       : MLP kiểu DeepSynergy trên [expr, tA + tB, tA * tB] (đối xứng, không dùng đồ thị)

Chạy:  python -m src.training.baselines --data data/synth.pt --split combo --fold 0
"""
import argparse
import json

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

from src.data.dataset import load, make_split
from src.eval.metrics import classification_metrics


def features(data, idx, use_drugs=True):
    """Ghép đặc trưng phẳng cho các bộ ba `idx`: expr của cell, kèm (tA + tB, tA * tB) nếu use_drugs."""
    t = data["triplets"][idx]
    x = [data["expr"][t[:, 2]]]
    if use_drugs:
        ta, tb = data["targets"][t[:, 0]], data["targets"][t[:, 1]]
        x += [ta + tb, ta * tb]
    return torch.cat(x, 1).numpy()


def run_baselines(data_path, split, fold, seed=0):
    """Train và đánh giá 3 baseline, trả về dict {tên: metric trên test}."""
    data = load(data_path)
    tr, _, te = make_split(data, split, fold, seed=seed)
    y = data["y"].numpy()
    out = {"majority": classification_metrics(y[te], np.full(len(te), np.bincount(y[tr]).argmax()))}

    lr = LogisticRegression(max_iter=2000, class_weight="balanced")
    lr.fit(features(data, tr, use_drugs=False), y[tr])
    out["cell_only"] = classification_metrics(y[te], lr.predict(features(data, te, use_drugs=False)))

    # ponytail: MLP sklearn không có class weight; đủ làm mốc tham chiếu, chuyển sang torch nếu cần mạnh hơn
    mlp = MLPClassifier(hidden_layer_sizes=(256, 64), early_stopping=True, max_iter=200, random_state=seed)
    mlp.fit(features(data, tr), y[tr])
    out["mlp"] = classification_metrics(y[te], mlp.predict(features(data, te)), mlp.predict_proba(features(data, te)))

    for k, m in out.items():
        print(f"{k:10s} qwk {m['qwk']:.4f}  macro_f1 {m['macro_f1']:.4f}  polar_err {m['polar_error']:.4f}")
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/synth.pt")
    p.add_argument("--split", default="combo", choices=["random", "combo", "cell"])
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--out", default=None, help="file json để lưu kết quả (tùy chọn)")
    a = p.parse_args()
    res = run_baselines(a.data, a.split, a.fold)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(res, f, indent=2)
