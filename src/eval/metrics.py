"""Prediction metrics for the 3-class ordinal label (0 ant, 1 add, 2 syn)."""
import numpy as np
from sklearn.metrics import balanced_accuracy_score, cohen_kappa_score, f1_score

CLASSES = [0, 1, 2]


def prediction_metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    polar = np.isin(y, [0, 2])
    f1 = f1_score(y, p, labels=CLASSES, average=None, zero_division=0)
    return {
        "qwk": cohen_kappa_score(y, p, labels=CLASSES, weights="quadratic"),
        "macro_f1": f1.mean(),
        "balanced_acc": balanced_accuracy_score(y, p),
        "f1_ant": f1[0], "f1_add": f1[1], "f1_syn": f1[2],
        # syn predicted as ant or ant as syn, among true syn/ant
        "polar_error": float((p[polar] == 2 - y[polar]).mean()) if polar.any() else float("nan"),
    }
