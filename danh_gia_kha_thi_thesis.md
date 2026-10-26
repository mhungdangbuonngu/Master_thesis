# Đánh giá tính khả thi của đề tài luận văn: Explainable GNN cho dự đoán hiệp đồng thuốc 3 lớp

**Ngày lập:** 01/10/2026
**Chế độ:** `deep-research` — quick mode (research brief), có tra cứu bổ sung để kiểm chứng
**Đầu vào đã đọc:** [khao_sat_xai_graph_drug_synergy.md](khao_sat_xai_graph_drug_synergy.md), [literature_review.md](literature_review.md), [tong_quan_tai_lieu.md](tong_quan_tai_lieu.md), [review_report.md](review_report.md)
**Tuyên bố sử dụng AI:** Tài liệu này do công cụ AI hỗ trợ soạn. Các nhận định mới (đánh dấu **[Mới]**) đã được đối chiếu với nguồn ở mục Tài liệu tham khảo; các phần còn lại là tổng hợp và phân tích, cần bạn tự kiểm chứng lại trước khi đưa vào luận văn.

---

## Tóm tắt

Đề tài **khả thi, nhưng có điều kiện**. Dữ liệu, công cụ và tài nguyên tính toán đều sẵn có, và phương án B (benchmark chất lượng giải thích) gần như chắc chắn cho ra kết quả. Tuy vậy có ba vấn đề cần sửa **trước khi bắt đầu code**:

1. **Lỗi khái niệm ở trục chính (phương án A).** Logit tương phản `Δ_syn = z_syn − z_add` lấy lớp *additive* trong **không gian nhãn** làm mốc. Nó không loại bỏ được hiệu ứng đơn trị liệu trong **không gian đầu vào**. Attribution trên `Δ_syn` vì vậy **chưa phải** là giải thích bậc tương tác như tài liệu khảo sát đang tuyên bố.
2. **Tuyên bố mới (novelty) cần viết lại.** Đã có công trình tách attribution tương tác cho tổ hợp thuốc: Integrated Hessians (Janizek và cộng sự, 2021) và EXPRESS (*Nature Biomedical Engineering*, 2023). Câu "chưa có công trình nào phân tách attribution đơn trị liệu và tương tác" (khảo sát §3.4) là **không đúng**. Vẫn còn khoảng trống thật để khai thác, nhưng hẹp hơn.
3. **Bộ dữ liệu ghi trong kế hoạch không dùng được cho bài toán 3 lớp.** Bộ "O'Neil 13,243 bộ ba" là bản đã tiền xử lý của DeepDDS, và bản này **đã bỏ vùng 0–10**. Cần lấy lại điểm Loewe gốc (~23 nghìn bộ ba) từ DrugComb hoặc từ bản phát hành của DeepSynergy.

Sửa ba điểm này xong thì đề tài vẫn giữ được đóng góp có thể bảo vệ. Phần còn lại của tài liệu trình bày chi tiết và đưa ra workflow cụ thể có các mốc quyết định đi tiếp hay dừng (go/no-go).

---

## Phần 1 — Tường thuật lại dự định đề tài

### 1.1 Hướng đi đã thay đổi thế nào

| Giai đoạn | Trọng tâm | Tài liệu |
|---|---|---|
| Ban đầu | **DRP** (một thuốc, một dòng tế bào), lấy XGDP (Wang, Kumar & Rajapakse, 2025) làm mốc: GNN kết hợp GNNExplainer/IG để giải thích cơ chế tác dụng thuốc | `literature_review.md`, `tong_quan_tai_lieu.md` |
| Phản biện | Hội đồng phản biện giả lập cho kết luận *Major Revision*. Phản biện viên Devil's Advocate nêu ra **tiền đề chưa được kiểm tra**: *giải thích trung thực với model (faithful) ≠ bằng chứng cơ chế sinh học* | `review_report.md` |
| Hiện tại | Mở rộng sang **DSP** (hai thuốc, một dòng tế bào), vẫn giữ trục XAI trên đồ thị, đặt thành **bài toán phân lớp 3 lớp có thứ tự** | `khao_sat_xai_graph_drug_synergy.md` |

### 1.2 Bài toán

