#!/bin/bash
# Label smoothing on the full grid (planner 3.3), then the report.
#   bash run_smooth.sh [workers]
set -u
cd "$(dirname "$0")"
export PYTHONPATH=.
W=${1:-3}
LOG=runs/pipeline.log
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }
say "stage smooth (label smoothing, full grid)"
python -m src.sweep --stage smooth --workers "$W" >> $LOG 2>&1
say "report"; python -m src.eval.report >> $LOG 2>&1
say "smooth done"
