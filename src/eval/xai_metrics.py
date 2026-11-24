"""Metrics for the explanations, each with its own null  (planner 6.3).

Everything is reported as (value, null, diff). A raw fidelity number is meaningless here:
switching off 25% of the genes moves the output a lot whatever the 25% are, so the only
readable quantity is the gap between the explanation's deletion and a matched random one.

Faithfulness  Fid+, Fid-, the completeness gap, and the Faithfulness Violation Test
Stability     Jaccard@k across seeds, folds, synergy scores and thresholds
Plausibility  hypergeometric enrichment of the top genes in drug targets and KEGG pathways,
              against a null of random genes matched on expression decile
Reported separately, never mixed: a faithful-but-implausible explanation means the model
learned something odd; a plausible-but-unfaithful one means the explainer is wrong.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import hypergeom, pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[2]
KEGG = ROOT / "src" / "data" / "raw" / "kegg"


# ------------------------------------------------------------------------- faithfulness
def fidelity(rec_list, key):
    """Fid+ = f(full) - f(delete top-k), against the matched random deletion."""
    val, null = [], []
    for r in rec_list:
        if key not in r:
            continue
        f = r[key]
        val.append(f["full"] - f["del_top"])
        null.append(float(np.mean([f["full"] - x for x in f["del_rand"]])))
    if not val:
        return {}
    v, n = np.array(val), np.array(null)
    return {"fid_plus": float(v.mean()), "null": float(n.mean()), "diff": float((v - n).mean()),
            "n": len(v), "win_rate": float((v > n).mean())}


def fidelity_minus(rec_list, key):
    """Fid- = f(full) - f(keep only top-k). Small is good, but the inputs are far
    out of distribution, so this is reported with a warning and never used to conclude."""
    val = [r[key]["full"] - r[key]["keep_top"] for r in rec_list if key in r and "keep_top" in r[key]]
    return {"fid_minus": float(np.mean(val)), "n": len(val)} if val else {}


def completeness(rec_list, which):
    """|sum(attr) - (f(1)-f(0))| relative to the swing, i.e. how trustworthy IG is here."""
    out = {}
    for unit in ("gene", "frag"):
        rel = []
        for r in rec_list:
            g = r.get(f"gap_{which}")
            if g is None:
                continue
            swing = abs(g["f1"] - g["f0"]) + 1e-9
            rel.append(abs(g[unit]) / swing)
        if rel:
            out[unit] = float(np.median(rel))
    return out


def violation_test(rec_list, which):
    """Faithfulness Violation Test (Liu et al., ICML 2022), in the deletion form.

    For the top-k units the attribution ranks highest, compare the attribution value with
    the measured effect of deleting that unit alone. A faithful explainer gives a positive
    correlation. `violation_rate` is the share of triples whose correlation is negative:
    the attribution there points the opposite way to the model's real sensitivity.
    """
    rho, viol = [], 0
    for r in rec_list:
        f = r.get(f"fvt_{which}")
        if f is None or len(f["attr"]) < 4:
            continue
        a, e = np.asarray(f["attr"], dtype=float), np.asarray(f["effect"], dtype=float)
        if a.std() < 1e-9 or e.std() < 1e-9:
            continue
        s = spearmanr(a, e).statistic
        rho.append(s)
        viol += int(s < 0)
    if not rho:
        return {}
    return {"spearman": float(np.mean(rho)), "violation_rate": viol / len(rho), "n": len(rho)}


def attention_vs_ig(rec_list, which="contrast", k=50):
    """Does attention rank genes like IG does, and does deleting by attention hurt as much?"""
    j = []
    for r in rec_list:
        att = r.get("att_cls_gene")
        ig = r.get(f"gene_attr_{which}")
        if att is None or ig is None:
            continue
        j.append(overlap(np.asarray(att, dtype=float), np.asarray(ig, dtype=float), k))
    return {"jaccard_top_k": float(np.mean(j)), "n": len(j)} if j else {}


# ----------------------------------------------------------------------------- stability
def topk(v, k):
    v = np.asarray(v, dtype=float)
    return set(np.argsort(-v)[:k].tolist())


def jaccard(a, b):
    return len(a & b) / max(len(a | b), 1)


def overlap(v1, v2, k):
    return jaccard(topk(v1, k), topk(v2, k))


def cosine(v1, v2):
    """Cosine of the two full attribution vectors: agreement on the overall direction.

    Reported next to Jaccard@k because the two answer different questions. A high cosine with a
    Jaccard at the null means the explanations agree on the broad shape but not on which k genes
    come out on top, and it is the second number that decides whether a gene list can be handed
    to anyone. Only Jaccard was computed before, so that distinction could not be read off the
    tables at all.
    """
    a, b = np.asarray(v1, dtype=float).ravel(), np.asarray(v2, dtype=float).ravel()
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else np.nan


def stability(attr_by_run, k=50):
    """Jaccard@k and cosine of THE SAME triple explained by different runs.

    The caller must pass attribution lists already aligned triple by triple. `stability_null`
    below deliberately pairs different triples, so if the caller's lists are misaligned the two
    functions compute the same quantity and stability comes out at the null no matter what the
    model does. That is not a hypothetical: it is what the RQ5 tables did until the explained
    triples were matched by id.
    """
    runs = list(attr_by_run)
    if len(runs) < 2:
        return {}
    n = min(len(attr_by_run[r]) for r in runs)
    jac, cos = [], []
    for i in range(n):
        for x in range(len(runs)):
            for y in range(x + 1, len(runs)):
                a, b = attr_by_run[runs[x]][i], attr_by_run[runs[y]][i]
                jac.append(overlap(a, b, k))
                cos.append(cosine(a, b))
    return {"jaccard": float(np.mean(jac)), "cosine": float(np.nanmean(cos)),
            "pairs": len(jac), "triples": n}


def stability_null(attr_by_run, k=50, seed=0):
    """Null: pair up DIFFERENT triples, i.e. how much two explanations overlap by chance."""
    runs = list(attr_by_run)
    if len(runs) < 2:
        return {}
    rng = np.random.default_rng(seed)
    n = min(len(attr_by_run[r]) for r in runs)
    jac, cos = [], []
    for i in range(n):
        j = int(rng.integers(n))
        if j == i:
            j = (j + 1) % n
        a, b = attr_by_run[runs[0]][i], attr_by_run[runs[1]][j]
        jac.append(overlap(a, b, k))
        cos.append(cosine(a, b))
    return {"jaccard": float(np.mean(jac)), "cosine": float(np.nanmean(cos)), "triples": n}


# -------------------------------------------------------------------------- plausibility
def kegg_sets(min_size=5, max_size=500):
    """pathway id -> set of gene symbols, from the KEGG REST dumps."""
    sym = {}
    for line in (KEGG / "genes.tsv").read_text().splitlines():
        p = line.split("\t")
        if len(p) >= 4 and p[1] == "CDS":
            names = p[3].split(";")[0]
            sym[p[0]] = names.split(",")[0].strip()
    names = {}
    for line in (KEGG / "pathways.tsv").read_text().splitlines():
        p = line.split("\t")
        if len(p) == 2:
            names[p[0]] = p[1].replace(" - Homo sapiens (human)", "")
    sets = {}
    for line in (KEGG / "gene2pathway.tsv").read_text().splitlines():
        p = line.split("\t")
        if len(p) != 2:
            continue
        pw = p[0].replace("path:", "")
        g = sym.get(p[1])
        if g:
            sets.setdefault(pw, set()).add(g)
    return ({k: v for k, v in sets.items() if min_size <= len(v) <= max_size}, names)


def drug_targets():
    t = pd.read_csv(ROOT / "src" / "data" / "drug_targets.csv")
    return t.groupby("drug").gene.apply(set).to_dict()


def enrichment(top_genes, gene_set, universe):
    """One-sided hypergeometric p of seeing this many set members among the top genes."""
    top, s, u = set(top_genes), set(gene_set) & set(universe), set(universe)
    hit = len(top & s)
    if not s or not top:
        return 1.0, 0
    return float(hypergeom.sf(hit - 1, len(u), len(s), len(top))), hit


def target_hit_rate(rec_list, idx_list, genes, trip, drugs, which="contrast", k=50,
                    n_null=20, expr=None, seed=0):
    """Share of triples whose top-k genes are enriched in the two drugs' known targets.

    This is the quantity SynergyX reports as 62.2%, measured here with a null of random
    gene sets matched on expression decile (so a trivially "always pick highly expressed
    genes" explainer does not score).
    """
    tg = drug_targets()
    rng = np.random.default_rng(seed)
    decile = None
    if expr is not None:
        m = np.asarray(expr).mean(0)
        decile = np.digitize(m, np.quantile(m, np.linspace(0.1, 0.9, 9)))
    sig, sig_null, hits = 0, 0, []
    n = 0
    for r, i in zip(rec_list, idx_list):
        a = r.get(f"gene_attr_{which}")
        if a is None:
            continue
        a = np.asarray(a, dtype=float)
        order = np.argsort(-a)[:k]
        top = [genes[j] for j in order]
        da, db, _ = trip[int(i)].tolist()
        tset = tg.get(drugs[da], set()) | tg.get(drugs[db], set())
        if not tset:
            continue
        n += 1
        p, hit = enrichment(top, tset, genes)
        sig += int(p < 0.05)
        hits.append(hit)
        pn = []
        for _ in range(n_null):
            if decile is None:
                pick = rng.choice(len(genes), k, replace=False)
            else:                                    # match the expression-decile profile
                pick = []
                for dd in decile[order]:
                    pool = np.flatnonzero(decile == dd)
                    pick.append(int(rng.choice(pool)))
                pick = np.array(pick)
            pn.append(enrichment([genes[j] for j in pick], tset, genes)[0])
        sig_null += int(np.mean([x < 0.05 for x in pn]) > 0.5)
    if not n:
        return {}
    return {"frac_enriched": sig / n, "null_frac_enriched": sig_null / n,
            "mean_hits": float(np.mean(hits)), "n": n}


def pathway_profile(rec_list, genes, which="contrast", k=50, top_pw=10):
    """Which KEGG pathways the explanations land in, pooled over triples (for RQ6)."""
    sets, names = kegg_sets()
    count = {}
    for r in rec_list:
        a = r.get(f"gene_attr_{which}")
        if a is None:
            continue
        top = {genes[j] for j in np.argsort(-np.asarray(a, dtype=float))[:k]}
        for pw, s in sets.items():
            p, hit = enrichment(top, s, genes)
            if p < 0.05:
                count[pw] = count.get(pw, 0) + 1
    tot = max(len(rec_list), 1)
    out = sorted(count.items(), key=lambda x: -x[1])[:top_pw]
    return [{"pathway": pw, "name": names.get(pw, pw), "frac_triples": c / tot} for pw, c in out]


# ----------------------------------------------------------- RQ3: interaction vs logit level
def level_divergence(rec_list, k=50):
    """Jaccard@k between the contrast-level and logit-level top genes, and vs the ant level."""
    out = {}
    for a, b in (("contrast", "logit"), ("contrast", "ant"), ("logit", "ant")):
        v = [overlap(np.asarray(r[f"gene_attr_{a}"], dtype=float),
                     np.asarray(r[f"gene_attr_{b}"], dtype=float), k)
             for r in rec_list if f"gene_attr_{a}" in r and f"gene_attr_{b}" in r]
        if v:
            out[f"{a}_vs_{b}"] = float(np.mean(v))
    return out


def frag_interaction_summary(rec_list):
    """How much of the pair signal is genuinely second order (planner 6.2)."""
    ratio, pos = [], []
    for r in rec_list:
        phi = np.asarray(r.get("frag_phi"))
        if phi is None or phi.size == 0:
            continue
        fi, fj = (np.asarray(x) for x in r["frag_single"])
        first = np.abs(np.subtract.outer(fi * 0, fj * 0) + fi[:, None] + fj[None, :]).mean() + 1e-9
        ratio.append(float(np.abs(phi).mean() / first))
        pos.append(float((phi > 0).mean()))
    return {"interaction_over_first_order": float(np.mean(ratio)) if ratio else np.nan,
            "frac_positive_phi": float(np.mean(pos)) if pos else np.nan, "n": len(ratio)}
