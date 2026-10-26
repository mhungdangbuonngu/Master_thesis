# Khảo sát: Explainable Graph Neural Networks cho bài toán dự đoán hiệp đồng thuốc (Drug Synergy Prediction)

> **Mục đích tài liệu.** Phục vụ việc mở rộng đề tài từ *drug response prediction* (DRP, bài toán một thuốc — một dòng tế bào) sang *drug synergy prediction* (DSP, bài toán hai thuốc — một dòng tế bào), vẫn giữ trục XAI trên đồ thị. Tài liệu gồm ba phần: (1) bản đồ các công trình tương tự, (2) đánh giá phê phán hiện trạng, (3) đề xuất hướng giải quyết cụ thể cho project.
>
> **Ngày lập:** 12/08/2026 · **Cập nhật:** điều chỉnh toàn bộ theo thiết lập **phân lớp 3 lớp** (synergistic / additive / antagonistic) — xem §1.1, §5.1, §6.2, §6.4, §6.5
> **Tài liệu liên quan:** [literature_review.md](literature_review.md), [review_report.md](review_report.md)

---

## 1. Đặt lại bài toán: vì sao DSP không phải là "DRP mở rộng"

Trước khi khảo sát, cần làm rõ một điểm mà phần lớn tài liệu bỏ qua và nó sẽ quyết định toàn bộ thiết kế của project.

| Khía cạnh | DRP (bài toán hiện tại) | DSP (bài toán mở rộng) |
|---|---|---|
| Đầu vào | (thuốc, dòng tế bào) | (thuốc A, thuốc B, dòng tế bào) — bộ ba |
| Đầu ra | IC50 / AUC / log-fold change | **Phân lớp 3 lớp: synergistic / additive (neutral) / antagonistic** — dẫn xuất từ synergy score (Loewe, Bliss, HSA, ZIP) |
| Bản chất đại lượng | Đo trực tiếp hiệu lực | **Đại lượng dư (residual)** so với một mô hình cộng tính giả định |
| Câu hỏi giải thích | "Gene/substructure nào khiến thuốc này hiệu quả?" | "Điều gì khiến A+B *vượt quá* tổng của A và B?" |
| Tính đối xứng | Không áp dụng | Bắt buộc: f(A,B,c) = f(B,A,c) |

Hệ quả quan trọng nhất: **synergy là một đại lượng tương tác (interaction), nên giải thích cho synergy phải là giải thích bậc tương tác, không phải giải thích bậc đơn thể.** Đây chính là lỗ hổng lớn nhất của toàn bộ literature hiện có (xem §3.4) và cũng là cơ hội tốt nhất cho project (xem §5).

### 1.1 Thiết lập cụ thể của project: phân lớp 3 lớp

Project đặt bài toán ở dạng **phân lớp 3 lớp** — tác động tốt (synergistic), xấu (antagonistic), trung tính (additive/neutral). Ngưỡng quy ước phổ biến nhất trong cộng đồng (theo SynergyFinder, áp dụng cho Loewe và ZIP):

```
score >  10   →  synergistic   (tốt)
-10 ≤ score ≤ 10   →  additive / neutral   (trung tính)
score < -10   →  antagonistic  (xấu)
```

Thiết lập này kéo theo bốn hệ quả mà toàn bộ phần còn lại của tài liệu đã được điều chỉnh theo.

**(a) Lớp trung tính chính là giả thuyết không (null hypothesis) — đây là lợi thế lớn, không phải phiền phức.**

Trong thiết lập nhị phân phổ biến (synergy vs. non-synergy), nhãn "không hiệp đồng" gộp chung cả cộng tính lẫn đối kháng. Đây là mất mát thông tin nghiêm trọng, vì hai thứ đó **trái ngược nhau về mặt lâm sàng**. Với 3 lớp, lớp additive chính là **mô hình cộng tính** mà synergy được định nghĩa dựa trên đó. Nghĩa là bài toán **tự mang sẵn mốc tham chiếu ngay trong không gian nhãn** — không cần dựng lại từ dữ liệu đơn trị liệu.

Điều này làm phương án A (§5.1) đơn giản đi đáng kể và về mặt lý thuyết còn sạch hơn phiên bản hồi quy.

**(b) Ba lớp có thứ tự (ordinal), không phải danh định (nominal).**

`antagonistic < additive < synergistic`. Nhầm *synergistic* thành *antagonistic* (nhầm hai cực) nghiêm trọng hơn hẳn nhầm *synergistic* thành *additive* (nhầm liền kề): một bên là khuyến nghị một tổ hợp gây hại, một bên chỉ là bỏ lỡ cơ hội.

**Cross-entropy thông thường phạt hai loại lỗi này như nhau** — đây là sai lầm thiết kế dễ mắc. Cần:
- Ordinal loss: CORAL / CORN, hoặc cumulative link model (ordinal logistic) trên đầu ra
- Hoặc tối thiểu: cost-sensitive cross-entropy với ma trận chi phí phạt nặng lỗi nhầm cực
- Và **bắt buộc** báo cáo Quadratic Weighted Kappa (QWK) — metric phạt lỗi theo bình phương khoảng cách thứ tự

**(c) Mất cân bằng lớp nghiêm trọng và bất đối xứng.**

Với ngưỡng ±10, lớp *additive* thường chiếm đa số áp đảo còn *antagonistic* là lớp thiểu số. Accuracy sẽ trở nên vô nghĩa (đoán tất cả là "trung tính" đã đạt độ chính xác cao). Bắt buộc: metric theo từng lớp, macro-F1, class weighting hoặc focal loss, và báo cáo **ma trận nhầm lẫn đầy đủ** chứ không chỉ số tổng hợp.

**(d) Không so sánh trực tiếp được với số liệu đã công bố — cảnh báo quan trọng.**

Gần như toàn bộ baseline ở §2 (DeepDDS, SynergyX, MD-Syn, AttenSyn, KGANSynergy…) làm **phân lớp nhị phân**, và nhiều bài còn chủ động **loại bỏ vùng trung tính** (chỉ giữ mẫu có |score| ≥ 10) để tăng độ tách bạch giữa hai lớp. Con số AUROC 0.919 của MD-Syn vì vậy **không cùng bài toán** với thiết lập của bạn — vùng khó nhất (ranh giới quanh 0) đã bị cắt bỏ khỏi tập đánh giá của họ.

→ Bắt buộc **tự chạy lại baseline dưới thiết lập 3 lớp**. Nên báo cáo song song cả kết quả nhị phân theo đúng giao thức gốc để hiệu chuẩn và chứng minh pipeline của mình đúng.

> **Ghi chú tận dụng:** chính điểm (d) lại là một đóng góp phụ dễ lấy — *"hiệu năng của các model DSP hiện tại sụt bao nhiêu khi phải phân biệt cả vùng trung tính?"* là câu hỏi chưa ai trả lời, và câu trả lời gần như chắc chắn là "sụt nhiều".

