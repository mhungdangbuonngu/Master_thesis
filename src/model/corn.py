"""Ordinal head and losses for ant < add < syn  (planner 5.1, 5.2; RQ2).

CORN (Cao, Mirjalili, Raschka 2022) turns K ordered classes into K-1 CONDITIONAL binary
tasks, task k trained only on samples with y >= k:
    q0 = P(y > ant)                       trained on every sample
    q1 = P(y > add | y > ant)              trained on samples with y > ant
Cumulative probabilities chain, so they can never cross:
    P(y > ant) = q0 ,  P(y > add) = q0 * q1   <=  P(y > ant)
Class probabilities:
    P(ant) = 1 - q0 ,  P(add) = q0 - q0*q1 ,  P(syn) = q0*q1
Rank consistency is structural, so the model cannot output P(y>add) > P(y>ant), which a
plain 3-way softmax can effectively do.

For attribution (planner 6.2) a "logit" per class is needed. We use z_c = log P(c), so
    delta_syn = z_syn - z_add = log P(syn) - log P(add) = log( q1 / (1 - q1) )  = the second
cumulative logit. The contrast attribution is therefore an attribution on one scalar that
the network computes directly, which is cheaper and less noisy than a difference of two
softmax logits.
"""
import torch
import torch.nn.functional as F
from torch import nn

ANT, ADD, SYN = 0, 1, 2
EPS = 1e-7


class CornHead(nn.Module):
    """K-1 = 2 cumulative logits."""

    def __init__(self, d_in, n_classes=3):
        super().__init__()
        self.fc = nn.Linear(d_in, n_classes - 1)
        self.n_classes = n_classes

    def forward(self, h):
        return self.fc(h)                                    # (B, 2) conditional logits

    @staticmethod
    def probs(logits):
        q = torch.sigmoid(logits)                            # (B, 2)
        cum = torch.cumprod(q, dim=1)                        # P(y>ant), P(y>add)
        p_ant = 1 - cum[:, 0]
        p_add = cum[:, 0] - cum[:, 1]
        p_syn = cum[:, 1]
        return torch.stack([p_ant, p_add, p_syn], 1).clamp_min(EPS)

    @staticmethod
    def class_logits(logits):
        """z_c = log P(c), computed with log-sigmoid so it never saturates.

        log P(ant) = logsig(-l0)
        log P(add) = logsig(l0) + logsig(-l1)
        log P(syn) = logsig(l0) + logsig(l1)
        so z_syn - z_add = logsig(l1) - logsig(-l1) = l1 EXACTLY, for any l.

        An earlier version took log(probs()), whose clamp at 1e-7 flattened log P(syn) for
        confidently antagonistic triples: the gradient vanished and the contrast came out as
        -4.1 instead of l1 = -9 (logits [-12, -9]). Every attribution of the logit / contrast
        targets on such triples was wrong, which showed up as broken IG completeness.
        """
        l0, l1 = logits[:, 0], logits[:, 1]
        ls = F.logsigmoid
        return torch.stack([ls(-l0), ls(l0) + ls(-l1), ls(l0) + ls(l1)], 1)


def corn_loss(logits, y, weight=None):
    """Conditional BCE: task k only on samples with y >= k (Cao et al. 2022)."""
    loss, n = 0.0, 0
    for k in range(logits.shape[1]):
        m = y >= k
        if m.sum() == 0:
            continue
        t = (y[m] > k).float()
        w = None if weight is None else weight[y[m]]
        loss = loss + F.binary_cross_entropy_with_logits(logits[m, k], t, weight=w, reduction="sum")
        n += int(m.sum())
    return loss / max(n, 1)


def corn_loss_smooth(logits, y, weight=None, soft=None):
    """CORN with SOFT conditional targets for boundary triples (planner 3.3).

    A triple scoring 9.8 and one scoring 10.2 get opposite hard labels although the assay
    barely separates them. `soft` holds, per sample and per conditional task k, the target
    probability sigmoid((score - threshold_k) / tau), so a triple far from the threshold keeps
    a target of essentially 1 or 0 and only the boundary band is softened. This fits CORN
    exactly, because each task k already predicts a probability, P(y > k).

    The sample MASK is unchanged (task k still trains only on y >= k), so the only difference
    from `corn_loss` is the target value - which keeps the two runs comparable.
    """
    if soft is None:
        return corn_loss(logits, y, weight)
    loss, n = 0.0, 0
    for k in range(logits.shape[1]):
        m = y >= k
        if m.sum() == 0:
            continue
        w = None if weight is None else weight[y[m]]
        loss = loss + F.binary_cross_entropy_with_logits(logits[m, k], soft[m, k], weight=w,
                                                         reduction="sum")
        n += int(m.sum())
    return loss / max(n, 1)


def soft_targets(score, thresholds, tau=5.0):
    """sigmoid((score - t_k) / tau) for each ordinal threshold t_k -> (N, K-1).

    tau is in score units: tau = 5 means a triple 5 points past the threshold already has a
    target of 0.73, and one 15 points past it has 0.95.
    """
    t = torch.as_tensor(thresholds, dtype=score.dtype, device=score.device)
    return torch.sigmoid((score[:, None] - t[None, :]) / tau)


def nominal_loss(logits, y, weight=None):
    """Plain 3-way cross-entropy: the ablation that ignores the ordering."""
    return F.cross_entropy(logits, y, weight=weight)


# Cost matrix ablation: penalise a polar confusion (syn <-> ant) four times an adjacent one.
COST = torch.tensor([[0.0, 1.0, 4.0],
                     [1.0, 0.0, 1.0],
                     [4.0, 1.0, 0.0]])


def cost_loss(logits, y, weight=None, lam=1.0):
    """Cross-entropy + lam * expected cost: the middle ground between CE and ordinal.

    Expected cost alone is NOT used: its minimiser on this data is "always predict additive"
    (the middle class has the lowest expected cost under any confusion), and a first run of
    it collapsed to exactly that (QWK 0.000 on all 6 runs, kept in runs_v1_cls/cost_collapsed/). Adding CE
    keeps the likelihood signal; the cost term then only reshapes which errors are cheap.
    """
    p = logits.softmax(1)
    c = COST.to(logits.device)[y]                            # (B, 3) cost of each prediction
    per = (p * c).sum(1)
    if weight is not None:
        per = per * weight[y]
    return F.cross_entropy(logits, y, weight=weight) + lam * per.mean()
