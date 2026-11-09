# Frontier, open gaps, and venues for network-based explainable drug synergy prediction (2024–2026)

Scope note: about 17 search and fetch calls (as of 2026-11-09). Already-covered papers are only noted, not analysed: TranSynergy, GraphSynergy, SANEpool, IDSP, PathSynergy, SynerGNet, HANSynergy, KGANSynergy, MGAE-DC, HypergraphSynergy, SDCInterpreter, SynergyX, DeepDDS. "[UNVERIFIED]" means the claim comes only from a search snippet or abstract; I did not read the full text.

## Q1. 2024–2026 network-based synergy models that claim interpretability

### Takeaway
Network-based interpretable synergy papers kept appearing in 2025–2026. Examples are CASynergy, SDCInterpreter, HyperSynergyX, SynCell and DRUGSYNC. Almost all of them validate explanations only qualitatively (pathway enrichment plus literature case studies). Few report cold-start results, and none that I found uses a signed or directed network or predicted drug–target interactions (DTIs) as seeds.

### Cited Findings
- **CASynergy.** Li H, Zheng L, Li L, Chen Y, Li J, Zheng C, Su Y. *PLoS Comput Biol* 2025;21(10):e1013567, doi:10.1371/journal.pcbi.1013567. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)
  - *Network and model:* starts from a human PPI network (15,790 proteins, 217,160 edges) and builds a cell-line-specific network. CCLE-derived key proteins per cell line are the seeds, and Dijkstra plus a greedy Steiner-like heuristic connects them. A GCN encodes each drug's molecular graph. A second GCN runs over the cell-line network with gene expression as node features. Cross-attention links the drug pair and the cell line.
  - *Explanation method:* a causal-attention module learns soft node and edge masks that split the graph into a "causal" and a "shortcut" subgraph, trained with bias and intervention losses. The top 25% of genes by mask score become key genes, which go into Enrichr KEGG enrichment.
  - *Validation:* qualitative only. Pathways are compared with the literature for KPL-1, NCI-H520 and ES2. Of the top 100 predicted combinations, 14 are supported by the literature. Removing causal attention lowers AUC only from 0.8740 to 0.8645. There is no quantitative explanation metric and no wet-lab work.
  - *Evaluation:* includes drug cold-start, combination cold-start and cell-line cold-start splits on Oncology-Screen (21 drugs, 29 cell lines). Data are DrugCombDB and Oncology-Screen.
  - *Code:* github.com/ahu-bioinf-lab/CASynergy
