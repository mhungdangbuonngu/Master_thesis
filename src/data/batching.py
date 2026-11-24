"""Vectorised batching of molecule pairs (no torch_geometric).

All 36 molecules are stored once as flat atom/edge arrays on the device. A batch of triples
is turned into one batched graph with ragged gathers, so there is no Python loop per sample.
Molecules are laid out as [A_0, B_0, A_1, B_1, ...], which is why SynGT reads drug A from
`pooled[0::2]` and drug B from `pooled[1::2]`.
"""
import torch


def ragged_index(starts, counts):
    """Flat indices of count[i] consecutive items beginning at starts[i], concatenated."""
    total = int(counts.sum())
    if total == 0:
        return torch.zeros(0, dtype=torch.long, device=starts.device)
    off = torch.cumsum(counts, 0) - counts                      # exclusive cumsum
    pos = torch.arange(total, device=starts.device) - torch.repeat_interleave(off, counts)
    return torch.repeat_interleave(starts, counts) + pos


class MolStore:
    """Flat storage of every drug's graph, plus BRICS fragment ids."""

    def __init__(self, drugs_pt, device):
        self.drugs = drugs_pt["drugs"]
        xs, eis, frs, na, ne, nf = [], [], [], [], [], []
        for d in self.drugs:
            g = drugs_pt["graphs"][d]
            xs.append(g["x"])
            eis.append(g["edge_index"])
            frs.append(g["frag"])
            na.append(g["x"].shape[0])
            ne.append(g["edge_index"].shape[1])
            nf.append(g["n_frag"])
        self.x = torch.cat(xs).to(device)
        self.e = torch.cat(eis, 1).to(device)
        self.frag = torch.cat(frs).to(device)
        self.na = torch.tensor(na, device=device)
        self.ne = torch.tensor(ne, device=device)
        self.n_frag = torch.tensor(nf, device=device)
        self.a_start = torch.cumsum(self.na, 0) - self.na
        self.e_start = torch.cumsum(self.ne, 0) - self.ne
        self.atom_max_single = int(self.na.max())
        self.device = device

    # Tensors with exactly one entry per drug. The permuted-SMILES control has to move ALL of
    # them together; `frag` and `x` are per-atom and `e` per-edge, so they stay put.
    PER_DRUG = ("na", "ne", "n_frag", "a_start", "e_start")

    def permute_drugs(self, perm):
        """Give drug i the molecule of drug perm[i], keeping i as its identity index.

        The assertion exists because this control has already leaked twice by forgetting a
        drug-indexed tensor: the first version permuted only (a_start, na, e_start, ne), which
        left `n_frag` pointing at the original molecule's fragment count, so the XAI fragment
        masks would have read the wrong number of fragments for a permuted run. A per-drug
        tensor added to MolStore later will now fail loudly here instead of leaking silently.
        """
        n = len(self.drugs)
        for k in self.PER_DRUG:
            v = getattr(self, k)
            setattr(self, k, v[perm.to(v.device)])
        missed = [k for k, v in vars(self).items() if torch.is_tensor(v)
                  and v.dim() == 1 and v.shape[0] == n and k not in self.PER_DRUG]
        assert not missed, f"per-drug tensors left unpermuted: {missed}"

    def collate(self, trip, expr):
        """trip (B, 3) long [drug_a, drug_b, cell]; expr (B, G). Returns the batch dict."""
        b = trip.shape[0]
        mols = torch.stack([trip[:, 0], trip[:, 1]], 1).reshape(-1)     # A0,B0,A1,B1,...
        na = self.na[mols]
        ai = ragged_index(self.a_start[mols], na)
        x = self.x[ai]
        frag = self.frag[ai]

        mol_batch = torch.repeat_interleave(torch.arange(2 * b, device=trip.device), na)
        off = torch.cumsum(na, 0) - na
        atom_pos = torch.arange(int(na.sum()), device=trip.device) - torch.repeat_interleave(off, na)

        ne = self.ne[mols]
        ei_local = self.e[:, ragged_index(self.e_start[mols], ne)]
        ei = ei_local + torch.repeat_interleave(off, ne)[None, :]

        return {"x": x, "edge_index": ei, "mol_batch": mol_batch, "atom_pos": atom_pos,
                "n_mol": 2 * b, "atom_max": int(na.max()), "expr": expr, "frag": frag,
                "mols": mols, "n_atoms_per_mol": na, "trip": trip}


PERM_SEED = 1234


def permute_molecules(store, model=None, seed=PERM_SEED):
    """The permuted-SMILES null control: identity kept, chemistry destroyed.

    A drug's index, and so everything the model can memorise about that drug, is unchanged;
    the molecule behind the index becomes another drug's. Both the graph store and the Morgan
    fingerprint buffer go through this one function on purpose. The first version of the
    control permuted only the graphs, so `drug_fp` still looked up the real fingerprint by the
    original index: the "no chemistry" control still had chemistry, and its QWK was not a null.

    Pass model=None when the weights come from a checkpoint. `drug_fp` is a persistent buffer,
    so it is restored already permuted by load_state_dict and must not be permuted twice.
    """
    perm = torch.randperm(len(store.drugs), generator=torch.Generator().manual_seed(seed))
    store.permute_drugs(perm)
    if model is not None and getattr(model, "drug_fp", None) is not None:
        model.drug_fp = model.drug_fp[perm.to(model.drug_fp.device)]
    return perm
