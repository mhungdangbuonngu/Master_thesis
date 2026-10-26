"""Metric cho bài toán phân lớp 3 lớp có thứ tự và mất cân bằng (khảo sát §6.5)."""
import numpy as np
from sklearn.metrics import (balanced_accuracy_score, cohen_kappa_score, confusion_matrix, f1_score,
                             roc_auc_score)


def classification_metrics(y_true, y_pred, proba=None):
    """Tính bộ metric chính.

    Args:
        y_true, y_pred: mảng nhãn {0 = ant, 1 = add, 2 = syn}.
        proba: (n, 3) xác suất dự đoán (tùy chọn, dùng để tính macro-AUROC).
    Returns:
        dict gồm:
          qwk         : Quadratic Weighted Kappa (metric chính, phạt lỗi theo bình phương khoảng cách thứ tự)
          macro_f1, bacc
          f1_ant/add/syn: F1 riêng từng lớp
          polar_error : tỷ lệ nhầm cực (syn <-> ant), loại lỗi nguy hiểm nhất
          adjacent_error: tỷ lệ nhầm liền kề (syn <-> add, add <-> ant)
          confusion   : ma trận nhầm lẫn 3x3 (hàng = nhãn thật)
          macro_auroc : chỉ có khi truyền proba
    """
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    f1 = f1_score(y_true, y_pred, average=None, labels=[0, 1, 2], zero_division=0)
    dist = np.abs(y_true - y_pred)
    m = {
        "qwk": cohen_kappa_score(y_true, y_pred, weights="quadratic"),
        "macro_f1": f1.mean(),
        "bacc": balanced_accuracy_score(y_true, y_pred),
        "f1_ant": f1[0], "f1_add": f1[1], "f1_syn": f1[2],
        "polar_error": (dist == 2).mean(),
        "adjacent_error": (dist == 1).mean(),
        "confusion": confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist(),
    }
    if proba is not None and len(np.unique(y_true)) == 3:
        m["macro_auroc"] = roc_auc_score(y_true, proba, multi_class="ovr", average="macro")
    return {k: (round(float(v), 4) if np.isscalar(v) else v) for k, v in m.items()}
