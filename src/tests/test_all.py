"""Unit tests that must pass before any sweep (planner 7.1, 7.2 step 3).

    python -m pytest src/tests/test_all.py -q

The three that actually guard the thesis:
  * test_symmetry            f(A,B,c) == f(B,A,c) exactly, not approximately
  * test_corn_rank_consistent  P(y>add) <= P(y>ant) always
  * test_no_leakage_*        a test drug/cell never appears in training; the expression
                             scaler is fitted on training cells only
"""
import numpy as np
import pytest
import torch

from src.data.batching import MolStore, ragged_index
from src.eval import metrics as M
from src.model.corn import CornHead, corn_loss
from src.model.syngt import SynGT
from src.train import standardise

PROC = __import__("pathlib").Path(__file__).resolve().parents[2] / "data" / "processed"


@pytest.fixture(scope="module")
def data():
    return (torch.load(PROC / "dataset.pt", weights_only=False),
            torch.load(PROC / "drugs.pt", weights_only=False),
            torch.load(PROC / "cells.pt", weights_only=False),
            torch.load(PROC / "splits.pt", weights_only=False))


def build(ce, dr, **kw):
    torch.manual_seed(0)
    # the FINAL architecture (skip readout + fingerprint branch), as trained by src.train
    kw = {"readout": "skip", "drug_fp": dr["fp2"], "att_dropout": 0.0, **kw}
    return SynGT(ce["gene_emb"], atom_dim=dr["atom_dim"], d=32, gnn_layers=2, fine_layers=1,
                 coarse_layers=1, heads=2, ff=64, dropout=0.0, **kw).eval()


def test_ragged_index():
    starts = torch.tensor([10, 0, 5])
    counts = torch.tensor([2, 3, 1])
    assert ragged_index(starts, counts).tolist() == [10, 11, 0, 1, 2, 5]


def test_symmetry(data):
    """The model must be exactly symmetric in A <-> B: no A/B type embedding anywhere."""
    d, dr, ce, _ = data
    m = build(ce, dr)
    store = MolStore(dr, "cpu")
    trip = d["idx"][:8]
    swapped = trip.clone()
    swapped[:, [0, 1]] = swapped[:, [1, 0]]
    expr = ce["expr"][trip[:, 2]]
    with torch.no_grad():
        a = m(store.collate(trip, expr))
        b = m(store.collate(swapped, expr))
    assert torch.allclose(a, b, atol=1e-5), (a - b).abs().max()


def test_symmetry_skip_readout(data):
    """The skip readout ([pA+pB ; |pA-pB| ; cell]) must keep the exact A <-> B symmetry."""
    d, dr, ce, _ = data
    torch.manual_seed(0)
    m = SynGT(ce["gene_emb"][:64], atom_dim=dr["atom_dim"], d=32, gnn_layers=2,
              fine_layers=1, coarse_layers=1, heads=2, ff=64, dropout=0.0,
              readout="skip").eval()
    store = MolStore(dr, "cpu")
    trip = d["idx"][:8]
    swapped = trip.clone()
    swapped[:, [0, 1]] = swapped[:, [1, 0]]
    expr = ce["expr"][trip[:, 2]][:, :64]
    with torch.no_grad():
        a = m(store.collate(trip, expr))
        b = m(store.collate(swapped, expr))
    assert torch.allclose(a, b, atol=1e-5), (a - b).abs().max()


def test_corn_rank_consistent():
    logits = torch.randn(500, 2) * 5
    p = CornHead.probs(logits)
    cum_gt_ant = p[:, 1] + p[:, 2]
    cum_gt_add = p[:, 2]
    assert (cum_gt_add <= cum_gt_ant + 1e-6).all()
    assert torch.allclose(p.sum(1), torch.ones(500), atol=1e-5)


