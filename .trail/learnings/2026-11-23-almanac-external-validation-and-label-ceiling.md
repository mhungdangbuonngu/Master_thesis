---
title: The O'Neil to ALMANAC external validation is capped by the two studies disagreeing, not by the model
author: Mhungdangbuonngu
date: 2026-11-23
branch: gate1-pipeline
id: l-4e71c3b2
scope: repo
status: active
src: agent
touches:
  - src/data/almanac.py
  - src/data/almanac_smiles.py
  - src/data/almanac_build.py
  - src/data/cell_line_map_almanac.csv
  - src/eval/external.py
  - src/repro/xgb_external.py
  - src/eval/report.py
  - src/tests/test_all.py
---

## Decided

ALMANAC comes out of the DrugComb v1.4 summary table that already supplied O'Neil, not out of
NCI's `ComboDrugGrowth_Nov2017.zip`. DrugComb runs one SynergyFinder pipeline over every
study, so `synergy_loewe` in ALMANAC means what it means in the training labels; recomputing
Loewe from raw percent-growth would compare the model against a different definition of the
target. v1.4 has no `study_name` column, but each study occupies a contiguous `block_id`
range, and ALMANAC is blocks 132369..432467 (300,099 combination blocks, 60 NCI-60 lines, 102
drugs, no monotherapy). The range was found by taking the drug and cell vocabulary from the
middle of the study and growing the longest contiguous run that uses nothing else.

Report the external number together with the cross-dataset ceiling. 1,163 ALMANAC triples are
the same experiment as an O'Neil triple (same compound pair by InChIKey, same DepMap model),
and on those the two studies' own Loewe values correlate at Pearson 0.21, their 3-class labels
agree 57% of the time, and QWK between the datasets is 0.149. Of the 42 triples O'Neil calls
synergistic, ALMANAC keeps 1. Bliss, ZIP and HSA agree even less (QWK 0.065, 0.010, 0.076).
Restricting to the quartile of O'Neil rows with the tightest replicate IQR makes the agreement
WORSE (QWK 0.102 on 291 rows), so the disagreement is not O'Neil's measurement noise. Any claim
about a model's external QWK has to be read against that ceiling: over the full external set
SynGT 0.023, SynGT+smoothing 0.032, DeepSynergy 0.017, XGBoost 0.016, DeepDDS 0.013, all with
synergy-class recall 0.01-0.04 against a 0.015 base rate. In DTSyn's own binary protocol SynGT
reaches BACC 0.529 and AUROC 0.567 on ALMANAC, which is the BACC 0.57 DTSyn publishes for the
same transfer: the published external number for this model family was already near chance.

Keep the pipeline control that scores one set of predictions against two labels, split by
whether the matching O'Neil row was in that run's training set. On the 424 triples whose O'Neil
row was HELD OUT, SynGT scores QWK 0.561 against O'Neil's label and 0.139 against ALMANAC's;
on the 739 it trained on, 0.967 against O'Neil and 0.149 against ALMANAC. Same experiments,
same predictions, same scoring code, two labels. Every model does this (DeepDDS 0.481/0.139,
DeepSynergy 0.605/0.120, XGBoost 0.489/0.086 on the held-out group), which is what rules the
architecture out as the cause. The train-group number is not a result; it is the cheap proof that
the external scoring path is wired correctly (gene order, the fold's z-score, the swapped
per-drug fingerprint buffer, drug and cell indices). If it ever drops, suspect the pipeline
before the biology.

## Tried and ruled out

Blaming the collapse on input-side domain shift. ALMANAC cells sit no further from the
training cells than O'Neil's own held-out cells do under leave_cell (median nearest-training
distance 34.97-36.70 across folds against 33.63-36.46 in 944-gene space), and the ALMANAC compounds' maximum Tanimoto to
a training compound is higher than O'Neil compounds' to each other (median 0.222 against
0.191). Both checks are in `report.py` as `external_domain_shift` and `external_chem_shift`.

ChEMBL's API as the resolver for the ALMANAC drug names. On 2026-11-23
`molecule.json?pref_name__iexact=` hangs past 60 s and `molecule/<id>.json` answers HTTP 500,
so `src/data/smiles.py` would not run today either. PubChem's PUG REST is blocked for this IP
by NCBI, and Wikidata's query service was rate-limiting to one request a minute during an
outage. What works: NCI CACTUS for names (73 of 102, though it knows almost nothing approved
after about 2010) and UniChem for ChEMBL ids (InChI, then RDKit). A hand-written ChEMBL id is
pinned to its molecular formula in the code, because a wrong id returns a valid structure of
another drug: that check caught the first id tried for cabazitaxel.

Giving cisplatin its platinum back for the external set. The model has never seen a Pt atom,
so it was excluded instead (4,770 triples).

## Watch out

`rdMolStandardize.Cleanup` disconnects metal-ligand bonds, and `LargestFragmentChooser` then
keeps the organic part. Carboplatin and oxaliplatin have been in `data/processed/smiles.csv`
as cyclobutane-1,1-dicarboxylic acid and 1,2-diaminocyclohexane since the data was built, with
no Pt in any of the 36 molecule graphs; each appears in 814 triples (3.8% of the table). The
comment in `smiles.py` says RDKit parses the dative-free form, which was checked, but the
molecule after standardisation was not. The external set reuses those same Pt-free structures
on purpose, so both sides are consistent. Fixing the training structures means retraining 828
runs.

A forked worker cannot touch CUDA once the parent has ("Cannot re-initialize CUDA in forked
subprocess"), so the external scorer's process pool uses the spawn context.

A stage of `run_external.sh` can fail without failing the script: `xgb_external.py` imported a
name (`SUBSETS`) that lives in `report.py`, every one of its 15 `xargs` children died on the
import, and the sweep went straight on to the report, which built its tables with the XGBoost
column simply missing. Check the run count per model in `external_almanac.csv`, not the log's
"done" line.

Eleven of the 60 NCI-60 lines have no DepMap expression in this release (ten are in the model
list but unsequenced, NCI/ADR-RES is absent), which is the whole reason the external set has 49
cell lines. The curated mapping, with the reason per line, is
`src/data/cell_line_map_almanac.csv`.

In the code:

- `python -m src.data.almanac && python -m src.data.almanac_smiles && python -m src.data.almanac_build`
- `bash run_external.sh 2` then `bash run_external2.sh 2` (the second is DTSyn's binary protocol)
- tables: `reports/tables/external_almanac.csv`, `external_label_agreement.csv`,
  `external_control.csv`, `external_ranking.csv`, `external_domain_shift.csv`,
  `external_chem_shift.csv`
- the overlap flags and the O'Neil row mapping live in `data/processed/almanac.pt`
  (`seen_pair`, `seen_cell`, `oneil_ord3_loewe`, `oneil_row`)
