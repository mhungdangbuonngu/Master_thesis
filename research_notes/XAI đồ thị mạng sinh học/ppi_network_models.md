# Group 3 – Graph & Network-Path XAI (PPI / signaling-network-centric drug synergy models), 2019–2026

Verification legend used below:
- **[FT]** = details taken from the paper's full text (journal HTML / Europe PMC full-text XML).
- **[ABS]** = only the abstract / bibliographic record was readable; details not checked against the full text.
- **[SEC]** = only a secondary source (third-party summary or comparison table) was available. Treat as unverified.

Several full texts were blocked during this session (PMC returned a bot-check page, MDPI and HKU returned 403, nature.com redirected to login, and bioRxiv returned 429). Where that happened I used Europe PMC full-text XML instead, or flagged the gap.

---

## Q1. Theoretical foundation: Cheng, Kovács & Barabási 2019, "Network-based prediction of drug combinations"

### Takeaway
This paper is verified as Nat Commun 10:1197 (2019). It introduced the separation score s_AB and six "exposure" classes. Only "Complementary Exposure" correlated with therapeutic effect: the two drugs' target modules both hit the disease module but sit in separate network neighbourhoods. Validation was retrospective only (approved combinations and literature), with no new experiments.

### Cited Findings
- **Citation [FT]:** Feixiong Cheng, István A. Kovács, Albert-László Barabási. *Nature Communications* 10(1):1197, March 2019. DOI 10.1038/s41467-019-09186-x. PMCID PMC6416394, PMID 30867426. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41467-019-09186-x&resultType=core&format=json)
- **Separation score [FT]:** s_AB is the mean shortest-path distance between the targets of A and B, minus the average of each drug's within-set mean distance, i.e. s_AB = ⟨d_AB⟩ − (⟨d_AA⟩+⟨d_BB⟩)/2. s_AB < 0 means the target modules overlap; s_AB ≥ 0 means they are topologically separated. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- **Drug–disease proximity [FT]:** z = (d − μ)/σ against degree-matched random sets. The z-score did not separate approved drug pairs from random pairs, so s_AB was used for drug–drug relations. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- **Six classes [FT]:** P1 Overlapping, P2 Complementary, P3 Indirect, P4 Single, P5 Non-exposure, P6 Independent Action. Only P2 was significant for efficacy in hypertension and cancer (P < 1.0×10⁻⁴, permutation test). Overlapping Exposure (P1) was significantly associated with adverse effects. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- **Network resources [FT]:**
  - Interactome: 243,603 physical PPIs among 16,677 proteins, from 15 databases.
  - Drug targets: DrugBank v4.3, TTD, PharmGKB, ChEMBL v20, BindingDB and IUPHAR, with affinity ≤10 µM; 1,978 drugs have ≥2 targets.
  - Disease genes: 8 resources.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- **Data and results [FT]:**
  - 681 pairwise combinations involving 362 drugs.
  - 13,397 DrugBank DDIs plus TWOSIDES cardiovascular events.
  - Network prediction of approved antihypertensive combinations: AUC 0.589 ± 0.002, vs 0.489 for a chemoinformatics baseline and 0.529 for a bioinformatics baseline.
  - For hydrochlorothiazide, 21 of 30 predicted partners (70%) had existing support.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- **Validation type [FT]:** Retrospective comparison with approved, clinical-trial and preclinical evidence. The authors state that experimental and prospective validation are still needed. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- **Limitations [FT]:** Selection bias in tested combinations; no dose information; pairs only; adverse effects also occur under P2; incomplete interactome and target data; tested only on hypertension and cancer. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- **Code [FT]:** Proximity code is at github.com/emreg00/toolbox; other code is available on request. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)