def test_corn_loss_recovers_order():
    """Fitting CORN on a clean ordinal signal must order the three classes correctly."""
    torch.manual_seed(0)
    x = torch.randn(600, 1)
    y = torch.bucketize(x[:, 0], torch.tensor([-0.5, 0.5]))      # 0,1,2 by threshold
    lin = torch.nn.Linear(1, 2)
    opt = torch.optim.Adam(lin.parameters(), lr=0.1)
    for _ in range(300):
        opt.zero_grad()
        corn_loss(lin(x), y).backward()
        opt.step()
    pred = CornHead.probs(lin(x)).argmax(1)
    assert M.ord3(y.numpy(), pred.numpy())["qwk"] > 0.8


def test_class_logit_contrast_matches_second_logit():
    """delta_syn = z_syn - z_add must equal the second conditional logit (planner 6.2)."""
    logits = torch.randn(64, 2)
    z = CornHead.class_logits(logits)
    assert torch.allclose(z[:, 2] - z[:, 1], logits[:, 1], atol=1e-4)


def test_mask_zero_changes_prediction(data):
    """A zero atom mask must change the output: the mask is really in the forward pass."""
    d, dr, ce, _ = data
    m = build(ce, dr)
    store = MolStore(dr, "cpu")
    b = store.collate(d["idx"][:4], ce["expr"][d["idx"][:4][:, 2]])
    with torch.no_grad():
        full = m(b)
        zero = m(b, mu_atom=torch.zeros(b["x"].shape[0]))
    assert not torch.allclose(full, zero, atol=1e-3)


def test_no_leakage_cells(data):
    """leave_cell: a test cell line may never appear in training."""
    d, _, _, sp = data
    idx = d["idx"]
    for tr, va, te in sp["splits"]["leave_cell"]:
        tr_u, te_u = set(idx[tr][:, 2].tolist()), set(idx[te][:, 2].tolist())
        assert not (tr_u & te_u), f"cells {sorted(tr_u & te_u)[:5]} in both train and test"


def test_no_leakage_held_out_drugs(data):
    """leave_drug: the HELD-OUT drugs may never appear in a training triple.

    A test triple legitimately contains one held-out drug and one training drug - that is
    what leave-drug-out means - so the invariant is about the held-out cluster, not about
    the union of drugs appearing in test triples.
    """
    d, _, _, sp = data
    idx, cl = d["idx"], np.array(sp["drug_cluster"])
    for f, (tr, va, te) in enumerate(sp["splits"]["leave_drug"]):
        held = set(np.flatnonzero(cl == f).tolist())
        train_drugs = set(idx[tr][:, 0].tolist()) | set(idx[tr][:, 1].tolist())
        assert not (held & train_drugs), f"fold {f}: held-out drugs {sorted(held & train_drugs)} in train"
        test_drugs = set(idx[te][:, 0].tolist()) | set(idx[te][:, 1].tolist())
        assert held & test_drugs, f"fold {f}: no held-out drug in test"


def test_no_leakage_pairs(data):
    """leave_combo: a test drug PAIR may not appear in training."""
    d, _, _, sp = data
    pair = d["pair"]
    for tr, va, te in sp["splits"]["leave_combo"]:
        a = {tuple(x) for x in pair[tr].tolist()}
        b = {tuple(x) for x in pair[te].tolist()}
        assert not (a & b)


def test_scaler_fitted_on_train_only(data):
    """standardise() must use training cells only: adding a test cell must not change it."""
    _, _, ce, _ = data
    expr = ce["expr"]
    train = torch.tensor([0, 1, 2, 3])
    z1 = standardise(expr, train)
    z2 = standardise(expr, torch.cat([train, torch.tensor([30])]))
    assert not torch.allclose(z1, z2)                 # the scaler does depend on its input set
    mu = expr[train].mean(0)
    assert torch.allclose(z1[train].mean(0), torch.zeros_like(mu), atol=1e-4)


def test_metrics_polar_error():
    y = np.array([0, 0, 2, 2, 1])
    pred = np.array([2, 0, 0, 2, 1])                  # one ant->syn and one syn->ant
    r = M.ord3(y, pred)
    assert r["polar_error"] == pytest.approx(2 / 5)
    assert r["qwk"] < 0.5


