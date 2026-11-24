# SynGT — tài liệu tham khảo, quy trình xây dựng, kết quả hiện tại

Cập nhật 20/11/2026. Nguồn: các file khảo sát trong repo, `reports/planner_de_xuat_3.md`,
code trong `src/`, và bảng số `reports/tables/*.csv` (sinh lúc 14:33 ngày 20/11).

Lúc viết file này còn hai việc **đang chạy**, nên vài ô trong bảng sẽ đổi:
`run_gap.sh` (DeepSynergy ở các split khó, 77/136 run xong; XGBoost 1/89 run) và phần giải thích
chéo theo điểm synergy. Chỗ nào phụ thuộc hai việc đó đều có ghi *(đang chạy)*.

Ký hiệu độ tin cậy của trích dẫn, giữ đúng cách các file khảo sát đã dùng:
**[FT]** đã đọc toàn văn · **[ABS]** mới đọc abstract hoặc qua bài tổng quan · **[KT]** phải kiểm lại
trước khi trích vào luận văn.

---

# Phần 1. Danh sách bài báo

## 1.1. Nhóm dùng trực tiếp trong project

### a) Khung mô hình và baseline

| Bài | Vai trò trong project |
|---|---|
| Hu J. et al. **DTSyn**. *Brief Bioinform* 2022;23(5):bbac302 · code trong PaddleHelix [FT] | **Khung chính của SynGT**: hai transformer mịn/thô, token nguyên tử + token gen, node2vec trên PPI. Cũng là nguồn của giao thức nhị phân bỏ vùng 0–10 mà RQ1 phản biện, và của ví dụ giải thích ETOPOSIDE + MK-2206 trong case study |
| Wang J. et al. **DeepDDS**. *Brief Bioinform* 2022;23(1):bbab390 · arXiv:2107.02467 [FT] | Baseline GNN chính. SynGT lấy lại đặc trưng nguyên tử 78 chiều và readout `[pA+pB ; \|pA−pB\| ; cell]` |
| Preuer K. et al. **DeepSynergy**. *Bioinformatics* 2018;34(9):1538–1546 [FT] | Baseline mạnh nhất trong bảng của tôi. Nguồn ý tưởng nhánh fingerprint Morgan |
| Liu Q., Xie L. **TranSynergy**. *PLoS Comput Biol* 2021;17(2):e1008653 [FT] | Tham chiếu giải thích cấp gen (SHAP + GSEA) |
| **MD-Syn**. *Front Pharmacol* 2025;16:1564339 · arXiv:2501.07884 [FT] | Tham chiếu attention thuốc–gen; case study MK-2206 + MK-8669 |
| **AttenSyn**. *J Chem Inf Model* 2024 [ABS] [KT: hai file trong repo ghi số tập khác nhau] | Bài thứ ba trình bày attention như lời giải thích (đối tượng của RQ4) |

### b) Dữ liệu, nhãn, nguồn sinh học

| Nguồn | Vai trò |
|---|---|
| O'Neil J. et al. *Mol Cancer Ther* 2016 | Bộ dữ liệu gốc |
| Zagidullin B. et al. **DrugComb**. *Nucleic Acids Res* 2019 | Đường lấy O'Neil (v1.4, Zenodo 11102665) |
| **SynergyFinder** (tài liệu) | Quy ước ngưỡng ±10 và bốn mô hình tham chiếu |
| Yadav B. et al. **ZIP**. *Comput Struct Biotechnol J* 2015 | Một trong bốn điểm synergy dùng cho phân tích độ nhạy |
| STRING v12 · L1000 (GSE92742) · DepMap/CCLE · KEGG · ChEMBL | Mạng PPI, 978 gen landmark, biểu hiện gen, pathway để chấm điểm, SMILES và đích thuốc |

### c) Đầu ra có thứ tự (ordinal)

| Bài | Vai trò |
|---|---|
| Cao W. et al. **CORN: rank-consistent ordinal regression**, 2022 [FT] | Đầu ra của SynGT |
| Cao W., Mirjalili V., Raschka S. **CORAL**. *Pattern Recognit Lett* 2020 [ABS] | Tiền thân của CORN, nêu trong phần phương pháp |
| **Weighted kappa cho phân lớp ordinal**. *Applied Soft Computing* 2023 [ABS] | Cơ sở của metric chính QWK |
| **Class Distance Weighted Cross-Entropy**. arXiv:2202.05167 [ABS] | Ablation loss có ma trận chi phí |
| Vargas V.M. et al. **Cumulative link models for deep ordinal classification**. arXiv:1905.13392 [ABS] | Bối cảnh họ phương pháp |

### d) XAI — phương pháp và cách đánh giá

| Bài | Vai trò |
|---|---|
| Sundararajan M., Taly A., Yan Q. **Integrated Gradients**. *ICML* 2017 [FT] | Phương pháp attribution chính, dùng cho cả ba đơn vị giải thích |
| Ying R. et al. **GNNExplainer**. *NeurIPS* 2019 [FT] | Explainer thứ hai để đối chiếu |
| Liu Y. et al. **Faithfulness Violation Test**. *ICML* 2022, PMLR v162 [FT] | Kiểm định attention cho RQ4 |
| Kakkad J. et al. **A survey on explainability of GNNs**. arXiv:2306.01958 [FT] | Cảnh báo attention không bảo đảm faithfulness |
| Rao J., Zheng S., Yang Y. *Patterns* 2022;3(12):100628 [FT] | Mẫu để dựng benchmark chất lượng giải thích |
| **SANEpool**. *Cancers* 2023;15(17):4210 [FT] | Hình mẫu giải thích có kiểm định thống kê (KS test) |
| Janizek J.D. et al. **Integrated Hessians**. *JMLR* 2021;22 [ABS] | Nền lý thuyết cho tương tác bậc hai |
| Grabisch M., Roubens M. *Int J Game Theory* 1999 [ABS] | Toán tử tương tác cặp mảnh của tôi cùng dạng với Shapley interaction index |
| **GraphFramEx**. *LoG* 2022 · **GraphXAI/ShapeGGen**. *Sci Data* 2023 [ABS] [KT công thức] | Nguồn định nghĩa Fid+/Fid− |

### e) Nhóm phản biện — chỗ đứng của ba trục đóng góp

| Bài | Vai trò |
|---|---|
| Abbasi F., Rousu J. *Curr Opin Struct Biol* 2024 · arXiv:2404.02484 [FT] | Lý do không chép số giữa các bài; leave-drug khó hơn leave-pair (p = 0,026) |
| **SynVerse**. Tasnina N. et al. *Brief Bioinform* 2025;26(6):bbaf676 [ABS] | 16 kiến trúc không hơn MLP one-hot; rewiring mạng gần như vô hại |
| **One-hot news**. Çandır E.B. et al. *Bioinformatics* 2026;42(3):btag040 [ABS] | Thay đặc trưng bằng one-hot chỉ đổi MSE −1%…+3%; attribution sụp khi bộ ba lặp lại |
| **PAIRWISE** benchmark. PMC12869695, preprint 01/2026 [ABS] | Bảng so sánh khung nhìn thuốc; chỉ áp dụng ở quy mô DrugComb đầy đủ |
| Faber L. et al. *KDD* 2021 [ABS] | Năm cạm bẫy khi so lời giải thích với ground truth cài sẵn |
| Azzolin S. et al. *ICLR* 2025 · arXiv:2406.15156 [ABS] | Các metric faithfulness không thay thế nhau |

