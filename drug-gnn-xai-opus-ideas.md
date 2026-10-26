# Ideation report: drug_synergy_xai

Human state of the art: Interpretable graph deep learning framework for drug synergy prediction by integrating functional and clinical similarities (DSimSynergy), Lai et al., npj Digital Medicine 2026

6 seed ideas (ranked by novelty, 1-10) and 8 limitations. No code has been written or run.

## Contents

- [S1 · novelty 6 · PathKNN-Syn: retrieval-augmented synergy prediction with a learned, pathway-factorised cell kernel and exemplar-level explanations](#s1)
- [S2 · novelty 6 · PathX-Comp: a crosstalk tensor over KEGG pathways that scores how two drugs' targeted pathways complement each other in a given cell line, added as a built-in interpretable synergy term in DSimSynergy](#s2)
- [S3 · novelty 6 · DoseCurve-Syn: a learned dose-space non-additivity operator. Synergy is computed as a second-order finite difference of cell-gated pathway response modules driven by each drug's targets.](#s3)
- [S4 · novelty 6 · FlipPath-Syn: matched-counterfactual training with a sparsemax pathway-gated cell encoder and minimal pathway-swap counterfactual explanations](#s4)
- [S5 · novelty 5 · SLink-Syn: a synthetic-lethality coupling term over cell-specific network-propagated target footprints, giving gene-pair attributions for drug synergy](#s5)
- [S0 · novelty 4.5 · SymTri-Rank: symmetric, cell-conditioned trilinear interaction head trained with magnitude-aware ranking, plus interaction-decomposed attributions for DSimSynergy](#s0)
- [Limitations of the human state of the art](#limitations)

<a id="s1"></a>
## S1 · novelty 6 · PathKNN-Syn: retrieval-augmented synergy prediction with a learned, pathway-factorised cell kernel and exemplar-level explanations

_Add a differentiable retrieval branch to DSimSynergy. For each query, it looks up labelled training triplets: the same drug pair in other cell lines, and each drug with other partners in the same cell line. The pair's cell lines are weighted by a learned kernel that sums per-KEGG-pathway expression distances with weights that depend on the drug pair; the partners are weighted by learned (also dissimilarity-seeking) attention over drug embeddings. The prediction comes with built-in exemplar and pathway attributions that can be checked by deletion._

### Motivation

On the random triplet split, the most informative evidence for a test triplet (a,b,c) is how the same pair behaved in other cell lines and how a and b behaved with other partners in c. DSimSynergy can only use this evidence implicitly, by memorising it in MLP weights from concatenated features (L2). That is data-hungry for the 3% positive class and gives no case-based explanation. Its cell encoder is one FC layer that ignores pathway structure and the drugs being combined. Its KEGG explanations are post-hoc SHAP–expression correlations taken from a different (regression) model (L4, L5). The similarity-network GCN assumes homophily, which is weakly supported (PCC 0.21–0.23) and contradicts the authors' own "pathway complementarity" mechanism (L7). The classifier also never sees Loewe magnitudes (L8). A retrieval branch addresses these directly. (i) It turns sparse positive labels into a non-parametric prior that sharpens the top of the ranking, which is what AUPR rewards. (ii) Its kernel on cell lines is factorised over KEGG pathways with weights that depend on the drug pair, so 'which pathways make cell line c' behave like c for this pair' is part of the forward computation, not a post-hoc correlation. (iii) Its partner kernel is learned and signed, so it can favour complementary rather than similar partners. (iv) It aggregates neighbours' continuous Loewe scores as evidence while keeping the binary labels unchanged. Every component is symmetric in (a,b), so retrieval evidence and its attributions do not depend on drug order (L3).

### Method

Notation: the training fold T contains (a,b,c,y,s), with y∈{0,1} and s the Loewe score. Mirrored copies of a triplet are treated as the same triplet. Only the current CV training fold is ever written to memory. Validation and held-out test triplets are only queried and never stored.

1) Pathway expression views. For each KEGG pathway p with at least 5 L1000 genes (about 250 pathways; gene sets from MSigDB C2:KEGG), x_c^p is the vector of z-scored log2(TPM+1) expression of the L1000 genes in p for cell line c. Precompute the per-pathway distance d_p(c,c') = ||x_c^p − x_{c'}^p||² / |p| as an 83×83×P tensor, once.

2) Pair-conditioned pathway kernel (same-pair memory). Let e_a and e_b be the DSimSynergy drug embeddings (concatenation of BP-GCN, ATC-GCN and GAT outputs, projected to 64 dimensions). Form the order-invariant pair code q_ab = [e_a+e_b, e_a⊙e_b]. Pathway weights are w_p(a,b) = softplus(u_p + v_pᵀ q_ab), with an L1 penalty λ_w·Σ_p w_p and λ_w = 1e-4 so that few pathways are active. The distance is D_ab(c,c') = Σ_p w_p(a,b)·d_p(c,c'). The memory is M_pair = {(a,b,c',y',s') ∈ T : c' ≠ c}. The attention is α_{c'} = softmax_{c'}(−D_ab(c,c')/τ), with τ learnable and initialised at 1.

3) Signed partner kernel (same-cell memory). M_a = {(a,b',c,y',s') ∈ T : b' ≠ b}, and M_b is defined symmetrically. The attention is β_{b'} = softmax_{b'}(h(e_b,e_{b'}, cell c)), where h = MLP([e_b⊙e_{b'}, |e_b−e_{b'}|, cell_emb_c]) → scalar. Because the input includes |e_b−e_{b'}| and there is no sign constraint, the model can learn to retrieve complementary partners rather than only similar ones (heterophily, L7). At eval time all partners are used. At train time at most K=64 partners are sampled per drug–cell.

4) Evidence summaries. For each memory m ∈ {pair, a, b}, compute the smoothed positive rate π_m = (Σ attn·y' + α0·π̄)/(Σ attn·n_eff + α0)·… In practice, use weighted counts n_m = N_m·Σ attn (N_m is the memory size), k_m = N_m·Σ attn·y', and π_m = (k_m + α0 π̄)/(n_m + α0), with α0 = 2 and π̄ the class prior. Also compute the magnitude evidence μ_m = Σ attn·clip(s',−50,100)/50 and the support σ_m = log1p(N_m). Evidence logit: r_m = logit(π_m). Merge the a- and b-memories symmetrically: r_drug = (r_a + r_b)/2, μ_drug = (μ_a + μ_b)/2.

5) Fusion. z = z_param(a,b,c) + Σ_{m∈{pair,drug}} γ_m(σ_m)·r_m + δᵀ[μ_pair, μ_drug]. Here z_param is the unchanged DSimSynergy classifier logit, made order-invariant by averaging its two orderings, and γ_m(σ) = softplus(g0_m + g1_m·σ), so evidence is trusted more when support is larger. The output is p = sigmoid(z). The loss is the paper's class-weighted CE (unchanged), the decision threshold is 0.5, and the checkpoint is chosen by validation F1, as in the protocol.

6) Leakage and train/test consistency. During training the query triplet and its mirror are always excluded from their own memories (leave-self-out). In addition, a random 20% of each memory is masked out (memory dropout), so the model does not over-trust evidence that is denser than what a held-out triplet will see. Val and test triplets query the training-fold memory only. The test split is never used, neither as memory nor for tuning.

7) Built-in explanations, exact by construction for the retrieval term. (a) Exemplar attribution: the contribution of each retrieved training triplet to z, computed as ∂z/∂y' times its attention mass; reported as 'pair X was synergistic (Loewe 42) in cell line Y, weight 0.31'. (b) Pathway attribution: w_p(a,b)·d_p contributions to the kernel, giving drug-pair-specific KEGG pathways that the classifier actually uses. (c) Partner attribution: β over b', which shows complementary or similar partner drugs, i.e. neighbour-level explanations on the similarity network. SHAP over genes and the GAT atom analysis are still run on the same classifier, not a separate regression model.

8) Faithfulness protocol. Deletion curves: remove the top-k exemplars (by attribution) from the memory, or zero the top-k pathway weights, then re-predict. Report the drop in p and in test AUPR versus random deletion of the same number of exemplars or pathways, k ∈ {1,3,5,10}. Run a randomised-weight sanity check.

Defaults: embedding dim 64, P≈250 pathways, K=64 sampled partners, memory dropout 0.2, α0=2, τ init 1, λ_w=1e-4, Adam lr 1e-4 (the retrieval head may use 1e-3), batch 512, 50 epochs on the subset.

### Addresses limitations

L2, L3, L4, L5, L7, L8

### Novelty claim

Published synergy predictors (DeepSynergy, DeepDDS, AttenSynergy, HyperGraphSynergy, JointSyn, DSimSynergy) are purely parametric, and exemplar or kNN baselines use fixed similarity. This idea is a differentiable, leakage-safe retrieval-augmented synergy classifier with two new ingredients: (1) a cell-line kernel that is factorised over KEGG pathways and conditioned on the drug pair, so the pathway explanation is part of the model's mechanism rather than a post-hoc SHAP–ORA summary; (2) a signed, cell-conditioned partner-retrieval kernel that can learn complementarity instead of similarity homophily. Its explanations are case-based (training exemplars with Loewe values), pathway-based and neighbour-based at once, and can be tested by deletion. It differs from S0, which changes the parametric fusion head and the loss; here the mechanism is non-parametric evidence retrieval with learned biological kernels, and the classifier, loss and threshold are left untouched.

### Implementation plan

1) data_utils: after the fixed test split and fold split, build per-fold index structures from the training fold only. These are dict pair_key(min(a,b),max(a,b)) → tensors (cell_idx, y, s), and dict (drug,cell) → tensors (partner_idx, y, s). Mirror rows are deduplicated by pair_key. Provide a collate function that gathers padded memory tensors (same-pair ≤83 entries; partners capped at K=64 when training, full at eval) with masks, and that removes the query itself plus 20% memory dropout during training.
2) pathway_prep.py: download the KEGG gene sets (MSigDB C2 KEGG GMT), intersect them with the 949 L1000 genes, keep pathways with ≥5 genes, and precompute the d_p tensor [83,83,P] as a .pt file.
3) model.py: add a RetrievalHead module that takes the drug embeddings (existing GCN/GAT outputs, linear-projected to 64), the cell embeddings, the d_p tensor and the memory batch, and returns r_pair, r_drug, μ's, γ's and attention maps. In forward, compute z_param for both orderings and average them, then add the retrieval terms as in Method step 5.
4) train.py: unchanged loss, lr, batch, checkpointing and threshold. Add the λ_w L1 term. Add flags --no_retrieval, --uniform_kernel (w_p constant, no conditioning) and --raw_expr_kernel (cosine on all 949 genes) for ablations.
5) explain.py: exemplar, pathway and partner attribution export; deletion/insertion faithfulness curves versus random; randomised-weight sanity check; and the existing SHAP over genes, run on the classifier.
Compute: the memory gather is O(batch×(83+2K)), negligible on the A100. Expected screening run on fold 1 at 50 epochs: <1 h.

### Expected effect

Under the random triplet split, same-pair-in-other-cells evidence is highly predictive, because synergy labels for a pair are strongly correlated across cell lines. A learned pathway kernel should pick out the cell lines that matter, which mostly raises the scores of true positives at the top of the ranking. Expected effect on the full benchmark: AUPR from 0.77 to about 0.80–0.83, F1 from 0.74 to about 0.76–0.79 (the evidence logit is well-calibrated around the prior, so 0.5 becomes a better operating point), AUROC 0.96 to about 0.97, ACC ≈0.98 (unchanged or slightly higher). Fold-to-fold variance should be lower thanks to order-invariance. Expected ablation ordering: no retrieval < uniform kernel < raw-expression kernel < pathway kernel conditioned on the drug pair. Faithfulness: deleting the top-5 exemplars or pathways should reduce p substantially more than random deletion.

### Risks

(1) Over-reliance on memory: the model may lean on retrieval and ignore drug/cell features, which would hurt pairs with little memory support and generalisation to DrugOut/CellOut. Monitor AUPR stratified by memory support. Mitigation: memory dropout and a support-dependent γ; fall back to z_param when memory is empty. (2) Train/test mismatch: if training memory is effectively denser than test memory despite leave-self-out, training would show over-confident fits and validation F1 lower than training F1. Mitigation: tune the memory dropout rate on the validation fold only. (3) Diffuse pathway weights: the pathway weights may stay spread out, so explanations are uninformative even though AUPR rises. Mitigation: raise λ_w, or replace softplus with sparsemax normalisation. (4) Gene-set coverage: few L1000 genes per KEGG pathway may make some d_p noisy. Mitigation: use pathways with ≥5 genes and optionally add GO-BP slim sets. (5) Leakage bugs: memory construction must use only training-fold rows. Assert that no test or validation pair_key+cell combination appears in memory; a mistake would show up as implausibly high validation scores.

### Novelty check

I found no paper that proposes a differentiable, leakage-safe retrieval branch for a GNN synergy classifier. Such a branch would draw on two memories: the same pair in other cell lines, and each drug with other partners in the same cell line. It would use a pathway-factorised cell kernel conditioned on the drug pair, a signed (complementarity-capable) partner kernel, support-gated evidence fusion, and exemplar and pathway attributions checked by deletion.

Each ingredient does have a clear precedent:
- **Using labelled synergy triplets as context or memory:** SynerGPT does in-context learning over known synergy examples, with context selection and a kNN baseline over triplet embeddings.
- **Retrieval-augmented, case-based prediction with exemplar explanations:** this exists for the closely related DDI task (CBR-DDI), and as LLM-RAG synergy models.
- **Pathway-induced learned kernel weights for interpretable similarity:** PIMKL does this.
- **The core motivation:** the 'One-hot news' study already shows that synergy models mainly exploit label co-variation across cell lines and pairs, which is what the retrieval branch makes explicit.

The contribution is therefore a non-trivial, well-engineered combination and adaptation of known ideas (retrieval augmentation, kNN or attention over labelled neighbours, pathway multiple-kernel learning) applied to this benchmark. It is not a fundamentally new mechanism. The parts with the least precedent are the pathway kernel conditioned on the drug pair, the signed partner retrieval, and the deletion-based faithfulness protocol for exemplar explanations in synergy prediction.

One caveat on the expected gains: because existing models already exploit label co-variation, the AUPR improvement on the random triplet split may be modest.

I only found RADDI (retrieval-augmented DDI) in a search summary, without a link, so it is not listed as a reference.

Closest prior work found:

- SynerGPT: In-Context Learning for Personalized Drug Synergy Prediction and Drug Design (2023) https://arxiv.org/abs/2307.11694: High conceptual overlap: this is the closest precedent. A transformer predicts synergy for a query triplet by conditioning on a set of known, labelled synergy triplets in the same cell-line context, which works like a learned retrieval memory, and it optimises which context examples to select. It also includes a kNN baseline over (drug1, drug2, cell) embeddings. It does not use a pathway-factorised, pair-conditioned cell kernel, a signed partner kernel, a fusion with a parametric GNN, or deletion-tested exemplar explanations.
- One-hot news: drug synergy models shortcut molecular features (bioRxiv 2025 / Bioinformatics) (2025) https://www.biorxiv.org/content/10.1101/2025.04.18.649584.full.pdf: Supports the motivation rather than the method. It shows that published synergy models mainly act as identifier lookups that exploit label co-variation across drugs and cell lines. This is the implicit memorisation that PathKNN-Syn would make explicit. It also means the AUPR gain from explicit retrieval on a random triplet split may be smaller than expected, because parametric models already capture much of this signal.

<a id="s2"></a>
## S2 · novelty 6 · PathX-Comp: a crosstalk tensor over KEGG pathways that scores how two drugs' targeted pathways complement each other in a given cell line, added as a built-in interpretable synergy term in DSimSynergy

_Map each drug's DrugBank targets onto KEGG pathways and read the cell line's pathway activity from L1000 expression. A symmetric pathway-pair crosstalk matrix, sparse and limited to pathways within 2 hops of each other, then scores how the two drugs' pathways complement each other in that cell. This score is added to the DSimSynergy logit, so the model gives exact pathway-pair attributions instead of explaining after the fact with SHAP and ORA._

### Motivation

Limitations addressed:
- **L7:** DSimSynergy's GCN smooths features towards similar drugs, but drug similarity correlates only weakly with synergy (PCC about 0.2).
- **L4 and L5:** the paper's own explanation, the "pathway complementarity network", is found after training. SHAP is correlated with expression, the genes with |PCC|>0.5 go into a KEGG ORA, and then a pathway-crosstalk network is inspected by hand. None of this is a mechanism inside the model, and none of it is tested for faithfulness.
- **L2:** synergy enters only through concatenation followed by an MLP. With about 3% positives, the MLP has to learn implicitly which pairs of drug targets and which cellular contexts interact, so the ranking of positives (AUPR) suffers.

The idea is to build the hypothesis the authors themselves propose directly into the model. Two drugs are synergistic when they hit distinct but connected pathways that are active in the cell line, and redundant (often antagonistic) when they hit the same pathway. We express this as an explicit, cell-modulated bilinear form over pathways. The inductive bias is strong and low in parameters, which helps the rare positive class. The prediction also breaks down exactly into pathway-pair contributions that can be tested by deletion.

### Method

**Inputs**, all precomputed with no label information:
- Drug–target binary matrix T (D×G), from the DrugBank data already used for the BP network.
- KEGG human pathway gene sets (MSigDB c2.cp.kegg, legacy and medicus), keeping pathways with at least 1 target among the 521 drugs and at least 3 of the 949 L1000 genes. This leaves P ≈ 150–250 pathways.
- Membership matrices: M (P×G) over all genes, and M_L (P×949) over the L1000 genes.
- A pathway graph Â (P×P): pathways p and q are linked if their gene-set Jaccard is above 0.05 or KEGG lists a map-to-map link. Â is symmetric-normalised.
- Hop masks: H0 = I, H1 = 1-hop, H2 = exactly 2-hop.

**1) Drug–pathway engagement.**
- Raw coverage: c_A = (M T_Aᵀ) / sqrt(|G_p|), then propagated to neighbouring pathways: c̃_A = (I + γÂ)c_A, with γ = 0.5.
- Engagement: e_A = softplus(w_e ⊙ c̃_A + V h_A), where h_A is the DSimSynergy drug embedding (BP-GCN ‖ ATC-GCN ‖ GAT), V is a P×dim matrix, and w_e is a learned per-pathway scale initialised to 1.
- An L1 penalty λ_V‖V‖₁ (λ_V = 1e-3) keeps engagement anchored to the known targets. V h_A can only add pathway engagement that the drug's features and similarity neighbours support.

**2) Cell pathway activity.**
- m_c = σ((W_m ⊙ M_L) x_c + b_m), where x_c is z-scored log2(TPM+1) L1000 expression.
- W_m is a learnable gene-in-pathway weight matrix masked to membership, initialised to 1/|G_p∩L1000|, so it starts as a mean pathway score.