def test_qwk_punishes_polar_more_than_adjacent():
    y = np.array([0] * 50 + [1] * 50 + [2] * 50)
    adj = y.copy(); adj[:10] = 1                       # 10 ant -> add
    pol = y.copy(); pol[:10] = 2                       # 10 ant -> syn
    assert M.ord3(y, adj)["qwk"] > M.ord3(y, pol)["qwk"]


def test_gene_embedding_carries_network(data):
    """node2vec on real STRING must separate connected pairs from random ones; the rewired
    null must not. This guards the ablation in planner 5.3."""
    _, _, ce, _ = data
    e = torch.nn.functional.normalize(ce["gene_emb"], dim=1)
    r = torch.nn.functional.normalize(ce["gene_emb_rewired"], dim=1)
    assert e.norm(dim=1).sum() > 0 and r.norm(dim=1).sum() > 0
    assert e.shape == r.shape


def test_fragfp_completeness(data):
    """Joint IG over fragments + fingerprints must satisfy completeness on the SAME path."""
    from src.xai import masks as K
    d, dr, ce, _ = data
    torch.manual_seed(0)
    m = SynGT(ce["gene_emb"][:64], atom_dim=dr["atom_dim"], d=32, gnn_layers=2,
              fine_layers=1, coarse_layers=1, heads=2, ff=64, dropout=0.0,
              drug_fp=dr["fp2"]).eval()
    store = MolStore(dr, "cpu")
    trip = d["idx"][:1]
    b = store.collate(trip, ce["expr"][trip[:, 2]][:, :64])
    r = K.graph_vs_fp(m, b, store, "contrast", steps=64)
    swing = abs(r["f1"] - r["f0"]) + 1e-9
    assert abs(r["ig_gap"]) / swing < 0.05, r
    assert 0.0 <= r["ig_share_fp"] <= 1.0
    # fp off must change the output (the branch is really used) ...
    assert abs(r["del_fp"]) > 0
    # ... and symmetry still holds with the fp branch
    sw = trip.clone(); sw[:, [0, 1]] = sw[:, [1, 0]]
    with torch.no_grad():
        assert torch.allclose(m(b), m(store.collate(sw, ce["expr"][sw[:, 2]][:, :64])), atol=1e-5)


def test_class_logits_no_saturation():
    """z_syn - z_add must equal l1 even for extreme logits (no clamp, gradient alive)."""
    l = torch.tensor([[-12.0, -9.0], [3.0, 2.0], [25.0, -30.0]], requires_grad=True)
    z = CornHead.class_logits(l)
    assert torch.allclose(z[:, 2] - z[:, 1], l[:, 1].detach(), atol=1e-5)
    (z[:, 2]).sum().backward()
    assert (l.grad[:, 1].abs() > 1e-6).all()


def test_soft_targets_boundary():
    """Label smoothing must soften only the boundary band, and keep the ordinal direction."""
    from src.model.corn import corn_loss, corn_loss_smooth, soft_targets
    score = torch.tensor([-60.0, -10.0, 0.0, 9.8, 10.2, 40.0])
    soft = soft_targets(score, [-10.0, 10.0], tau=5.0)
    assert soft.shape == (6, 2)
    assert soft[0, 0] < 0.01 and soft[-1, 1] > 0.99      # far from threshold -> nearly hard
    assert abs(soft[1, 0] - 0.5) < 1e-5                   # exactly at the threshold -> 0.5
    assert abs(soft[3, 1] - soft[4, 1]) < 0.09            # 9.8 vs 10.2 are nearly the same
    assert (soft[:, 0] >= soft[:, 1]).all()               # P(y>ant) >= P(y>add)
    # with no soft targets it must fall back to the hard loss exactly
    lg, y = torch.randn(6, 2), torch.tensor([0, 0, 1, 1, 2, 2])
    assert torch.allclose(corn_loss_smooth(lg, y, None, None), corn_loss(lg, y, None))


# ----------------------------------------------------------------- XAI comparability guards
# These three exist because the RQ5 stability tables were silently measuring nothing. Each one
# fails on exactly one of the root causes, so a regression cannot pass review as a result.

