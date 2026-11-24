"""Metrics for the three label settings (planner 3.3, 6.5 of the survey).

Ordinal 3-class is the main setting, so QWK leads and accuracy is never reported alone:
69.9% of O'Neil triples are `additive` under Loewe +-10, so predicting one class scores high.
`polar` is the share of test triples confused between syn and ant - the clinically dangerous
error that plain cross-entropy treats like any other (planner RQ2).
"""
import numpy as np
from sklearn.metrics import (average_precision_score, cohen_kappa_score, confusion_matrix,
                             f1_score, roc_auc_score)

ANT, ADD, SYN = 0, 1, 2


def ord3(y, pred, prob=None):
    y, pred = np.asarray(y), np.asarray(pred)
    cm = confusion_matrix(y, pred, labels=[0, 1, 2])
    n = max(len(y), 1)
    polar = (cm[ANT, SYN] + cm[SYN, ANT]) / n
    adjacent = (cm[ANT, ADD] + cm[ADD, ANT] + cm[ADD, SYN] + cm[SYN, ADD]) / n
    out = {"qwk": cohen_kappa_score(y, pred, weights="quadratic", labels=[0, 1, 2]),
           "kappa": cohen_kappa_score(y, pred, labels=[0, 1, 2]),
           "macro_f1": f1_score(y, pred, average="macro", labels=[0, 1, 2], zero_division=0),
           "mae": float(np.abs(y - pred).mean()),
           "acc": float((y == pred).mean()),
           "bacc": float(np.mean([(pred[y == c] == c).mean() if (y == c).any() else np.nan
                                  for c in (0, 1, 2)])),
           "polar_error": float(polar), "adjacent_error": float(adjacent),
           "confusion": cm.tolist()}
    for c, name in ((ANT, "ant"), (ADD, "add"), (SYN, "syn")):
        m = y == c
        out[f"f1_{name}"] = f1_score(y == c, pred == c, zero_division=0)
        out[f"recall_{name}"] = float((pred[m] == c).mean()) if m.any() else np.nan
        if prob is not None and m.any() and (~m).any():
            out[f"auprc_{name}"] = average_precision_score(m, prob[:, c])
            out[f"auroc_{name}"] = roc_auc_score(m, prob[:, c])
    if prob is not None:
        out["macro_auroc"] = float(np.nanmean([out.get(f"auroc_{n}", np.nan)
                                               for n in ("ant", "add", "syn")]))
    return out


def binary(y, prob, thr=0.5):
    y = np.asarray(y)
    pred = (prob >= thr).astype(int)
    cm = confusion_matrix(y, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    return {"auroc": roc_auc_score(y, prob) if len(set(y)) > 1 else np.nan,
            "auprc": average_precision_score(y, prob) if len(set(y)) > 1 else np.nan,
            "acc": float((y == pred).mean()),
            "bacc": float(0.5 * (tp / max(tp + fn, 1) + tn / max(tn + fp, 1))),
            "prec": float(tp / max(tp + fp, 1)), "tpr": float(tp / max(tp + fn, 1)),
            "kappa": cohen_kappa_score(y, pred, labels=[0, 1]),
            "f1": f1_score(y, pred, zero_division=0), "confusion": cm.tolist()}


def main_metric(setting):
    """What early stopping and model selection watch."""
    return "qwk" if setting.startswith("ord3") else "auprc"


def bootstrap_ci(values, n=2000, seed=0):
    v = np.asarray([x for x in values if np.isfinite(x)])
    if len(v) < 2:
        return float(np.mean(v)) if len(v) else np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    bs = v[rng.integers(0, len(v), (n, len(v)))].mean(1)
    return float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