- **Đầu vào:** bộ ba (thuốc A, thuốc B, dòng tế bào c). Thuốc biểu diễn bằng molecular graph; dòng tế bào biểu diễn bằng omics trên PPI/pathway graph.
- **Đầu ra:** `antagonistic < additive < synergistic`, lấy ngưỡng ±10 trên điểm Loewe (theo quy ước của SynergyFinder).
- **Ràng buộc:** đối xứng f(A,B,c) = f(B,A,c), dùng loss ordinal (CORAL/CORN hoặc cost-sensitive CE), metric chính là QWK cùng macro-F1, per-class AUPRC và ma trận nhầm lẫn.

### 1.3 Câu hỏi nghiên cứu (diễn đạt lại theo kế hoạch hiện có)

> **RQ chính:** Có thể giải thích một model GNN dự đoán hiệp đồng thuốc 3 lớp ở **mức tương tác**, tức là chỉ ra cái gì khiến A+B lệch khỏi tính cộng tính, một cách **trung thực, ổn định và có thể kiểm chứng định lượng** hay không?

Ba câu hỏi phụ:
- **RQ1 (phương án B):** Trên cùng backbone, cùng split và cùng bộ metric, các phương pháp XAI (attention, GNNExplainer, IG, SHAP, CETExplainer) xếp hạng thế nào về faithfulness, stability và plausibility?
- **RQ2 (phương án A):** Attribution "hướng tới phần tương tác" có khác thật sự so với attribution trên dự đoán tổng thể không, và cơ chế của bộ ba hiệp đồng có khác về chất so với bộ ba đối kháng không?
- **RQ3 (G3):** Giải thích có ổn định khi đổi reference model (Loewe/Bliss/HSA/ZIP) và khi đổi ngưỡng (±5/±10/±20) không?

### 1.4 Chiến lược đã đề ra

- **B làm nền → A làm trục chính → C (counterfactual) làm phần mở rộng.**
- **Không** đặt mục tiêu đạt SOTA về hiệu năng. Đóng góp nằm ở chất lượng giải thích.
- Lộ trình 5 giai đoạn, tổng cộng 17–23 tuần (khảo sát §8).

---

## Phần 2 — Đánh giá tính khả thi

### 2.1 Chấm điểm FINER

| Tiêu chí | Đánh giá | Ghi chú |
|---|---|---|
| **F**easible (khả thi) | ⚠️ Có điều kiện | Dữ liệu, công cụ và GPU đều đủ. Phạm vi thực nghiệm hiện tại **quá rộng** so với 17–23 tuần (xem §2.6) |
| **I**nteresting (đáng quan tâm) | ✅ Cao | Giải thích cho phần tương tác là câu hỏi đúng bản chất của synergy |
| **N**ovel (mới) | ⚠️ Vừa phải, cần định vị lại | Interaction attribution cho tổ hợp thuốc đã có (Integrated Hessians, EXPRESS), nhưng **chưa có trên GNN/PPI, chưa có cho thiết lập 3 lớp, chưa có benchmark faithfulness** (xem §2.3) |
| **E**thical | ✅ | Chỉ dùng dữ liệu công khai cấp dòng tế bào, không có đối tượng người |
| **R**elevant (liên quan) | ✅ | Gắn với thiết kế liệu pháp phối hợp trong ung thư |

### 2.2 Vấn đề nghiêm trọng nhất: logit tương phản ≠ attribution tương tác **[Mới]**

**Kế hoạch hiện tại** (khảo sát §5.1): lấy `Δ_syn = z_syn − z_add` rồi tính attribution `φ_syn(g) = IG(Δ_syn, g)`, và cho rằng gene có `φ_syn` cao là "gene đẩy bộ ba ra khỏi trạng thái cộng tính".

**Vì sao lập luận này chưa đúng.** Trong tài liệu khảo sát, hai khái niệm "mốc cộng tính" đang bị đồng nhất:

| | Mốc trong **không gian nhãn** | Mốc trong **không gian đầu vào** |
|---|---|---|
| Là gì | Lớp *additive*, một trong ba đầu ra | Hiệu ứng khi chỉ có thuốc A, hoặc chỉ có thuốc B |
| `Δ_syn` trừ đi | ✅ cái này | ❌ không trừ cái này |

Phân tích logit của một model bất kỳ thành:
`z_k(A,B,c) = u_k(A,c) + u_k(B,c) + v_k(A,B,c)`
(gồm hiệu ứng riêng của A, hiệu ứng riêng của B và phần tương tác thật). Khi đó:

```
Δ_syn = [u_syn − u_add](A,c) + [u_syn − u_add](B,c) + [v_syn − v_add](A,B,c)
         └──── hiệu ứng chính của A ────┘ └─ của B ─┘   └── tương tác thật ──┘
```

Hai số hạng đầu không tự triệt tiêu. Ví dụ, nếu thuốc A "hay hiệp đồng với mọi thứ" thì gene mà A tác động vẫn có `φ_syn` cao, dù không hề có tương tác riêng với B. Như vậy `Δ_syn` trả lời câu hỏi *"vì sao model chọn synergistic chứ không chọn additive?"*. Đó là **contrastive explanation**, một kỹ thuật đã biết (Jacovi và cộng sự, 2021; Contrastive IG, 2025). Nó **không** trả lời câu hỏi *"A và B tương tác với nhau qua gene nào?"*.

**Cách sửa: biến điểm yếu thành đóng góp.** Đừng bỏ `Δ_syn`. Hãy so sánh **ba cấp attribution** trên cùng model:

| Cấp | Định nghĩa | Vai trò |
|---|---|---|
| (i) Thông thường | IG / GNNExplainer trên `z_syn` | Cách literature đang làm |
| (ii) Tương phản | IG trên `Δ_syn = z_syn − z_add` | Rẻ, đã biết, đóng vai trò baseline mạnh |
| (iii) **Tương tác thật** | Sai phân bậc hai theo sự có mặt của từng thuốc, ví dụ `Δ(A,B) − Δ(A,∅) − Δ(∅,B) + Δ(∅,∅)`, rồi mới attribution về từng gene. Hoặc dùng Integrated Hessians / Shapley interaction (thư viện `shapiq`) với "player" là nhóm đặc trưng của thuốc A, nhóm của thuốc B và các gene/pathway | **Đóng góp chính** |

Thí nghiệm then chốt: (iii) có khác (ii) và (i) không, và cái nào trung thực hơn trên một benchmark có **ground truth cài sẵn** (§2.5).

**Hệ quả kéo theo:** để đánh giá `Δ(A,∅)` thì model phải xử lý được đầu vào "chỉ một thuốc" mà không bị ra ngoài phân phối (out-of-distribution). Muốn vậy cần **huấn luyện thêm trên dữ liệu đơn trị liệu**, tức là đưa nhánh đơn trị liệu trở lại thành thành phần **bắt buộc** cho cấp (iii), chứ không chỉ là một mục ablation như khảo sát §5.1 đang viết. O'Neil có dữ liệu đơn trị liệu, nên điều này làm được, nhưng cần đưa vào kế hoạch ngay từ GĐ2.

### 2.3 Định vị lại tính mới **[Mới]**

Công trình đã có mà kế hoạch hiện tại chưa nhắc tới:

| Công trình | Đã làm | Chưa làm |
|---|---|---|
| **Integrated Hessians** (Janizek, Sturmfels & Lee, *JMLR* 2021) | Attribution tương tác cặp đặc trưng cho mạng nơ-ron; có ví dụ về dự đoán đáp ứng tổ hợp thuốc | Không dùng đồ thị/GNN; không đánh giá faithfulness |
| **EXPRESS** (Janizek và cộng sự, *Nat. Biomed. Eng.* 2023) | Shapley trên một ensemble model dự đoán synergy (AML, 133 tổ hợp, 285 bệnh nhân) | Không dùng GNN, không làm 3 lớp, không có benchmark giải thích |
| **SHAP cho synergy** (*npj Digital Medicine* 2026) | SHAP lên đặc trưng dòng tế bào trong một model graph DL dự đoán synergy | Attribution đơn thể, không phải tương tác |
| **DeepDrugs** (2026) | Tri-linear attention, tự nhận là "mechanism-aware" | Thuộc nhóm attention, chưa kiểm chứng faithfulness |

**Tuyên bố đóng góp đề xuất, có thể bảo vệ được:**
> *Công trình đầu tiên (trong phạm vi khảo sát) (1) đưa interaction attribution lên GNN trên PPI/pathway cho DSP, (2) trong thiết lập 3 lớp có thứ tự, cho phép so sánh cơ chế hiệp đồng với cơ chế đối kháng, và (3) đánh giá định lượng faithfulness của ba cấp attribution trên benchmark có ground truth cài sẵn.*