- The GraphSynergy repository links its PPI and drug–protein data to this Nat Commun paper, so GraphSynergy reuses the Cheng et al. interactome. — [GitHub JasonJYang/GraphSynergy](https://github.com/JasonJYang/GraphSynergy)

### Inferences
- This is not a learning model. It is a hand-crafted topological explanation (separation plus disease-module overlap), and later deep models (GraphSynergy, and the "shortest-path between targets" analysis in DeepSignalingFlow) operationalise it.
- The low AUC (0.589) shows the principle is explanatory more than strongly predictive. That is a useful framing for a thesis: network topology serves as a prior or explanation, not as a standalone predictor.

### Gaps
- I did not see the exact count of cancer combinations; it is in Supplementary Data 3.

---

## Q2. TranSynergy (Liu & Xie, PLOS Comput Biol 2021)

### Takeaway
Verified. The model uses RWR-propagated drug-target profiles on STRING plus a self-attention transformer over genes. Gene-level explanations come from SHAP, and pathway-level explanations from GSEA run on the Shapley-ranked genes (SA-GSEA). Explanations were validated by literature-backed case studies only. Code is public.

### Cited Findings
- **Citation:** Qiao Liu, Lei Xie. "TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations." *PLOS Comput Biol* 17(2):e1008653, 12 Feb 2021. DOI 10.1371/journal.pcbi.1008653. bioRxiv preprint 10.1101/2020.07.08.193904. — [DOAJ / search summary](https://doaj.org/article/8d64a5139d704774bae342cc957fb3ce); [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.07.08.193904v1.full.pdf)
- **Data [FT]:**
  - Merck O'Neil screen, preprocessed following DeepSynergy: 36 drugs, 35 cell lines, 523 pairs, 18,553 data points.
  - Regression on synergy score. For classification metrics, synergy > 30 is labelled positive.
  - Sources: [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Splits [FT]:**
  - Leave-drug-combination-out: nested 5-fold CV.
  - Leave-cell-line-out: affinity-propagation clusters of cell lines; train on the largest cluster (28 lines).
  - Leave-drug-out: drug clusters.
  - Sources: [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Resources [FT]:**
  - PPI: STRING, with confidence scores as edge weights.
  - Targets: DrugBank (5.0) and ChEMBL.
  - Cell-line features: DepMap gene dependency (Achilles + Sanger CRISPR, MICE-imputed) and Harmonizome (CCLE/GDSC) expression.
  - Sources: [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Architecture [FT]:**
  - RWR on STRING propagates each drug's target vector, with α = 0.5 chosen by grid search.
  - Each input is a 2,401-gene vector per entity (drug A, drug B, cell line), reduced to 512 dimensions by one layer.
  - A scaled dot-product self-attention transformer runs without positional encoding, followed by a fully connected regressor.
  - Sources: [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Explanation method (SA-GSEA) [FT]:** SHAP GradientExplainer and DeepExplainer compute per-gene Shapley values, with a k-means background and an average over 10 runs. Cell-line genes are ranked by Shapley value and GSEA is run on that ranked list. — [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Explanation validation [FT]:** Case studies only: 7 high-scoring, correctly predicted samples from T47D, CAOV3 and MSTO-211H, linked to the literature. The authors say firmer conclusions "might require additional experimental evidence." — [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Performance [FT], leave-combo-out vs DeepSynergy:**
  - MSE 232, significantly lower (p < 0.001).
  - Pearson about +3%, Spearman about +5%, PR-AUC +5.6%, ROC-AUC only slightly higher.
  - Leave-cell-out and leave-drug-out scores were lower but still beat DeepSynergy.
  - Per-tissue Pearson ranged from 0.66 (prostate) to 0.79 (ovarian).
  - The authors predicted new ovarian cancer combinations.
  - Sources: [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Limitations [FT]:**
  - A small gene set (drug targets plus cancer genes).
  - Weaker cold-start performance.
  - Drugs without known targets are poorly represented.
  - No mutation or CNV features.
  - Synergy scores are not harmonised across methods.
  - The authors explicitly say attention weights may not explain predictions, which is why they use SHAP instead.
  - Mechanistic interpretations are hypotheses.
  - Sources: [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)
- **Code:** https://github.com/qiaoliuhub/drug_combination — [PLOS full text](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)

### Inferences
- The synergy score is most likely Loewe, since the paper follows DeepSynergy preprocessing and DeepSynergy used Loewe via Combenefit. The part of the paper I read did not name it explicitly.
- The authors' own statement that "attention is not explanation" is a citable argument for thesis work that compares attention-based and attribution-based explanations.

### Gaps
- I did not confirm which gene-set library SA-GSEA uses (the brief says Reactome). The fetched first ~100k characters did not mention Reactome, and the last ~14k characters (Methods tail / supplement) were not read.
- STRING version not stated in the part I read.

---

## Q3. GraphSynergy (Yang et al. 2021) – venue check: **JAMIA, not Bioinformatics**

### Takeaway
Confirmed as *JAMIA* 28(11):2336–2345 (2021). It is a spatial GCN on the Cheng et al. PPI network that embeds drug-target modules and cell-line protein modules, combines a "therapy score" and a "toxicity score" into a synergy probability, and uses attention over proteins for interpretation. The full text is paywalled, so only abstract-level and secondary details could be checked.

### Cited Findings
- **Citation [ABS]:** Jiannan Yang, Zhongzhi Xu, William Ka Kei Wu, Qian Chu, Qingpeng Zhang. "GraphSynergy: a network-inspired deep learning model for anticancer drug combination prediction." *J Am Med Inform Assoc* 28(11):2336–2345, Oct 2021. DOI 10.1093/jamia/ocab162, PMID 34472609, PMCID PMC8510276. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC8075535%20OR%20PMCID:PMC8510276&resultType=core&format=json)
- **Erratum:** An erratum exists, DOI 10.1093/jamia/ocab214. — [OUP JAMIA page](https://academic.oup.com/jamia/article/28/11/2336/6362567)
- **Method [ABS]:** A spatial-based GCN on the PPI network encodes the protein modules targeted by the drug pair and those associated with the cell line. Therapy and toxicity scores assess pharmacological effects, and an attention component captures pivotal proteins. — [OUP JAMIA page](https://academic.oup.com/jamia/article/28/11/2336/6362567)
- **Performance [ABS]:** ACC 0.7553 on DrugCombDB (+11.94% vs DeepSynergy) and 0.7557 on Oncology-Screen (+10.95%). — [OUP JAMIA page](https://academic.oup.com/jamia/article/28/11/2336/6362567)
- **Explanation [ABS]:** Proteins given high contribution weights are associated with molecular functions and processes such as transcription and transcription regulation. — [OUP JAMIA page](https://academic.oup.com/jamia/article/28/11/2336/6362567)
- **Resources (repo):**
  - PPI and drug–protein associations come from the Cheng et al. 2019 Nat Commun interactome.
  - Cell–protein associations come from CCLE via Harmonizome.
  - Datasets: DrugCombDB and Oncology-Screen.
  - Code: https://github.com/JasonJYang/GraphSynergy
  - Sources: [GitHub](https://github.com/JasonJYang/GraphSynergy)
- **Press release:** City University of Hong Kong issued one; Qingpeng Zhang is the corresponding author. — [CityU news](https://www.cityu.edu.hk/en/research/stories/2021/12/02/using-ai-accurately-predicting-synergistic-cancer-drug-combinations)
- **[SEC] secondary-summary details (unverified):**
  - The therapy and toxicity scores are combined through a sigmoid into a synergy probability.
  - Seven baselines: Network Proximity, GraRep, DeepWalk, Node2Vec, DeepSynergy, GCN, KGNN.
  - A 2-hop receptive field worked best.
  - A NSCLC case study suggested Pemetrexed + Gefitinib.
  - This summary also wrongly cites the paper as "Jiang et al., 2021, Nature Machine Intelligence." That is an error; the correct venue is JAMIA.
  - Sources: [BestHub summary](https://besthub.dev/articles/graphsynergy-a-network-inspired-deep-learning-model-for-predicting-anti-cancer-drug-combinations-eefd2fcf6d43)

### Inferences
- The toxicity score appears to operationalise Cheng et al.'s observation that overlapping exposure links to adverse effects. This is inferred from the design, not confirmed from the formulas.
- Explanation validation appears to be qualitative (functional annotation of high-attention proteins plus a case study), with no quantitative faithfulness test. This rests on the abstract and the secondary source.

### Gaps
- Exact therapy and toxicity score formulas, synergy-score type and threshold for classification labels, dataset sizes, split protocol (likely random), AUC values, and stated limitations could not be verified. The full text is paywalled, and Europe PMC full-text XML returned HTTP 500.

---

## Q4. Fuhai Li lab signaling-network family: DeepSignalingSynergy → IDSP → SANEpool → DeepSignalingFlow

### Takeaway
This is one lab's line of work (Washington University in St. Louis, Fuhai Li). All four models build graphs from about 46–48 KEGG core cancer signaling pathways plus DrugBank drug-gene edges, train on NCI ALMANAC (later also O'Neil, DrugComb and DrugCombDB), and derive explanations from learned edge weights or attention pooling. Validation is mostly statistical (selection-frequency KS tests; top-10 vs bottom-10 F-tests) plus visualisation, with little literature or wet-lab validation.

### Cited Findings
**DeepSignalingSynergy**
- **Citation [ABS]:** Heming Zhang, Jiarui Feng, Amanda Zeng, Philip Payne, Fuhai Li. "Predicting Tumor Cell Response to Synergistic Drug Combinations Using a Novel Simplified Deep Learning Model." *AMIA Annu Symp Proc* 2020:1364–1372 (epub 25 Jan 2021). PMID 33936513, PMC8075535. bioRxiv 10.1101/2020.04.10.036491. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC8075535%20OR%20PMCID:PMC8510276&resultType=core&format=json); [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.04.10.036491.full.pdf)
- **Inputs [ABS / SEC snippet]:** 46 signaling pathways (45 signaling plus cell cycle) on NCI ALMANAC. 21 drugs with DrugBank targets on the pathway genes were kept. Pathway-layer outputs feed a densely connected DBN that outputs a synergy score. — [bioRxiv snippet](https://www.biorxiv.org/content/10.1101/2020.04.10.036491.full.pdf)
- **[SEC] interpretability and numbers:** A third-party comparison table says it used iNNvestigate to extract layer-wise importance of pathways and genes, with Pearson 0.40 and AUC 0.93. Unverified. — [search result, PMC8075535-related](https://pmc.ncbi.nlm.nih.gov/articles/PMC8075535)

**IDSP (Interpretable Deep Signaling Pathways)**
- **Citation [ABS]:** Zehao Dong, Heming Zhang, Yixin Chen, Fuhai Li. "Interpretable Drug Synergy Prediction with Graph Neural Networks for Human-AI Collaboration in Healthcare." arXiv:2105.07082 (cs.LG), 14 May 2021. Only v1 exists, and no journal reference is listed. — [arXiv](https://arxiv.org/abs/2105.07082)
- **Method [ABS]:**
  - A GNN on gene-gene and gene-drug regulatory relations from 46 core cancer signaling pathways, using NCI ALMANAC.
  - An MLP learns edge weights from node relations, with inductive aggregation.
  - Important signaling interactions are read from the learned edge weights.
  - Tested transductively and inductively (unseen genes or pathways), with no drug chemical features.
  - Reports "highly comparable performance" with SOTA but gives no numbers in the abstract, and different salient signaling patterns per cell line.
  - No code link.
  - Sources: [arXiv](https://arxiv.org/abs/2105.07082)

**SANEpool**
- **Citation [FT via Europe PMC XML]:** Zehao Dong, Heming Zhang, Yixin Chen, Philip R. O. Payne, Fuhai Li. "Interpreting the Mechanism of Synergism for Drug Combinations Using Attention-Based Hierarchical Graph Pooling." *Cancers (Basel)* 15(17):4210, Aug 2023. DOI 10.3390/cancers15174210, PMID 37686486, PMC10486573. arXiv preprint 2209.09245. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.3390/cancers15174210&resultType=core&format=json); [arXiv](https://arxiv.org/abs/2209.09245)
- **Setup [FT]:** Regression of a continuous synergy score (the average ComboScore across doses), evaluated inductively with unseen drug pairs and 5-fold CV. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10486573/fullTextXML)
- **Datasets [FT]:**
  - NCI-DCD (NCI ALMANAC): 5,658 graphs, 1,364 genes, about 25k edges, 46 KEGG pathways.
  - O'Neil-DCD: 4,637 graphs, 1,823 genes.
  - GDSC-SDD (single-drug): 16,761 graphs, 969 genes.
  - Node features: CCLE expression. Drug-gene edges: DrugBank 5.1.5. Gene-gene edges: KEGG.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10486573/fullTextXML)
- **Architecture [FT]:**
  - 2 GCN layers and 2 SANEpool layers. Node attention is a cosine score against a trainable vector, with top-k selection (200 nodes in the last layer, 90% of edges kept). Trainable edge weights are applied by Hadamard product.
  - A Decagon-style, drug-order-invariant decoder produces the output.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10486573/fullTextXML)
- **Explanation and validation [FT]:**
  - Per cell line, a gene's "synergic" and "non-synergic" importance is the frequency with which SANEpool selects it.
  - KS tests show the two distributions differ significantly in every cell line.
  - Outputs: heatmaps (SF-295, K-562), a K-562 top-10 gene list, and subnetwork visualisations.
  - No enrichment analysis or wet-lab check appeared in the part I read.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10486573/fullTextXML)
- **Performance [FT], Pearson (error):**
  - NCI-DCD: 0.656 (MSE 44.35) vs TranSynergy 0.644 and DeepSignalingSynergy 0.631.
  - GDSC-SDD: 0.825 vs TranSynergy 0.794.
  - O'Neil-DCD: 0.614 vs TranSynergy 0.615, so TranSynergy is marked best here. The abstract's claim of best performance on all datasets is not fully supported.
  - The error column is labelled RMSE in parts of the table, which looks inconsistent.
  - Other baselines: DeepSynergy, GCN, GIN, GAT, DAGNN, SAGPool, DiffPool.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10486573/fullTextXML)
- **Limitations [FT]:** Limited numbers of drug combinations and cell lines; more multi-omics planned. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10486573/fullTextXML)

**DeepSignalingFlow**
- **Citation [FT via Europe PMC XML]:** Heming Zhang, Yixin Chen, Philip Payne, Fuhai Li. "Using DeepSignalingFlow to mine signaling flows interpreting mechanism of synergy of cocktails." *npj Syst Biol Appl* 10(1):92, 21 Aug 2024. DOI 10.1038/s41540-024-00421-w, PMC11339460. bioRxiv 2021: "Mining signaling flow to interpret mechanisms of synergy of drug combinations using deep graph neural networks," 10.1101/2021.03.25.437003. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41540-024-00421-w&resultType=core&format=json); [bioRxiv](https://www.biorxiv.org/content/10.1101/2021.03.25.437003.full.pdf)
- **Data and resources [FT]:**
  - NCI ALMANAC (2,788 points), O'Neil (1,008), DrugComb (27,781), DrugCombDB (21,399).
  - 5-fold CV.
  - 48 KEGG core cancer signaling pathways covering 2,016 genes, with directed adjacency; DrugBank targets.
  - RNA-seq and CNV from Cell Model Passports.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11339460/fullTextXML)
- **Architecture [FT]:** A weighted bi-directional GNN (WeB-GNN/GCN) with separate trainable weight matrices for upstream→downstream and downstream→upstream message passing, 3 layers, and a decoder. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11339460/fullTextXML)
- **Explanation [FT]:**
  - Learned flow matrices are averaged over the 5 folds. A gene's weighted degree, scaled by its RNA-seq value, gives a cell-line-specific degree.
  - A core subnetwork is built by thresholding degree and dropping edges with weight < 0.1.
  - For each combination, edge weights are summed along shortest paths (length < 5) between the two drugs' targets.
  - Top-10 and bottom-10 combinations per cell line are compared with F-tests: 21 of 41 cell lines had higher mean and median path weight for the top-10, with p < 0.1.
  - Example subnetworks for T-47D and PC-3 (88 genes each).
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11339460/fullTextXML)
- **Performance [FT], Pearson, 5-fold:**
  - NCI ALMANAC 63.75 ± 1.58%, O'Neil 65.81 ± 2.83%, DrugComb 63.68 ± 0.92%, DrugCombDB 61.51 ± 0.64%.
  - These beat GCN, GIN, GAT, GraphFormer and MixHop; for example GCN scored 44.88% on ALMANAC.
  - Sources: [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11339460/fullTextXML)
- **Limitations [FT]:** Pan-cancer only; a limited set of KEGG pathways and targets; KEGG edge types unused; new pairs constrained by training data; described as exploratory. — [Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11339460/fullTextXML)
- **Code:** https://github.com/FuhaiLiAiLab/DeepSignalingFlow — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41540-024-00421-w&resultType=core&format=json)

### Inferences
- The DeepSignalingFlow "shortest-path weight between the two drugs' targets" analysis is a learned counterpart of Cheng's s_AB. It is a natural bridge between network-medicine theory and GNN XAI.
- Validation in this family is weak. The statistical tests (KS on selection frequency, F-test with p < 0.1 in only 21 of 41 cell lines) show that the explanations differ between classes, not that they are faithful to the model or biologically correct. No fidelity, sparsity or ground-truth benchmark is reported, which is a clear gap a thesis could fill.

### Gaps
- IDSP: only the abstract was seen. No numbers, no code, no peer-reviewed version found; it seems superseded by SANEpool.
- DeepSignalingSynergy: the full text was not read (bioRxiv 429; Europe PMC full text 500). The iNNvestigate method and the Pearson/AUC numbers are from a secondary table only.
- DeepSignalingFlow: the synergy-score type (probably the ALMANAC ComboScore or a DrugComb score) and MSE were not stated in the sections I read.
- SANEpool: the code link sits in the unread tail of the paper.

---

## Q5. Other PPI / pathway-propagation synergy models with interpretability (PathSynergy, SynerGNet, DIPx, SynPathy, others)

### Takeaway
- **PathSynergy (BIB 2025)** is verified, but it is a pathway-map plus CNN model with GAT on drug molecular graphs. It is not PPI-propagation, and its explanations are gradients over MSigDB C2 pathways. Notably, it includes wet-lab validation in liver cancer.
- **SynerGNet (Biomolecules 2024)** is a PPI-graph GNN with **no explanation method**.
- **DIPx (eLife 2025)** is a pathway-activation random forest with permutation importance.
- **SynPathy (Mol Cancer Res 2022)** uses PPI proximity of drug-associated pathways, but only its abstract was checked.

### Cited Findings
**PathSynergy**
- **Citation [FT]:** Fengyue Zhang†, Xuqi Zhao† (equal contribution), Jinrui Wei, Lichuan Wu*. "PathSynergy: a deep learning model for predicting drug synergy in liver cancer." *Briefings in Bioinformatics* 26(2):bbaf192, March 2025 (published 24 Apr 2025). DOI 10.1093/bib/bbaf192. — [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Setup [FT]:** Binary classification. Synergy score > 10 is positive and < 0 negative; pairs in between are excluded. The score type was not given in the extract. — [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Data [FT]:**
  - O'Neil, filtered to 29 cell lines, 28 drugs and 6,271 combinations.
  - 5-fold CV with seed 42; random splits only.
  - External test: 1,252 DrugCombDB pairs (95 drugs, 62 cell lines).
  - CCLE TPM expression, DrugBank targets, MSigDB C2 (3,090 pathways), TCGA-LIHC.
  - Sources: [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Architecture [FT]:**
  - model_a: a GAT (10 heads) on RDKit drug graphs plus an MLP on cell lines.
  - model_b: pathways clustered with K-means (K = 3), reduced by PCA, placed on a 2D "pathway map," then classified by a CNN.
  - The two are fused with a learnable weighting parameter.
  - No PPI network is used.
  - Sources: [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Explanation and validation [FT]:**
  - Pathway contributions come from gradients through the trained weights.
  - Case study: sorafenib + trametinib, top-20 pathways discussed against the literature.
  - Wet lab: six FDA-approved drugs were predicted to synergise with sorafenib or lenvatinib and tested with CCK-8 and Chou–Talalay CI; colony formation and transwell assays were run for pimecrolimus + sorafenib.
  - The pathway attributions themselves were not validated experimentally.
  - Sources: [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Performance [FT]:**
  - 5-fold CV: ACC 0.95, ROC-AUC 0.98, PR-AUC 0.97, F1 0.92.
  - External DrugCombDB: ACC 0.83, ROC-AUC 0.81, F1 0.80. MGAE-DC had a higher ROC-AUC (0.89) there.
  - Sources: [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Limitations [FT]:** Small training set; CV-to-external performance drop; one-dimensional shared-gene pathway similarity; PCA information loss; in vitro only, in 4 liver cancer lines. — [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Code:** https://github.com/ZhangFengyuea300/PathSynergy — [OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)
- **Possible confusion:** A dblp record (journals/bib/ZhangZWW24) lists a BIB paper by the same authors. It may be the same work with a different year label; this was not resolved. — [dblp](https://dblp.org/rec/journals/bib/ZhangZWW24)

**SynerGNet**
- **Citation [FT]:** Mengmeng Liu, Gopal Srivastava, J. Ramanujam, Michal Brylinski. "SynerGNet: A Graph Neural Network Model to Predict Anticancer Drug Synergy." *Biomolecules* 14(3):253, 21 Feb 2024. DOI 10.3390/biom14030253, PMID 38540674, PMC10967862. — [PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/)
- **Setup and data [FT]:**
  - Binary synergistic vs antagonistic classification on AZ-DREAM: 3,272 pairs, augmented to 2.3M instances.
  - External test: 55 DrugCombDB instances.
  - 5-fold random CV; no leave-drug-out or leave-cell-out.
  - Score type and threshold not stated.
  - Sources: [PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/)
- **Resources and architecture [FT]:**
  - PPI from IHP-PING (STRING, BioGRID, DIP, HPRD, IntAct, MINT, MIPS, UniProt), confidence ≥ 0.7, 18,997 nodes.
  - Node features: CCLE expression, CNV, mutations, STITCH drug-protein scores, GO embeddings (218 dimensions).
  - Two GENConv layers, JK-Net, max/mean pooling.
  - Knowledge-based graph reduction by edge contraction.
  - Sources: [PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/)
- **Interpretability [FT]:** None described. — [PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/)
- **Performance [FT]:**
  - With augmentation: AUC 0.790, BAC 0.734 (BAC 0.676 without).
  - DrugCombDB external: AUC 0.748, BAC 0.633, but FPR 0.735.
  - Sources: [PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/)
- **Code:** https://github.com/MengLiu90/SynerGNet — [PMC/NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/)

**DIPx – venue verified as eLife**
- **Citation [FT]:** Quang Thinh Trac, Yue Huang, Tom Erkers, …, Yudi Pawitan, Trung Nghia Vu. "Pathway activation model for personalized prediction of drug synergy." *eLife* 13:RP100071 (Version of Record 3 June 2025; reviewed preprint 2024). DOI 10.7554/eLife.100071. — [eLife](https://elifesciences.org/articles/100071)
- **Setup [FT]:** Loewe score computed with Combenefit; ≥ 20 counts as highly synergistic. A random forest regressor predicts the score, with a bootstrap confidence score. — [eLife](https://elifesciences.org/articles/100071)
- **Data and splits [FT]:**
  - AZ-DREAM: 75 cell lines, 903 combinations. Test Set 1 has combinations seen in training; Test Set 2 has unseen combinations, effectively leave-combo-out.
  - O'Neil external set: 29 cell lines, 583 combinations.
  - Sources: [eLife](https://elifesciences.org/articles/100071)
- **Features [FT]:**
  - 4,762 MSigDB v6.2 pathways.
  - Pathway activation scores (PAS) built from the summed expression of upstream/target, downstream and driver-gene subsets: 14,286 features.
  - Targets from AZS, DrugBank and ChEMBL.
  - Sources: [eLife](https://elifesciences.org/articles/100071)
- **Explanation [FT]:**
  - Permutation feature importance plus median PAS.
  - Network enrichment analysis (NEA) z-scores on a gene network, which PAS predicts with Spearman 0.46.
  - Literature case checks (e.g., ERBB2 for capivasertib + sapitinib).
  - No experimental validation of the pathways.
  - Sources: [eLife](https://elifesciences.org/articles/100071)
- **Performance [FT], Spearman:**
  - Test 1: 0.50 vs TAIJI-M 0.38.
  - Test 2: 0.26 vs 0.18, not statistically significant.
  - O'Neil with both drugs unseen: 0.09.
  - Sources: [eLife](https://elifesciences.org/articles/100071)
- **Code:** https://www.github.com/tracquangthinh/DIPx — [eLife](https://elifesciences.org/articles/100071)

**SynPathy**
- **Citation [ABS]:** Yi-Ching Tang, Assaf Gottlieb. "SynPathy: Predicting Drug Synergy through Drug-Associated Pathways Using Deep Learning." *Mol Cancer Res* 20(5):762–769, 2022. DOI 10.1158/1541-7786.MCR-21-0735, PMID 35046110. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41540-024-00421-w%20OR%20DOI:10.1158/1541-7786.MCR-21-0735&resultType=core&format=json)
- **Abstract findings [ABS]:** MSE 70.6 ± 6.4; suggests candidate pathways explaining predictions. Pairs are more synergistic when their top contributing pathways are closer on the protein interaction network. — [Europe PMC record](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1158/1541-7786.MCR-21-0735&resultType=core&format=json)
- **Feature construction (described by DIPx):** SynPathy computes pathway enrichment scores from the PPI distance between each drug's targets and the pathway genes. — [eLife DIPx](https://elifesciences.org/articles/100071v1)
- **Data:** An AACR figshare data collection exists. — [AACR figshare](https://aacr.figshare.com/collections/Data_from_SynPathy_Predicting_Drug_Synergy_through_Drug-Associated_Pathways_Using_Deep_Learning/6545396)

**Other candidates surfaced (not verified)**
- **DGSSynADR** (*Bioinformatics* 2023, btad607): heterogeneous graph of drug-drug, drug-target and PPI edges, claimed biologically interpretable. — [dbpia mirror](https://dbpia.nl.go.kr/bioinformatics/article/39/10/btad607/7301437)
- **SynergyGTN** (*Sci Rep* 2025): graph transformer that integrates PPI information "to improve biological interpretability". — [search summary via Nature](https://www.nature.com/articles/s41598-025-12936-1)
- **TAG-CP** (*Expert Syst Appl* 2025): maps targets onto an IntAct PPI and reports that synergistic pairs' targets are typically within 1–2 intermediates. — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0957417425001885)
- **Review:** A 2024 mini-review by Abbasi & Rousu covers PPI/target-based synergy methods. — [Aalto PDF](https://acris.aalto.fi/ws/portalfiles/portal/145900356/New_methods_for_drug_synergy_prediction_-_A_mini-review.pdf)

### Inferences
- Across the verified papers, only PathSynergy did any wet-lab work, and it validated predicted combinations, not explanations. No paper in this group measures explanation faithfulness quantitatively (deletion/insertion, fidelity, ground-truth subnetworks).
- Split rigour varies. TranSynergy is the only verified model with leave-drug-out and leave-cell-out. SANEpool, DeepSignalingFlow, PathSynergy and SynerGNet use (random) 5-fold CV. DIPx uses a seen vs unseen combination split.
- "PPI-centric" really covers two groups: genome-wide PPIs (Cheng interactome, STRING, IHP-PING) in GraphSynergy, TranSynergy, SynerGNet and SynPathy, and curated KEGG signaling subgraphs of about 1.3k–2k genes in the Fuhai Li family. The second group is smaller and directed, which makes subnetwork explanations more readable.

### Gaps
- NetSyn and PathDNN were not searched within the tool budget. I did not confirm that they exist as synergy models or whether they are relevant.
- DGSSynADR, SynergyGTN and TAG-CP were seen only in search snippets: no citation details or XAI details verified.
- No 2026 papers were found in this session. A dedicated search (e.g., PubMed for "drug synergy" AND "protein interaction" AND explainable, 2025–2026) is still needed.