**3) Hop-structured crosstalk matrix.**
- K = Σ_{k=0..2} H_k ⊙ (S_k + S_kᵀ)/2. The S_k are learnable P×P matrices whose entries exist only on hop-k edges, so the parameter count is about the number of edges (a few thousand).
- Initialisation: the diagonal (k=0) starts at −0.1, the redundancy prior; the k=1 and k=2 entries start at +0.05, the complementarity prior. All signs are free to change.
- An L1 penalty λ_K‖K‖₁ (λ_K = 1e-4) keeps K sparse.

**4) Complementarity logit**, symmetric in A and B by construction:
- s(A,B,c) = Σ_{p,q} (e_A ⊙ m_c)_p K_pq (e_B ⊙ m_c)_q = ẽ_Aᵀ K ẽ_B.
- Pathway dropout of 0.1 is applied to ẽ during training.

**5) Final logit:** z = z_DSim(A,B,c) + β·s(A,B,c), with β a learnable scalar initialised to 1. z_DSim is the unchanged concat+MLP head (logit of the synergistic class).
- Loss: the paper's class-weighted cross-entropy, plus λ_K‖K‖₁ + λ_V‖V‖₁.
- Optimiser and splits as in the paper: Adam lr 1e-4, batch 512, checkpoint chosen by validation F1, same splits.

**6) Explanations.** These are exact for the complementarity branch:
- Each pathway pair gets a contribution φ_pq = β ẽ_A,p K_pq ẽ_B,q, and these sum to the branch logit.
- Pathway-level attribution: φ_p = Σ_q (φ_pq + φ_qp)/2.
- Gene-level attribution inside a pathway follows from the masked linear map, with exact gradient×input on W_m through σ.
- Global outputs: the learned K, which gives the signed crosstalk edges the model actually uses, and the cell-modulated pairs behind the top-ranked synergistic triplets.

**7) Faithfulness protocol** (classifier, held-out test set, reporting only):
- Deletion curves: mask the top-k pathway pairs by |φ| (set ẽ_p = 0 or K_pq = 0) and track the drop in predicted probability and in AUPR. Compare with random masking and with the same number of pathways chosen by baseline SHAP+ORA.
- Randomised-K sanity check.
- Branch share: Var(βs)/Var(z) across test triplets.

**Ablations that isolate the mechanism:**
- (a) Baseline.
- (b) Branch with K diagonal only, i.e. redundancy without crosstalk.
- (c) K dense and low-rank (r = 16) with no KEGG hop prior.
- (d) Without m_c, i.e. no cell context.
- (e) Gene-set labels shuffled across pathways.

**Default hyperparameters:** γ = 0.5, λ_K = 1e-4, λ_V = 1e-3, pathway dropout 0.1, β₀ = 1, P ≈ 200.

### Addresses limitations

L7, L4, L2, L5, L3

### Novelty claim

The new element is a learned, signed crosstalk matrix over pathway pairs, restricted to pathways within 2 hops on the KEGG pathway graph and modulated by the cell's pathway activity. It turns the post-hoc "pathway complementarity network" from DSimSynergy (and similar ORA-style explanations) into a symmetric scoring term inside the model whose explanations are exact. Prior work differs:
- Pathway-informed synergy models (e.g. DeepTraSynergy, pathway-based TranSynergy variants, EXPRESS/Janizek ensembles) use pathways as input features or as post-hoc summaries.
- Bilinear and trilinear heads, including candidate S0, interact in a latent space that has no biological meaning.
- Retrieval with a pathway kernel (S1) compares cell lines with each other. It does not model which pathway of drug A interacts with which pathway of drug B.

Here the interaction space itself is the KEGG basis, with a prior on redundancy (diagonal) versus complementarity (1–2 hops). The learned edges can be read directly as testable mechanistic hypotheses and are checked with deletion tests.

### Implementation plan

1. **Data prep (new script, e.g. Code/prep_pathways.py).**
   - Load the DrugBank targets already used to build the BP network, and the KEGG GMT from MSigDB (a local copy; vendor it if there is no internet).
   - Build T, M, M_L (aligned to the 949-gene order of the cell expression matrix), Â, and the hop masks H1 and H2 (as sparse edge-index lists).
   - Save everything as .npz. This uses no synergy labels.
