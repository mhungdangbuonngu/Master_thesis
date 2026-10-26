# Peer Review Package — Simulated Journal Review Panel

**Manuscript**: *Explainable Graph Neural Networks for Drug Response and Drug Synergy Prediction: A Literature Review*
**File under review**: `literature_review.md` (243 lines, ~36 references, thesis-chapter length)
**Translation of record**: `tong_quan_tai_lieu.md` (Vietnamese)
**Review Date**: 2026-08-12
**Review Round**: 1
**Mode**: `academic-paper-reviewer` v1.10.0 — `full` (EIC + R1 + R2 + R3 + Devil's Advocate + Editorial Synthesis)
**Paper type**: Literature Review (narrative/thematic) — evaluated under §2.3 of `review_criteria_framework.md`

> **Read-only notice.** No reviewer modified the manuscript. This is a standalone report.

---

## Phase 0 — Reviewer Configuration Card

| Slot | Identity | Expertise | Review preference |
|------|----------|-----------|-------------------|
| **EIC** | Editor-in-Chief, *Briefings in Bioinformatics*-tier venue for computational precision oncology | Method-review editing; commissions survey articles | Values a synthesis that a reader could not assemble by reading the cited surveys themselves; intolerant of manuscript-readiness defects |
| **R1 (Methodology)** | Evidence-synthesis methodologist, systematic/scoping review reporting (PRISMA, PRISMA-ScR), reproducible search design | Search-protocol reproducibility, screening flow, risk-of-bias appraisal, data extraction | Treats the *corpus* as the review's dataset and the *search* as its instrument |
| **R2 (Domain)** | DRP/DSP method developer; publishes on GDSC/CCLE/DrugComb benchmarks and GNN architectures | Canonical-method coverage, benchmark literacy, citation accuracy | Checks whether the field's actual landmark papers are present |
| **R3 (Perspective)** | Translational-AI / regulatory-science researcher; clinical decision support, human factors in XAI | Who consumes the explanation; regulatory and deployment context; cross-disciplinary borrowing | Asks "explanation for whom, and to what standard" |
| **DA (Devil's Advocate)** | Adversarial methodologist, causal inference for ML-in-biology | Core-argument stress test, circularity, frame-lock | Only challenges; does not score |

**Field analysis**: Primary discipline — computer science / machine learning (bioinformatics). Secondary — cancer pharmacology / precision oncology. Paradigm — computational-methods survey. Target venue tier — high-quality bioinformatics survey venue, or a doctoral thesis Chapter 2. Maturity — advanced draft, structurally complete, not submission-ready.

**Verification performed before scoring** (two load-bearing citations checked against primary sources):
- Wang, Kumar, & Rajapakse (2025), XGDP — *Scientific Reports*, **15**, Article 179 — **correct as cited**.
- Wang, Wang, & Wei, AttenSyn — *J. Chem. Inf. Model.*, **2024, 64(7)**, 2854–2862 — **cited incorrectly** as "(2023) … 64(8)".

---
---

# Phase 1 — Reviewer Reports (independent, no cross-referencing)

---

## Report 1 — Editor-in-Chief

### Reviewer Role
EIC

### Reviewer Identity
Editor-in-Chief of a bioinformatics methods journal that publishes commissioned surveys of computational precision-oncology methods.

### Review Focus
Whether the manuscript's synthesis contributes something a reader could not obtain by reading the six surveys it cites; whether the scope claimed in §1.2 is delivered; and whether the manuscript is in a state a journal or a thesis committee could receive.

### Overall Assessment

**Recommendation**: **Major Revision**

**Confidence Score**: 4

**Summary Assessment**

The manuscript surveys computational drug response prediction (DRP) and drug synergy prediction (DSP), tracks the field's migration from statistical and generative models to graph neural networks, and argues that the integration of explainable AI with GNNs — exemplified by XGDP (Wang et al., 2025) — constitutes an emerging but under-benchmarked frontier. The topic is well chosen and genuinely timely, the three-theme architecture (foundations → architectures → explainability) is the right decomposition, and the manuscript's most valuable original move is the taxonomy in §4.3 and §5.2 that separates *architecturally-constrained self-interpretability* (XMR, GCNPath, SubCDR) from *post-hoc explanation of unconstrained models* (XGDP, DRExplainer) and correctly observes that no study has compared the two on shared data. That observation, and the three-item evaluation checklist in §7.2, are the parts of this review that a reader could not assemble from the cited surveys alone.

Against this, the manuscript is not currently in submittable condition, for reasons that are separable from its intellectual content. Author and affiliation are unfilled placeholders (lines 3–4). The manuscript repeatedly refers to "the requester" and a "user-supplied seed corpus" (§1.3, §1.4, §4.2) — process vocabulary that cannot appear in an academic manuscript, and which discloses inside the argument that the corpus was steered by a stated prior interest in one specific paper. The AI Disclosure states that the human author "has not yet independently verified every source," which is a submission blocker in its own right. Substantively, the review's central positive claim — that XGDP represents the field's frontier of rigor — is reached through a search that §1.3 says was deliberately directed at the intersection where XGDP sits, and is never stress-tested by an appraisal of XGDP's own limitations.

I recommend Major Revision. The intellectual scaffolding is sound and worth completing; the review methodology, the evidentiary discipline, and the manuscript hygiene are not yet at the level the content deserves.

### Strengths

**S1: A genuinely non-obvious organizing distinction.**
§4.3 and §5.2 identify two "largely unreconciled interpretability philosophies" — constrained self-interpretable architectures versus post-hoc explanation of unconstrained models — and correctly note (§6.1, gap five) that no study compares them on identical data and tasks. None of the six surveys cited (Kakkad et al., 2023; Nandan et al., 2025; Rao et al., 2022; Gangwal & Lavecchia, 2026; Berry & Cheng, 2025; Besharatifard & Vafaee, 2024) frames the DRP/DSP subfield this way. This is the manuscript's clearest original contribution and should be promoted, not buried at the end of §4.

**S2: An actionable, transferable reviewer checklist.**
§7.2 distils three concrete minimum reporting criteria — one hard generalization split, faithfulness via a second independent explainer *or* a quantitative ground-truth benchmark, and one externally cross-checked mechanistic case study. This is exactly the kind of output an editor wants from a survey: something a referee can apply to the next submission. It deserves to be a numbered box or table, not a clause inside a 300-word sentence.

**S3: Honest disclosure of a bibliographic ambiguity.**
§1.3 explicitly reports that a seed-list title resolved to two distinct real papers (Torkamannia et al., 2022 and Li et al., 2025) and includes both rather than silently picking one. This is better practice than most published surveys exhibit, and §2.2 goes on to use the pair productively as a before/after window on the field's graph-based turn.

**S4: Cross-sectional argumentative continuity.**
The manuscript threads recurring problems — scoring-convention inconsistency (§2.2), splitting-protocol inconsistency (§2.2, §3.2), the generalization gap (§2.3, §6.1) — forward across sections rather than stating them once. §3.2's observation that a DSP train/test split can be "unseen" along three distinct axes (unseen drug, unseen cell line, unseen pairing) is a good, specific piece of analysis.

### Weaknesses

**W1: Manuscript is not in submittable form.**
**Problem**: Author name and affiliation are placeholders (`[Author Name]`, `[Department, Institution — HUST]`, lines 3–4). The body refers to "the requester" (§1.3 twice, §1.4, §4.2) and to "the requester's stated primary interest" as a justification for the review's structure. The AI Disclosure states the author "has not yet independently verified every source in this document."
**Why it matters**: Any one of these would cause desk return. Together they signal a draft that was exported from a drafting workflow rather than prepared for readers. The "requester" framing is the most damaging, because it converts a methodological choice (why §4 is the centre of gravity) into an admission that the corpus was shaped by a prior preference for one paper.
**Suggestion**: Fill metadata. Replace every instance of "the requester" with an impersonal methodological rationale ("this review centres §4 on the XAI-GNN intersection because …"). Complete source verification and update the disclosure to say verification is complete, or retain the caveat only where genuinely unresolved.
**Severity**: Critical

**W2: The review's headline claim is reached by a search designed to reach it.**
**Problem**: §1.3 states that forward citation tracking and semantic search were used "to identify papers explicitly at the intersection of GNNs and explainability … since this intersection was underrepresented in the seed set relative to the requester's stated primary interest." §4.2 and §7.1 then conclude that XGDP "represents the current frontier of rigor in this subfield."
**Why it matters**: A survey that targets its search on the neighbourhood of a designated focal paper, and then finds that paper to be the frontier, has not tested the claim — it has restated its search protocol. Whether or not the conclusion is true, the manuscript as written cannot support it.
**Suggestion**: Either (a) separate the corpus into a protocol-driven set and a focal-paper set and report the frontier claim only over the protocol-driven set, or (b) reframe XGDP as an *illustrative exemplar chosen for depth of treatment* rather than as an empirically-established frontier, and let the checklist in §7.2 carry the normative weight instead.
**Severity**: Critical

**W3: The manuscript never appraises its own central exhibit.**
**Problem**: XGDP is discussed across §1.1, §3.1, §4.2 (twice, at length), §4.3, §5.1, §6.1, §6.2, §7.1 and §7.2. In every instance it is described approvingly. No limitation of XGDP is stated anywhere in the manuscript.
**Why it matters**: A review whose evaluative apparatus is applied to every method except the one it champions has abandoned the comparative stance that makes it a review. Readers will notice, and the omission undercuts the credibility of the criticism directed at AttenSyn.
**Suggestion**: Add a paragraph in §4.2 appraising XGDP against the manuscript's own §7.2 checklist — including that XGDP reports one case study, does not report a quantitative faithfulness metric, and does not test SHAP/LIME comparators (the very omission §4.1 criticises the field for).
**Severity**: Major

**W4: The review offers no comparative apparatus.**
**Problem**: The manuscript contains no tables and no figures. Its core comparative claims — which methods use which explainer, which validate how, which report which splits — are delivered entirely in prose across §4.2 and §4.3.
**Why it matters**: For a survey this is a structural deficiency, not a formatting preference. A method×property matrix is what makes a survey citable and reusable; without it, readers must reconstruct the comparison the manuscript claims to have made.
**Suggestion**: Add at minimum two tables: (T1) reviewed method × {task, backbone, explanation mechanism, validation type, benchmark, split regimes reported}; (T2) the §6.1 gaps × supporting evidence × proposed §6.2 remedy.
**Severity**: Major

**W5: Scope is claimed more broadly than it is delivered.**
**Problem**: §1.2 claims coverage of "explainability methods applied to graph neural networks" broadly, and §1.1 frames the review as positioning the subfield "relative to the broader GNN-explainability literature." The general XAI-GNN coverage in §4.1 consists of GNNExplainer, Integrated Gradients, attention, plus three surveys — no other explainer is named anywhere.
**Why it matters**: §5.3 and §6.1 (gap six) build an argument on the claim that counterfactual and surrogate methods are "essentially absent" from the DRP/DSP domain. That claim is only interesting if the manuscript has established what exists outside the domain, which it has not.
**Suggestion**: Either narrow §1.2's stated scope to the three explainers actually surveyed, or add the general-domain explainers needed to support the absence argument (see R2's W1).
**Severity**: Major

### Detailed Comments

**Title & Abstract** — Title is accurate and appropriately specific. The abstract is a single 300-word block; consider structuring it, and note that it asserts "thirty-six sources" via a four-layer strategy without stating that the seed corpus was externally supplied, which the body does disclose.

**Introduction** — §1.1 is the manuscript's strongest writing: the DRP/DSP distinction is crisp, and the shared-benchmark "double-edged methodological fact" framing is well made. §1.2 is a single sentence of roughly 200 words; split it. §1.4 is a competent roadmap but should not justify §4's prominence by reference to "the requester."

**Literature Review / Framework** — Thematic organisation is sound. §2, §3, §4 each end with a summary subsection, which aids navigation.

**Methodology (§1.3)** — See R1's report; from an editorial standpoint the section reads as a narrative account rather than a protocol, and the "18 seed + 18 supplementary = 36" arithmetic does not survive the disclosed duplicate resolution.

**Synthesis (§5) / Gaps (§6) / Conclusion (§7)** — Content is substantive but delivery is punishing: §6.1 presents six gaps as one 900-word paragraph, §6.2 six agenda items as another, §7.1 six conclusions as a third. Convert to numbered lists. There is also no *Limitations of this review* section; for a survey with an externally-seeded corpus and no formal protocol, that omission is conspicuous.

**References** — Venue quality is high (Nature portfolio, OUP bioinformatics titles, ACS, NeurIPS/ICLR/ICML). Formatting is mostly clean APA 7, with defects itemised by R2.

### Questions for Authors

1. If the seed corpus had not designated XGDP as the paper of central interest, would the review's conclusion about the field's frontier have been the same? What in the corpus, independent of that designation, supports it?
2. §1.3 reports 18 seed sources plus 18 supplementary equals 36, while also stating that one seed title resolved into two included papers. Which seed source was dropped, and on what criterion?
3. Is this manuscript intended for journal submission or as a thesis chapter? The required revisions differ substantially — a journal survey needs the comparative tables and a tightened scope; a thesis chapter additionally needs an explicit link from §6.2 to the candidate's own planned contribution.
4. §7.2 asserts that "no single method reviewed here satisfies all three criteria simultaneously." Was this verified method-by-method against a recorded extraction, or inferred from the narrative?

### Minor Issues

- Lines 3–4: unfilled metadata placeholders.
- §1.2 and §6.1 contain single sentences exceeding 150 words.
- The Vietnamese translation carries the date as `08/08/20263` (line 5) — a typographical error requiring correction, and the translation will need re-synchronisation after revision.
- No page or line numbering in the source document, which impedes referee citation.

### Dimension Scores

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 64 | Adequate | The two-philosophies framing and §7.2 checklist are genuine; the frontier claim is not independently established |
| Methodological Rigor (25%) | 50 | Weak | No protocol, no screening flow, corpus arithmetic inconsistent, corpus externally seeded |
| Evidence Sufficiency (25%) | 57 | Weak/Adequate boundary | 36 high-quality sources but canonical omissions and zero extracted quantitative evidence |
| Argument Coherence (15%) | 66 | Adequate | Strong cross-sectional threading, undermined by two circular arguments and one phantom cross-reference |
| Writing Quality (15%) | 68 | Adequate | Fluent and precise, but sentence length and register breaches are systematic |
| Literature Integration | 60 | Adequate | Good integration of what is present; landmark DRP/DSP methods absent |
| Significance & Impact | 70 | Adequate/Strong | Real value to thesis-stage readers and referees if the checklist is foregrounded |
| **Weighted Average** | **60.4** | **Major Revision** | (64×.20)+(50×.25)+(57×.25)+(66×.15)+(68×.15) |

---

## Report 2 — Peer Reviewer 1 (Methodology)

### Reviewer Role
Peer Reviewer 1 — Methodology

### Reviewer Identity
Evidence-synthesis methodologist specialising in reporting standards for computational and machine-learning reviews (PRISMA 2020, PRISMA-ScR); referees survey submissions for bioinformatics venues.

### Review Focus
For a literature review, the search protocol is the instrument and the corpus is the dataset. I assess reproducibility of the search, transparency of screening, appraisal of included studies, discipline of data extraction, and whether the manuscript's synthetic claims are supported by evidence it actually extracted.

### Overall Assessment

**Recommendation**: **Major Revision**

**Confidence Score**: 5

**Summary Assessment**

The manuscript is a narrative thematic review of GNN-based and XAI-augmented DRP/DSP methods. §1.3 describes a four-layer search strategy — Boolean database search, citation chaining, forward citation tracking, semantic search — followed by a four-criterion screen. As a *narrative* of how sources were found, this is more transparent than typical for the genre, and the explicit disclosure of a resolved title ambiguity is commendable. As a *protocol*, it is not reproducible: no database is named, no query string is given, no search date is recorded, no screening counts are reported, and no risk-of-bias or study-quality appraisal is applied to included work.

Three specific defects go beyond reporting convention. First, the corpus arithmetic in §1.3 is internally inconsistent: 18 seed sources with one title resolving into two included papers yields 19, not 18, so the stated "18 + 18 = 36" requires an undisclosed exclusion. Second, the manuscript extracted no quantitative results from any reviewed study — not one RMSE, PCC, AUC, or effect size appears anywhere — yet §5.1 asserts that graph representations "consistently outperform unstructured feature-vector baselines" and §2.2 that graph-based methods "now outperform non-graph deep learning baselines." These are quantitative claims discharged by citation to other reviews. Third, §5.1 characterises four findings as robust because they "recur with enough independence of source and method," while several of the corroborating sources are surveys of the same underlying primary studies — recurrence across overlapping surveys is not independence.

None of these is unfixable, and none impugns the manuscript's intellectual framing. But collectively they mean that a reader cannot reconstruct how the corpus was assembled, cannot verify any comparative performance claim, and cannot distinguish independently-supported findings from repeatedly-cited ones. Major Revision.

### Strengths

**S1: Multi-layer search design is the right architecture.**
The four layers in §1.3 — Boolean search, backward citation chaining, forward citation tracking, semantic search — correspond to the recommended complementary strategies for technology-domain reviews, where database indexing lags and preprints carry real weight. The design is sound; only its documentation is deficient.

**S2: Field-appropriate evidence profile, explicitly justified.**
§1.2 argues that arXiv/bioRxiv preprints and NeurIPS/ICLR/ICML proceedings should be admitted on equal footing with journal articles because foundational contributions (GCN, GAT, GNNExplainer) are canonically conference papers. This is correct for CS/ML and is stated rather than assumed — exactly the kind of pre-registered inclusion rationale a methodologist wants to see.

**S3: Transparent handling of a bibliographic ambiguity.**
The Torkamannia (2022) / Li (2025) resolution in §1.3, and its later productive use in §2.2, converts a screening problem into an analytic asset and documents the decision rule ("silently selecting one risked either an anachronistic citation or an inexact title match"). This is better than most published narrative reviews.

**S4: Independent bibliographic verification was attempted.**
The AI Disclosure states that authors, venues, years and DOIs were verified via independent search rather than accepted from internal knowledge. The verification is incomplete (see W5 and R2's findings), but the practice is the right one and should be stated in §1.3, not only in the disclosure.

### Weaknesses

**W1: The search is not reproducible.**
**Problem**: §1.3 refers to "Boolean database search" and "semantic search (via web search over Google Scholar-indexed and publisher databases)" without naming a single database, giving a single query string, or recording a search date or date range for execution. No screening counts are reported at any stage.
**Why it matters**: Reproducibility of the search is the review-paper analogue of reproducibility of an experimental protocol. As written, no reader can re-run this search, and no reader can assess how much of the corpus was determined by protocol versus by the supplied seed. For a thesis chapter, an examiner will ask for this directly.
**Suggestion**: Add a protocol subsection or appendix reporting, at minimum: databases queried (e.g. Scopus, Web of Science, PubMed, Semantic Scholar, arXiv), verbatim Boolean strings per database, date of execution, and a screening flow with counts — records identified, duplicates removed, titles/abstracts screened, full texts assessed, excluded with reasons, included. A PRISMA 2020 flow diagram is the standard vehicle; PRISMA-ScR is acceptable if the review is positioned as a scoping review.
**Severity**: Critical

**W2: Corpus arithmetic does not reconcile.**
**Problem**: §1.3 states "a curated seed set of 18 candidate sources," then reports that one seed title resolved into two distinct real papers, "**both** … included in this review," then concludes "36 sources were retained: 18 from the original seed list (with the R4 duplicate resolved by inclusion of both variants) and 18 supplementary sources (14 XAI-GNN-focused plus 4 additional confirmatory/foundational)." Eighteen seed titles with one yielding two included papers gives 19 seed-derived sources; 19 + 18 = 37, not 36. The reference list does contain exactly 36 entries, so a seed source was excluded without disclosure.
**Why it matters**: An undisclosed exclusion is precisely what a screening flow exists to prevent. The number 36 also underwrites §1.3's claim that the corpus "falls within the review-type source count range (30–80 sources)," so the count is load-bearing.
**Suggestion**: Reconcile explicitly. State which seed source was excluded and under which screening criterion, or correct the totals. Report seed and supplementary streams as separate rows in the screening flow.
**Severity**: Critical

**W3: No quantitative evidence was extracted, yet comparative performance claims are made.**
**Problem**: The manuscript reports no numerical result from any reviewed method — no metric value, no dataset size, no comparison table. Meanwhile §5.1 states that graph-structured representation "consistently outperforms unstructured feature-vector baselines," §2.2 that graph-based methods "now outperform non-graph deep learning baselines on standard benchmarks," and §3.1 that contrastive components are "each independently necessary" per GraphCDR's ablations.
**Why it matters**: These are the manuscript's empirical load-bearing claims and each is discharged by citing a survey that made the comparison, not by evidence the manuscript assembled. Because §2.2 and §3.2 correctly argue that split protocols and synergy scoring conventions are inconsistent across the literature, the manuscript is in the position of asserting a cross-paper performance ranking while simultaneously proving that cross-paper performance rankings are unreliable.
**Suggestion**: Add an extraction table for the primary method papers recording, per method: task (DRP/DSP), dataset(s), split protocol, primary metric and value, baselines compared against. Then either support the comparative claims from that table or downgrade them to attributed statements ("Besharatifard and Vafaee (2024) report that …") and state explicitly that this review did not independently verify cross-paper comparability.
**Severity**: Critical

**W4: "Independence" of corroborating evidence is asserted, not established.**
**Problem**: §5.1 claims four findings "recur with enough independence of source and method to be treated as robust," and §2.3 and §6.1 describe the generalization gap as "documented independently" for DRP and DSP, citing Partin et al. (2026), Abbasi and Rousu (2024) and Besharatifard and Vafaee (2024). Two of those three are review articles whose evidence base is the same primary DSP literature.
**Why it matters**: Treating multiple reviews of an overlapping primary corpus as independent replication inflates apparent robustness — the review-paper form of pseudoreplication. It is the same failure mode the manuscript itself warns about when it notes that shared benchmark panels concentrate reported gains within one set of biases (§1.1, §5.1).
**Suggestion**: For each "convergent" finding in §5.1, state the evidence type (primary method paper with ablation / benchmark study / secondary review) and check whether the primary sources actually differ. Reserve "independent" for findings supported by non-overlapping primary evidence.
**Severity**: Major

**W5: No quality or bias appraisal of included studies.**
**Problem**: §1.3 describes a "methodological soundness check" as a screening criterion, but no appraisal result is reported for any included source, and the manuscript admits preprints on equal footing without recording peer-review status per source.
**Why it matters**: §2.3 of the review-criteria framework treats risk-of-bias assessment as a defining dimension of review-type papers. Practically: DRExplainer is cited as a arXiv/journal hybrid (Shi et al., 2025), Duan et al. (2026) and several others are advance-online publications, and the manuscript's claims about which methods validate rigorously depend on how carefully each was assessed. Readers cannot see that assessment.
**Suggestion**: Add a column to the extraction table recording peer-review status (journal / conference-proceedings / preprint) and, for method papers, whether code and data are publicly available. This also directly supports the reproducibility argument in §6.
**Severity**: Major

### Detailed Comments

**Review Methodology (§1.3)** — The four-layer narrative should become a protocol with an appendix. Note that layer three is described as motivated by the requester's stated interest; a protocol would instead state the research question that motivated the targeted search. The screening criteria (peer-review/preprint quality, recency, relevance, methodological soundness) are reasonable but are not operationalised — "recency (favoring 2019–2026 unless foundational)" needs a decision rule for what counts as foundational.

**Synthesis (§5)** — §5.1's four convergent findings and §5.2's three debates are well chosen. §5.3's claim that the absence of counterfactual and surrogate methods "appears to reflect adoption lag rather than a principled exclusion" is an inference about causes of absence drawn from absence of evidence; either support it (e.g. by noting that no reviewed paper offers a reason for exclusion) or mark it as conjecture.

**Gaps (§6.1)** — The six gaps are individually well argued. Gap two (generalization × explanation-faithfulness never studied jointly) is the most valuable and most clearly supported. Gap one and gap six both amount to "no benchmark exists"; consider merging or sharpening the distinction.

**Results/figures** — None present. See EIC W4; from a methodology standpoint, the missing screening flow and the missing extraction table are the two that matter most.

**Reproducibility of the review itself** — The manuscript advocates reproducibility for the methods it reviews (§4.1, §6.2) while not meeting the analogous standard for its own procedure. Fixing W1–W3 resolves this asymmetry.

### Questions for Authors

1. What Boolean strings were executed, against which databases, and on what dates? Can the search be re-run today and yield the same corpus?
2. Which seed source was excluded to arrive at 36, and under which of the four screening criteria?
3. Was any structured extraction performed (spreadsheet, table, notes) from which the §5.1 convergent findings and the §7.2 "no method satisfies all three criteria" claim were derived? If so, it should be reported as an appendix; if not, both claims need to be re-derived from an explicit extraction.
4. Given §2.2's own argument that synergy scoring conventions and split protocols vary across papers, on what basis does §5.1 assert a consistent cross-paper performance advantage for graph representations?

### Minor Issues

- §1.3: "This falls within the review-type source count range (30–80 sources)" — cite the source of that range or drop the appeal to it.
- §1.3: "each was independently verified for bibliographic accuracy via targeted web search" — this belongs in the protocol with a statement of what "verified" checked (title, authors, year, venue, DOI resolution).
- §2.1 attributes to Okyere et al. (2025) a framework distinction between direct-prediction and latent-representation models; this is used to motivate the entire generative-models subsection and would benefit from a page-level pointer.
- Effort/recency: five 2026 sources are advance-online; note the access date for each, since advance-online metadata changes on issue assignment.

### Dimension Scores

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 62 | Adequate | Framing is original; not a methodological contribution |
| Methodological Rigor (25%) | 45 | Weak | Non-reproducible search, unreconciled corpus count, no appraisal, no extraction |
| Evidence Sufficiency (25%) | 54 | Weak | Adequate corpus size, but no primary evidence extracted to support comparative claims |
| Argument Coherence (15%) | 68 | Adequate | Sound structure; robustness argument overstates independence |
| Writing Quality (15%) | 70 | Adequate | Clear and precise; sentence length impedes the methods section most |
| Literature Integration | 62 | Adequate | Integration good where coverage exists |
| **Weighted Average** | **56.2** | **Major Revision** | (62×.20)+(45×.25)+(54×.25)+(68×.15)+(70×.15) |

---

## Report 3 — Peer Reviewer 2 (Domain)

### Reviewer Role
Peer Reviewer 2 — Domain

### Reviewer Identity
DRP/DSP method developer; publishes GNN architectures benchmarked on GDSC, CCLE, DrugComb, NCI-ALMANAC and the O'Neil dataset; reviews for bioinformatics and cheminformatics venues.

### Review Focus
Whether the corpus contains the field's landmark methods, whether the technical characterisations of the methods it does cover are accurate, and whether citations resolve correctly.

### Overall Assessment

**Recommendation**: **Major Revision**

**Confidence Score**: 5

**Summary Assessment**

This review surveys DRP and DSP with a focus on the explainability layer, and its technical descriptions of the methods it does cover are, with one class of exception, accurate and well-judged: the account of NIHGCN's parallel heterogeneous convolution plus neighbourhood-interaction layer (§3.1), of GraphCDR's contrastive regulariser and the ablation evidence for it (§3.1), of AttenSyn's interactive attention pooling (§3.2), and of XMR's Reactome-constrained visible network (§4.2) are all correct at the level of detail attempted. The relational-extension argument in §3.1 — that RGCN/RGAT matter for DRP specifically because multi-omic biological graphs carry semantically distinct edge types — is well made and is the kind of reasoning I would want a survey to supply.

My substantive concern is coverage. A review that concludes GNNs "have become the dominant architecture for both drug response and drug synergy prediction" (§7.1) does not cite DeepSynergy, the field's canonical deep-learning DSP baseline; does not cite DeepDDS, the graph-based DSP method most commonly benchmarked against; and does not cite GraphDRP, DeepCDR, tCNNS, DrugCell or PaccMann on the DRP side. The visible-neural-network lineage that XMR belongs to originates with DrugCell, which is absent. On the XAI side, a review arguing that counterfactual and self-interpretable methods are underused in this domain cites none of the general-domain methods it is implicitly recommending — no PGExplainer, SubgraphX, GraphMask, GraphSVX or CF-GNNExplainer. The absence argument in §5.3 and §6.1 cannot be evaluated when the alternatives are unnamed.

Separately, one citation is wrong in a way that propagates: AttenSyn is cited as 2023, 64(8), but is *J. Chem. Inf. Model.* 2024, 64(7), 2854–2862. The year appears in in-text citations across six sections. There are also APA disambiguation failures among the four distinct Wang-led references.

The manuscript's analytical apparatus is good enough that filling these gaps would produce a genuinely useful survey. As it stands the corpus is too thin at the base to support the field-level claims built on it. Major Revision.

### Strengths

**S1: Accurate, non-superficial method descriptions.**
§3.1's treatment of NIHGCN distinguishes the parallel graph convolution from the neighbourhood-interaction layer and correctly identifies the linear-correlation readout; §3.1 on GraphCDR correctly reports that the ablations isolate the contrastive term, the multi-omic features and the response-graph structure as independently necessary. Many surveys at this length reduce methods to a one-line label; this one does not.

**S2: The relational-extension rationale is well argued.**
§3.1's explanation of why RGCN/RGAT matter for DRP — heterogeneous biological graphs carry PPI, pathway co-membership and drug-target edges whose semantics differ, and collapsing them discards the specificity that motivated graph representations — is correct and is exactly the right level of technical reasoning for a survey audience.

**S3: The DSP-specific attribution problem is correctly identified.**
§3.2 and §4.2 recognise that explaining a synergy prediction requires attributing to the *joint* interaction across two molecular graphs plus cell-line context, that this is a harder attribution target than single-drug DRP, and that SANEpool is among the few methods addressing it directly. This is a genuine domain insight and is not stated in the surveys cited.

**S4: The three-axis split taxonomy for DSP is a useful contribution.**
§3.2's observation that a DSP test pair can be unseen because a constituent drug is unseen, because the cell line is unseen, or because the specific pairing is unseen even when both drugs were seen elsewhere — and that most papers report only one or two of these regimes — is precise, correct, and directly actionable for readers designing evaluations.

**S5: Correct and useful critique of attention-as-explanation.**
§4.1, §4.3 and §5.2 consistently and correctly distinguish attention weights from validated explanations, grounding the caution in Kakkad et al. (2023) and Rao et al. (2022), and apply it concretely to AttenSyn. This is the manuscript's sharpest piece of domain-level criticism.

### Weaknesses

**W1: Landmark DRP and DSP methods are absent from the corpus.**
**Problem**: On the DSP side, DeepSynergy (Preuer et al., 2018, *Bioinformatics*) — the method that established the O'Neil dataset as the field's benchmark and that essentially every subsequent DSP paper compares against — is not cited, nor is DeepDDS (Wang et al., 2022, *Briefings in Bioinformatics*), the graph-based DSP method most commonly used as the GNN baseline, nor MatchMaker or TranSynergy. On the DRP side, GraphDRP (Nguyen et al., 2021), DeepCDR (Liu et al., 2020), tCNNS (Liu et al., 2019), PaccMann and DrugCell (Kuenzi et al., 2020) are all absent. DrugCell's absence is the most consequential: XMR is described in §4.2 as a "visible neural network" constrained to Reactome pathways, and DrugCell is the origin of that design in cancer drug response.
**Why it matters**: §7.1's first conclusion — that GNNs became dominant for both tasks — and §5.1's first convergent finding are field-level claims. They cannot be established from a corpus that omits the methods that constitute the field's benchmark lineage. A domain referee will read the omission of DeepSynergy in a DSP review the way a methods referee reads a missing control.
**Suggestion**: Add the DRP and DSP landmark methods above, at minimum as a short lineage paragraph in §3.1 and §3.2 respectively, and cite DrugCell explicitly where XMR's visible-network design is introduced in §4.2.
**Severity**: Critical

**W2: The general XAI-GNN toolkit the manuscript recommends is never named.**
**Problem**: §5.3 states that counterfactual, causal and surrogate explanation methods are "essentially absent from the DRP/DSP-specific method papers," §6.1 (gap six) that SHAP/LIME are untested in the domain, and §6.2 (item five) recommends importing counterfactual explanation. Yet §4.1 names only GNNExplainer, Integrated Gradients and attention. No counterfactual GNN explainer is cited anywhere — not CF-GNNExplainer, not RCExplainer — nor are PGExplainer, SubgraphX, GraphMask or GraphSVX, which are the standard comparators in the general graph-XAI benchmarks the manuscript itself relies on (Rao et al., 2022).
**Why it matters**: An absence claim requires an inventory of what is absent. Without one, §5.3 and gap six are unfalsifiable, and the agenda item in §6.2 gives a reader no concrete method to adopt.
**Suggestion**: Extend §4.1 with a paragraph inventorying the general-domain GNN explainer families (perturbation/subgraph: GNNExplainer, PGExplainer, SubgraphX; gradient: IG, Grad-CAM variants; surrogate: GraphLIME, GraphSVX; counterfactual: CF-GNNExplainer, RCExplainer), then state which of these have and have not appeared in DRP/DSP work.
**Severity**: Critical

**W3: AttenSyn is cited with the wrong year and issue, and the error propagates.**
**Problem**: The reference list gives "Wang, T., Wang, R., & Wei, L. (2023). AttenSyn … *Journal of Chemical Information and Modeling, 64*(8), 2854–2862." The paper is 2024, volume 64, issue **7**, pages 2854–2862 (DOI 10.1021/acs.jcim.3c00709 — the DOI as given is correct). Volume 64 of JCIM is 2024, so the entry is internally inconsistent as printed. The year "(2023)" then appears in in-text citations in §3.2, §4.2 (twice), §4.3, §5.1, §5.2 and §6.1.
**Why it matters**: The year matters substantively here, because §4.2 and §4.3 position AttenSyn as an *earlier* and evidentially weaker contemporary of XGDP (2025) and DRExplainer (2025). Dating it 2023 rather than 2024 strengthens that framing by a year that the record does not support.
**Suggestion**: Correct to (2024), 64(7); update all seven in-text citations; re-check whether any "earlier and contemporaneous" framing in §4.2 needs adjusting.
**Severity**: Major

**W4: APA author-disambiguation failures across four Wang-led references.**
**Problem**: The corpus contains Wang, C., Kumar, & Rajapakse (2025); Wang, T., Wang, R., & Wei (2023→2024); Wang, Y., Wang, J., & Liu (2024); and Wang, Z., Zhou, Zhang, Mo, & Wang (2023). Under APA 7 §8.18, when different works shorten to the same "Wang et al. (Year)" form, enough surnames must be given to disambiguate. §4.2 uses the bare "AttenSyn (Wang et al., 2023)" while XMR is also Wang et al. (2023). §1.1 uses "Wang et al., 2025" for the claim about shared pharmacogenomic resources, where the intended referent (XGDP) is not obvious from context.
**Why it matters**: Two distinct 2023 Wang-led methods with different explanation philosophies are the subject of a direct comparison in §4.2 and §4.3. Ambiguous short forms in exactly that passage will mislead.
**Suggestion**: Use expanded forms throughout ("Wang, Wang, and Wei (2024)"; "Wang, Zhou, et al. (2023)"), which the manuscript already does in most, but not all, instances.
**Severity**: Major

**W5: Partin et al. (2026) is load-bearing but never actually reviewed, and its first citation contains a false cross-reference.**
**Problem**: Partin et al. (2026) is cited in §2.3, §6.1, §6.2, §7.1 and §7.2 as the primary evidence for the cross-dataset generalization gap in single-drug DRP. §2.2 introduces it as "documented for single-drug DRP by Partin et al. (2026, **discussed in Section 2.1** and revisited in Section 6)." Section 2.1 does not mention Partin et al. at any point; it discusses Okyere, Xiao, Dr.VAE, VAEN and scPreGAN. The manuscript never describes what Partin et al. did — the datasets, the models benchmarked, or the magnitude of the observed generalization drop.
**Why it matters**: This is the manuscript's single most-reused empirical citation and the anchor for gap two and for the §7.2 recommendation about hard generalization splits. A citation carrying that much weight must be reviewed in the body, and the cross-reference to a discussion that does not exist will be caught by any careful reader.
**Suggestion**: Add a paragraph in §2.1 (or a new §2.4) reviewing Partin et al.'s benchmark design and headline cross-dataset findings, then correct the cross-reference.
**Severity**: Major

### Detailed Comments

**§2.1** — Dr.VAE, VAEN and scPreGAN are accurately described and the "23 of 26 FDA-approved drugs" detail for Dr.VAE is correctly attributed. The claim that these methods "treat interpretability as a secondary concern at best" is fair. Consider noting that VAEN's cross-panel transfer result is itself early evidence for the generalization theme developed later.

**§2.2** — The synergy-reference-model discussion (Loewe / Bliss / HSA / ZIP) is one of the manuscript's most useful passages and is correctly framed as a comparability threat. It would be strengthened by noting which specific public datasets ship which scores (DrugComb provides multiple; the O'Neil data is commonly used with Loewe), which is exactly the operational detail a reader needs.

**§3.1** — Accurate throughout. GCNPath's pathway-constrained message passing and SubCDR's subcomponent decomposition are correctly characterised as interpretability-adjacent rather than XAI proper. DeepDR's "135 model configurations across nine drug encoders and nine cell encoders" is correct.

**§3.2** — Accurate but thin: this section carries the entire DSP-architecture theme on AttenSyn plus one survey. With DeepDDS, DeepSynergy and one knowledge-graph method added, it would balance §3.1.

**§4.2** — The strongest section in the manuscript. XGDP, XMR, SANEpool, DRExplainer and AttenSyn are each characterised by their distinct explanation strategy rather than lumped together, and the mapping in §4.3 onto the general post-hoc/self-interpretable and validated/unvalidated axes is genuinely illuminating.

**References** — Aside from W3 and W4: Rampásek should be Rampášek (diacritic); Shi et al. (2025) mixes an arXiv identifier with a journal advance-online designation and gives the arXiv URL rather than the journal DOI — pick one form; Duan et al. (2026) and Xiao et al. (2025) give a publisher URL / no article number where a DOI and article number exist. Venue quality overall is high.

### Questions for Authors

1. Was DeepSynergy (Preuer et al., 2018) excluded deliberately, or did it not surface in the search? If deliberate, on what criterion — it predates the 2019 recency window but is as foundational to DSP as GCN is to graph learning.
2. XMR is described as a "visible neural network." Should DrugCell (Kuenzi et al., 2020) be cited as the origin of that architecture in cancer drug response, and does its inclusion change the §4.3 claim that self-interpretable designs form a distinct tradition?
3. §4.1 states that no reviewed GNN-specific DRP/DSP method reports SHAP or LIME baselines. Was this verified per paper, or inferred? DRExplainer in particular reports comparisons whose baseline set should be checked.
4. §4.2 says XGDP "reports not just which architecture predicts best, but whether the two explainers agree more or less depending on architecture." Is this a quantitative agreement measure reported in the paper, or an inference from its qualitative case analysis? The distinction matters for the claim that XGDP's factorial design is a template others should generalise.

### Minor Issues

- §1.1: "NCI-ALMANAC, DrugComb, and the O'Neil dataset" — DrugComb is an aggregating portal rather than a primary screen; worth a clause distinguishing it.
- §3.1: DeepDR (Jiang & Li, 2024) is a library, not a model; the text handles this correctly but the §1.3 seed description calls it "one software library," which should match.
- Terminology: "DSP/DDS" is introduced in the abstract and §1.1 and then "DDS" is never used again — drop it or use it.
- Consider stating GDSC version (GDSC1 vs GDSC2) where the manuscript discusses benchmark overlap in §1.1 and §5.1; the distinction affects the overlap argument.

### Dimension Scores

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 65 | Adequate | §3.2 split taxonomy and §4.3 mapping are original domain contributions |
| Methodological Rigor (25%) | 55 | Weak | Corpus construction not sound at the base |
| Evidence Sufficiency (25%) | 52 | Weak | Landmark methods and the recommended XAI alternatives both absent |
| Argument Coherence (15%) | 70 | Adequate | Technically coherent; one false cross-reference |
| Writing Quality (15%) | 72 | Adequate | Technically precise; long sentences |
| **Literature Integration** | **52** | **Weak** | Primary focus of this report — coverage gaps are the dominant defect |
| **Weighted Average** | **59.1** | **Major Revision** | (65×.20)+(55×.25)+(52×.25)+(70×.15)+(72×.15) |

---

## Report 4 — Peer Reviewer 3 (Perspective)

### Reviewer Role
Peer Reviewer 3 — Perspective (cross-disciplinary, translational, impact)

### Reviewer Identity
Translational-AI and regulatory-science researcher working on clinical decision support and human factors in explainable AI; background spanning clinical informatics and ML evaluation.

### Review Focus
Whether the review's stated motivation — clinical trust and mechanistic hypothesis generation — is followed through into the disciplines that determine whether either is achieved; whether the proposed agenda is feasible; and which stakeholder perspectives shape what an adequate explanation would be.

### Overall Assessment

**Recommendation**: **Major Revision**

**Confidence Score**: 3

**Summary Assessment**

The manuscript opens by grounding the entire enterprise in two extra-technical motivations: clinical trust, and mechanism-of-action hypothesis generation for drug discovery (§1.1, citing Lavecchia, 2025 and Gangwal & Lavecchia, 2026). It closes (§7.2) with implications for practice and policy, including a caution against premature clinical deployment. Between those bookends, the review is conducted almost entirely within machine-learning methodology. The word "clinician" appears once, in the framing sentence; no regulatory framework is cited; no literature on how human experts actually use model explanations is engaged; and no work on causal inference — the discipline whose entire subject matter is when associational evidence licenses mechanistic claims — appears in the corpus, even though §5.3 lists causal-inference-based explanation as a legitimate XAI category and then drops it.

The consequence is that the review's normative recommendations are unanchored. §6.2 proposes a shared explanation-quality benchmark "grounded in curated cancer pathway/target databases," and §7.2 recommends a pharmacologically cross-checked case study as a minimum standard, but neither specifies who judges adequacy, against what decision, or at what cost. The one reviewed study that did use expert judgment as a criterion — Rao et al. (2022), which evaluated explainers against medicinal-chemist assessments — is cited for its benchmark and its fidelity/stability findings but not for the methodological move of putting a human expert in the evaluation loop, which is precisely the template §6.2 needs.

This is a Major Revision on cross-disciplinary grounds rather than a rejection: nothing in the manuscript is wrong here, and the additions I am asking for are bounded — roughly two paragraphs in §4.1/§6.2 and a reframed §7.2. What they would buy is a review whose recommendations a translational reader could act on.

### Strengths

**S1: The motivating framing is correct and well chosen.**
§1.1's articulation — that a model predicting sensitivity without indicating which genes, pathways or substructures drove the prediction supports neither mechanism-of-action hypothesis generation, nor biomarker discovery, nor clinician trust — is the right justification for the review and is stated more precisely than most papers in this space manage.

**S2: The deployment caution in §7.2 is well judged and non-obvious.**
The observation that "an explanation attached to a poorly generalizing prediction offers false reassurance rather than genuine mechanistic insight" is the single most translationally important sentence in the manuscript. It correctly identifies that explanation and generalization are not independent quality axes — a point the technical literature routinely misses.

**S3: The review identifies its own audiences explicitly.**
§7.2 addresses method designers, mechanism-discovery groups, the translational pipeline, and referees/thesis committees in turn. Segmenting implications by audience is good practice and makes the checklist directly usable.

**S4: Gap two is the right cross-cutting question.**
Asking whether mechanistic explanations remain stable when a model is applied out-of-distribution (§6.1) is the question that determines whether any of this reaches a clinic. It is well posed and, as far as this reviewer knows, genuinely open.

### Weaknesses

**W1: "Explanation for whom" is never asked, so explanation quality has no defined standard.**
**Problem**: The manuscript treats explanation quality as an intrinsic property measurable by faithfulness metrics and ground-truth benchmarks (§4.1, §6.1, §6.2). It never distinguishes the consumers whose needs differ sharply: a medicinal chemist wanting an actionable structural hypothesis, a computational biologist wanting a testable pathway hypothesis, an oncologist wanting a reason to trust a recommendation, and a regulator wanting an auditable basis for a decision. §7.2 says explanations should be credible to "a domain expert, not just a benchmark metric" without saying which expert or how credibility would be measured.
**Why it matters**: Faithfulness — whether an explanation reflects the model's computation — and usefulness — whether it supports the consumer's decision — are orthogonal, and the review's entire evaluative apparatus measures only the first while its stated motivation is the second. A benchmark built as §6.2 proposes could be topped by a method that no chemist finds actionable.
**Suggestion**: Add a short subsection in §4.1 distinguishing faithfulness, plausibility and utility as separate evaluation targets, and engage the human-centred XAI evaluation literature (e.g. Doshi-Velez & Kim's application-grounded / human-grounded / functionally-grounded taxonomy). Then state which target §6.2's proposed benchmark addresses.
**Severity**: Major

**W2: Regulatory and translational context is entirely absent despite a policy-framed section.**
**Problem**: §7.2 is titled "Implications for Practice and Policy" and issues a deployment caution, but no regulatory instrument, guidance document or clinical-evaluation framework is cited anywhere — not the EU AI Act's high-risk classification for medical AI, not FDA guidance on AI/ML in drug development or SaMD, not reporting standards for clinical prediction models (TRIPOD+AI) or trial protocols for AI interventions (SPIRIT-AI / CONSORT-AI).
**Why it matters**: The manuscript's own logic makes explainability a compliance-adjacent question — if explanation is required for clinical trust, the requirement is increasingly a legal one, with defined obligations. A section labelled "Policy" that cites no policy will read as under-informed to exactly the translational audience it addresses, and the omission also weakens §6.2's benchmark proposal, since regulatory expectations are a natural source of benchmark design constraints.
**Suggestion**: Add a paragraph to §7.2 situating the review's checklist relative to at least one regulatory framework and one clinical-prediction reporting standard, and note explicitly which of the three checklist items maps to an existing external requirement.
**Severity**: Major

**W3: Causal inference is named as relevant, then dropped.**
**Problem**: §5.3 lists "causal-inference-based explanation" among the legitimate XAI categories identified by the general surveys, notes its absence from DRP/DSP work, and does not return to it. §6.2 recommends importing counterfactual explanation but frames it purely as medicinal-chemistry structural modification ("what minimal change to this molecule would eliminate the predicted synergy"), not as causal reasoning.
**Why it matters**: The gap between "the model used gene X" and "gene X is mechanistically involved" is a causal-inference gap, and it is the gap the entire review is about. Omics features are heavily correlated and confounded by lineage and tissue of origin, so a faithful attribution to a gene may reflect a confounder rather than a mechanism. Without engaging this, §6.2's benchmark proposal risks certifying attributions that are faithful to the model and uninformative about biology.
**Suggestion**: Add a paragraph — §4.1 or §5.3 — distinguishing model-faithfulness from biological-causality, noting confounding in cell-line omics as the concrete obstacle, and pointing to perturbation-based validation (CRISPR screens, LINCS/L1000 perturbation data) as the causal evidence type that would close the gap. This also gives §6.2's third agenda item a concrete data source.
**Severity**: Major

**W4: The proposed agenda has no feasibility analysis.**
**Problem**: §6.2 recommends that mechanistic case studies cross-checked against external pharmacological databases become "a minimum reporting standard," and §6.1 notes wet-lab validation is rare. No estimate is given of what compliance would cost — in expertise, time, or access to experimental capacity — and no account is offered of why the practice is currently rare.
**Why it matters**: Recommending a norm without addressing its cost is how survey agendas fail to change behaviour. The reason wet-lab validation is rare is that most groups publishing DRP/DSP methods are ML groups without wet-lab access; a recommendation that ignores this will be ignored in turn.
**Suggestion**: Distinguish tiers of validation by cost — database cross-check (cheap, immediately adoptable, and what XGDP actually did), public perturbation-data cross-check (moderate), prospective wet-lab validation (expensive, requires collaboration) — and target the minimum standard at the cheapest tier while positioning the others as aspirational. This makes the recommendation adoptable and is more consistent with what the reviewed exemplars actually demonstrate.
**Severity**: Major

**W5: Patient- and clinician-facing considerations are absent from a precision-oncology review.**
**Problem**: The review is framed by precision oncology and closes with clinical deployment caution, but never addresses cohort representativeness in the underlying panels (GDSC/CCLE cell-line collections are known to under-represent non-European ancestries and several tumour types), nor equity implications of models trained on them, nor the clinician's decision context in which an explanation would be received.
**Why it matters**: §1.1 and §5.1 already establish that the field's near-universal reliance on a small overlapping set of panels concentrates gains within those panels' biases. The manuscript stops at a methodological framing of that fact when it has a translational one available — the biases are demographic and disease-distributional, not only statistical, and that is what makes the generalization gap a clinical-equity problem rather than only a benchmarking problem.
**Suggestion**: Extend the §5.1 shared-substrate discussion by one or two sentences on the composition of those panels and its equity consequences, and connect it to the §7.2 external-cohort validation caution.
**Severity**: Minor

### Detailed Comments

**Introduction** — The motivation is stated in translational terms and then not carried forward; the fix is largely a matter of returning to §1.1's framing in §6 and §7 rather than adding new scope.

**§4.1** — This is where the faithfulness/plausibility/utility distinction belongs. The section currently treats "faithfulness" as the property of interest throughout, which is defensible but should be stated as a choice rather than assumed.

**§5.1 / §5.3** — §5.1's fourth convergent finding (shared evaluation substrate) is the natural hook for both the equity point (W5) and the causal-confounding point (W3).

**§6.2** — Six agenda items, all reasonable, none costed or sequenced. Consider ordering them by adoptability: items three and six are immediately actionable by any group; item one requires community coordination; item two requires access to specific cross-dataset splits.

**§7.2** — The strongest closing material in the manuscript. Reframing the three-item checklist as a boxed, numbered standard, and adding the regulatory anchor from W2, would make it the piece of this review most likely to be cited.

### Questions for Authors

1. Who is the intended consumer of the explanations this review advocates — medicinal chemist, computational biologist, oncologist, or regulator? Does the answer change which of the reviewed methods is preferable?
2. Given that cell-line omics features are strongly correlated and confounded by lineage, what distinguishes a faithful attribution to a gene from evidence that the gene is mechanistically involved? Does the review's proposed benchmark (§6.2) address that distinction?
3. Would you expect the §7.2 checklist to be adoptable by an ML group without wet-lab access? If so, which of the three items are satisfiable from public data alone?
4. Should the review engage regulatory requirements for explainability in clinical AI, given that §7.2 is framed as policy-facing?

### Minor Issues

- §7.2: "thesis committees and journal reviewers" is the only place a non-researcher audience is named; the policy framing in the section title promises more than the content delivers.
- "clinical trust" is invoked in §1.1 and §7.2 but never operationalised; either define it once or use a narrower term.

### Dimension Scores

| Dimension | Score (0-100) | Descriptor | Notes |
|-----------|--------------|------------|-------|
| Originality (20%) | 66 | Adequate | Explanation×generalization coupling insight is genuinely novel and undervalued in the manuscript |
| Methodological Rigor (25%) | 55 | Weak | Assessed from the perspective of evaluation-target definition, which is undefined |
| Evidence Sufficiency (25%) | 58 | Weak/Adequate | No engagement with human-centred XAI, regulatory, or causal literatures |
| Argument Coherence (15%) | 68 | Adequate | Motivation and conclusion are consistent; the middle does not connect them |
| Writing Quality (15%) | 70 | Adequate | — |
| **Significance & Impact** | **68** | **Adequate** | Primary focus of this report — real potential impact, currently under-delivered |
| **Weighted Average** | **60.2** | **Major Revision** | (66×.20)+(55×.25)+(58×.25)+(68×.15)+(70×.15) |

---

## Report 5 — Devil's Advocate

*(Per protocol, the Devil's Advocate does not score and does not duplicate other reviewers' dimensions. Findings below are restricted to logical structure, evidence selection, and core-argument vulnerability.)*

### Devil's Advocate Review

**Affirmation before challenge.** This manuscript is well organised, technically literate, and unusually honest about parts of its own process — the disclosure of a resolved bibliographic ambiguity in §1.3 is more than most published reviews offer, and the §7.2 evaluation checklist is a real contribution that would survive most of what follows. What follows attacks the argument, not the effort.

### Strongest Counter-Argument

The review's central empirical claim is that XGDP represents the current frontier of rigor in XAI-GNN drug response prediction, and its central normative claim is that the field needs benchmarked, biologically grounded explanation. A scholar holding the opposite view would argue that both claims are artefacts of the review's construction rather than findings about the field.

Take the frontier claim first. §1.3 states that the corpus began as an externally supplied seed set, that XGDP was designated the paper of central interest before the search, and that layer three of the search was executed specifically because "this intersection was underrepresented in the seed set relative to the requester's stated primary interest." A search targeted at a paper's neighbourhood will return that paper's neighbourhood, and within it, the designated paper will be the most thoroughly described — because it was read most closely, not because it is best. The manuscript then treats depth of its own treatment as evidence of the paper's standing: §4.2 calls XGDP's factorial design "within the corpus reviewed here, unique," a claim whose scope qualifier concedes the point. No limitation of XGDP is stated anywhere across nine separate discussions of it, while every other method receives an explicit evidential downgrade. That asymmetry is what confirmation bias looks like in a review article.

Now the normative claim. §7.2 concludes that "no single method reviewed here satisfies all three criteria simultaneously, which is itself the clearest evidence that this remains an open, actionable frontier." But the three criteria were derived in the immediately preceding sentences from three different exemplars — the hard-split criterion from Partin, the faithfulness criterion from XGDP *or* DRExplainer, the case-study criterion from XGDP and DrugS. A checklist assembled by taking each item from whichever paper does it best cannot be satisfied by any single paper. The conclusion is guaranteed by the construction, and the manuscript presents it as a discovery.

Strip both artefacts away and what survives is worth keeping — the two-philosophies distinction (§4.3, §5.2), the three-axis DSP split taxonomy (§3.2), and the observation that explanation stability under distribution shift is unstudied (§6.1). Those do not depend on XGDP's standing and would hold if XGDP were removed from the corpus entirely. The paper's real contribution is a framework; its stated contribution is a verdict about a field. The verdict is the part that does not survive scrutiny.

### Issue List

#### CRITICAL

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| C1 | Confirmation bias / Logic chain | The frontier verdict is produced by a search protocol explicitly steered toward the focal paper's neighbourhood, then reported as a finding about the field. The manuscript discloses the steering (§1.3) and does not treat it as a limitation anywhere. | §1.3, §1.4, §4.2, §7.1 |
| C2 | Logic chain break (circularity) | "No single method satisfies all three criteria" is entailed by how the criteria were assembled — one from each best-in-class exemplar — yet is presented as evidence that the frontier is open. | §7.2 (final sentences) |
| C3 | Cherry-picking / asymmetric appraisal | XGDP is discussed in nine places and criticised in none, while AttenSyn, XMR, SANEpool and DRExplainer each receive explicit evidential limitations. The evaluative standard is applied to every method except the designated exemplar. | §1.1, §3.1, §4.2, §4.3, §5.1, §6.1, §6.2, §7.1, §7.2 |
| C4 | Data–conclusion mismatch | §5.1 declares four findings "robust" on grounds of "independence of source and method," but the manuscript extracted no quantitative data from any source and several corroborating sources are surveys of an overlapping primary corpus. Robustness is asserted from citation recurrence. | §5.1; cf. §2.2, §3.2 |

#### MAJOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| M1 | Evidence gap | The afatinib/EGFR case study is treated as the manuscript's exemplar of external validation, but afatinib is a licensed, second-generation EGFR inhibitor whose target is among the best-characterised in oncology. An explainer that *failed* to recover EGFR here would be broken. A near-tautological confirmation is presented as strong evidence, and the manuscript never asks what a hard test would look like. | §1.1, §4.2, §6.1, §7.1 |
| M2 | Hidden assumption | The review argues at length that attention weights are unfaithful and that GNNExplainer/IG agreement is stronger evidence, without noting that both are perturbation- and gradient-based methods evaluated on the same trained model and the same feature space. Agreement between two attribution methods on a shared, confounded input can reflect a shared artefact rather than a shared truth. | §4.2, §4.3, §5.1 |
| M3 | Internal contradiction | §2.2 and §3.2 argue that cross-paper performance comparison is unreliable because synergy scoring conventions and split protocols differ; §2.2 and §5.1 then assert cross-paper performance rankings ("graph-based methods now outperform non-graph deep learning baselines"). The manuscript cannot have both. | §2.2 vs §5.1 |
| M4 | Logic chain | §5.3 infers from the absence of counterfactual/surrogate methods in the corpus that the absence "appears to reflect adoption lag rather than a principled exclusion," reasoning from absence of evidence to a cause of that absence, with no reviewed source addressing the question. | §5.3, §6.1 (gap six) |
| M5 | Evidence gap / false cross-reference | Partin et al. (2026) is the sole primary support for the DRP generalization gap and is cited five times, never described, and introduced with a cross-reference to a discussion in §2.1 that does not exist. | §2.2 → §2.1; §2.3, §6.1, §6.2, §7.1, §7.2 |
| M6 | Overgeneralization | §7.1 concludes GNNs are "the dominant architecture" for both tasks. The manuscript's evidence is that the papers it selected are graph-based and that the surveys it cites say so. No bibliometric or share-of-literature evidence is presented, and the corpus was selected for graph relevance. | §7.1, §1.2 (scope) |

#### MINOR

| # | Dimension | Issue Description | Location |
|---|-----------|-------------------|----------|
| m1 | Framing | "The requester's stated primary interest" is offered inside the manuscript as a justification for §4's prominence, making a private preference an argumentative premise. | §1.3, §1.4, §4.2 |
| m2 | Overclaiming | The abstract's "four-layer search strategy" and "screened against relevance, recency, and methodological rigor criteria" imply a systematic protocol the body does not document. | Abstract vs §1.3 |
| m3 | Self-exemption | The manuscript demands reproducibility, benchmarking and external validation of every method it reviews, while supplying none of the analogous artefacts for itself (protocol, extraction, limitations). | §6.2 vs §1.3 |
| m4 | Unsupported inference | §4.2 claims XGDP can report "whether the two explainers agree more or less depending on architecture." Whether that is a reported quantitative result or an inference is not stated. | §4.2 |

### Ignored Alternative Explanations/Paths

1. **The subfield may be small because the problem is not yet worth solving at this layer, not because of adoption lag.** The manuscript's consistent explanation for every gap is immaturity — "adoption lag" (§5.3), "the field's overall youth" (§4.3), "still uncommon" (§4.2). A more parsimonious rival explanation is that explanation of cell-line DRP models has low expected value because the underlying predictions do not transfer (a fact the manuscript itself establishes in §2.3 and §6.1), so groups rationally invest in generalization before interpretability. That rival hypothesis explains the same observations, is consistent with the manuscript's own evidence, and inverts the §6.2 agenda's priority ordering. It is never considered.

2. **Interpretability may be better pursued by improving the data than by explaining the model.** Every remedy proposed in §6.2 is an explanation-side intervention. The alternative — that mechanistic claims should come from perturbation data (CRISPR screens, LINCS/L1000) with the predictive model used only for prioritisation — is never posed, despite being how much of the field's mechanistic evidence is actually generated. This is an alternative *path*, not merely an alternative method, and it would reframe explainability as triage rather than as evidence.

3. **The two "philosophies" may not be in competition.** §5.2 frames constrained self-interpretability and post-hoc explanation as rival positions awaiting an empirical adjudication (§6.1 gap five). They may simply address different questions — the constrained approach fixing the hypothesis space in advance, the post-hoc approach searching it after the fact — in which case the head-to-head comparison the manuscript calls for is not well posed, and the interesting study is their combination, which §6.1 mentions in a subordinate clause and §6.2 does not develop.

4. **XGDP's dual-explainer agreement may be a weaker signal than claimed.** The manuscript treats agreement between GNNExplainer and Integrated Gradients as cross-validation because the methods "rest on different mathematical foundations." An equally available reading is that both interrogate the same trained model over the same correlated feature space and will therefore agree on whatever the model latched onto, including a confounder. The manuscript asserts the favourable reading without argument.

### Missing Stakeholder Perspectives

- The experimental pharmacologist who would be asked to test an XAI-derived hypothesis, and whose willingness determines whether §6.2's validation standard is achievable.
- The regulator or clinical-evaluation body whose definition of an adequate explanation may not coincide with faithfulness metrics.
- The patient populations represented — and not represented — in the GDSC/CCLE panels on which every reviewed method depends.
- Authors of the methods criticised for weak interpretability claims (e.g. AttenSyn), whose stated goals may not have included the evidentiary standard applied to them.

### Unexamined Premise

*(Frame-lock detection — an assumption underlying the whole manuscript that none of the eight challenge dimensions captured.)*

**The review assumes throughout that a faithful explanation of a predictive model constitutes mechanistic evidence about biology.** Every evaluative move depends on it: faithfulness is treated as the property that separates good explanations from bad (§4.1, §5.1); "mechanism prediction" and "explanation" are used interchangeably from the title onward; and §6.2's proposed benchmark would score explanations against curated pathway databases as though model-attribution and biological-mechanism were the same target.

They are not. Faithfulness establishes that the explanation reflects what *the model* computed. The model was fit to observational cell-line data in which omics features are heavily correlated and confounded by lineage and tissue of origin. A perfectly faithful explanation of such a model can therefore identify a confounder, a lineage marker, or a proxy — and be maximally faithful while being mechanistically wrong. Conversely, an unfaithful explanation could name the right gene by accident.

This distinction is the difference between the review's stated goal (mechanism) and its actual evaluative apparatus (faithfulness). The manuscript never states it, and consequently its central research agenda — better faithfulness benchmarks — may not advance its central motivation at all. Two of the manuscript's own observations point at the premise without naming it: the §7.2 remark that an explanation on a poorly generalizing model "offers false reassurance," and the §6.1 gap-two question about whether explanations survive distribution shift. Both are symptoms of this premise. Naming it explicitly would strengthen the review considerably — and would reframe §6.2's agenda around perturbation-grounded rather than attribution-grounded validation.

### Observations (Non-Defects)

- The manuscript's willingness to flag the Torkamannia/Li title ambiguity in the body rather than resolving it silently is genuinely unusual and should be preserved through revision.
- §3.2's three-axis analysis of what "unseen" can mean for a drug pair is the manuscript's most quietly valuable technical passage and is currently buried; it would carry more weight as a figure.
- The AI Disclosure is more candid than most, including its admission of incomplete verification. That candour is a liability for submission and a credit to the author; the fix is to complete the verification, not to soften the disclosure.

---
---

# Phase 2 — Editorial Decision

## Manuscript Information
- **Title**: Explainable Graph Neural Networks for Drug Response and Drug Synergy Prediction: A Literature Review
- **Decision Date**: 2026-08-12
- **Review Round**: 1

---

## Decision

### **Major Revision**

**Note on decision constraint**: The Devil's Advocate returned four CRITICAL findings (C1–C4). Per Checkpoint Rule #4 of the reviewer protocol, a CRITICAL DA finding precludes an Accept decision regardless of dimension scores. The scores independently place the manuscript in the Major Revision band, so the constraint is not doing the work here — but it is recorded.

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence | Weighted Score |
|----------|------|---------------|------------|----------------|
| EIC | Bioinformatics methods-journal editor | Major Revision | 4 | 60.4 |
| Reviewer 1 | Evidence-synthesis methodologist | Major Revision | 5 | 56.2 |
| Reviewer 2 | DRP/DSP method developer | Major Revision | 5 | 59.1 |
| Reviewer 3 | Translational-AI / regulatory science | Major Revision | 3 | 60.2 |
| Devil's Advocate | Adversarial methodologist | *(does not score)* | — | 4 CRITICAL, 6 MAJOR |

**Panel mean**: 59.0 → Major Revision (50–64 band). Unanimous recommendation, no dissent on decision level.

---

## Consensus Analysis

### Points of Agreement

**[CONSENSUS-5]** — All five reviewers, independently:

1. **The corpus and the search that produced it are the manuscript's weakest link.** R1 W1/W2 (non-reproducible search, unreconciled 18+18=36 arithmetic); R2 W1/W2 (landmark DRP/DSP methods and the recommended general XAI methods both absent); EIC W5 (scope claimed exceeds scope delivered); R3 W2/W3 (three adjacent literatures absent); DA C1 (search steered toward the focal paper). Every reviewer reached this from a different direction.

2. **The manuscript makes comparative and robustness claims it did not gather evidence to support.** R1 W3 (no quantitative extraction, yet cross-paper performance rankings asserted); R1 W4 (surveys of an overlapping corpus counted as independent corroboration); DA C4 and M3 (§2.2's comparability warning contradicts §5.1's comparative claim); EIC W4 (no comparative apparatus of any kind); R2 (the field-dominance claim rests on a corpus selected for graph relevance).

3. **XGDP is never appraised.** EIC W3, R2 (implicit in the AttenSyn dating question, which alters XGDP's relative framing), DA C3 and M1. Nine discussions, zero limitations. The panel regards this as the manuscript's most correctable serious defect.

**[CONSENSUS-4]** — Four of five:

4. **Presentation of §6 and §7 defeats their content** (EIC, R1, R2, R3): six gaps, six agenda items and six conclusions are each delivered as a single undifferentiated paragraph, and there is not one table or figure in the manuscript.

5. **The manuscript holds reviewed methods to standards it does not meet itself** (R1, R3, DA m3, EIC): reproducibility, benchmarking, external validation and limitations are demanded throughout §6.2 and supplied nowhere for the review itself.

**[CONSENSUS-3]** — Three of five:

6. **Manuscript-readiness defects are independently disqualifying** (EIC W1, R2 W3/W4, DA m1): metadata placeholders, "requester" register, unverified-sources disclosure, and the AttenSyn citation error.

### Points of Disagreement

**Disagreement 1: Is the XGDP framing recoverable, or must the frontier claim be withdrawn?**
- **EIC view** (W2): recoverable via reframing — present XGDP as an exemplar selected for depth of treatment rather than as an empirically established frontier, and shift normative weight to the §7.2 checklist.
- **DA view** (C1, C3): the verdict is an artefact of construction and cannot be repaired by softened wording; the search steering must be reported as a limitation and the frontier claim withdrawn as a *finding*, not merely hedged.
- **Disagreement type**: Severity disagreement (both agree the claim is unsupported; they differ on whether reframing suffices).
- **Editor's Resolution**: Adopt the DA's stronger requirement. Reframing alone would leave the manuscript asserting a field-level verdict produced by a corpus the manuscript itself says was steered. **R2 in the roadmap requires both**: (a) an explicit Limitations subsection disclosing the seeded, interest-steered corpus, and (b) restatement of the XGDP material as an in-depth exemplar analysis, with the normative load carried by the §7.2 checklist.
- **Resolution Rationale**: Conservative principle. A disclosed limitation costs the manuscript little and makes the remaining contribution defensible; an undisclosed one is the kind of defect a thesis examiner or referee finds independently, at greater cost.

**Disagreement 2: How much new literature must be added?**
- **R2 view** (W1, W2): substantial — the DRP/DSP landmark lineage (DeepSynergy, DeepDDS, GraphDRP, DeepCDR, DrugCell and others) plus the general XAI-GNN explainer families.
- **R3 view** (W1–W3): different additions — human-centred XAI evaluation, regulatory frameworks, causal inference.
- **EIC view** (W5): alternatively, *narrow the claimed scope* to match what is covered, rather than expanding coverage.
- **Disagreement type**: Direction disagreement.
- **Editor's Resolution**: R2's additions are **required**; R3's are **required in reduced form** (two paragraphs plus a reframed §7.2, not a new section); EIC's narrowing option is **rejected** for the DRP/DSP lineage — a DSP review without DeepSynergy is not a scope choice — but **accepted** for the general-XAI-GNN scope, where §1.2 should be narrowed *and* §4.1 given the explainer inventory needed to support the absence argument in §5.3/§6.1.
- **Resolution Rationale**: Expertise weighting. R2 holds confidence 5 in exactly this domain and identifies omissions that falsify field-level claims; R3 holds confidence 3 and identifies enrichments that improve reach without being load-bearing.

**Disagreement 3: Severity of the §7.2 circularity (DA C2).**
- **DA view**: CRITICAL — the concluding claim is entailed by the checklist's construction.
- **EIC / R1 view**: neither flagged it independently; R1's W3 covers the adjacent problem that the claim was never verified against an extraction.
- **Disagreement type**: Existence disagreement (the other reviewers did not detect it).
- **Editor's Resolution**: Upheld as CRITICAL. On inspection the entailment is exact — the three criteria are drawn in the preceding sentences from Partin, from XGDP-or-DRExplainer, and from XGDP-and-DrugS respectively. **R4 in the roadmap requires** that the claim either be dropped or be re-derived from an explicit method×criterion extraction table, in which case it becomes a verified finding rather than a construction artefact.
- **Resolution Rationale**: Evidence-based. The DA's reading is checkable against the text and survives checking.

---

## Decision Rationale

The panel converged unanimously on Major Revision from four independent perspectives, with a mean weighted score of 59.0 — mid-band, not borderline. The consensus is unusually specific: all five reviewers located the manuscript's central defect in the same place, namely that its corpus was assembled by a procedure it cannot document (R1 W1/W2), steered toward a designated focal paper (DA C1), missing the field's landmark methods (R2 W1), and never subjected to structured extraction (R1 W3) — and that the manuscript's field-level claims are nonetheless stated as findings about the field rather than about the corpus.

I have not chosen Reject because the defects are procedural and repairable rather than conceptual, and because three distinct contributions survive every attack made on the manuscript: the constrained-versus-post-hoc interpretability distinction (§4.3, §5.2), the three-axis DSP split taxonomy (§3.2), and the coupling of explanation quality to out-of-distribution generalization (§6.1 gap two, §7.2). The Devil's Advocate — whose brief is to find the strongest case against — explicitly concedes that these hold independently of the XGDP framing. A review with three defensible original contributions and a documented corpus is publishable; this manuscript needs the second half of that sentence.

I have not chosen Minor Revision because two of the required repairs change the manuscript's claims, not just its presentation. Adding the DRP/DSP landmark lineage will alter §3 and may alter the dominance claim in §7.1; disclosing the seeded corpus removes the frontier verdict as a finding. Both require re-review.

The AI Disclosure's statement that sources have not been independently verified is treated here as blocking rather than as a minor issue, and one verified error (AttenSyn dated 2023/64(8) rather than 2024/64(7)) confirms that the concern is live rather than pro forma. Full verification is R1 in the roadmap.

---

## Required Revisions (Must Fix)

| # | Revision Item | Source | Severity | Section | Effort |
|---|--------------|--------|----------|---------|--------|
| R1 | Complete source verification; fix AttenSyn (2024, 64(7)); fix APA disambiguation for the four Wang-led references; fix Rampášek diacritic, Shi et al. hybrid arXiv/journal entry, missing DOIs/article numbers; fill author/affiliation metadata; remove all "requester" language | R2 W3/W4, EIC W1, DA m1 | Critical | Header, §1.3, §1.4, §4.2, References, Disclosure | 2–3 days |
| R2 | Add a **Limitations of this review** subsection disclosing the externally-seeded, interest-steered corpus; restate XGDP material as an in-depth exemplar rather than an established frontier; add an appraisal of XGDP against the manuscript's own §7.2 checklist | DA C1/C3, EIC W2/W3 | Critical | New §1.5 or §6.3; §4.2; §7.1 | 3–4 days |
| R3 | Document the search as a reproducible protocol: databases, verbatim Boolean strings, execution dates, screening flow with counts (PRISMA 2020 or PRISMA-ScR), inclusion/exclusion criteria operationalised; reconcile the 18+18=36 arithmetic and disclose the excluded seed source | R1 W1/W2 | Critical | §1.3 + appendix | 3–4 days |
| R4 | Build a structured extraction table (method × task × dataset × split protocol × explanation mechanism × validation type × peer-review status × code availability); re-derive or withdraw the §5.1 robustness claims and the §7.2 "no method satisfies all three criteria" claim from it | R1 W3/W5, DA C2/C4, EIC W4 | Critical | New table in §4 or appendix; §5.1; §7.2 | 4–5 days |
| R5 | Add the missing DRP/DSP landmark methods: DeepSynergy, DeepDDS, (and as appropriate MatchMaker/TranSynergy) for DSP; GraphDRP, DeepCDR, tCNNS, DrugCell for DRP — with DrugCell cited where XMR's visible-network design is introduced | R2 W1 | Critical | §3.1, §3.2, §4.2 | 3–4 days |
| R6 | Add a general XAI-GNN explainer inventory to §4.1 (PGExplainer, SubgraphX, GraphMask, GraphLIME/GraphSVX, CF-GNNExplainer/RCExplainer) so that the absence arguments in §5.3 and §6.1 gap six become checkable; narrow §1.2's stated scope to match delivered coverage | R2 W2, EIC W5 | Critical | §1.2, §4.1, §5.3, §6.1 | 2–3 days |
| R7 | Review Partin et al. (2026) substantively in the body (benchmark design, models, cross-dataset findings) and correct the false cross-reference in §2.2 pointing to a §2.1 discussion that does not exist | R2 W5, DA M5 | Major | §2.1/§2.4, §2.2 | 1 day |
| R8 | Resolve the internal contradiction between §2.2/§3.2 (cross-paper comparison unreliable) and §2.2/§5.1 (cross-paper performance ranking asserted): either attribute the ranking to its sources explicitly or qualify it by split protocol and scoring convention | DA M3, R1 W3 | Major | §2.2, §5.1 | 1 day |
| R9 | Add the faithfulness-vs-mechanism distinction (DA Unexamined Premise; R3 W3): state that a faithful attribution over confounded observational omics is not mechanistic evidence, and reframe §6.2's benchmark proposal accordingly, with perturbation data (CRISPR, LINCS/L1000) named as the causal-evidence tier | DA Unexamined Premise, R3 W3 | Major | §4.1 or §5.3; §6.2 | 2 days |
| R10 | Restructure §6.1, §6.2 and §7.1 from single paragraphs into numbered lists; add the two comparative tables (method×property; gap×evidence×remedy); box the §7.2 three-item checklist | EIC W4, R1, R2, R3 | Major | §6, §7 | 2 days |

### Required Item Details

**R2: Disclose the corpus construction and de-escalate the frontier claim**
- **Problem**: §1.3 discloses that the seed corpus was externally supplied and that search layer three was directed at the focal paper's neighbourhood; §4.2/§7.1 then report XGDP's frontier status as a finding. No limitation section exists and XGDP is never criticised.
- **Source**: DA C1/C3 ("a search targeted at a paper's neighbourhood will return that paper's neighbourhood"); EIC W2/W3.
- **Requirement**: (a) New Limitations subsection stating that the corpus began from an externally supplied seed set, that supplementary search was directed toward the XAI-GNN intersection, and that the review therefore characterises a corpus rather than establishing a field-level ranking. (b) Rewrite the §4.2 and §7.1 XGDP passages so that XGDP is an exemplar analysed in depth, with the normative claim carried by the §7.2 checklist. (c) One paragraph appraising XGDP's own limitations against that checklist.
- **Acceptance criteria**: The words "frontier," "unique," and "current frontier of rigor" no longer appear as unqualified claims about the field; at least three specific limitations of XGDP are stated; the Limitations subsection names the seed-corpus provenance explicitly.

**R3: Make the search reproducible**
- **Problem**: No database, query string, execution date, or screening count is reported; corpus arithmetic does not reconcile (18 seed with one title yielding two included papers ≠ 18).
- **Source**: R1 W1/W2.
- **Requirement**: Protocol subsection or appendix with databases queried, verbatim Boolean strings per database, execution dates, and a PRISMA-style flow with counts at each stage (identified / deduplicated / screened / full-text assessed / excluded with reasons / included), reported separately for the seed and supplementary streams. State which seed source was excluded and under which criterion.
- **Acceptance criteria**: A reader can re-execute the search from the text alone; every number in §1.3 reconciles with the reference list count of 36.

**R4: Extract before you synthesise**
- **Problem**: No structured extraction underlies the §5.1 robustness claims or the §7.2 exhaustiveness claim; no quantitative result from any reviewed method appears anywhere.
- **Source**: R1 W3/W5; DA C2/C4; EIC W4.
- **Requirement**: One extraction table covering all primary method papers. Then either re-derive §5.1's convergent findings and §7.2's "no method satisfies all three" claim from it, marking which rows support each, or withdraw both claims. Where a claim rests on a secondary survey rather than on extracted data, attribute it explicitly.
- **Acceptance criteria**: Every comparative or robustness claim in §5.1 and §7.2 traces to a table row or to a named attributed source; the table is included as a display item.

---

## Suggested Revisions (Should Fix)

| # | Revision Item | Source | Priority | Section | Expected Improvement |
|---|--------------|--------|----------|---------|---------------------|
| S1 | Add the faithfulness / plausibility / utility distinction and one human-centred XAI evaluation reference; state which target the §6.2 benchmark addresses | R3 W1 | P2 | §4.1, §6.2 | Gives explanation quality a defined standard |
| S2 | Anchor §7.2 to at least one regulatory framework (EU AI Act high-risk classification, FDA AI/ML guidance) and one clinical-prediction reporting standard (TRIPOD+AI) | R3 W2 | P2 | §7.2 | Makes the policy-titled section actually policy-informed |
| S3 | Tier the §6.2 validation recommendation by cost (database cross-check → public perturbation data → prospective wet-lab) and target the minimum standard at the cheapest tier | R3 W4 | P2 | §6.2 | Makes the recommended norm adoptable by ML-only groups |
| S4 | Address the rival hypothesis that the XAI-DRP subfield is small because predictions do not transfer, not because of adoption lag; state why the manuscript prefers its own explanation | DA Alt. 1 | P2 | §5.3, §6.1 | Removes an unexamined causal claim; strengthens gap two |
| S5 | Note GDSC/CCLE panel composition and its equity implications where the shared-substrate argument is made | R3 W5 | P3 | §5.1, §7.2 | Connects the generalization gap to clinical equity |
| S6 | Promote the §3.2 three-axis DSP split taxonomy to a figure or table | R2, DA Obs. | P3 | §3.2 | Foregrounds an under-displayed contribution |
| S7 | Split §1.2 and other 150+ word sentences; reduce paragraph length throughout §2 and §6 | EIC, R1 | P3 | Throughout | Readability |
| S8 | State whether §4.2's claim about explainer agreement varying by architecture is a reported quantitative result or an inference | R2 Q4, DA m4 | P3 | §4.2 | Removes an ambiguous evidential claim |
| S9 | Re-synchronise the Vietnamese translation after revision; fix the date typo `08/08/20263` | EIC | P3 | `tong_quan_tai_lieu.md` | Consistency of the bilingual record |

---

## Revision Roadmap

### Priority 1 — Structural and Evidentiary (est. 18–24 days)
- [ ] **R3**: Search protocol + PRISMA-style screening flow; reconcile corpus arithmetic *(do first — R4 and R5 depend on the corpus being settled)*
- [ ] **R5**: Add DRP/DSP landmark methods (DeepSynergy, DeepDDS, GraphDRP, DeepCDR, tCNNS, DrugCell)
- [ ] **R6**: Add general XAI-GNN explainer inventory; narrow §1.2 scope
- [ ] **R4**: Build extraction table; re-derive or withdraw §5.1 robustness and §7.2 exhaustiveness claims
- [ ] **R2**: Limitations subsection; de-escalate the XGDP frontier claim; appraise XGDP
- [ ] **R1**: Complete source verification; fix citations; fill metadata; remove "requester" language

### Priority 2 — Argument Repair and Content (est. 6–8 days)
- [ ] **R7**: Review Partin et al. (2026) in the body; fix the §2.2→§2.1 false cross-reference
- [ ] **R8**: Resolve the §2.2 / §5.1 comparability contradiction
- [ ] **R9**: Faithfulness-vs-mechanism distinction; reframe §6.2 around perturbation-grounded validation
- [ ] **S1**, **S2**, **S3**, **S4**: evaluation-target definition, regulatory anchor, cost-tiered validation, rival hypothesis

### Priority 3 — Presentation (est. 3–4 days)
- [ ] **R10**: Numbered lists for §6.1/§6.2/§7.1; two comparative tables; boxed §7.2 checklist
- [ ] **S5**–**S9**: equity note, §3.2 figure, sentence splitting, §4.2 clarification, Vietnamese re-sync

### Total Estimated Effort
**Major Revision: 5–7 weeks** (27–36 working days), assuming full-text access to the ~12 newly required sources.

**Critical path**: R3 → R4 → R2. The extraction table (R4) cannot be built before the corpus is settled (R3 and R5), and the frontier-claim revision (R2) should follow R4, since the extraction may show the claim is supportable after all — in which case it survives as a verified finding rather than a construction artefact.

---

## Revision Deadline

- **Recommended deadline**: 2026-09-30 (7 weeks)
- **Basis**: Major Revision standard is 6–8 weeks; the upper end is warranted because R5 and R6 require acquiring and reading roughly twelve new sources.
- **Re-review**: Required. Submit with a point-by-point response letter; run `/ars-reviewer re-review` (or the equivalent verification pass) against this roadmap.

---

## Closing

We encourage you to consider the reviewers' comments carefully and submit a substantially revised manuscript, which will undergo another round of review.

The panel was unanimous that this manuscript has a real contribution and is currently under-served by its own procedure. Three findings — the constrained-versus-post-hoc interpretability distinction, the three-axis DSP generalization taxonomy, and the coupling of explanation quality to out-of-distribution behaviour — survived adversarial challenge intact and are worth the work of a documented corpus and an honest limitations section. The most efficient path is the critical path above: settle the corpus, extract from it, and let the claims follow the extraction rather than the other way round.

---

## Appendix: Verification Log

| Citation | Claim checked | Result |
|----------|--------------|--------|
| Wang, C., Kumar, G. A., & Rajapakse, J. C. (2025). XGDP. *Scientific Reports, 15*, Article 179 | Venue, volume, article number, year | **Confirmed** — [nature.com/articles/s41598-024-83090-3](https://www.nature.com/articles/s41598-024-83090-3) |
| Wang, T., Wang, R., & Wei, L. (2023). AttenSyn. *JCIM, 64*(8), 2854–2862 | Year, volume, issue | **Error** — published 2024, *JCIM* **64**(7), 2854–2862; DOI as cited is correct. Year propagates to seven in-text citations |
| Corpus count: "18 seed + 18 supplementary = 36" | Internal arithmetic vs. disclosed duplicate resolution vs. reference-list count | **Inconsistent** — reference list contains exactly 36 entries; 18 seed titles with one resolving to two included papers implies 19; one seed source excluded without disclosure |
| §2.2 cross-reference: "Partin et al. (2026, discussed in Section 2.1…)" | Whether §2.1 discusses Partin et al. | **False cross-reference** — §2.1 discusses Okyere, Xiao, Dr.VAE, VAEN, scPreGAN only; Partin et al. is never described anywhere in the manuscript |

*Remaining 34 references were not independently verified in this review round; per R1 and the manuscript's own AI Disclosure, full verification remains an author obligation (roadmap item R1).*