## 1.2. Corpus của bài tổng quan tài liệu (36 nguồn)

Đây là danh mục của `literature_review.md` và bản dịch `tong_quan_tai_lieu.md` — hai file có
**danh mục tham khảo trùng khít** (đã đối chiếu). Cách chọn: bốn tầng tìm kiếm (Boolean trên cơ sở
dữ liệu, truy vết trích dẫn, trích dẫn xuôi, tìm theo nghĩa), sàng theo mức liên quan, độ mới và
độ chặt phương pháp.

**Tổng quan và khảo sát (10)** — Abbasi & Rousu 2024 · Berry & Cheng 2025 (arXiv:2509.07887) ·
Besharatifard & Vafaee 2024 (*AI Review* 57:49) · Gangwal & Lavecchia 2026 (*Comput Sci Rev* 61:100943) ·
Lavecchia 2025 (*WIREs Comput Mol Sci*) · Li Y. et al. 2025 (*npj Drug Discovery* 2:30) ·
Nandan et al. 2025 (*Neural Comput Appl* 37) · Pan et al. 2023 (*Life* 13(9):1878) ·
Torkamannia et al. 2022 (*BIB* 23(3):bbac075) · Wang Y. et al. 2024 (*Clin Transl Discovery* 4(4):e317) ·
Zhang O. et al. 2025 (*Chem Rev*).

**Nền tảng GNN và XAI (5)** — Kipf & Welling 2017 (GCN) · Veličković et al. 2018 (GAT) ·
Sundararajan et al. 2017 (IG) · Ying et al. 2019 (GNNExplainer) · Kakkad et al. 2023 (khảo sát XAI-GNN).

**Dự đoán đáp ứng thuốc đơn (DRP) (11)** — Jia et al. 2021 (*Nat Commun* 12:1740) ·
Rampásek et al. 2019 (Dr.VAE) · Wei et al. 2022 (scPreGAN) · Jiang & Li 2024 (DeepDR) ·
Liu X. et al. 2022 (GraphCDR) · Peng et al. 2022 (*Bioinformatics* 38(19)) ·
Li Y. et al. 2023 (MMCL-CDR) · Duan et al. 2026 (*Neural Networks*) ·
Xiao et al. 2025 (*Sci Rep* 15) · Okyere et al. 2025 (*CSBJ*) · Partin et al. 2026 (*BIB* 27(1):bbaf667).

**XAI cho DRP và cơ chế (8)** — Wang C. et al. 2025 (XGDP, *Sci Rep* 15:179) ·
Shi et al. 2025 (DRExplainer, arXiv:2408.12139) · Liu X. & Zhang W. 2023 (*PLOS CB* 19(8):e1011382) ·
Wang Z. et al. 2023 (XMR) · Yoon & Lee 2026 (GCNPath) · Yu & Fan 2025 (*Sci Rep* 15:20824) ·
Rao et al. 2022 (*Patterns*) · Dong et al. 2023 (SANEpool, *Cancers* 15(17):4210).

**Hiệp đồng thuốc (2)** — Wang T. et al. 2023 (AttenSyn) và nhóm bài đã liệt ở §1.1.

> Nhận xét để viết phần related work: corpus này **nghiêng về DRP**. Phần hiệp đồng thuốc mỏng,
> và đó là lý do phải đọc thêm hai file khảo sát ở §1.3.

## 1.3. Bài chỉ xuất hiện trong hai file khảo sát chuyên sâu

Hai file này hẹp hơn và sát project hơn: `khao_sat_xai_graph_drug_synergy.md` (XAI cho hiệp đồng
thuốc, 33 nguồn) và `reports/XAI đồ thị mạng sinh học.md` (giải thích bằng đường dẫn mạng, ~25 công trình).
Phần lớn ở mức [ABS] — bảng đối sánh trong các file đó ghi rõ ô nào chưa xác minh.

**Giải thích cấp phân tử** — ResGIN-Att (arXiv:2604.21473) · DPASyn (arXiv:2505.19144).

**Giải thích cấp gen / pathway** — GraphSynergy (*JAMIA* 2021) · IDSP (arXiv:2105.07082) ·
PathSynergy (*BIB* 2025;26(2):bbaf192) · SynerGNet (*Biomolecules* 2024) · SynPathy (*Mol Cancer Res* 2022) ·
DeepSignalingSynergy (*AMIA* 2020) · DeepSignalingFlow (*npj Syst Biol Appl* 2024) · DIPx (*eLife* 2025) ·
PathDNN (*JCIM* 2020) · DrugCell (Kuenzi et al., *Cancer Cell* 2020).

**Attention đa phương thức** — SynergyX (*BIB* 2024;25(2):bbae015) · MVCASyn (*JCST* 2025) ·
MARSY (*Bioinformatics* 2023;39(4):btad177).

**Knowledge graph và hypergraph** — KGANSynergy (*BIB* 2023) · HANSynergy (*JCIM* 2024) ·
SynergyGraph (*Sci Rep* 2025) · MGAE-DC (*PLOS CB* 2023) · HypergraphSynergy (*Bioinformatics* 2022) ·
HGTSynergy (*BMC Bioinform* 2026) · SynDRep (*Bioinform Adv* 2025) · SDCInterpreter (*JCIM* 2026) ·
CASynergy (*PLOS CB* 2025) · SynCell (arXiv 2025–26) · KG-Synergy (*BIB* 2023).

**Explainer chuyên biệt, chưa ai mang sang bài toán hiệp đồng** — PaGE-Link (*WWW* 2023) ·
Power-Link (*KDD* 2024) · xPath (*AAAI* 2023) · CF-GNNExplainer (*AISTATS* 2022) ·
GCFExplainer (*ACM TIST* 2024) · GSAT (*ICML* 2022) · CETExplainer (arXiv:2408.17129) ·
DRPreter (*Brief Bioinform* 2022).

**Nền dược lý mạng và mốc lịch sử** — Cheng F., Kovács I.A., Barabási A.-L. (*Nat Commun* 2019,
lý thuyết Complementary Exposure và s_AB) · Menden M.P. et al. (AstraZeneca–Sanger DREAM Challenge,
*Nat Commun* 2019) · Janizek J.D. et al. (TreeCombo, 2018; và *Nat Biomed Eng* 2023 dùng Shapley
interaction index giữa thuốc và gen) · CancerGPT (*npj Digit Med* 2024).

