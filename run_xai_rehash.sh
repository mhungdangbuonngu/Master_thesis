#!/bin/bash
# Re-run every explanation after the triple-sampling seed was fixed.
#   bash run_xai_rehash.sh [workers]
#
# Why this has to be re-run rather than just re-reported: `pick_triples` seeded its rng with
# `hash(split)`, which Python salts per process, so each `run_explain` invocation explained a
# different sample of triples. Seeds 0/1/2 of one fold shared 0 to 2 triples out of 40, and the
# RQ5 stability tables compared them anyway, positionally. The attributions themselves are fine;
# it is the CHOICE of triples that was not comparable across runs, and that choice is baked into
# each explain.pt. The pre-fix outputs are kept in runs_xai_prehashfix/ for comparison.
set -u
cd "$(dirname "$0")"
export PYTHONPATH=.
W=${1:-4}
LOG=runs/pipeline.log
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }

say "rehash: clearing explain outputs (backup in runs_xai_prehashfix/)"
test -d runs_xai_prehashfix || { echo "ABORT: no backup directory"; exit 1; }
rm -f runs/*/explain.pt runs/*/explain.log runs/*/explain_ref.pt runs/*/explain_ref.log

say "rehash: explain sweep (39 runs)"
python -m src.xai.explain_sweep --workers "$W" >> $LOG 2>&1

say "rehash: cross-convention explains on the shared reference triples (15 runs)"
for st in ord3_bliss ord3_zip ord3_hsa ord3_loewe_t5 ord3_loewe_t20; do
  for f in 0 1 2; do echo "syngt_${st}_leave_combo_f${f}_s0"; done
done | xargs -P "$W" -I{} sh -c 'python -m src.xai.run_explain --run {} --light --ref-setting ord3_loewe > runs/{}/explain_ref.log 2>&1 && echo "ok {}" || echo "FAIL {}"' >> $LOG 2>&1

say "rehash: case study"; python -m src.eval.case_study >> $LOG 2>&1
say "rehash: report";     python -m src.eval.report >> $LOG 2>&1
say "rehash done"
