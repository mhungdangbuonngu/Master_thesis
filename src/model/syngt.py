"""SynGT: molecular GNN + two transformers for 3-class drug synergy  (planner 5.1).

Follows DTSyn's two-granularity design, with three deliberate changes (planner 5.1):
  * GIN instead of a 2-layer GCN on the molecule graph (GCN kept as an ablation)
  * no A/B type embedding anywhere, so f(A,B,c) = f(B,A,c) holds BY CONSTRUCTION
    (DTSyn only checks empirically that drug order does not matter)
  * a CORN ordinal head over ant < add < syn instead of a binary output

    fine transformer   : [CLS_f | atoms of A | atoms of B | gene tokens]
    coarse transformer : [CLS_c | pooled A | pooled B | pooled cell]
    head               : MLP([CLS_f ; CLS_c]) -> 2 cumulative logits (or 3 / 1 for ablations)

Attention is computed with fused SDPA during training (no T x T matrix is materialised, so
978 gene tokens fit), and with an explicit softmax only when `need_weights=True`, which the
XAI code uses at batch size 1. No torch_geometric: message passing is gather/index_add.
"""
import torch
import torch.nn.functional as F
from torch import nn

from src.model.corn import CornHead


# --------------------------------------------------------------------------- graph encoder
def gin_propagate(x, edge_index):
    """sum over neighbours; edge_index holds both directions already."""
    src, dst = edge_index
    out = torch.zeros_like(x)
    return out.index_add_(0, dst, x[src])


def gcn_propagate(x, edge_index, n):
    """symmetric-normalised neighbour mean with self loops (the DTSyn ablation).

    The degree normalisation is computed in fp32 and cast back to x's dtype: under bf16
    autocast rsqrt returns fp32, and index_add_ rejects a dtype mismatch between self and
    source ("self (BFloat16) and source (Float) must have the same scalar type").
    """
    src, dst = edge_index
    loop = torch.arange(n, device=x.device)
    row = torch.cat([src, loop])
    col = torch.cat([dst, loop])
    deg = torch.zeros(n, device=x.device, dtype=torch.float32).index_add_(
        0, row, torch.ones(row.shape[0], device=x.device))
    w = (deg[row].rsqrt() * deg[col].rsqrt()).to(x.dtype)
    out = torch.zeros_like(x)
    return out.index_add_(0, row, x[col] * w[:, None])


class MolEncoder(nn.Module):
    def __init__(self, d_in=78, d=128, layers=3, kind="gin", dropout=0.1):
        super().__init__()
        self.kind, self.layers = kind, layers
        self.inp = nn.Linear(d_in, d)
        self.mlps = nn.ModuleList([nn.Sequential(nn.Linear(d, 2 * d), nn.ReLU(),
                                                 nn.Linear(2 * d, d)) for _ in range(layers)])
        self.norms = nn.ModuleList([nn.LayerNorm(d) for _ in range(layers)])
        self.eps = nn.Parameter(torch.zeros(layers))
        self.drop = nn.Dropout(dropout)

    def forward(self, x, edge_index, mask=None):
        """x (N_atoms, d_in) of a batched graph; returns (N_atoms, d)."""
        h = self.inp(x)
        n = h.shape[0]
        for i in range(self.layers):
            if self.kind == "gin":
                m = gin_propagate(h, edge_index)
                h2 = self.mlps[i]((1 + self.eps[i]) * h + m)
            else:
                h2 = self.mlps[i](gcn_propagate(h, edge_index, n))
            h = self.norms[i](h + self.drop(F.relu(h2)))      # residual keeps atom identity
        return h


# ------------------------------------------------------------------------------ transformer
class Attention(nn.Module):
    def __init__(self, d, heads, dropout):
        super().__init__()
        self.h, self.dk = heads, d // heads
        self.qkv = nn.Linear(d, 3 * d)
        self.out = nn.Linear(d, d)
        self.p = dropout

    def forward(self, x, pad_mask=None, need_weights=False):
        b, t, d = x.shape
        q, k, v = self.qkv(x).chunk(3, -1)
        q, k, v = [z.view(b, t, self.h, self.dk).transpose(1, 2) for z in (q, k, v)]
        bias = None
        if pad_mask is not None:                              # True = keep
            bias = torch.zeros(b, 1, 1, t, device=x.device, dtype=q.dtype)
            bias = bias.masked_fill(~pad_mask[:, None, None, :], float("-inf"))
        if need_weights:
            a = (q @ k.transpose(-2, -1)) / self.dk ** 0.5
            if bias is not None:
                a = a + bias
            w = a.softmax(-1)
            o = w @ v
        else:                                                 # fused: no (t,t) tensor in memory
            o = F.scaled_dot_product_attention(q, k, v, attn_mask=bias,
                                               dropout_p=self.p if self.training else 0.0)
            w = None
        o = o.transpose(1, 2).reshape(b, t, d)
        return self.out(o), w