2. **Model (the DSimSynergy model file).** Add a `PathComp` nn.Module containing:
   - registered buffers: c̃ (D×P, precomputed), M_L mask, and the edge lists;
   - parameters: w_e, V (Linear dim→P, no bias), W_m (as values on the masked entries, i.e. a sparse Linear), b_m, edge weights per hop, β;
   - forward(hA, hB, x_c, idxA, idxB): build dense K by scattering the edge weights into a P×P matrix and symmetrising, then return `s = einsum('bp,pq,bq->b', eA*m, K, eB*m)`.
   - In the main forward, reuse the drug embeddings already computed by the BP-GCN, ATC-GCN and GAT, and add β·s to the synergistic-class logit (for a 2-class CE output, add +βs/2 to class 1 and −βs/2 to class 0).
3. **Training script.**
   - Add the L1 penalties to the loss. Keep the splits (random_state 0 and 42), class weights, lr 1e-4, batch 512 and F1-based checkpointing unchanged.
   - Log β and the branch share.
   - Screening run: fold 1, 50 epochs. Full run: 5 folds, about 200 epochs each. The branch adds under 1M parameters and the P×P einsum is negligible compared with the GAT.
4. **Explain script (new, Code/explain_pathcomp.py).**
   - Compute φ_pq per test triplet, global |φ| rankings and the K edge list, saved as CSV for network plots.
   - Run the deletion/insertion curves against random masking and against the baseline's SHAP+ORA pathways, and the randomised-K check.
   - Keep the existing SHAP gene analysis, now run on the classifier itself.
5. **Ablation flags:** `--k_mode {hop,diag,lowrank}`, `--no_cell_mod`, `--shuffle_genesets`.

### Expected effect

**Held-out DrugCombDB test, averaged over 5 folds:**
- AUPR: 0.77 → about 0.79–0.81. The gain should be largest on synergistic pairs whose drugs have low BP/ATC similarity, i.e. those that rely on complementary pathways. We will report stratified AUPR by similarity quintile.
- F1: 0.74 → about 0.75–0.77.
- AUROC: 0.96 → about 0.96–0.97.
- ACC: about 0.98, unchanged.

**Fold-1 screening:** the branch should beat ablation (b) (diagonal only) and ablation (e) (shuffled gene sets) by at least 0.01 AUPR. That would show the gain comes from the crosstalk prior, not from extra parameters.

**Explainability:** removing the top 5% of pathway pairs should lower the predicted probability much more than random removal (target: at least 3× the drop). It should also beat a baseline SHAP+ORA pathway set of the same size. The learned K should recover known complementary axes, such as MAPK–PI3K-Akt and EGFR-TKI-resistance neighbours.

### Risks

- **The branch gets ignored.** On a random split, drug-identity memorisation by z_DSim dominates; this would show up as β→0, a branch share below 5%, and no AUPR change. Mitigations: warm up with the branch alone for 5 epochs, or apply dropout to z_DSim during early epochs.
- **Target coverage is sparse or noisy** in KEGG for some drugs (e.g. chemotherapies with DNA as the target). V h_A partly compensates, but explanations for these drugs will rest more on V; we report this share separately.
- **The KEGG GMT may not be available offline.** Fallback: GO-BP sets that are already on disk, clustered into about 200 modules.
- **K overfits**, giving unstable edges across folds. We check this with the overlap of edge rankings across folds and adjust λ_K if needed.
- **Gains are within fold variance.** The screening run might look positive or negative by chance, so we confirm with all 5 folds and paired tests against the ablations.
- **Partly faithful explanations.** Pathway attributions are exact only for the branch. If most of the logit comes from z_DSim, the explanation covers only part of the decision; the branch-share metric makes this visible.

### Novelty check

The biological hypothesis is not new. Drugs hitting distinct but connected pathways are synergistic, while hitting the same pathway is redundant. Chen et al. 2016 already used this rule in a pathway–pathway interaction network for synergy prediction, SynPathy found it with pathway proximity, and DIPx used pathway activation scores built from target interactions. Pathway-informed deep models (TranSynergy, SynPathy, PathSynergy) use pathways as inputs or as post-hoc explanations. Bilinear heads (e.g. the low-rank attention plus bilinear predictor model) are standard but work in latent space.

I found no paper that puts a learned, signed, sparse pathway×pathway crosstalk matrix inside a synergy GNN. The idea's version restricts the matrix to KEGG 0/1/2-hop edges with a redundancy or complementarity prior, gates it by the cell line's learned pathway activity, adds it as a logit term, and decomposes it exactly into pathway-pair contributions that are tested by deletion. Searches for a learnable pathway-pathway interaction matrix, pathway-level cross-attention between drug A and drug B, and a pathway crosstalk tensor for synergy all came back without a direct match. Taken together, this is a non-trivial adaptation that turns a known network-pharmacology heuristic into a structured, interpretable bilinear head. It is not a fundamentally new mechanism: the parts are known (bilinear forms, masked graph-structured parameters, pathway activity scores, deletion-based faithfulness tests), and the combination and its faithfulness framing are the contribution. Hence 6.

Caveat: I can't rule out very recent 2025–2026 preprints with pathway-pair attention, but none came up in several phrasings of the search.

Closest prior work found:

- Synergy evaluation by a pathway–pathway interaction network: a new way to predict drug combination (2016) https://pubs.rsc.org/en/content/articlelanding/2016/mb/c5mb00599j: Closest conceptual precedent. It scores drug pairs by mapping each drug's targets to pathways and using a pathway–pathway interaction network, and it states that redundant and complementary rules matter (same pathway through different targets; few, highly connected pathways). The scoring is fixed and network-based: there is no learned signed crosstalk matrix, no modulation by the cell line and no deep model. The idea's core hypothesis is therefore not new.
- SynPathy: Predicting Drug Synergy through Drug-Associated Pathways Using Deep Learning (2022) https://aacrjournals.org/mcr/article/20/5/762/694641/SynPathy-Predicting-Drug-Synergy-through-Drug: A deep model that uses drug-target-to-pathway enrichment scores and cell features as inputs. Its finding that synergy goes up when the two drugs' top pathways are close on the PPI network is the same complementarity hypothesis. But pathways are only input features and are interpreted after the fact. There is no explicit learned bilinear pathway-pair term.

<a id="s3"></a>
## S3 · novelty 6 · DoseCurve-Syn: a learned dose-space non-additivity operator. Synergy is computed as a second-order finite difference of cell-gated pathway response modules driven by each drug's targets.

_Each drug is mapped to a nonnegative "pathway-inhibition dose" vector (DrugBank targets → KEGG/GO pathways, propagated over 1–2 pathway hops, plus a sparse learned residual from the DSimSynergy embeddings). The doses go through cell-gated response modules of two kinds: convex threshold modules ("bypass/AND" modules, which can only produce synergy) and concave saturating modules ("redundancy" modules, which can only produce antagonism). Their mixed finite difference F(uA+uB) − F(uA) − F(uB) + F(0) is added to the DSimSynergy logit. The result is symmetric by construction and has a Loewe-like interaction inductive bias. Its attributions are exact module/pathway/target decompositions, checked with deletion tests._

### Motivation

Synergy (Loewe > 10) means the combined effect deviates from what the two single-agent effects add up to. DSimSynergy never represents that deviation. It concatenates per-drug embeddings with a cell embedding and asks an MLP to discover the interaction implicitly, which is data-hungry when only ~3% of triplets are positive (L2). Its output depends on drug order and is symmetrised only by augmentation (L3). Drug targets never meet the expression of the cell line being treated, and the pathway explanations are post-hoc SHAP–expression correlations followed by ORA (L4). Those explanations come from a different model (the regressor) and are never tested for faithfulness (L5). The GCN also smooths drugs toward similar drugs, even though the authors' own mechanistic finding is that synergy comes from complementary pathways 1–2 hops apart (L7).
The existing candidates handle interaction with a generic trilinear form (S0), nearest-neighbour exemplars (S1), or a learned pathway-pair crosstalk matrix (S2). None of them has the defining structure of synergy: one shared, saturating, cell-specific response function evaluated at single doses and at the combined dose, with synergy read off as the curvature (mixed second difference) of that function. In such an operator, an additive drug pair gives exactly zero interaction. The sign of the interaction is set mechanically: needing both drugs to cross a threshold gives synergy, while hitting an already-saturated module gives antagonism. This is a strong, low-parameter prior on the rare positive class. Because the logit is an explicit sum of module terms, the explanations come straight from the computation and are not reconstructed afterwards.

### Method

Notation. Genes G = L1000 (949) ∪ all DrugBank target genes of the 521 drugs. Pathways k=1..K: KEGG human gene sets (~186). If KEGG is unavailable, use the GO-BP sets already used for the BP network, filtered to size 15–300 and to the top K=300 by target coverage. Membership matrix M ∈ {0,1}^{K×|G|}, row-normalised to M̃. Pathway graph A_P: Jaccard overlap of the gene sets, top-10 neighbours per pathway, symmetric-normalised.

1) Cell pathway state. x_c is the z-scored log2(TPM+1) expression (missing target genes are set to 0 and given a learned per-gene bias). Pathway activity a_c = M̃_{L1000} x_c ∈ R^K. Cell context z_c = LeakyReLU(W_z[a_c ; h_c]), where h_c is the existing FCNN cell embedding (d=64).

2) Drug dose vectors (nonnegative, cell-gated).
- Target prior: p⁰_A = M̃ t_A, with t_A ∈ {0,1}^{|G|} the DrugBank targets.
- Propagation to model complementarity at a distance: p_A = p⁰_A + α₁ A_P p⁰_A + α₂ A_P² p⁰_A, with α = softplus(learned), initialised to 0.5 and 0.25.
- Learned residual for missing or off-target effects: r_A = ReLU(W_r e_A), where e_A is the concatenated DSimSynergy drug embedding (BP-GCN ‖ ATC-GCN ‖ GAT). An L1 penalty λ_r = 1e-3 keeps it sparse.
- Drug potency: s_A = softplus(w_s·e_A + b_s).
- Cell vulnerability gate: g_c = 2σ(W_g z_c) ∈ (0,2)^K, which says how much inhibiting each pathway matters in cell c, read from that cell's expression.
- Dose: u_A^c = s_A · g_c ⊙ (p_A + r_A) ∈ R^K_{≥0}.
- Combination: concentration addition in pathway space, u_{AB}^c = u_A^c + u_B^c. This is symmetric by construction.

3) Response modules (m=1..M, M=64; half of each type). Module input y_m(u) = Σ_k W⁺_{mk} u_k, with W⁺ = softplus(Ŵ) and an L1 penalty λ_W = 1e-4 so each module uses a sparse set of pathways.
- Convex "bypass/AND" modules: h_m(y) = τ·softplus((y − θ_m)/τ), with τ=0.5 and θ_m learnable (init 1.0). Their effect becomes large only when the combined dose crosses the threshold, i.e. when both drugs are needed to shut down redundant routes.
- Concave "redundancy/saturation" modules: h_m(y) = κ_m(1 − exp(−y/κ_m)), with κ_m learnable (init 1.0).
- Interaction of module m: Δ_m(A,B,c) = h_m(y_m(u_A+u_B)) − h_m(y_m(u_A)) − h_m(y_m(u_B)) + h_m(0). Because the inputs are nonnegative, Δ_m ≥ 0 for convex modules and Δ_m ≤ 0 for concave ones. The sign is fixed by the module type, so no sign is learned.
- Cell-specific module weight: ω_{c,m} = softplus(V z_c + b_V)_m ≥ 0.

4) Logit. ℓ(A,B,c) = ½[f(A,B,c) + f(B,A,c)] + β · Σ_m ω_{c,m} Δ_m + b.
- f is the unchanged DSimSynergy concat-MLP head. Averaging over both drug orders makes it symmetric, and it carries the main effects of each drug in each cell.
- β ≥ 0 is learnable, initialised to 1.
- Mechanism dropout: with probability 0.3 per batch the f term is dropped from the logit, i.e. the loss is computed on β·ΣωΔ + b + ½(main-effect-only head) with the pair-specific part of f zeroed. In practice, f is replaced by f_main(A,c) + f_main(B,c), a small MLP on [e_d ; h_c]. This forces the mechanistic branch to carry pair-specific information instead of being bypassed.

