"""Run the explanations over the trained SynGT runs -> runs/*/explain.pt  (planner 6, 7.2).

    python -m src.xai.explain_sweep --workers 2

Which runs get explained, and why:
  headline  ord3_loewe x leave_combo x 5 folds x 3 seeds   - RQ3, RQ4, RQ6, and the seed
                                                             dimension of RQ5 (full, with
                                                             GNNExplainer as 2nd explainer)
  variants  the 4 synergy scores and the 3 thresholds      - the "is the explanation an
                                                             artefact of the label
                                                             convention" dimension of RQ5
  ppi       rewired / no-node2vec ablations                - does the explanation change when
                                                             the PPI information is destroyed
"""
import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "runs"


def targets():
    out = []
    for f in range(5):
        for s in (0, 1, 2):
            out.append((f"syngt_ord3_loewe_leave_combo_f{f}_s{s}", False))
    for st in ["ord3_bliss", "ord3_zip", "ord3_hsa", "ord3_loewe_t5", "ord3_loewe_t20"]:
        for f in range(3):
            out.append((f"syngt_{st}_leave_combo_f{f}_s0", True))
    for tag in ["rewired", "nogeneemb", "nofp"]:
        for f in range(3):
            out.append((f"syngt_ord3_loewe_leave_combo_f{f}_s0_{tag}", True))
    return [(r, light) for r, light in out if (RUNS / r / "model.pt").exists()]


def run_one(run, light, i, n, t0):
    out = RUNS / run / "explain.pt"
    if out.exists() or (RUNS / run / "explain.log").exists():
        return run, "skip"
    cmd = [sys.executable, "-m", "src.xai.run_explain", "--run", run]
    if light:
        cmd.append("--light")
    with open(RUNS / run / "explain.log", "w") as log:
        r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT,
                           env={**os.environ, "PYTHONPATH": str(ROOT)})
    st = "ok" if r.returncode == 0 else f"FAIL({r.returncode})"
    print(f"[{i + 1}/{n}] {(time.time() - t0) / 60:5.1f}m {st:10s} {run}", flush=True)
    return run, st


def main(workers, reverse=False):
    tg = targets()[::-1] if reverse else targets()   # a 2nd sweep can work from the other end
    print(f"=== explain: {len(tg)} runs, {workers} workers ===", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(lambda p: run_one(p[1][0], p[1][1], p[0], len(tg), t0), enumerate(tg)))
    bad = [r for r, s in res if s.startswith("FAIL")]
    print(f"=== explain done in {(time.time() - t0) / 60:.1f}m, "
          f"{sum(s == 'ok' for _, s in res)} ok, {len(bad)} failed ===", flush=True)
    if bad:
        print("failed:", bad[:10], flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--reverse", action="store_true")
    a = p.parse_args()
    main(a.workers, a.reverse)
