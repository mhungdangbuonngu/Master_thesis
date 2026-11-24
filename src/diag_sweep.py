"""Diagnostic sweep for the SynGT underfitting problem (folds 0-2, seed 0, ord3 leave_combo).

    python -m src.diag_sweep --workers 5

Reference: the plain SynGT runs of stage `main` (same folds, same seed, same 80/12 budget).
Every variant here starts from the tuned config in runs/hp_best.json.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

from src.sweep import best_args, run_one

VARIANTS = {
    "skip": ["--readout", "skip"],
    "skip_ad0": ["--readout", "skip", "--att-dropout", "0"],
    "skip_lr1e3": ["--readout", "skip", "--lr", "1e-3"],
    "skip_p20": ["--readout", "skip", "--epochs", "120", "--patience", "20"],
    "skip_nofine": ["--readout", "skip", "--no-fine"],
    # round 2: base = skip + no attention dropout + 120/20 budget
    "r2_drop03": ["--readout", "skip", "--att-dropout", "0", "--epochs", "120", "--patience", "20",
                  "--dropout", "0.3"],
    "r2_drop05": ["--readout", "skip", "--att-dropout", "0", "--epochs", "120", "--patience", "20",
                  "--dropout", "0.5"],
    "r2_wide": ["--readout", "skip", "--att-dropout", "0", "--epochs", "120", "--patience", "20",
                "--dropout", "0.3", "--head-hidden", "2048,512"],
    "r2_fp": ["--readout", "skip", "--att-dropout", "0", "--epochs", "120", "--patience", "20",
              "--drug-fp"],
}


def jobs(variants):
    out = []
    for tag in variants:
        for f in range(3):
            a = ["--model", "syngt", "--setting", "ord3_loewe", "--split", "leave_combo",
                 "--fold", str(f), "--seed", "0", "--epochs", "80", "--patience", "12"]
            # later flags win in argparse, so the variant can override the budget / lr
            out.append(a + best_args() + VARIANTS[tag] + ["--name", f"dx_{tag}_f{f}"])
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=5)
    p.add_argument("--only", nargs="*", default=list(VARIANTS))
    a = p.parse_args()
    js = jobs(a.only)
    t0 = time.time()
    print(f"=== diag: {len(js)} runs ===", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(lambda q: run_one(q[1], q[0], len(js), t0), enumerate(js)))
    print("=== diag done ===", flush=True)