5) Loss. Class-weighted BCE, as in the benchmark, plus λ_r‖r‖₁ + λ_W‖W⁺‖₁. No other loss changes are made, so any gain can be attributed to the operator.
- Optional calibration, reported as a separate ablation row: one scalar logit offset fitted on the validation fold only, maximising validation F1.

6) Built-in attributions (exact, computed for the classifier itself).
- Module level: the logit contribution of module m is β ω_{c,m} Δ_m. These sum exactly to the mechanistic part of the logit.
- Pathway and drug level: for each module, h is a 1-D function of y. The exact path decomposition along the straight line from 0 to y gives each pathway a share of Δ_m from W⁺_{mk}(u_{A,k}+u_{B,k}), split by the share of drug A versus drug B. Pathway shares are then mapped back to individual target genes through M̃ t_A and the hop terms. This yields "drug A's target EGFR (ErbB pathway) and drug B's target PIK3CA (PI3K-Akt) jointly push bypass module 17 past its threshold in cell c".
- Cell level: ∂ω/∂x_c and g_c identify the expression genes that make the module or pathway decisive in that cell. Unlike the paper's procedure, no correlation-plus-ORA step is needed.
- Substructure level: SHAP or GAT attributions on f are kept, so the paper's atom-level analysis still works.

7) Faithfulness protocol, reported on the held-out test set.
- Deletion curves: zero the top-k modules/pathways (k = 1, 3, 5, 10) and compare with random-k masking, measuring the drop in predicted probability and in AUPR.
- Target knock-out counterfactuals: remove a single target from t_A.
- Sanity check: re-randomise W⁺ and V and confirm the attributions change.
- Order consistency: attributions for (A,B) and (B,A) must be identical (exact here, by construction).

Defaults: Adam lr 1e-4 (benchmark), batch 512, K≈186 (KEGG) or 300, M=64, τ=0.5, 2 hops, mechanism dropout 0.3, λ_r=1e-3, λ_W=1e-4. Checkpoint chosen by validation F1 per the protocol. The extra compute is about 4 evaluations of a K×M layer per triplet, which is negligible.

### Addresses limitations

L2, L3, L4, L5, L7, L1

### Novelty claim

As far as we know, no published deep synergy predictor builds the classification logit from a mixed second-order finite difference, F(uA+uB) − F(uA) − F(uB) + F(0), of a shared cell-conditioned response function over a pathway-dose space grounded in drug targets. In this operator the curvature type of each module (convex threshold vs. concave saturation) fixes the sign of the interaction. This turns two ideas into a differentiable, trainable inductive bias: the defining structure of reference-model synergy (deviation from dose additivity), and the paper's own post-hoc "pathway complementarity network" hypothesis (via 1–2 hop propagation and AND-type bypass modules).

This differs from the existing candidates in the following ways:
- S0: there is no free trilinear interaction tensor. Interaction exists only through the curvature of the response.
- S1: there is no retrieval.
- S2: no pairwise pathway×pathway parameters are learned. Pair effects emerge from shared module nonlinearities, so parameters grow as K·M rather than K².
- DeepSynergy, DeepDDS, JointSyn and HyperGraphSynergy all use concatenation or attention fusion.
- Mechanistic models (e.g. Boolean/ODE signalling simulations) are not trained end-to-end on HTS synergy data, and they do not provide exact additive attributions.

The explanations decompose the classifier's logit exactly, are order-invariant by construction, and are checked by deletion tests.

### Implementation plan

1) Data prep script (new, prep_pathway_dose.py). Load the DrugBank target table and GO-BP gene sets already used to build the BP similarity network (in Code/Data or the similarity-construction script). Load KEGG gene sets: an MSigDB c2.cp.kegg GMT file if present, otherwise the GO-BP fallback. Build and save:
- the gene universe G;
- M̃ (sparse);
- A_P (pathway top-10 Jaccard graph, normalised);
- the target matrix T ∈ {0,1}^{521×|G|};
- cell expression for G (from the DepMap 24Q4 matrix in the repo; target genes outside L1000 are taken from the full protein-coding matrix if present, otherwise masked).
Save everything as .pt files.

2) Model (new module pathway_dose.py, class DoseCurveHead). Parameters: hop weights α, W_r, w_s/b_s, W_z, W_g, Ŵ (M×K), θ, κ, V, β. forward(eA, eB, idxA, idxB, x_c, h_c) returns the mechanistic logit and a dict containing Δ_m, ω, uA, uB for attribution. Implement h(0) analytically. Use float32 and clamp θ and κ to be positive.

3) Modify the main DSimSynergy model class:
- expose the per-drug embedding e_d (BP-GCN ‖ ATC-GCN ‖ GAT outputs before concatenation);
- compute the existing head on both orders and average them;
- add the f_main MLP for mechanism dropout;
- add DoseCurveHead's output to the logit;
- add the L1 terms to the loss in the training loop.
Keep the class-weighted CE (written as a 2-logit CE [0, ℓ] so the existing code path stays the same).

4) Training script: no change to the splits (test split random_state 0, StratifiedKFold random_state 42). Add a flag --mech {on,off} and the mechanism-dropout rate. Fast screening uses fold 1 for 50 epochs. Ablations:
- (a) baseline;
- (b) symmetrised baseline only;
- (c) + DoseCurve without hops;
- (d) full;
- (e) convex-only and concave-only module variants;
- (f) + validation-only logit-offset calibration.

5) Explain script (new, explain_dosecurve.py):
- per-triplet module, pathway, target and drug decomposition;
- aggregated module→pathway tables per drug pair (e.g. Binimetinib–Brigatinib, for comparison with the paper);
- deletion/insertion curves vs random masking;
- target knock-out counterfactuals;
- weight-randomisation sanity check;
- SHAP on f, kept for gene and atom analysis to stay continuous with the paper.

6) Full benchmark: 5 folds at about 200–300 epochs each. This fits in under 50 GB, since the model is small.

### Expected effect

Internal test set, averaged over 5 folds:
- AUPR: from 0.77 to about 0.79–0.81. The non-additivity prior mainly helps rank rare positives where the two drugs are individually unremarkable but act on complementary pathways in that cell.
- F1: from 0.74 to about 0.76–0.78. The symmetrised head lowers variance, and the optional validation-only offset calibration adds another ~0.01–0.02 at the 0.5 rule.
- AUROC: about +0.005 (0.96 → ~0.965).
- ACC: unchanged at ~0.98, since it is saturated.

In the ablation, the full model is expected to beat the symmetrised baseline by at least +0.015 AUPR, and removing the hops or one module type to recover part of the gain.

Explainability: deletion of the top-3 attributed modules is expected to cut the mean predicted synergy probability of true positives far more than random-3 deletion (target: ≥3× larger drop). Attributions are exactly order-invariant. Pathway explanations now come from the classifier itself, so the paper's p53/PI3K-Akt/EGFR-TKI-resistance-style findings can be checked directly.

### Risks

1) The baseline head f absorbs all the signal and β shrinks, leaving the mechanistic branch decorative. Signs would be a low share of logit variance from ΣωΔ and ablation (c/d) ≈ (b). Mitigations: mechanism dropout, and reporting the variance share.
2) Sparse or incorrect DrugBank target annotations (or targets outside the expression matrix) make p⁰ uninformative. The learned residual r_A would then dominate, which weakens biological interpretability. Monitor ‖r‖/‖p‖.
3) Threshold modules with too-high θ give zero gradient. Watch for dead modules (Δ≡0); re-initialise θ from quantiles of y on the training set.
4) Mirror (B,A,c) triplets of test pairs present in training via the paper's augmentation are kept unchanged by the rules. Symmetrisation removes order noise but does not fix this, so absolute numbers stay comparable to the paper.
5) With only ~83 cell lines, the cell gates g_c and ω_c may overfit. This would appear as a larger train–validation gap. Mitigation: weight decay on W_g and V.
6) The gain may be small (<0.01 AUPR) on the random split, where memorising drug pairs already works well. In that case the main payoff would be faithful explanations and possibly better PairOut/DrugOut behaviour.

### Novelty check

The nearest precedent is ComboNet (Jin et al. 2020). It already evaluates one shared response function on each drug's target vector and on the combined target vector, and reads synergy off the deviation from an additive (Bliss) expectation, with target-level explanations. That formula is taken from a search snippet; the PDF could not be read. TranSynergy covers target profiles meeting cell expression, with pathway explanations from post-hoc SHAP gene-set analysis. DeepSynBa and DDoS build Loewe or dose-response structure into deep models. CPA adds drug embeddings in latent space. New elements found in no paper: concentration addition of pathway 'doses' propagated 1–2 hops over the pathway graph; the exact mixed second difference F(uA+uB)-F(uA)-F(uB)+F(0), which gives exactly zero for additive pairs; convex threshold modules that can only give synergy and concave saturating modules that can only give antagonism; cell-gated module weights; and an exact, order-invariant decomposition of the classifier's own logit, checked with deletion tests. Together this is a non-trivial combination and adaptation of known ideas, not a fully new mechanism. Score 6.

Closest prior work found:

- Discovering Synergistic Drug Combinations for COVID with Biological Bottleneck Models (ComboNet) (2020) https://arxiv.org/abs/2011.04651: High on the core mechanism. Drug-to-target module and target-to-disease module learned jointly with synergy; a 'Bliss layer' combines predicted target vectors, and synergy is the deviation from the expectation computed from single-drug predictions (formula from a search snippet, PDF not read). Target-level explanations. No pathway-dose space, cell gating, fixed-sign convex/concave modules, or exact attributions.
- TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations (2021) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/: Medium. Drug-target profiles spread over a protein interaction network meet cell-line expression for the same genes; pathway explanations come from post-hoc SHAP gene-set analysis (SA-GSEA). No non-additivity operator.

<a id="s4"></a>
## S4 · novelty 6 · FlipPath-Syn: matched-counterfactual training with a sparsemax pathway-gated cell encoder and minimal pathway-swap counterfactual explanations

_Train DSimSynergy against matched counterfactual training triplets: the same drug pair in another cell line with the opposite label, or the same cell line and one shared drug with a partner of the opposite label. Encode each cell line through KEGG pathway modules gated by a drug-pair-conditioned sparsemax, so pathways with a zero gate provably have no effect. Explain each prediction with the smallest set of pathways that, when swapped in from a matched antagonistic cell line, flips the classifier's decision._

### Motivation

On a random split, most drug pairs in DrugCombDB are tested in many cell lines. The hard positives are pairs that are synergistic in only a few of those cell lines, which is context-specific synergy. DSimSynergy's plain class-weighted CE over i.i.d. triplets (L1) lets the model fit pair-level base rates through its drug embeddings and leave the cell features underused. Its FC cell encoder (L4) has no pathway structure and ignores which drugs are being combined. Its KEGG explanations come from post-hoc SHAP–expression correlation followed by ORA, computed on a separate regression model (L5), and their faithfulness is never tested. FlipPath-Syn addresses this in three ways.
(i) A matched-counterfactual contrastive loss compares each triplet with labelled training triplets that differ in exactly one factor, either the cell line or one partner drug, and have the opposite label. The model can only reduce this loss by learning which cell or partner differences flip synergy. That is the ranking information AUPR rewards among pairs whose drugs are individually common (L1, L2).
(ii) A pathway-factorised cell encoder whose pathway gates depend on the drug pair (symmetric in A and B) gives a target-aware inductive bias suited to only 83 cell lines (L4, L3).
(iii) Sparsemax gates are exactly zero for unselected pathways, so swapping their genes between cell lines provably cannot change the logit. Explanations are interventional by construction. Counterfactual "flip sets" are computed on the classifier itself and come with a built-in deletion/insertion faithfulness test (L5).