Mỗi vế trên cần được kiểm tra lại bằng một lượt tìm kiếm có hệ thống trước khi viết Chương 1. Hiện mới tìm nhanh, nên chưa thể khẳng định "chưa ai làm".

### 2.4 Dữ liệu **[Mới]**

| Vấn đề | Thực tế | Hành động |
|---|---|---|
| "O'Neil — 13,243 bộ ba" | Đây là bản của DeepDDS: chỉ giữ score > 10 (6,188 mẫu) và score < 0 (7,055 mẫu), **đã bỏ vùng 0–10** | Dùng bản Loewe gốc (~23 nghìn bộ ba, 38 thuốc, 39 dòng tế bào) từ DrugComb hoặc DeepSynergy |
| Giả định "antagonistic là lớp thiểu số" | **Chưa chắc đúng** với Loewe trên O'Neil. Riêng vùng < 0 đã có 7,055 mẫu, nên nếu cắt ở −10 thì số mẫu đối kháng có thể vẫn lớn. Phân bố phụ thuộc vào reference model | Bước đầu tiên của GĐ1 là **đếm phân bố 3 lớp cho cả 4 reference model × 3 ngưỡng** rồi mới chọn loss |
| Bliss/HSA/ZIP | DrugComb cung cấp sẵn cả 4 điểm cho mỗi khối thí nghiệm | G3 rất rẻ, không cần tự tính từ đường cong liều–đáp ứng |
| Dữ liệu đơn trị liệu | O'Neil có kèm. DrugComb có cột IC50 / đáp ứng đơn thuốc | Cần cho cấp attribution (iii) |
| Omics, PPI, pathway | CCLE/DepMap, STRING, KEGG/Reactome, DrugBank: đều công khai | Không có rủi ro |

### 2.5 Đánh giá giải thích: điểm yếu nằm ở việc kiểm chứng **[Mới]**

Phản biện Devil's Advocate trong `review_report.md` đã nêu: *faithful với model ≠ đúng về sinh học*. Kế hoạch hiện tại dùng ba loại đánh giá: faithfulness (Fidelity±), plausibility (enrichment KEGG) và stability (Jaccard). Không loại nào trả lời được câu hỏi *"explainer có tìm đúng tương tác hay không"*, vì **không có ground truth cho cơ chế hiệp đồng**.

**Đề xuất bổ sung (rẻ và tăng sức nặng nhiều nhất): benchmark bán tổng hợp (semi-synthetic).**
1. Giữ nguyên đặc trưng thật (omics, PPI, thuốc).
2. Sinh **nhãn giả** bằng một quy tắc tương tác cài sẵn, ví dụ "hiệp đồng nếu thuốc A đánh vào gene X, thuốc B đánh vào gene Y nằm cùng pathway P, và dòng tế bào biểu hiện cao gene Z", kèm nhiễu.
3. Huấn luyện model trên nhãn giả, rồi đo xem cấp (i), (ii), (iii) có tìm lại được {X, Y, Z} hay không bằng precision@k và AUROC trên các gene/cạnh cài sẵn.
4. Thêm một quy tắc chỉ có **hiệu ứng chính** (A mạnh, không tương tác với B). Explainer tốt phải **không** gán điểm tương tác cho trường hợp này.

Cách làm này theo đúng tinh thần CETExplainer (dựng ground truth để đánh giá) và làm cho mọi tuyên bố trong RQ2 trở nên **có thể bị bác bỏ (falsifiable)**. Đây cũng là câu trả lời trực tiếp cho phản biện Devil's Advocate.

### 2.6 Phạm vi và thời gian

Ma trận thực nghiệm đang viết trong khảo sát gồm 7 baseline × 5 split × 3 ngưỡng × 4 reference model × 6 phương pháp XAI × nhiều seed. Tổng số lần chạy lên tới **hàng nghìn**, cộng thêm việc phải tái lập từng baseline theo cả giao thức nhị phân. Với 17–23 tuần cho một người thì **không khả thi** nếu làm hết.

**Cắt gọn (MVP và phần mở rộng):**

