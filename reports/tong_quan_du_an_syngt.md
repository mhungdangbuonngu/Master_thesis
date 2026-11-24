# Tổng quan dự án SynGT — dự đoán hiệp đồng thuốc 3 lớp + XAI

Cập nhật: 23/11/2026. Chi tiết số liệu: `reports/ket_qua_syngt.md`, bảng gốc: `reports/tables/`.
Kế hoạch gốc: `reports/planner_de_xuat_3.md`.

## 1. Dự án làm gì

Dự đoán một cặp thuốc trên một dòng tế bào ung thư là **đối kháng (ant)**, **cộng tính (add)** hay **hiệp đồng (syn)**, rồi **giải thích** vì sao mô hình đưa ra dự đoán đó. Dữ liệu là O'Neil (qua DrugComb v1.4): 18.870 bộ ba (thuốc A, thuốc B, dòng tế bào), 36 thuốc, 37 dòng tế bào, 7 loại mô. Nhãn lấy từ điểm Loewe với ngưỡng ±10 (4.391 ant / 13.207 add / 1.272 syn).

## 2. Mô hình tên là gì, cấu trúc ra sao

**Tên: SynGT** (Synergy Graph-Transformer), khoảng 4,16 triệu tham số.

Luồng dữ liệu của một bộ ba:

1. **Thuốc A, B** (SMILES) → đồ thị phân tử, đặc trưng nguyên tử 78 chiều → **GIN 2 lớp** (d = 256) → token cho từng nguyên tử.
2. **Dòng tế bào** → biểu hiện 944 gen landmark (z-score chỉ fit trên train) → mỗi gen là một token = embedding node2vec (huấn luyện trên mạng PPI STRING) ghép với giá trị biểu hiện.
3. **Transformer mịn** (2 lớp, 4 đầu): chuỗi `[CLS | nguyên tử A | nguyên tử B | token gen]`.
4. **Transformer thô** (2 lớp): chuỗi `[CLS | thuốc A đã pool | thuốc B đã pool | tế bào]`.
5. **Readout**: nối `[CLS mịn ; CLS thô ; pA+pB ; |pA−pB| ; vector tế bào]`, cộng thêm **nhánh MLP fingerprint Morgan** vào vector từng thuốc.
6. **Đầu CORN** (ordinal): 2 logit có điều kiện, ra xác suất ant < add < syn có thứ tự bảo đảm theo cấu trúc.

Hai tính chất thiết kế: không có embedding phân biệt A/B nên mô hình **đối xứng tuyệt đối** f(A,B,c)=f(B,A,c) (có test đơn vị); và `z_syn − z_add` đúng bằng logit có điều kiện thứ hai (có test).

## 3. Có trùng mô hình của bài báo khác không

**Không giống hệt bài nào, nhưng không phải kiến trúc mới.** SynGT là sự ghép các ý đã công bố:

| Thành phần | Nguồn |
|---|---|
| Hai transformer mịn/thô, token nguyên tử + gen, node2vec trên PPI | **DTSyn** (Brief Bioinform 2022) — khung chính |
| Đặc trưng nguyên tử 78 chiều; readout `[pA+pB ; \|pA−pB\| ; cell]` | DeepDDS |
| Nhánh fingerprint Morgan | DeepSynergy |
| GIN thay GCN | khác DTSyn (GCN được giữ làm ablation) |
| Đầu CORN 3 lớp có thứ tự, đánh giá QWK | **mới trong lĩnh vực synergy** (theo khảo sát lúc lập plan) |
| Đối xứng A↔B theo cấu trúc | DTSyn chỉ kiểm tra bằng thực nghiệm; chi tiết nhỏ |

Vì vậy bài báo **không nên** được định vị là "kiến trúc mới". Phần ablation còn cho thấy bỏ hai transformer không làm giảm kết quả, nên càng không thể lập luận theo hướng đó.

## 4. Quy trình đã chạy (flow)