### Method

Backbone: keep DSimSynergy's drug branches (BP-GCN, ATC-GCN, GAT+GMP over MACCS and molecular graphs), giving d_A and d_B in R^D. Replace the 949→d' FC cell encoder and make the pair representation symmetric.

1) Pathway modules. Map the 949 L1000 genes to KEGG pathways and keep those with ≥5 member genes (expected P≈180–220). Add one extra module, "unannotated", for genes that belong to no kept pathway. For each pathway p, a small per-pathway MLP e_p: R^{|G_p|}→R^8 (Linear-LeakyReLU-Linear) turns x_c[G_p] into a pathway-activity embedding u_p(c). All modules run in parallel as one block-sparse matmul with a gene→pathway mask.

2) Drug-pair-conditioned sparse gate. Define q_AB = MLP_q(d_A + d_B) ⊕ MLP_q(d_A ⊙ d_B), which is symmetric in A and B. Then g(A,B) = sparsemax( (Q q_AB) / τ ) ∈ Δ^P, with Q ∈ R^{P×h} and τ = 0.5. Add a target prior: the logit offset is β·log(1 + n_targets_p(A) + n_targets_p(B)), where n_targets_p counts the drug's DrugBank targets in p or in its 1-hop KEGG neighbours, and β is learned and initialised at 0.5. The cell context is z_{c|AB} = Σ_p g_p(A,B)·W_p u_p(c) with W_p ∈ R^{d'×8}. A pathway with g_p = 0 contributes exactly zero, so the logit is exactly invariant to that pathway's genes.

3) Symmetric head. s(A,B,c) = ½[MLP(d_A ⊕ d_B ⊕ z) + MLP(d_B ⊕ d_A ⊕ z)], logit-averaged. The original concat-MLP is kept, so the gain can be attributed to the encoder and the loss rather than the head.

4) Losses. L = L_wCE + λ_cell·L_cell + λ_drug·L_drug + λ_ent·L_sparse.
• L_cell (pair-matched): for each training triplet i = (A,B,c,y), sample j = (A,B,c',1−y) from the same training fold, if one exists. L_cell = softplus(m − (2y−1)(s_i − s_j)), with margin m = 1 and weight 1/√|matches_i| to avoid over-weighting pairs tested in many cell lines.
• L_drug (partner-matched): j = (A,B',c,1−y) or (A',B,c,1−y), with the same form.
• L_sparse = mean_p g_p · 1[p not in the target prior], a small push towards target-related pathways.
Defaults: λ_cell = 0.5, λ_drug = 0.25, λ_ent = 0.01, Adam lr 1e-4, batch 512 anchors plus up to 512 matched partners in the same forward pass, about 50 epochs on the subset. Checkpoint selection stays on validation F1 at 0.5. A scalar logit offset b* chosen on the validation fold only is reported as a separate ablation row; the main row uses a threshold of 0.5.

5) Counterfactual pathway explanation (classifier, test time). For a predicted-synergistic triplet (A,B,c), the reference c' is the matched antagonistic cell line from the training data with the nearest pathway-embedding distance. Define the hybrid x(S) = x_c with the genes of the pathways in S replaced by x_{c'}. Run greedy forward selection over the pathways with g_p > 0, adding the pathway whose swap lowers the logit most, until the prediction flips to <0.5. This gives the minimal flip set S*, which is a pair-specific, cell-specific causal pathway explanation. Each pathway also gets a contrastive contribution φ_p = s(x_c) − s(x({p})). Atom-level: integrated gradients on GAT node features (baseline zero), summed over atoms, giving drug substructure attributions for the same classifier.

6) Faithfulness protocol. (a) Deletion curves: drop in probability and in test AUPR when top-k pathways by φ are swapped to the reference cell, compared with random gated pathways and with SHAP-ORA pathways from the baseline. (b) A null-swap check: swapping all pathways with g_p = 0 must change the logit by exactly 0, which is verified numerically. (c) A sanity check with randomised weights. (d) Flip-set size distribution.

### Addresses limitations

L1, L4, L5, L3, L2

### Novelty claim

Existing synergy models, including DSimSynergy, JointSyn, HyperGraphSynergy, DeepDDS and the candidates S0–S3, are trained on i.i.d. triplets or on global rankings. None of them uses controlled counterfactual supervision, meaning training pairs that differ in exactly one factor (cell line or partner) and have the opposite label. S0 uses a global magnitude-weighted ranking; FlipPath-Syn uses single-factor, opposite-label matched contrasts. S1 retrieves exemplars as input features; here matched exemplars are used only as a training signal, and at test time as counterfactual references for explanation. S2 and S3 model pathway-pair crosstalk or dose non-additivity on the drug side. FlipPath-Syn instead puts structure in the cell encoder, using sparsemax gates conditioned on the drug pair, so pathway irrelevance is exact and interventional. To our knowledge it is also the first synergy model whose explanation is a minimal pathway-swap counterfactual that flips the classifier's own decision, with faithfulness guaranteed in part by construction (exact zero effect of ungated pathways) and tested by deletion curves, rather than post-hoc SHAP-expression correlation followed by ORA.

### Implementation plan

1) data/pathways.py: load the KEGG gene sets (msigdb c2.cp.kegg GMT) and intersect them with the 949 L1000 genes. Build the gene→pathway mask M (949×P+1), the KEGG 1-hop pathway adjacency, and per-drug target counts per pathway from the existing DrugBank target files. Cache everything as .npy.
2) data/matching.py: after the fixed split and fold indices are built, and using only the current fold's training indices, build dict pair→{cell: label} and (cell, drug)→{partner: label}. For each training index, precompute arrays of opposite-label matched indices for the pair-matched and partner-matched cases. No validation or test triplet is ever indexed.
3) model.py: add a PathwayCellEncoder (block-diagonal per-pathway MLPs via a masked Linear plus a grouped Linear), a PairGate (sparsemax implementation of about 20 lines, target prior term), and a symmetric forward pass that averages both drug orders. Keep the GCN, GAT and head modules unchanged. Expose forward(..., return_gate=True).
4) train.py: the collate function draws one pair-matched and one partner-matched partner for each anchor where available and concatenates them into the batch. Add L_cell, L_drug and L_sparse to the existing class-weighted CE. Use config flags for λ values so that ablations (λ=0, FC encoder in place of the pathway encoder, dense softmax gate in place of sparsemax, no target prior) are single switches. Keep validation-F1 checkpointing. Optionally fit a validation-only bias b* and report it separately.
5) explain.py: greedy minimal flip set, φ_p contributions, IG over atoms (captum), deletion/insertion curves compared with random and with SHAP-ORA baselines, null-swap assertion, randomised-weight sanity check. Outputs are CSVs and figures for the Binimetinib–Brigatinib case for continuity with the paper.
Compute: about 1.3× baseline time per epoch (doubled batch, small pathway MLPs). Fold-1 screening at 50 epochs takes well under an hour on half an A100; the full run is 5 folds × about 150 epochs.

### Expected effect

Fold-1 screening: AUPR +0.03 to +0.05 over the reproduced baseline at equal epochs, mostly from L_cell, the pair-matched contrasts that sharpen within-pair ranking across cell lines. F1 +0.02 to +0.04 at the fixed 0.5 threshold, and +0.04 to +0.06 with the validation-calibrated offset. AUROC +0.005 to +0.01. ACC unchanged or +0.002. Full benchmark target: AUPR ≈ 0.80–0.82 versus 0.77, F1 ≈ 0.76–0.78 versus 0.74, AUROC ≈ 0.965–0.97, ACC ≈ 0.98. The largest gains should appear on the stratum of test triplets whose pair has mixed labels across training cell lines. Expected ablation pattern: removing L_cell gives the largest drop; replacing sparsemax with softmax gives similar accuracy but loses the null-swap guarantee and has flatter deletion curves; the FC encoder is about 0.01 AUPR worse. Explanations: deletion of the top-3 φ pathways should reduce the predicted probability several-fold more than random gated pathways, and flip sets should typically contain 1–5 pathways.

### Risks

(1) Matched partners may be scarce for some pairs; with only about 3% positives, many positives may have no opposite-label partner in the same cell line. The loss then degrades towards plain CE and the gain shrinks. Coverage statistics will be logged and positives with no matched partner up-weighted. (2) The contrastive loss can over-emphasise pairs tested in many cell lines and hurt calibration at 0.5, which would show as worse F1 at 0.5 but better AUPR. Mitigations: 1/√n weighting, a lower λ_cell, and the reported calibrated offset. (3) The sparsemax gate may collapse to a few pathways, or to the "unannotated" module, which would make explanations trivial and hurt AUPR. Monitor gate entropy and fall back to τ = 1 or entmax-1.5. (4) The pathway-factorised encoder has more parameters than one FC layer and may overfit 83 cell lines, which would show as a train/validation gap. Use dropout on u_p and weight decay. (5) Greedy flip sets are approximate and depend on the choice of reference cell line, so they will be reported together with φ ranks and with stability across the 5 fold models.

### Novelty check

I searched for each of the three parts of FlipPath-Syn. Each part has a clear precedent, but I found no paper that combines them, or that applies the matched-counterfactual training signal to synergy prediction.

(ii) The pathway-factorised cell encoder conditioned on the drugs has close precedents. DRPreter uses drug-conditioned attention over KEGG pathway subgraphs, though for single-drug response. MOViDA and the DrugCell line of work use pathway-modular 'visible' networks, and MOViDA extends this to synergy. TranSynergy and DSimSynergy itself already produce pathway-level synergy explanations. What is new here is the sparsemax gate conditioned symmetrically on the drug pair, with a DrugBank target prior. That is a modest change: sparsemax and entmax are standard ways to get exact sparsity.

(iii) Counterfactual explanations that flip a prediction with a minimal change are well established in XAI; CF-GNNExplainer is one example. Faithfulness testing by perturbation exists for synergy models at the motif level (VINCENT). However, I found no synergy model whose explanation is the smallest set of pathways that, swapped in from a matched antagonistic cell line, flips the decision, with the guarantee that ungated pathways have exactly zero effect.

(i) For the matched-counterfactual contrastive loss, I found no prior work. It would pair each training triplet with one that differs only in the cell line, or only in one partner drug, and has the opposite label. Related ideas exist: PDTSyn treats each cell line as a domain, MGAE-DC uses label-specific channels, and HetBiSyn uses hard-negative mining. None of them uses single-factor, opposite-label matched pairs. The loss itself, though, is a pairwise margin loss applied to a sensible choice of pairs. That is closer to a well-motivated training trick than a new mechanism.

Overall this is a non-trivial and coherent combination of known parts (pathway-modular encoders, sparse gating, pairwise ranking losses, counterfactual explanations). It is new in how they are put together for this problem, but no single part is new in mechanism. That puts it at 6.

Closest prior work found:

- DRPreter: Interpretable Anticancer Drug Response Prediction Using Knowledge-Guided Graph Neural Networks and Transformer (2022) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9699175/: This is the closest match to component (ii). DRPreter splits the cell line into KEGG pathway subgraphs and uses a drug–pathway transformer to find the pathways that matter for each drug. That is a drug-conditioned, pathway-factorised cell encoder with per-pathway interpretation. Differences: it predicts single-drug response rather than pair synergy, it uses dense attention rather than sparsemax (so it has no exact-zero guarantee), and it has no counterfactual training or flip-set explanations.
- TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations (2021) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/: TranSynergy predicts synergy with pathway-level interpretation. It explains pathways post hoc, using SHAP followed by gene set enrichment (SA-GSEA), which is the same kind of explanation the proposal criticises in DSimSynergy. Its cell encoder has no pathway structure, and it uses no matched-contrast training.