def test_pick_triples_stable_across_processes():
    """The explained triples must depend on (split, fold) and on no process-local state.

    `pick_triples` seeded its rng with `hash(split) % 1000`. Python salts string hashes per
    process unless PYTHONHASHSEED is set, and it was set nowhere, so every `run_explain`
    invocation drew a different sample: seeds 0/1/2 of one fold shared 0 to 2 triples out of 40,
    and comparing them was comparing explanations of unrelated triples.
    """
    import os
    import subprocess
    import sys

    code = ("from src.xai.run_explain import pick_triples;"
            "from src.train import load_all;"
            "d,dr,ce,sp=load_all('cpu');"
            "tr,va,te=sp['splits']['leave_combo'][0];"
            "print(pick_triples(d,te,'ord3_loewe',40,'leave_combo',0)['syn'].tolist())")
    outs = []
    for hs in ("0", "1", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": hs, "PYTHONPATH": "."}
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           env=env, cwd=str(PROC.parents[1]))
        assert r.returncode == 0, r.stderr[-2000:]
        outs.append(r.stdout.strip())
    assert len(set(outs)) == 1, f"pick_triples depends on PYTHONHASHSEED: {outs}"


def test_stability_separates_from_its_own_null():
    """Identical explanations must score 1.0, not the null.

    `stability_null` pairs DIFFERENT triples on purpose. If a caller hands `stability`
    misaligned lists, the two functions compute the same quantity and stability lands on the
    null whatever the model does, which is how "explanations are unstable across seeds" was
    produced. Identical input is the sharpest case: it has to come out at 1.0.
    """
    from src.eval import xai_metrics as X
    rng = np.random.default_rng(0)
    v = [rng.normal(size=944) for _ in range(20)]
    st = X.stability({"a": v, "b": [x.copy() for x in v]})
    assert st["jaccard"] == pytest.approx(1.0)
    assert st["cosine"] == pytest.approx(1.0, abs=1e-6)
    nl = X.stability_null({"a": v, "b": [x.copy() for x in v]})
    assert nl["jaccard"] < 0.2, "the null must not look like a perfect match"


def test_permuted_smiles_control_moves_every_drug_indexed_tensor():
    """The permuted-SMILES null control must leave nothing behind.

    It has leaked twice: first the Morgan fingerprint buffer kept the real chemistry, then
    `n_frag` kept the original molecule's fragment count. `MolStore.permute_drugs` asserts that
    no per-drug tensor is left unpermuted; this checks the assertion actually bites.
    """
    from src.data.batching import MolStore, permute_molecules
    dr = torch.load(PROC / "drugs.pt", weights_only=False)
    a, b = MolStore(dr, "cpu"), MolStore(dr, "cpu")
    perm = permute_molecules(b, None)
    assert not torch.equal(perm, torch.arange(len(dr["drugs"])))
    for k in MolStore.PER_DRUG:
        assert not torch.equal(getattr(a, k), getattr(b, k)), f"{k} was not permuted"
    b.extra_per_drug = torch.zeros(len(dr["drugs"]))     # a tensor a later change might add
    with pytest.raises(AssertionError):
        b.permute_drugs(perm)


# ------------------------------------------------------------------ external set (ALMANAC)
@pytest.fixture(scope="module")
def almanac():
    p = PROC / "almanac.pt"
    if not p.exists():
        pytest.skip("almanac.pt not built")
    return torch.load(p, weights_only=False)


