# Planner đề xuất 3 — SynGT: Graph Neural Network + Transformer cho phân lớp hiệp đồng thuốc ba lớp, và XAI ở cấp tương tác

**Tài liệu duy nhất của project.** Ghi toàn bộ: bài báo tham khảo, câu hỏi nghiên cứu, dữ liệu, kiến trúc, tiền xử lý, huấn luyện, XAI, kết quả kỳ vọng, lộ trình, rủi ro.

**Phạm vi.** Một mô hình GNN + Transformer cho bài toán hiệp đồng thuốc, đầu ra **phân lớp ba lớp: antagonistic / additive / synergistic**, kèm phần XAI. Đi theo đúng khung của các bài đã đăng (DTSyn, DeepDDS, TranSynergy, MD-Syn), phát triển thêm hai điểm mới cụ thể và giải thích một vấn đề nằm sẵn bên trong các bài đó.

**Ngày lập:** 16/11/2026. Mọi con số về bài báo đều trích từ bài gốc, có dẫn nguồn và ghi rõ giao thức đo; mọi con số về dữ liệu và hạ tầng đã kiểm tra trực tiếp trên máy (phụ lục C).

---

## Phần 0. Tóm tắt một trang

**Mô hình.** SynGT, theo khung hai transformer của DTSyn (*Brief Bioinform* 2022):
- Thuốc: SMILES → đồ thị phân tử RDKit → GNN → token nguyên tử.
- Dòng tế bào: biểu hiện 978 gen landmark L1000 → token gen, cộng embedding node2vec trên mạng PPI.
- **Transformer mịn**: attention giữa token nguyên tử của cả hai thuốc và token gen → quan hệ cấu trúc con ↔ gen.
- **Transformer thô**: attention giữa ba token mức cao (thuốc A, thuốc B, dòng tế bào).
- Đầu ra: **ba lớp có thứ tự**, dùng đầu rank-consistent CORN, metric chính là QWK.

**Ba đóng góp, mỗi cái trả lời một câu hỏi nghiên cứu.**

| # | Đóng góp | Khoảng trống trong bài đã đăng |
|---|---|---|
| **N1** | Đặt bài toán thành **phân lớp ba lớp có thứ tự** (ant < add < syn) với đầu CORN và metric QWK; đo xem hiệu năng của chính các mô hình đã công bố tụt bao nhiêu khi **không được xóa vùng trung tính** | DTSyn gán nhãn dương khi score > 10, âm khi score < 0, rồi **bỏ toàn bộ vùng 0–10**: từ 23.052 bộ ba còn 13.243, tức **loại 42,6% dữ liệu**. Vùng bị xóa đúng là vùng khó nhất. Theo khảo sát của tôi, chưa có bài nào đặt bài toán này ở dạng **ordinal** |
| **N2** | **Attribution ở cấp tương tác**: giải thích cho hiệu logit `Δ_syn = z_syn − z_add` thay vì cho `z_syn` | Hiệp đồng là phần dôi ra so với cộng tính, nhưng mọi bài đều giải thích cho dự đoán tổng. Lớp additive trong thiết lập ba lớp **chính là mốc tham chiếu**, nên phép trừ này miễn phí và nằm trong cùng một forward pass |
| **N3** | **Kiểm định attention có trung thực không**, kèm null và kiểm tra độ ổn định qua seed, fold, bốn điểm synergy và ba ngưỡng | Phần giải thích của DTSyn là **một ví dụ duy nhất** (ETOPOSIDE + MK-2206 trên CAOV3 và NCIH23), đối chiếu literature, **không có kiểm định thống kê nào**, và chính tác giả dùng chữ "may indicate" |

Kèm theo N1, thiết lập ba lớp mở ra một câu hỏi mà thiết lập nhị phân không hỏi được: **cơ chế gây đối kháng là gì**, và nó có khác về chất so với cơ chế hiệp đồng hay không.

**Kết quả kỳ vọng.** Nhị phân theo giao thức DTSyn: AUROC 0,88–0,92 (DTSyn 0,89). Ba lớp trên dữ liệu đầy đủ: QWK 0,50–0,62. Mức tụt giữa hai thiết lập là con số đầu bài của bài báo. Chi tiết ở phần 8.

---

## Phần 1. Bài báo tham khảo

### 1.1. Bốn bài nền, lấy kiến trúc từ đây

| Bài | Nguồn | Kiến trúc | Cách giải thích | Kiểm chứng giải thích |
|---|---|---|---|---|
| **DTSyn** ← khung chính | Hu J. et al. *Brief Bioinform* 2022;23(5):bbac302 · code: PaddleHelix/apps/drug_drug_synergy/DTSyn | Đồ thị phân tử RDKit, đặc trưng nguyên tử 78 chiều (DeepChem, hậu xử lý như DeepDDS), **GCN 2 lớp (512, 128)**; embedding gen node2vec 128 chiều trên PPI, giới hạn ở gen hallmark L1000; biểu hiện CCLE 978 gen qua MLP 3 lớp; **transformer mịn** trên token nguyên tử + token gen; **transformer thô** 2 lớp, 4 đầu, hidden 64, dropout 0,6; MLP 2 lớp | Attention của cả hai transformer | **Một ví dụ duy nhất**; chỉ đối chiếu literature; không test thống kê |
| **DeepDDS** | Wang J. et al. *Brief Bioinform* 2022;23(1):bbab390 · arXiv:2107.02467 | GCN/GAT trên đồ thị phân tử + MLP trên biểu hiện | Correlation matrix của đặc trưng nguyên tử | Định tính |
| **TranSynergy** | Liu Q., Xie L. *PLoS Comput Biol* 2021;17(2):e1008653 | Giảm chiều đầu vào → **self-attention transformer trên gen** → FC. Đầu vào: drug–target lan truyền trên mạng, gene dependency, biểu hiện | **SA-GSEA**: GSEA trên giá trị SHAP để suy ra pathway | Enrichment (tìm được RAF oncogenic signature); ablation cho thấy self-attention là thành phần then chốt |
| **MD-Syn** | *Front Pharmacol* 2025;16:1564339 · arXiv:2501.07884 | MOLFORMER (1D) + GCN & node2vec-PPI (2D) + graph-transformer pooling, 4 đầu attention | Heatmap attention thuốc–gen | Case study MK-2206 + MK-8669 → PAK6; UMAP |

### 1.2. Số của các bài, để biết mốc

**DTSyn, random 5-fold trên O'Neil** (nhãn: score > 10 dương, score < 0 âm, bỏ vùng giữa):
ROC-AUC 0,89 · PR-AUC 0,87 · ACC 0,81 · BACC 0,81 · PREC 0,84 · TPR 0,74 · Kappa 0,61. Bài tự ghi: **DeepDDS tốt hơn một chút ở thiết lập này**.

**DTSyn, bốn kiểu chia dữ liệu khó** (ROC-AUC / PR-AUC / TPR):