<a id="s5"></a>
## S5 · novelty 5 · SLink-Syn: a synthetic-lethality coupling term over cell-specific network-propagated target footprints, giving gene-pair attributions for drug synergy

_Spread each drug's DrugBank targets over a protein–protein interaction (PPI) graph whose edge weights depend on the cell line's expression, giving a per-cell gene "footprint". A symmetric, low-rank gene×gene coupling matrix, guided by synthetic-lethality and paralog priors and gated by the cell's DepMap gene dependencies, scores how the two footprints complement each other. A redundancy penalty pushes down pairs that hit the same essential genes. The resulting term is added to the order-averaged DSimSynergy logit, so each prediction comes with exact, deletion-testable target-gene-pair explanations._

### Motivation

L4: DSimSynergy encodes the cell line independently of the drugs, with one fully connected layer over 949 genes. Drug targets are never connected to their own expression or essentiality in that cell. So the model cannot represent the most established mechanistic route to context-specific synergy: two drugs hitting complementary nodes of a buffered (synthetic-lethal or paralog-compensated) system that the cell actually depends on. L7: GCN smoothing over BP/ATC similarity assumes similar drugs synergise (PCC only 0.21–0.23), while the authors' own explanation is complementarity. Our coupling term rewards complementarity explicitly and penalises redundancy (overlapping essential targets), so it is heterophily-aware by construction. L2: concatenation plus an MLP has no explicit pair term. Ours is a bilinear pairwise interaction in gene space, conditioned on the cell. L5: explanations are currently post-hoc SHAP on a separate regression model. Our term decomposes exactly into contributions from gene pairs (i,j) inside the classifier itself, so we can run deletion faithfulness tests. L3: the coupling is symmetric, and the backbone logit is averaged over both drug orders, so predictions and attributions are order-invariant. Why this should help AUPR on the rare positive class: the positives that DSimSynergy misses are the context-specific ones, where the same pair is synergistic in a few cell lines only. Cell-specific dependency gating and expression-weighted propagation are the features that vary across cell lines for a fixed pair.

### Method

Gene universe: G = L1000 landmark genes (949) ∪ DrugBank targets of the 521 drugs, about 1.5–2.5k genes. Graph: STRING v12 physical/functional links with combined score ≥ 700, restricted to G and given self-loops; adjacency A.
Cell inputs: x_c = log2(TPM+1) expression over G (DepMap 24Q4, the same source the paper already uses). d_c = DepMap CRISPR Chronos gene effect over G, imputed with the gene-wise median where missing.
Essentiality gate: e_c = σ(−(d_c − θ)/τ), with θ = −0.5 and τ = 0.2 as defaults, and θ learnable.

1) Cell-conditioned propagation (APPNP-style personalised PageRank)
Edge gate: w_ij^c = A_ij · σ(a1·x_ic + a2·x_jc + a3·x_ic·x_jc + b), with 4 scalar parameters shared across edges. Ŵ^c = D^{-1/2} W^c D^{-1/2}.
Seed: s_A = softmax over the targets T_A of learned per-(drug, target) logits, initialised uniform; DrugBank action (inhibitor/agonist) is used as a sign feature.
Footprint: p_A^c = Σ_{k=0}^{K} α(1−α)^k (Ŵ^c)^k s_A, with K = 6 and α = 0.3. This is computed once per batch for each unique cell (83 cells) as sparse matrix products, then indexed by drug.

2) Synthetic-lethality coupling (symmetric, low rank)
q_A = g_c ⊙ p_A^c, where g_c = e_c ⊙ softplus(w_g·x_c + b_g) is a gene-wise gate for expression and dependency.
M = ½(U Λ Vᵀ + V Λ Uᵀ), with U, V ∈ R^{|G|×R}, R = 32, and Λ diagonal.
z_SL = q_Aᵀ M q_B. This is symmetric in A and B and never forms the full |G|² matrix: z_SL = ½[(Uᵀq_A)ᵀΛ(Vᵀq_B) + (Vᵀq_A)ᵀΛ(Uᵀq_B)].

3) Redundancy (anti-synergy) term
z_red = −softplus(β) · (p_A ⊙ e_c)ᵀ(p_B ⊙ e_c) / (‖p_A ⊙ e_c‖ ‖p_B ⊙ e_c‖ + ε).
Hitting the same essential genes predicts additivity or antagonism.

4) Final logit
ℓ = ½[f_DSim(A,B,c) + f_DSim(B,A,c)] + γ · (z_SL + z_red), with γ learnable and initialised at 0.1.
The DSimSynergy backbone is unchanged (BP/ATC GCN, molecular GAT, cell MLP).

5) Prior and sparsity regularisers
- SL prior: L_prior = −mean_{(i,j)∈P} M_ij + mean_{(i,j)∼random} softplus(M_ij), where P = SynLethDB human SL pairs ∪ Ensembl paralog pairs within G.
- Sparsity: L_sp = ‖U‖_1 + ‖V‖_1.
- Total loss: L = class-weighted CE (as in the paper) + λ_p L_prior + λ_s L_sp, with λ_p = 0.05 and λ_s = 1e-5.

6) Training and evaluation
Same splits, Adam lr 1e-4 (the coupling module also uses lr 1e-4), batch 512, about 50 epochs on the screening subset. Checkpoint chosen by validation F1, as in the protocol. Test predictions use threshold 0.5 and are averaged over fold models.

7) Explanations (exact, inside the classifier)
- z_SL = Σ_{i,j} q_Ai M_ij q_Bj. The top gene pairs (i,j) by |q_Ai M_ij q_Bj + q_Aj M_ji q_Bi| give the target-to-target or target-to-downstream-gene pairs that drive each prediction in that cell.
- Path attribution: decompose p_A into per-hop contributions along the PPI graph.
- Pathway-level summaries come from aggregating pair scores over KEGG gene sets. This aggregation is exact, not ORA.
- Faithfulness: (a) deletion curves that zero the top-k genes in g_c, compared with random genes of matched degree, reporting Δprob and ΔAUPR; (b) a sanity check with randomised U and V.
- SHAP over expression and GAT/atom attributions are kept so the paper's analyses remain available.

### Addresses limitations

L4, L7, L2, L5, L3

### Novelty claim

S2 scores crosstalk between KEGG pathway pairs, S3 models non-additivity in dose space, S1 retrieves training exemplars, S4 trains on counterfactual triplets, and S0 adds a generic trilinear embedding head. This idea is different from all of them. It places the interaction in gene space, as a learned synthetic-lethality coupling between network-propagated target footprints. It uses three cell-specific ingredients that no candidate and no published synergy GNN we know of (DeepDDS, JointSyn, HyperGraphSynergy, DSimSynergy) combines: (i) a PPI propagation operator whose edge weights depend on the cell's expression; (ii) gating by CRISPR dependency (essentiality); (iii) a bilinear coupling that is anchored to SL and paralog priors and paired with an explicit redundancy penalty, so it separates complementarity from overlap. Network-proximity "complementary exposure" (Cheng et al. 2019) is static, does not depend on the cell, and is not learned. Here it becomes a differentiable, cell-specific, supervised module whose explanations are gene pairs and can be tested by deletion.

### Implementation plan

1) Data prep script (new file prep_slink.py):
- Build the gene universe G from the L1000 list plus DrugBank targets of the drugs in Code/Data/TRAIN.
- Download the STRING edges (≥700), the DepMap 24Q4 CRISPRGeneEffect matrix (same release as the expression data), and the SynLethDB and paralog lists.
- Save: A as a sparse COO tensor; x_c and d_c for the 83 cell lines; a target-index list per drug; the prior pair index P.
2) Model (new module slink.py): class SLinkHead(nn.Module) holds the edge gate, per-target seed logits, U, V, Λ, the gate g_c, β and γ. forward(drugA_idx, drugB_idx, cell_idx):
- Run the propagation for the unique cells (torch.sparse.mm, K = 6).
- Gather the footprints for A and B and return z_SL, z_red and cached q vectors for attribution.
- Memory is small: for each of up to 83 cells, |G| × number of drugs used in the batch, about 2k × 521 floats, roughly 4 MB per cell, done in chunks.
3) Edit the DSimSynergy model file (the class whose forward concatenates the three drug features with the cell feature):
- Compute f(A,B,c) and f(B,A,c) and average their logits.
- Add γ(z_SL + z_red) to the synergy-class logit. For the 2-class CE output, add it to logit[:,1] − logit[:,0] by adding to logit[:,1].
4) Edit the training loop: add L_prior and L_sp to the loss. Splits, the class weights, the F1-based checkpointing and the 0.5 threshold stay unchanged.
5) New explain_slink.py:
- Top gene-pair attributions per triplet, aggregated over KEGG.
- Deletion and insertion curves on the test set versus random degree-matched genes.
- Sanity check with randomised weights.
6) Ablation flags:
- --no_sl (backbone + order averaging only);
- --no_prop (K = 0, targets only);
- --no_dep (e_c = 1);
- --shuffle_dep (dependency vectors permuted across cells);
- --no_prior (λ_p = 0);
- --no_red.
Each is run on the screening subset (fold 1, 50 epochs). The full 5-fold run is done for the best configuration.

### Expected effect

These are hoped-for effects, not measured results.
- Internal test, screening subset: AUPR up by about 0.02–0.04 over DSimSynergy re-run at the same budget. F1 up by about 0.02–0.03, because there should be fewer false positives on pairs that are synergistic in other cell lines but not this one, and more recall on context-specific positives.
- AUROC up by about 0.005. ACC roughly unchanged at about 0.98.
- Full benchmark target: AUPR ≥ 0.79 and F1 ≥ 0.75, against the paper's 0.77 and 0.74.
- Order averaging should also reduce the fold-to-fold variance of F1.
- Ablations: most of the gain should disappear under --no_sl and --shuffle_dep, which would confirm that the cell-specific coupling is the cause.
- Explanations: deletion of the top-k attributed genes should cause a much larger drop in synergy probability than random degree-matched deletion. A non-trivial share of the top pairs should be known SL or paralog pairs or members of the same pathway, for example MAPK and PI3K nodes for combinations involving Binimetinib.

### Risks

(1) In the random split, memorisation by the backbone may dominate, so the coupling term adds little and γ shrinks towards 0. This would show up as small differences between the full model and --no_sl; mitigation is to report the PairOut/CellOut-style breakdown on validation. (2) DepMap CRISPR data may be missing for some of the 83 cell lines; median imputation weakens the gate. --shuffle_dep would then show no loss. (3) Hub genes in STRING can dominate the footprints and make the explanations generic (TP53, EGFR everywhere). Mitigations: degree-normalised propagation and comparing against degree-matched random genes in the deletion tests. (4) The SL prior lists are sparse and biased towards cancer genes, so the prior could overfit attributions to known pairs. Check this with --no_prior and the randomised-weight sanity check. (5) Adding an external data source (CRISPR effects) could be challenged. It is a cell-level feature from the same DepMap release, contains no synergy labels and does not touch the external test sets. The --no_dep ablation measures the effect without it. (6) Extra parameters (U and V: about 2k × 32 × 2) could overfit the about 3% positive class. The L1 penalty and low rank limit this; overfitting would show up as a gap between validation and test AUPR.

### Novelty check

