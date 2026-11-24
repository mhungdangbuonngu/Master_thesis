"""XGBoost on O'Neil, scored zero-shot on NCI-ALMANAC  (planner 5.3, 7.2).

    python -m src.repro.xgb_external --split random --fold 0 --seed 0

The booster is not saved by src.repro.xgb, so this retrains it with the same arguments (same
seed, same data, same hyper-parameters, so the same model) and then scores ALMANAC. It writes
to runs/xgbext_<...>/ and never touches the original run directory.

Features for ALMANAC are built by the same `features()` as training, with the Morgan
fingerprints of the ALMANAC drugs and expression z-scored with the mean and sd of the O'NEIL
training cells of this fold.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import xgboost as xgb

from src.eval import metrics as M
from src.eval.external import subsets
from src.repro.xgb import features, parse as xgb_parse
from src.train import RUNS, load_all, standardise

PROC = Path(__file__).resolve().parents[2] / "data" / "processed"


def main(a):
    t0 = time.time()
    out = RUNS / (a.name or f"xgbext_{a.setting}_{a.split}_f{a.fold}_s{a.seed}")
    out.mkdir(parents=True, exist_ok=True)
    d, dr, ce, sp = load_all("cpu")
    ext = torch.load(PROC / "almanac.pt", weights_only=False)
    tr_i, va_i, te_i = sp["splits"][a.split][a.fold]

    y_all = d["y"][a.setting]
    assert not a.setting.startswith("bin_gap"), "external table is the 3-class setting"
    y = y_all.long()

    train_cells = torch.unique(d["idx"][tr_i][:, 2])
    expr = standardise(ce["expr"], train_cells).numpy().astype(np.float32)
    mu = ce["expr"][train_cells].mean(0, keepdim=True)
    sd = ce["expr"][train_cells].std(0, keepdim=True).clamp_min(1e-6)
    expr_ext = ((ext["expr"] - mu) / sd).numpy().astype(np.float32)
    fp = dr["fp2"].numpy().astype(np.float32)
    fp_ext = ext["fp2"].numpy().astype(np.float32)
    trip = d["idx"].numpy()

    X = {k: features(trip[i.numpy()], fp, expr) for k, i in (("train", tr_i), ("val", va_i))}
    Y = {k: y[i].numpy() for k, i in (("train", tr_i), ("val", va_i))}
    cnt = np.bincount(Y["train"], minlength=3).astype(float)
    w = (cnt.sum() / (3 * np.maximum(cnt, 1)))[Y["train"]]
    clf = xgb.XGBClassifier(
        n_estimators=a.n_estimators, max_depth=a.max_depth, learning_rate=a.lr,
        subsample=a.subsample, colsample_bytree=a.colsample, tree_method="hist",
        objective="multi:softprob", eval_metric="mlogloss",
        early_stopping_rounds=a.patience, n_jobs=a.n_jobs, random_state=a.seed, verbosity=0)
    clf.fit(X["train"], Y["train"], sample_weight=w, eval_set=[(X["val"], Y["val"])],
            verbose=False)

    yx = ext["y"][a.setting].numpy()
    ok = torch.ones(len(yx), dtype=torch.bool)
    prob = np.zeros((len(yx), 3), dtype=np.float32)
    idx = ext["idx"].numpy()
    for s in np.array_split(np.arange(len(yx)), max(1, len(yx) // 20000)):
        prob[s] = clf.predict_proba(features(idx[s], fp_ext, expr_ext))
    pred = prob.argmax(1)

    res = {"run": out.name, "model": "xgboost", "loss": "xgb", "setting": a.setting,
           "split": a.split, "fold": a.fold, "seed": a.seed, "n_external": int(len(yx)),
           "trees": int(clf.best_iteration), "seconds": round(time.time() - t0, 1)}
    for name, m in subsets(ext, torch.tensor(yx), ok).items():
        i = m.numpy()
        r = {"n": int(i.sum()), **M.ord3(yx[i], pred[i], prob[i])}
        syn, hit = yx[i] == 2, pred[i] == 2
        tp, fn = int((syn & hit).sum()), int((syn & ~hit).sum())
        tn, fp_ = int((~syn & ~hit).sum()), int((~syn & hit).sum())
        r["syn_vs_rest"] = {**M.binary(syn.astype(int), prob[i][:, 2]),
                            "bacc_argmax": 0.5 * (tp / max(tp + fn, 1) + tn / max(tn + fp_, 1))}
        res[name] = r
    # The same control as src/eval/external.py: on the triples both studies ran, score the SAME
    # predictions against O'Neil's label instead of ALMANAC's.
    if a.setting.startswith("ord3"):
        i = subsets(ext, torch.tensor(yx), ok)["measured_by_both"].numpy()
        yo = ext["oneil_ord3_loewe"].numpy()[i]
        res["measured_by_both_vs_oneil_label"] = {"n": int(i.sum()),
                                                  **M.ord3(yo, pred[i], prob[i])}
    np.savez_compressed(out / "pred_almanac.npz", prob=prob, pred=pred)
    (out / "external_almanac.json").write_text(json.dumps(res, indent=1))
    # a config.json so load_runs() can see the run; metrics.json stays out, since the O'Neil
    # numbers of this model are already reported by the real xgboost run
    (out / "config.json").write_text(json.dumps({**vars(a), "model": "xgboost", "loss": "xgb",
                                                 "run": out.name}, indent=1))
    print(f"{out.name:52s} almanac_qwk {res['all']['qwk']:.4f}  "
          f"unseen_pair {res['unseen_pair']['qwk']:.4f}  ({res['seconds']:.0f}s)")
    return res


if __name__ == "__main__":
    p = argparse.ArgumentParser(parents=[], add_help=True)
    base = xgb_parse([])
    for k, v in vars(base).items():
        p.add_argument(f"--{k.replace('_', '-')}", type=type(v) if v is not None else str,
                       default=v)
    main(p.parse_args())