| Mô hình | leave-drug | leave-combination | leave-cell | leave-tumor |
|---|---|---|---|---|
| **DTSyn** | **0,73 / 0,70 / 0,65** | **0,78 / 0,75 / 0,71** | **0,82 / 0,79 / 0,75** | **0,81 / 0,80 / 0,74** |
| DeepDDS | 0,71 / 0,68 / 0,48 | 0,76 / 0,75 / 0,56 | 0,81 / 0,79 / 0,69 | 0,79 / 0,79 / 0,63 |
| DeepSynergy | 0,66 / 0,73 / 0,46 | 0,71 / 0,77 / 0,54 | 0,75 / 0,81 / 0,60 | 0,73 / 0,80 / 0,57 |
| Random Forest | 0,70 / 0,67 / 0,47 | 0,73 / 0,71 / 0,57 | 0,77 / 0,75 / 0,61 | 0,79 / 0,79 / 0,63 |
| MLP | 0,69 / 0,68 / 0,59 | 0,72 / 0,71 / 0,63 | 0,79 / 0,77 / 0,66 | 0,76 / 0,75 / 0,62 |
| SVM | 0,64 / 0,62 / 0,56 | 0,68 / 0,65 / 0,62 | 0,77 / 0,75 / 0,69 | 0,76 / 0,75 / 0,66 |

**Ablation của DTSyn** — bằng chứng rằng transformer là thành phần quan trọng, không phải trang trí:

| Biến thể | ROC-AUC | Kappa |
|---|---|---|
| DTSyn đầy đủ | 0,89 | 0,61 |
| Bỏ transformer mịn | 0,87 | 0,58 |
| Chỉ transformer mịn | 0,71 | 0,34 |
| **Bỏ cả hai transformer** | **0,69** | **0,30** |

**Trên tập độc lập, DTSyn yếu**: BACC 0,57 (ALMANAC) · 0,56 (FLOBAK) · 0,53 (FORCINA) · 0,51 (AstraZeneca) · 0,48 (YOHE). Tác giả tự nhận TPR không ổn định.

Các số khác để tham khảo: MD-Syn AUROC 0,919 · MatchMaker 0,97 · GAECDS 0,98 — **không so sánh trực tiếp được**, vì mỗi bài một bộ dữ liệu, một ngưỡng, một kiểu split. Abbasi & Rousu (*Curr Opin Struct Biol* 2024, arXiv:2404.02484) đếm hơn chín phương pháp báo AUROC ≥ 0,9 và kết luận rằng thiết lập đánh giá "không luôn được báo cáo rõ ràng và dễ so sánh". Họ cũng đo được leave-drug-out khó hơn leave-pair-out có ý nghĩa thống kê (p = 0,026).

→ **Luận văn chỉ so số với DTSyn và DeepDDS, trên cùng dữ liệu và cùng giao thức, do mình tự chạy lại.** Không chép số từ các bài khác vào bảng so sánh.

### 1.3. Khoảng trống đã xác minh, chỗ đặt tính mới

Ba lần tra cứu độc lập (16/11/2026) cho kết quả:

1. **Phân lớp ba lớp có tồn tại nhưng luôn ở dạng nominal, và thường bị thu về nhị phân.** Các ngưỡng phổ biến: < 0 là ant, > 30 là syn, 0–30 là add. TensoGraph dựng đồ thị ba loại cạnh rồi **gộp add và ant thành một lớp âm**. SYNDEEP ghi rõ ComboScore cho ba lớp một cách tự nhiên nhưng họ chuyển về nhị phân "để giảm chi phí tính toán".
2. **Chưa thấy bài nào đặt bài toán ở dạng ordinal** với đầu rank-consistent (CORAL, CORN) và đánh giá bằng QWK. QWK chỉ xuất hiện ở các lĩnh vực ordinal khác, ví dụ phân độ nặng viêm loét đại tràng.
3. **Vùng trung tính bị xóa với quy mô lớn mà không ai đo hậu quả.** DTSyn loại 9.809 trong 23.052 bộ ba. Thang đo mịn hơn cũng tồn tại trong y văn ("possibly synergistic" khi 0 < score < 10, "likely synergistic" khi > 10) nhưng chưa ai mô hình hóa theo thứ tự.

Cần nói rõ trong luận văn rằng đây là kết luận từ khảo sát của chúng tôi, và nên tự kiểm chứng lại trước khi nộp.

---

## Phần 2. Câu hỏi nghiên cứu

Bảng dưới đây là xương sống của luận văn: mỗi câu hỏi gắn với một khoảng trống trong bài đã đăng, một thí nghiệm cụ thể, và một kết quả kỳ vọng. **Mọi mục trong các phần sau đều phải truy về được một dòng ở đây.**

| RQ | Câu hỏi | Khoảng trống | Thí nghiệm | Kết quả theo hướng nào cũng dùng được |
|---|---|---|---|---|
| **RQ1** | Khi phải phân biệt cả vùng trung tính, hiệu năng của các mô hình hiệp đồng tụt bao nhiêu? | DTSyn loại 42,6% dữ liệu; không bài nào đo hậu quả | Chạy SynGT, DTSyn, DeepDDS trên **ba thiết lập nhãn** trên cùng dữ liệu: (a) nhị phân bỏ vùng giữa (đúng DTSyn), (b) nhị phân giữ toàn bộ dữ liệu, (c) ba lớp ordinal | Tụt nhiều → số liệu đã công bố được đo trên tập dễ hơn thực tế. Tụt ít → vùng trung tính không khó như tưởng. Cả hai đều là phát hiện |
| **RQ2** | Đầu ra ordinal có hơn đầu ra nominal không, và có giảm **lỗi nhầm cực** (syn ↔ ant) không? | Chưa ai làm ordinal cho bài toán này | So CORN với cross-entropy thường và với cross-entropy có ma trận chi phí; đo QWK, MAE, macro-F1, **và riêng tỷ lệ lỗi nhầm cực** | Lỗi nhầm cực là lỗi nguy hiểm về mặt lâm sàng: khuyến nghị một tổ hợp gây hại. Giảm được là đóng góp thực dụng |
| **RQ3** | Attribution cấp tương tác (`z_syn − z_add`) có khác attribution cấp logit (`z_syn`) không? | Mọi bài giải thích dự đoán tổng, không phải phần dôi ra | Jaccard@k giữa hai tập gen và hai tập cấu trúc con; phân tích ca mà hai cấp khác nhau nhiều nhất | Khác nhiều → cách giải thích của literature đang trả lời sai câu hỏi. Trùng nhau → phép trừ không cần thiết, biết sớm là tốt |
| **RQ4** | Attention của transformer có phải lời giải thích trung thực không? | DTSyn, MD-Syn, AttenSyn đều trình bày attention như lời giải thích mà không kiểm định | Fid+/Fid− có null xóa ngẫu nhiên; so attention với IG và GNNExplainer; **Faithfulness Violation Test** (Liu et al., ICML 2022) | Attention trượt → củng cố cảnh báo của Kakkad et al. 2023 ngay trong lĩnh vực này. Attention đạt → hợp thức hóa cách làm của ba bài kia |
| **RQ5** | Lời giải thích có ổn định không, hay chỉ là ảnh của một lựa chọn quy ước? | MD-Syn tự nhận phụ thuộc Loewe nhưng không ai test | Jaccard@k của top-k qua 5 seed, 5 fold, **bốn điểm synergy** (Loewe/ZIP/Bliss/HSA) và **ba ngưỡng** (±5/±10/±20) | Không ổn định → "cơ chế" phát hiện được phần lớn là ảnh của định nghĩa toán học. Ổn định → lời giải thích có nền |
| **RQ6** | Cơ chế gây **đối kháng** có khác về chất so với cơ chế hiệp đồng không? | Thiết lập nhị phân vứt bỏ lớp đối kháng nên không hỏi được | Attribution trên `z_ant − z_add`; so pathway làm giàu của nhóm ant với nhóm syn | Khác pathway → thiết lập ba lớp mở ra một hướng. Chỉ đảo dấu → lớp ant không mang thông tin cơ chế riêng |