| Hạng mục | MVP (bắt buộc) | Làm thêm nếu còn thời gian |
|---|---|---|
| Baseline | Majority class, model chỉ dùng đặc trưng dòng tế bào, DeepSynergy (MLP), DeepDDS | GraphSynergy, SynergyX, MD-Syn |
| Split | Random 5-fold, leave-drug-combination-out, leave-cell-line-out | Leave-drug-out, leave-tissue-out |
| Ngưỡng / reference model | Loewe ±10 làm chính; độ nhạy chỉ chạy trên **model cuối** và **1 split** | Toàn bộ lưới |
| XAI | IG, GNNExplainer, attention, cùng ba cấp (i)/(ii)/(iii) | SHAP, CETExplainer, counterfactual (C) |
| Seed | 3 | 5 |

### 2.7 Tài nguyên tính toán

Khoảng 23 nghìn bộ ba, PPI cỡ khoảng 1,000 gene (LINCS landmark): **một GPU 8–16 GB (hoặc Colab/Kaggle) là đủ**. IG có chi phí khoảng 50 lần forward cho mỗi mẫu. Cấp (iii) đắt hơn khoảng 4 lần (4 cấu hình có/không có thuốc) hoặc phải lấy mẫu Shapley. Nên giới hạn ở khoảng 500–1,000 bộ ba được chọn có phân tầng theo lớp. Không có rủi ro lớn về tính toán.

### 2.8 Bảng rủi ro (cập nhật so với khảo sát §7)

| Rủi ro | Mức | Phòng ngừa |
|---|---|---|
| Lỗi khái niệm ở `Δ_syn` (§2.2) | **Nghiêm trọng** nếu không sửa | Dùng thiết kế ba cấp attribution |
| Novelty bị hội đồng bác vì đã có EXPRESS / Integrated Hessians | Cao | Trích dẫn và định vị lại như §2.3 |
| Dùng nhầm bộ dữ liệu đã bỏ vùng trung tính | Cao | Dùng dữ liệu gốc từ DrugComb |
| Đầu vào chỉ một thuốc nằm ngoài phân phối khi tính cấp (iii) | Vừa | Huấn luyện kèm dữ liệu đơn trị liệu; kiểm tra calibration trên mẫu đơn trị liệu đã giữ lại (held-out) |
| Model chỉ học đặc trưng dòng tế bào | Vừa | Baseline "chỉ dòng tế bào" là bắt buộc |
| Ba cấp attribution cho kết quả gần như trùng nhau | Vừa | **Bản thân đây cũng là kết quả** (một kết quả âm có giá trị). Benchmark bán tổng hợp sẽ cho biết vì sao |
| Phạm vi quá rộng | Cao | Theo bảng MVP ở §2.6 |

### 2.9 Kết luận về tính khả thi

> **Khả thi có điều kiện: 7/10.** Phương án B gần như chắc chắn ra kết quả. Phương án A khả thi **sau khi** chuyển sang thiết kế ba cấp và bổ sung benchmark bán tổng hợp. Phương án C chỉ nên làm nếu thật sự còn thời gian.

---

## Phần 3 — Workflow đi đến lời giải

Mỗi giai đoạn đều có **mốc quyết định (gate)**. Nếu không qua gate thì chuyển sang phương án dự phòng, không cố đẩy tiếp.

```
GĐ0 Chốt đề ─► GĐ1 Dữ liệu ─► GĐ2 Backbone ─► GĐ3 Benchmark XAI (B) ─► GĐ4 Interaction (A) ─► GĐ5 Mở rộng + viết
   (1–2 t)       (3 t)          (4 t)            (4 t)                     (5 t)                  (3–4 t)
                  Gate 1         Gate 2          Gate 3 (pilot A sớm)       Gate 4
```

### GĐ0 — Chốt đề và định vị (1–2 tuần)
1. Đọc kỹ bản đầy đủ của 4 bài: Integrated Hessians, EXPRESS, Jacovi 2021 (contrastive), CETExplainer.
2. Chạy `/ars-lit-review` (hoặc `deep-research` ở chế độ `lit-review`) với truy vấn hẹp *"interaction attribution" + "drug synergy" + GNN* để kiểm tra lại tuyên bố novelty ở §2.3.
3. Viết lại khảo sát §3.4 và §5.1 theo thiết kế ba cấp.
4. Thống nhất với thầy hướng dẫn: hạn nộp, cấp luận văn (đồ án kỹ sư hay thạc sĩ), và bảng MVP.
- **Đầu ra:** bản đề cương 1–2 trang (RQ, đóng góp, MVP).