**Lưu ý về nhiễu nhãn, cần cho phần thảo luận** — một preprint phân tích 391.652 ma trận DrugComb
báo Loewe chỉ tương quan r = 0,28 với ZIP và r = 0,33 với Bliss, và 21–34% ma trận bị một phương pháp
gọi là hiệp đồng trong khi phương pháp khác gọi là đối kháng [KT, chưa đọc toàn văn]. Con số này khớp
với kết quả độ nhạy của tôi ở §3.5.

---

# Phần 2. Các bước xây dựng project

Toàn bộ chạy lại bằng `bash run_all.sh 4`. Mỗi chặng tự bỏ qua run đã xong nên ngắt giữa đường
không mất gì. Thứ tự: dò siêu tham số → chặn G1 → lưới chính → giải thích → case study → bảng báo cáo.

## 2.1. Dữ liệu

**Nguồn:** O'Neil (Merck 2016) lấy qua DrugComb v1.4 (`summary_table_v1.4.csv`, Zenodo 11102665),
giới hạn `block_id ≤ 92208`. Đây đúng là bộ mà DTSyn, DeepDDS, AttenSyn và MD-Syn dùng, nên số liệu
so được. Không mở rộng lên DrugComb đầy đủ — việc đó để ở hướng phát triển.

**Đường đi của số lượng mẫu**, ghi trong `data/processed/provenance_*.json`:

| Bước | Còn lại |
|---|---|
| Khối tổ hợp trong O'Neil | 92.208 khối, đều có `css` |
| Ánh xạ dòng tế bào sang DepMap | 39 → **37** dòng |
| Gộp bản lặp theo trung vị, khử trùng lặp | **21.571** bộ ba · 38 thuốc · 37 dòng · trung vị 4 bản lặp/bộ ba · trung vị IQR của Loewe 2,46 |
| Loại bộ ba không có SMILES công khai | **18.870** bộ ba · **36** thuốc · 510 cặp · 37 dòng · 7 loại mô (mất 12,5%) |

Hai thuốc bị loại là **MK-4541** và **MRK-003** (mã nội bộ Merck, không có cấu trúc công khai).
Hai thuốc **carboplatin** và **oxaliplatin** phải nhập SMILES tay từ DrugBank vì ChEMBL không có cấu
trúc phức platin; 34 thuốc còn lại tra bằng `pref_name__iexact`. **Không dùng khớp mờ**: đã thử
`search.json` của ChEMBL, truy vấn "gemcitabine" trả về "GEMCITABINE ELAIDATE" — một chất khác.
Không có hai tên nào trỏ về cùng InChIKey nên không phải gộp thuốc.

**Ba thiết lập nhãn** trên cùng bộ dữ liệu đó — đây là thiết kế trung tâm của RQ1:

| Thiết lập | Quy tắc | Dữ liệu dùng |
|---|---|---|
| `bin_gap_*` (giao thức DTSyn) | > 10 dương · < 0 âm · **bỏ vùng 0–10** | 12.223 bộ ba (**bỏ 35,2%**) |
| `bin_all_*` | > 10 dương · còn lại âm | 100% |
| `ord3_*` ← **chính** | > 10 syn · −10…10 add · < −10 ant | 100% — **4.391 ant / 13.207 add / 1.272 syn** |

Lớp syn chỉ 6,7%, nên accuracy vô nghĩa; metric chính là **QWK**, phụ là macro-F1, MAE, balanced
accuracy và riêng **tỷ lệ nhầm cực** (syn ↔ ant).

Bảng độ nhạy phủ bốn điểm synergy × ba ngưỡng. Tỷ lệ dữ liệu bị giao thức DTSyn xóa thay đổi rất
mạnh theo điểm: Loewe 35,2% · Bliss 49,7% · ZIP 52,7% · HSA 59,7%. Riêng con số này đã là một
luận điểm cho RQ1.

**Năm kiểu chia dữ liệu** (`src/data/build.py`): random 5 fold · leave_combo 5 · leave_drug 5
(36 thuốc chia 5 cụm cỡ 8/8/8/8/4) · leave_cell 5 · leave_tumor 7 (một fold mỗi loại mô).
Tập validation **luôn chia theo cùng đơn vị với split ngoài** — leave_drug thì validation cũng theo
thuốc. Có test đơn vị cho việc này.

## 2.2. Tiền xử lý

**Phía thuốc** (`src/data/smiles.py`, `featurize.py`):
1. Chuẩn hóa RDKit: tách muối, trung hòa điện tích, chuẩn hóa tautomer, sinh InChIKey.
2. SMILES → đồ thị phân tử vô hướng; đặc trưng nguyên tử **78 chiều theo DeepChem, hậu xử lý kiểu
   DeepDDS** — đúng như DTSyn để so sánh công bằng. Số nguyên tử 8–69, trung vị 29.
3. Chia mảnh **BRICS**, lưu ánh xạ nguyên tử → mảnh (1–13 mảnh, trung vị 4,5). Đây là đơn vị giải
   thích ở phía hóa học.
4. Fingerprint Morgan (trung vị 54,5 bit bật) và RDKit descriptor, cho nhánh fingerprint và cho
   DeepSynergy, XGBoost.

**Phía dòng tế bào** (`src/data/cell.py`):
1. Lấy biểu hiện của 978 gen landmark L1000, giao với DepMap → còn **944 gen**.
2. **Z-score theo từng gen, fit chỉ trên các dòng trong tập train của từng fold.** Chỗ dễ rò thông
   tin nhất, có test đơn vị.
3. node2vec 128 chiều trên **STRING score ≥ 700** (16.201 nút, 236.930 cạnh) → 911/944 gen có vector.
   Có sẵn bản **STRING xáo trộn giữ bậc** để làm đối chứng.
4. Gom gen theo pathway KEGG — **chỉ dùng để chấm điểm XAI, không đưa vào mô hình**, tránh vòng lặp.

## 2.3. Mô hình của tôi: SynGT

**SynGT** (Synergy Graph-Transformer), khoảng 4,16 triệu tham số, code ở `src/model/syngt.py`.
Luồng một bộ ba (thuốc A, thuốc B, dòng tế bào):

1. Hai SMILES → đồ thị → **GIN 2 lớp dùng chung trọng số** (siamese), d = 256 → token cho từng nguyên tử.
2. 944 gen → mỗi gen một token = `[embedding node2vec ; giá trị biểu hiện]` qua một lớp tuyến tính.
3. **Transformer mịn** (2 lớp, 4 đầu): chuỗi `[CLS | nguyên tử A | nguyên tử B | token gen]`.
   Ma trận attention nguyên tử ↔ gen ở đây chính là thứ DTSyn, MD-Syn và AttenSyn trình bày như
   lời giải thích, nên nó được giữ lại để kiểm định ở RQ4.
4. **Transformer thô** (2 lớp): chuỗi `[CLS | thuốc A đã pool | thuốc B đã pool | vector tế bào]`.
5. **Readout "skip"**: nối `[CLS_mịn ; CLS_thô ; pA+pB ; |pA−pB| ; vector tế bào]`, cộng thêm
   **nhánh MLP fingerprint Morgan** vào từng vector thuốc.