RQ1 và RQ2 là nửa dự đoán. RQ3 đến RQ6 là nửa XAI. RQ1 và RQ4 là hai câu "giải thích một vấn đề bên trong bài đã đăng" mà bạn muốn.

---

## Phần 3. Dữ liệu

### 3.1. Nguồn

| Loại | Nguồn | Trạng thái |
|---|---|---|
| **Tổ hợp thuốc, chính** | **O'Neil** (Merck 2016) qua DrugComb v1.4, `src/data/raw/summary_table_v1.4.csv` | **Có trên máy.** Pipeline hiện tại đã trích ra 21.571 bộ ba, 38 thuốc, 37 dòng tế bào. Bài gốc DTSyn ghi 23.052 bộ ba, 38 thuốc, 39 dòng tế bào — chênh lệch do bước lọc, **phải đối chiếu và ghi lại lý do** |
| Điểm synergy | Loewe, ZIP, Bliss, HSA — cả bốn đều có trong cùng file | Có trên máy, không khuyết Loewe |
| **Kiểm chứng ngoài** | NCI-ALMANAC thô, `ComboDrugGrowth_Nov2017.zip` | Tải được, 83 MB |
| Biểu hiện | DepMap `OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv` | Có trên máy |
| Gen landmark | 978 gen L1000 (danh sách từ GSE92742 `gene_info`) | Cần tải danh sách |
| SMILES | ChEMBL API, tra `pref_name__iexact` | Hoạt động cho 34/38 thuốc O'Neil. **PubChem chặn IP máy này** |
| Mạng PPI | STRING v12, score ≥ 700 | Có trên máy; dùng để huấn luyện node2vec |
| Đích thuốc | ChEMBL mechanism | Đã dùng được; 33/38 thuốc có đích |
| Pathway | KEGG (`src/data/raw/kegg/`) | Một phần có sẵn; dùng để chấm plausibility |

**Quy mô cố ý giữ nhỏ.** Chỉ O'Neil làm dữ liệu chính, ALMANAC làm kiểm chứng ngoài. Đây đúng là thiết lập của DTSyn, DeepDDS, AttenSyn và MD-Syn, nên số liệu so được. Mở rộng lên DrugComb đầy đủ (466.033 khối tổ hợp đã có trên máy) để ở phần hướng phát triển, không nằm trong phạm vi.

### 3.2. SMILES cho 38 thuốc

Ba tầng, có log cho từng thuốc:
1. Khớp tên chính xác trên ChEMBL (`pref_name__iexact`), dùng map `CHEMBL` sẵn có trong `src/data/build_targets.py`. Đã thử: **34/38 thuốc có SMILES**.
2. Thiếu: **carboplatin, oxaliplatin** (phức platin, ChEMBL không có cấu trúc) → nhập tay từ DrugBank, ghi nguồn. RDKit đọc được Pt.
3. Thiếu: **MK-4541, MRK-003** (mã nội bộ Merck, không có cấu trúc công khai), xuất hiện trong **12,5% số bộ ba**. Ba lựa chọn, theo thứ tự ưu tiên:
   - kiểm tra file SMILES đi kèm code DeepDDS và DTSyn — hai bài này cũng chạy trên O'Neil nên có thể đã điền;
   - nếu không có, loại các bộ ba chứa hai thuốc này và **báo cáo rõ số bộ ba còn lại**;
   - không bao giờ dùng khớp mờ để lấp.

**Cấm khớp mờ.** Đã thử `search.json` của ChEMBL: truy vấn "gemcitabine" trả về "GEMCITABINE ELAIDATE", một chất khác. Một ánh xạ sai là nhãn sai âm thầm xuyên suốt luận văn.

### 3.3. Ba thiết lập nhãn — đây là thiết kế trung tâm của RQ1

Cả ba chạy trên **cùng một bộ dữ liệu gốc**, chỉ khác cách gán nhãn và cách lọc:

| Thiết lập | Nhãn | Dữ liệu dùng | Vai trò |
|---|---|---|---|
| **(a) nhị phân, bỏ vùng giữa** | score > 10 → dương; score < 0 → âm; **bỏ 0 ≤ score ≤ 10** | khoảng 57% dữ liệu (DTSyn: 13.243 / 23.052) | Tái lập DTSyn và DeepDDS. Mốc để chứng minh pipeline đúng |
| **(b) nhị phân, giữ toàn bộ** | score > 10 → dương; còn lại → âm | 100% | Cô lập ảnh hưởng của việc xóa vùng giữa |
| **(c) ba lớp ordinal** ← **thiết lập chính** | score > 10 → syn; −10 ≤ score ≤ 10 → add; score < −10 → ant | 100% | Đầu ra mà luận văn nhắm tới |

Phân bố ở thiết lập (c) trên O'Neil với Loewe ±10, **đã đo từ dữ liệu thật**: ant 23,4% · add 70,1% · syn 6,4%. Lớp syn là lớp thiểu số nặng, nên bắt buộc dùng AUPRC từng lớp và trọng số lớp, **không dùng accuracy**.

Bảng độ nhạy: cả bốn điểm synergy (Loewe, ZIP, Bliss, HSA) × ba ngưỡng (±5, ±10, ±20). Thiết lập chính là Loewe ±10, theo quy ước SynergyFinder.

**Mẫu ranh giới.** Bộ ba có score 9,8 và 10,2 bị gán hai nhãn khác nhau dù thực nghiệm gần như không phân biệt được. Báo cả hai cách: giữ nguyên, và label smoothing theo khoảng cách tới ngưỡng. Cách thứ hai hợp với bản chất ordinal hơn.

### 3.4. Chia dữ liệu

Bốn kiểu, đúng như DTSyn để so được:

| Split | Giữ lại | Số của DTSyn để đối chiếu |
|---|---|---|
| random 5-fold | — | ROC-AUC 0,89 |
| leave-combination-out | cặp thuốc | 0,78 |
| leave-drug-out | thuốc | 0,73 |
| leave-cell-out | dòng tế bào | 0,82 |
| leave-tumor-out | loại mô (7 loại) | 0,81 |

Mỗi split 5 fold × 5 seed. Tập validation lấy từ trong phần train của mỗi fold, **chia theo cùng đơn vị với split ngoài** (ví dụ leave-drug thì validation cũng theo thuốc), nếu không sẽ rò thông tin và chọn mô hình sai.

---

## Phần 4. Tiền xử lý — từng bước

Phần này phải viết thành code chạy một lệnh và ghi ra `data/processed/`, kèm một file `provenance.json` ghi phiên bản nguồn và số dòng sau mỗi bước.

### 4.1. Phía thuốc

