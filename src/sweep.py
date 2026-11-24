"""Run a stage of the experiment grid in parallel -> runs/*  (planner 7.2).

    python -m src.sweep --stage g1 --workers 4
    python -m src.sweep --stage rest --workers 4

Stages, in the order the planner runs them:
    hp          16 random SynGT configs on one fold            -> hyperparameters
    g1          DeepDDS / DeepSynergy under DTSyn's binary protocol (GATE)
    main        7 models x 3 label settings, leave_combo (+ random for SynGT/DeepDDS) -> RQ1
    hard        3 models x ord3 x {leave_drug, leave_cell, leave_tumor}  -> generalisation
    ablation    10 SynGT variants on leave_combo               -> RQ2 and the PPI ablation
    sensitivity 4 synergy scores x 3 thresholds                -> RQ5 input side

Budget: every model in every stage trains with 120 epochs / patience 20 (recorded in each
run's config.json). Runs that already have metrics.json are skipped, so a stage can be
re-run after a crash.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"

SEEDS3 = [0, 1, 2]          # headline tables
SEEDS2 = [0, 1]             # ablations and sensitivity, to keep the grid affordable
FOLDS = {"random": 5, "leave_combo": 5, "leave_drug": 5, "leave_cell": 5, "leave_tumor": 7}
ALL_MODELS = ["syngt", "deepdds", "deepsynergy", "onehot", "cell_only", "drug_only", "majority"]
SETTINGS3 = ["ord3_loewe", "bin_gap_loewe", "bin_all_loewe"]
# One budget for every model after G1, the same as G1 itself. (An earlier 80/12 budget was
# dropped: SynGT's validation curve is noisy and 12 epochs of patience cut it early.)
BUDGET = ["--epochs", "120", "--patience", "20"]

# Overwritten from runs/hp_best.json once stage `hp` has run.
BEST = {"d": 128, "gnn_layers": 3, "fine_layers": 2, "coarse_layers": 2, "heads": 4,
        "ff": 256, "dropout": 0.3, "lr": 3e-4, "batch": 128}


def best_args():
    cfg = dict(BEST)
    f = RUNS / "hp_best.json"
    if f.exists():
        cfg.update({k: v for k, v in json.loads(f.read_text())["best"].items() if k in BEST})
    out = []
    for k, v in cfg.items():
        out += [f"--{k.replace('_', '-')}", str(v)]
    return out


def job(model, setting, split, fold, seed, extra=(), budget=True):
    a = ["--model", model, "--setting", setting, "--split", split,
         "--fold", str(fold), "--seed", str(seed)] + (BUDGET if budget else [])
    if model == "syngt":
        a += best_args()
    return a + list(extra)


def stage_hp():
    import numpy as np
    rng = np.random.default_rng(0)
    jobs = []
    for i in range(16):
        jobs.append(["--model", "syngt", "--setting", "ord3_loewe", "--split", "leave_combo",
                     "--fold", "0", "--seed", "0", "--epochs", "80", "--patience", "12",
                     "--d", str(int(rng.choice([64, 128, 256]))),
                     "--gnn-layers", str(int(rng.choice([2, 3, 4]))),
                     "--fine-layers", str(int(rng.choice([1, 2]))),
                     "--coarse-layers", str(int(rng.choice([1, 2]))),
                     "--heads", str(int(rng.choice([4, 8]))),
                     "--ff", str(int(rng.choice([128, 256, 512]))),
                     "--dropout", f"{rng.uniform(0.1, 0.6):.2f}",
                     "--lr", f"{10 ** rng.uniform(-4.3, -3.0):.2e}",
                     "--batch", str(int(rng.choice([64, 128, 256]))),
                     "--name", f"hp{i:02d}"])
    return jobs


def stage_g1():
    """DTSyn's protocol: binary with the neutral band removed, random 5-fold, full budget."""
    return [job(m, "bin_gap_loewe", "random", f, s, budget=False)
            for m in ["deepdds", "deepsynergy", "syngt", "onehot"]
            for f in range(5) for s in SEEDS3]



def stage_main():
    jobs = [job(m, st, "leave_combo", f, s)
            for m in ALL_MODELS for st in SETTINGS3 for f in range(5) for s in SEEDS3]
    # The same label comparison on a random split, to show RQ1 is not an artefact of
    # leave-combination-out. bin_gap on random is already covered by the G1 stage, and two
    # seeds are enough here because leave_combo carries the headline confidence intervals.
    jobs += [job(m, st, "random", f, s)
             for m in ["syngt", "deepdds"] for st in ["ord3_loewe", "bin_all_loewe"]
             for f in range(5) for s in SEEDS2]
    return jobs


def stage_hard():
    return [job(m, "ord3_loewe", split, f, s)
            for m in ["syngt", "deepdds", "deepsynergy", "onehot"]
            for split in ["leave_drug", "leave_cell", "leave_tumor"]
            for f in range(FOLDS[split]) for s in SEEDS2]


ABLATIONS = {
    "nofine": ["--no-fine"],
    "nocoarse": ["--no-coarse"],
    "notransformer": ["--no-fine", "--no-coarse"],
    "gcn": ["--gnn", "gcn"],
    "nogeneemb": ["--no-gene-emb"],
    "rewired": ["--gene-emb", "rewired"],
    "permsmiles": ["--permute-smiles"],
    "nominal": ["--loss", "nominal"],
    "cost": ["--loss", "cost"],
    "cornsmooth": ["--loss", "corn_smooth"],   # soft targets for boundary triples (planner 3.3)
    "genes384": ["--n-gene-tokens", "384"],
    "nofp": ["--no-drug-fp"],                  # graph-only drugs: what the fingerprint buys
    "clsreadout": ["--readout", "cls"],        # the original CLS-only readout
}


