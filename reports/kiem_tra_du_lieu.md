# Kiểm tra dữ liệu SynGT — đã đúng chưa, đã đủ chuẩn để huấn luyện chưa

Ngày kiểm: 21/11/2026. Kiểm bằng dữ liệu thật trong `data/processed/`, không chỉ đọc code.
Mã liên quan: `src/data/{oneil,smiles,cell,featurize,splits}.py`, `src/train.py`.

**Kết luận ngắn: dữ liệu đúng và đủ chuẩn để huấn luyện.** Không tìm thấy rò rỉ nào. Có 6 giới
hạn thực sự, tất cả đều là tính chất của dữ liệu gốc chứ không phải lỗi pipeline; chúng cần được
nêu trong phần Limitations chứ không cần sửa.

## 1. Bằng chứng mạnh nhất: trích đúng bộ O'Neil

DrugComb v1.4 **không có cột `study_name`**, nên việc lấy O'Neil phải dựa vào giả định
`block_id <= 92208`. Giả định này giờ đã được kiểm chứng độc lập:

| Kiểm tra | Pipeline cho ra | O'Neil 2016 công bố | Khớp |
|---|---|---|---|
| Số cặp thuốc | **583** | **583** | đúng tuyệt đối |
| Số thuốc | 38 | 38 | đúng |
| Số dòng tế bào | 39 | 39 | đúng |
| Dòng tế bào mỗi cặp | đúng 37 (min = median = max) | lưới đầy | đúng |

Con số 583 khớp chính xác là bằng chứng thuyết phục nhất: nếu ranh giới block sai, số cặp gần
như chắc chắn sẽ lệch. Lưới hoàn toàn cân bằng (mọi cặp đều có đủ 37 dòng tế bào) cũng loại
khả năng trích lẫn sang study khác.

## 2. Gộp bản lặp và đối xứng A↔B

- Mỗi bộ ba xuất hiện dưới nhiều block (bản lặp và cả hai thứ tự thuốc): median **4** block,
  315 bộ ba có 8 block.
- Thứ tự cặp được chuẩn hóa (`min`/`max` theo tên) **trước khi** gộp, nên (A,B) và (B,A) rơi vào
  cùng một bộ ba. Kết quả: **0 bộ ba trùng**, **0 cặp tự thân (A=A)**.
- Gộp bằng **median** của từng điểm synergy, giữ lại `n_replicates` và `loewe_iqr` để báo nhiễu nhãn.

## 3. Không có rò rỉ trong bất kỳ split nào

Kiểm toàn bộ **27 fold** trên 5 kiểu chia:

| Kiểu chia | Fold | Chồng hàng train/val/test | Phủ dữ liệu | Trùng hàng |
|---|---|---|---|---|
| random | 5 | 0 | 18.870/18.870 | 0 |
| leave_combo | 5 | 0 | 18.870/18.870 | 0 |
| leave_cell | 5 | 0 | 18.870/18.870 | 0 |
| leave_tumor | 7 | 0 | 18.870/18.870 | 0 |
| leave_drug | 5 | 0 | 18.870/18.870 | 0 |

Định nghĩa đơn vị bị giữ lại cũng đúng, không chỉ đúng ở mức hàng:

- **leave_combo**: 0 cặp thuốc trùng giữa train và test; đồng thời **3.774/3.774** bộ ba test có
  cả hai thuốc đã thấy trong train. Đúng định nghĩa "cặp mới, thuốc cũ".
- **leave_drug**: **0 bộ ba test có cả hai thuốc đã thấy** ở mọi fold. Mọi bộ ba test đều có ít
  nhất một thuốc hoàn toàn mới (fold 0: 4.440 có một thuốc mới, 2.886 có cả hai mới). Validation
  cũng nghiêm y như vậy. Đây là định nghĩa nghiêm, không phải bản dễ.
- **leave_cell / leave_tumor**: 0 dòng tế bào trùng giữa train và test, và giữa val và test.

Validation luôn được chia theo **cùng đơn vị** với split ngoài, nên việc chọn epoch không mượn
thông tin từ đơn vị bị giữ lại.

## 4. Không rò rỉ qua thống kê fit trên dữ liệu

- **z-score biểu hiện gen**: `standardise(expr, train_cells)` với `train_cells` lấy từ **chỉ các
  hàng train** (`torch.unique(trip[tr_i][:, 2])`). Cùng một hàm được dùng cho cả SynGT và
  XGBoost, nên so sánh giữa các mô hình là công bằng.