1. Lấy SMILES theo quy trình §3.2 → `smiles.csv` với các cột `drug, smiles, source, chembl_id, resolved_by`.
2. Chuẩn hóa RDKit: tách muối, trung hòa điện tích, chuẩn hóa tautomer, sinh InChIKey. **Hai tên trỏ về cùng InChIKey thì phải gộp thành một thuốc**, nếu không sẽ rò thông tin ở split theo thuốc.
3. SMILES → đồ thị: nguyên tử là nút, liên kết là cạnh, vô hướng.
4. Đặc trưng nguyên tử **78 chiều theo DeepChem, hậu xử lý như DeepDDS** — đúng như DTSyn, để so sánh công bằng: ký hiệu nguyên tử (one-hot), bậc, số H, hóa trị ẩn, tính thơm.
5. Chia mảnh **BRICS** cho mỗi phân tử, lưu ánh xạ nguyên tử → mảnh. Dùng cho XAI ở §6.
6. Cache toàn bộ ra đĩa. 38 thuốc nên chỉ chạy một lần, vài giây.

### 4.2. Phía dòng tế bào

1. Ánh xạ tên dòng tế bào O'Neil sang DepMap qua `src/data/cell_line_map.csv` (đã có). Ghi lại dòng nào không ánh xạ được.
2. Lấy biểu hiện của **978 gen landmark L1000**, giao với gen có trong DepMap. Kỳ vọng còn khoảng 950.
3. Chuẩn hóa z-score **theo từng gen, fit chỉ trên các dòng tế bào trong tập train của từng fold**. Đây là chỗ rất dễ rò thông tin, và phải có test đơn vị.
4. Huấn luyện **node2vec 128 chiều trên STRING** (score ≥ 700), giới hạn ở tập gen trên → embedding gen, dùng chung cho mọi fold. Đây là thành phần "graph" thứ hai, đúng như DTSyn và MD-Syn.
5. Gộp gen theo pathway KEGG để chấm plausibility ở §6 — **chỉ dùng để chấm điểm, không đưa vào mô hình**, tránh vòng lặp.

### 4.3. Nhãn và khử trùng lặp

1. Gộp bản lặp cùng (A, B, cell) bằng **trung vị**, giữ lại độ phân tán để báo cáo.
2. Khử trùng lặp **trước khi chia fold**.
3. Đối xứng hóa: nếu dữ liệu có cả (A,B) và (B,A) thì gộp.
4. Sinh nhãn cho cả ba thiết lập ở §3.3 và cả bốn điểm synergy.
5. Loại khối thiếu `css` hoặc có dải nồng độ quá hẹp.
6. In ra bảng phân bố lớp cho từng thiết lập và từng điểm synergy. **Bảng này vào luận văn.**

---

## Phần 5. Kiến trúc SynGT và cách huấn luyện

### 5.1. Flow mô hình

```
  SMILES_A ──RDKit──► đồ thị A ──┐
                                 │   GNN DÙNG CHUNG TRỌNG SỐ (siamese)
  SMILES_B ──RDKit──► đồ thị B ──┤   GIN 3 lớp, hidden 128, đặc trưng nguyên tử 78 chiều
                                 │   (ablation: GCN 2 lớp 512→128 đúng như DTSyn; GAT)
                                 ▼
                    token nguyên tử A (n_A × 128) ,  token nguyên tử B (n_B × 128)
                                 │
  biểu hiện 950 gen ──► MLP 3 lớp ──► token gen (950 × 128)
  node2vec STRING   ──────(+)──────►  cộng vào token gen
                                 │
   ┌─────────────────────────────▼──────────────────────────────┐
   │ TRANSFORMER MỊN  (fine-granularity, theo DTSyn)             │
   │ chuỗi đầu vào: [CLS_f | nguyên tử A | nguyên tử B | gen]    │
   │ 2 lớp, 4 đầu, d_model 128, FFN 256, dropout 0,3             │
   │ ❗ KHÔNG có type embedding riêng cho A và B                  │
   │    → mô hình đối xứng tuyệt đối theo cấu trúc               │
   │ cho ra: ma trận attention nguyên tử ↔ gen  → dùng cho RQ4   │
   └─────────────────────────────┬──────────────────────────────┘
                                 │
   ┌─────────────────────────────▼──────────────────────────────┐
   │ TRANSFORMER THÔ  (coarse-granularity, theo DTSyn)           │
   │ chuỗi: [CLS_c | pool(thuốc A) | pool(thuốc B) | pool(cell)] │
   │ 2 lớp, 4 đầu, hidden 64, dropout 0,6  (cấu hình của DTSyn)  │
   └─────────────────────────────┬──────────────────────────────┘
                                 ▼
          [CLS_f ; CLS_c] ──► MLP 2 lớp (512, ReLU, dropout)
                                 ▼
   ĐẦU RA ORDINAL (CORN): 2 logit tích lũy
        P(y > ant) ,  P(y > add)     →  3 lớp: ant < add < syn
   (ablation: 3 logit softmax thường; 3 logit + ma trận chi phí)
```

**Bốn quyết định thiết kế, mỗi cái có lý do:**

| Quyết định | Lý do |
|---|---|
| Không có type embedding A/B trong transformer mịn | Cho **đối xứng tuyệt đối** `f(A,B,c) = f(B,A,c)` theo cấu trúc, không phải nhờ tăng dữ liệu. DTSyn chỉ kiểm tra bằng thực nghiệm rằng thứ tự thuốc không ảnh hưởng; ở đây nó đúng theo định nghĩa. Có test đơn vị |
| GIN thay vì GCN ở nhánh thuốc | GIN mạnh hơn về mặt biểu diễn cho đồ thị phân tử. **Giữ GCN 2 lớp của DTSyn làm ablation** để biết chênh lệch đến từ đâu |
| Đầu CORN | Ba lớp có thứ tự; CORN bảo đảm tính nhất quán theo hạng, nên không cho ra dự đoán vô lý kiểu `P(y>add) > P(y>ant)` |
| Giữ hai transformer của DTSyn | Ablation của chính họ cho thấy bỏ cả hai thì ROC-AUC tụt 0,89 → 0,69. Đây là thành phần quan trọng nhất, không nên đổi |

### 5.2. Huấn luyện

| Khoản | Lựa chọn |
|---|---|
| Loss | CORN loss + trọng số lớp nghịch theo tần suất. Ablation: cross-entropy; CE có ma trận chi phí phạt nặng lỗi nhầm cực |
| Optimizer | AdamW, lr dò trong `[1e-5, 1e-3]`, weight decay 1e-4, cosine schedule, warmup 5%, gradient clipping 1,0 |
| Batch | 128 hoặc 256 |
| Dừng sớm | Theo **QWK trên tập validation**, patience 20. Không theo loss, không theo accuracy |
| Dò siêu tham số | Ngẫu nhiên 40 cấu hình trên validation của fold 0 (số lớp GNN 2–4, d_model 64/128/256, số đầu 4/8, dropout 0,1–0,6, lr). **Cùng ngân sách 40 cấu hình cho mọi baseline** |
| Số lần chạy | 5 seed × 5 fold × 5 split × 3 thiết lập nhãn cho mô hình chính |
| Ensemble | Báo cả một seed và cả trung bình 5 seed |
| Ghi lại | Mọi siêu tham số, phiên bản dữ liệu, số tham số vào `runs/<name>/config.json` |

**Lý do nhấn mạnh mục này:** lần chạy trước trong repo, baseline DeepSynergy chỉ đạt QWK 0,222, thấp bất thường với một mô hình nền tảng. Nguyên nhân gần như chắc chắn nằm ở chuẩn hóa đặc trưng hoặc ở việc không dò siêu tham số. Đây là chỗ mất điểm trước hội đồng, và §7 đặt nó thành một chặn cứng.