6. **Đầu CORN**: 2 logit có điều kiện → ba lớp có thứ tự ant < add < syn, bảo đảm theo cấu trúc
   (không thể ra `P(y>add) > P(y>ant)`).

Hai tính chất có test đơn vị: **không có embedding phân biệt A/B** nên mô hình đối xứng tuyệt đối
`f(A,B,c) = f(B,A,c)`; và `z_syn − z_add` **đúng bằng** logit có điều kiện thứ hai, kể cả khi logit
cực trị — đây là điều kiện để target XAI `contrast` có nghĩa chính xác.

**Có trùng bài nào không?** Không giống hệt bài nào, nhưng **không phải kiến trúc mới** — đây là
sự ghép các ý đã công bố, và phải viết đúng như vậy trong bài:

| Thành phần | Lấy từ |
|---|---|
| Hai transformer mịn/thô, token nguyên tử + gen, node2vec trên PPI | **DTSyn** (khung chính) |
| Đặc trưng nguyên tử 78 chiều, readout `[pA+pB ; \|pA−pB\| ; cell]` | **DeepDDS** |
| Nhánh fingerprint Morgan | **DeepSynergy** |
| GIN thay GCN | Khác DTSyn; GCN giữ làm ablation |
| Đầu CORN ba lớp có thứ tự + metric QWK | **Mới trong lĩnh vực hiệp đồng thuốc** (theo khảo sát lúc lập plan, cần kiểm lại trước khi nộp) |
| Đối xứng A↔B theo cấu trúc | DTSyn chỉ kiểm bằng thực nghiệm; đây là chi tiết nhỏ |

## 2.4. Mô hình để so sánh

Tất cả dùng **chung một trainer, chung cỡ đầu ra, chung ngân sách** 120 epoch / patience 20, nên
bảng so sánh là cùng điều kiện (`src/repro/baselines.py`, `src/repro/xgb.py`).

| Mô hình | Thuộc bài nào | Vai trò |
|---|---|---|
| **DeepSynergy** | Preuer et al. 2018 | Fingerprint Morgan r=3 + descriptor + biểu hiện → MLP 2048-1024-256. Baseline mạnh nhất |
| **DeepDDS** | Wang et al. 2022 | GCN 2 lớp trên đồ thị phân tử + MLP trên biểu hiện → nối → MLP. Mô hình GNN gần SynGT nhất |
| **XGBoost** | Thực hành phổ biến, planner 5.3 | Fingerprint Morgan + biểu hiện → gradient boosting. *(đang chạy, 1/89 run)* |
| **one-hot** | Baseline danh tính, theo SynVerse và One-hot news | one-hot thuốc A + thuốc B + dòng tế bào → MLP. **Bắt buộc có trong mọi bảng** |
| **chỉ thuốc** / **chỉ tế bào** | Đối chứng tầm thường | Trả lời câu "mô hình có thật học tương tác, hay chỉ học đặc điểm dòng tế bào" |
| **majority** | Đối chứng tầm thường | Luôn đoán add; chứng minh accuracy vô nghĩa ở đây |

**DTSyn chưa được tái lập thành một mô hình riêng** — SynGT dùng khung của nó, nhưng trong bảng
không có cột "DTSyn". Đây là một thiếu sót phải ghi rõ ở phần giới hạn.

**Ablation kiến trúc** (10 biến thể): bỏ transformer mịn · bỏ transformer thô · bỏ cả hai ·
GCN thay GIN · bỏ node2vec · **node2vec trên STRING xáo giữ bậc** · readout CLS kiểu DTSyn gốc ·
chỉ đồ thị (bỏ fingerprint) · **hoán vị SMILES** (giữ danh tính, hoán vị cả fingerprint để không rò
thông tin hóa học) · ba loss (CORN / CE thường / CE + chi phí).

## 2.5. Huấn luyện

| Khoản | Giá trị |
|---|---|
| Loss | CORN loss + trọng số lớp nghịch tần suất |
| Optimizer | AdamW, weight decay 1e-4, warmup 5% rồi cosine, gradient clipping 1,0, bf16 autocast |
| Siêu tham số | Từ đợt dò 16 cấu hình ngẫu nhiên: d = 256, GIN 2 lớp, transformer 2 + 2 lớp, 4 đầu, FFN 256, dropout 0,15, lr 3,29e-4, batch 256 |
| Dừng sớm | Theo **QWK trên validation** (AUPRC cho thiết lập nhị phân), patience 20. Không theo loss, không theo accuracy |
| Chọn mô hình | Theo val, không bao giờ theo test |
| Số lần chạy | 3 seed cho bảng chính và G1, 2 seed cho ablation và độ nhạy |
| Ghi lại | Mọi siêu tham số, phiên bản dữ liệu, số tham số vào `runs/<name>/config.json` |

**Chặn cứng G1:** trước khi xây gì mới, phải tái lập được số công bố của DeepDDS và DeepSynergy ở
thiết lập nhị phân gốc. Lý do: lần chạy trước của repo, DeepSynergy chỉ đạt QWK 0,222 — thấp bất
thường cho mô hình nền tảng của lĩnh vực, gần như chắc là lỗi pipeline. Kết quả chặn G1 ở §3.2.

**Quy mô đã chạy:** 656 run huấn luyện (613 lưới chính + 16 dò siêu tham số + 27 chẩn đoán kiến trúc)
và 39 run giải thích, 0 lỗi. Đang chạy thêm 136 run cho DeepSynergy ở split khó và 89 run XGBoost.
**16 test đơn vị đều qua**, gồm: đối xứng A↔B, không rò thông tin giữa các split, z-score chỉ fit
trên train, và `contrast` = logit thứ hai.

## 2.6. XAI — dùng gì, giải thích cái gì, làm sao giải thích được

**Cơ chế chung:** mọi đơn vị giải thích được cài thành một **mặt nạ mềm bên trong forward pass**
(`src/xai/masks.py`). Nhờ vậy cùng một đoạn code cho cả gradient (Integrated Gradients) và cả phép
xóa (Fidelity) — hai thứ đo được trên cùng một thang.

**Bốn đơn vị giải thích:**

| Mặt nạ | Đơn vị | Vì sao chọn |
|---|---|---|
| `mu_gene` (944) | Gen landmark | Đơn vị mà TranSynergy và DTSyn dùng. Baseline của IG là **trung bình biểu hiện của tập train**, không phải vector 0 |
| `mu_frag` | Mảnh BRICS | Xóa **mảnh nguyên vẹn** thay vì nguyên tử rời: xóa nguyên tử lẻ tạo phân tử không tồn tại nên Fid+ bị thổi phồng |
| `mu_atom` | Nguyên tử | Để đối chiếu với attention cấp nguyên tử |
| `mu_fp` (2) | Nhánh fingerprint của A và B | Mặt nạ mảnh không chạm tới nhánh này. Cho `mu_fp` mặt nạ riêng thì "tỷ lệ quyết định đến từ fingerprint" trở thành một con số có định nghĩa chính xác |