1. **Dữ liệu** (`src/data/`): trích O'Neil, tra SMILES (36/38 thuốc; MK-4541 và MRK-003 không có cấu trúc công khai nên bị loại), chuẩn hóa RDKit, đặc trưng, node2vec (có bản STRING xáo giữ bậc để đối chứng), 5 kiểu chia: random, leave_combo, leave_drug, leave_cell, leave_tumor. Validation luôn chia theo cùng đơn vị với split ngoài.
2. **Mô hình** (`src/model/`, `src/repro/`): SynGT và các baseline: majority, chỉ tế bào, chỉ thuốc, one-hot, DeepSynergy, DeepDDS.
3. **Chặn G1**: tái lập số công bố trước khi làm gì khác. Đạt (xem §5).
4. **Dò siêu tham số** 16 cấu hình; **chẩn đoán kiến trúc** 27 run (xem §6).
5. **Sweep** (`src/sweep.py`): 613 run lưới chính + 16 dò + 27 chẩn đoán = 656 run, cùng ngân sách 120 epoch/patience 20. Không run nào lỗi hay thiếu.
6. **XAI** (`src/xai/`): 39 run giải thích, rồi **case study** khai báo trước, rồi **bảng báo cáo** (`src/eval/report.py`).
7. 16 test đơn vị đều qua.

Cách chạy lại: `bash run_all.sh 4` (toàn bộ, bỏ qua run đã xong) hoặc `bash run_xai.sh 4` (chỉ phần XAI).

## 5. Kết quả dự đoán

QWK 3 lớp (`main_ord3.csv`), cùng ngân sách 120 epoch / patience 20:

| Mô hình | leave_combo | leave_drug | leave_cell | leave_tumor |
|---|---|---|---|---|
| **SynGT + label smoothing** | **0,627** | 0,214 | 0,489 | 0,474 |
| DeepSynergy | 0,605 | 0,051 | 0,456 | 0,433 |
| SynGT (CORN thường) | 0,589 | **0,224** | 0,478 | 0,459 |
| one-hot | 0,573 | 0,190 | 0,478 | 0,460 |
| XGBoost (fingerprint + biểu hiện) | 0,546 | 0,194 | **0,504** | **0,489** |
| DeepDDS | 0,536 | 0,191 | 0,483 | 0,459 |

- Label smoothing ở ngưỡng (planner 3.3) thắng CORN thường trên validation ở **cả bốn** kiểu chia, nên nó được chọn theo validation chứ không theo test. Nó đổi recall lớp hiệp đồng để lấy QWK: ở leave_combo 0,440 so với 0,456, ở leave_drug chỉ còn 0,221 so với 0,315.
- **XGBoost trên fingerprint thắng mọi mô hình học sâu ở leave_cell và leave_tumor.** Đây là con số khó chịu nhất của dự án.
- DeepSynergy sụp ở leave_drug (0,051): nó là mô hình mạnh nhất khi thuốc đã gặp, và gần như vô dụng khi chưa gặp.
- Baseline tái lập được số công bố (DeepDDS ROC-AUC 0,945 so với ~0,93 công bố), nên pipeline đáng tin.
- **Kết quả nổi bật (RQ1):** bỏ vùng trung tính 0–10 như DTSyn làm AUROC tăng 0,054–0,060 và AUPRC tăng 0,21–0,30 ở mọi mô hình.

Ngoài O'Neil, trên NCI-ALMANAC (234.333 bộ ba, zero-shot, không huấn luyện lại):

| Mô hình | QWK nội bộ (leave_combo) | QWK trên ALMANAC |
|---|---|---|
| SynGT + label smoothing | 0,627 | 0,032 |
| SynGT | 0,589 | 0,023 |
| DeepSynergy | 0,605 | 0,017 |
| XGBoost | 0,546 | 0,016 |
| DeepDDS | 0,536 | 0,013 |