class Block(nn.Module):
    def __init__(self, d, heads, ff, dropout, att_dropout=None):
        super().__init__()
        self.n1, self.n2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.att = Attention(d, heads, dropout if att_dropout is None else att_dropout)
        self.ff = nn.Sequential(nn.Linear(d, ff), nn.ReLU(), nn.Dropout(dropout), nn.Linear(ff, d))
        self.drop = nn.Dropout(dropout)

    def forward(self, x, pad_mask=None, need_weights=False):
        a, w = self.att(self.n1(x), pad_mask, need_weights)
        x = x + self.drop(a)
        x = x + self.drop(self.ff(self.n2(x)))
        return x, w


# ------------------------------------------------------------------------------------ model
class SynGT(nn.Module):
    """head: 'corn' (2 cumulative logits), 'nominal' (3), 'binary' (1)."""

    def __init__(self, gene_emb, atom_dim=78, d=128, gnn_layers=3, gnn="gin",
                 fine_layers=2, coarse_layers=2, heads=4, ff=256, dropout=0.3,
                 head="corn", use_fine=True, use_coarse=True, use_gene_emb=True,
                 readout="cls", att_dropout=None, head_hidden=(512, 128), drug_fp=None):
        super().__init__()
        self.d, self.head_kind = d, head
        self.readout = readout
        # chemistry prior: a Morgan-fingerprint MLP added to each pooled drug vector. Fragment
        # masks do not reach this branch, so it gets its own mask `mu_fp` and the XAI reports
        # how much of each decision comes from the graph and how much from the fingerprint
        # (planner 6.1, "fingerprint unit").
        if drug_fp is not None:
            self.register_buffer("drug_fp", drug_fp.float())
            self.fp_mlp = nn.Sequential(nn.Linear(drug_fp.shape[1], 256), nn.ReLU(),
                                        nn.Dropout(dropout), nn.Linear(256, d))
        else:
            self.drug_fp = None
        self.use_fine, self.use_coarse = use_fine, use_coarse
        self.register_buffer("gene_emb", gene_emb)            # (G, d_emb) node2vec, frozen
        g, de = gene_emb.shape
        self.n_genes = g
        self.use_gene_emb = use_gene_emb

        self.mol = MolEncoder(atom_dim, d, gnn_layers, gnn, dropout)
        self.gene_in = nn.Linear(de + 1 if use_gene_emb else 1, d)
        self.cell_mlp = nn.Sequential(nn.Linear(g, 512), nn.ReLU(), nn.Dropout(dropout),
                                      nn.Linear(512, 256), nn.ReLU(), nn.Linear(256, d))
        # type embeddings: atoms of A and B share one type -> exact symmetry in A <-> B
        self.type_fine = nn.Embedding(3, d)                   # 0 cls, 1 atom, 2 gene
        self.type_coarse = nn.Embedding(3, d)                 # 0 cls, 1 drug, 2 cell
        self.cls_f = nn.Parameter(torch.zeros(1, 1, d))
        self.cls_c = nn.Parameter(torch.zeros(1, 1, d))
        self.fine = nn.ModuleList([Block(d, heads, ff, dropout, att_dropout)
                                   for _ in range(fine_layers)])
        self.coarse = nn.ModuleList([Block(d, heads, ff, dropout, att_dropout)
                                     for _ in range(coarse_layers)])
        n_out = {"corn": 2, "nominal": 3, "binary": 1}[head]
        # readout "skip": the CLS tokens PLUS DeepDDS's symmetric pair/cell vector
        # [pA + pB ; |pA - pB| ; cell], so the head never has to route everything through
        # attention (see planner 5.1, "readout"). Both extra terms are symmetric in A <-> B.
        d_cat = d * (int(use_fine) + int(use_coarse) + (3 if readout == "skip" else 0))
        h1, h2 = head_hidden
        self.mlp = nn.Sequential(nn.LayerNorm(d_cat), nn.Linear(d_cat, h1), nn.ReLU(),
                                 nn.Dropout(dropout), nn.Linear(h1, h2), nn.ReLU(),
                                 nn.Dropout(dropout if h1 > 512 else 0.0))
        self.out = CornHead(h2, 3) if head == "corn" else nn.Linear(h2, n_out)
        nn.init.trunc_normal_(self.cls_f, std=0.02)
        nn.init.trunc_normal_(self.cls_c, std=0.02)

    # ---- atom tokens for a batch of molecule pairs
    def atom_tokens(self, batch, mu=None):
        """batch: dict from collate(); mu: optional (N_atoms,) soft mask for XAI."""
        h = self.mol(batch["x"], batch["edge_index"])
        if mu is not None:
            h = h * mu[:, None]
        b, amax = batch["n_mol"], batch["atom_max"]
        tok = h.new_zeros(b, amax, self.d)
        tok[batch["mol_batch"], batch["atom_pos"]] = h
        mask = torch.zeros(b, amax, dtype=torch.bool, device=h.device)
        mask[batch["mol_batch"], batch["atom_pos"]] = True
        return tok, mask, h

    def gene_tokens(self, expr, mu=None):
        """expr (B, G) standardised expression -> (B, G, d)."""
        b, g = expr.shape
        if self.use_gene_emb:
            e = self.gene_emb[None].expand(b, g, -1)
            z = torch.cat([e, expr[..., None]], -1)
        else:
            z = expr[..., None]
        t = self.gene_in(z)
        if mu is not None:
            t = t * mu[:, :, None] if mu.dim() == 2 else t * mu[None, :, None]
        return t

    def forward(self, batch, mu_atom=None, mu_gene=None, mu_fp=None, need_weights=False):
        """mu_fp: (B, 2) or (2,) weight on the fingerprint branch of drug A / drug B."""
        expr = batch["expr"]
        b = expr.shape[0]
        # mu_gene switches a gene off everywhere, not only in the fine transformer. Expression
        # is z-scored, so mu = 0 sets a gene to the training mean - exactly the IG baseline
        # XGDP recommends (mean expression, not zero).
        if mu_gene is not None:
            expr = expr * (mu_gene if mu_gene.dim() == 2 else mu_gene[None, :])
        at, amask, _ = self.atom_tokens(batch, mu_atom)
        a_n = at.shape[1]
        # pooled per-drug vectors (mean over that molecule's atoms)
        pooled = at.sum(1) / amask.sum(1, keepdim=True).clamp_min(1)
        pa, pb = pooled[0::2], pooled[1::2]                   # molecules come in pairs (A, B)
        if self.drug_fp is not None:
            t = batch["trip"]
            fa_, fb_ = self.fp_mlp(self.drug_fp[t[:, 0]]), self.fp_mlp(self.drug_fp[t[:, 1]])
            if mu_fp is not None:
                m = mu_fp if mu_fp.dim() == 2 else mu_fp[None].expand(b, 2)
                fa_, fb_ = fa_ * m[:, 0:1], fb_ * m[:, 1:2]
            pa, pb = pa + fa_, pb + fb_

        wf = None
        if self.use_fine:
            atoms = torch.cat([at[0::2], at[1::2]], 1)        # (B, 2*amax, d)
            am = torch.cat([amask[0::2], amask[1::2]], 1)
            gt = self.gene_tokens(expr, mu_gene)
            x = torch.cat([self.cls_f.expand(b, 1, -1), atoms, gt], 1)
            types = torch.cat([
                torch.zeros(1, dtype=torch.long, device=x.device),
                torch.ones(atoms.shape[1], dtype=torch.long, device=x.device),
                torch.full((gt.shape[1],), 2, dtype=torch.long, device=x.device)])
            x = x + self.type_fine(types)[None]
            pad = torch.cat([torch.ones(b, 1, dtype=torch.bool, device=x.device), am,
                             torch.ones(b, gt.shape[1], dtype=torch.bool, device=x.device)], 1)
            wf = []
            for blk in self.fine:
                x, w = blk(x, pad, need_weights)
                if w is not None:
                    wf.append(w)
            cls_f = x[:, 0]
            self.last_atom_slice = (1, 1 + atoms.shape[1])
            self.last_gene_slice = (1 + atoms.shape[1], x.shape[1])
        else:
            cls_f = None

        wc = None
        if self.use_coarse:
            cell = self.cell_mlp(expr)
            x2 = torch.stack([self.cls_c.expand(b, 1, -1)[:, 0], pa, pb, cell], 1)
            t2 = torch.tensor([0, 1, 1, 2], device=x2.device)   # A and B share type -> symmetric
            x2 = x2 + self.type_coarse(t2)[None]
            wc = []
            for blk in self.coarse:
                x2, w = blk(x2, None, need_weights)
                if w is not None:
                    wc.append(w)
            cls_c = x2[:, 0]
        else:
            cls_c = None

        parts = [p for p in (cls_f, cls_c) if p is not None]
        if self.readout == "skip":
            parts += [pa + pb, (pa - pb).abs(), self.cell_mlp(expr)]
        h = self.mlp(torch.cat(parts, -1))
        logits = self.out(h)
        if need_weights:
            return logits, {"fine": wf, "coarse": wc}
        return logits

    # ---- scalars used by the XAI code (planner 6.2)
    def class_logits(self, logits):
        if self.head_kind == "corn":
            return CornHead.class_logits(logits)
        return logits

    def contrast(self, logits, which="syn"):
        """delta_syn = z_syn - z_add ; delta_ant = z_ant - z_add."""
        z = self.class_logits(logits)
        return z[:, 2] - z[:, 1] if which == "syn" else z[:, 0] - z[:, 1]