**Ba mục tiêu attribution — đây là đóng góp N2:**

| Mục tiêu | Công thức | Ai đang làm |
|---|---|---|
| `logit` | `z_syn` | Toàn bộ literature hiện nay |
| `contrast` | `z_syn − z_add` | **Đề xuất của luận văn.** Hiệp đồng là phần dôi ra so với cộng tính, nên đây mới là "điều gì đẩy bộ ba ra khỏi trạng thái cộng tính". Với đầu CORN, hiệu này **bằng đúng** logit có điều kiện thứ hai nên phép trừ miễn phí |
| `ant` | `z_ant − z_add` | Chưa ai làm, vì thiết lập nhị phân gộp lớp đối kháng vào lớp âm. Dùng cho RQ6 |

**Bộ đo, mỗi chỉ số một null** (`src/eval/xai_metrics.py`):

- **Fid+**: xóa top-k (10% và 25% gen; 1 và 2 mảnh) rồi đo độ đổi của mục tiêu, so với **10 phép xóa
  ngẫu nhiên khớp số lượng**. *(planner ghi 20 lần, code đang là 10 — phải sửa một trong hai chỗ.)*
- **Fid−**: chỉ giữ top-k. Báo kèm cảnh báo vì đầu vào lạc phân phối nặng.
- **Completeness gap của IG**: `sum(attr) − (f(1) − f(0))`. Báo ra, không che. Đường tích phân dùng
  `mu = alpha³` với 32 bước — đường thẳng đều bị lệch nặng vì chuẩn hóa bậc của GCN làm đầu ra gần
  như chỉ chuyển động khi alpha < 0,05.
- **Faithfulness Violation Test** (Liu et al., ICML 2022): Spearman giữa attribution và hiệu ứng xóa
  từng đơn vị, trên 10 đơn vị xếp cao nhất.
- **Attention có phải lời giải thích không**: Jaccard@50 giữa attention (CLS → gen) và IG.
- **Độ ổn định**: Jaccard@50 qua **3 seed**, qua **5 fold**, và qua **4 điểm synergy × 3 ngưỡng**
  (cùng kiến trúc, cùng split, cùng fold, cùng seed, chỉ đổi quy ước nhãn), mỗi cái một null hoán vị.
- **Plausibility**: làm giàu top-50 gen với pathway KEGG và với đích của chính hai thuốc
  (hypergeometric), null là tập gen ngẫu nhiên **khớp phân bố mức biểu hiện**.
- **Tương tác cặp mảnh**: `phi(i,j) = f(all) − f(−i) − f(−j) + f(−i,−j)`, một sai phân hữu hạn
  **chính xác** chứ không xấp xỉ (phân tử ở đây chỉ 1–13 mảnh nên cả ma trận tốn ~200 forward pass).
  Cùng dạng với Shapley interaction index của Grabisch & Roubens.
- **Đồ thị so với fingerprint**: IG chung trên `[mảnh, fp_A, fp_B]` trên một đường tích phân, cộng
  thêm phép xóa trực tiếp từng nhánh.

**Nguyên tắc tách faithfulness khỏi plausibility.** Faithfulness hỏi lời giải thích có phản ánh đúng
cái mô hình dùng không; plausibility hỏi nó có khớp sinh học không. Gộp hai thứ là lỗi phần lớn
literature mắc phải. Trung thực nhưng không hợp lý sinh học nghĩa là **mô hình** học sai; hợp lý
nhưng không trung thực nghĩa là **explainer** sai.

**Case study khai báo trước** (`src/eval/case_study.py`): bốn cặp thuốc, các dòng tế bào và pathway
kỳ vọng được ghi cứng trong file **trước khi chạy giải thích** và không sửa về sau. Cặp đầu là ví dụ
của chính DTSyn (ETOPOSIDE + MK-2206 trên CAOV3 và NCIH23) để so trực tiếp với 5 gen họ công bố.
Mỗi cặp được giải thích bằng 3 seed của fold mà tập test chứa cặp đó, nên mô hình bị chất vấn chưa
từng thấy tổ hợp đó khi huấn luyện. Planner yêu cầu **bắt buộc báo cáo ít nhất một ca giải thích sai**.

**Chỉ giải thích lớp syn và lớp ant.** "Gen nào khiến cặp thuốc này *không* tương tác" là câu hỏi
thoái hóa; nêu rõ trong chương phương pháp thay vì để hội đồng phát hiện.

---

# Phần 3. Kết quả hiện tại

Mọi con số là trung bình trên fold × seed, trong ngoặc vuông là khoảng tin cậy bootstrap 95%.
Bảng gốc: `reports/tables/*.csv`.

## 3.1. Một đoạn tóm tắt

SynGT đạt **QWK 0,589** ở leave-combination-out, **đứng thứ hai** sau DeepSynergy (0,605), hơn rõ
DeepDDS (0,536), ngang one-hot (0,573). Chặn G1 **đạt**: cả hai baseline công bố đều bằng hoặc vượt
số gốc của chính chúng, nên pipeline đáng tin. Phần XAI **trung thực với mô hình** (Fid+ thắng null
ở 97–99,8% bộ ba, completeness lệch ≤ 1,4%) và **ổn định giữa các seed** (Jaccard top-50 0,19–0,28
so với null 0,026–0,033; cosine 0,47–0,59 so với null quanh 0), nhưng **không chứng minh được ý
nghĩa sinh học**. Bản trước của file này viết độ ổn định là 0,032–0,044, tức ngang ngẫu nhiên; đó là
lỗi đo, đã sửa và chạy lại, xem §3.8. Hai transformer — thành phần lẽ ra là cốt lõi của khung DTSyn —
**không đóng góp gì** vào độ chính xác.

Nói thẳng: **đây không phải một bài báo "mô hình mới tốt nhất".** Nhưng nó là một bài báo phản biện
giao thức có số liệu đầy đủ, và loại bài đó có chỗ đứng.

## 3.2. Chặn G1 — tái lập số công bố (random 5-fold, nhị phân bỏ vùng 0–10, 15 run)

| Mô hình | ROC-AUC | AUPRC | Số công bố |
|---|---|---|---|
| DeepSynergy | **0,958 ± 0,003** | 0,805 | AUC 0,90 |
| one-hot | 0,957 ± 0,004 | 0,804 | — |
| SynGT | 0,946 ± 0,004 | 0,732 | (DTSyn: 0,89) |
| DeepDDS | 0,945 ± 0,004 | 0,754 | ~0,93 |

**Đạt.** Hai cảnh báo phải viết vào bài:
1. **one-hot đạt 0,957** — không dùng SMILES, không dùng biểu hiện gen, vẫn ngang DeepSynergy. Trên
   random split, nhớ danh tính (cặp thuốc, dòng tế bào) gần như là đủ, nên **random split không phân
   biệt được các mô hình**. Kết quả này tái hiện độc lập phát hiện của SynVerse và One-hot news.
2. **AUPRC không so trực tiếp được giữa các bài** vì tỷ lệ lớp dương ở đây chỉ 10,4%. Chỉ AUROC so được.