### 5.3. Baseline

| Nhóm | Mô hình | Mục đích |
|---|---|---|
| Tầm thường | majority (luôn đoán add) | Với 70,1% là add, accuracy vô nghĩa — bảng này chứng minh điều đó |
| Tầm thường | **chỉ dòng tế bào** (bỏ hết thông tin thuốc) | Nếu nó gần mô hình chính thì mô hình đang học đặc điểm dòng tế bào, không học tương tác thuốc. Hội đồng hay hỏi câu này |
| Tầm thường | chỉ thuốc (bỏ dòng tế bào) | Đối xứng với trên |
| Danh tính | one-hot thuốc + one-hot cell → MLP | **Trong lần chạy trước, baseline này đạt QWK 0,569 và thắng GNN trên PPI (0,369).** Phải có trong mọi bảng |
| Cổ điển | Morgan fingerprint + biểu hiện → XGBoost | Rẻ, mạnh, hay thắng mô hình sâu |
| Đã công bố | **DeepSynergy**, **DeepDDS**, **DTSyn** | Chạy lại trên cả ba thiết lập nhãn. Đây là ba cột so sánh chính |
| Ablation kiến trúc | bỏ transformer mịn · bỏ transformer thô · bỏ cả hai · GCN thay GIN · bỏ node2vec · **node2vec trên mạng xáo giữ bậc** | Tái lập ablation của DTSyn và kiểm tra đóng góp của mạng PPI |
| Ablation đầu ra | CORN · CE thường · CE có ma trận chi phí | Trả lời RQ2 |

Ablation "node2vec trên mạng xáo giữ bậc" là phép thử rẻ và đáng giá: repo này đã có module xáo mạng, và kết quả trước đó cho thấy mạng PPI thật không hơn mạng xáo. Nếu lặp lại ở đây thì đó là một quan sát đáng viết, vì DTSyn và MD-Syn đều dùng node2vec trên PPI mà không kiểm tra.

---

## Phần 6. XAI — áp dụng như thế nào

Chỉ bắt đầu sau khi mô hình đã qua mốc ở §7. Giải thích một mô hình yếu thì không ai đọc.

### 6.1. Ba đơn vị giải thích

| Đơn vị | Lấy ra bằng cách nào | Tương ứng với bài nào |
|---|---|---|
| **Gen** | IG trên vector biểu hiện; baseline là **trung bình biểu hiện của các dòng tế bào trong tập train** (không phải vector 0) | TranSynergy (SHAP trên gen), DTSyn (attention trên gen) |
| **Cấu trúc con phân tử** | IG trên mặt nạ mảnh BRICS `μ_frag ∈ [0,1]`; GNNExplainer trên đồ thị phân tử để đối chiếu | DeepDDS, AttenSyn, MD-Syn |
| **Cặp nguyên tử ↔ gen** | Ma trận attention của transformer mịn | DTSyn, MD-Syn |

Xóa **mảnh BRICS nguyên vẹn** thay vì nguyên tử rời: xóa nguyên tử lẻ tạo phân tử không tồn tại nên Fid+ bị thổi phồng. Mảnh vẫn lạc phân phối, nhưng null dùng đúng cùng phép xóa nên hiệu số còn nghĩa.

### 6.2. Ba mục tiêu attribution — đây là đóng góp N2

Cùng một mô hình, cùng một mẫu, ba cách lấy attribution:

| Cấp | Mục tiêu | Ai đang làm |
|---|---|---|
| (i) logit | `z_syn` | Toàn bộ literature hiện nay |
| (ii) **tương phản** | `Δ_syn = z_syn − z_add` | **Đề xuất của luận văn.** Lớp add là mốc cộng tính, nên hiệu này đúng là "điều gì đẩy bộ ba ra khỏi trạng thái cộng tính về phía hiệp đồng" |
| (iii) tương phản phía đối kháng | `Δ_ant = z_ant − z_add` | Chưa ai làm, vì thiết lập nhị phân bỏ lớp ant. Dùng cho RQ6 |

Với đầu CORN, `z_syn − z_add` lấy từ logit tích lũy `P(y > add)`; viết rõ công thức trong chương phương pháp.

Ba phép thử để chứng minh (ii) có giá trị, nếu trượt thì phải biết sớm:
1. **Phân kỳ.** Jaccard@k giữa top-k của (ii) và của (i). Trùng gần hết thì ý tưởng vô nghĩa.
2. **Đặc hiệu.** Gen trong top-k của `Δ_syn` không được trùng nhiều với top-k của `Δ_ant`. Trùng nhiều nghĩa là gen đó chỉ đại diện "có tác động nói chung".
3. **Đối lập.** Với bộ ba nhãn ant, cơ chế phát hiện được phải khác **về chất** (khác pathway) so với bộ ba syn, không chỉ đảo dấu. Đây chính là RQ6.

### 6.3. Bộ đo, mỗi chỉ số một null

Nguyên tắc: mọi chỉ số báo dưới dạng **(giá trị, null, hiệu)**, kèm CI bootstrap. Null phải đi qua đúng bộ trích như kết quả thật.

| Nhóm | Chỉ số | Null |
|---|---|---|
| **Faithfulness** | **Fid+**: xóa top-k% (gen, hoặc mảnh) rồi đo độ đổi của logit | Xóa ngẫu nhiên cùng số lượng, cùng kích thước, 20 lần |
| | **Fid−**: chỉ giữ top-k | Giữ ngẫu nhiên cùng số lượng. **Báo kèm cảnh báo**: đầu vào lạc phân phối nặng, không dùng để kết luận |
| | Sparsity, comprehensiveness, sufficiency | — |
| | Completeness gap của IG | — |
| **Attention có trung thực không (RQ4)** | Xóa theo top-k attention so với xóa theo top-k IG, trên cùng k | Xóa ngẫu nhiên |
| | **Faithfulness Violation Test** (Liu et al., ICML 2022) | Theo đúng giao thức của bài |
| **Stability (RQ5)** | Jaccard@k qua 5 seed · qua 5 fold · **qua 4 điểm synergy** · **qua 3 ngưỡng** | Bộ ba bị hoán vị nhãn |
| **Plausibility** | Làm giàu top-50 gen với **đích của A hoặc B** (hypergeometric) — cùng cách đo như con số 62,2% của SynergyX | Tập gen ngẫu nhiên cùng kích thước, khớp phân bố mức biểu hiện |
| | Làm giàu với pathway KEGG chứa đích | Như trên |

**Tách riêng faithfulness và plausibility.** Faithfulness hỏi lời giải thích có phản ánh đúng cái mô hình dùng không; plausibility hỏi nó có khớp sinh học không. Gộp hai thứ là lỗi phần lớn literature mắc phải. Trung thực nhưng không hợp lý sinh học nghĩa là **mô hình** học sai; hợp lý nhưng không trung thực nghĩa là **explainer** sai.

**Chỉ giải thích lớp syn và lớp ant.** "Gen nào khiến cặp thuốc này *không* tương tác" là câu hỏi thoái hóa. Nêu rõ điều này trong chương phương pháp thay vì để hội đồng phát hiện.

### 6.4. Case study — chọn trước khi chạy

Ghi danh sách vào repo kèm trích dẫn **trước** khi chạy explain, không sửa về sau.

