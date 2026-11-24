"""Masks and attribution operators for SynGT  (planner 6.1, 6.2).

Three explanation units, all implemented as a soft mask inside the forward pass so the same
code gives both gradients (Integrated Gradients) and deletions (Fidelity):

  atoms      mu_atom (N_atoms,)   one weight per atom of the batched pair
  fragments  mu_frag (n_frag,)    BRICS fragments; expanded to atoms before use. Deleting a
                                  whole fragment keeps a chemically meaningful substructure,
                                  which deleting single atoms does not (planner 6.1)
  genes      mu_gene (G,)         one weight per landmark gene token
  fp         mu_fp (2,)           the Morgan-fingerprint branch of drug A and drug B. The
                                  fragment masks cannot reach it, so `fragfp` attributes
                                  over fragments AND the two fingerprints on ONE path: their
                                  attributions share one completeness budget, which is what
                                  makes "share of the decision carried by the fingerprint"
                                  a well-defined number

Three attribution targets (planner 6.2):
  logit      z_syn                       what the literature attributes
  contrast   z_syn - z_add = delta_syn    the interaction level this thesis proposes
  ant        z_ant - z_add                antagonism, only askable in a 3-class setting
"""
import torch

TARGETS = ("logit", "contrast", "ant")


def target_scalar(model, logits, which):
    z = model.class_logits(logits)
    if which == "logit":
        return z[:, 2]
    if which == "contrast":
        return z[:, 2] - z[:, 1]
    if which == "ant":
        return z[:, 0] - z[:, 1]
    raise ValueError(which)


def frag_to_atom(mu_frag, frag_ids, frag_offset):
    """mu over fragments -> mu over atoms, for a batched pair graph."""
    return mu_frag[frag_ids + frag_offset]


def fragment_layout(batch, store):
    """Global fragment ids for a batched collate: returns (atom->frag index, n_frag_total)."""
    nf = store.n_frag[batch["mols"]]
    off = torch.cumsum(nf, 0) - nf
    atom_off = torch.repeat_interleave(off, batch["n_atoms_per_mol"])
    return batch["frag"] + atom_off, int(nf.sum()), nf, off


def forward_with(model, batch, mu_atom=None, mu_gene=None, mu_fp=None):
    return model(batch, mu_atom=mu_atom, mu_gene=mu_gene, mu_fp=mu_fp)


def has_fp(model):
    return getattr(model, "drug_fp", None) is not None


# ----------------------------------------------------------------- Integrated Gradients
def ig(model, batch, which, unit="gene", steps=32, power=1, store=None):
    """IG of `which` w.r.t. the mask of `unit`, path mu(alpha) = alpha**power from 0 to 1.

    Returns (attr, f1, f0, gap) where gap = sum(attr) - (f(1) - f(0)) is the completeness
    error - reported, never hidden: a large gap means the attribution is not trustworthy.
    """
    dev = batch["expr"].device
    if unit == "gene":
        n = batch["expr"].shape[1]
    elif unit == "atom":
        n = batch["x"].shape[0]
    elif unit == "fp":
        n = 2
    else:                                                # frag, or fragfp = frags + 2 fps
        fa, n, _, _ = fragment_layout(batch, store)
        nfr = n
        if unit == "fragfp":
            n = nfr + 2

    def f(mu):
        if unit == "gene":
            return target_scalar(model, forward_with(model, batch, mu_gene=mu), which)
        if unit == "atom":
            return target_scalar(model, forward_with(model, batch, mu_atom=mu), which)
        if unit == "fp":
            return target_scalar(model, forward_with(model, batch, mu_fp=mu), which)
        if unit == "fragfp":
            return target_scalar(model, forward_with(model, batch, mu_atom=mu[:nfr][fa],
                                                     mu_fp=mu[nfr:]), which)
        return target_scalar(model, forward_with(model, batch, mu_atom=mu[fa]), which)

    one, zero = torch.ones(n, device=dev), torch.zeros(n, device=dev)
    with torch.no_grad():
        f1, f0 = f(one).sum().item(), f(zero).sum().item()

    total = torch.zeros(n, device=dev)
    for k in range(steps):
        t = (k + 0.5) / steps
        a = t ** power
        w = power * t ** (power - 1) if power > 1 else 1.0
        mu = (one * a).requires_grad_(True)
        out = f(mu).sum()
        g, = torch.autograd.grad(out, mu)
        total += g.detach() * w / steps
    attr = total * 1.0                                   # mu goes 0 -> 1, so x - x' = 1
    return attr.detach(), f1, f0, float(attr.sum().item() - (f1 - f0))