### GĐ1 — Pipeline dữ liệu (3 tuần)
1. Tải O'Neil từ DrugComb, gồm cả 4 điểm synergy và dữ liệu đơn trị liệu.
2. **Đếm phân bố 3 lớp** cho 4 reference model × 3 ngưỡng, rồi đưa vào một bảng trong luận văn.
3. Ghép SMILES (lấy từ DrugBank/PubChem) → molecular graph (RDKit); omics từ CCLE/DepMap cho 978 gene landmark; PPI từ STRING (ngưỡng ≥ 700); target từ DrugBank.
4. Viết hàm tạo 3 kiểu split MVP, **chia theo nhóm** để tránh rò rỉ, có kiểm tra tự động rằng không có cặp/dòng tế bào nào nằm ở cả train và test.
5. **Dựng benchmark bán tổng hợp** (§2.5): 2–3 quy tắc tương tác cài sẵn và 1 quy tắc chỉ có hiệu ứng chính.
- **Gate 1:** Lớp nhỏ nhất có ≥ ~5% số mẫu ở cấu hình chính? Nếu **không**, đổi sang ZIP/Bliss hoặc gộp thêm ALMANAC.

### GĐ2 — Backbone 3 lớp (4 tuần)
1. Kiến trúc: hai nhánh GNN cho thuốc chia sẻ trọng số; gộp hai nhánh bằng phép đối xứng (tổng + tích Hadamard); GNN trên PPI cho dòng tế bào, trong đó các node target của thuốc được đánh dấu; đầu ra ordinal (CORAL).
2. **Thêm head đơn trị liệu và hỗ trợ đầu vào thuốc rỗng `∅`** (embedding học được), huấn luyện chung với dữ liệu đơn trị liệu. Đây là điều kiện cho cấp (iii).
3. Chạy các baseline MVP. Tái lập DeepDDS theo giao thức nhị phân gốc để chứng minh pipeline đúng.
4. Báo cáo: QWK, macro-F1, per-class F1/AUPRC, ma trận nhầm lẫn, tỷ lệ lỗi nhầm cực.
- **Gate 2:** Model chính vượt rõ baseline "chỉ dòng tế bào" về QWK trên split leave-combination-out? Nếu **không**, model không học được tương tác thuốc và mọi giải thích về sau là vô nghĩa. Phải sửa backbone trước khi đi tiếp.

### GĐ3 — Benchmark XAI (phương án B) cùng pilot A sớm (4 tuần)
1. Cài đặt IG (Captum), GNNExplainer (PyG), attention; metric Fidelity±, sparsity, Jaccard@k qua 3 seed, enrichment KEGG.
2. **Pilot A ngay trong tuần đầu GĐ3:** tính cấp (i), (ii), (iii) trên khoảng 200 bộ ba và trên benchmark bán tổng hợp.
- **Gate 3 ("kill test"):**
  - Nếu (iii) tìm lại được gene cài sẵn tốt hơn rõ rệt so với (i)/(ii) → đi tiếp GĐ4 với A làm trục chính.
  - Nếu cả ba gần như trùng nhau → luận văn chuyển sang **B làm trục chính**, còn A trở thành một chương "kết quả âm có giải thích". Kết quả này vẫn bảo vệ được.

### GĐ4 — Interaction-level explanation (phương án A) (5 tuần)
1. Chạy ba cấp attribution trên toàn bộ tập đánh giá (500–1,000 bộ ba phân tầng), có bootstrap CI.
2. Ba thí nghiệm kiểm chứng của khảo sát §5.1 (phân kỳ, đặc hiệu, đối lập syn/ant), giờ chạy trên cả ba cấp.
3. Kiểm tra độ ổn định qua reference model và qua ngưỡng (RQ3), chỉ trên model cuối.
4. Phân tích riêng các mẫu nằm gần ranh giới ±10.
- **Gate 4:** Có ít nhất một kết luận định lượng có khoảng tin cậy không chứa 0 cho RQ2 hoặc RQ3.

### GĐ5 — Mở rộng và viết (3–4 tuần)
1. 2–3 case study có đối chiếu với literature độc lập, **trong đó có một case model giải thích sai**.
2. Counterfactual trên PPI (phương án C), chỉ làm khi còn ≥ 2 tuần dư.
3. Viết luận văn. Có thể dùng `/ars-outline` để lập dàn ý và bản đồ bằng chứng (evidence map), rồi `/ars-reviewer` để phản biện giả lập trước khi nộp.