---

## 2. Bản đồ các công trình tương tự

Tôi phân loại theo **đơn vị giải thích** (unit of explanation) — tức là model trả lời "cái gì quan trọng" ở cấp độ nào — vì đây là tiêu chí phân biệt có ý nghĩa nhất khi so sánh, chứ không phải theo kiến trúc mạng.

### 2.1 Nhóm A — Giải thích ở cấp nguyên tử / cấu trúc con phân tử

Model học trên molecular graph của thuốc, giải thích bằng attention trên nguyên tử hoặc substructure.

| Công trình | Nguồn | Kiến trúc | Cách giải thích | Kiểm chứng giải thích |
|---|---|---|---|---|
| **DeepDDS** | *Briefings in Bioinformatics* 2022, 23(1):bbab390 | GCN/GAT trên molecular graph + MLP trên gene expression | Correlation matrix của atomic features → cấu trúc hóa học quan trọng | Chỉ định tính; không có metric faithfulness |
| **AttenSyn** | *J. Chem. Inf. Model.* 2024, 64(7):2854–2862 | Attention-based GNN, bilinear pooling | Trọng số attention trên nguyên tử | Case study định tính |
| **MD-Syn** | *Front. Pharmacol.* 2025, 16:1564339 | MOLFORMER (1D) + GCN & node2vec-PPI (2D) + graph-trans pooling, 4 attention head | Heatmap attention drug–gene; ánh xạ vùng attention cao về nhóm chức | Case study MK-2206 + MK-8669 → PAK6; UMAP clustering |
| **ResGIN-Att** | arXiv:2604.21473 (23/04/2026) | Residual GIN + LSTM + cross-attention | Cross-attention module xác định substructure then chốt | Chỉ tuyên bố, chưa thấy protocol đánh giá |
| **DPASyn** | arXiv:2505.19144 (05/2025, rev 09/2025) | Dual attention (intra-drug + cross-drug) + precision-aware quantization | — | **Đáng chú ý: bài tự nhận là "mechanism-aware" nhưng abstract không hề trình bày cơ chế giải thích nào.** Xem §3.1 |

**Nhận xét nhóm A.** Đây là nhóm đông nhất và cũng yếu nhất về mặt XAI. Giải thích cấp nguyên tử trả lời được "phân tử này có nhóm chức nào đáng chú ý" nhưng **không trả lời được câu hỏi hiệp đồng** — vì một nhóm chức của thuốc A không giải thích tại sao A cần B. MD-Syn là bài duy nhất trong nhóm cố gắng bắc cầu sang cấp gene (qua PPI), và cũng là bài trung thực nhất khi tự liệt kê giới hạn "atom-level interpretation may limit chemical understanding".

### 2.2 Nhóm B — Giải thích ở cấp gene / protein / pathway (mechanism-level)

Model đặt thuốc lên mạng sinh học (PPI, signaling pathway), giải thích bằng cách chỉ ra gene hoặc pathway then chốt. **Đây là nhóm gần với XGDP nhất và là nhóm đáng học hỏi nhất cho project.**

| Công trình | Nguồn | Kiến trúc | Cách giải thích | Kiểm chứng giải thích |
|---|---|---|---|---|
| **GraphSynergy** | *Bioinformatics* 2021 (PMID 34472609) | GCN mã hóa quan hệ topo bậc cao trong PPI của protein module đích | Attention component gán trọng số đóng góp cho từng protein | Đối chiếu literature, định tính |
| **IDSP** (Interpretable Deep Signaling Pathways) | arXiv:2105.07082 (2021), Dong, Zhang, Chen, Li | MLP học edge weight theo quan hệ gene–drug, inductive | Phát hiện signaling interaction quan trọng; salient pattern riêng cho từng dòng tế bào | Đối chiếu 46 core cancer pathway; **không dùng thông tin hóa học của thuốc** |
| **SANEpool** | *Cancers* 2023, 15(17):4210 | Hierarchical graph pooling, attention-based node/edge selection, top-k gene qua từng tầng | **Ante-hoc**: gán "synergic importance" cho gene = tỷ lệ gene được dùng khi cặp thuốc hiệp đồng | **Kolmogorov–Smirnov test trên 45 dòng tế bào, p < 0.05** — kiểm chứng thống kê hiếm hoi |
| **PathSynergy** | *Briefings in Bioinformatics* 2025, 26(2):bbaf192 | GAT + pathway mapping | Ánh xạ signaling pathway | Ứng dụng ung thư gan |
| **SynerGNet** | 2024 (PMC10967862) | GNN trên PPI người với cancer-specific featured graph | Đặc trưng sinh học tích hợp vào đồ thị | — |

**Nhận xét nhóm B.** SANEpool là **hình mẫu tốt nhất về mặt phương pháp luận** trong toàn bộ khảo sát: giải thích được thiết kế ngay trong kiến trúc (ante-hoc) chứ không gắn thêm sau, và quan trọng hơn — nó **được kiểm định thống kê** thay vì chỉ kể một case study đẹp. IDSP đáng chú ý ở chỗ chứng minh có thể dự đoán synergy tốt *chỉ từ signaling network*, không cần cấu trúc hóa học; điều này gợi ý rằng phần lớn tín hiệu hiệp đồng nằm ở mức mạng, không ở mức phân tử — một luận điểm quan trọng cho project.

### 2.3 Nhóm C — Giải thích qua attention đa phương thức (multi-modal / transformer)

| Công trình | Nguồn | Kiến trúc & dữ liệu | Cách giải thích | Kiểm chứng giải thích |
|---|---|---|---|---|
| **SynergyX** | *Briefings in Bioinformatics* 2024, 25(2):bbae015 | Cấu trúc "sandwich" 3 tầng: DCMA (drug–cell mutual attention) → DSSA/CSSA (self-attention) → DDMA/CCMA (mutual attention); ESPF encoding; **6 loại omics từ DepMap** (exp, mut, cn, met, eff, dep); 4,079 gene | Attention score từ DCMA và CCMA | **Định lượng: 62.2% số thuốc được kiểm tra có enrichment có ý nghĩa với gene đích đã biết**; pathway enrichment cho CCMA |
| **DTSyn** | 2022 | Two-branch Transformer encoder (molecule / protein / cell line) | Attention xuyên phương thức | Định tính |
| **MVCASyn** | *J. Comput. Sci. Technol.* 2025 | Multi-view learning + cross-attention | Cross-attention | — |