1. **ETOPOSIDE + MK-2206 trên CAOV3 và NCIH23.** Đây **đúng là ví dụ duy nhất mà DTSyn đem ra giải thích**: hiệp đồng ở CAOV3, đối kháng ở NCIH23. DTSyn báo các gen SNAP25, GALE, PRKCD, PIK3R3, DDIT4 có hệ số tương tác cao, chỉ đối chiếu literature. Đây là cơ hội **so sánh trực tiếp**: cùng một cặp, cùng hai dòng tế bào, lời giải thích của SynGT ở cấp tương tác có trỏ vào đâu, và có vượt null không. Một cặp đối kháng và một cặp hiệp đồng trong cùng một ca là điều kiện hoàn hảo cho RQ6.
2. **MK-2206 + MK-8669** — ca của MD-Syn, họ báo PAK6.
3. Một cặp có cơ chế đã biết rõ, chọn từ O'Neil theo quy tắc ghi trước: syn ở phần lớn dòng tế bào và cả hai thuốc có đích trên mạng.

**Bắt buộc báo cáo ít nhất một ca mà mô hình giải thích sai.** Sự trung thực này làm luận văn mạnh lên, và nó chặn trước phản biện kiểu "ca được chọn sau khi xem kết quả".

---

## Phần 7. Thực thi

### 7.1. Module

```
src/data/   oneil.py (trích O'Neil từ DrugComb, 3 thiết lập nhãn, 4 điểm)
            smiles.py (ChEMBL 3 tầng, chuẩn hóa RDKit, InChIKey)
            featurize.py (đồ thị, đặc trưng nguyên tử 78 chiều, mảnh BRICS)
            cell.py (978 gen landmark, z-score theo fold, node2vec STRING)
            splits.py (random, leave-combo, leave-drug, leave-cell, leave-tumor)
src/model/  syngt.py (GNN + 2 transformer)   corn.py (đầu ordinal + loss)
src/repro/  deepsynergy.py  deepdds.py  dtsyn.py    ← mốc G1
src/xai/    masks.py  ig.py  gnn_explainer.py  attention.py  fvt.py
src/eval/   metrics.py (QWK, macro-F1, AUPRC từng lớp, lỗi nhầm cực)
            faithfulness.py  stability.py  plausibility.py  report.py
src/tests/  đối xứng f(A,B,c)=f(B,A,c) · completeness của IG
            CORN nhất quán theo hạng · z-score chỉ fit trên train
            InChIKey trùng thì cùng một thuốc · validation chia cùng đơn vị với split ngoài
```

### 7.2. Thứ tự và mốc quyết định

| Bước | Việc | Mốc |
|---|---|---|
| 1 | Tiền xử lý §4 đầy đủ; bảng phân bố lớp cho 3 thiết lập × 4 điểm | Số bộ ba và số thuốc đã chốt và ghi vào `provenance.json` |
| 2 | **Tái lập DeepDDS và DTSyn ở thiết lập (a)** | **G1 — chặn cứng.** ROC-AUC trong khoảng 0,86–0,92 ở random 5-fold. Không đạt thì **dừng mọi việc khác** và sửa pipeline. Đây là bài học từ con số 0,222 |
| 3 | SynGT + dò 40 cấu hình; test đơn vị, nhất là test đối xứng và test rò z-score | Mọi test đơn vị phải qua trước khi sweep |
| 4 | Sweep 5 split × 3 thiết lập nhãn; bảng RQ1 và RQ2; ablation | **G2.** SynGT ở thiết lập (a) phải ngang DTSyn (±0,02 ROC-AUC); ở thiết lập (c) phải hơn one-hot (QWK 0,569) |
| 5 | XAI: ba đơn vị, ba mục tiêu attribution; RQ3, RQ4 | **G3.** Fid+ không vượt null → báo cáo lời giải thích không trung thực; đó cũng là kết quả |
| 6 | Stability (RQ5), đối kháng (RQ6), plausibility, case study | — |
| 7 | Viết bài báo và luận văn | — |

### 7.3. Tính toán

Hạ tầng đã kiểm tra: **A100 80 GB**, torch 2.11, CUDA sẵn. Dữ liệu nhỏ (21.571 bộ ba, 38 thuốc) nên mỗi run chỉ vài phút. Tổng khối lượng khoảng 400–500 run, chạy trong vài ngày.

**Ràng buộc thật là RAM: 50 GiB theo cgroup** (`free -h` báo con số của host, sai ở đây). Lúc kiểm tra máy đang ở 70,3%. Hệ quả:
- Đọc `summary_table_v1.4.csv` (193 MB) **theo chunk**, ghi parquet rồi mới dùng.
- Chạy `/mnt/data/tm/check_mem.sh -b` trước và trong mỗi bước nặng; dừng thêm tải nếu mã trả về khác 0.
- Chú ý điểm nghẽn thật của transformer mịn: chuỗi dài khoảng `n_A + n_B + 950` token. Với 950 token gen, ma trận attention là 950² mỗi đầu mỗi mẫu. Nếu quá nặng thì **giảm xuống 300–400 gen chọn theo phương sai**, và ghi rõ lựa chọn này. Đây là rủi ro kỹ thuật cần thử ngay ở bước 3.

---

## Phần 8. Kết quả có thể đạt được

Đây là kỳ vọng có cơ sở, không phải lời hứa. Nêu rõ trong luận văn rằng đây là khoảng dự kiến trước khi chạy.

### 8.1. Phần dự đoán

| Thiết lập | Chỉ số | Kỳ vọng | Căn cứ |
|---|---|---|---|
| (a) nhị phân bỏ vùng giữa, random 5-fold | ROC-AUC | **0,88–0,92** | DTSyn 0,89; DeepDDS khoảng 0,93 |
| (a), leave-combination | ROC-AUC | 0,76–0,80 | DTSyn 0,78 |
| (a), leave-drug | ROC-AUC | 0,71–0,76 | DTSyn 0,73 |
| (b) nhị phân giữ toàn bộ | ROC-AUC | **tụt 0,05–0,12 so với (a)** | Vùng 0–10 là vùng ranh giới; đây là con số trung tâm của RQ1 |
| (c) ba lớp ordinal, leave-combination | **QWK** | **0,50–0,62** | One-hot MLP đã đạt 0,569 trong lần chạy trước; mô hình đa phương thức nên bằng hoặc hơn |
| (c) | macro-F1 | 0,45–0,58 | Lớp syn chỉ 6,4% |
| (c) | AUPRC lớp syn | 0,20–0,40 | Lớp thiểu số nặng; con số này phải báo riêng |
| (c) | **lỗi nhầm cực (syn↔ant)** | **CORN thấp hơn CE 20–40% tương đối** | Đóng góp thực dụng của RQ2 |

**Rủi ro đã lường: có thể SynGT không thắng one-hot ở thiết lập (c).** Lần chạy trước, one-hot thắng GNN trên PPI khá rõ (0,569 so với 0,369). Nếu lặp lại, đó **không phải thất bại của luận văn**, vì đóng góp nằm ở N1 (đặt bài toán ordinal và đo cái giá của vùng trung tính) và ở phần XAI. Nhưng phải báo cáo thẳng, và phải thảo luận: với leave-combo trên một bộ dữ liệu chỉ 38 thuốc, danh tính thuốc là một đặc trưng rất mạnh.

### 8.2. Phần XAI