- **Chọn gen** (khi hạ xuống 384 token): xếp theo phương sai trên **toàn bộ model DepMap**, là
  dữ liệu ngoài 37 dòng tế bào của chúng ta → không rò rỉ theo cả hai chiều.
- **Trọng số lớp**: `torch.bincount(y[tr_i])` — chỉ từ hàng train.
- **Chọn mô hình**: early stopping và lưu checkpoint hoàn toàn theo **validation**; test chỉ được
  đánh giá một lần sau khi nạp lại checkpoint tốt nhất.
- **bin_gap**: các hàng trong vùng trung tính là NaN và bị loại khỏi **cả ba** tập một cách nhất
  quán, trong cả `src/train.py` và `src/repro/xgb.py`.

## 5. Cấu trúc thuốc và biểu hiện gen

- SMILES: 36/38 thuốc tra được, **36/36 hợp lệ với RDKit**, **0 InChIKey trùng**, **0 SMILES
  chuẩn hóa trùng** → không có thuốc nào bị đếm hai lần dưới hai tên.
- 2 thuốc bị loại (MK-4541, MRK-003) vì không có cấu trúc công khai. Việc loại này **gần như
  không làm lệch nhãn**: phần bị loại có ant/add/syn = 25,2/69,6/5,2% so với phần giữ lại
  23,3/70,0/6,7%, loewe trung bình −5,64 so với −5,51.
- Biểu hiện: 944 gen landmark có trong DepMap (trên 978 của L1000), log2(TPM+1), khoảng 0–13,4,
  **0 giá trị NaN**.

## 6. Sáu giới hạn thực sự (nêu trong Limitations, không phải lỗi)

**1. Nhiễu nhãn ngay tại ngưỡng.** **10,2%** bộ ba (2.195) có nửa khoảng IQR giữa các bản lặp
vắt qua ngưỡng ±10 — nghĩa là lớp của chúng có thể đổi nếu lấy mẫu lại bản lặp. IQR phân vị 99
là **12,0**, lớn hơn cả ngưỡng. Đây là giới hạn nội tại của dữ liệu. Nó cũng giải thích vì sao
label smoothing tại ngưỡng cải thiện được kết quả (6/6 cặp fold, +0,043 val QWK): mô hình không
còn bị phạt vì những bộ ba mà bản thân nhãn đã mơ hồ.

**2. Hai dòng tế bào dùng biểu hiện của dòng chị em.** COLO320DM → COLO-320, EFM192B → EFM-192A
(2/37). Đã ghi rõ trong `src/data/cell_line_map.csv`.

**3. Hai dòng tế bào bị loại.** OCUBM (có trong DepMap nhưng không có profile biểu hiện) và
UWB1289+BRCA1 (không có trong DepMap; **không** tái dùng biểu hiện của UWB1.289 vì như vậy sẽ
tạo ra hai dòng tế bào có đầu vào giống hệt nhau). Quyết định sau là đúng.

**4. 33/944 gen landmark có vector node2vec toàn số 0** vì không có trong STRING ở ngưỡng
score ≥ 700. Ít ảnh hưởng: ablation bỏ hẳn gene embedding chỉ làm QWK giảm 0,003.

**5. leave_drug có tập train nhỏ hơn tập test.** Fold 0: train 5.365 so với test 7.326 (train chỉ
28% dữ liệu). Đây là hệ quả tất yếu của định nghĩa nghiêm. Nó là một phần lý do QWK ở leave_drug
thấp (0,22), và cần nói rõ là mô hình ở đó học từ ít hơn một phần ba dữ liệu.

**6. Mất cân bằng lớp.** Hiệp đồng chỉ 6,7% (1,272/18.870). Với split theo đơn vị, tỉ lệ hiệp
đồng trong test dao động 4,5–8,3% giữa các fold. Đã xử lý bằng trọng số lớp và báo theo từng fold,
nhưng khoảng tin cậy của các chỉ số liên quan đến lớp hiệp đồng vì vậy rộng hơn.

## 7. Số liệu cuối cùng dùng để huấn luyện

| | |
|---|---|
| Bộ ba | 18.870 |
| Thuốc | 36 |
| Dòng tế bào | 37 |
| Cặp thuốc | 510 |
| Loại mô | 7 (Bowel 8, Ovary 8, Lung 7, Skin 6, Breast 5, Prostate 2, Pleura 1 dòng) |
| Nhãn ord3_loewe (ant/add/syn) | 4.391 / 13.207 / 1.272 |
| Điểm synergy | Loewe, Bliss, ZIP, HSA |
| Ngưỡng | ±5, ±10, ±20 |

Provenance đầy đủ trong `data/processed/provenance_*.json`.
