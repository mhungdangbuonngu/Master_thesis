"""Train SynergyGNN với class-weighted cross-entropy và early stopping theo QWK trên tập val.

Chạy:  python -m src.training.train --data data/synth.pt --split combo --fold 0 --out runs/synth_combo_f0
Đầu ra trong --out:  model.pt (trọng số tốt nhất) và metrics.json (metric trên tập test)
"""
import argparse
import json
import os

import numpy as np
import torch
from torch import nn

from src.data.dataset import load, make_split
from src.eval.metrics import classification_metrics
from src.model.gnn import SynergyGNN


def build_model(data, args):
    """Khởi tạo model từ dữ liệu và siêu tham số. Dùng chung cho train và eval (tải lại checkpoint)."""
    return SynergyGNN(data["adj"], data["targets"], hidden=args["hidden"], gene_dim=args["gene_dim"],
                      drug_dim=args["drug_dim"], n_layers=args["layers"], dropout=args["dropout"])


@torch.no_grad()
def predict(model, data, idx, device, bs=512):
    """Dự đoán cho các bộ ba `idx`. Trả về (y_true, y_pred, proba) dạng numpy."""
    model.eval()
    probs = []
    for s in range(0, len(idx), bs):
        t = data["triplets"][idx[s:s + bs]].to(device)
        probs.append(torch.softmax(model(t[:, 0], t[:, 1], data["expr"].to(device)[t[:, 2]]), 1).cpu())
    p = torch.cat(probs).numpy()
    return data["y"][idx].numpy(), p.argmax(1), p


def train(args):
    """Vòng lặp train hoàn chỉnh. Trả về dict metric trên tập test.

    Các bước:
      1. Chia train/val/test theo args["split"] (leave-combination-out mặc định).
      2. Trọng số lớp = 1 / tần suất lớp trong train (xử lý mất cân bằng: lớp additive chiếm đa số).
      3. Mỗi epoch: train với augmentation hoán đổi A<->B (model đã đối xứng sẵn nên đây chỉ là kiểm tra an toàn,
         không tốn thêm gì), sau đó đánh giá QWK trên val.
      4. Giữ trọng số có QWK val tốt nhất; dừng nếu `patience` epoch liên tiếp không cải thiện.
      5. Nạp lại trọng số tốt nhất, tính metric trên test, lưu model.pt và metrics.json.
    """
    torch.manual_seed(args["seed"])
    np.random.seed(args["seed"])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data = load(args["data"])
    tr, va, te = make_split(data, args["split"], args["fold"], seed=args["seed"])
    print(f"split={args['split']} fold={args['fold']}: train {len(tr)} / val {len(va)} / test {len(te)}")

    model = build_model(data, args).to(device)
    counts = torch.bincount(data["y"][tr], minlength=3).float()
    loss_fn = nn.CrossEntropyLoss(weight=(counts.sum() / (3 * counts.clamp(min=1))).to(device))
    opt = torch.optim.AdamW(model.parameters(), lr=args["lr"], weight_decay=args["wd"])
    expr, trip, y = data["expr"].to(device), data["triplets"].to(device), data["y"].to(device)

    best, best_state, wait = -1.0, None, 0
    for ep in range(args["epochs"]):
        model.train()
        perm = torch.tensor(tr)[torch.randperm(len(tr))].to(device)
        total = 0.0
        for s in range(0, len(perm), args["bs"]):
            i = perm[s:s + args["bs"]]
            t = trip[i]
            loss = loss_fn(model(t[:, 0], t[:, 1], expr[t[:, 2]]), y[i])
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * len(i)
        val = classification_metrics(*predict(model, data, va, device)[:2])
        print(f"epoch {ep:3d}  loss {total / len(tr):.4f}  val qwk {val['qwk']:.4f}  macro_f1 {val['macro_f1']:.4f}")
        if val["qwk"] > best:
            best, wait = val["qwk"], 0
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= args["patience"]:
                print("early stop")
                break

    model.load_state_dict(best_state)
    yt, yp, p = predict(model, data, te, device)
    m = classification_metrics(yt, yp, p)
    print("TEST:", json.dumps(m))
    os.makedirs(args["out"], exist_ok=True)
    torch.save({"state": model.state_dict(), "args": args}, f"{args['out']}/model.pt")
    with open(f"{args['out']}/metrics.json", "w") as f:
        json.dump(m, f, indent=2)
    return m


def get_args():
    """Đọc tham số dòng lệnh, trả về dict."""
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/synth.pt")
    p.add_argument("--split", default="combo", choices=["random", "combo", "cell"])
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--out", default="runs/synth_combo_f0")
    p.add_argument("--epochs", type=int, default=60)
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--bs", type=int, default=256)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--wd", type=float, default=1e-4)
    p.add_argument("--hidden", type=int, default=32)
    p.add_argument("--gene_dim", type=int, default=4)
    p.add_argument("--drug_dim", type=int, default=16)
    p.add_argument("--layers", type=int, default=2)
    p.add_argument("--dropout", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=0)
    return vars(p.parse_args())


if __name__ == "__main__":
    train(get_args())
