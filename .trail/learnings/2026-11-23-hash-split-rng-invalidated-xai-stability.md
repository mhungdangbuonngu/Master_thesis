---
title: hash(split) in the explanation rng made every XAI stability number meaningless
author: Mhungdangbuonngu
date: 2026-11-23
branch: gate1-pipeline
id: l-9c41ab7e
scope: repo
status: active
src: agent
touches:
  - src/xai/run_explain.py
  - src/eval/report.py
  - src/eval/xai_metrics.py
  - src/data/batching.py
  - src/tests/test_all.py
---

## Decided

Any comparison between two explanation runs must align attributions by triple id, never by
position in the record list, and every stability table must print the number of triples the two
runs actually share. The rng that picks which triples to explain may depend on (split, fold) and
on nothing else, process-local state included.

## Tried and ruled out

"O'Neil has 37 cell lines against 944 genes, so almost any gene subset identifies the cell line
and each seed settles on a different one." This was the standing explanation for the explanation
being unstable across seeds. Ruled out: the instability does not exist. Cross-seed Jaccard@50 is
0.190 to 0.279 against a null of 0.026 to 0.033 once the triples match.

The `--ref-setting` flag, added to force every label convention to explain one shared reference
set of triples, was believed to have fixed the cross-convention comparison. It had no effect,
because the root cause was elsewhere. The giveaway was `n_triples` showing 2 to 9 instead of 40.

## Watch out

Python salts string hashes per process unless PYTHONHASHSEED is set, so a line like
`default_rng(10_000 + 97 * fold + hash(split) % 1000)` looks deterministic and is not. Each
`run_explain` invocation is its own process, so three seeds of one fold shared 0 to 2 triples out
of 40.

`stability_null` is defined as "pair up DIFFERENT triples". If the caller hands `stability`
misaligned lists, the measurement and its own null compute the same quantity, so landing on the
null is forced by the code rather than observed from the model. Treat any "at the null" result as
unverified until the shared-triple count is checked.

The key (setting, split, fold, seed) does NOT identify a run: `_nofp`, `_nogeneemb` and
`_rewired` carry the same four values as the main run, and sorted() hands the slot to the last
one. The RQ5 baseline was the rewired-STRING ablation for as long as that key was used.

A number quoted in a report is not necessarily a number the pipeline computes. The cosine 0.436
that appeared in the write-ups had no corresponding function in `xai_metrics.py` at all.

In the code:
- `SPLIT_RNG_OFFSET` replaces `hash(split)` in `pick_triples`
- `is_plain_cfg`, `aligned()`, `n_triples` column in the three stability tables of report.py
- `cosine` added to `stability` / `stability_null`; real value 0.473 to 0.593
- `MolStore.permute_drugs` + `permute_molecules`, with an assert for any per-drug tensor left out
  (the permuted-SMILES control had leaked twice: first `drug_fp`, then `n_frag`)
- three regression tests, one running `pick_triples` under three PYTHONHASHSEED values
- pre-fix explanations kept in `runs_xai_prehashfix/`; re-run took 4h47m for 54 runs