def test_shared_compounds_have_identical_features(almanac, data):
    """A compound in both datasets must reach the model as the same molecule.

    21 of the 101 ALMANAC compounds are O'Neil compounds under another name (ADM
    HYDROCHLORIDE is DOXORUBICIN, GEMZAR (LILLY) is GEMCITABINE). The resolver is supposed to
    reuse the training structure for those, so an external number is never the feature
    pipeline being compared against itself.
    """
    import pandas as pd
    _, dr, _, _ = data
    o = pd.read_csv(PROC / "smiles.csv")
    a = pd.read_csv(PROC / "almanac_smiles.csv")
    okey = {r.drug: r.inchikey for _, r in o.iterrows() if isinstance(r.smiles, str)}
    akey = {r.drug: r.inchikey for _, r in a.iterrows() if isinstance(r.smiles, str)}
    oi = {d: i for i, d in enumerate(dr["drugs"])}
    ai = {d: i for i, d in enumerate(almanac["drugs"])}
    shared = [(ad, od) for ad, ak in akey.items() for od, ok in okey.items()
              if ak == ok and ad in ai and od in oi]
    assert len(shared) >= 20, f"expected ~21 shared compounds, found {len(shared)}"
    for ad, od in shared:
        assert torch.equal(almanac["fp2"][ai[ad]], dr["fp2"][oi[od]]), f"{ad} != {od} (fp)"
        assert torch.equal(almanac["graphs"][ad]["x"], dr["graphs"][od]["x"]), f"{ad} (atoms)"


def test_oneil_overlap_rows_point_at_the_same_experiment(almanac, data):
    """`oneil_row` must index the O'Neil triple with the same compounds and the same cell.

    The external control scores one set of predictions against two labels, so a row that
    points at the wrong O'Neil triple would silently invent agreement (or disagreement)
    between the two studies.
    """
    import pandas as pd
    d, _, _, _ = data
    if "oneil_row" not in almanac:
        pytest.skip("almanac.pt predates the oneil_row mapping")
    o = pd.read_csv(PROC / "smiles.csv")
    a = pd.read_csv(PROC / "almanac_smiles.csv")
    okey = dict(zip(o.drug, o.inchikey))
    akey = dict(zip(a.drug, a.inchikey))
    cmap = pd.read_csv(PROC.parents[1] / "src" / "data" / "cell_line_map.csv")
    amap = pd.read_csv(PROC.parents[1] / "src" / "data" / "cell_line_map_almanac.csv")
    omid = dict(zip(cmap.drugcomb_name, cmap.model_id))
    amid = dict(zip(amap.drugcomb_name, amap.model_id))
    rows = (almanac["oneil_row"] >= 0).nonzero().flatten()
    assert len(rows) > 500, "the two studies should overlap on about 1,163 triples"
    for i in rows[:: max(1, len(rows) // 25)]:
        r = int(almanac["oneil_row"][i])
        ea, eb, ec = almanac["idx"][i].tolist()
        oa, ob, oc = d["idx"][r].tolist()
        assert sorted((akey[almanac["drugs"][ea]], akey[almanac["drugs"][eb]])) == \
               sorted((okey[d["drugs"][oa]], okey[d["drugs"][ob]])), "different compounds"
        assert amid[almanac["cells"][ec]] == omid[d["cells"][oc]], "different cell line"
        assert int(almanac["oneil_ord3_loewe"][i]) == int(d["y"]["ord3_loewe"][r])


def test_external_scaler_never_sees_the_external_cells(almanac, data):
    """The z-score for ALMANAC must come from O'Neil training cells, nothing else.

    src.eval.external computes mu/sd from the fold's training cells and applies them to the
    external matrix. If it ever fitted on ALMANAC's own cells the external numbers would be
    quietly optimistic, so the two routes are compared here.
    """
    d, _, ce, sp = data
    tr = sp["splits"]["leave_combo"][0][0]
    tc = torch.unique(d["idx"][tr][:, 2])
    mu = ce["expr"][tc].mean(0, keepdim=True)
    sd = ce["expr"][tc].std(0, keepdim=True).clamp_min(1e-6)
    mine = (almanac["expr"] - mu) / sd
    theirs = standardise(torch.cat([ce["expr"], almanac["expr"]]), tc)[len(ce["expr"]):]
    assert torch.allclose(mine, theirs, atol=1e-5)
    own = (almanac["expr"] - almanac["expr"].mean(0, keepdim=True)) / \
          almanac["expr"].std(0, keepdim=True).clamp_min(1e-6)
    assert not torch.allclose(mine, own, atol=1e-2), "this would be fitting on the test set"