The main ingredients are already published. TranSynergy (2021) combines network-propagated drug-target profiles over a PPI network with cell gene dependency and expression, and explains predictions with SHAP over genes and pathways. That is the core of the 'cell-specific target footprint + essentiality + gene-level explanation' idea for this task, and the proposal's novelty section omits it. SynCell (2025) already builds a PPI subnetwork for each cell line from expression. Cheng et al. (2019) set out the complementarity-versus-overlap principle on the interactome. SL-partner mapping of drug targets for combination discovery dates to 2018. What I found no precedent for is the specific form: a learned, symmetric, low-rank bilinear gene×gene coupling between the two footprints, regularised towards SynLethDB and paralog pairs; a separate redundancy penalty on shared essential genes; propagation edges gated by the cell's expression; and exact in-model gene-pair attributions with deletion tests. That is a non-trivial adaptation and combination rather than a new mechanism, so 5 fits better than 3–4 or 7. Caveats: I could not read Li et al. 2018 ('Network propagation predicts drug synergy in cancers', Cancer Research), which may overlap further. A yeast study found that synergy predicted from chemical-genetic profiles plus the genetic-interaction network did not hold up, which questions the SL-coupling hypothesis. TranSynergy should be cited and ideally used as a baseline.

Closest prior work found:

- TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations (2021) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/: High. Each drug is represented by its DrugBank targets propagated over a PPI network; the cell line by gene dependency and/or expression over the same genes; a transformer combines them, and a SHAP-based gene-set method gives gene and pathway attributions. This already covers the core of 'propagated target footprints + cell essentiality + gene-level explanations'. It lacks a learned symmetric bilinear SL coupling, SL/paralog priors, a redundancy penalty, cell-conditioned edge weights and exact in-model gene-pair attributions.
- SynCell: Contextualized Drug Synergy Prediction (2025) https://arxiv.org/html/2511.17695v3: Medium. Builds a PPI subnetwork for each cell line from that cell's highly expressed proteins inside a drug–protein–cell knowledge graph for synergy prediction; claims better generalisation and interpretability. Anticipates the cell-conditioned propagation ingredient (hard subnetworks rather than learned expression-gated edge weights). No SL coupling or dependency gating.

<a id="s0"></a>
## S0 · novelty 4.5 · SymTri-Rank: symmetric, cell-conditioned trilinear interaction head trained with magnitude-aware ranking, plus interaction-decomposed attributions for DSimSynergy

_Replace DSimSynergy's order-dependent concat+MLP head with a permutation-invariant, cell-gated low-rank drug×drug×cell interaction head and a partner/cell-conditioned atom readout. Train it with class-weighted CE plus a Loewe-magnitude-weighted pairwise ranking loss and a Loewe regression loss, and calibrate the logit offset on the validation fold only. The aim is higher AUPR/F1, with explanations that are exact and order-consistent and whose faithfulness is tested._

### Motivation

DSimSynergy's AUROC is 0.96 but its AUPR is only 0.77 and F1 0.74. That gap is what you would expect from a model that ranks well overall but orders the rare positives poorly at the top, and is evaluated at a 0.5 threshold whose meaning has been shifted by class weighting. Five limitations drive this and are fixed together:
(L2) Synergy is a non-additive drug×drug×cell interaction, but the baseline only concatenates features and leaves the MLP to discover multiplicative terms from about 3% positives. That is data-hungry, and the interaction itself is never exposed.
(L3) Concatenation makes f(A,B,c) ≠ f(B,A,c). Symmetry is only encouraged through augmentation, so predictions and SHAP attributions depend on input order. Mirrored copies of test triplets can also enter training if augmentation happens before the split.
(L1, L8) Pointwise class-weighted BCE neither optimises the top of the ranking nor uses the Loewe magnitude. A score of 11 and a score of 80 get the same label, even though magnitude is a strong ordering signal among positives.
(L6, L5) Global max-pooled GAT attention is computed per drug, ignoring the partner drug and the cell line. The attributions come from a separate regression model, and their faithfulness is never measured.

### Method

Notation: drug a, drug b, cell c, label y∈{0,1}, Loewe score s (available for every labelled triplet). Data, splits and labels are unchanged.

1) Drug encoder. Keep the BP-GCN, ATC-GCN and molecular GAT. Replace the global max pool with a context-conditioned gated attention readout. For drug a with atom states h_i (GAT output, dimension F), partner pooled vector m_b (a mean pool of b's atoms, used only as the query, so there is no recursion) and cell vector h_c:
- q = W_q[m_b ; h_c]
- α_i = softmax_i( w^T tanh(W_k h_i + q) )
- g_a = Σ_i α_i h_i
The α_i are exact convex weights that depend on the partner and the cell.
Drug vector: z_a = LayerNorm(W_d[e_a^BP ; e_a^ATC ; g_a]) ∈ R^256. The same shared weights are used for both drugs.

2) Cell encoder. Keep the 949-gene MLP: h_c = LeakyReLU(W_1 x_c) ∈ R^256, with dropout 0.2.

3) Cell-conditioned FiLM:
- γ_c = 1 + tanh(W_γ h_c)
- β_c = W_β h_c
- u_a = γ_c ⊙ z_a + β_c (same for u_b)

4) Symmetric interaction head. The logit is ℓ = ℓ_add + ℓ_int + b0, where:
- ℓ_add = MLP_add([u_a + u_b ; h_c]). This is the additive / single-agent context term.
- ℓ_int = MLP_pair([u_a ⊙ u_b ; |u_a − u_b|]) + Σ_{r=1..R} (P u_a)_r (P u_b)_r (Q h_c)_r. The second part is a low-rank trilinear (CP) drug×drug×cell term with R = 64 and shared P, so it is symmetric in a and b.
Every component is invariant to swapping a and b. Reverse-order augmentation becomes unnecessary and is removed, which also removes any risk of mirror leakage. The MLPs are 2 layers with hidden size 256, LeakyReLU and dropout 0.3.

5) Auxiliary heads, which share the same encoder:
- Regression head: ŝ = MLP_reg(same features as the logit). Loss L_reg = Huber_δ=1( ŝ − clip(s, −50, 100)/20 ).
- Magnitude-aware pairwise ranking loss within each batch. P = positives, N = negatives. N_h = the top-k (k = 8·|P|, capped at |N|) negatives with the highest logits, i.e. hard-negative mining.
  L_rank = (1/|P||N_h|) Σ_{i∈P, j∈N_h} w_i · softplus( −(ℓ_i − ℓ_j)/τ )
  where w_i = 1 + log(1 + (s_i − 10)/10) and τ = 0.5.
  If a batch has no positives, L_rank = 0. Batches are drawn by a sampler that guarantees at least 16 positives per batch of 512 while keeping the natural class ratio for the remainder.
- Total loss: L = L_wCE + λ_rank·L_rank + λ_reg·L_reg, with λ_rank = 0.5 and λ_reg = 0.2. L_wCE uses the baseline's class weights.

6) Validation-only calibration (L1). After training each fold, fit a scalar temperature T and offset δ on that fold's validation set: the offset maximises validation F1 at p = σ((ℓ+δ)/T) ≥ 0.5, and T minimises validation NLL. Fold both into the model's bias, so the reported ACC and F1 still use threshold 0.5 on the model's output probability. The test set is never touched. Checkpoint selection still uses validation F1 as in the protocol, computed after re-fitting δ at each evaluated epoch. To be transparent, the uncalibrated F1@0.5 is also reported.

7) Explanations of the evaluated classifier itself (L5):
(a) Exact decomposition ℓ = ℓ_add + ℓ_int. Report what fraction of each positive's logit comes from the interaction term.
(b) Integrated Gradients (50 steps, baseline = training-set mean expression) of ℓ_int with respect to the 949 genes, giving pair-specific gene attributions. Aggregate them to KEGG/GO-BP gene sets by summed |IG| with a permutation null, rather than via correlation + ORA.
(c) Atom attributions = α_i × IG over atom features. Because the readout is conditioned, the atoms highlighted for drug a change with partner b.
(d) Faithfulness: deletion curves on the test set (for analysis only, no selection). Mask the top-k genes (replace with their mean) or top-k atoms (zero the node) for k ∈ {5, 10, 20, 50}. Measure the drop in predicted probability and in AUPR versus random masking of the same k, and run a randomised-weights sanity check. Compare against GMP+GAT-attention and SHAP on the baseline.
(e) Order consistency: attributions under (a,b) versus (b,a) are identical by construction. For the baseline, report their Spearman correlation.

Defaults: Adam lr 1e-4 (heads at 3e-4), batch 512, weight decay 1e-5, 50 epochs on the subset benchmark, 150 epochs per fold on the full benchmark, early stopping with patience 30 on validation F1.

### Addresses limitations

L1, L2, L3, L8, L6, L5

### Novelty claim

Relative to DSimSynergy, the main new element is a provably order-invariant, cell-gated low-rank trilinear drug×drug×cell head. It sits on top of the functional/clinical similarity GCN and the molecular GAT, and it splits each logit exactly into an additive part and an interaction part that can be attributed separately. The second new element is a context-conditioned atom readout, which gives combination-specific substructure attributions instead of per-drug GAT attention. The third is training with a Loewe-magnitude-weighted, hard-negative pairwise ranking loss alongside CE and an auxiliary Loewe regression. Prior synergy models (DeepDDS, AttenSyn, JointSyn, HyperGraphSynergy) use these pieces only separately or not at all: bilinear or attention fusion without exact symmetry, plain BCE, and separate classification and regression models. None of them reports faithfulness via deletion curves on the evaluated classifier.

### Implementation plan

1) Data loader (Code/ dataset script): drop the reverse-order augmentation, or keep it only on the training split after splitting; for the symmetric model it is redundant either way. Carry the Loewe score s as a third tensor alongside y. Implement a PositiveAwareBatchSampler that guarantees at least 16 positives per batch of 512.
2) models.py:
- Replace the global max pool in the GAT module with ContextReadout(h_atoms, batch_idx, query) that returns g and α.
- Add DrugProj (concat→Linear→LayerNorm), FiLM(h_c) and SymTriHead(u_a, u_b, h_c) returning (ℓ_add, ℓ_int, ŝ).
- forward() computes m_a and m_b (mean pools) first, then each drug's readout with the query [m_partner ; h_c].
3) train.py: implement loss = wCE + 0.5·rank_loss(logits, y, s) + 0.2·huber(ŝ, s'), where rank_loss does in-batch hard-negative mining. After each validation pass, fit the offset δ by grid search over logit quantiles to maximise validation F1, then select the checkpoint by that F1. After training, fit T on validation by LBFGS and store T and δ in the checkpoint.
4) eval.py: apply σ((ℓ+δ)/T), compute AUPR, AUROC, F1@0.5 and ACC@0.5 on the held-out test set, and average over the folds' models. Also log the uncalibrated F1@0.5.
5) explain.py: use Captum IntegratedGradients on ℓ_int with respect to cell expression and atom features; aggregate to KEGG gene sets from the existing enrichment resources; implement the deletion/insertion curves and the randomised-weights check; check order consistency.
6) Ablations on the subset benchmark (fold 1, 50 epochs): baseline; +symmetric head only; +trilinear term; +rank loss; +regression loss; +calibration; +context readout. This attributes the gain to each component.

### Expected effect

These are the expected effects on the DrugCombDB internal test set; none of them has been run yet.
- AUPR: from 0.77 to about 0.80–0.83. The main contributors should be the explicit interaction term and the magnitude-weighted ranking loss, both of which order strong synergies at the top.
- F1: from 0.74 to about 0.77–0.80, mostly from validation-calibrated thresholding, with lower variance across folds because symmetry removes order noise.
- AUROC: from 0.96 to about 0.96–0.97.
- ACC: about 0.98, unchanged or slightly higher.
- Explanations: the deletion curves should show a significantly larger probability and AUPR drop for top-IG genes and top-attributed atoms than for random masking. Order-consistency should be 1.0, against Spearman well below 1 for the baseline.

### Risks

