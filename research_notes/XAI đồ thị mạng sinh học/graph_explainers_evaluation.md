# Graph explainability and explanation evaluation, transferable to network-based drug synergy prediction (drug A, drug B, cell line triple)

Legend: **[V]** = checked against a source fetched or searched in this session. **[PK]** = from prior knowledge, not re-checked in this session. The citation and arXiv ID are believed correct, but treat formulas and numbers as unverified until you check the paper.

## Q1. Which instance-level explainers (mask, search, Shapley, path) suit heterogeneous/multi-relational graphs and link/triple prediction?

### Takeaway
Path-based explainers fit synergy best. PaGE-Link (WWW 2023, not KDD), Power-Link (KDD 2024) and xPath (AAAI 2023) were designed for heterogeneous graphs and link or node prediction. Their explanation is a path, e.g. drug A → target → PPI path → gene ← target ← drug B, plus cell-line context. Generic mask explainers (GNNExplainer, PGExplainer, GraphMask) can be used on a triple, but they return unordered edge sets. They need relation-aware masks and a connectivity constraint to be readable.

### Cited Findings
- **PaGE-Link**: Zhang S., Zhang J., Song X., Adeshina S., Zheng D., Faloutsos C., Sun Y. "PaGE-Link: Path-based Graph Neural Network Explanation for Heterogeneous Link Prediction." Proc. ACM Web Conference 2023 (WWW '23), pp. 3784–3793; arXiv 2302.12465. **It is WWW 2023, not KDD 2023 as the task brief says.** [V] — [arXiv](https://arxiv.org/pdf/2302.12465.pdf); [NSF PAR](https://par.nsf.gov/biblio/10464426)
  - Idea: heterogeneous path-enforcing mask learning. Edge masks are learned per edge type and regularised so that the selected edges form paths from source to target. Candidate paths are then extracted with a k-shortest-path search on the mask-weighted graph. Code: github.com/amazon-science/page-link-path-based-gnn-explanation. [V] — [arXiv](https://arxiv.org/pdf/2302.12465.pdf)
  - Results: using its explanations improved AUC for recommendation on citation and user-item graphs by 9–35%. 78.79% of human-evaluation responses preferred its explanations. Moving from subgraph search to path search shrinks the search space by orders of magnitude, and runtime scales linearly in the number of edges. [V] — [deepai summary of paper](https://api.deepai.org/publication/page-link-path-based-graph-neural-network-explanation-for-heterogeneous-link-prediction)
- **Power-Link** (Chang Y. et al., KDD 2024; arXiv 2401.02290 [PK on ID]): the first path-based explainer for GNN knowledge-graph-completion models, and it compares against PaGE-Link. It is the closest match to multi-relational triple scoring. [V for existence/venue] — [liner review](https://liner.com/review/pathbased-explanation-for-knowledge-graph-completion)
- **xPath**: Li Y. et al. "Towards Fine-Grained Explainability for Heterogeneous Graph Neural Network." AAAI 2023; arXiv 2312.15237. It explains black-box heterogeneous GNNs on node classification. Each explanation is a (node, influence path) pair: the node says *what* matters and the path says *how* it affects the prediction. It perturbs walks by graph rewiring, needs no access to model internals, and finds the top-K explanations by greedy search. The authors report better fidelity than adapted baselines; this is self-reported. [V] — [arXiv](https://arxiv.org/pdf/2312.15237); [mlanthology](https://mlanthology.org/aaai/2023/li2023aaai-fine/)
- **GNNExplainer**: Ying R., Bourgeois D., You J., Zitnik M., Leskovec J., NeurIPS 2019, arXiv 1903.03894. It learns a soft edge mask M and a feature mask F that maximise mutual information MI(Y, (G_S, X_S)). In practice it minimises the cross-entropy of the original prediction under the masked graph, plus a size penalty ‖M‖₁ and a mask-entropy penalty. It runs one optimisation per instance and applies to node, graph and (by adaptation) link tasks. [PK] — [arXiv](https://arxiv.org/abs/1903.03894)
- **PGExplainer**: Luo D. et al., NeurIPS 2020, arXiv 2011.04573. A shared MLP takes embeddings and predicts edge-mask logits, sampled with a Gumbel/concrete relaxation. Because it is amortised and inductive, it is fast for many triples. Later work reported that it was hard to reproduce [PK]. — [arXiv](https://arxiv.org/abs/2011.04573)
- **GraphMask**: Schlichtkrull M., De Cao N., Titov I., ICLR 2021, arXiv 2010.00577. It learns, per layer, gates that drop messages (edges) and replace them with a learned baseline vector, trained amortised with an L0/hard-concrete penalty. It was built for R-GCN-style multi-relational models (QA, SRL), so it suits relation-typed graphs well. [PK] — [arXiv](https://arxiv.org/abs/2010.00577)
- **PGM-Explainer**: Vu M., Thai M.T., NeurIPS 2020, arXiv 2010.05788. It perturbs node features, records prediction changes, and fits a Bayesian network over node variables, which gives dependency structure rather than additive scores. [PK] — [arXiv](https://arxiv.org/abs/2010.05788)
- **SubgraphX**: Yuan H., Yu H., Wang J., Li K., Ji S., ICML 2021, arXiv 2102.05152. It runs Monte Carlo tree search over connected subgraphs, scoring each by a Shapley value with players restricted to the L-hop neighbourhood. It is expensive, and designed for graph and node classification. [PK] — [arXiv](https://arxiv.org/abs/2102.05152)
- **GStarX**: Zhang S., Liu Y., Shah N., Sun Y., NeurIPS 2022, arXiv 2206.07161. It scores nodes with the structure-aware HN value (Hamiache–Navarro), which respects graph connectivity, unlike plain Shapley. [PK] — [arXiv](https://arxiv.org/abs/2206.07161)
- **GraphSVX**: Duval A., Malliaros F., ECML-PKDD 2021, arXiv 2104.10482. It builds a surrogate on node and feature coalitions (a decomposition similar to KernelSHAP) and gives Shapley estimates jointly for nodes and features. [PK] — [arXiv](https://arxiv.org/abs/2104.10482)
- Survey reference: Yuan H., Yu H., Gui S., Ji S. "Explainability in Graph Neural Networks: A Taxonomic Survey." IEEE TPAMI 2022/2023, arXiv 2012.15445. [PK] — [arXiv](https://arxiv.org/abs/2012.15445)
- **CETExplainer** (closest biomedical analogue, see Q5): it treats drug response as link prediction in a directed heterogeneous network and uses an R-GCN over 4 edge types: sensitivity, resistance, drug similarity, and cell similarity. It is compared to GNNExplainer and ExplaiNE. [V] — [arXiv 2408.17129](https://arxiv.org/html/2408.17129v2)

### Inferences
- For a synergy triple (A, B, c), a natural explanation is a set of paths from A and from B that converge on genes or pathways, weighted by cell-line context. PaGE-Link's path-enforcing loss can be adapted with two sources (A, B) and a cell-line-conditioned node set. Power-Link's design is more natural if the model scores the triple like a KG link.
- Mask explainers explain one forward pass. When the triple score is symmetric in A and B, the masks should be symmetrised or explained jointly. Otherwise an explanation for (A, B) can differ from one for (B, A).
- Shapley-based methods (SubgraphX, GraphSVX, GStarX) are attractive for the "interaction" framing. With PPI-scale graphs (more than 10k nodes) they are costly, unless the players are restricted to a k-hop neighbourhood around both drugs' targets.

### Gaps
- No published paper was found that applies PaGE-Link, Power-Link or xPath to drug-synergy or drug–gene graphs.
- PIGNN: could not identify a uniquely named "PIGNN" self-explaining GNN. The name is used by several unrelated physics-informed or pathway-informed works. The intended paper needs clarification.

## Q2. Counterfactual graph explainers: are they suitable for "which gene/edge removal kills synergy"?

### Takeaway
Counterfactual explainers answer the minimal-edit question directly ("remove the fewest edges/genes to flip synergistic → non-synergistic"). This maps onto knockout or CRISPR-style biology and can be checked against DepMap dependency. Most were built for node or graph classification on homogeneous graphs. A synergy setting needs a regression-to-threshold target and type-restricted edits (for example, only PPI or target edges).

### Cited Findings
- **CF-GNNExplainer**: Lucic A., ter Hoeve M., Tolomei G., de Rijke M., Silvestri F., AISTATS 2022, arXiv 2102.03322. It learns a binary perturbation of the adjacency matrix by edge deletion only. The loss combines a prediction-flip term and an edit-distance term, and the result is a minimal deletion set that changes the prediction [PK on loss details]. The paper uses drug discovery as its motivating example and contrasts itself with explainers that return an "important subgraph" rather than a counterfactual. [V] — [arXiv](https://arxiv.org/pdf/2102.03322v4)
- **CLEAR**: Ma J., Guo R., Mishra S., Zhang A., Li J., NeurIPS 2022, arXiv 2210.08443. It is a generative (graph VAE) counterfactual explainer with a causal-model view, which makes it amortised. It allows node and feature edits as well as edge edits. [PK] — [arXiv](https://arxiv.org/abs/2210.08443)
- **GCFExplainer**: Huang Z., Kosan M., Medya S., Ranu S., Singh A., WSDM 2023, arXiv 2210.11695. It finds *global* counterfactuals: a small set of representative counterfactual graphs that cover many inputs, found by vertex-reinforced random walks over the edit graph. [PK] — [arXiv](https://arxiv.org/abs/2210.11695)
- **RCExplainer**: Bajaj M. et al., "Robust Counterfactual Explanations on Graph Neural Networks", NeurIPS 2021, arXiv 2107.04086. It models decision regions of the last GNN layer as linear boundaries, and selects edges that are robust to noise and counterfactual. [PK] — [arXiv](https://arxiv.org/abs/2107.04086)
- **CLARUS** (bioRxiv 2022.11.21.517358): an interactive platform where domain experts manually edit PPI-based patient graphs (synthetic network plus two KIRC networks) and re-predict or retrain the GNN. It is a human-in-the-loop counterfactual tool for biology. [V] — [bioRxiv](https://www.biorxiv.org/content/10.1101/2022.11.21.517358.full.pdf)
- A 2026 comparative study (arXiv 2609.05113) benchmarks counterfactual explainers that allow multiple types of graph edit, and gives a drug–drug adverse-interaction example. A March 2026 paper (De Sanctis et al., arXiv 2603.04209) argues for going beyond edge deletion in counterfactuals for molecular graphs. [V for existence; contents not read] — [arXiv 2609.05113](https://arxiv.org/pdf/2609.05113); [arXiv 2603.04209](https://arxiv.org/abs/2603.04209)
- The search found no peer-reviewed application of CF-GNNExplainer specifically to drug–gene or synergy networks. [V, negative result] — [search context: CF-GNNExplainer](https://arxiv.org/pdf/2102.03322v4)

### Inferences
- An "in silico knockout" counterfactual removes all edges of a gene node. It is directly comparable to DepMap CRISPR gene effect in the same cell line, and to SynLethDB pairs: removing a gene that is synthetic-lethal with drug A's target should change the A+B prediction. That gives an external validity check that path and mask explainers lack.
- Edge-deletion-only counterfactuals (CF-GNNExplainer) are the safest for PPI graphs, because added edges have no biological meaning unless they are taken from a curated resource.
- Out-of-distribution risk: deleting hub edges makes graphs the model never saw in training, which is the same OOD issue raised in Q5 (Azzolin et al.).

### Gaps
- No published counterfactual-explainer study on synergy triples was found. Whether a counterfactual explanation agrees with experimental double-knockout data is untested.

## Q3. Interaction attribution (Shapley interaction index, Shapley-Taylor, Integrated Hessians, Faith-SHAP, Archipelago): has any of it been applied to drug combinations?

### Takeaway
Yes, though not inside GNNs. Janizek et al. used Integrated Hessians on an AML drug-combination neural network (JMLR 2021). They also used Shapley interaction indices of drug × gene in XGBoost ensembles (Nat Biomed Eng 2023), validated with pathway enrichment and DepMap. Other synergy models (TranSynergy) use plain SHAP plus gene-set enrichment. Applying interaction indices to graph explainers for synergy appears unexplored.

### Cited Findings
- **Integrated Hessians**: Janizek J.D., Sturmfels P., Lee S.-I. "Explaining Explanations: Axiomatic Feature Interactions for Deep Networks." JMLR 22 (2021), 1–54; arXiv 2002.04138. It extends Integrated Gradients to pairwise interactions: Γ_ij(x) is a double path integral of ∂²f/∂x_i∂x_j between baseline and input. Self-interaction terms make Σ_ij Γ_ij = IG completeness [PK on the formula]. The authors report it is faster than other methods when there are many features. The case study is the largest public AML drug-combination dataset (12,362 two-drug samples on patient cells). They found that variability in response is attributable to the drug Venetoclax is paired with, and analysed which genetic factors modulate the drug–drug interaction. [V] — [JMLR](https://jmlr.org/papers/v22/20-1223.html); [arXiv](https://arxiv.org/pdf/2002.04138)
- **EXPRESS / ensembles of explainable models**: Janizek J.D., Dincer A.B., Celik S., Chen H., Chen W., Naxerova K., Lee S.-I. "Uncovering expression signatures of synergistic drug responses via ensembles of explainable machine-learning models." Nat Biomed Eng 7(6):811–829 (2023), doi:10.1038/s41551-023-01034-0. [V] — [PMC11149694](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694)
  - Method: 133 combinations of 46 drugs tested ex vivo in samples from 285 AML patients. They used TreeSHAP on 100 XGBoost models and averaged explanations, which is valid by Shapley linearity. **They used a Shapley interaction index between each drug feature and each gene** to find genes whose importance depends on a specific drug being in the combination, and tested the rankings for pathway enrichment. [V] — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694)
  - Findings relevant to evaluation. Predictive accuracy did not reliably indicate explanation quality within a model class. Single models gave highly variable attributions. Ensembling raised the average pairwise cosine similarity of attributions from 0.77 to 0.98. At realistic AML transcriptome correlation levels, all methods performed poorly with high variance. [V] — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694)
  - Biological validation. A monocytic differentiation signature predicted Venetoclax-combination synergy, consistent with known resistance of monocytic subclones. DepMap dependency on the drug targets was significantly associated with the signature (empirical P = 0.001, 0.001 and 0.026 under three null models). Known mechanisms were recovered: BCL-2 for venetoclax; CDA and NT5C2 for cytarabine. [V] — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694)
- **TranSynergy** (Liu Q., Xie L., PLoS Comput Biol 2021): a transformer over gene–gene interactions for synergy. It proposes SA-GSEA (Shapley Additive Gene Set Enrichment Analysis), which uses SHAP gene attributions for pathway deconvolution. This is additive, not an interaction index. [V] — [PMC7906476](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/)
- **Shapley interaction index**: Grabisch M., Roubens M., Int J Game Theory 28 (1999) 547–565. For players i, j: I_ij = Σ_{S⊆N\{i,j}} [|S|!(n−|S|−2)!/(n−1)!]·[v(S∪{i,j}) − v(S∪{i}) − v(S∪{j}) + v(S)]. The bracketed term is the discrete "synergy" (second difference), structurally the same as Bliss-style excess over additivity. [PK] — [doi 10.1007/s001820050125](https://doi.org/10.1007/s001820050125)
- **Shapley-Taylor interaction index**: Sundararajan M., Dhamdhere K., Agarwal A., ICML 2020, arXiv 1902.05622. It is an order-k analogue of a Taylor expansion and satisfies an interaction-distribution axiom. [PK] — [arXiv](https://arxiv.org/abs/1902.05622)
- **Faith-SHAP**: Tsai C.-P., Yeh C.-K., Ravikumar P., JMLR 2023, arXiv 2203.00870. It defines interaction indices as the coefficients of the most faithful order-ℓ polynomial approximation of the set function, and is unique under its axioms. [PK] — [arXiv](https://arxiv.org/abs/2203.00870)
- **Archipelago**: Tsang M., Rambhatla S., Liu Y., NeurIPS 2020, arXiv 2006.10965. ArchDetect detects interactions with discrete mixed differences, and ArchAttribute attributes to interaction sets. It is model-agnostic and fast. [PK] — [arXiv](https://arxiv.org/abs/2006.10965)
- Caveat: Shapley attributions are harder to get right with correlated features such as gene expression. [V, via search summary of Janizek 2023] — [PMC11149694](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694)

### Inferences
- A synergy model is itself an interaction function. Explaining it by gene-level interaction indices over drug-A-side and drug-B-side features matches the biological question better than additive gene scores. One concrete version: I_{g_A, g_B} for a gene in A's neighbourhood and a gene in B's neighbourhood, with masking of nodes or edges as the value function.
- Ensembling explanations (Janizek 2023) is a cheap way to improve stability, and should be reported as a baseline for any GNN explainer.

### Gaps
- No graph-structured (node/edge-player) Shapley interaction application to synergy GNNs was found.
- Not checked: whether the Janizek JMLR AML case study used a graph. It is believed to use tabular expression plus drug identity [PK].

## Q4. Which self-explainable / inherently interpretable GNNs are relevant?

### Takeaway
GSAT (stochastic attention with an information bottleneck) and prototype GNNs (ProtGNN) are the main inherently interpretable designs. In synergy, the existing "self-explainable" work is attention or pooling based (SANEpool, CASynergy). Its faithfulness is not guaranteed: raw GAT attention is unstable and naive averaging over layers is insufficient.

### Cited Findings
- **GSAT**: Miao S., Liu M., Li P. "Interpretable and Generalizable Graph Learning via Stochastic Attention Mechanism." ICML 2022, arXiv 2201.12987. It learns Bernoulli edge attention p_uv and samples a subgraph. A KL term to a prior Bernoulli(r) bounds I(G; G_S), an information-bottleneck view, so the selected subgraph is what the predictor actually uses. [PK] — [arXiv](https://arxiv.org/abs/2201.12987)
- **ProtGNN**: Zhang Z., Liu Q., Wang H., Lu C., Lee C., AAAI 2022, arXiv 2112.00911. It classifies by similarity to learned prototype subgraphs, which are projected onto real training subgraphs by MCTS. [PK] — [arXiv](https://arxiv.org/abs/2112.00911)
- **SANEpool**: Dong Z. et al., "Interpreting the Mechanism of Synergism for Drug Combinations Using Attention-Based Hierarchical Graph Pooling," arXiv 2209.09245; published in *Cancers* 2023 (PMC10486573). Self-attention graph pooling scores genes and gene–gene and gene–drug edges, and selects a sub-network per cell line and combination as the explanation. Networks are built from genes in 46 core cancer signalling pathways; data come from NCI ALMANAC. [V] — [arXiv](https://arxiv.org/pdf/2209.09245); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10486573)
- **CASynergy**: a causal-attention model that builds cell-line-specific gene networks from prior knowledge and adds causal inference for interpretable synergy prediction. [V, abstract-level] — [PMC12548910](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12548910/)
- **Attention faithfulness**: Hu et al., "Faithful Interpretation for Graph Neural Networks," arXiv 2410.06950. Small perturbations, such as adding an edge or a node, significantly change both GAT predictions and attention interpretations. They propose FGAI, which stabilises attention. [V] — [arXiv](https://arxiv.org/abs/2410.06950v1)
- Shin et al., "Revisiting Attention Weights as Interpretations of Message-Passing Neural Networks," arXiv 2406.04612. Averaging attention over layers is insufficient. Their GAtt accounts for the computation tree, and they argue GATs are explainable when interpreted correctly. [V] — [arXiv](https://arxiv.org/html/2406.04612v1)
- The original NLP critique is Jain S., Wallace B.C. "Attention is not Explanation," NAACL 2019, arXiv 1902.10186; with the rebuttal by Wiegreffe S., Pinter Y., "Attention is not not Explanation," EMNLP 2019. [PK] — [arXiv](https://arxiv.org/abs/1902.10186)
- **Azzolin et al. (ICLR 2025)** report that self-explainable and domain-invariant ("modular") GNNs escape the result that perfectly faithful explanations of injective regular GNNs are uninformative (see Q5). This is a theoretical argument for building the explainer into the synergy model. [V] — [arXiv 2406.15156](https://arxiv.org/abs/2406.15156v2)

### Inferences
- When attention or pooling is used as the explanation in a synergy GNN (SANEpool, GraphSynergy-style), report a perturbation-based fidelity check and a stability check. Attention weights alone will not satisfy reviewers given the papers above.
- A GSAT-style stochastic edge mask on the PPI layer, conditioned on (A, B, c), is the most direct inherently interpretable design for this thesis.

### Gaps
- No GSAT or ProtGNN application to synergy was found.
- PIGNN is unidentified (see Q1).

## Q5. Evaluation: which metrics, benchmarks and known faithfulness pitfalls apply?

### Takeaway
Report fidelity+ and fidelity− (necessity and sufficiency), sparsity, stability, and where possible ground-truth accuracy. Do not treat agreement with ground truth as proof that the explanation is faithful to the model. Faber et al. (KDD 2021) showed models may not use the planted motif. Azzolin et al. (ICLR 2025) showed faithfulness metrics disagree with each other, are tied to OOD behaviour, and are uninformative for injective regular GNNs.

### Cited Findings
- **GraphXAI / ShapeGGen**: Agarwal C., Queen O., Lakkaraju H., Zitnik M. "Evaluating Explainability for Graph Neural Networks." Scientific Data 10, 144 (2023); doi:10.1038/s41597-023-01974-x; arXiv 2208.09339. ShapeGGen generates synthetic graphs with ground-truth explanations and controllable size, degree distribution and homophily or heterophily. GraphXAI includes loaders, GNNs, visualisers and metrics. [V] — [arXiv](https://arxiv.org/abs/2208.09339v2); [Zitnik lab](https://zitniklab.hms.harvard.edu/projects/GraphXAI)
  - Metric families: Graph Explanation Accuracy (GEA), Faithfulness (GEF), Stability (GES), and counterfactual and group fairness (GECF, GEGF). [V] — [DOAJ](https://doaj.org/article/993af0bc7ead4318aa8097ae16a3be21)
  - Formula details [PK]: GEA is a Jaccard index between the predicted and ground-truth masks. GEF = 1 − exp(−KL(ŷ_full ‖ ŷ_masked)). GES is the distance between explanations of an input and its perturbed version. Exact forms were not checked; the Springer page was blocked by a login redirect.
  - ShapeGGen was designed to avoid the Faber et al. pitfalls, such as redundant explanations and weak predictors. [V] — [search summary](https://arxiv.org/pdf/2208.09339v2.pdf)
- **Fidelity and characterization score**: Amara K., Ying R., Zhang Z., Han Z., Shan Y., Brandes U., Schemm S., Zhang C. "GraphFramEx: Towards Systematic Evaluation of Explainability Methods for Graph Neural Networks." LoG 2022, PMLR 198:44:1–44:23; arXiv 2206.09677. It separates *necessary* explanations (measured by Fid+) from *sufficient* ones (Fid−) and combines them into a single **characterization score**. Finding: personalised PageRank did best on synthetic benchmarks, while gradient methods did better on complex real graphs. [V] — [PMLR](https://proceedings.mlr.press/v198/amara22a.html); [arXiv](https://arxiv.org/html/2206.09677v5)
  - Formulas [PK]. Fid+ = 1/N Σ [1(ŷ_i = y_i) − 1(ŷ_i^{G∖S} = y_i)], i.e. the change when the explanation is removed. Fid− = 1/N Σ [1(ŷ_i = y_i) − 1(ŷ_i^{S} = y_i)], i.e. the change when only the explanation is kept. Probability versions replace the indicators with predicted probabilities. Charact = (w₊+w₋) / (w₊/Fid+ + w₋/(1−Fid−)), a weighted harmonic mean, by default w₊ = w₋ = 0.5. Sparsity = 1 − |S|/|G|. Fidelity originates in Yuan et al. TPAMI ([arXiv 2012.15445](https://arxiv.org/abs/2012.15445)) and Pope et al. CVPR 2019.
- **Faber L., Moghaddam A.K., Wattenhofer R.** "When Comparing to Ground Truth is Wrong: On Evaluating GNN Explanation Methods." KDD 2021, pp. 332–341. The standard pipeline (train GNN, explain, compare to planted ground truth) has five pitfalls, mainly that the GNN may not use the ground-truth edges. They propose three benchmark datasets to avoid these, and evaluate gradient methods, GNNExplainer and PGM-Explainer. [V] — [DBLP](https://dblp.org/rec/conf/kdd/FaberMW21)
- **Azzolin S., Longa A., Teso S., Passerini A.** "Reconsidering Faithfulness in Regular, Self-Explainable and Domain Invariant GNNs." ICLR 2025; arXiv 2406.15156 (v1 titled "Perks and Pitfalls of Faithfulness…"). Findings: (i) faithfulness metrics are not interchangeable, so an explanation can score faithful on one and unfaithful on another; (ii) for injective regular GNNs, perfectly faithful explanations are completely uninformative; (iii) this does not hold for modular (self-explainable or domain-invariant) GNNs; (iv) faithfulness is tightly linked to OOD generalisation. [V] — [arXiv](https://arxiv.org/abs/2406.15156v2); [ICLR](https://www.iclr.cc/virtual/2025/poster/28564)
- Related work: Agarwal C., Zitnik M., Lakkaraju H. "Probing GNN Explainers: A Rigorous Theoretical and Empirical Analysis of GNN Explanation Methods," AISTATS 2022, arXiv 2106.09078. [V, existence] — [arXiv](https://arxiv.org/pdf/2106.09078v2.pdf). An ICLR 2026 poster, "GNN Explanations that do not Explain and How to find Them", continues this line. [V, existence only] — [ICLR 2026](https://iclr.cc/virtual/2026/poster/10010418)
- **CETExplainer's evaluation** has no fidelity metric. It reports Precision@k, Recall@k and F1@k against constructed ground truth (best F1 = 0.6594), and stability as the average overlap of explanations across training epochs of the prediction model: Stability = Σ|T_e1 ∩ T_e2| / N_E. CETExplainer and GNNExplainer scored about 8, ExplaiNE 1.058. [V] — [arXiv 2408.17129](https://arxiv.org/html/2408.17129v2)

### Inferences
- Recommended protocol for the thesis:
  1. Fid+ and Fid− with the characterization score on the *regression* synergy score, using absolute change or a threshold flip.
  2. Sparsity curves.
  3. Stability across seeds or epochs and across input perturbations.
  4. Semi-synthetic ground-truth accuracy, by planting a synergy mechanism.
  5. Biological plausibility (Q6).
  
  Report fidelity alongside an OOD-aware variant, for example retraining with removal (RemOve And Retrain) or soft masks, because of Azzolin et al.
- Ground-truth agreement on planted motifs is only valid if the model is shown to rely on the motif. One check is accuracy collapsing when the motif is ablated, which addresses the Faber pitfalls.

### Gaps
- Exact GraphXAI and GraphFramEx formulas were not re-checked: Springer was blocked and the appendix was not fetched. The [PK] formulas should be verified from the PDFs.
- No synergy-specific explainer benchmark exists that I could find.

## Q6. Which biomedical ground-truth proxies and semi-synthetic benchmarks can validate synergy explanations?

### Takeaway
No database gives "true" explanations for synergy. The practical approach combines (a) constructed ground truth from the data graph, as CETExplainer does, (b) semi-synthetic planted mechanisms, and (c) orthogonal biological evidence: DepMap dependency, known-MoA combinations, pathway enrichment, SL pairs, and LINCS signatures. Janizek et al. 2023 is a worked example of (c).

### Cited Findings
- **CETExplainer**: Li X., Gui J., Gao Q., Shi H., Yue Z. "Controllable Edge-Type-Specific Interpretation in Multi-Relational Graph Neural Networks for Drug Response Prediction." arXiv 2408.17129 (v2, Sep 2024; no venue listed). [V] — [arXiv](https://arxiv.org/html/2408.17129v2)
  - Data: GDSCv2 (17,071 response pairs; 477 cell lines × 157 drugs), CCLE omics, PubChem SMILES, 49,343 cell-similarity and 5,540 drug-similarity triples. **No PPI network is used.**
  - Objective: max_{G_s} MI(Y, G_s) + Score(G_s), with Score = Σ_r w_r r_i + Penalty(N) and Penalty = αN + βN². The edge-type weights w_r are user-controllable (0.1/0.4/0.4/0.1).
  - **Ground-truth construction**: for a (cell line, drug) prediction, take the one-hop similar cell lines and similar drugs and check whether sensitive or resistant links exist among them. This gives 3 scenarios, and explanations are scored by triple overlap. It is a "neighbourhood-consistency" proxy, not mechanistic truth.
- **DepMap** as external validation: Janizek et al. used DepMap genetic dependency to validate an explanation-derived signature (empirical P ≤ 0.026). [V] — [PMC11149694](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694). DepMap reference: Tsherniak A. et al., Cell 2017, doi:10.1016/j.cell.2017.06.010. [PK] — [doi](https://doi.org/10.1016/j.cell.2017.06.010)
- **Known MoA recovery** (BCL-2 for venetoclax; CDA and NT5C2 for cytarabine) was used as a positive-control check. [V] — [PMC11149694](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694). A canonical synergy-MoA control is BRAF + MEK inhibition (dabrafenib + trametinib) in BRAF-V600 melanoma, where the expected explanation is the MAPK path BRAF→MEK1/2→ERK. Flaherty K.T. et al., NEJM 2012, doi:10.1056/NEJMoa1210093. [PK] — [doi](https://doi.org/10.1056/NEJMoa1210093)
- **Pathway enrichment**: TranSynergy's SA-GSEA (SHAP + GSEA) [V] — [PMC7906476](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/); Janizek's interaction-index rankings tested for enrichment [V] — [PMC11149694](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694).
- **Synthetic lethality**: KG4SL (Wang S. et al., Bioinformatics 2021) is a KG-GNN for SL prediction, and is a source of SL-pair knowledge and models. [V] — [PMC8336442](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8336442/). SynLethDB 2.0: Wang J. et al., Database (Oxford) 2022 [PK; venue unverified, possibly Database not NAR].
- **LINCS L1000**: Subramanian A. et al., Cell 2017, doi:10.1016/j.cell.2017.10.049 [PK]. A 2025 preprint (arXiv 2512.22251) merges PrimeKG++ with LINCS 2020 into a directed KG for perturbation prediction. [V] — [arXiv](https://www.arxiv.org/pdf/2512.22251)
- **Semi-synthetic GT**: ShapeGGen (Q5) is generic. In biology, CLARUS uses a synthetic PPI-based dataset with known modules. [V] — [bioRxiv](https://www.biorxiv.org/content/10.1101/2022.11.21.517358.full.pdf)

### Inferences
- Construct a semi-synthetic synergy benchmark. Keep the real PPI graph and real drug–target edges, then define a synergy label as a known function of the graph. For example, synergy occurs when A's and B's targets lie on two parallel branches of a pathway, or when a SynLethDB pair is hit across them, gated by cell-line expression. Train the model on these labels. The planted genes and paths become the ground truth, and the Faber check (does the model actually use them?) can be run by ablation. *(The deleted local file data/make_synthetic.py and ground_truth.json in the repo suggest this was already prototyped.)*
- Validation tiers for real data:
  1. Do explanation genes overlap DrugBank targets of A or B?
  2. Are they enriched for Reactome/KEGG pathways of the known MoA?
  3. Is their DepMap gene effect stronger in cell lines where the pair is synergistic?
  4. Are SL pairs among (gene near A, gene near B) enriched?
  5. Is the LINCS consensus signature of A or B concordant with them?

### Gaps
- No paper was found that builds explanation ground truth specifically for drug *synergy* triples. CETExplainer covers single-drug response only.
- SynLethDB and DrugBank citation details were not verified.

## Q7. Context-specific networks (cell-line/tissue PPI, signed/directed resources): are any used in synergy models?

### Takeaway
Cell-line context in synergy GNNs is usually injected by expression-gating a global STRING PPI (SynCell) or by building cell-line-specific gene networks from prior knowledge (CASynergy, SANEpool). Signed and directed resources (SIGNOR, KEGG; OmniPath not found in synergy GNNs) appear mainly in logic-modelling synergy work such as CASCADE.

### Cited Findings
- **SynCell** (Peng K. et al., arXiv 2511.17695 v3, Dec 2025; preprint): a heterogeneous drug–protein–cell graph built from NCI-ALMANAC, PrimeKG, STRING, DepMap and DrugBank. It uses one global STRING network (combined score above 400; 16,591 edges, 1,257 proteins). Cell context comes from "expresses" edges for proteins in the top 20% of DepMap expression (13,529 edges), not separate per-cell subnetworks. It claims interpretability but gives no explanation analysis. Its result tables are internally inconsistent; treat with caution. [V] — [arXiv](https://arxiv.org/html/2511.17695v3)
- **CASynergy**: builds cell-line-specific networks with prior knowledge plus causal attention. [V, abstract] — [PMC12548910](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12548910/)
- **SANEpool**: detects cell-line-specific sub-networks over 46 core cancer pathways. [V] — [arXiv 2209.09245](https://arxiv.org/pdf/2209.09245)
- **Logic modelling with signed networks**: Niederdorfer B. et al., "Strategies to Enhance Logic Modeling-Based Cell Line-Specific Drug Synergy Prediction," Front Physiol 2020, doi:10.3389/fphys.2020.00862. The CASCADE 2.0 prior-knowledge network was extended manually using SIGNOR, KEGG and literature. The paper notes study bias in annotated interactions. [V] — [PMC7399174](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7399174/)
- Resources [PK]:
  - PCNet: Huang J.K. et al., Cell Systems 2018, "Systematic Evaluation of Molecular Networks for Discovery of Disease Genes," doi:10.1016/j.cels.2018.03.001.
  - HumanBase/GIANT tissue networks: Greene C.S. et al., Nat Genet 2015, doi:10.1038/ng.3259.
  - OmniPath: Türei D. et al., Nat Methods 2016; Mol Syst Biol 2021, doi:10.15252/msb.20209923.
  - SIGNOR 3.0: Lo Surdo P. et al., NAR 2023 (database issue).
  
  Links: [PCNet](https://doi.org/10.1016/j.cels.2018.03.001); [GIANT](https://doi.org/10.1038/ng.3259); [OmniPath 2021](https://doi.org/10.15252/msb.20209923)

### Inferences
- Expression-pruned or expression-gated PPI is the de facto cell-line context mechanism. An explainer should then report whether its explanation genes are actually expressed in cell line c, which is a cheap plausibility filter.
- Signed and directed edges (OmniPath, SIGNOR) would let path explanations carry activation or inhibition semantics. For example, A inhibits X, which activates Y, and B inhibits Y, giving convergent inhibition. No synergy GNN using this was found, so it is a potential thesis contribution.

### Gaps
- No synergy GNN using OmniPath or signed message passing was found.
- Whether PCNet or HumanBase tissue networks have been used in synergy GNNs was not verified.
- Tool-call budget prevented checking GraphSynergy (Yang J. et al., JAMIA 2021 [PK]) and DeepDDS for their network and interpretability details.