| RQ | Chỉ số | Kỳ vọng |
|---|---|---|
| RQ3 | Jaccard@20 giữa cấp (ii) và cấp (i) | **0,2–0,5**, tức khác nhau rõ. Nếu > 0,8 thì phép trừ không cần thiết và phải viết ra |
| RQ4 | Fid+ của IG so với null | Vượt null rõ |
| RQ4 | Fid+ của attention so với của IG | **Attention yếu hơn IG**; có khả năng trượt Faithfulness Violation Test. Kết quả này củng cố cảnh báo của Kakkad et al. 2023 ngay trong lĩnh vực hiệp đồng thuốc |
| RQ5 | Jaccard@20 qua seed | 0,3–0,6 |
| RQ5 | Jaccard@20 **qua điểm synergy** (Loewe ↔ Bliss) | **0,1–0,4**, tức thấp. Nếu đúng vậy thì "cơ chế" mà các bài báo công bố phần lớn là ảnh của một lựa chọn quy ước — đây có thể là phát hiện mạnh nhất của luận văn |
| RQ6 | Pathway làm giàu ở nhóm ant so với nhóm syn | Khác nhau; nếu giống thì lớp ant không mang cơ chế riêng |
| Plausibility | Tỷ lệ cặp có top-50 gen làm giàu đích của A hoặc B | 30–60%, so với SynergyX báo 62,2% ở một cách đo khác |

### 8.3. Đầu ra của project

1. **Một bài báo** đủ format chuẩn: Abstract · Introduction · Related work · Methods (dữ liệu, kiến trúc, ba thiết lập nhãn, XAI) · Experiments (5 split, baseline, ablation) · Results (RQ1–RQ6) · Discussion · Limitations · Data and code availability. Nơi gửi: *Briefings in Bioinformatics*, *Bioinformatics*, *BMC Bioinformatics*, *Journal of Cheminformatics*.
2. **Luận văn sáu chương**: (1) nền tảng và tổng quan · (2) dữ liệu, ba thiết lập nhãn, giao thức có null · (3) SynGT và bảng hiệu năng (RQ1, RQ2) · (4) XAI cấp tương tác (RQ3) · (5) attention có trung thực không và độ ổn định (RQ4, RQ5) · (6) cơ chế đối kháng, case study, giới hạn (RQ6).
3. **Code và dữ liệu đã xử lý** công khai, kèm `provenance.json` và file cấu hình của mọi run.

**Câu mạnh nhất luận văn được phép viết:** *"lời giải thích trung thực với mô hình ở mức vượt null, và ổn định qua seed ở mức X, nhưng kém ổn định khi đổi định nghĩa điểm synergy"* — không bao giờ là "mô hình tìm đúng cơ chế sinh học".

---

## Phần 9. Rủi ro

| Rủi ro | Mức | Dấu hiệu sớm | Xử lý |
|---|---|---|---|
| **Không tái lập được số của DTSyn/DeepDDS** | **Cao** | G1 trượt | Dừng mọi việc khác. So từng bước với code gốc: đặc trưng nguyên tử, ngưỡng nhãn, cách gộp bản lặp, cách chia fold |
| **Transformer mịn quá nặng với 950 token gen** | **Cao** | OOM hoặc một epoch quá lâu | Giảm xuống 300–400 gen theo phương sai; hoặc gộp gen theo pathway thành token; ghi rõ lựa chọn và chạy ablation |
| Thiếu SMILES cho MK-4541, MRK-003 | Vừa | Ngay bước 1 | Tìm trong code DeepDDS và DTSyn; nếu không có thì loại và báo cáo số bộ ba còn lại |
| SynGT không thắng one-hot ở thiết lập 3 lớp | Vừa–Cao | G2 | Đã lường ở §8.1. Báo cáo thẳng; đóng góp nằm ở N1 và phần XAI |
| Lớp syn chỉ 6,4%, học không nổi | Vừa | Recall lớp syn rất thấp | Trọng số lớp, focal loss; báo AUPRC từng lớp; nếu vẫn thấp thì **nói thẳng là lớp này chưa đủ dữ liệu** thay vì che bằng metric tổng hợp |
| Mô hình học "đoán add" để tối ưu loss | Vừa | Accuracy cao mà macro-F1 thấp | Theo dõi QWK và macro-F1 khi train, không theo loss; đối chiếu baseline majority |
| Tính mới của N1 bị trùng | Vừa | Khi viết related work | Đã tra ba lần và chưa thấy bài nào làm ordinal + QWK, nhưng **phải tự kiểm chứng lại trước khi nộp**. Nếu trùng, dồn trọng tâm sang N2 và N3 |
| Attribution nhiễu ở vùng ranh giới | Vừa | Hiệu logit dao động mạnh giữa seed | Trung bình qua 5 seed; lọc theo độ tin cậy dự đoán; bootstrap CI; **phân tích riêng nhóm ranh giới** vì đó là nhóm thú vị nhất |
| Xóa mảnh tạo phân tử không có thật | Vừa | Null cũng cho Fid+ rất cao | Null dùng đúng cùng phép xóa; chỉ đọc hiệu số, không đọc giá trị tuyệt đối |
| Vượt 50 GiB RAM | Vừa | `check_mem.sh` trả mã 1 hoặc 2 | Stream theo chunk, cache ra đĩa, giảm số worker |
| Hội đồng hỏi "giải thích này có đúng sinh học không" | — | — | Trả lời bằng §6.3: faithfulness và plausibility báo riêng, có null, và có một ca giải thích sai được báo cáo |

---

## Phần 10. Lộ trình 12 tháng

| Tháng | Việc | Kết quả |
|---|---|---|
| 1 | Tiền xử lý §4 đầy đủ; SMILES; bảng phân bố lớp | Dữ liệu chốt, có `provenance.json` |
| 2 | **Tái lập DeepSynergy, DeepDDS, DTSyn** | **G1** — pipeline được chứng minh đúng |
| 3 | SynGT, đầu CORN, test đơn vị; giải quyết rủi ro độ dài chuỗi | Mô hình chạy được |
| 4 | Dò siêu tham số; sweep thiết lập (a) và (b) | Bảng RQ1 |
| 5 | Sweep thiết lập (c), 5 split; ablation đầy đủ | **G2** — bảng RQ1, RQ2, phần cứng nhất của luận văn |
| 6–7 | XAI: ba đơn vị, ba mục tiêu attribution; Fid±; RQ3, RQ4 | **G3** |
| 8 | Stability qua seed, fold, điểm synergy, ngưỡng (RQ5) | Bảng RQ5 |
| 9 | Cơ chế đối kháng (RQ6); plausibility; case study gồm ETOPOSIDE + MK-2206 | Chương case study |
| 10 | Viết và nộp bài báo | Bài nộp |
| 11–12 | Viết luận văn, chuẩn bị bảo vệ | Bảo vệ |

---

## Phụ lục A. Tái dùng được gì từ code hiện có