- Ranking loss over-sharpens scores. Calibration would show this as AUROC or ACC falling, or the validation-chosen offset becoming extreme. Mitigation: lower λ_rank to 0.2.
- The trilinear term overfits to drug identity with only 83 cell lines. This would show as training–validation gap growth. Mitigation: dropout on P and Q, and reduce R to 32.
- The validation-selected offset may not transfer to the test set when validation positives are few. This would show as calibrated F1 being no better than uncalibrated. Both are reported.
- Removing augmentation could reduce effective sample count for the GAT. If so, keep training-only augmentation, which is harmless for a symmetric model.
- The Loewe regression could compete with classification (negative transfer). This would show as lower AUPR when the regression loss is added in the ablation; then set λ_reg to 0.
- Context-conditioned atom attention could become diffuse and less interpretable. Deletion curves will show whether it is faithful anyway.
- Possible protocol objection: the calibration offset is folded into the model, but it is fitted only on validation data. Uncalibrated threshold-0.5 numbers are reported as well for transparency.

### Novelty check

I score this idea 4.5 out of 10. It brings together known components well, but its central design was already published, mainly in RECOVER.

**Already published**
- **The symmetric, cell-conditioned head.** RECOVER (2022) has a permutation-invariant combination module (symmetric aggregation plus a bilinear tensor with symmetric slices), conditioned on the cell line through FiLM. That is essentially "symmetric head + cell FiLM".
- **The low-rank drug×drug×cell interaction term.** DTF (2019) and comboFM (2020) already model synergy as low-rank drug × drug × cell-line tensor/factorization interactions.
- **Exact symmetry instead of data augmentation.** The interpretable-GNN synergy paper (2021) already gets exact order invariance from a symmetric factorization decoder.
- **Partner- and cell-conditioned atom attention.** SDDSynergy, HSSynergy and CongFu already provide partner- and/or cell-conditioned substructure attention or fusion. The context-conditioned atom readout is a variant of these.

**Apparently new**
In my searches I found no synergy model that uses all of the following:
- a Loewe-magnitude-weighted, hard-negative pairwise ranking loss next to class-weighted CE and an auxiliary Loewe regression;
- an exact additive-versus-interaction split of the logit, with attribution computed separately on the interaction term;
- faithfulness tests (deletion curves, randomised-weight sanity checks, order-consistency) applied to the classifier that is actually evaluated.

These are the real contributions. However, each one is a standard technique imported from learning-to-rank or explainable-AI work. Fitting the decision offset on validation data is routine.

**Why 4.5**
- It is more than an obvious single trick (3), because it is grafted onto DSimSynergy's similarity-GCN backbone and the explanation-faithfulness part is a non-trivial combination.
- It is below 5–6 because the most prominent claimed novelty, the "provably order-invariant cell-gated bilinear/trilinear head", is closely anticipated by RECOVER.
- The ranking and faithfulness pieces may be less explored in this field, but my searches were not exhaustive.

To argue for novelty, the paper should cite RECOVER, DTF and comboFM directly. It should then present the magnitude-aware ranking objective and the faithfulness-tested interaction attributions as the main contributions, rather than the symmetric head.

Closest prior work found:

- RECOVER: sequential model optimization platform for combination drug repurposing identifies novel synergistic compounds in vitro (2022) https://arxiv.org/abs/2202.04202: High overlap with the head design. RECOVER already builds a permutation-invariant drug-combination module from symmetric aggregation and a bilinear tensor whose slices are constrained to be symmetric, and it conditions the model on the cell line with FiLM. That covers the core of SymTri-Rank's 'symmetric, cell-gated bilinear/trilinear head plus FiLM'. RECOVER differs in three ways: it uses Bliss regression, not Loewe classification; it has no ranking loss; and it has no GO/ATC similarity GCNs or attribution decomposition.
- Interpretable Drug Synergy Prediction with Graph Neural Networks for Human-AI Collaboration in Healthcare (2021) https://arxiv.org/abs/2105.07082: Moderate overlap. It uses a symmetric factorization decoder (u1^T D^T D u2), which makes drug-pair synergy scores order-invariant by construction, and it argues for interpretability. This is a precedent for exact symmetry instead of augmentation. It has no cell-gated CP term, no ranking loss and no faithfulness tests.

<a id="limitations"></a>
## Limitations of the human state of the art (8)

### L1. Fixed 0.5 threshold and plain class-weighted cross-entropy are mismatched to ~3% positives (methodological)

The model is trained with class-weighted BCE/CE and evaluated at a fixed 0.5 threshold. Class weighting changes the scale of the predicted probabilities, so 0.5 is not the F1-optimal operating point, and BCE optimises a pointwise likelihood rather than how well positives are ranked at the top, which is what AUPR measures. This should show up as F1 (0.74) clearly below what the ranking quality (AUROC 0.96) would allow, and as variance in F1 across folds. A follow-up method could optimise the precision–recall region directly (focal loss, a pairwise/AUC or AP surrogate loss, or hard-negative mining) and choose the decision threshold (or calibrate) on the validation fold only. Choosing the checkpoint by validation F1 at 0.5 also makes model selection depend on this arbitrary threshold.

_Evidence:_ "For computing ACC and F1, we applied a default decision threshold of 0.5 to the predicted probabilities"; benchmark: class-weighted cross-entropy, checkpoint by validation F1; AUPR 0.77 / F1 0.74 vs AUROC 0.96, ACC 0.98 ("these metrics were already approaching their upper bounds").

### L2. Synergy is modelled by concatenation plus an MLP, with no explicit drug–drug or drug–cell interaction term (methodological)

The three drug embeddings per drug and the cell-line embedding are simply concatenated and passed to an FCNN. Synergy is by definition a non-additive interaction between two drugs in a specific cellular context. Concatenation forces the MLP to learn multiplicative and contextual interactions implicitly, which is data-hungry for the rare positive class. It also gives no interpretable account of why a particular pair interacts. A follow-up could use explicit interaction modules: bilinear or tensor-factorised drug×drug×cell terms, cross-attention between substructures of the two drugs, or cell-conditioned (FiLM-style) gating of the drug embeddings. These should improve AUPR and F1, especially for pairs whose drugs are individually common but whose synergy is context-specific, and would expose pairwise attributions.

_Evidence:_ "These features are fused and concatenated through drug-drug-cell triplet combinations and input into the prediction module"; Fig. 1D: "The concatenated vectors are input into FCNN for prediction".

### L3. The architecture depends on drug order; symmetry is only encouraged by data augmentation (methodological)

Because of the concatenation, f(A,B,c) ≠ f(B,A,c) in general. The authors add reversed triplets to the training data instead of building in permutation invariance, and they do not symmetrise at test time. As a result, predictions and attributions for the same pair can differ depending on input order. Augmenting before the 9:1 split could also let (B,A,c) mirrors of test triplets into training. A permutation-invariant pair encoder (sum/product, or a symmetric bilinear form) or averaging both orders at inference would make predictions and SHAP attributions order-consistent, and is expected to reduce variance on the held-out set.

_Evidence:_ "each drug triplet (Drug A, Drug B, Cell line) was augmented by including its reverse ordering ... such that the model learns symmetric representations regardless of input order. Data were partitioned into training and test sets at a 9:1 ratio".

### L4. Cell-line encoder ignores drug targets and pathway structure; pathway explanations are post-hoc correlations (methodological)

Cell lines are encoded by a single FC layer over 949 L1000 genes, independently of which drugs are being combined. Drug target genes enter only indirectly, through BP-Jaccard similarity weights, and are never linked to the target genes' expression in that cell line. Gene and pathway explanations are produced afterwards: SHAP values are correlated with expression, and the genes with PCC > 0.5 go into a hypergeometric ORA. The architecture has no pathway structure, so the KEGG explanations are a second-stage statistical summary rather than faithful model mechanisms. A follow-up could use a target-aware, pathway-structured cell encoder: KEGG or GO gene-set bottleneck units, with expression gated or attended by each drug's targets and their network neighbourhood. This gives built-in, drug-pair-specific pathway attributions and a better inductive bias for the 83-cell-line regime.

_Evidence:_ Eq. (10): h = σ(W(1)x + b(1)) on 949 genes; "we computed the correlation between gene expression values and their corresponding SHAP values"; "KEGG pathway enrichment analysis using hypergeometric test-based ORA on genes with positive correlations greater than 0.5".

### L5. Explanations come from a different model (regression) than the classifier being evaluated, and faithfulness is never tested (evaluation)

The SHAP gene and pathway analysis is run on the synergy-score regression model, and case drugs are chosen using regression-predicted scores. The benchmarked classifier itself is never explained. No quantitative faithfulness test is reported, such as deletion/insertion curves, ablating the top-SHAP genes or top-attention atoms, or a sanity check with randomised weights. Plausibility is argued only through literature anecdotes. A follow-up should explain the classifier directly and report faithfulness metrics (for example, the drop in AUPR or in the predicted probability when the top-k attributed genes, pathways or atoms are masked, compared with random masking). This also gives a measurable way to show the explanations are more faithful.

_Evidence:_ "we employed SHAP ... to interpret cell line features within our synergy score prediction model (see Supplementary Note 6)"; "drug combinations were screened and selected based on their synergy scores, which were predicted by the DSimSynergy model".

### L6. GAT attention with global max pooling is an unreliable substructure attribution (methodological)

Graph-level drug features use element-wise global max pooling, so each output dimension is set by a single atom and most atoms get zero gradient. GAT attention coefficients describe how neighbours are weighted when messages are passed between atoms, not how much each atom contributes to the synergy prediction. The paper shows only atoms with attention scores above 1 for two drugs. The attention is also computed per drug, independently of the partner drug and the cell line, so it cannot show which substructure matters for this particular combination. Attention-based or gated readouts conditioned on the partner drug and the cell, attributions computed by integrated gradients or occlusion, and a substructure-masking faithfulness test would address this. The richer readout may also help AUPR.

_Evidence:_ Eq. (9): h_graph = max_i h'_i (GMP); "Attention weight visualization of drug molecular substructures ... (only atoms with scores greater than 1 are shown)"; GAT applied per drug, then concatenated.

### L7. The GCN on similarity networks assumes homophily that the data only weakly support (theoretical)

The GCN uses symmetric-normalised propagation (Eq. 5) over BP and ATC similarity graphs, which smooths each drug's MACCS features towards its similar neighbours. Pairwise similarity, however, correlates only weakly with mean synergy (PCC 0.21 for BP, 0.23 for ATC), and pathway complementarity rather than similarity is what the authors themselves invoke as the mechanism. Uniform smoothing can blur the features that distinguish complementary drugs. The neighbour contributions are also not exposed as explanations. Learned edge weights or attention over the similarity networks (GAT-style, or allowing negative/heterophilic messages) would let the model decide which neighbours matter and would yield neighbour-level attributions. Gains should appear as better AUPR on pairs of dissimilar drugs that are synergistic.

_Evidence:_ "significant positive correlations for both the similarity network based on biological process (PCC = 0.21...) and ... ATC (PCC = 0.23...)"; "drugs form a 'pathway complementarity network' by targeting distinct but interconnected signaling pathways"; Eq. (5), with fixed adjacency A.

### L8. Classification and regression models are trained separately, so the classifier never sees the continuous Loewe score (methodological)

The binary task discards the magnitude of Loewe scores: triplets with score 11 and score 80 receive the same label. Triplets in the (0,10] band are dropped entirely, and the regression model is trained separately. The synergy magnitude is a rich ranking signal for the rare positive class that the classifier never uses. Multi-task training, with a shared encoder, the classification head and an auxiliary Loewe regression or ranking head on the same training triplets (labels and splits unchanged), could improve the ordering of positives and therefore AUPR. It would also make the gene and pathway attributions consistent between the two tasks.

_Evidence:_ "For the binary synergy classification task ... optimized using binary cross-entropy loss. For the synergy score prediction task ... optimized using mean squared error loss"; the paper describes them as "two distinct prediction tasks".
