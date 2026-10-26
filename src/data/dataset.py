"""Đọc file .pt đã chuẩn bị và chia train/val/test theo 3 kiểu split."""
import numpy as np
import torch


def load(path):
    """Đọc dict dữ liệu do prepare.py tạo ra (file do chính mình sinh nên dùng weights_only=False)."""
    return torch.load(path, weights_only=False)


def make_split(data, kind="combo", fold=0, n_folds=5, val_frac=0.1, seed=0):
    """Chia chỉ số bộ ba thành (train, val, test).

    kind:
      "random": chia ngẫu nhiên từng bộ ba (chỉ để so với số liệu đã công bố, dễ rò rỉ thông tin)
      "combo" : leave-drug-combination-out, cặp thuốc ở test không xuất hiện trong train
      "cell"  : leave-cell-line-out, dòng tế bào ở test không xuất hiện trong train
    Cách làm: gán mỗi nhóm (cặp thuốc / dòng tế bào) vào một fold ngẫu nhiên; fold `fold` làm test.
    Tập val lấy ngẫu nhiên `val_frac` từ phần train, dùng cho early stopping.
    """
    t = data["triplets"].numpy()
    groups = {"random": np.arange(len(t)), "combo": t[:, 0] * 100_000 + t[:, 1], "cell": t[:, 2]}[kind]
    rng = np.random.default_rng(seed)
    uniq = rng.permutation(np.unique(groups))
    fold_of = dict(zip(uniq, np.arange(len(uniq)) % n_folds))
    is_test = np.array([fold_of[g] == fold for g in groups])
    test = np.where(is_test)[0]
    train = rng.permutation(np.where(~is_test)[0])
    n_val = int(len(train) * val_frac)
    return train[n_val:], train[:n_val], test
