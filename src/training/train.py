"""Train one model on one (network, seed, fold); writes config.json, metrics.json, model.pt.

python -m src.training.train --model gnn --network real --seed 0 --fold 0
networks (gnn only): real | rew1 | rew2 | none   (rew1/rew2: independent degree-preserving
rewirings, regenerated per seed; none: m = 0, self-loops only)
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

from src.data import dataset
from src.data.rewire import rewire
from src.eval.metrics import prediction_metrics
from src.model.gnn import SynergyGNN
from src.training.baselines import DeepSynergyMLP, OneHotMLP

RUNS = Path(__file__).resolve().parents[2] / "runs"


def build_model(a, data):
    if a.model == "onehot":
        return OneHotMLP(len(data["drugs"]), len(data["cells"]), dropout=a.dropout)
    if a.model == "deepsyn":
        return DeepSynergyMLP(data["expr"], data["targets"], dropout=a.dropout)
    edges = data["edge_index"]
    if a.network in ("rew1", "rew2"):
        edges = rewire(edges, seed={"rew1": 1000, "rew2": 2000}[a.network] + a.seed)
    return SynergyGNN(data["expr"], data["targets"], edges, hidden=a.hidden, proj=a.proj,
                      mlp=a.mlp, dropout=a.dropout)


def forward(model, a, trip):
    if a.model == "gnn" and a.network == "none":
        return model(trip, torch.zeros(model.edge_index.shape[1], device=trip.device))
    return model(trip)


@torch.no_grad()
def predict(model, a, trip):
    model.eval()
    return torch.cat([forward(model, a, t).argmax(1) for t in trip.split(1024)]).cpu().numpy()


def main(a):
    torch.manual_seed(a.seed)
    np.random.seed(a.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    data = dataset.load()
    trip = data["triples"]
    y = dataset.labels(data["scores"][a.score], a.threshold)
    tr, va, te = dataset.leave_combo_split(trip, a.fold, a.seed)
    trip, y = trip.to(dev), y.to(dev)
    model = build_model(a, data).to(dev)

    freq = torch.bincount(y[tr], minlength=3).float()
    loss_fn = nn.CrossEntropyLoss(weight=(freq.sum() / (3 * freq.clamp(min=1))))
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.wd)

    name = a.name or f"{a.model}_{a.network if a.model == 'gnn' else 'na'}_{a.score}{a.threshold:g}_s{a.seed}_f{a.fold}"
    out = RUNS / name
    out.mkdir(parents=True, exist_ok=True)
    cfg = {**vars(a), "n_params": sum(p.numel() for p in model.parameters()),
           "n_train": len(tr), "n_val": len(va), "n_test": len(te), "data_config": data["config"]}
    (out / "config.json").write_text(json.dumps(cfg, indent=2))

    best, best_epoch, history, t0 = -np.inf, 0, [], time.time()
    tr_t = torch.as_tensor(tr, device=dev)
    for epoch in range(a.epochs):
        model.train()
        total = 0.0
        for b in tr_t[torch.randperm(len(tr_t), device=dev)].split(a.batch):
            loss = loss_fn(forward(model, a, trip[b]), y[b])
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * len(b)
        ytr = y[tr].cpu().numpy()
        m_tr = prediction_metrics(ytr, predict(model, a, trip[tr]))["qwk"]
        m_va = prediction_metrics(y[va].cpu().numpy(), predict(model, a, trip[va]))["qwk"]
        history.append({"epoch": epoch, "loss": total / len(tr), "train_qwk": m_tr, "val_qwk": m_va})
        print(f"epoch {epoch:3d} loss {total / len(tr):.4f} train_qwk {m_tr:.3f} val_qwk {m_va:.3f}", flush=True)
        if m_va > best:
            best, best_epoch = m_va, epoch
            torch.save(model.state_dict(), out / "model.pt")
        elif epoch - best_epoch >= a.patience:
            break

    model.load_state_dict(torch.load(out / "model.pt"))
    res = {"best_epoch": best_epoch, "seconds": time.time() - t0, "history": history,
           "val": prediction_metrics(y[va].cpu().numpy(), predict(model, a, trip[va])),
           "test": prediction_metrics(y[te].cpu().numpy(), predict(model, a, trip[te]))}
    (out / "metrics.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res["test"], indent=2))


def parse(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=["gnn", "onehot", "deepsyn"], default="gnn")
    p.add_argument("--network", choices=["real", "rew1", "rew2", "none"], default="real")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--score", choices=["loewe", "bliss", "zip", "hsa"], default="loewe")
    p.add_argument("--threshold", type=float, default=10)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--wd", type=float, default=1e-4)
    p.add_argument("--dropout", type=float, default=0.4)
    p.add_argument("--hidden", type=int, default=16)
    p.add_argument("--proj", type=int, default=2)
    p.add_argument("--mlp", type=int, default=64)
    p.add_argument("--batch", type=int, default=256)
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--name", default="")
    return p.parse_args(argv)


if __name__ == "__main__":
    main(parse())