### Ánh xạ sang các chương của luận văn

| Chương | Nội dung | Lấy từ |
|---|---|---|
| 1. Mở đầu | Bài toán, RQ, đóng góp (bản đã định vị lại) | GĐ0 |
| 2. Tổng quan | Literature review đã sửa theo `review_report.md`, cộng thêm mục interaction attribution | GĐ0 |
| 3. Phương pháp | Dữ liệu, backbone ordinal, ba cấp attribution, benchmark bán tổng hợp | GĐ1–2 |
| 4. Thực nghiệm dự đoán | Bảng hiệu năng, baseline | GĐ2 |
| 5. Thực nghiệm giải thích | Benchmark B, pilot và kết quả A, độ ổn định | GĐ3–4 |
| 6. Thảo luận | Case study, giới hạn (faithful ≠ cơ chế), hướng phát triển | GĐ5 |

### Công cụ

PyTorch Geometric (GNN, GNNExplainer) · Captum (IG, Layer IG) · `shapiq` (Shapley interaction) · RDKit · `coral-pytorch` · scikit-learn (QWK: `cohen_kappa_score(weights="quadratic")`) · gseapy (enrichment).

---

## Câu hỏi bạn cần trả lời (ảnh hưởng tới kế hoạch)

1. **Hạn nộp** cụ thể là khi nào? Lộ trình 17–23 tuần chỉ vừa khít nếu bắt đầu ngay.
2. Đây là **đồ án tốt nghiệp kỹ sư hay luận văn thạc sĩ**? Nếu là đồ án kỹ sư thì phương án B cùng pilot A đã đủ; nếu là thạc sĩ thì nên làm đầy đủ A.
3. Thầy hướng dẫn có yêu cầu **bắt buộc** dùng một backbone cụ thể (ví dụ XGDP) không?

---

## Giới hạn của bản đánh giá này

- Quick mode: chỉ tra cứu có mục tiêu, **không phải** tìm kiếm có hệ thống. Kết luận về novelty ở §2.3 cần kiểm tra lại (bước 2 của GĐ0).
- Phân bố 3 lớp của O'Neil chưa được đếm trực tiếp. Nhận định ở §2.4 là suy luận từ số liệu của DeepDDS.
- Lập luận ở §2.2 là phân tích toán học của trợ lý AI. Nên trình bày lại với thầy hướng dẫn để kiểm tra.
- Chưa đọc toàn văn EXPRESS và bài *npj Digital Medicine* 2026, mới đọc tóm tắt và trang tổng quan.

---

## Tài liệu tham khảo (bổ sung so với khảo sát)

1. Janizek, J. D., Sturmfels, P., & Lee, S.-I. (2021). Explaining explanations: Axiomatic feature interactions for deep networks (Integrated Hessians). *JMLR*. https://arxiv.org/abs/2002.04138
2. Janizek, J. D. et al. (2023). Uncovering expression signatures of synergistic drug responses via ensembles of explainable machine-learning models (EXPRESS). *Nature Biomedical Engineering*. Preprint: https://www.biorxiv.org/content/10.1101/2021.10.06.463409
3. Jacovi, A. et al. (2021). Contrastive explanations for model interpretability. *EMNLP*. https://arxiv.org/abs/2103.01378
4. Contrastive Integrated Gradients for whole slide image classification (2025). https://arxiv.org/abs/2511.08464
5. Muschalik, M. et al. (2024). shapiq: Shapley interactions for machine learning. *NeurIPS Datasets & Benchmarks*. https://github.com/mmschlk/shapiq
6. Interpretable graph deep learning framework for drug synergy prediction by integrating functional and clinical similarities (2026). *npj Digital Medicine*. https://www.nature.com/articles/s41746-026-02830-z
7. DeepDrugs: a mechanism-aware tri-linear attention framework for synergistic drug-combination prediction. https://pmc.ncbi.nlm.nih.gov/articles/PMC13122632/
8. MD-Syn (mô tả tiền xử lý O'Neil theo DeepDDS: 13,243 bộ ba, ngưỡng > 10 / < 0). https://arxiv.org/abs/2501.07884
9. Các tài liệu khác: xem [khao_sat_xai_graph_drug_synergy.md §9](khao_sat_xai_graph_drug_synergy.md).
