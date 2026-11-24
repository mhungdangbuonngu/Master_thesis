"""Collect runs/* into reports/tables/*.csv + tables.md  (planner 8).

    python -m src.eval.report

Prediction tables (RQ1, RQ2 and the generalisation grid) are built from metrics.json; the
XAI tables (RQ3-RQ6) are built from explain.pt and are skipped while those do not exist yet,
so this can be run at any point during the sweep.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from src.eval import metrics as M
from src.eval import xai_metrics as X

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "runs"
OUT = ROOT / "reports" / "tables"

# What the source papers report, for the G1 gate only (never copied into a comparison table).
PUBLISHED = {
    ("deepdds", "random"): "DeepDDS paper: ROC-AUC ~0.93 (random 5-fold, O'Neil)",
    ("deepsynergy", "random"): "DeepSynergy paper: AUC 0.90 as a classifier (O'Neil)",
    ("deepdds", "leave_combo"): "DeepDDS paper: AUC 0.89 (leave-combination-out)",
}
MODEL_ORDER = ["syngt", "syngt_smooth", "deepdds", "deepsynergy", "xgboost", "onehot",
               "drug_only", "cell_only", "majority"]


def load_runs():
    rows = []
    for d in sorted(RUNS.glob("*")):
        f, c = d / "metrics.json", d / "config.json"
        if not (f.exists() and c.exists()):
            continue
        cfg = json.loads(c.read_text())
        m = json.loads(f.read_text())
        r = {"run": d.name, **{k: cfg.get(k) for k in
             ("model", "setting", "split", "fold", "seed", "loss", "gnn", "no_fine",
              "no_coarse", "no_gene_emb", "gene_emb", "permute_smiles", "readout",
              "no_drug_fp", "att_dropout", "n_params",
              "n_train", "n_test", "best_epoch", "epochs_run", "seconds")}}
        r.update({f"test_{k}": v for k, v in m["test"].items() if not isinstance(v, list)})
        r.update({f"val_{k}": v for k, v in m["val"].items() if not isinstance(v, list)})
        r["confusion"] = m["test"].get("confusion")
        rows.append(r)
    return pd.DataFrame(rows)


def agg(df, by, cols):
    """mean, std and bootstrap CI over folds x seeds."""
    out = []
    for key, g in df.groupby(by, dropna=False):
        rec = dict(zip(by if isinstance(by, list) else [by],
                       key if isinstance(key, tuple) else [key]))
        rec["n_runs"] = len(g)
        for c in cols:
            if c not in g:
                continue
            v = g[c].dropna().values
            if len(v) == 0:
                continue
            mean, lo, hi = M.bootstrap_ci(v)
            rec[c] = mean
            rec[f"{c}_std"] = float(np.std(v))
            rec[f"{c}_lo"], rec[f"{c}_hi"] = lo, hi
        out.append(rec)
    return pd.DataFrame(out)


def srt(t, by, ascending=True):
    """sort_values that tolerates columns a half-finished sweep has not produced yet."""
    by = [by] if isinstance(by, str) else list(by)
    asc = [ascending] * len(by) if isinstance(ascending, bool) else list(ascending)
    keep = [(c, a) for c, a in zip(by, asc) if c in t.columns]
    if not len(t) or not keep:
        return t
    return t.sort_values([c for c, _ in keep], ascending=[a for _, a in keep])


def _syngt_final_arch(df):
    """SynGT at the final architecture with no ablation flag set. Says nothing about the loss."""
    return ((df.model == "syngt") & (~df.no_fine.fillna(False))
            & (~df.no_coarse.fillna(False)) & (~df.no_gene_emb.fillna(False))
            & (df.gene_emb == "real") & (~df.permute_smiles.fillna(False)) & (df.gnn == "gin")
            & (df.readout.fillna("cls") == "skip") & (~df.no_drug_fp.fillna(False)))


def is_plain_syngt(df):
    """SynGT with no ablation flag set, trained with the plain CORN loss."""
    return _syngt_final_arch(df) & (df.loss == "corn")


def is_plain_cfg(c):
    """is_plain_syngt, applied to one run's config dict. For the explain tables.

    They key runs by (setting, split, fold, seed), and every leave_combo ablation shares that
    key with the real run: syngt_ord3_loewe_leave_combo_f0_s0 and its _nofp / _nogeneemb /
    _rewired siblings all carry the same four values, so the last name in sorted order used to
    win the slot. The cross-convention baseline was therefore the REWIRED-STRING ablation
    rather than SynGT, and the cross-seed slot for seed 0 was an ablation too.
    """
    return (c.get("model") == "syngt" and c.get("loss") == "corn"
            and not c.get("no_fine") and not c.get("no_coarse") and not c.get("no_gene_emb")
            and c.get("gene_emb") == "real" and not c.get("permute_smiles")
            and c.get("gnn") == "gin" and (c.get("readout") or "cls") == "skip"
            and not c.get("no_drug_fp"))


def aligned(e, cls, ids, which):
    """gene_attr_<which> for exactly `ids`, in that order, pulled out by triple id."""
    pos = {int(i): j for j, i in enumerate(e["idx"].get(cls, []))}
    return [np.asarray(e["records"][cls][pos[i]][f"gene_attr_{which}"], dtype=float)
            for i in ids]


def is_smooth_syngt(df):
    """Same architecture and same fold x seed grid, CORN targets smoothed at the thresholds.

    This is a separate row in the main table rather than an ablation line, because it is the
    variant selected on VALIDATION QWK (it wins on all four splits there) and so it is the one
    that should be read against the baselines. Keeping it out of the table while it existed in
    runs/ meant its 34 hard-split runs were reported nowhere.
    """
    return _syngt_final_arch(df) & (df.loss == "corn_smooth")


# --------------------------------------------------------------------------------- tables
def t_g1(df):
    d = df[(df.setting == "bin_gap_loewe") & (df.split == "random")]
    d = d[(d.model != "syngt") | is_plain_syngt(d)]
    cols = ["test_auroc", "test_auprc", "test_acc", "test_bacc", "test_prec", "test_tpr",
            "test_kappa"]
    t = agg(d, ["model"], cols)
    t["published_reference"] = [PUBLISHED.get((m, "random"), "") for m in t.model]
    return srt(t, "test_auroc", False)


def t_rq1(df):
    """The cost of keeping the neutral band (planner RQ1)."""
    d = df[df.setting.isin(["bin_gap_loewe", "bin_all_loewe", "ord3_loewe"])]
    d = d[(d.model != "syngt") | is_plain_syngt(d)]
    t = agg(d, ["model", "setting", "split"],
            ["test_auroc", "test_auprc", "test_qwk", "test_macro_f1", "test_bacc",
             "test_acc", "test_polar_error", "n_test"])
    return srt(t, ["split", "setting", "model"])


def t_rq1_drop(df):
    """Same model, same split: binary-with-gap vs binary-on-everything."""
    d = df[df.setting.isin(["bin_gap_loewe", "bin_all_loewe"])]
    d = d[(d.model != "syngt") | is_plain_syngt(d)]
    if d.empty or d.setting.nunique() < 2:
        return pd.DataFrame()          # one of the two label settings has not been run yet
    p = d.pivot_table(index=["model", "split"], columns="setting",
                      values=["test_auroc", "test_auprc"], aggfunc="mean")
    rows = []
    for (model, split), r in p.iterrows():
        v = {}
        for metric in ("auroc", "auprc"):
            gap = r.get((f"test_{metric}", "bin_gap_loewe"), np.nan)
            all_ = r.get((f"test_{metric}", "bin_all_loewe"), np.nan)
            v[f"{metric}_gap_removed"], v[f"{metric}_all_data"] = gap, all_
            v[f"{metric}_drop"] = gap - all_
        rows.append({"model": model, "split": split, **v})
    t = pd.DataFrame(rows).dropna(subset=["auroc_drop"])
    return srt(t, ["split", "auroc_drop"], [True, False])


def t_rq2(df):
    """Ordinal (CORN) vs nominal cross-entropy vs cost-sensitive (planner RQ2)."""
    d = df[(df.model == "syngt") & (df.setting == "ord3_loewe") & (df.split == "leave_combo")]
    d = d[is_plain_syngt(d.assign(loss="corn"))]       # every architecture flag at default
    return srt(agg(d, ["loss"], ["test_qwk", "test_mae", "test_macro_f1", "test_polar_error",
                             "test_adjacent_error", "test_recall_syn", "test_recall_ant",
                             "test_auprc_syn", "test_acc"]), "test_qwk", False)


def t_main(df):
    """The headline 3-class table across every split.

    SynGT appears twice: `syngt` is the plain CORN loss, `syngt_smooth` the smoothed-target
    variant. Both are the same architecture on the same folds and seeds, so the two rows are
    paired and the difference between them is the loss alone.
    """
    d = df[df.setting == "ord3_loewe"].copy()
    d = d[(d.model != "syngt") | is_plain_syngt(d) | is_smooth_syngt(d)]
    d.loc[is_smooth_syngt(d), "model"] = "syngt_smooth"
    t = agg(d, ["model", "split"],
            ["test_qwk", "test_macro_f1", "test_mae", "test_bacc", "test_polar_error",
             "test_recall_ant", "test_recall_add", "test_recall_syn",
             "test_auprc_ant", "test_auprc_syn", "test_macro_auroc"])
    if t.empty:
        return t
    t["model_rank"] = t.model.map({m: i for i, m in enumerate(MODEL_ORDER)})
    return srt(t, ["split", "model_rank"]).drop(columns="model_rank")


def t_ablation(df):
    d = df[(df.model == "syngt") & (df.setting == "ord3_loewe") & (df.split == "leave_combo")]

    def tag(r):
        if r.no_fine and r.no_coarse:
            return "no transformer at all"
        if r.no_fine:
            return "no fine transformer"
        if r.no_coarse:
            return "no coarse transformer"
        if r.no_gene_emb:
            return "no node2vec gene embedding"
        if r.gene_emb == "rewired":
            return "node2vec on REWIRED STRING"
        if r.permute_smiles:
            return "permuted SMILES (identity kept)"
        if r.gnn == "gcn":
            return "GCN instead of GIN"
        if r.loss == "corn_smooth":
            return "CORN + label smoothing at the thresholds"
        if r.loss != "corn":
            return f"loss = {r.loss}"
        if r.readout != "skip":
            return "CLS-only readout (original DTSyn-style)"
        if r.no_drug_fp:
            return "graph only (no fingerprint branch)"
        return "SynGT (full)"

    d = d.assign(variant=[tag(r) for _, r in d.iterrows()])
    return srt(agg(d, ["variant"], ["test_qwk", "test_macro_f1", "test_polar_error",
                                    "test_recall_syn", "n_params"]), "test_qwk", False)


def t_sensitivity(df):
    d = df[(df.model == "syngt") & (df.split == "leave_combo") & df.setting.str.startswith("ord3")]
    d = d[is_plain_syngt(d)]
    return srt(agg(d, ["setting"], ["test_qwk", "test_macro_f1", "test_polar_error",
                                "test_recall_syn", "test_recall_ant"]), "setting")


def t_diag(df):
    """The architecture diagnosis (runs_diag/): chosen on validation QWK, test shown after."""
    d = df[df.run.str.startswith("dx_")].copy()
    if d.empty:
        return d
    d["variant"] = d.run.str.replace(r"^dx_|_f\d$", "", regex=True)
    return srt(agg(d, ["variant"], ["val_qwk", "test_qwk", "test_macro_f1", "test_polar_error",
                                    "n_params", "seconds"]), "val_qwk", False)


def t_hp(df):
    d = df[df.run.str.startswith("hp")]
    if d.empty:
        return pd.DataFrame()
    keep = ["run", "val_qwk", "test_qwk", "n_params", "epochs_run", "seconds"]
    return srt(d[[c for c in keep if c in d]], "val_qwk", False)


# ------------------------------------------------------------------------------ XAI tables
def explain_runs():
    return sorted(RUNS.glob("*/explain.pt"))


def load_explains(fname="explain.pt"):
    out = {}
    for d in sorted(RUNS.glob("*")):
        f = d / fname
        if f.exists():
            out[d.name] = torch.load(f, weights_only=False)
    return out


def t_faithfulness(ex):
    rows = []
    for run, e in ex.items():
        for cls in ("syn", "ant"):
            recs = e["records"].get(cls, [])
            if not recs:
                continue
            for which in X_TARGETS:
                for lvl in (0.1, 0.25):
                    f = X.fidelity(recs, f"fid_gene_{which}_{lvl}")
                    if f:
                        rows.append({"run": run, "class": cls, "target": which, "unit": "gene",
                                     "k": lvl, **f})
                for k in (1, 2):
                    f = X.fidelity(recs, f"fid_frag_{which}_{k}")
                    if f:
                        rows.append({"run": run, "class": cls, "target": which, "unit": "frag",
                                     "k": k, **f})
    if not rows:
        return pd.DataFrame()
    d = pd.DataFrame(rows)
    return agg(d, ["class", "target", "unit", "k"], ["fid_plus", "null", "diff", "win_rate"])


def t_completeness(ex):
    rows = []
    for run, e in ex.items():
        for cls in ("syn", "ant"):
            for which in X_TARGETS:
                c = X.completeness(e["records"].get(cls, []), which)
                if c:
                    rows.append({"run": run, "class": cls, "target": which, **c})
    return pd.DataFrame(rows).groupby(["class", "target"]).mean(numeric_only=True).reset_index() \
        if rows else pd.DataFrame()


def t_fvt(ex):
    rows = []
    for run, e in ex.items():
        for cls in ("syn", "ant"):
            for which in X_TARGETS:
                v = X.violation_test(e["records"].get(cls, []), which)
                if v:
                    rows.append({"run": run, "class": cls, "target": which, **v})
            a = X.attention_vs_ig(e["records"].get(cls, []))
            if a:
                rows.append({"run": run, "class": cls, "target": "attention_vs_ig", **a})
    if not rows:
        return pd.DataFrame()
    return agg(pd.DataFrame(rows), ["class", "target"],
               ["spearman", "violation_rate", "jaccard_top_k"])


def t_rq3(ex):
    rows = []
    for run, e in ex.items():
        for cls in ("syn", "ant"):
            recs = e["records"].get(cls, [])
            if not recs:
                continue
            rows.append({"run": run, "class": cls, **X.level_divergence(recs),
                         **X.frag_interaction_summary(recs)})
    if not rows:
        return pd.DataFrame()
    return agg(pd.DataFrame(rows), ["class"],
               ["contrast_vs_logit", "contrast_vs_ant", "logit_vs_ant",
                "interaction_over_first_order", "frac_positive_phi"])


def t_graph_fp(ex):
    """Share of each decision carried by the fingerprint branch vs the molecular graph."""
    rows = []
    for run, e in ex.items():
        for cls in ("syn", "ant"):
            for r in e["records"].get(cls, []):
                for which, g in r.get("graph_vs_fp", {}).items():
                    sw = abs(g["f1"] - g["f0"]) + 1e-9
                    rows.append({"run": run, "class": cls, "target": which,
                                 "ig_share_fp": g["ig_share_fp"],
                                 "ig_gap_rel": abs(g["ig_gap"]) / sw,
                                 "del_fp_abs": abs(g["del_fp"]), "del_graph_abs": abs(g["del_graph"]),
                                 "fp_dominates": float(abs(g["del_fp"]) > abs(g["del_graph"]))})
    if not rows:
        return pd.DataFrame()
    return agg(pd.DataFrame(rows), ["class", "target"],
               ["ig_share_fp", "ig_gap_rel", "del_fp_abs", "del_graph_abs", "fp_dominates"])


def t_label_agreement():
    """How much the 3-class label itself moves when the convention changes (planner 3.3).

    Pure data, no model: the fraction of triples keeping their class when the synergy score is
    swapped (Loewe -> Bliss / ZIP / HSA) or the threshold moved (+-10 -> +-5 / +-20). This is
    the ceiling on any cross-convention agreement an explanation could show, so it must be
    reported next to the RQ5 stability numbers.
    """
    d = torch.load(ROOT / "data" / "processed" / "dataset.pt", weights_only=False)
    base = d["y"]["ord3_loewe"].numpy()
    rows = []
    for other in ["ord3_bliss", "ord3_zip", "ord3_hsa", "ord3_loewe_t5", "ord3_loewe_t20"]:
        o = d["y"][other].numpy()
        rec = {"setting": other, "n": len(base),
               "same_class_frac": float((o == base).mean()),
               "kappa": float(M.ord3(base, o, None)["kappa"]),
               "qwk_vs_loewe": float(M.ord3(base, o, None)["qwk"])}
        for c, name in ((0, "ant"), (2, "syn")):
            m = base == c
            rec[f"{name}_kept"] = float((o[m] == c).mean()) if m.any() else np.nan
            rec[f"{name}_n"] = int(m.sum())
            rec[f"{name}_n_other"] = int((o == c).sum())
        rows.append(rec)
    return pd.DataFrame(rows)


def t_stability_cross(ex):
    """RQ5 across the LABEL CONVENTION, not across seeds (planner 6.3, 8.2).

    The headline model is trained on Loewe +-10. These rows ask how much of the explanation
    survives when only the convention changes: the same architecture, the same split, the same
    fold and the same seed, trained on Bliss / ZIP / HSA, or on Loewe at +-5 / +-20.

    Comparable only because `pick_triples` draws the explained triples from an rng keyed by
    (split, fold) alone, so every setting explains the same triples - EXCEPT where the label
    itself moved a triple out of the class being compared, so `n_triples` is reported and the
    comparison is restricted to the triples both runs hold.
    """
    base_setting = "ord3_loewe"
    byk = {}
    for run, e in {**ex, **load_explains("explain_ref.pt")}.items():
        c = e["config"]
        if not is_plain_cfg(c):            # an ablation must not take the slot - see is_plain_cfg
            continue
        byk[(c["setting"], c["split"], c["fold"], c["seed"])] = e
    rows = []
    for (setting, split, fold, seed), e in byk.items():
        if setting == base_setting:
            continue
        b = byk.get((base_setting, split, fold, seed))
        if b is None:
            continue
        for cls in ("syn", "ant"):
            ids_a = {int(i): j for j, i in enumerate(e["idx"].get(cls, []))}
            ids_b = {int(i): j for j, i in enumerate(b["idx"].get(cls, []))}
            shared = sorted(set(ids_a) & set(ids_b))
            if not shared:
                continue
            for which in X_TARGETS:
                va, vb = aligned(e, cls, shared, which), aligned(b, cls, shared, which)
                st = X.stability({"a": va, "b": vb})
                nl = X.stability_null({"a": va, "b": vb})
                rows.append({"setting": setting, "class": cls, "target": which,
                             "jaccard": st["jaccard"], "null": nl.get("jaccard", np.nan),
                             "diff": st["jaccard"] - nl.get("jaccard", np.nan),
                             "n_triples": len(shared),
                             "frac_class_kept": len(shared) / max(len(ids_b), 1)})
    if not rows:
        return pd.DataFrame()
    return srt(agg(pd.DataFrame(rows), ["setting", "class", "target"],
                   ["jaccard", "null", "diff", "n_triples", "frac_class_kept"]),
               ["setting", "class", "target"])


def t_stability_fold(ex):
    """RQ5 across FOLDS: the same label setting, different training data."""
    byk = {}
    for run, e in ex.items():
        c = e["config"]
        if c["setting"] != "ord3_loewe" or c["seed"] != 0 or not is_plain_cfg(c):
            continue                       # the PPI ablations share (setting, fold, seed=0)
        byk[c["fold"]] = e
    rows = []
    folds = sorted(byk)
    for cls in ("syn", "ant"):
        for which in X_TARGETS:
            # different folds explain DIFFERENT triples (each fold's own test set), so the
            # comparison here is of the gene RANKING as a whole, averaged over triples
            per_fold = {}
            for f in folds:
                recs = byk[f]["records"].get(cls, [])
                if recs:
                    per_fold[f] = [np.mean([np.asarray(r[f"gene_attr_{which}"], dtype=float)
                                            for r in recs], 0)]
            if len(per_fold) < 2:
                continue
            st = X.stability(per_fold)
            rows.append({"class": cls, "target": which, "jaccard_mean_map": st["jaccard"],
                         "n_folds": len(per_fold)})
    return pd.DataFrame(rows)


def t_stability(ex):
    """Jaccard@50 of the SAME triples across seeds (planner RQ5).

    Explanations are matched by triple id, not by position in the record list. They used to be
    compared positionally, which measured nothing at all: `pick_triples` seeded its rng with
    `hash(split)`, Python salts string hashes per process, and each seed ran in its own process,
    so seeds 0/1/2 of one fold shared 0 to 2 triples out of 40. Record i of seed 0 was simply a
    different triple from record i of seed 1, and a comparison between explanations of unrelated
    triples naturally sits at the null - which is exactly what the table reported.

    `n_triples` is now a column so that an empty or tiny intersection can never again be read
    as an unstable explanation.
    """
    groups = {}
    for run, e in ex.items():
        c = e["config"]
        if not is_plain_cfg(c):
            continue
        groups.setdefault((c["setting"], c["split"], c["fold"]), {})[c["seed"]] = e
    rows = []
    for (setting, split, fold), by_seed in groups.items():
        if len(by_seed) < 2:
            continue
        for cls in ("syn", "ant"):
            per = [set(int(i) for i in e["idx"].get(cls, [])) for e in by_seed.values()]
            if not per or not all(per):
                continue
            shared = sorted(set.intersection(*per))
            if len(shared) < 2:
                continue
            for which in X_TARGETS:
                attr = {s: aligned(e, cls, shared, which) for s, e in by_seed.items()}
                st = X.stability(attr)
                nl = X.stability_null(attr)
                if st:
                    rows.append({"setting": setting, "split": split, "fold": fold, "class": cls,
                                 "target": which, "jaccard": st["jaccard"],
                                 "null": nl.get("jaccard", np.nan),
                                 "diff": st["jaccard"] - nl.get("jaccard", np.nan),
                                 "cosine": st.get("cosine", np.nan),
                                 "cosine_null": nl.get("cosine", np.nan),
                                 "n_triples": len(shared), "n_seeds": len(attr)})
    if not rows:
        return pd.DataFrame()
    return agg(pd.DataFrame(rows), ["setting", "split", "class", "target"],
               ["jaccard", "null", "diff", "cosine", "cosine_null", "n_triples"])


def t_plausibility(ex):
    d = torch.load(ROOT / "data" / "processed" / "dataset.pt", weights_only=False)
    ce = torch.load(ROOT / "data" / "processed" / "cells.pt", weights_only=False)
    rows = []
    for run, e in ex.items():
        for cls in ("syn", "ant"):
            recs = e["records"].get(cls, [])
            ids = e["idx"].get(cls, [])
            if not recs:
                continue
            r = X.target_hit_rate(recs, ids, e["genes"], d["idx"], d["drugs"],
                                  which="contrast", expr=ce["expr"].numpy())
            if r:
                rows.append({"run": run, "class": cls, **r})
    if not rows:
        return pd.DataFrame()
    return agg(pd.DataFrame(rows), ["class"], ["frac_enriched", "null_frac_enriched", "mean_hits"])


def t_rq6(ex):
    """Pathways the explanations land in, synergy vs antagonism (planner RQ6)."""
    rows = []
    for run, e in ex.items():
        for cls in ("syn", "ant"):
            recs = e["records"].get(cls, [])
            if not recs:
                continue
            for p in X.pathway_profile(recs, e["genes"], which="contrast"):
                rows.append({"run": run, "class": cls, **p})
    if not rows:
        return pd.DataFrame()
    d = pd.DataFrame(rows)
    piv = d.groupby(["class", "pathway", "name"]).frac_triples.mean().reset_index()
    return srt(piv, ["class", "frac_triples"], [True, False]).groupby("class").head(10)


X_TARGETS = ("logit", "contrast", "ant")


SUBSETS = ["all", "unseen_pair", "unseen_cell", "unseen_pair_and_cell", "new_chemistry",
           "measured_by_both", "measured_by_both_vs_oneil_label"]


def _smooth_cfg(c):
    """is_plain_cfg, but for the smoothed-target loss."""
    return is_plain_cfg({**c, "loss": "corn"}) and c.get("loss") == "corn_smooth"


def external_runs():
    """One row per (run, subset) from runs/*/external_almanac.json.

    A SynGT run is kept only if it is the final architecture with no ablation flag set. The
    ablations share the (setting, split, fold, seed) key and the model name with the real
    runs, so without this an accidentally scored `_nofp` or `_rewired` run would be averaged
    into the SynGT row.
    """
    rows = []
    for d in sorted(RUNS.glob("*")):
        f = d / "external_almanac.json"
        if not f.exists():
            continue
        e = json.loads(f.read_text())
        if e["model"] == "syngt":
            c = json.loads((d / "config.json").read_text())
            if not (is_plain_cfg(c) or _smooth_cfg(c)):
                continue
        for sub in SUBSETS:
            r = e.get(sub)
            if not r:
                continue
            flat = {f"ext_{k}": v for k, v in r.items() if not isinstance(v, (list, dict))}
            syn = {f"ext_syn_{k}": v for k, v in (r.get("syn_vs_rest") or {}).items()
                   if not isinstance(v, list)}
            rows.append({"run": e["run"], "model": e["model"], "loss": e["loss"],
                         "setting": e["setting"], "split": e["split"], "fold": e["fold"],
                         "seed": e["seed"], "subset": sub, **flat, **syn})
    return pd.DataFrame(rows)


def t_cross_dataset_labels():
    """Do O'Neil and ALMANAC agree about the triples they BOTH measured? (planner 5.3)

    Pure data, no model. 1,163 triples appear in both studies with the same compound pair (by
    InChIKey) and the same DepMap cell line, each with its own DrugComb-computed synergy
    scores. This is the ceiling on external transfer: a model cannot predict ALMANAC's label
    from O'Neil's any better than ALMANAC's label can be predicted from O'Neil's own.
    """
    ext = torch.load(ROOT / "data" / "processed" / "almanac.pt", weights_only=False)
    m = ext["oneil_ord3_loewe"] >= 0
    yo = ext["oneil_ord3_loewe"][m].numpy()
    rows = []
    for score in ["loewe", "bliss", "zip", "hsa"]:
        ya = ext["y"][f"ord3_{score}"][m].numpy()
        sa = ext["score"][score][m].numpy()
        rec = {"score": score, "n": int(m.sum()),
               "same_class_frac": float((ya == yo).mean()),
               "qwk": float(M.ord3(yo, ya, None)["qwk"]),
               "kappa": float(M.ord3(yo, ya, None)["kappa"])}
        if score == "loewe":
            so = ext["oneil_loewe"][m].numpy()
            rec["pearson_score"] = float(np.corrcoef(so, sa)[0, 1])
            rec["spearman_score"] = float(pd.Series(so).corr(pd.Series(sa), method="spearman"))
            rec["mean_oneil"], rec["mean_almanac"] = float(so.mean()), float(sa.mean())
        for c, name in ((0, "ant"), (2, "syn")):
            k = yo == c
            rec[f"{name}_kept"] = float((ya[k] == c).mean()) if k.any() else np.nan
            rec[f"{name}_n_oneil"] = int(k.sum())
            rec[f"{name}_n_almanac"] = int((ya == c).sum())
        rows.append(rec)
    # Loewe again, now only on the triples O'Neil measured tightly (its own IQR in the lowest
    # quartile over the overlap). ALMANAC cannot be filtered the same way: its triples are
    # single blocks, so the noise there is whatever one measurement gives.
    if "oneil_loewe_iqr" in ext:
        iqr = ext["oneil_loewe_iqr"][m].numpy()
        thr = np.nanquantile(iqr, 0.25)
        k = iqr <= thr
        ya = ext["y"]["ord3_loewe"][m].numpy()
        rows.append({"score": "loewe_oneil_tight_quartile", "n": int(k.sum()),
                     "same_class_frac": float((ya[k] == yo[k]).mean()),
                     "qwk": float(M.ord3(yo[k], ya[k], None)["qwk"]),
                     "kappa": float(M.ord3(yo[k], ya[k], None)["kappa"]),
                     "oneil_iqr_max": float(thr)})
    return pd.DataFrame(rows)


def t_external_shift():
    """Is the external set simply out of distribution on the INPUT side? (planner 5.3)

    One row per leave_cell fold: how far the held-out O'Neil cells and the 49 ALMANAC cells
    sit from that fold's training cells in 944-gene expression space, plus what the z-score
    (fitted on those training cells) looks like for each. If the two distances match, a
    collapse on ALMANAC cannot be blamed on the cell features being alien.
    """
    proc = ROOT / "data" / "processed"
    ce = torch.load(proc / "cells.pt", weights_only=False)
    d = torch.load(proc / "dataset.pt", weights_only=False)
    sp = torch.load(proc / "splits.pt", weights_only=False)
    ext = torch.load(proc / "almanac.pt", weights_only=False)
    rows = []
    for f, (tr, _, te) in enumerate(sp["splits"]["leave_cell"]):
        tc = torch.unique(d["idx"][tr][:, 2])
        hc = torch.unique(d["idx"][te][:, 2])
        C = ce["expr"][tc]

        def nearest(x):
            return ((x[:, None, :] - C[None, :, :]) ** 2).sum(-1).sqrt().min(1).values

        mu, sd = C.mean(0, keepdim=True), C.std(0, keepdim=True).clamp_min(1e-6)
        zo, za = (ce["expr"][hc] - mu) / sd, (ext["expr"] - mu) / sd
        rows.append({"fold": f, "n_train_cells": int(len(tc)),
                     "dist_oneil_heldout": float(nearest(ce["expr"][hc]).median()),
                     "dist_almanac": float(nearest(ext["expr"]).median()),
                     "z_sd_oneil_heldout": float(zo.std()), "z_sd_almanac": float(za.std()),
                     "z_over3_oneil_heldout": float((zo.abs() > 3).float().mean()),
                     "z_over3_almanac": float((za.abs() > 3).float().mean())})
    return pd.DataFrame(rows)


def t_external_chem():
    """And is the external set out of distribution on the DRUG side? (planner 5.3)

    Max Tanimoto (Morgan r=2, 2048 bits) of each ALMANAC compound to any training compound,
    against the same quantity computed inside O'Neil with the drug itself left out. The
    comparison is the point: if ALMANAC's molecules are no further from the training set than
    O'Neil's own molecules are from each other, the drug branch is not the reason the
    external numbers collapse.
    """
    proc = ROOT / "data" / "processed"
    dr = torch.load(proc / "drugs.pt", weights_only=False)
    ext = torch.load(proc / "almanac.pt", weights_only=False)
    A, B = dr["fp2"].numpy() > 0, ext["fp2"].numpy() > 0

    def tanimoto(x, y):
        inter = (x[:, None, :] & y[None, :, :]).sum(-1)
        union = (x[:, None, :] | y[None, :, :]).sum(-1)
        return inter / np.maximum(union, 1)

    ext_max = tanimoto(B, A).max(1)
    own = tanimoto(A, A)
    np.fill_diagonal(own, 0)
    own_max = own.max(1)
    rows = []
    for name, v in (("almanac_to_oneil", ext_max), ("oneil_to_oneil_loo", own_max)):
        rows.append({"comparison": name, "n_drugs": len(v),
                     "max_tanimoto_median": float(np.median(v)),
                     "q25": float(np.quantile(v, 0.25)), "q75": float(np.quantile(v, 0.75)),
                     "frac_below_0.4": float((v < 0.4).mean()),
                     "frac_at_least_0.9": float((v >= 0.9).mean())})
    return pd.DataFrame(rows)


def t_external_control():
    """The pipeline control, split by what the run was actually trained on (planner 5.3).

    1,163 ALMANAC triples are the same experiment as an O'Neil triple (same compound pair by
    InChIKey, same DepMap cell line). For each scored run those rows are grouped by whether
    the O'Neil row sat in that run's TRAINING set or its test/validation set, and the SAME
    predictions are scored twice: against O'Neil's label and against ALMANAC's.

    Reading it: a high `qwk_vs_oneil` on the training group only says the model memorised
    O'Neil, which is what makes it a pipeline check - features, drug indices and the swapped
    fingerprint buffer all have to be right for it to come out high at all. The honest number
    is the test group, and the gap between its two columns is how much of the external
    collapse belongs to the target rather than to the model.
    """
    proc = ROOT / "data" / "processed"
    ext = torch.load(proc / "almanac.pt", weights_only=False)
    if "oneil_row" not in ext:
        return pd.DataFrame()
    sp = torch.load(proc / "splits.pt", weights_only=False)
    m = (ext["oneil_ord3_loewe"] >= 0).numpy()
    yo = ext["oneil_ord3_loewe"].numpy()[m]
    ya = ext["y"]["ord3_loewe"].numpy()[m]
    rows_oneil = ext["oneil_row"].numpy()[m]
    out = []
    for d in sorted(RUNS.glob("*")):
        f = d / "pred_almanac.npz"
        if not (f.exists() and (d / "external_almanac.json").exists()):
            continue
        e = json.loads((d / "external_almanac.json").read_text())
        c = json.loads((d / "config.json").read_text())
        if e["model"] == "syngt" and not (is_plain_cfg(c) or _smooth_cfg(c)):
            continue
        z = np.load(f)
        if "pred" not in z:
            continue
        pred, prob = z["pred"][m], z["prob"][m]
        tr, va, te = sp["splits"][e["split"]][e["fold"]]
        in_train = np.isin(rows_oneil, tr.numpy())
        in_test = np.isin(rows_oneil, np.concatenate([va.numpy(), te.numpy()]))
        for name, sel in (("oneil_train", in_train), ("oneil_heldout", in_test)):
            if sel.sum() < 20:
                continue
            out.append({"run": e["run"], "model": e["model"], "loss": e["loss"],
                        "split": e["split"], "fold": e["fold"], "seed": e["seed"],
                        "group": name, "n": int(sel.sum()),
                        "qwk_vs_oneil": float(M.ord3(yo[sel], pred[sel], prob[sel])["qwk"]),
                        "qwk_vs_almanac": float(M.ord3(ya[sel], pred[sel], prob[sel])["qwk"])})
    e = pd.DataFrame(out)
    if e.empty:
        return e
    e.loc[e.loss == "corn_smooth", "model"] = "syngt_smooth"
    t = agg(e, ["model", "split", "group"], ["qwk_vs_oneil", "qwk_vs_almanac"])
    n = e.groupby(["model", "split", "group"]).n.median().rename("n_triples").reset_index()
    t = t.merge(n, on=["model", "split", "group"], how="left")
    t["model_rank"] = t.model.map({m2: i for i, m2 in enumerate(MODEL_ORDER)})
    return srt(t, ["model_rank", "split", "group"]).drop(columns="model_rank")


def t_external_ranking():
    """A softer question than the 3-class label: does the model RANK ALMANAC at all?

    Spearman between a signed model score and ALMANAC's continuous Loewe value over all
    234,333 triples. The signed score is P(syn) - P(ant), which is the natural ordinal
    summary of a CORN head and is defined for every model here. QWK can sit at zero while a
    ranking signal survives, so this separates "predicts the wrong class" from "carries no
    information about the external set at all". The same correlation against O'Neil's own
    Loewe, on the triples both studies measured, is the reference.
    """
    proc = ROOT / "data" / "processed"
    ext = torch.load(proc / "almanac.pt", weights_only=False)
    sa = ext["score"]["loewe"].numpy()
    m = (ext["oneil_ord3_loewe"] >= 0).numpy()
    so = ext["oneil_loewe"].numpy()[m]
    out = []
    for d in sorted(RUNS.glob("*")):
        f = d / "pred_almanac.npz"
        if not (f.exists() and (d / "external_almanac.json").exists()):
            continue
        e = json.loads((d / "external_almanac.json").read_text())
        c = json.loads((d / "config.json").read_text())
        if e["model"] == "syngt" and not (is_plain_cfg(c) or _smooth_cfg(c)):
            continue
        z = np.load(f)
        if "prob" not in z or z["prob"].ndim != 2 or z["prob"].shape[1] != 3:
            continue                                   # binary runs have no 3-class score
        s = z["prob"][:, 2] - z["prob"][:, 0]
        out.append({"run": e["run"], "model": e["model"], "loss": e["loss"],
                    "setting": e["setting"], "split": e["split"],
                    "spearman_almanac_loewe":
                        float(pd.Series(s).corr(pd.Series(sa), method="spearman")),
                    "spearman_oneil_loewe_overlap":
                        float(pd.Series(s[m]).corr(pd.Series(so), method="spearman")),
                    "spearman_almanac_loewe_overlap":
                        float(pd.Series(s[m]).corr(pd.Series(sa[m]), method="spearman"))})
    e = pd.DataFrame(out)
    if e.empty:
        return e
    e.loc[e.loss == "corn_smooth", "model"] = "syngt_smooth"
    cols = ["spearman_almanac_loewe", "spearman_oneil_loewe_overlap",
            "spearman_almanac_loewe_overlap"]
    t = agg(e, ["model", "setting", "split"], cols)
    t["model_rank"] = t.model.map({m2: i for i, m2 in enumerate(MODEL_ORDER)})
    return srt(t, ["setting", "split", "model_rank"]).drop(columns="model_rank")


def t_external(df):
    """NCI-ALMANAC, zero-shot (planner 5.3, 7.2).

    `all` is the whole external set; the other rows strip the overlap with O'Neil, which is
    9 of 49 cell lines and 21 of 95 compounds. The internal column is the O'Neil test QWK of
    the SAME runs, so the drop from internal to external is read off one line.
    """
    e = external_runs()
    if e.empty:
        return e
    e.loc[e.loss == "corn_smooth", "model"] = "syngt_smooth"
    # the grouping carries `setting` and `split`: the 3-class rows and DTSyn's binary-gap rows
    # are different tasks with different metrics, and a model trained on random folds is not
    # the same model as one trained on held-out combinations
    cols = ["ext_qwk", "ext_bacc", "ext_macro_f1", "ext_mae", "ext_polar_error",
            "ext_recall_ant", "ext_recall_add", "ext_recall_syn",
            "ext_auprc_syn", "ext_macro_auroc", "ext_syn_auprc", "ext_syn_bacc_argmax",
            "ext_auroc", "ext_auprc", "ext_tpr", "ext_f1"]
    by = ["model", "setting", "split", "subset"]
    t = agg(e, by, cols)
    n = e.groupby(by).ext_n.median().rename("n_triples").reset_index()
    t = t.merge(n, on=by, how="left")
    if not df.empty:
        ref = df[df.run.isin(e.run.unique())][["run", "test_qwk", "test_auprc", "test_bacc"]]
        key = e[["run"] + by].merge(ref, on="run", how="left")
        ig = (key[key.subset == "all"].groupby(["model", "setting", "split"])
              [["test_qwk", "test_auprc", "test_bacc"]].mean()
              .rename(columns=lambda c: f"internal_{c[5:]}").reset_index())
        t = t.merge(ig, on=["model", "setting", "split"], how="left")
    t["model_rank"] = t.model.map({m: i for i, m in enumerate(MODEL_ORDER)})
    t["subset_rank"] = t.subset.map({s: i for i, s in enumerate(SUBSETS)})
    return srt(t, ["setting", "split", "model_rank", "subset_rank"]).drop(
        columns=["model_rank", "subset_rank"])


def guard(name, fn, *args):
    """Build one table. A table whose inputs are not in runs/ yet is skipped with a warning
    rather than killing the whole report, so this can be run mid-sweep (planner 7.2)."""
    try:
        t = fn(*args)
        return pd.DataFrame() if t is None else t
    except Exception as e:                                        # noqa: BLE001
        print(f"WARN  table {name} skipped: {type(e).__name__}: {e}", flush=True)
        return pd.DataFrame()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_runs()
    tables = {}
    if not df.empty:
        d1 = df[~df.run.str.match(r"(hp|dx_)")]       # hp / diagnostic runs: own tables only
        tables.update({
            "hp_search": guard("hp_search", t_hp, df),
            "label_agreement": guard("label_agreement", t_label_agreement),
            "architecture_diagnosis": guard("architecture_diagnosis", t_diag, df),
            "g1_reproduction": guard("g1_reproduction", t_g1, df),
            "rq1_label_settings": guard("rq1_label_settings", t_rq1, d1),
            "rq1_gap_cost": guard("rq1_gap_cost", t_rq1_drop, d1),
            "rq2_ordinal_loss": guard("rq2_ordinal_loss", t_rq2, d1),
            "main_ord3": guard("main_ord3", t_main, d1),
            "ablation": guard("ablation", t_ablation, d1),
            "sensitivity": guard("sensitivity", t_sensitivity, d1),
            "external_almanac": guard("external_almanac", t_external, d1),
            "external_label_agreement":
                guard("external_label_agreement", lambda _: t_cross_dataset_labels(), d1),
            "external_domain_shift":
                guard("external_domain_shift", lambda _: t_external_shift(), d1),
            "external_chem_shift":
                guard("external_chem_shift", lambda _: t_external_chem(), d1),
            "external_control":
                guard("external_control", lambda _: t_external_control(), d1),
            "external_ranking":
                guard("external_ranking", lambda _: t_external_ranking(), d1),
            "external_almanac_runs": guard("external_almanac_runs", lambda _: external_runs(), d1),
        })
    ex = load_explains()
    if ex:
        tables.update({
            "xai_faithfulness": guard("xai_faithfulness", t_faithfulness, ex),
            "xai_completeness": guard("xai_completeness", t_completeness, ex),
            "xai_attention_fvt": guard("xai_attention_fvt", t_fvt, ex),
            "rq3_levels": guard("rq3_levels", t_rq3, ex),
            "rq5_stability": guard("rq5_stability", t_stability, ex),
            "rq5_stability_cross_score": guard("rq5_stability_cross_score", t_stability_cross, ex),
            "rq5_stability_cross_fold": guard("rq5_stability_cross_fold", t_stability_fold, ex),
            "xai_plausibility": guard("xai_plausibility", t_plausibility, ex),
            "rq6_pathways": guard("rq6_pathways", t_rq6, ex),
            "xai_graph_vs_fp": guard("xai_graph_vs_fp", t_graph_fp, ex),
        })

    md = ["# Bảng kết quả", "", f"{len(df)} run, {len(ex)} file explain.", ""]
    for name, t in tables.items():
        if t is None or len(t) == 0:
            continue
        t.to_csv(OUT / f"{name}.csv", index=False)
        md += [f"## {name}", "", t.round(4).to_markdown(index=False), ""]
    (OUT / "tables.md").write_text("\n".join(md))
    print(f"{len(df)} runs, {len(ex)} explains -> {sum(len(t) > 0 for t in tables.values())} tables")
    for name, t in tables.items():
        if len(t):
            print(f"  {name}: {len(t)} rows")


if __name__ == "__main__":
    main()