**Nhận xét nhóm C.** SynergyX là **baseline mạnh nhất hiện nay** cả về hiệu năng lẫn quy mô dữ liệu (DrugComb v1.5: 330,917 tổ hợp, 354 thuốc, 167 dòng tế bào; validation ngoài trên O'Neil, ALMANAC, Oncology Screen, DrugCombDB). Con số 62.2% là một trong rất ít nỗ lực **định lượng hóa** chất lượng giải thích trong lĩnh vực này — nhưng cần đọc kỹ: đó là "attention có trỏ đúng gene đích không", tức đo *plausibility* (tính hợp lý sinh học), **không phải** *faithfulness* (giải thích có phản ánh đúng cái model thực sự dùng không). Hai khái niệm này thường bị đánh đồng.

Tác giả SynergyX cũng thẳng thắn nêu một giới hạn rất đáng suy nghĩ: **dữ liệu có nhãn chỉ phủ 1.56% không gian dự đoán**.

### 2.4 Nhóm D — Knowledge graph & hypergraph (quan hệ bậc cao)

| Công trình | Nguồn | Ý tưởng chính | Tình trạng XAI |
|---|---|---|---|
| **KGANSynergy** | *Briefings in Bioinformatics* 2023, 24(3):bbad167 | Knowledge graph hierarchical propagation tìm neighbor đa nguồn; multi-attention phân biệt tầm quan trọng của neighbor | Attention trên neighbor — có tiềm năng giải thích nhưng chưa khai thác sâu |
| **HypergraphSynergy** | — | Coi bộ ba (thuốc, thuốc, dòng tế bào) là **một hyperedge** | Mô hình hóa đúng bản chất bậc ba, nhưng chưa có explainer tương ứng |
| **HANSynergy** | *J. Chem. Inf. Model.* 2024 | Heterogeneous graph attention network | Attention theo loại quan hệ |
| **SynergyGraph** | *Scientific Reports* 2025 | KG representation + hypergraph modeling, dự đoán synergy score theo dòng tế bào | — |
| **MGAE-DC** | *PLoS Comput. Biol.* 2023, 19(1):e1010951 | Multi-channel graph autoencoder | — |
| **HGTSynergy** | 2026 (PMC12870253) | Transfer learning trên DDI heterogeneous graph | — |

**Nhận xét nhóm D.** HypergraphSynergy là công trình **duy nhất mô hình hóa đúng cấu trúc bậc ba** của bài toán — nhưng lại **không có thành phần giải thích**. Đây là một khoảng trống rõ ràng và cụ thể: *chưa ai xây explainer cho hypergraph trong bài toán synergy*.

### 2.5 Nhóm E — Explainer chuyên biệt (chủ yếu vẫn ở phía DRP, chưa chuyển sang DSP)

Nhóm này quan trọng vì nó cho thấy **kỹ thuật XAI đã đi xa hơn ở phía DRP**, và đây chính là chỗ project có thể bắc cầu.

| Công trình | Nguồn | Đóng góp | Bài toán |
|---|---|---|---|
| **CETExplainer** | arXiv:2408.17129 (30/08/2024), Li, Gui, Gao, Shi, Yue | Post-hoc explainer với **edge-type-specific weighting có kiểm soát**; dùng mutual information giữa subgraph và prediction; **xây dựng ground truth để đánh giá định lượng chất lượng giải thích** | DRP |
| **DRPreter** | 2022 (PMC9699175) | Chia đồ thị dòng tế bào thành subgraph theo pathway + type-aware transformer phát hiện quan hệ pathway–thuốc | DRP |
| **XGDP** | *Sci. Rep.* 2025, 15, Art. 179 | GNN + GNNExplainer/IG cho cơ chế tác dụng thuốc | DRP |
| **CF-GNNExplainer** | arXiv:2102.03322 | Giải thích phản thực (counterfactual): tìm thay đổi nhỏ nhất làm đảo dự đoán | Tổng quát |
| **GCFExplainer** | *ACM TIST* 2024 | Counterfactual **toàn cục** (global), không chỉ từng mẫu | Tổng quát |

**Nhận xét nhóm E — điểm mấu chốt của cả khảo sát.** CETExplainer làm đúng cái mà toàn bộ literature DSP còn thiếu: **xây ground truth và đánh giá giải thích một cách định lượng**. Nhưng nó dừng ở DRP. Không có công trình tương đương ở phía DSP. Tương tự, giải thích phản thực (counterfactual) — vốn rất phù hợp với câu hỏi "bỏ gene nào đi thì hiệp đồng biến mất" — hầu như chưa được áp dụng cho DSP.

### 2.6 Tài liệu tổng quan nên đọc

| Tài liệu | Nguồn |
|---|---|
| A review of deep learning approaches for drug synergy prediction in cancer | *npj Drug Discovery* 2025 |
| A review on graph neural networks for predicting synergistic drug combinations | *Artificial Intelligence Review* 2024 |
| Explainable Artificial Intelligence in Drug Discovery: Bridging Predictive Power and Mechanistic Insight (Lavecchia) | *WIREs Comput. Mol. Sci.* 2025 |
| Deep learning for predicting synergistic drug combinations: State-of-the-arts and future directions (Wang et al.) | *Clinical and Translational Discovery* 2024 |
| Rethinking Attention-Model Explainability through Faithfulness Violation Test (Liu et al.) | *ICML* 2022, PMLR v162 |
| Reconsidering Faithfulness in Regular, Self-Explainable, and Domain Invariant GNNs | arXiv:2406.15156 |

---

## 3. Đánh giá phê phán hiện trạng

Đây là phần quan trọng nhất để định vị đóng góp của project. Tôi nêu sáu vấn đề, xếp theo mức độ nghiêm trọng.

### 3.1 Phần lớn "explainability" trong DSP là attention visualization, không phải giải thích đã được kiểm chứng

Đếm lại toàn bộ bảng ở §2: trong khoảng 18 công trình, **chỉ có SANEpool (KS test) và SynergyX (enrichment 62.2%) đưa ra bằng chứng định lượng** cho chất lượng giải thích. Số còn lại dừng ở heatmap attention kèm một case study được chọn lọc.

Đây không phải chi tiết nhỏ. Từ Jain & Wallace (2019) và Faithfulness Violation Test (ICML 2022), cộng đồng đã biết rằng **trọng số attention có thể bị hoán vị mà không làm thay đổi dự đoán** — nghĩa là attention cao không đảm bảo đó là thứ model thực sự dùng. Một số bài (điển hình DPASyn) tự gắn nhãn "mechanism-aware" cho kiến trúc dual-attention mà không hề trình bày quy trình giải thích nào; đây là **lạm dụng thuật ngữ**.

> **Hệ quả cho project:** không nên chỉ thêm attention rồi gọi đó là XAI. Đóng góp phải nằm ở chỗ *chứng minh* giải thích là trung thực.

### 3.2 Không có ground truth cho giải thích → đánh giá bằng case study là confirmation bias có hệ thống

Quy trình phổ biến hiện nay: chọn một vài cặp thuốc, xem gene/pathway nào có attention cao, tra literature, thấy có bài nói pathway đó liên quan ung thư → kết luận "model nắm được cơ chế".

Vấn đề: (a) cặp thuốc được chọn *sau khi* đã xem kết quả; (b) hầu hết pathway ung thư phổ biến (PI3K/AKT/mTOR, MAPK, p53) đều có literature ủng hộ, nên gần như *luôn* tìm được bằng chứng khớp; (c) không có trường hợp nào được báo cáo là "giải thích sai". Một phương pháp mà **không có khả năng bị bác bỏ** thì không phải là đánh giá.

CETExplainer là công trình hiếm hoi nhận ra và xử lý điều này bằng cách xây ground truth — nhưng cho DRP.

### 3.3 Đơn vị giải thích không thống nhất → các công trình không so sánh được với nhau

Nguyên tử/substructure (DeepDDS, MD-Syn, AttenSyn, ResGIN-Att) · gene/protein (GraphSynergy, SANEpool, SynerGNet) · pathway (IDSP, PathSynergy, DRPreter) · cross-modal attention (SynergyX, DTSyn).

Không có công trình nào so sánh chất lượng giải thích **giữa các cấp độ này trên cùng một backbone và cùng một split**. Vì vậy câu hỏi rất cơ bản — *"giải thích ở cấp nào là hữu ích nhất cho DSP?"* — vẫn chưa có ai trả lời.

### 3.4 Giải thích bậc đơn thể cho một bài toán bậc tương tác — lỗ hổng khái niệm lớn nhất

Đây là vấn đề nghiêm trọng nhất và là **cơ hội tốt nhất cho project**.

Synergy được định nghĩa là phần *dôi ra* so với mô hình cộng tính. Nhưng khi model highlight "nhóm pyrimidinone của 5-FU quan trọng" hay "gene EGFR có attention cao", nó đang giải thích cho *dự đoán tổng thể*, không phải cho *phần dôi ra*. Một gene có thể có attention rất cao đơn giản vì thuốc A tác động mạnh lên nó — điều đó chẳng nói gì về hiệp đồng.

Nói cách khác: **hiện chưa có công trình nào phân tách attribution thành phần "đơn trị liệu" và phần "tương tác".** Và về mặt lý thuyết thì công cụ đã sẵn có (Shapley interaction index, Integrated Hessians, interaction attribution) — chỉ là chưa ai mang sang bài toán này.

### 3.5 Nhãn synergy phụ thuộc reference model, nhưng chưa ai kiểm tra độ ổn định của giải thích qua các reference model

Loewe, Bliss, HSA, ZIP cho ra các nhãn khác nhau trên cùng dữ liệu thí nghiệm. MD-Syn tự nhận giới hạn này ("training relies on Loewe scoring method; different synergy quantification approaches yield inconsistent results"). Nhưng câu hỏi tiếp theo chưa ai hỏi:

> Nếu đổi từ Loewe sang Bliss, **giải thích có đổi không?** Nếu có, thì "cơ chế" mà model phát hiện ra là cơ chế sinh học hay chỉ là ảnh của một định nghĩa toán học?

Đây là một thí nghiệm rẻ, dễ làm, và kết quả dù theo hướng nào cũng có giá trị công bố.

### 3.6 Đánh giá generalization không đồng nhất và giải thích chưa từng được kiểm tra tính ổn định

Các split được dùng: random 5-fold, leave-drug-out, leave-cell-line-out, leave-drug-combination-out, leave-tissue-out. MD-Syn và SynergyX làm khá đầy đủ; nhiều bài khác chỉ báo cáo random split — vốn dễ rò rỉ thông tin vì cùng một cặp thuốc xuất hiện ở cả train và test với dòng tế bào khác nhau.

Nhưng kể cả các bài làm đầy đủ split cũng chỉ báo cáo **độ ổn định của hiệu năng**, chưa ai báo cáo **độ ổn định của giải thích** qua các seed, các fold, các split. Một explainer cho ra tập gene khác hẳn nhau giữa hai seed thì không dùng được trong thực tế.

### 3.7 Tóm tắt khoảng trống

| # | Khoảng trống | Mức độ khai thác được cho luận văn |
|---|---|---|
| G1 | Giải thích cho *phần tương tác*, không phải cho dự đoán tổng | ★★★ Cao — mới về khái niệm, khả thi |
| G2 | Bộ đánh giá định lượng chất lượng giải thích cho DSP (faithfulness, không chỉ plausibility) | ★★★ Cao — chắc chắn làm được, giá trị thực dụng lớn |
| G3 | Độ ổn định của giải thích qua reference model (Loewe/Bliss/ZIP/HSA) | ★★ Vừa — rẻ, dễ, kết quả nào cũng có giá trị |
| G4 | So sánh công bằng các XAI method trên cùng backbone/split cho DSP | ★★ Vừa — công sức lớn, novelty vừa phải |
| G5 | Explainer cho hypergraph / quan hệ bậc ba | ★★ Vừa — mới, nhưng rủi ro kỹ thuật cao |
| G6 | Counterfactual explanation cho synergy | ★★ Vừa — rất hợp với câu hỏi lâm sàng, nhưng không gian tìm kiếm lớn |

---

## 4. Những gì chuyển được và không chuyển được từ DRP sang DSP

| Thành phần | Chuyển được? | Ghi chú |
|---|---|---|
| Molecular graph encoder (GCN/GAT/GIN trên SMILES) | ✅ Trực tiếp | Chỉ cần hai nhánh chia sẻ trọng số (siamese) để đảm bảo tính đối xứng |
| Cell line encoder (omics → embedding) | ✅ Trực tiếp | Dùng lại nguyên vẹn |
| PPI / pathway graph | ✅ Trực tiếp | Dùng lại; nhưng cần thêm cạnh cho **cả hai** thuốc |
| GNNExplainer / Integrated Gradients | ⚠️ Chuyển được về mặt kỹ thuật | Nhưng **giải thích sai bài toán** — xem §3.4. Cần bọc thêm lớp interaction |
| Ground-truth cơ chế tác dụng (drug–target từ DrugBank) | ⚠️ Một phần | Có target cho từng thuốc, nhưng **không có ground truth cho cơ chế *hiệp đồng*** |
| Metric đánh giá (RMSE, Pearson với IC50) | ❌ Phải thay | Thiết lập 3 lớp cần QWK, macro-F1, per-class AUPRC — xem §6.5 |
| Hàm mất mát hồi quy (MSE) | ❌ Phải thay | Cần ordinal loss hoặc cost-sensitive cross-entropy — xem §1.1b |
| Giả định "một thuốc — một cơ chế" | ❌ Sụp đổ | Hiệp đồng thường đến từ *hai* pathway giao nhau |

---

## 5. Đề xuất hướng giải quyết cho project

Tôi đề xuất ba phương án, kèm khuyến nghị cụ thể ở cuối.

### 5.1 Phương án A (khuyến nghị làm trục chính) — Interaction-level Explanation cho DSP

**Ý tưởng cốt lõi.** Thay vì giải thích cho dự đoán, giải thích cho **độ lệch khỏi tính cộng tính**. Với thiết lập 3 lớp, điều này có một công thức rất gọn.

Gọi `z_syn`, `z_add`, `z_ant` là ba logit đầu ra của model cho một bộ ba (A, B, c). **Lớp trung tính chính là mốc tham chiếu**, nên định nghĩa hai logit tương phản:

```
Δ_syn = z_syn − z_add        (điều gì đẩy bộ ba này sang phía hiệp đồng)
Δ_ant = z_ant − z_add        (điều gì đẩy bộ ba này sang phía đối kháng)
```

Rồi tính attribution **trên logit tương phản** thay vì trên logit lớp:

```
φ_syn(g) = Attribution( Δ_syn , g )
φ_ant(g) = Attribution( Δ_ant , g )
```

với `g` là một gene / protein / cạnh trong đồ thị, và `Attribution` là Integrated Gradients, GNNExplainer hoặc CETExplainer.

Gene có `φ_syn` cao là gene **đẩy bộ ba ra khỏi trạng thái cộng tính về phía hiệp đồng** — đây mới đúng là cơ chế hiệp đồng, chứ không phải "gene mà thuốc A tác động mạnh".

**Vì sao thiết lập 3 lớp làm ý tưởng này mạnh hơn.** Ở phiên bản hồi quy, phải dựng mốc cộng tính bằng cách huấn luyện thêm nhánh đơn trị liệu rồi trừ attribution — vừa tốn công vừa khuếch đại nhiễu qua hai phép trừ. Ở đây **mốc cộng tính đã nằm sẵn trong không gian nhãn**: chỉ cần một phép trừ logit, thực hiện *bên trong* cùng một model, trên cùng một forward pass. Sạch hơn hẳn về mặt lý thuyết và rẻ hơn nhiều về mặt tính toán.

**Ba khẳng định có thể kiểm chứng (đây là phần làm luận văn đứng vững).** Ý tưởng trên chỉ có giá trị nếu chứng minh được `φ_syn` khác thật sự với attribution thông thường. Ba thí nghiệm:

1. **Tính phân kỳ.** So sánh top-k gene của `φ_syn` với top-k gene của attribution trên `z_syn` trực tiếp (cách làm của literature hiện tại). Nếu trùng nhau gần hết thì ý tưởng vô nghĩa — cần biết sớm. Kỳ vọng: overlap thấp, vì attribution trên `z_syn` bị chi phối bởi gene "thuốc mạnh" chung chung.
2. **Tính đặc hiệu.** Gene trong top-k của `φ_syn` phải **không** trùng nhiều với gene có `φ_ant` cao. Nếu một gene vừa đẩy sang hiệp đồng vừa đẩy sang đối kháng thì đó là gene đại diện cho "có tác động nói chung", không phải cơ chế.
3. **Tính đối lập.** Với các bộ ba được gán nhãn *antagonistic*, cơ chế phát hiện được phải khác về chất (khác pathway) so với bộ ba *synergistic* — chứ không chỉ đảo dấu. Đây là thí nghiệm mà thiết lập nhị phân **không thể làm được**, vì nó đã vứt bỏ lớp đối kháng.

Điểm 3 chính là chỗ thiết lập 3 lớp của bạn tạo ra lợi thế mà không bài nào trong §2 có.

**Nhánh đơn trị liệu — vẫn nên giữ, nhưng ở vai trò khác.** Không còn bắt buộc để tính mốc tham chiếu, nhưng vẫn hữu ích làm **giám sát phụ trợ (auxiliary supervision)**: buộc backbone học biểu diễn phản ánh hiệu lực đơn thuốc giúp phần tương tác được tách bạch hơn. Đây trở thành một mục trong ablation study chứ không phải thành phần bắt buộc — **giảm rủi ro của project đáng kể**, vì không còn phụ thuộc vào việc O'Neil có đủ dữ liệu đơn trị liệu cho mọi cặp hay không.

**Vì sao đây là đóng góp thật.** Không công trình nào trong §2 làm điều này. Giải quyết trực tiếp G1. Có nền tảng lý thuyết (Shapley interaction index, Integrated Hessians, contrastive attribution) chứ không phải heuristic tự nghĩ.

**Rủi ro và cách phòng.** Hiệu logit có thể nhiễu ở vùng ranh giới (score gần ±10, nơi model không chắc chắn). Phòng bằng: (a) trung bình attribution qua nhiều seed; (b) chỉ xét mẫu có độ tin cậy dự đoán trên ngưỡng; (c) báo cáo khoảng tin cậy bootstrap; (d) phân tích riêng nhóm mẫu gần ranh giới — chính nhóm này mới là nơi thú vị nhất về mặt khoa học.

### 5.2 Phương án B (làm chương thực nghiệm nền, rủi ro thấp) — Benchmark chất lượng giải thích cho DSP

Chuyển kiến trúc kiểu XGDP sang DSP, rồi **so sánh có hệ thống** các phương pháp XAI trên **cùng một backbone, cùng một split, cùng một bộ metric**:

- Phương pháp so sánh: attention weights · GNNExplainer · Integrated Gradients · SHAP · CETExplainer (chuyển từ DRP sang) · counterfactual
- Metric **faithfulness** (giải thích có phản ánh đúng model không): Fidelity+, Fidelity−, Sparsity, Comprehensiveness, Sufficiency
- Metric **stability**: Jaccard index của top-k gene qua 5 seed và qua các fold
- Metric **plausibility**: enrichment với KEGG/Reactome pathway và DrugBank target
- **Faithfulness violation test** (Liu et al., ICML 2022) — bài kiểm tra mà attention thường trượt

Giải quyết G2 và G4. Novelty vừa phải nhưng **rất chắc chắn ra kết quả**, và là nền để phương án A đứng lên. Nếu A gặp trục trặc, riêng B đã đủ làm một luận văn.

### 5.3 Phương án C (mở rộng nếu còn thời gian) — Counterfactual Synergy Explanation

Câu hỏi: *"Thay đổi nhỏ nhất nào làm cặp thuốc này mất tính hiệp đồng?"* — ví dụ knock-out một gene khỏi PPI subgraph, hoặc thay một nhóm chức trên phân tử.

Dùng CF-GNNExplainer / GCFExplainer. Đây là dạng giải thích **gần với câu hỏi lâm sàng thật** nhất (bệnh nhân mang đột biến gene X thì tổ hợp này còn hiệu quả không?). Rủi ro: không gian tìm kiếm rất lớn, dễ sinh ra phản thực vô nghĩa về mặt hóa học. Nên giới hạn ở phản thực trên **gene/PPI** thay vì trên cấu trúc phân tử.

### 5.4 Khuyến nghị

> **B làm nền → A làm trục chính → C làm phần mở rộng.**
>
> Lý do: B đảm bảo luận văn có kết quả dù A thất bại; A tạo ra đóng góp khái niệm để bảo vệ; C là phần "nice to have" cho câu hỏi phản biện của hội đồng.

---

## 6. Thiết kế thực nghiệm cụ thể

### 6.1 Dữ liệu

| Loại | Nguồn đề xuất | Ghi chú |
|---|---|---|
| Tổ hợp thuốc (chính) | **O'Neil** — 13,243 bộ ba, 38 thuốc, 31 dòng tế bào | **Bắt buộc chọn** vì có kèm dữ liệu đơn trị liệu → điều kiện cần cho phương án A |
| Tổ hợp thuốc (mở rộng) | DrugComb v1.5 (330,917 tổ hợp) | Dùng để kiểm tra khả năng mở rộng |
| Validation ngoài | NCI-ALMANAC, DrugCombDB, Oncology Screen | Theo đúng thiết lập của SynergyX để so sánh công bằng |
| Omics dòng tế bào | CCLE / DepMap; 978 landmark gene của LINCS L1000 | Có thể mở rộng lên 6 loại omics như SynergyX |
| Mạng PPI | STRING (hoặc HumanNet) | |
| Pathway | KEGG, Reactome | Dùng làm ground truth proxy cho enrichment |
| Drug–target | DrugBank, STITCH | |

### 6.2 Nhãn và ngưỡng phân lớp

Tính **cả bốn** reference model: Loewe, Bliss, HSA, ZIP. Huấn luyện chính trên Loewe với ngưỡng ±10 (quy ước SynergyFinder), rồi chạy thí nghiệm chéo để trả lời G3.

**Phân tích độ nhạy theo ngưỡng — bắt buộc.** Ngưỡng ±10 là quy ước, không phải hằng số sinh học. Cần chạy ít nhất ba cấu hình và báo cáo cả ba:

| Ngưỡng | Đặc điểm | Vai trò |
|---|---|---|
| ±5 | Lớp trung tính hẹp, ba lớp cân bằng hơn, nhiều nhiễu thí nghiệm lọt vào hai cực | Kiểm tra tính bền |
| **±10** | Quy ước chuẩn | **Cấu hình chính** |
| ±20 | Lớp trung tính rất rộng, hai cực rất "sạch" nhưng cực kỳ mất cân bằng | Kiểm tra giới hạn trên |

Câu hỏi cần trả lời rõ trong luận văn: **giải thích do model sinh ra có ổn định khi đổi ngưỡng không?** Nếu tập gene then chốt thay đổi hoàn toàn khi chuyển từ ±5 sang ±20, thì "cơ chế" phát hiện được phần lớn là ảnh của một lựa chọn quy ước, chứ không phải sinh học. Đây là thí nghiệm rẻ và kết quả theo hướng nào cũng đáng công bố.

**Xử lý mẫu ranh giới.** Bộ ba có score sát ngưỡng (ví dụ 9.8 vs 10.2) bị gán hai nhãn khác nhau dù về mặt thí nghiệm gần như không phân biệt được. Hai cách xử lý, nên thử cả hai: (a) giữ nguyên và chấp nhận nhiễu nhãn; (b) dùng label smoothing hoặc soft label theo khoảng cách tới ngưỡng. Cách (b) hợp với bản chất ordinal hơn.

### 6.3 Chia dữ liệu — bắt buộc báo cáo đầy đủ

1. Random 5-fold (để đối chiếu với các bài đã công bố)
2. **Leave-drug-out** — thuốc mới
3. **Leave-cell-line-out** — dòng tế bào mới
4. **Leave-drug-combination-out** — cặp thuốc mới
5. Leave-tissue-out — loại mô mới (khó nhất)

Không được chỉ báo cáo random split. Đây là lỗi phổ biến khiến kết quả bị thổi phồng.

### 6.4 Baseline so sánh

DeepSynergy (nền tảng, MLP) · DeepDDS · GraphSynergy · KGANSynergy · SynergyX (**SOTA hiện tại**) · MD-Syn · HypergraphSynergy

**Lưu ý bắt buộc về tính công bằng (xem §1.1d).** Các baseline trên đều công bố kết quả **nhị phân**, phần lớn còn loại bỏ vùng trung tính. **Không được chép số từ bài gốc vào bảng so sánh của mình.** Quy trình đúng:

1. Chạy lại từng baseline dưới thiết lập 3 lớp của mình (thay tầng đầu ra thành 3 nơ-ron, giữ nguyên backbone)
2. Đồng thời tái lập kết quả nhị phân theo đúng giao thức gốc để **chứng minh pipeline của mình đúng** — nếu tái lập ra số gần với bài gốc thì bảng 3 lớp mới đáng tin
3. Báo cáo cả hai bảng; chênh lệch giữa chúng chính là đóng góp phụ đã nêu ở §1.1

Thêm hai baseline tầm thường nhưng bắt buộc phải có vì dữ liệu mất cân bằng:
- **Majority class** — luôn đoán "trung tính"
- **Chỉ dùng đặc trưng dòng tế bào** (bỏ thông tin thuốc) — nếu baseline này đã gần bằng model chính thì model đang học đặc điểm dòng tế bào chứ không học tương tác thuốc. Đây là bài kiểm tra rất dễ bỏ sót và rất hay bị hội đồng hỏi.

### 6.5 Metric

Vì bài toán là **phân lớp 3 lớp có thứ tự và mất cân bằng**, bộ metric phải khác hẳn thông lệ nhị phân của literature.

| Nhóm | Metric | Ghi chú |
|---|---|---|
| **Chính (ordinal)** | **Quadratic Weighted Kappa (QWK)** | Metric chủ đạo — phạt lỗi theo bình phương khoảng cách thứ tự, phù hợp cả với dữ liệu mất cân bằng |
| Tổng hợp | Macro-F1, Balanced Accuracy (BACC), Macro-AUROC (one-vs-rest) | **Không dùng accuracy thường** — vô nghĩa khi lớp trung tính áp đảo |
| Theo từng lớp | Precision / Recall / F1 / AUPRC riêng cho synergistic, additive, antagonistic | Bắt buộc. Lớp *antagonistic* thường là lớp yếu nhất và cũng quan trọng nhất về mặt an toàn |
| Cấu trúc lỗi | **Ma trận nhầm lẫn đầy đủ**, tách riêng tỷ lệ *lỗi liền kề* (syn↔add, add↔ant) và *lỗi nhầm cực* (syn↔ant) | Lỗi nhầm cực phải báo cáo riêng — đây là loại lỗi nguy hiểm về mặt lâm sàng |
| Hồi quy (phụ) | RMSE, Pearson r, Spearman ρ trên synergy score gốc | Chạy như nhiệm vụ phụ để đối chiếu với literature |
| Faithfulness của giải thích | Fidelity+, Fidelity−, Sparsity, Comprehensiveness, Sufficiency, Faithfulness Violation Test | Tính **riêng cho từng lớp** |
| Stability của giải thích | Jaccard@k qua seed, qua fold, **và qua ngưỡng phân lớp** (§6.2) | Chiều "qua ngưỡng" là chiều mới, chưa ai báo cáo |
| Plausibility | Enrichment với KEGG/Reactome (Fisher exact / hypergeometric), overlap với DrugBank target | |

**Ba lưu ý quan trọng:**

1. Phải báo cáo faithfulness và plausibility **tách riêng**. Gộp chung là lỗi mà phần lớn literature hiện nay mắc phải (§3.1).
2. **Giải thích cho lớp trung tính gần như vô nghĩa** — "gene nào khiến cặp thuốc này *không* tương tác" là câu hỏi thoái hóa. Chỉ đánh giá chất lượng giải thích trên lớp *synergistic* và *antagonistic*; nêu rõ điều này trong phần phương pháp thay vì để hội đồng phát hiện.
3. Fidelity+/− vốn được định nghĩa cho phân lớp nên **áp dụng trực tiếp được** — đây là một lợi thế của thiết lập 3 lớp so với hồi quy, nơi các metric này phải chế lại.

---

## 7. Rủi ro chính và cách phòng

| Rủi ro | Mức độ | Cách phòng |
|---|---|---|
| **Lớp *antagonistic* quá ít mẫu để học** | **Cao** | Class weighting / focal loss; gộp thêm dữ liệu đối kháng từ DrugComb và ALMANAC; nếu vẫn quá ít thì **báo cáo trung thực là lớp này chưa đủ dữ liệu** thay vì che bằng metric tổng hợp |
| Model học "đoán trung tính" để tối ưu loss | Cao | Theo dõi macro-F1 và QWK trong quá trình huấn luyện thay vì loss; đối chiếu với baseline majority class (§6.4) |
| Kết quả nhạy với ngưỡng ±10 | Vừa–Cao | Phân tích độ nhạy ba ngưỡng (§6.2); soft label cho mẫu ranh giới |
| Hiệu logit `Δ` nhiễu ở vùng ranh giới | Vừa | Trung bình qua nhiều seed; bootstrap CI; lọc theo độ tin cậy dự đoán; phân tích riêng nhóm ranh giới |
| Dữ liệu đơn trị liệu trong O'Neil không phủ hết các cặp | **Thấp** (đã giảm) | Với công thức logit tương phản, nhánh đơn trị liệu chỉ còn là giám sát phụ trợ trong ablation (§5.1) |
| Không có ground truth thật cho cơ chế hiệp đồng | Cao | Dùng proxy (shared pathway, known synergy mechanism từ literature) và **nói rõ đây là proxy**, không được trình bày như ground truth thật |
| Chi phí tính toán của interaction attribution | Vừa | Giới hạn ở top-k gene; dùng sampling cho Shapley |
| Không đánh bại được SynergyX về AUROC | Vừa | **Không đặt mục tiêu là SOTA hiệu năng.** Đóng góp nằm ở chất lượng giải thích — nêu rõ điều này ngay từ phần Introduction |
| Hội đồng hỏi "giải thích này có ý nghĩa lâm sàng không" | Vừa | Chuẩn bị 2–3 case study có kiểm chứng ngoài (wet-lab literature độc lập), và **cả một case study mà model giải thích sai** — sự trung thực này làm mạnh luận văn |

---

## 8. Lộ trình gợi ý

| Giai đoạn | Nội dung | Đầu ra |
|---|---|---|
| **GĐ 1** (3–4 tuần) | Dựng pipeline dữ liệu O'Neil + CCLE + STRING/KEGG; tái lập DeepDDS và GraphSynergy làm baseline | Bộ dữ liệu sạch + 2 baseline chạy được |
| **GĐ 2** (4–5 tuần) | Backbone 3 lớp với ordinal loss + xử lý mất cân bằng; hai nhánh thuốc chia sẻ trọng số đảm bảo đối xứng; đủ 5 kiểu split | Model chính + bảng hiệu năng đầy đủ (QWK, macro-F1, per-class, ma trận nhầm lẫn) |
| **GĐ 3** (4–5 tuần) | Triển khai bộ metric XAI (Phương án B) — so sánh attention / GNNExplainer / IG / SHAP / CETExplainer, tính riêng cho lớp *synergistic* và *antagonistic* | Bảng benchmark giải thích — **chương chắc chắn có kết quả** |
| **GĐ 4** (4–6 tuần) | Attribution trên logit tương phản (Phương án A) + ba thí nghiệm kiểm chứng §5.1; thí nghiệm chéo reference model và chéo ngưỡng (G3) | Đóng góp chính của luận văn |
| **GĐ 5** (2–3 tuần) | Case study + phản thực (Phương án C nếu kịp); viết báo cáo | Bản thảo hoàn chỉnh |

---

## 9. Tài liệu tham khảo

**Nhóm A — giải thích cấp phân tử**
1. Wang J. et al. DeepDDS: deep graph neural network with attention mechanism to predict synergistic drug combinations. *Briefings in Bioinformatics* 2022;23(1):bbab390. https://academic.oup.com/bib/article/23/1/bbab390/6375262 · arXiv: https://arxiv.org/abs/2107.02467
2. AttenSyn: An Attention-Based Deep Graph Neural Network for Anticancer Synergistic Drug Combination Prediction. *J. Chem. Inf. Model.* 2024;64(7):2854–2862. https://pubs.acs.org/doi/10.1021/acs.jcim.3c00709
3. MD-Syn: synergistic drug combination prediction based on a multidimensional feature fusion method and attention mechanisms. *Front. Pharmacol.* 2025;16:1564339. https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2025.1564339/full
4. Song J. et al. Drug Synergy Prediction via Residual Graph Isomorphism Networks and Attention Mechanisms. arXiv:2604.21473 (2026). https://arxiv.org/abs/2604.21473
5. Nie Y. et al. DPASyn: Mechanism-Aware Drug Synergy Prediction via Dual Attention and Precision-Aware Quantization. arXiv:2505.19144 (2025). https://arxiv.org/abs/2505.19144

**Nhóm B — giải thích cấp gene / pathway**
6. Yang J. et al. GraphSynergy: a network-inspired deep learning model for anticancer drug combination prediction. *Bioinformatics* 2021. https://pubmed.ncbi.nlm.nih.gov/34472609/
7. Dong Z., Zhang H., Chen Y., Li F. Interpretable Drug Synergy Prediction with Graph Neural Networks for Human-AI Collaboration in Healthcare (IDSP). arXiv:2105.07082 (2021). https://arxiv.org/abs/2105.07082
8. Interpreting the Mechanism of Synergism for Drug Combinations Using Attention-Based Hierarchical Graph Pooling (SANEpool). *Cancers* 2023;15(17):4210. https://pmc.ncbi.nlm.nih.gov/articles/PMC10486573/
9. PathSynergy: a deep learning model for predicting drug synergy in liver cancer. *Briefings in Bioinformatics* 2025;26(2):bbaf192. https://academic.oup.com/bib/article/26/2/bbaf192/8119326
10. SynerGNet: A Graph Neural Network Model to Predict Anticancer Drug Synergy. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/

**Nhóm C — attention đa phương thức**
11. SynergyX: a multi-modality mutual attention network for interpretable drug synergy prediction. *Briefings in Bioinformatics* 2024;25(2):bbae015. https://academic.oup.com/bib/article/25/2/bbae015/7604885
12. MVCASyn: Predicting Synergistic Drug Combinations Based on Multi-View Learning and Cross-Attention Mechanism. *J. Comput. Sci. Technol.* 2025. https://link.springer.com/article/10.1007/s11390-025-4928-8

**Nhóm D — knowledge graph & hypergraph**
13. KGANSynergy: knowledge graph attention network for drug synergy prediction. *Briefings in Bioinformatics* 2023;24(3):bbad167. https://academic.oup.com/bib/article/24/3/bbad167/7147878
14. HANSynergy: Heterogeneous Graph Attention Network for Drug Synergy Prediction. *J. Chem. Inf. Model.* 2024. https://pubs.acs.org/doi/10.1021/acs.jcim.4c00003
15. SynergyGraph: predicting cell line specific drug combination synergy scores using knowledge graph representation and hypergraph modeling. *Scientific Reports* 2025. https://www.nature.com/articles/s41598-025-33581-8
16. MGAE-DC: Predicting the synergistic effects of drug combinations through multi-channel graph autoencoders. *PLoS Comput. Biol.* 2023. https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1010951

**Nhóm E — explainer chuyên biệt**
17. Li X., Gui J., Gao Q., Shi H., Yue Z. Controllable Edge-Type-Specific Interpretation in Multi-Relational Graph Neural Networks for Drug Response Prediction (CETExplainer). arXiv:2408.17129 (2024). https://arxiv.org/abs/2408.17129
18. DRPreter: Interpretable Anticancer Drug Response Prediction Using Knowledge-Guided Graph Neural Networks and Transformer. https://pmc.ncbi.nlm.nih.gov/articles/PMC9699175/
19. Lucic A. et al. CF-GNNExplainer: Counterfactual Explanations for Graph Neural Networks. arXiv:2102.03322. https://arxiv.org/pdf/2102.03322
20. GCFExplainer: Global Counterfactual Explainer for Graph Neural Networks. *ACM TIST* 2024. https://dl.acm.org/doi/10.1145/3698108

**Đánh giá chất lượng giải thích**
21. Liu Y. et al. Rethinking Attention-Model Explainability through Faithfulness Violation Test. *ICML* 2022, PMLR v162. https://proceedings.mlr.press/v162/liu22i/liu22i.pdf
22. Towards Faithful and Consistent Explanations for Graph Neural Networks. arXiv:2205.13733. https://arxiv.org/pdf/2205.13733
23. Reconsidering Faithfulness in Regular, Self-Explainable, and Domain Invariant GNNs. arXiv:2406.15156. https://arxiv.org/html/2406.15156

**Phân lớp ordinal, mất cân bằng lớp và ngưỡng synergy**
24. SynergyFinder Documentation — quy ước ngưỡng ±10 cho Loewe/ZIP và bốn reference model (HSA, Bliss, Loewe, ZIP). https://synergyfinder.aittokallio.group/synfin_docs/
25. Yadav B. et al. Searching for Drug Synergy in Complex Dose-Response Landscapes Using an Interaction Potency Model (ZIP). https://pubmed.ncbi.nlm.nih.gov/26949479/
26. Weighted kappa measures for ordinal multi-class classification performance. *Applied Soft Computing* 2023. https://www.sciencedirect.com/science/article/pii/S1568494623000388
27. Vargas V.M. et al. Cumulative link models for deep ordinal classification. arXiv:1905.13392. https://arxiv.org/pdf/1905.13392
28. Distribution Consistency Penalty in the Quadratic Kappa Loss for Ordinal Regression of Imbalanced Datasets. *ACM* 2022. https://dl.acm.org/doi/fullHtml/10.1145/3507548.3507612
29. Class Distance Weighted Cross-Entropy Loss — hàm mất mát phạt theo khoảng cách lớp cho bài toán ordinal. arXiv:2202.05167. https://arxiv.org/pdf/2202.05167

**Tổng quan**
30. A review of deep learning approaches for drug synergy prediction in cancer. *npj Drug Discovery* 2025. https://www.nature.com/articles/s44386-025-00034-1
31. A review on graph neural networks for predicting synergistic drug combinations. *Artificial Intelligence Review* 2024. https://link.springer.com/article/10.1007/s10462-023-10669-z
32. Lavecchia A. Explainable Artificial Intelligence in Drug Discovery: Bridging Predictive Power and Mechanistic Insight. *WIREs Comput. Mol. Sci.* 2025. https://wires.onlinelibrary.wiley.com/doi/10.1002/wcms.70049
33. Wang et al. Deep learning for predicting synergistic drug combinations: State-of-the-arts and future directions. *Clinical and Translational Discovery* 2024. https://onlinelibrary.wiley.com/doi/full/10.1002/ctd2.317

---

## Phụ lục: lưu ý về độ tin cậy của tài liệu này

- Thông tin về **SynergyX, SANEpool, MD-Syn, IDSP, CETExplainer, DeepDDS, ResGIN-Att, DPASyn** được lấy trực tiếp từ bài gốc (số liệu dataset, split, cách kiểm chứng giải thích đều đã đối chiếu).
- Thông tin về **GraphSynergy, DTSyn, HypergraphSynergy, HANSynergy, SynergyGraph, MGAE-DC, HGTSynergy, MVCASyn, PathSynergy, SynerGNet** dựa trên abstract và mô tả trong các bài tổng quan — **cần đọc lại bản đầy đủ trước khi trích dẫn vào luận văn**.
- Các ô để trống "—" trong bảng nghĩa là **chưa xác minh**, không phải "không có".
- Mục §3 (đánh giá phê phán) là phân tích của tôi dựa trên đối chiếu chéo các bài trên, không phải trích dẫn từ một nguồn duy nhất — nếu đưa vào luận văn cần tự kiểm chứng lại từng luận điểm.