def stage_ablation():
    return [job("syngt", "ord3_loewe", "leave_combo", f, s, extra)
            for extra in ABLATIONS.values() for f in range(3) for s in SEEDS2]


def stage_sensitivity():
    settings = ["ord3_bliss", "ord3_zip", "ord3_hsa", "ord3_loewe_t5", "ord3_loewe_t20"]
    return [job("syngt", st, "leave_combo", f, s)
            for st in settings for f in range(3) for s in SEEDS2]


def stage_xgb():
    """Morgan fingerprints + expression -> gradient-boosted trees (planner 5.3).

    Trained by src.repro.xgb, not src.train, so these jobs carry a leading "xgb" marker that
    run_one() uses to pick the entry point.
    """
    out = []
    for st in SETTINGS3:
        out += [["xgb", "--setting", st, "--split", "leave_combo", "--fold", str(f),
                 "--seed", str(s)] for f in range(5) for s in SEEDS3]
    for split in ["leave_drug", "leave_cell", "leave_tumor", "random"]:
        out += [["xgb", "--setting", "ord3_loewe", "--split", split, "--fold", str(f),
                 "--seed", str(s)] for f in range(FOLDS[split]) for s in SEEDS2]
    return out


def stage_smooth():
    """Promote label smoothing from a 3-fold ablation to the full grid (planner 3.3).

    The 6-run ablation beat plain CORN on 6/6 paired folds and on validation (+0.043 val QWK),
    so it is no longer a side variant: it needs the same 5 folds x 3 seeds as the main table,
    and the hard splits, or it cannot be compared against DeepSynergy on equal footing.
    """
    extra = ABLATIONS["cornsmooth"]
    out = [job("syngt", "ord3_loewe", "leave_combo", f, s, extra)
           for f in range(5) for s in SEEDS3]
    for split in ["leave_drug", "leave_cell", "leave_tumor"]:
        out += [job("syngt", "ord3_loewe", split, f, s, extra)
                for f in range(FOLDS[split]) for s in SEEDS2]
    return out


STAGES = {"hp": stage_hp, "g1": stage_g1, "main": stage_main, "hard": stage_hard,
          "ablation": stage_ablation, "sensitivity": stage_sensitivity, "xgb": stage_xgb,
          "smooth": stage_smooth}
ORDER = ["hp", "g1", "main", "hard", "ablation", "sensitivity", "xgb", "smooth"]
REST = ["main", "hard", "ablation", "sensitivity", "xgb", "smooth"]


def pick_hp():
    """Write runs/hp_best.json from the finished hp runs (best validation QWK)."""
    best, cfg = -1e9, None
    for d in RUNS.glob("hp*"):
        f = d / "metrics.json"
        if not f.exists():
            continue
        v = json.loads(f.read_text())["val"]["qwk"]
        if v > best:
            best, cfg = v, json.loads((d / "config.json").read_text())
    if cfg is None:
        return None
    keep = {k: cfg[k] for k in BEST}
    (RUNS / "hp_best.json").write_text(json.dumps({"val_qwk": best, "run": cfg["run"],
                                                   "best": keep}, indent=1))
    print(f"hp best: {cfg['run']}  val_qwk {best:.4f}  {keep}", flush=True)
    return keep


def run_one(args, i, n, t0):
    if args and args[0] == "xgb":                      # trees: a different entry point
        from src.repro.xgb import parse as xparse, run_name as xname
        args = args[1:]
        name, module = xname(xparse(args)), "src.repro.xgb"
    else:
        from src.train import parse, run_name
        name, module = run_name(parse(args)), "src.train"
    out = RUNS / name
    if (out / "metrics.json").exists():
        return name, "skip"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "train.log", "w") as log:
        r = subprocess.run([sys.executable, "-m", module] + args, stdout=log,
                           stderr=subprocess.STDOUT, cwd=ROOT,
                           env={**os.environ, "PYTHONPATH": str(ROOT)})
    status = "ok" if r.returncode == 0 else f"FAIL({r.returncode})"
    print(f"[{i + 1}/{n}] {(time.time() - t0) / 60:5.1f}m {status:10s} {name}", flush=True)
    return name, status


def main(stage, workers):
    stages = {"all": ORDER, "rest": REST}.get(stage, [stage])
    for st in stages:
        if st in REST or st == "g1":
            pick_hp()                      # use the tuned config for every SynGT run
        jobs = STAGES[st]()
        print(f"=== stage {st}: {len(jobs)} runs, {workers} workers ===", flush=True)
        t0 = time.time()
        with ThreadPoolExecutor(workers) as ex:
            res = list(ex.map(lambda p: run_one(p[1], p[0], len(jobs), t0), enumerate(jobs)))
        bad = [n for n, s in res if s.startswith("FAIL")]
        print(f"=== stage {st} done in {(time.time() - t0) / 60:.1f}m, "
              f"{sum(s == 'ok' for _, s in res)} ok, {sum(s == 'skip' for _, s in res)} skipped, "
              f"{len(bad)} failed ===", flush=True)
        if bad:
            print("failed:", bad[:10], flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--stage", default="rest", choices=["all", "rest"] + ORDER)
    p.add_argument("--workers", type=int, default=4)
    a = p.parse_args()
    main(a.stage, a.workers)