- Thứ tự giữa các mô hình ở bảng trên **không còn nhìn thấy được** ở cột ALMANAC: mọi mô hình đều về cùng một mức, recall lớp hiệp đồng 0,01–0,04 trên tỷ lệ cơ sở 0,015.
- Không phải lệch phân phối đầu vào: khoảng cách biểu hiện tới dòng ALMANAC (34,97–36,70) ngang với tới dòng O'Neil bị giữ lại (33,63–36,46), và thuốc ALMANAC còn gần tập huấn luyện hơn (Tanimoto trung vị 0,222 so với 0,191 của chính thuốc O'Neil so với nhau).
- Không phải đường ống chấm điểm: trên 424 bộ ba mà dòng O'Neil tương ứng bị giữ lại, cùng một vector dự đoán cho QWK 0,561 theo nhãn O'Neil và 0,139 theo nhãn ALMANAC.
- Trần của bài kiểm tra là **QWK 0,149**: đó là mức hai nghiên cứu đồng thuận với nhau trên 1.163 thí nghiệm trùng nhau, và trong 42 tổ hợp O'Neil gọi là hiệp đồng, ALMANAC giữ lại 1. Chi tiết ở `ket_qua_syngt.md` §8.

## 6. XAI có giải thích được không

Phương pháp: Integrated Gradients trên gen, mảnh BRICS và nguyên tử; ba target (`logit`, `contrast = z_syn−z_add`, `ant`); tương tác cặp mảnh bậc hai chính xác; attention; GNNExplainer; đo riêng đóng góp của đồ thị so với fingerprint.

**Làm được:**
- Giải thích **trung thực với mô hình**: xóa đơn vị xếp hạng cao thay đổi dự đoán nhiều hơn xóa ngẫu nhiên ở 97–99% bộ ba; sai số completeness ≤ 1,4%.
- Giải thích **ổn định giữa các seed**: Jaccard top-50 0,190–0,279 so với null 0,026–0,033, cosine 0,473–0,593 so với null quanh 0, trên đúng 40 bộ ba dùng chung. *Bản báo cáo trước nói ngược lại (≈ 0,03, "ngang ngẫu nhiên"); đó là lỗi đo chứ không phải tính chất của mô hình, xem `ket_qua_syngt.md` §7.4.*
- Giải thích **ổn định cả khi đổi quy ước nhãn**: cả 30 dòng chéo quy ước (4 điểm synergy, 2 ngưỡng) đều vượt null, Jaccard 0,077–0,283 so với null 0,026–0,034.
- Lời giải thích cho đối kháng gần như trực giao với lời giải thích cho hiệp đồng (tương quan ≈ 0,09), một câu hỏi mà mô hình nhị phân không hỏi được.
- Attention gần như không trùng IG (Jaccard 0,041–0,051): không nên coi attention là lời giải thích.

**Không làm được:**
- **Không có ý nghĩa sinh học**: không có enrichment KEGG; 0/8 case study vượt null; 5 gen DTSyn công bố cho ETOPOSIDE+MK-2206 xếp hạng 163–917/944 trong kết quả của chúng tôi.
- Fingerprint mang khoảng 51–55% quyết định, nên giải thích cấp mảnh chỉ nói được một nửa câu chuyện; tương tác cặp mảnh chỉ bằng 2–4% hiệu ứng bậc một.

Kết luận: XAI cho ra giải thích *đúng với mô hình* nhưng *chưa chứng minh đúng với sinh học*.

## 7. Vấn đề đã gặp

