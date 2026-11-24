#!/bin/bash
# NCI-ALMANAC external validation (planner 5.3, 7.2).
#   bash run_external.sh [workers]
# Scores already-trained checkpoints zero-shot; nothing is retrained except XGBoost, whose
# booster src.repro.xgb does not save (it goes to its own runs/xgbext_* directories).
# leave_combo is the grid every model family shares (5 folds x 3 seeds), and it is the split
# the external question is actually about: drug pairs the model has not seen.
set -u
cd "$(dirname "$0")"
export PYTHONPATH=.
W=${1:-2}
LOG=runs/external.log
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a $LOG; }

say "syngt, leave_combo"
python -m src.eval.external --all "syngt_ord3_loewe_leave_combo_f?_s?" --workers "$W" >> $LOG 2>&1
say "syngt_smooth, leave_combo"
python -m src.eval.external --all "syngt_ord3_loewe_leave_combo_f?_s?_corn_smooth" --workers "$W" >> $LOG 2>&1
say "syngt, random"
python -m src.eval.external --all "syngt_ord3_loewe_random_f?_s?" --workers "$W" >> $LOG 2>&1
say "deepdds + deepsynergy, leave_combo"
python -m src.eval.external --all "deepdds_ord3_loewe_leave_combo_f?_s?" --workers "$W" >> $LOG 2>&1
python -m src.eval.external --all "deepsynergy_ord3_loewe_leave_combo_f?_s?" --workers "$W" >> $LOG 2>&1
say "xgboost, leave_combo (retrained, own run dirs)"
for f in 0 1 2 3 4; do for s in 0 1 2; do
  echo "--split leave_combo --fold $f --seed $s"
done; done | xargs -P "$W" -I{} sh -c "python -m src.repro.xgb_external {} >> $LOG 2>&1"
say "report"
python -m src.eval.report >> $LOG 2>&1
say "external done"
