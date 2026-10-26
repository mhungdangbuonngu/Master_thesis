"""Kill test (Gate 3): explainer có tìm lại được gene cài sẵn trong dữ liệu bán tổng hợp không?

Dữ liệu sinh bởi make_synthetic.py có 3 nhóm gene:
  syn_genes  (Z) : gây HIỆP ĐỒNG, chỉ khi A thuộc S_A và B thuộc S_B   -> tương tác thật
  ant_genes  (W) : gây ĐỐI KHÁNG, chỉ khi A thuộc S_A và B thuộc S_C   -> tương tác thật
  main_genes (M) : thuốc thuộc S_M mạnh lên ở MỌI cặp                 -> hiệu ứng chính, KHÔNG phải tương tác

Bộ ba được chấm: thuộc tập test, có nhãn thật đúng lớp đang xét, cặp thuốc mang tương tác cài sẵn
(S_A x S_B với SYN, S_A x S_C với ANT) VÀ có ít nhất một thuốc thuộc S_M, tức hiệu ứng chính và tương tác
cùng có mặt. Hai chỉ số:
  1. recall@3 : tỷ lệ gene cài sẵn đúng (Z hoặc W) nằm trong top-3 |attribution|  -> càng cao càng tốt
  2. main@3   : tỷ lệ gene hiệu ứng chính M nằm trong top-3                     -> càng THẤP càng tốt
     (explainer coi hiệu ứng chính là "cơ chế hiệp đồng" là đang giải thích sai câu hỏi)

Giả thuyết của thesis: cấp "interaction" có recall@3 tương đương nhưng main@3 thấp hơn hẳn "logit" và "contrast".

Chạy:  python -m src.eval.explain_benchmark --data data/synth.pt --run runs/synth_combo_f0 --gt data/raw_synth/ground_truth.json
"""
import argparse
import json

import numpy as np
import torch

from src.data.dataset import load, make_split
from src.eval.attribution import LEVELS, attribute
from src.model.gnn import ANT, SYN
from src.training.train import build_model


def topk_hit(attr, gene_idx, k=3):
    """Trung bình theo bộ ba của (số gene trong gene_idx lọt top-k |attr|) / min(k, len(gene_idx))."""
    top = attr.abs().topk(k, dim=1).indices
    hits = torch.isin(top, torch.tensor(gene_idx)).sum(1).float()
    return (hits / min(k, len(gene_idx))).mean().item()


def run(data_path, run_dir, gt_path, max_triplets=200, steps=32, seed=0):
    """Tính recall@3 và main@3 cho cả 3 cấp attribution, cho lớp SYN và ANT. Trả về dict kết quả."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data = load(data_path)
    ck = torch.load(f"{run_dir}/model.pt", weights_only=False)
    model = build_model(data, ck["args"]).to(device)
    model.load_state_dict(ck["state"])
    model.eval()
    gt = json.load(open(gt_path))
    gi = {g: i for i, g in enumerate(data["genes"])}
    di = {d: i for i, d in enumerate(data["drugs"])}
    gidx = {k: [gi[g] for g in gt[k]] for k in ("syn_genes", "ant_genes", "main_genes")}
    def in_set(key):
        """Mask (D,) đánh dấu các thuốc thuộc nhóm gt[key]."""
        m = torch.zeros(len(data["drugs"]), dtype=torch.bool)
        m[[di[d] for d in gt[key]]] = True
        return m
    S_A, S_B, S_C, S_M = (in_set(k) for k in ("S_A", "S_B", "S_C", "S_M"))

    _, _, te = make_split(data, ck["args"]["split"], ck["args"]["fold"], seed=ck["args"]["seed"])
    te = torch.tensor(te)
    ref = list(range(len(data["drugs"])))  # tham chiếu = mọi thuốc (E_r lấy trên toàn bộ thuốc)
    rng = np.random.default_rng(seed)
    a_, b_ = data["triplets"][:, 0], data["triplets"][:, 1]
    pair = lambda X, Y: (X[a_] & Y[b_]) | (Y[a_] & X[b_])
    has_main = S_M[a_] | S_M[b_]
    subset = {SYN: pair(S_A, S_B) & has_main, ANT: pair(S_A, S_C) & has_main}

    res = {}
    for cls, name, planted in [(SYN, "syn", "syn_genes"), (ANT, "ant", "ant_genes")]:
        idx = te[(data["y"][te] == cls) & subset[cls][te]]
        idx = idx[rng.permutation(len(idx))[:max_triplets]]
        if len(idx) == 0:
            continue
        for level in LEVELS:
            a = attribute(model, data, idx, cls, level, ref, steps=steps, device=device)
            res[f"{name}/{level}"] = {"n": len(idx), "recall@3": round(topk_hit(a, gidx[planted]), 3),
                                      "main@3": round(topk_hit(a, gidx["main_genes"]), 3)}
            print(f"{name}/{level:12s} n={len(idx):4d}  recall@3 {res[f'{name}/{level}']['recall@3']:.3f}  "
                  f"main@3 {res[f'{name}/{level}']['main@3']:.3f}")
    with open(f"{run_dir}/explain_benchmark.json", "w") as f:
        json.dump(res, f, indent=2)
    return res


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/synth.pt")
    p.add_argument("--run", default="runs/synth_combo_f0")
    p.add_argument("--gt", default="data/raw_synth/ground_truth.json")
    p.add_argument("--max_triplets", type=int, default=200)
    p.add_argument("--steps", type=int, default=32)
    a = p.parse_args()
    run(a.data, a.run, a.gt, a.max_triplets, a.steps)
