"""Raw CSVs -> src/data/processed/oneil.pt, then print the data report (planner 5.1).

Run: python -m src.data.prepare [--min-score 700] [--hops 1]
"""
import argparse
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import torch

HERE = Path(__file__).parent
RAW = HERE / "raw"
OUT = HERE / "processed" / "oneil.pt"

# DrugComb v1.4 has no study_name column. O'Neil is the first study: block_id 1..92208
# (22,737 triples x 4 replicates; block 92209 starts the next study, KBM-7).
ONEIL_LAST_BLOCK = 92208
SCORES = ["synergy_loewe", "synergy_bliss", "synergy_zip", "synergy_hsa"]


def load_oneil(cells):
    d = pd.read_csv(RAW / "summary_table_v1.4.csv", usecols=["block_id", "drug_row", "drug_col",
                    "cell_line_name"] + SCORES, dtype={"drug_row": str, "drug_col": str})
    d = d[d.block_id <= ONEIL_LAST_BLOCK]
    n_all = d.groupby(["drug_row", "drug_col", "cell_line_name"]).ngroups
    # canonical order so (A,B) and (B,A) replicates fall into one triple
    a, b = np.minimum(d.drug_row, d.drug_col), np.maximum(d.drug_row, d.drug_col)
    d = d.assign(drug_a=a, drug_b=b)
    d = d[d.cell_line_name.isin(cells)]
    return d.groupby(["drug_a", "drug_b", "cell_line_name"])[SCORES].mean().reset_index(), n_all


def load_expression(model_ids):
    e = pd.read_csv(RAW / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv", index_col=0)
    e = e[e.IsDefaultEntryForModel == "Yes"].set_index("ModelID")
    e = e.drop(columns=["SequencingID", "ModelConditionID", "IsDefaultEntryForMC", "IsDefaultEntryForModel"])
    e.columns = [c.split(" (")[0] for c in e.columns]  # "TP53 (7157)" -> "TP53"
    e = e.loc[:, ~e.columns.duplicated()].astype(np.float32)
    # z-score per gene across all DepMap models, so 0 = pan-cancer average
    z = (e - e.mean()) / e.std().replace(0, 1)
    return z.loc[model_ids]


def load_string(min_score):
    info = pd.read_csv(RAW / "9606.protein.info.v12.0.txt.gz", sep="\t", usecols=[0, 1])
    name = dict(zip(info.iloc[:, 0], info.iloc[:, 1]))
    l = pd.read_csv(RAW / "9606.protein.links.v12.0.txt.gz", sep=" ")
    l = l[l.combined_score >= min_score]
    g = nx.Graph()
    g.add_edges_from(zip(l.protein1.map(name), l.protein2.map(name)))
    g.remove_edges_from(nx.selfloop_edges(g))
    return g


def main(min_score=700, hops=1):
    cmap = pd.read_csv(HERE / "cell_line_map.csv")
    cmap = cmap[cmap.match != "none"]
    syn, n_all = load_oneil(set(cmap.drugcomb_name))
    expr = load_expression(cmap.model_id.tolist())
    expr.index = cmap.drugcomb_name.tolist()

    targets = pd.read_csv(HERE / "drug_targets.csv")
    g = load_string(min_score)
    g = g.subgraph(set(g) & set(expr.columns)).copy()
    seeds = set(targets.gene) & set(g)
    keep = set(seeds)
    for s in seeds:
        keep |= set(nx.single_source_shortest_path_length(g, s, cutoff=hops))
    g = g.subgraph(keep).copy()

    genes = sorted(g)
    gi = {x: i for i, x in enumerate(genes)}
    drugs = sorted(set(syn.drug_a) | set(syn.drug_b))
    di = {x: i for i, x in enumerate(drugs)}
    cells = sorted(set(syn.cell_line_name))
    ci = {x: i for i, x in enumerate(cells)}

    T = torch.zeros(len(drugs), len(genes))
    for d, x in zip(targets.drug, targets.gene):
        if d in di and x in gi:
            T[di[d], gi[x]] = 1
    edges = torch.tensor([[gi[u], gi[v]] for u, v in g.edges()]).T  # undirected, each edge once

    data = {
        "genes": genes, "drugs": drugs, "cells": cells,
        "edge_index": edges,
        "expr": torch.tensor(expr.loc[cells, genes].values),
        "targets": T,
        "triples": torch.tensor(np.c_[syn.drug_a.map(di), syn.drug_b.map(di), syn.cell_line_name.map(ci)]),
        "scores": {s.removeprefix("synergy_"): torch.tensor(syn[s].values, dtype=torch.float32) for s in SCORES},
        "config": {"min_score": min_score, "hops": hops, "drugcomb": "v1.4 (zenodo 11102665)",
                   "string": "v12.0", "targets": "drug_targets.csv"},
    }
    OUT.parent.mkdir(exist_ok=True)
    torch.save(data, OUT)
    report(data, g, gi, n_all, targets)


def report(data, g, gi, n_all, targets):
    T, drugs, tr = data["targets"], data["drugs"], data["triples"]
    E = data["edge_index"].shape[1]
    print(f"triples: {len(tr)} kept of {n_all} O'Neil triples (rest: cell line without expression)")
    print(f"drugs {len(drugs)}, cells {len(data['cells'])}, genes {len(data['genes'])}, edges {E}")
    print(f"MLP input after flatten at proj=4: {4 * len(data['genes'])}")
    lost = sorted(set(targets.gene) - set(gi))
    print(f"target genes not in filtered network ({len(lost)}): {lost}")
    no_t = [d for d, n in zip(drugs, T.sum(1)) if n == 0]
    print(f"drugs without targets on network ({len(no_t)}): {no_t}")
    n_bad = int(((T[tr[:, 0]].sum(1) == 0) | (T[tr[:, 1]].sum(1) == 0)).sum())
    print(f"triples with a target-less drug: {n_bad} ({n_bad / len(tr):.1%})")

    for name, s in data["scores"].items():
        for t in (5, 10, 20):
            ant, syn = (s < -t).float().mean().item(), (s > t).float().mean().item()
            print(f"{name:6s} ±{t:<2d} ant {ant:5.1%} add {1 - ant - syn:5.1%} syn {syn:5.1%}")

    # shortest distance between target sets of each pair, on the filtered network
    tset = {i: [data["genes"][j] for j in T[i].nonzero().flatten().tolist()] for i in range(len(drugs))}
    dist = []
    for a, b in {(int(a), int(b)) for a, b, _ in tr}:
        if tset[a] and tset[b]:
            ln = nx.multi_source_dijkstra_path_length(g, set(tset[a]))
            dist.append(min((ln.get(x, np.inf) for x in tset[b]), default=np.inf))
    print("pair target distance:", pd.Series(dist).value_counts().sort_index().to_dict())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--min-score", type=int, default=700)
    # 1-hop keeps every target-target shortest path of length <= 3 (any interior node is
    # adjacent to an endpoint), which covers all O'Neil pairs; 2-hop gives 12k genes.
    p.add_argument("--hops", type=int, default=1)
    main(**vars(p.parse_args()))