| Vấn đề | Xử lý |
|---|---|
| SynGT bản đầu underfit (QWK 0,460, thua one-hot) do chỉ đọc qua CLS | Thêm readout skip, bỏ attention dropout, thêm fingerprint; chọn theo val QWK → 0,589 |
| `log(probs)` bị kẹp ở 1e-7, làm gradient bằng 0 với bộ ba đối kháng chắc chắn | Công thức log-sigmoid; chạy lại toàn bộ XAI. Một kết luận trước đó ("logit thua null") thực ra là sản phẩm của lỗi và đã bị loại |
| Loss chi phí thuần sụp về luôn đoán add | Đổi thành CE + chi phí, chạy lại |
| Đối chứng hoán vị SMILES còn rò qua fingerprint | Hoán vị cả hai |
| Run dò HP lọt vào bảng chính; ngân sách không đồng đều | Lọc trong báo cáo; mọi mô hình 120/20 |
| RAM chạm 91% | Hạ xuống 4 worker. Nguyên nhân chính là `/tmp` (tmpfs) chiếm ~16 GB của các dự án khác |
| `pick_triples` gieo rng bằng `hash(split)`, mà Python thêm muối hash theo tiến trình, nên mỗi run giải thích một tập bộ ba khác (3 seed chung nhau 0–2 trên 40). Bảng độ ổn định vẫn so theo vị trí, và vì đối chứng được định nghĩa là "ghép bộ ba khác nhau", hàm đo và hàm đối chứng tính cùng một đại lượng. Kết luận "giải thích không ổn định giữa các seed" là sản phẩm của lỗi này | Bảng offset cố định; khớp theo id bộ ba; in `n_triples`; test chạy trong 3 tiến trình với `PYTHONHASHSEED` khác nhau. Chạy lại 54 run giải thích (23/11, 4h47m). Kết luận đảo: Jaccard 0,19–0,28 so với null 0,026–0,033 |
| Khóa `(quy ước, split, fold, seed)` trùng giữa run chính và 3 run ablation, nên mốc so sánh của bảng RQ5 thật ra là bản node2vec trên STRING đã xáo | Thêm `is_plain_cfg`, ablation không chiếm chỗ trong cả 3 bảng ổn định |
| Cosine 0,436 từng được báo trong tài liệu, nhưng `xai_metrics.py` không có hàm cosine nào: con số đó tính tay ngoài pipeline | Đưa cosine vào `stability` / `stability_null`. Giá trị thật 0,473–0,593 |
| Đối chứng hoán vị SMILES rò lần hai, qua `n_frag`; và phần XAI dựng lại kho phân tử từ dữ liệu gốc nên sẽ giải thích run hoán vị bằng phân tử thật (chưa run nào bị) | Một hàm `permute_molecules` duy nhất cho cả kho phân tử và fingerprint, kèm `assert` bắt tensor theo thuốc bị bỏ sót |
| 34 run label smoothing ở split khó không xuất hiện ở bảng nào vì `is_plain_syngt` đòi `loss == "corn"` | `t_main` thêm dòng `syngt_smooth` ở cả 4 split |

## 8. Giới hạn và việc chưa làm

- O'Neil chỉ có 36 thuốc, 37 dòng tế bào, nên danh tính chi phối; đây là lý do hợp lý nhất cho việc transformer và PPI không đóng góp. Đây là giả thuyết, chưa được kiểm chứng riêng.
- Nghịch lý còn lại: lời giải thích ổn định với mô hình nhưng không khớp sinh học. Không còn quy được cho nhiễu giữa seed.
- Kiểm chứng ngoài trên ALMANAC **đã chạy** ngày 23/11/2026 (234.333 bộ ba lấy từ khoảng block 132.369–432.467 của chính file DrugComb v1.4, 101 thuốc, 49 dòng tế bào). Zero-shot QWK 0,023 cho SynGT, 0,013–0,017 cho DeepDDS, DeepSynergy, XGBoost. Trần của bài kiểm tra này là QWK 0,149, vì hai nghiên cứu chỉ đồng thuận tới mức đó trên 1.163 thí nghiệm trùng nhau, nên nó không trả lời được câu hỏi tổng quát hóa.
- **Chưa chạy so với planner:** DTSyn chưa được tái lập như một mô hình riêng (chỉ có khung tương tự trong SynGT).
- Lệch planner: dò 16 cấu hình thay vì 40, 3 seed thay vì 5; dò HP làm trên readout CLS cũ.
- Chưa commit code. Tổng 828 run huấn luyện, 39 run giải thích, 15 run giải thích chéo quy ước, 20 test đơn vị.

## 9. Hướng viết bài

Không viết "SOTA". Ba trục đứng được: (1) giao thức bỏ vùng trung tính thổi phồng kết quả; (2) bài toán 3 lớp có thứ tự cho phép giải thích riêng cho đối kháng; (3) giải thích trung thực với mô hình không đồng nghĩa ổn định hay có ý nghĩa sinh học, kèm đối chứng null, nhiều seed và case study khai báo trước.