| Có sẵn | Dùng cho |
|---|---|
| `src/data/dataset.py` — sinh nhãn ba lớp, `leave_combo_split` | §3.3, §3.4; mở rộng thêm 4 kiểu split |
| `src/data/build_targets.py` — map ChEMBL cho 38 thuốc, lấy mechanism | §3.2, và plausibility ở §6.3 |
| `src/data/rewire.py` — xáo mạng giữ bậc | Ablation node2vec trên mạng xáo ở §5.3 |
| `src/explain/edge_ig.py` — IG trên mặt nạ, đường tích phân α = t³, 32 bước, cache theo (thuốc, cell) | §6.1, §6.2. **Bài học đã có: lưới α đều cho sai số completeness rất lớn** |
| `src/eval/explain_metrics.py` — Jaccard, overlap@k, fidelity, stability, bootstrap CI | §6.3 |
| `src/training/sweep.py` — điều phối bằng file lock, bỏ qua run đã có `metrics.json` | §7.2 |
| `src/tests/test_all.py` — 10 test đang pass | Mở rộng theo §7.1 |
| Thiếu | **`rdkit` bắt buộc cài.** `torch_geometric` không bắt buộc: GIN viết được bằng torch thuần với gather/index_add, và repo đã có sẵn cách làm này |

**Kết quả của hướng cũ** (GNN trên PPI, mạng thật không giúp dự đoán: hiệu QWK −0,016 [−0,034; 0,001] so với mô hình không mạng; one-hot 0,569 so với GNN 0,369) nằm ở [ket_qua_full_run.md](ket_qua_full_run.md). Dùng ở hai chỗ: một tiểu mục trong chương 1 để lý giải vì sao SynGT đặt đồ thị phân tử làm trung tâm và chỉ dùng PPI cho embedding gen; và ablation "node2vec trên mạng xáo" ở §5.3.

## Phụ lục B. Những chỗ cần tự kiểm chứng trước khi nộp

1. Tính mới của N1: tra lại "ordinal drug synergy", "three-class synergy QWK" trên Google Scholar và PubMed.
2. Số bộ ba của O'Neil: pipeline hiện tại cho 21.571, DTSyn ghi 23.052, DeepSynergy ghi hơn 20.000 với 583 tổ hợp. Phải đối chiếu bước lọc và ghi rõ lý do chênh lệch.
3. Thông tin về MD-Syn, AttenSyn, SynergyX trong bản này lấy từ khảo sát trong repo (`khao_sat_xai_graph_drug_synergy.md`) — **đọc lại bản đầy đủ trước khi trích vào luận văn**.
4. DTSyn có vài chỗ không nhất quán cần lưu ý khi trích: chiều của vector dòng tế bào ghi 978 ở một chỗ và 954 ở chỗ khác; abstract nói TPR tốt nhất trên cả năm tập độc lập nhưng phần kết quả báo BACC tốt nhất ở bốn trong năm.

## Phụ lục C. Đã kiểm tra những gì, ngày 16/11/2026

| Kiểm tra | Kết quả |
|---|---|
| GPU | NVIDIA A100-SXM4-80GB · torch 2.11.0+cu130 · CUDA khả dụng |
| RAM | 50 GiB theo cgroup, đang dùng 70,3%. `free -h` báo số của host, **không dùng được** |
| Đĩa `/mnt/data` | Còn 622 GB |
| `summary_table_v1.4.csv` (193 MB) | 466.033 khối tổ hợp · 709.187 khối đơn trị liệu · 4.150 thuốc · 112 dòng tế bào · không khuyết `synergy_loewe` |
| O'Neil trong pipeline hiện tại | 21.571 bộ ba · 38 thuốc · 37 dòng tế bào · phân bố ba lớp Loewe ±10: ant 23,4% / add 70,1% / syn 6,4% |
| Đích thuốc | 33/38 thuốc có đích trên STRING; trung vị 2 đích mỗi thuốc; 5 thuốc không có đích nào |
| ChEMBL `pref_name__iexact` | Hoạt động; **34/38 thuốc O'Neil có SMILES** |
| ChEMBL `search.json` (khớp mờ) | **Không đáng tin**: "gemcitabine" → "GEMCITABINE ELAIDATE" |
| PubChem REST | Bị chặn từ IP máy này |
| NCI-ALMANAC `ComboDrugGrowth_Nov2017.zip` | HTTP 200, 83 MB |
| Code gốc: KristinaPreuer/DeepSynergy · Sinwang404/DeepDDS · PaddleHelix (DTSyn) | Truy cập được |
| `rdkit`, `torch_geometric` | **Chưa cài** |

---

## Đọc gì

**Bốn bài nền**
1. Hu J. et al. **DTSyn: a dual-transformer-based neural network to predict synergistic drug combinations**. *Brief Bioinform* 2022;23(5):bbac302. https://academic.oup.com/bib/article/23/5/bbac302/6652782 · bioRxiv 2022.03.29.486200 · code: https://github.com/PaddlePaddle/PaddleHelix/tree/dev/apps/drug_drug_synergy/DTSyn
2. Wang J. et al. **DeepDDS**. *Brief Bioinform* 2022;23(1):bbab390 · arXiv:2107.02467 · code: https://github.com/Sinwang404/DeepDDS
3. Liu Q., Xie L. **TranSynergy**. *PLoS Comput Biol* 2021;17(2):e1008653. https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653 · PMC7906476
4. **MD-Syn**. *Front Pharmacol* 2025;16:1564339 · arXiv:2501.07884

**Mốc và bối cảnh**
5. Preuer K. et al. **DeepSynergy**. *Bioinformatics* 2018;34(9):1538–1546 · code: https://github.com/KristinaPreuer/DeepSynergy — Pearson 0,73; AUC 0,90; thuốc mới 0,48; dòng tế bào mới 0,57
6. O'Neil J. et al. **An unbiased oncology compound screen...** *Mol Cancer Ther* 2016 — bộ dữ liệu gốc
7. Abbasi F., Rousu J. **New methods for drug synergy prediction: a mini-review**. *Curr Opin Struct Biol* 2024 · arXiv:2404.02484 — vì sao không chép số giữa các bài
8. Zagidullin B. et al. **DrugComb**. *Nucleic Acids Res* 2019 — nguồn dữ liệu

**Ordinal và mất cân bằng lớp**
9. Cao W. et al. **CORN: rank-consistent ordinal regression**, 2022; Cao W., Mirjalili V., Raschka S. **CORAL**, *Pattern Recognit Lett* 2020
10. **Quadratic weighted kappa cho phân lớp ordinal**, *Applied Soft Computing* 2023
11. **Class Distance Weighted Cross-Entropy Loss**, arXiv:2202.05167 — ma trận chi phí cho lỗi nhầm cực
12. **SynergyFinder** — quy ước ngưỡng ±10 và bốn mô hình tham chiếu. https://synergyfinder.aittokallio.group/synfin_docs/

**XAI**
13. Sundararajan M., Taly A., Yan Q. **Integrated Gradients**. *ICML* 2017
14. Ying R. et al. **GNNExplainer**. *NeurIPS* 2019
15. Liu Y. et al. **Rethinking Attention-Model Explainability through Faithfulness Violation Test**. *ICML* 2022, PMLR v162 — dùng cho RQ4
16. Kakkad J. et al. **A survey on explainability of graph neural networks**. arXiv:2306.01958 — cảnh báo attention không bảo đảm faithfulness
17. Rao J., Zheng S., Yang Y. **Quantitative evaluation of explainable graph neural networks for molecular property prediction**, 2022 — mẫu để dựng benchmark giải thích
18. **SANEpool**. *Cancers* 2023;15(17):4210 — hình mẫu giải thích có kiểm định thống kê (KS test, 45 dòng tế bào)
