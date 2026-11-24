"""XGBoost baseline on Morgan fingerprints + expression  (planner 5.3).

    python -m src.repro.xgb --setting ord3_loewe --split leave_combo --fold 0 --seed 0

Gradient-boosted trees do not fit SynGT's epoch loop, so this script has its own training
path. Everything that could bias the comparison is kept identical to `src.train`:
  * the same splits.pt folds, and the same validation subset of each fold
  * z-score fitted on the TRAINING cell lines only
  * the same label settings, including dropping the neutral band for bin_gap
  * the same metrics module and the same runs/<name>/{config,metrics,pred} contract
Features are symmetric in A <-> B by construction, like every other model in the table:
    [ fp(A) + fp(B) ,  |fp(A) - fp(B)| ,  expression ]
Early stopping uses XGBoost's own validation loss (mlogloss / logloss); the reported model is
the best iteration, and `best_epoch` in config.json is that iteration.
"""
import argparse
import json
import time

import numpy as np
import torch
import xgboost as xgb

from src.eval import metrics as M
from src.train import RUNS, load_all, standardise


def parse(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--setting", default="ord3_loewe")
    p.add_argument("--split", default="leave_combo")
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-estimators", type=int, default=2000)
    p.add_argument("--max-depth", type=int, default=6)
    p.add_argument("--lr", type=float, default=0.05)
    p.add_argument("--subsample", type=float, default=0.8)
    p.add_argument("--colsample", type=float, default=0.3)
    p.add_argument("--patience", type=int, default=50)
    p.add_argument("--n-jobs", type=int, default=2)
    p.add_argument("--name", default="")
    return p.parse_args(argv)


def run_name(a):
    return a.name or f"xgboost_{a.setting}_{a.split}_f{a.fold}_s{a.seed}"


def features(trip, fp, expr):
    """[fp(A)+fp(B) ; |fp(A)-fp(B)| ; expression] - symmetric in A <-> B."""
    a, b = fp[trip[:, 0]], fp[trip[:, 1]]
    return np.concatenate([(a + b), np.abs(a - b), expr[trip[:, 2]]], 1).astype(np.float32)


def main(a):
    t0 = time.time()
    out = RUNS / run_name(a)
    out.mkdir(parents=True, exist_ok=True)
    d, dr, ce, sp = load_all("cpu")
    tr_i, va_i, te_i = sp["splits"][a.split][a.fold]

    y_all = d["y"][a.setting]
    if a.setting.startswith("bin_gap"):                 # the neutral band leaves every subset
        ok = ~torch.isnan(y_all)
        tr_i, va_i, te_i = [i[ok[i]] for i in (tr_i, va_i, te_i)]
        y = torch.nan_to_num(y_all).long()
    else:
        y = y_all.long()

    train_cells = torch.unique(d["idx"][tr_i][:, 2])
    expr = standardise(ce["expr"], train_cells).numpy().astype(np.float32)
    fp = dr["fp2"].numpy().astype(np.float32)
    trip = d["idx"].numpy()

    X = {k: features(trip[i.numpy()], fp, expr) for k, i in
         (("train", tr_i), ("val", va_i), ("test", te_i))}
    Y = {k: y[i].numpy() for k, i in (("train", tr_i), ("val", va_i), ("test", te_i))}

    binary = a.setting.startswith("bin")
    n_cls = 2 if binary else 3
    cnt = np.bincount(Y["train"], minlength=n_cls).astype(float)
    w = (cnt.sum() / (n_cls * np.maximum(cnt, 1)))[Y["train"]]      # same class weighting
    clf = xgb.XGBClassifier(
        n_estimators=a.n_estimators, max_depth=a.max_depth, learning_rate=a.lr,
        subsample=a.subsample, colsample_bytree=a.colsample, tree_method="hist",
        objective="binary:logistic" if binary else "multi:softprob",
        eval_metric="logloss" if binary else "mlogloss",
        early_stopping_rounds=a.patience, n_jobs=a.n_jobs, random_state=a.seed, verbosity=0)
    clf.fit(X["train"], Y["train"], sample_weight=w,
            eval_set=[(X["val"], Y["val"])], verbose=False)

    def score(k):
        p = clf.predict_proba(X[k])
        if binary:
            return M.binary(Y[k], p[:, 1]), {"prob": p[:, 1]}
        return M.ord3(Y[k], p.argmax(1), p), {"prob": p, "pred": p.argmax(1)}

    test, extra = score("test")
    val, _ = score("val")
    np.savez_compressed(out / "pred.npz", test_idx=te_i.numpy(), y=Y["test"], **extra)
    cfg = {**vars(a), "model": "xgboost", "run": out.name, "loss": "xgb",
           "gnn": None, "gene_emb": None, "readout": None,
           "n_params": int(clf.get_booster().trees_to_dataframe().shape[0]),
           "n_train": len(tr_i), "n_val": len(va_i), "n_test": len(te_i),
           "train_cells": int(len(train_cells)), "best_epoch": int(clf.best_iteration),
           "epochs_run": int(clf.best_iteration) + 1, "n_features": X["train"].shape[1],
           "seconds": time.time() - t0}
    (out / "config.json").write_text(json.dumps(cfg, indent=1))
    (out / "metrics.json").write_text(json.dumps({"test": test, "val": val}, indent=1))
    key = M.main_metric(a.setting)
    print(f"{out.name}  val_{key} {val[key]:.4f}  test_{key} {test[key]:.4f}  "
          f"({clf.best_iteration} trees, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main(parse())
