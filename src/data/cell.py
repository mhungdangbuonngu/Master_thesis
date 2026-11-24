"""Cell-line features -> data/processed/cells.pt  (planner 4.2).

    python -m src.data.cell [--min-score 700] [--dim 128]

Expression: DepMap log2(TPM+1) restricted to the 978 LINCS L1000 landmark genes
(pr_is_lm == 1 in GSE92742_Broad_LINCS_gene_info). Stored RAW: the z-score is fitted per
fold on training cells only (src/data/splits.py + the training loop), so nothing about the
test cells leaks into the scaler.

Gene embeddings: node2vec on STRING v12 (combined_score >= 700) over the whole network,
then the vectors of our genes are taken. This is the DTSyn / MD-Syn recipe and it is the
only place the PPI enters the model, so "node2vec on a degree-preserving rewired STRING"
is a cheap and informative ablation (built here too).
"""
import argparse
import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import torch
from gensim.models import Word2Vec

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "src" / "data" / "raw"
OUT = ROOT / "data" / "processed"


def landmark_genes():
    g = pd.read_csv(RAW / "l1000_gene_info.txt.gz", sep="\t")
    return g[g.pr_is_lm == 1].pr_gene_symbol.tolist()


def expression(model_ids):
    e = pd.read_csv(RAW / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv", index_col=0)
    e = e[e.IsDefaultEntryForModel == "Yes"].set_index("ModelID")
    e = e.drop(columns=[c for c in ["SequencingID", "ModelConditionID", "IsDefaultEntryForMC",
                                    "IsDefaultEntryForModel"] if c in e.columns])
    e.columns = [c.split(" (")[0] for c in e.columns]       # "TP53 (7157)" -> "TP53"
    e = e.loc[:, ~e.columns.duplicated()].astype(np.float32)
    return e


def string_graph(min_score):
    info = pd.read_csv(RAW / "9606.protein.info.v12.0.txt.gz", sep="\t", usecols=[0, 1])
    name = dict(zip(info.iloc[:, 0], info.iloc[:, 1]))
    l = pd.read_csv(RAW / "9606.protein.links.v12.0.txt.gz", sep=" ")
    l = l[l.combined_score >= min_score]
    g = nx.Graph()
    g.add_edges_from(zip(l.protein1.map(name), l.protein2.map(name)))
    g.remove_edges_from(nx.selfloop_edges(g))
    return g


def walks(g, n_walks=10, length=40, seed=0):
    """Uniform random walks (node2vec with p=q=1, i.e. DeepWalk sampling)."""
    rng = np.random.default_rng(seed)
    nodes = list(g.nodes())
    adj = {n: list(g.neighbors(n)) for n in nodes}
    out = []
    for _ in range(n_walks):
        rng.shuffle(nodes)
        for n in nodes:
            w = [n]
            for _ in range(length - 1):
                nb = adj[w[-1]]
                if not nb:
                    break
                w.append(nb[rng.integers(len(nb))])
            out.append(w)
    return out


def embed(g, genes, dim, seed=0, tag=""):
    w = walks(g, seed=seed)
    m = Word2Vec(w, vector_size=dim, window=5, min_count=0, sg=1, workers=4, epochs=5, seed=seed)
    emb = np.zeros((len(genes), dim), dtype=np.float32)
    hit = 0
    for i, gene in enumerate(genes):
        if gene in m.wv:
            emb[i] = m.wv[gene]
            hit += 1
    print(f"  node2vec{tag}: {hit}/{len(genes)} genes have a vector")
    return torch.tensor(emb), hit


def rewire_keep_degree(g, seed=0):
    """Degree-preserving double-edge swap; the null network for the node2vec ablation."""
    h = g.copy()
    nx.double_edge_swap(h, nswap=10 * h.number_of_edges(), max_tries=100 * h.number_of_edges(),
                        seed=seed)
    return h


def main(min_score=700, dim=128):
    trip = pd.read_csv(OUT / "triples.csv")
    cmap = pd.read_csv(ROOT / "src" / "data" / "cell_line_map.csv")
    cells = sorted(trip.cell_line_name.unique())
    mid = dict(zip(cmap.drugcomb_name, cmap.model_id))
    model_ids = [mid[c] for c in cells]

    e = expression(model_ids)
    lm = landmark_genes()
    genes = [g for g in lm if g in e.columns]
    x = torch.tensor(e.loc[model_ids, genes].values.astype(np.float32))
    var_all = torch.tensor(e[genes].var(axis=0).values.astype(np.float32))   # variance over ALL
    # DepMap models, not just ours: token selection must not depend on the 37 cells in our data

    g = string_graph(min_score)
    print(f"STRING: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges")
    emb, hit = embed(g, genes, dim, tag="")
    emb_rw, _ = embed(rewire_keep_degree(g, 0), genes, dim, tag=" (rewired null)")

    obj = {"cells": cells, "model_ids": model_ids, "genes": genes, "expr": x,
           "gene_var_all_models": var_all, "gene_emb": emb, "gene_emb_rewired": emb_rw,
           "tissue": dict(zip(trip.cell_line_name, trip.tissue))}
    torch.save(obj, OUT / "cells.pt")

    rep = {"cells": len(cells), "landmark_in_l1000": len(lm), "landmark_in_depmap": len(genes),
           "string_min_score": min_score, "string_nodes": g.number_of_nodes(),
           "string_edges": g.number_of_edges(), "node2vec_dim": dim, "genes_with_vector": hit,
           "expr_mean": float(x.mean()), "expr_std": float(x.std())}
    (OUT / "provenance_cells.json").write_text(json.dumps(rep, indent=1))
    print(f"cells {len(cells)}  genes {len(genes)}/{len(lm)} landmark  expr {tuple(x.shape)}")
    return obj


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--min-score", type=int, default=700)
    p.add_argument("--dim", type=int, default=128)
    a = p.parse_args()
    main(a.min_score, a.dim)