## 3.3. Bảng chính — ba lớp, QWK

| Mô hình | leave_combo | leave_drug | leave_cell | leave_tumor | random |
|---|---|---|---|---|---|
| DeepSynergy | **0,605** [0,595–0,616] | *(đang chạy)* | *(đang chạy)* | *(đang chạy)* | — |
| **SynGT** | **0,589** [0,580–0,601] | **0,224** [0,173–0,280] | 0,478 | 0,459 | 0,628 |
| one-hot | 0,573 [0,564–0,581] | 0,190 | 0,478 | 0,460 | — |
| DeepDDS | 0,536 [0,529–0,544] | 0,191 | **0,483** | 0,459 | 0,606 |
| XGBoost | 0,534 *(1 run)* | — | — | — | — |
| chỉ thuốc | 0,409 | — | — | — | — |
| chỉ tế bào | 0,098 | — | — | — | — |
| majority | 0,000 | — | — | — | — |

Cách đọc trung thực:
- SynGT **hơn DeepDDS có ý nghĩa thống kê** (khoảng tin cậy rời nhau), cạnh tranh được với baseline
  mạnh nhất, nhưng **không đứng đầu**.
- Ở **leave_cell và leave_tumor, ba mô hình bằng nhau trong sai số** (0,478 / 0,478 / 0,483 và
  0,459 / 0,460 / 0,459). Ở hai split này one-hot ngang SynGT, tức thông tin thuốc và gen không giúp gì.
- Ở **leave_drug**, mọi mô hình sụp xuống 0,19–0,22 với khoảng tin cậy rất rộng. Thuốc mới là bài
  toán chưa giải được, đúng như Abbasi & Rousu đã chỉ ra (p = 0,026).
- **Nhầm cực của SynGT chỉ 0,3%** — thấp nhất bảng cùng DeepSynergy (0,27%), so với DeepDDS 0,76%
  và chỉ tế bào 8,4%. Đây là một điểm mạnh cụ thể và nên đưa lên.

## 3.4. RQ1 — cái giá của việc bỏ vùng trung tính

Cùng mô hình, cùng split, chỉ đổi cách gán nhãn.

| Mô hình | split | AUROC bỏ vùng → toàn bộ | AUPRC bỏ vùng → toàn bộ |
|---|---|---|---|
| DeepDDS | leave_combo | 0,907 → 0,847 (**−0,060**) | 0,625 → 0,344 (−0,281) |
| DeepSynergy | leave_combo | 0,922 → 0,866 (−0,055) | 0,679 → 0,405 (−0,273) |
| SynGT | leave_combo | 0,903 → 0,848 (−0,055) | 0,602 → 0,357 (−0,245) |
| one-hot | leave_combo | 0,923 → 0,869 (−0,054) | 0,693 → 0,421 (−0,272) |
| SynGT | random | 0,946 → 0,889 (−0,058) | 0,732 → 0,441 (−0,291) |
| DeepDDS | random | 0,945 → 0,889 (−0,056) | 0,754 → 0,452 (−0,302) |

**Kết luận RQ1:** khoảng **0,055 AUROC** của giao thức DTSyn đến từ việc loại chính những bộ ba khó
nhất. Hiệu ứng nhất quán ở mọi mô hình và mọi split, nên đây là thuộc tính của **giao thức đánh giá**,
không phải của một mô hình cụ thể. Đây là kết quả mạnh nhất của project.

**Một chỗ phải tự phản biện trước khi reviewer làm việc đó.** Mức tụt AUPRC 0,25 **không** quy hết
cho độ khó được: bỏ vùng trung tính cũng đổi tỷ lệ lớp dương từ 10,4% xuống 6,7%, mà AUPRC phụ thuộc
tỷ lệ này. Tính theo **lift trên tỷ lệ nền** thì mức tụt nhỏ hơn nhiều:

| Mô hình | lift AUPRC: bỏ vùng → toàn bộ |
|---|---|
| DeepDDS (leave_combo) | 5,96 → 5,10 (**−14,4%**) |
| SynGT (leave_combo) | 5,75 → 5,30 (−7,8%) |
| DeepSynergy (leave_combo) | 6,48 → 6,01 (−7,1%) |
| one-hot (leave_combo) | 6,62 → 6,25 (−5,6%) |

Nên trong bài phải báo **cả hai cách**: AUROC (−0,055, không phụ thuộc tỷ lệ lớp, đây là luận điểm
chính) và AUPRC kèm lift (−6…−14%, đây là cách đọc công bằng). Nếu chỉ báo "AUPRC tụt 0,25" thì
luận điểm sẽ bị bác ngay ở vòng phản biện đầu.

## 3.5. RQ2 và phân tích độ nhạy

**Loss ordinal** (leave_combo):

| Loss | QWK | MAE | Macro-F1 | Nhầm cực |
|---|---|---|---|---|
| **CORN** (15 run) | **0,589** | **0,219** | **0,660** | 0,3% |
| cross-entropy thường (6) | 0,580 | 0,227 | 0,655 | 0,4% |
| CE + chi phí kỳ vọng (6) | 0,580 | 0,223 | 0,658 | 0,3% |

CORN tốt nhất ở mọi chỉ số nhưng chênh chỉ khoảng 0,01 QWK. Phải viết là "lợi ích có nhưng khiêm
tốn". Giá trị thật của CORN không nằm ở con số mà ở hai chỗ: thứ tự lớp bảo đảm theo cấu trúc, và
nó cho target `contrast` một định nghĩa chính xác.

**Độ nhạy theo điểm synergy và ngưỡng:**

| Thiết lập | QWK |
|---|---|
| Loewe ±5 | 0,598 |
| **Loewe ±10 (chính)** | **0,589** |
| Loewe ±20 | 0,586 |
| HSA ±10 | 0,443 |
| ZIP ±10 | 0,417 |
| Bliss ±10 | 0,390 |

Ngưỡng gần như không ảnh hưởng, nhưng **đổi điểm synergy thì mất tới 0,20 QWK**. Khớp với con số
r = 0,28 giữa Loewe và ZIP trong y văn. Đây là lý do phải báo cáo độ nhạy, và là một luận điểm phụ
cho RQ1: cùng một dữ liệu thực nghiệm, đổi quy ước toán học thì bài toán khó hẳn lên.

## 3.6. Ablation — phần kết quả khó chịu nhất

| Biến thể | QWK |
|---|---|
| bỏ cả hai transformer | **0,591** |
| bỏ transformer mịn | 0,591 |
| **SynGT đầy đủ** | 0,589 |
| GCN thay GIN | 0,589 |
| bỏ embedding node2vec | 0,586 |
| node2vec trên STRING **xáo trộn** | 0,585 |
| bỏ transformer thô | 0,584 |
| SMILES hoán vị (chỉ giữ danh tính) | 0,574 |
| chỉ đồ thị, bỏ fingerprint | 0,565 |
| readout CLS gốc kiểu DTSyn | **0,483** |