# ------------------------------------------------- exact second-order fragment interaction
def fragment_interaction(model, batch, store, which="contrast"):
    """phi(i,j) = f(all) - f(-i) - f(-j) + f(-i,-j) for fragment i of A and j of B.

    An exact finite difference on the masking operator, not an approximation: molecules have
    1-13 BRICS fragments here, so the whole matrix costs ~200 forward passes per triple.
    phi > 0 means removing BOTH hurts the synergy score more than the sum of removing each,
    i.e. the two fragments act together - the pair-level mechanism the thesis is after.
    """
    fa, nf_total, nf, off = fragment_layout(batch, store)
    dev = batch["expr"].device
    na, nb = int(nf[0]), int(nf[1])                      # batch must hold ONE pair
    base = torch.ones(nf_total, device=dev)

    def f(mu):
        with torch.no_grad():
            return float(target_scalar(model, forward_with(model, batch, mu_atom=mu[fa]), which))

    f_all = f(base)
    fi = []
    for i in range(na):
        m = base.clone(); m[off[0] + i] = 0
        fi.append(f(m))
    fj = []
    for j in range(nb):
        m = base.clone(); m[off[1] + j] = 0
        fj.append(f(m))
    phi = torch.zeros(na, nb)
    for i in range(na):
        for j in range(nb):
            m = base.clone(); m[off[0] + i] = 0; m[off[1] + j] = 0
            phi[i, j] = f_all - fi[i] - fj[j] + f(m)
    return phi, f_all, torch.tensor(fi), torch.tensor(fj)


# --------------------------------------------------------------------------- deletions
def delete_topk(model, batch, attr, k, unit, store=None, keep=False):
    """f after switching off (or keeping only) the top-k entries of `attr`."""
    dev = batch["expr"].device
    n = attr.shape[0]
    k = max(1, min(int(k), n))
    top = torch.topk(attr, k).indices
    mu = torch.ones(n, device=dev) if not keep else torch.zeros(n, device=dev)
    mu[top] = 0.0 if not keep else 1.0
    if unit == "gene":
        return forward_with(model, batch, mu_gene=mu)
    if unit == "atom":
        return forward_with(model, batch, mu_atom=mu)
    fa, _, _, _ = fragment_layout(batch, store)
    return forward_with(model, batch, mu_atom=mu[fa])


def delete_random(model, batch, k, unit, rng, store=None, keep=False, match_size=None):
    """Null for Fidelity: same number of units (optionally size-matched for fragments)."""
    dev = batch["expr"].device
    if unit == "gene":
        n = batch["expr"].shape[1]
    elif unit == "atom":
        n = batch["x"].shape[0]
    else:
        _, n, _, _ = fragment_layout(batch, store)
    k = max(1, min(int(k), n))
    pick = torch.tensor(rng.choice(n, k, replace=False), device=dev)
    attr = torch.zeros(n, device=dev)
    attr[pick] = 1.0
    return delete_topk(model, batch, attr, k, unit, store, keep)


# ------------------------------------------------- graph vs fingerprint: who carries it?
def graph_vs_fp(model, batch, store, which="contrast", steps=32):
    """How much of the decision runs through the molecular graph vs the fingerprint branch.

    Two independent readings, so neither has to be trusted alone:
      ig share   joint IG over [fragments, fp_A, fp_B]: sum|a_fp| / (sum|a_frag| + sum|a_fp|)
      deletion   f(all) - f(fp off)   vs   f(all) - f(every fragment off, fp kept)
    """
    fa, nfr, _, _ = fragment_layout(batch, store)
    attr, f1, f0, gap = ig(model, batch, which, "fragfp", steps=steps, store=store)
    a_fr, a_fp = attr[:nfr].abs().sum().item(), attr[nfr:].abs().sum().item()
    dev = batch["expr"].device
    with torch.no_grad():
        full = float(target_scalar(model, forward_with(model, batch), which))
        no_fp = float(target_scalar(model, forward_with(
            model, batch, mu_fp=torch.zeros(2, device=dev)), which))
        no_graph = float(target_scalar(model, forward_with(
            model, batch, mu_atom=torch.zeros(batch["x"].shape[0], device=dev)), which))
    return {"ig_share_fp": a_fp / max(a_fr + a_fp, 1e-12), "ig_gap": gap, "f1": f1, "f0": f0,
            "attr_fp": attr[nfr:].cpu(), "del_fp": full - no_fp, "del_graph": full - no_graph}
