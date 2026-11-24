#!/bin/bash
# The last planner gaps: the label-smoothing ablation (planner 3.3) and the cross-convention
# explains that share one reference set of triples (planner RQ5), then the report.
#   bash run_tail2.sh [workers]
set -u
cd "$(dirname "$0")"
export PYTHONPATH=.
W=${1:-3}
LOG=runs/pipeline.log
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }
say "stage ablation (+cornsmooth)"; python -m src.sweep --stage ablation --workers "$W" >> $LOG 2>&1
say "refexp (RQ5 shared triples)"
for st in ord3_bliss ord3_zip ord3_hsa ord3_loewe_t5 ord3_loewe_t20; do
  for f in 0 1 2; do echo "syngt_${st}_leave_combo_f${f}_s0"; done
done | xargs -P 2 -I{} sh -c 'python -m src.xai.run_explain --run {} --light --ref-setting ord3_loewe > runs/{}/explain_ref.log 2>&1 && echo "ok {}" || echo "FAIL {}"' >> $LOG 2>&1
say "report"; python -m src.eval.report >> $LOG 2>&1
say "tail2 done"