Ba điều rút ra, cả ba đều ngược với bài gốc:

1. **Hai transformer không giúp gì** (0,591 so với 0,589). DTSyn báo ROC-AUC tụt 0,89 → 0,69 khi bỏ
   cả hai; **tôi không tái lập được điều đó**. Trong dữ liệu của tôi, thứ quyết định là **cách readout**
   (CLS-only tụt xuống 0,483). Vì vậy bài **không thể** định vị theo hướng "kiến trúc transformer".
2. **PPI không mang thông tin**: STRING thật và STRING xáo cho kết quả như nhau (0,586 / 0,585).
   Khớp với lần chạy trước của repo, và khớp với kết quả rewiring của SynVerse.
3. **Cấu trúc hóa học đóng góp ít**: hoán vị SMILES chỉ mất 0,015. Fingerprint giúp 0,024 so với
   chỉ dùng đồ thị — tức nhánh "cổ điển" còn hữu ích hơn nhánh GNN.

Để công bằng, nhắc lại hành trình kiến trúc (chọn theo **val** QWK, thứ tự val trùng thứ tự test):
bản đầu chỉ đọc qua token CLS như DTSyn bị **underfit** (val 0,486 / test 0,460, thua cả one-hot;
ở epoch 40 train loss còn 0,28 trong khi DeepSynergy đã xuống 0,06). Thêm readout skip → 0,552;
thêm head rộng → 0,581; thêm nhánh fingerprint → **0,605 val / 0,587 test**.

## 3.7. XAI — làm được gì

**Trung thực với mô hình: tốt.**
- **Fid+** thắng null ở **97–99,8%** bộ ba, cho cả gen lẫn mảnh BRICS và cả ba target. Ví dụ: xóa 25%
  gen theo `contrast` trên bộ ba hiệp đồng làm điểm giảm 5,34, xóa ngẫu nhiên cùng số lượng chỉ giảm 0,32.
- **Completeness** của IG lệch ≤ 1,4% với gen, ≤ 0,6% với mảnh.
- **FVT**: Spearman 0,32–0,47, tỷ lệ vi phạm 12–27%.

**RQ3 — ba target cho ba lời giải thích khác nhau** (tương quan thứ hạng):

| | contrast ↔ logit | contrast ↔ ant | logit ↔ ant |
|---|---|---|---|
| bộ ba hiệp đồng | 0,887 | 0,095 | 0,091 |
| bộ ba đối kháng | 0,727 | 0,084 | 0,053 |

Lời giải thích cho **đối kháng gần như trực giao** với lời giải thích cho hiệp đồng — một câu hỏi mà
mô hình nhị phân không đặt ra được. Nhưng phải trung thực: `contrast` và `logit` **trùng nhau nhiều**
(0,89 trên bộ ba syn), nên đóng góp N2 ở dạng mạnh ("phép trừ cho lời giải thích khác") **không
đứng được**; dạng đứng được là "lớp ant cho lời giải thích riêng", tức trục RQ6.

**Attention có phải lời giải thích không — không.** Jaccard@50 giữa attention (CLS → gen) và IG chỉ
**0,04–0,05**. Những gen mà DTSyn, MD-Syn và AttenSyn trình bày qua attention gần như không trùng với
những gen thực sự đổi quyết định khi bị xóa.

**Đồ thị hay fingerprint quyết định?** Theo IG chung: fingerprint mang **51–55%**. Theo phép xóa trực
tiếp: fingerprint "thắng" ở **65–76%** bộ ba. Tương tác cặp mảnh BRICS chỉ bằng **2–4%** hiệu ứng bậc
một — mô hình gần như cộng tính theo mảnh. Hệ quả: giải thích cấp mảnh chỉ nói được một nửa câu chuyện.

## 3.8. XAI — ổn định với mô hình, không khớp sinh học

**Ổn định giữa các seed.** Jaccard@50 của *cùng* bộ ba qua 3 seed: **0,19–0,28**, null 0,026–0,033;
cosine giữa hai bản đồ attribution 0,47–0,59, null từ −0,01 đến 0,06. Cả sáu tổ hợp lớp × target đều
vượt null.

Bản trước của file này báo 0,032–0,044 với null 0,027–0,040 và kết luận "ngang ngẫu nhiên". Con số
đó sai vì lỗi đo, không vì mô hình: hàm chọn bộ ba trong `src/xai/run_explain.py` dùng
`hash(split) % 1000` làm seed, và `hash()` trên chuỗi được Python muối lại mỗi tiến trình khi
`PYTHONHASHSEED` không được đặt. Mỗi lần gọi `run_explain` là một tiến trình riêng, nên ba seed của
cùng một fold giải thích **những bộ ba khác nhau**: chỉ 0 đến 2 trong 40 bộ ba là dùng chung. Bảng
"ổn định" vì thế đang so lời giải thích của các tam nguyên không liên quan, và nó bắt buộc phải ra
bằng null vì `stability_null` được định nghĩa đúng là "ghép các bộ ba khác nhau". Sau khi cố định
offset theo split và chạy lại toàn bộ 54 run giải thích, mỗi fold dùng chung 40/40 bộ ba.

**Ổn định qua quy ước nhãn.** Cùng split, fold, seed, chỉ đổi điểm synergy hoặc ngưỡng: cả 30 dòng
(4 điểm × 2 ngưỡng, hai lớp) đều vượt null, Jaccard 0,077–0,283 so với null 0,026–0,034, kể cả lớp
đối kháng. Trước đây mỗi ô chỉ dựa trên 1 đến 7 bộ ba dùng chung, giờ là 40.

**Qua fold** (cùng seed, khác dữ liệu train), so trên bản đồ attribution **trung bình**:
syn/`contrast` 0,288, syn/`logit` 0,241, phía ant 0,067–0,073. Bảng này đo bản đồ trung bình nên
không so trực tiếp được với hai bảng trên.

Giả thuyết cũ cho sự "không ổn định" (37 dòng tế bào, 944 gen, seed nào cũng chọn được một tập gen
đủ nhận ra dòng tế bào) không còn phải giải thích gì nữa, vì hiện tượng không tồn tại.

**Không chứng minh được ý nghĩa sinh học.**
- Enrichment KEGG trong top-50 gen: 0,19–0,26% bộ ba, null 0%. Về cơ bản là không có.
- Case study khai báo trước: SynGT **dự đoán đúng 5/8** bộ ba trên cả 3 seed, nhưng **0/8 vượt null**
  về pathway khai báo trước, và **0/8** có gen đích của chính hai thuốc trong top-50.
- Ví dụ của DTSyn (ETOPOSIDE + MK-2206): 5 gen họ công bố (SNAP25, GALE, PRKCD, PIK3R3, DDIT4) xếp
  hạng **163–917 trên 944** trong giải thích của tôi — **không tái lập**. Thêm nữa, dưới Loewe ±10
  thì CAOV3 có nhãn **additive**, không phải hiệp đồng như DTSyn mô tả.