- **SDCInterpreter** (already covered). *J Chem Inf Model*, Dec 2025. Heterogeneous drug–gene–pathway–cell graph, RGCN, then mask learning plus Dijkstra to extract mechanism paths. — [JCIM](https://pubs.acs.org/doi/10.1021/acs.jcim.5c02569); [PubMed](https://pubmed.ncbi.nlm.nih.gov/41469369/)
- **HyperSynergyX.** *IEEE JBHI* 2026, doi:10.1109/jbhi.2026.3673550. — [DOI](https://doi.org/10.1109/jbhi.2026.3673550) [UNVERIFIED, snippet only]
  - Predicts three-drug combinations with a hypergraph random walk.
  - A knowledge-graph retrieval-augmented generation (RAG) module retrieves mechanistic subgraphs and generates hypotheses with an LLM.
  - The explanation is generated text, not attribution.
- **SynCell.** Peng K, Su G, Shi Q, Gao S, Wang R, Chen C, Wen J. arXiv:2511.17695 (v1 Nov 2025, v4 Mar 2026). — [arXiv](https://arxiv.org/abs/2511.17695)
  - Heterogeneous GNN over drug–protein, protein–protein and protein–cell-line relations, with "cell-line-resolved interactomes" reconstructed from transcriptomics.
  - Claims its largest gains on unseen drugs and novel cell lines, and claims "biological interpretability".
  - The abstract does not describe how the network is built, whether drug–protein links are curated or predicted, or how interpretability was validated. No code link on the abstract page. [UNVERIFIED beyond the abstract]
- **DRUGSYNC.** bioRxiv 2024.12.05.627115. GCN over a STRING PPI graph with drug–protein and expression features mapped onto nodes. Claims good performance on novel drugs and cell lines. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.12.05.627115v1.full.pdf) [UNVERIFIED]
- **DIPx** ("Pathway activation model for personalized prediction of drug synergy"). bioRxiv 2024.06.05.597583, also an eLife reviewed preprint. Uses pathway activation scores and reports which pathways contribute most to each prediction. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.06.05.597583v3.full); [eLife](https://elifesciences.org/reviewed-preprints/100071) [UNVERIFIED details]
- **SYNERGIE.** *iScience* 2026. Network controllability analysis plus random walk with restart on a PPI network, combined with Bayesian optimization. Mechanism-based rather than deep learning. — [iScience](https://www.cell.com/iscience/fulltext/S2589-0042(26)00714-5); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13053784/) [UNVERIFIED details]
- **KGLGANSynergy.** *J Transl Med* 2025. Knowledge-graph local/global attention network. The snippet shows no explanation component. — [Springer](https://link.springer.com/article/10.1186/s12967-025-07545-5)
- **SynergyGraph.** *Sci Rep*, Dec 2025. Knowledge graph plus hypergraph for cell-line-specific synergy scores. Explainability was not evident in the snippet. — [PubMed](https://pubmed.ncbi.nlm.nih.gov/41444381/)
- **MD-Syn.** *Front Pharmacol* 2025. Molecular graph plus node2vec embeddings of a 978-landmark-gene PPI network. — [Frontiers](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2025.1564339/pdf)
- **PDTSyn.** *Brief Bioinform* 2026;27(2):bbag199. Treats each cell line as a domain and splits drug representations into domain-invariant and domain-specific parts (domain generalization). It is not explicitly network-based. — [BIB](https://academic.oup.com/bib/article/27/2/bbag199/8662206) [UNVERIFIED details]
- **DPASyn.** arXiv:2505.19144. "Mechanism-aware" dual attention for synergy. — [arXiv](https://arxiv.org/pdf/2505.19144) [UNVERIFIED details]
- **VINCENT.** Chuang F-S, Li X, Bian Y, Zhou K. arXiv:2608.25841, Aug 2026. Molecular-level rather than network-based, but directly relevant to interaction-level, quantitatively evaluated explanations.
  - It is a post-hoc method that explains a fixed synergy predictor with motif-pair explanations, meaning one motif from each drug that jointly drives the prediction.
  - Evidence comes from attention and gradients, and candidate motif pairs are checked with repeated local perturbations.
  - Quantitative results: mean motif recall 0.826 (95% CI 0.78–0.87) on 25 literature-annotated pairs, against 0.49–0.66 for baselines. TP/TN separation is 3.36 across 71 test pairs.
  - No code link on the abstract page.
  — [arXiv](https://arxiv.org/abs/2608.25841)
- **Related drug-response models (not synergy).** These are useful templates for quantitative or directed explanation.
  - DRExplainer (arXiv:2408.12139): directed GCN with "quantifiable interpretability". — [arXiv](https://arxiv.org/pdf/2408.12139)
  - XGDP (Sci Rep 2025): explainable GNN for drug mechanism. — [Nature](https://www.nature.com/articles/s41598-024-83090-3)
- **MolecBioNet** (arXiv:2507.09173). Drug–drug interaction (DDI) model, not synergy. Combines knowledge graphs with molecular graphs and claims interpretability at both levels. — [arXiv](https://arxiv.org/pdf/2507.09173)

### Inferences
- The typical 2025 recipe is a cell-line-specific PPI subgraph plus a GNN plus attention or masks, followed by enrichment analysis and literature case studies. CASynergy is the clearest example. Novelty claims will have to go beyond this pattern.
- The CASynergy ablation (an AUC change of about 0.01) suggests the "causal" module adds little to accuracy. Its interpretive value is untested.

### Gaps
- I could not verify the code, splits or explanation validation for SynCell, DRUGSYNC, HyperSynergyX, DPASyn or PDTSyn beyond their abstracts.
- The search was not exhaustive. Further candidates may exist in Briefings in Bioinformatics, Bioinformatics and JCIM for 2025–2026. Searching each journal site directly is recommended.

## Q2. Reviews, surveys, and benchmark or reproducibility studies

### Takeaway
2025–2026 brought strong evidence against current synergy models. In SynVerse and in "One-hot news", one-hot drug and cell identity baselines match 16 or more published architectures. Shuffled features and rewired networks barely hurt performance. Under leave-drug-out and leave-cell-line-out splits, performance collapses. Synergy labels themselves are noisy and depend on the reference model chosen (Bliss, Loewe, ZIP or HSA). The review literature (npj Drug Discovery 2025 and AI Review 2024) largely does not address these problems.

### Cited Findings
- **SynVerse.** Tasnina N, Haghani M, Murali TM. *Brief Bioinform* 2025;26(6):bbaf676. Code: github.com/Murali-group/SynVerse; data: zenodo 15277144. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753315); preprint [bioRxiv](https://www.biorxiv.org/content/10.1101/2025.04.30.651516v1.full)
  - Evaluates 16 models built from 8 feature types (fingerprints, SMILES, molecular graphs, target profiles, expression, LINCS-978), 5 preprocessing methods (autoencoders, random walk with restart on PPI, foundation models) and GCN or Transformer encoders. Data are DrugComb with the CSS score, plus checks on Loewe scores and O'Neil.
  - Splits: leave-triplet, leave-pair, leave-drug and leave-cell-line.
  - On unseen pairs, PCC is 0.78–0.94, but no model is significantly better than a one-hot MLP baseline. The baseline scores 0.81 against MARSY's 0.84, and 0.88 against SynergyX's 0.91.
  - Shuffling drug or cell features has no significant effect.
  - With strength-preserving network rewiring, models keep much of their PCC. The authors conclude the models exploit per-drug synergy distributions.
  - Leave-drug and leave-cell-line performance is poor, with no model beating the baseline.
  - Recommendations: use leakage-aware splits, always include a one-hot baseline, and run shuffling and rewiring ablations. Current predictors are "not ready" for experimental use.
- **One-hot news.** Çandır EB, Kuru HI, Rattray M, Çiçek AE, Tastan O. *Bioinformatics* 2026;42(3):btag040. Code: github.com/tastanlab/ohe. — [OUP](https://academic.oup.com/bioinformatics/article/42/3/btag040/8440676); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13005728/)
  - Tests DeepSynergy, DeepDDS, MatchMaker, MARSY and JointSyn on O'Neil, DrugComb and NCI-ALMANAC.
  - Replacing features with one-hot vectors changes MSE by roughly −1% to +3%. MARSY improves by 6.4% with one-hot vectors.
  - Residual learning on top of the one-hot model gains nothing from biological features.
  - On DrugComb leave-drug-out, MatchMaker reaches only PCC 0.13 (one-hot 0.10).
  - On synthetic data, attribution recovers the true features when entities do not repeat (Jaccard ≈1.0), but not under the repeated drug–drug–cell triplet structure (Jaccard ≈0.2–0.4 for the nonlinear model). The authors blame the triplet formulation itself for shortcut learning.
  - Recommendations: one-hot, average and shuffled baselines; leave-cell-line-out, leave-one-drug-out and leave-drug-out splits; use models only to prioritise within a known panel.
- **Leakage-controlled cold-start benchmark.** *BMC Bioinformatics*, 2026, doi:10.1186/s12859-026-06665-z. Finds that standard splits partly measure memorization of entity-specific base rates and that cold-start performance is overstated. Argues cold-start results should be reported next to random or grouped splits. — [BMC](https://link.springer.com/article/10.1186/s12859-026-06665-z) [UNVERIFIED: page redirected to login and only the snippet was seen. Authors and numbers not retrieved. The snippet lists a 2026-10 date.]
- **Earlier baseline (2022).** Baptista et al., *PLoS Comput Biol* 2022, also used one-hot identifier baselines. — [PLOS CB](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1010200)
- **npj Drug Discovery review.** Li L, Zhang H, Zheng C, Su Y. "A review of deep learning approaches for drug synergy prediction in cancer." *npj Drug Discov* 2025;2:30, doi:10.1038/s44386-025-00034-1. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13267116/); [Nature](https://www.nature.com/articles/s44386-025-00034-1)
  - Organises models as single-task or multi-task.
  - Future directions it names: concentration-aware prediction and datasets, modelling drug–cell interaction, loss weighting in multi-task models, and new auxiliary tasks such as disease–target association and DTA.
  - It does not discuss leakage or split design, cold-start, or label noise. Interpretability is mentioned only in passing. These are the same authors as CASynergy.
- **GNN synergy review.** "A review on graph neural networks for predicting synergistic drug combinations." *Artificial Intelligence Review*, doi:10.1007/s10462-023-10669-z (2024). Compares GNN synergy models and datasets. — [Springer](https://link.springer.com/article/10.1007/s10462-023-10669-z) [Journal and year inferred from the DOI prefix and the user's description; not verified on the landing page]
- **Other overviews.**
  - "New methods for drug synergy prediction: a mini-review", arXiv:2404.02484. — [arXiv](https://arxiv.org/pdf/2404.02484)
  - GNN-for-drug-discovery survey, arXiv:2509.07887 (covers DeepDDS and SynerGNet). — [arXiv](https://arxiv.org/pdf/2509.07887)
- **Label noise and score reliability.**
  - A preprint analysing 391,652 DrugComb matrices finds Bliss and ZIP agree strongly (r=0.92), while Loewe agrees weakly with ZIP (r=0.28) and Bliss (r=0.33).
  - In 21–34% of matrices, one method calls synergy where another calls antagonism.
  - Existing scores come without p-values. The preprint proposes shape-constrained regression with a wild bootstrap.
  — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13060067/) [figures from the search summary; not verified in full text]
- **"How to predict effective drug combinations – moving beyond synergy scores."** bioRxiv 2024.11.22.624812, published in *iScience* 2025. Argues for predicting combination efficacy or sensitivity instead of synergy scores, which reproduce poorly. — [iScience](https://www.cell.com/iscience/fulltext/S2589-0042(25)00883-1); [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.11.22.624812v1.full) [UNVERIFIED: full text blocked by HTTP 429. Replicate correlation numbers not retrieved.]
- **DrugComb reproducibility claims.** Sources disagree. The first DrugComb release reported satisfactory replicate reproducibility, while later reviews note synergy scores are hard to reproduce across replicates. — (from the search summary for the sources above) [UNVERIFIED]
- **SynergyFinder 3.0.** Proposes a Bliss/Loewe consensus score. — [NAR](https://academic.oup.com/nar/article/50/W1/W739/6586861)

### Inferences
- Any new network-based synergy paper from 2026 on will likely be expected to include the following, and reviewers aware of SynVerse and One-hot news (published in BIB and Bioinformatics) will probably ask for them:
  - one-hot, average and shuffled baselines;
  - network-rewiring controls;
  - leave-drug and leave-cell-line splits.
- One-hot news shows feature attribution fails under triplet repetition even on synthetic data. Network-node attributions from synergy GNNs may therefore not reflect biology, which directly undermines the qualitative pathway-enrichment validation used by CASynergy and others.

### Gaps
- Exact numbers in the BMC cold-start benchmark were not retrieved.
- Replicate-level reproducibility figures for synergy scores versus sensitivity scores were not obtained. The iScience paper is the key source to read.

## Q3. Evidence on the identified gaps

### Takeaway
Most gaps remain open. Partial coverage:
- cell-line-specific networks: CASynergy and SynCell;
- dose-dependent prediction: DeepSynBa, with no network explanation;
- interaction-level attribution with quantitative evaluation: VINCENT, molecular motifs only.

I found no 2024–2026 synergy paper that combines predicted DTIs as seeds, a signed or directed signaling network, and quantitative explanation evaluation.

### Cited Findings
- **Gap 1. Cold-start drugs without known targets (predicted DTIs as network seeds).** Not addressed as far as I found.
  - SynVerse and One-hot news show leave-drug performance near baseline (PCC ≈0.10–0.13 on DrugComb leave-drug-out). — [One-hot news](https://pmc.ncbi.nlm.nih.gov/articles/PMC13005728/); [SynVerse](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753315)
  - CASynergy's drug cold-start test is on 21 drugs whose targets are known. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)
  - SynCell and DRUGSYNC claim gains on unseen drugs, but it is unclear whether those drugs have curated targets. — [SynCell](https://arxiv.org/abs/2511.17695); [DRUGSYNC](https://www.biorxiv.org/content/10.1101/2024.12.05.627115v1.full.pdf)
  - The npj review proposes drug–target affinity prediction only as an auxiliary task. — [npj](https://pmc.ncbi.nlm.nih.gov/articles/PMC13267116/)
  - Status: **open**.
- **Gap 2. Cell-line-specific or dynamic networks.** Partly addressed.
  - CASynergy builds a static Steiner-like PPI subgraph per cell line. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)
  - SynCell builds transcriptome-derived cell-line interactomes. — [arXiv](https://arxiv.org/abs/2511.17695)
  - PDTSyn treats cell lines as domains. — [BIB](https://academic.oup.com/bib/article/27/2/bbag199/8662206)
  - Missing: no dynamic networks (time- or perturbation-dependent) for synergy, and no work testing whether cell-specific networks beat one-hot cell identity. SynVerse found expression features fail under leave-cell-line splits. — [SynVerse](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753315)
  - Status: **partially addressed; robustness unproven**.
- **Gap 3. Directed or signed networks.** Older work exists, but I found no 2024–2026 deep learning synergy model using them.
  - 2021 bioRxiv: signalling flow on directed KEGG edges over a 1,584-gene cancer network. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2021.03.25.437003v1.full.pdf)
  - 2022 bioRxiv: OmniPath signed and directed network with CARNIVAL. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2022.08.28.505568v1.full)
  - Drug response, not synergy: DRExplainer uses a directed GCN. — [arXiv](https://arxiv.org/pdf/2408.12139)
  - Status: **open for deep learning and XAI synergy**. [Search was not exhaustive]
- **Gap 4. Dose-dependent explanation.**
  - DeepSynBa (bioRxiv Jan 2025, *Bioinformatics* 2026;42(7):btag416) predicts full dose–response matrices. Its interpretable layer holds response-surface parameters that separate efficacy from potency. It is tested on NCI-ALMANAC and O'Neil, including novel drugs and cell lines, but has no network or mechanism attribution. — [OUP](https://academic.oup.com/bioinformatics/article/42/7/btag416/8712837); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13341016/)
  - An uncertainty-aware dose-specific model (bioRxiv 2025.11.05.686895) predicts the dose–response surface with attention. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2025.11.05.686895v1.full)
  - ComplexMatrixComb (bioRxiv 2025.10.06.680642) predicts IC50 doses. — [bioRxiv](https://www.biorxiv.org/content/10.1101/2025.10.06.680642v1.full.pdf)
  - The npj review lists concentration-awareness as a future direction. — [npj](https://pmc.ncbi.nlm.nih.gov/articles/PMC13267116/)
  - Status: dose-aware *prediction* is emerging. Dose-dependent *network explanation* is **open**.
- **Gap 5. Interaction-level (non-additive) attribution.**
  - VINCENT (arXiv Aug 2026) gives motif-pair explanations validated by perturbation, at the molecular-substructure level only. — [arXiv](https://arxiv.org/abs/2608.25841)
  - Network models (CASynergy, SDCInterpreter) give node, edge or path importance per combination. They do not separate the joint pair-specific contribution from the sum of single-drug contributions. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)
  - Status: **open at the network or gene level**; partly addressed at the molecular level.
- **Gap 6. Quantitative evaluation of explanations.**
  - CASynergy: qualitative only (enrichment plus 14/100 literature hits). — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)
  - VINCENT: motif recall against literature annotations. — [arXiv](https://arxiv.org/abs/2608.25841)
  - One-hot news: synthetic ground-truth feature recovery (Jaccard), showing attribution fails with repeated entities. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13005728/)
  - SynVerse: shuffling and rewiring tests as model-level faithfulness checks. — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753315)
  - Status: **partially addressed; there is no standard benchmark** for network-explanation fidelity in synergy.

### Inferences
- The most defensible thesis contribution combines several of these gaps:
  - a network-based explainer evaluated on synthetic networks with known ground-truth synergy mechanisms;
  - one-hot, shuffle and rewiring controls;
  - leave-drug-out splits;
  - predicted-DTI seeds for target-less drugs.
- One-hot news's synthetic-recovery design is a direct, citable template for evaluating explanations quantitatively.
- Explanations should be checked against rewired-network controls. If an explanation survives degree-preserving rewiring, it is probably not biological.

### Gaps
- I did not verify whether SynCell or DRUGSYNC use predicted DTIs.
- I did not search for 2024–2026 work on Shapley interaction indices or other non-additive attribution in synergy GNNs specifically.

## Q4. Venues and reviewer expectations

### Takeaway
Recent benchmark and model papers in this space appear in the following venues:
- *Briefings in Bioinformatics*: SynVerse, PDTSyn, SynergyX
- *Bioinformatics*: One-hot news, DeepSynBa
- *PLOS Computational Biology*: CASynergy
- *JCIM*: SDCInterpreter
- *IEEE JBHI*: HyperSynergyX
- *BMC Bioinformatics*: cold-start benchmark
- *Frontiers in Pharmacology*, *Sci Rep*, *J Transl Med*: MD-Syn, SynergyGraph, KGLGANSynergy

Expectations are rising. Leakage-aware or cold-start splits, a one-hot baseline, ablations and code release are becoming standard.

### Cited Findings
- Venue examples:
  - BIB: SynVerse, BIB 2025 — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753315); PDTSyn, BIB 2026 — [OUP](https://academic.oup.com/bib/article/27/2/bbag199/8662206); SynergyX, BIB 2024 — [OUP](https://academic.oup.com/bib/article/25/2/bbae015/7604885)
  - Bioinformatics: One-hot news, 2026 — [OUP](https://academic.oup.com/bioinformatics/article/42/3/btag040/8440676); DeepSynBa, 2026 — [OUP](https://academic.oup.com/bioinformatics/article/42/7/btag416/8712837)
  - PLOS CB: CASynergy, 2025 — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)
  - JCIM: SDCInterpreter, 2025 — [ACS](https://pubs.acs.org/doi/10.1021/acs.jcim.5c02569)
  - JBHI: HyperSynergyX, 2026 — [DOI](https://doi.org/10.1109/jbhi.2026.3673550)
  - BMC Bioinformatics: cold-start benchmark, 2026 — [BMC](https://link.springer.com/article/10.1186/s12859-026-06665-z)
- Explicit field recommendations that reviewers can cite:
  - avoid random triplet splits;
  - use leave-drug and leave-cell-line splits;
  - always compare against a one-hot MLP;
  - run module, shuffle and rewiring ablations.
  — [SynVerse](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753315); [One-hot news](https://pmc.ncbi.nlm.nih.gov/articles/PMC13005728/)
- Report cold-start results alongside random or grouped splits. — [BMC](https://link.springer.com/article/10.1186/s12859-026-06665-z) [UNVERIFIED snippet]
- Common practice in the model papers reviewed:
  - multiple datasets (O'Neil, DrugComb, DrugCombDB, NCI-ALMANAC);
  - cold-start splits;
  - literature case studies;
  - public GitHub code (CASynergy, SynVerse and One-hot news all release code).
  — [CASynergy](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)

### Inferences
- The following are my inferences, not from a source that states reviewer policy:
  - BIB and Bioinformatics reviewers now likely expect the SynVerse and One-hot news controls.
  - PLOS CB favours biological insight plus code.
  - JCIM accepts chemistry- or path-centric interpretability.
  - TCBB, JBHI and BMC Bioinformatics are more tolerant of incremental architectures.
- For conferences (ISMB/RECOMB proceedings in Bioinformatics, BIBM, ACM-BCB, NeurIPS or ICML workshops on ML for drug discovery or XAI), novelty in the explanation method plus quantitative faithfulness metrics would likely matter more than a biological case study. [INFERENCE; not sourced]
- External validation would strengthen a submission. Options include training on one dataset and testing on another (for example O'Neil → ALMANAC), held-out drugs, or a small wet-lab set. [INFERENCE]

### Gaps
- I found no published reviewer guidelines specific to synergy papers at these venues. The expectations above are inferred from recent papers' recommendations.
- I did not survey ISMB, RECOMB, BIBM, ACM-BCB or NeurIPS workshop proceedings for 2025–2026 synergy-XAI papers. This needs targeted searches (for example DBLP or the conference program pages).
