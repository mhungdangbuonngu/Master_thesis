#!/bin/bash
# Second external stage: DTSyn's own binary protocol (gap, random folds), so the ALMANAC
# number is directly comparable to the BACC 0,57 DTSyn reports on ALMANAC.
#   bash run_external2.sh [workers]
set -u
cd "$(dirname "$0")"
export PYTHONPATH=.
W=${1:-2}
LOG=runs/external.log
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }
say "syngt bin_gap, random (DTSyn protocol)"
python -m src.eval.external --all "syngt_bin_gap_loewe_random_f?_s?" --workers "$W" >> $LOG 2>&1
say "deepdds bin_gap, random"
python -m src.eval.external --all "deepdds_bin_gap_loewe_random_f?_s?" --workers "$W" >> $LOG 2>&1
say "report"
python -m src.eval.report >> $LOG 2>&1
say "external2 done"