- Có ca sai để báo cáo như planner yêu cầu: NCIH23 (nhãn ant, đoán add cả 3 seed) và AZD1775 + MK-8776
  (hai dòng, seed 1 lệch khỏi hai seed kia).

Kết luận gọn: **XAI cho ra lời giải thích đúng với mô hình và tái lập được qua seed cũng như qua quy
ước nhãn, nhưng chưa chứng minh đúng với sinh học.** Nghịch lý nằm ở đó: một lời giải thích ổn định
mà vẫn không chỉ vào pathway nào thì không quy được cho nhiễu.

## 3.9. Lỗi đã phát hiện và sửa

Ghi lại vì nó là bằng chứng về độ cẩn thận của pipeline, và vì một trong số đó đã từng tạo ra kết
luận sai.

| Lỗi | Hậu quả | Cách sửa |
|---|---|---|
| readout chỉ qua CLS | SynGT underfit, QWK 0,460 | readout skip, chọn theo val |
| `log(probs)` bị kẹp ở 1e-7 | gradient bằng 0 với bộ ba đối kháng chắc chắn; `contrast` sai (−4,1 thay vì −9) | công thức log-sigmoid; **chạy lại toàn bộ 39 run giải thích**. Kết luận cũ "target logit thua null" là sản phẩm của lỗi, đã loại |
| loss chi phí thuần | luôn đoán additive (QWK 0) | đổi sang CE + chi phí |
| hoán vị SMILES không hoán vị fingerprint | đối chứng bị rò thông tin hóa học | hoán vị cả hai |
| run dò HP và ablation lọt vào bảng chính | QWK của SynGT sai lệch | lọc trong `report.py` |
| ngân sách 80/12 cho baseline, 120/20 cho SynGT | so sánh không công bằng | mọi mô hình 120/20 |
| `torch.sparse.mm` với COO trên GPU | ~260 ms/batch | chuyển CSR, nhanh 5–14× và vẫn khả vi theo giá trị cạnh |

## 3.10. Đánh giá: project và bài báo có khả quan không

**Khả quan ở mức "một bài báo chắc chắn viết được, không phải một bài gây tiếng vang".**

Những gì đã nắm chắc trong tay:
- Pipeline **đã chứng minh tái lập được số công bố** (chặn G1 đạt). Đây là thứ phần lớn bài trong
  lĩnh vực không chứng minh, và là tiền đề để mọi bảng khác có giá trị.
- **656 run, 0 lỗi, 16 test đơn vị, cùng ngân sách cho mọi mô hình, mọi chỉ số có null và CI
  bootstrap.** Về mặt độ chặt thực nghiệm, cao hơn các bài đang được trích dẫn trong lĩnh vực.
- **RQ1 là một kết quả thật**, nhất quán trên 4 mô hình × 2 split.
- Ba kết quả âm có kiểm soát: transformer vô dụng, PPI ngang mạng xáo, attention không trùng IG.
  Kết quả âm có đối chứng đầy đủ vẫn là kết quả.

Những gì **không** nên hứa trong bài:
- Không viết SOTA. SynGT đứng thứ hai và ngang one-hot.
- Không viết "kiến trúc mới". Ablation của chính tôi bác điều đó.
- Không viết "phát hiện cơ chế sinh học". 0/8 case study vượt null.
- Không viết N2 ở dạng mạnh. `contrast` ↔ `logit` tương quan 0,89 trên bộ ba syn.

**Ba trục đứng được trên số liệu, xếp theo độ mạnh:**
1. **Giao thức bỏ vùng trung tính thổi phồng kết quả** (−0,055 AUROC ở mọi mô hình), kèm đề xuất
   thay bằng bài toán ba lớp có thứ tự với QWK và tỷ lệ nhầm cực. Trục chính của bài.
2. **Trung thực ≠ có nghĩa sinh học**: Fid+ thắng null 97–99% và Jaccard qua seed vượt null rõ
   (0,19–0,28 so với 0,026–0,033), nhưng enrichment KEGG bằng 0; ví dụ của DTSyn không tái lập;
   attention không trùng IG. Đây là phần phản biện có null, nhiều seed và case study khai báo trước
   — thứ mà các bài trước không có.
3. **Lớp đối kháng có lời giải thích riêng** (trực giao với hiệp đồng, tương quan 0,08–0,10), câu hỏi
   chỉ đặt được khi có ba lớp.

**Nơi gửi phù hợp:** tạp chí hoặc hội nghị bioinformatics tầm trung, hoặc một track về evaluation và
reproducibility. Không nhắm các chỗ đòi SOTA.

## 3.11. Còn thiếu gì

Theo thứ tự ảnh hưởng tới bài:

1. **Kiểm chứng ngoài trên ALMANAC** — đã chạy ngày 23/11/2026, và kết quả đổi hướng của mục này.
   ALMANAC được lấy từ chính `summary_table_v1.4.csv` của DrugComb (block 132.369–432.467), không
   cần file gốc của NCI, để nhãn Loewe hai bên cùng một pipeline SynergyFinder: 234.333 bộ ba, 101
   thuốc, 49 dòng tế bào. Zero-shot QWK 0,023 (SynGT), 0,032 (SynGT + label smoothing), 0,013
   (DeepDDS), 0,017 (DeepSynergy), 0,016 (XGBoost). Ở giao thức nhị phân của DTSyn, SynGT đạt BACC
   0,529 và AUROC 0,567, tức đúng mức BACC 0,57 mà DTSyn tự báo. Cái đáng viết vào luận văn không
   phải con số mô hình mà là trần của bài kiểm tra: trên 1.163 thí nghiệm cả hai nghiên cứu đều
   chạy, hai bộ nhãn Loewe chỉ đồng thuận QWK 0,149, và trong 42 dòng O'Neil gọi là hiệp đồng
   ALMANAC chỉ giữ lại 1. Đối chứng đường ống: cùng một vector dự đoán trên 424 bộ ba bị giữ lại
   cho QWK 0,561 theo nhãn O'Neil so với 0,139 theo nhãn ALMANAC. Chi tiết ở `ket_qua_syngt.md` §8.
2. **DTSyn chưa được tái lập thành mô hình riêng** — bảng so sánh thiếu cột của chính bài làm khung.
3. **DeepSynergy ở split khó và XGBoost** — *đang chạy*, sẽ lấp xong trong vài giờ.
4. **Lệch planner:** dò 16 cấu hình thay vì 40; 3 seed thay vì 5; và đợt dò HP làm trên readout CLS
   cũ, trước khi chốt readout skip — tức siêu tham số hiện dùng chưa được dò lại cho kiến trúc cuối.
5. Số bộ ba 18.870 so với 23.052 của DTSyn: **phải đối chiếu bước lọc và ghi rõ lý do chênh lệch**
   trong luận văn.
6. `N_RAND` = 10 trong code so với 20 trong planner — sửa một trong hai chỗ cho khớp.
7. Tính mới của đầu ra ordinal: **phải tra lại** "ordinal drug synergy", "three-class synergy QWK"
   trước khi nộp.
8. **Code chưa commit.**
