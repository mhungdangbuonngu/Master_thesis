# Kết quả chạy đầy đủ — SynGT (planner_de_xuat_3.md)

Ngày chạy xong: 18/11/2026. Bảng số gốc: `reports/tables/*.csv` và `reports/tables/tables.md`
(sinh bằng `python -m src.eval.report`). Mọi con số dưới đây là trung bình trên các fold × seed,
trong ngoặc là khoảng tin cậy bootstrap 95%.

## 0. Tóm tắt một đoạn

SynGT (GIN + hai transformer kiểu DTSyn + readout đối xứng + nhánh fingerprint + đầu ra CORN
3 lớp có thứ tự) đạt **QWK 0,589** ở leave-combination-out, đứng thứ hai sau DeepSynergy
(0,605), hơn rõ DeepDDS (0,536), ngang one-hot (0,573). Ở giao thức nhị phân của DTSyn,
SynGT đạt ROC-AUC 0,946. **RQ1 cho kết quả rõ nhất**: bỏ vùng trung tính 0–10 như DTSyn làm
AUROC tăng 0,054–0,060 và AUPRC tăng 0,21–0,30 ở *mọi* mô hình. Phần XAI **trung thực với
mô hình** (Fid+ thắng null ở 97–99% tam nguyên, completeness lệch ≤ 1,4%) và **ổn định giữa
các seed** (Jaccard top-50 0,19–0,28 so với null 0,026–0,033; cosine 0,47–0,59 so với null
khoảng 0), nhưng **không có ý nghĩa sinh học** (enrichment KEGG ≈ null; 0/8 case study vượt
null). Con số ổn định ở bản trước báo cáo là "ngang ngẫu nhiên": đó là lỗi đo, xem §7.4.
Hai transformer không đóng góp vào độ chính xác (ablation). **Kiểm chứng ngoài trên NCI-ALMANAC
đã chạy** (234.333 bộ ba, 101 thuốc, 49 dòng tế bào): zero-shot QWK rơi về 0,023, và cả DeepDDS,
DeepSynergy, XGBoost cũng rơi về 0,013–0,017. Nguyên nhân không phải mô hình: trên 1.163 thí
nghiệm cả hai nghiên cứu đều chạy, bản thân hai bộ nhãn chỉ đồng thuận QWK 0,149, và cùng một
vector dự đoán cho QWK 0,561 khi chấm theo nhãn O'Neil so với 0,139 khi chấm theo nhãn ALMANAC
(§8).

## 1. Thiết lập

| Mục | Giá trị |
|---|---|
| Dữ liệu | O'Neil (DrugComb v1.4): 18.870 tam nguyên, 36 thuốc, 510 cặp, 37 dòng tế bào, 7 mô |
| Nhãn chính | `ord3_loewe`: ant < −10 / add / syn > 10 → 4.391 / 13.207 / 1.272 |
| Tế bào | 944 gen landmark L1000, z-score fit trên train của từng fold; node2vec trên STRING ≥ 700 |
| Split | random, leave_combo (chính), leave_drug, leave_cell, leave_tumor |
| Seed | 3 seed cho bảng chính và G1, 2 seed cho ablation và độ nhạy |
| Ngân sách | 120 epoch, patience 20, **giống nhau cho mọi mô hình** |
| Tổng | 656 run train, 39 run giải thích, 0 lỗi |

**Kiến trúc chốt** (chọn theo **val** QWK trên fold 0–2 của leave_combo, `architecture_diagnosis.csv`):

| Biến thể | val QWK | test QWK |
|---|---|---|
| bản đầu (chỉ đọc qua token CLS, như DTSyn) | 0,486 | 0,460 |
| + readout skip `[pA+pB ; |pA−pB| ; cell]` | 0,552 | 0,553 |
| + head rộng | 0,581 | 0,564 |
| **+ nhánh fingerprint Morgan (bản chốt)** | **0,605** | **0,587** |

Bản đầu bị underfit: ở epoch 40, train loss của nó còn 0,28, trong khi DeepSynergy đã xuống 0,06.
Siêu tham số khác lấy từ đợt dò 16 cấu hình (`hp_search.csv`): d = 256, 2 lớp GIN,
2 + 2 lớp transformer, dropout 0,15, lr 3,3e-4, batch 256.

## 2. Gate G1 — tái lập số công bố (random 5-fold, nhị phân bỏ vùng 0–10, 15 run)

| Mô hình | ROC-AUC | AUPRC | Số công bố |
|---|---|---|---|
| DeepSynergy | 0,958 ± 0,003 | 0,805 | AUC 0,90 |
| one-hot | 0,957 ± 0,004 | 0,804 | — |
| **SynGT** | **0,946 ± 0,004** | 0,732 | (DTSyn: 0,89) |
| DeepDDS | 0,945 ± 0,004 | 0,754 | ~0,93 |

**Đạt.** Cả hai baseline đều bằng hoặc vượt số công bố của chính chúng. AUPRC không so trực
tiếp được với các bài khác vì tỷ lệ lớp dương ở đây chỉ 10,4%.

**Cảnh báo phải ghi trong bài:** one-hot (không SMILES, không biểu hiện gen) đạt 0,957 trên
random split. Trên split này, nhớ danh tính (cặp thuốc, dòng tế bào) gần như là đủ, nên random
split **không phân biệt được các mô hình**.

## 3. Bảng chính — 3 lớp, QWK (`main_ord3.csv`)

| Mô hình | leave_combo (15 run) | leave_drug | leave_cell | leave_tumor | random |
|---|---|---|---|---|---|
| DeepSynergy | **0,605** [0,595–0,616] | — | — | — | — |
| **SynGT** | **0,589** [0,580–0,601] | **0,224** [0,173–0,280] | 0,478 | 0,459 | 0,628 |
| one-hot | 0,573 [0,564–0,581] | 0,190 | 0,478 | 0,460 | — |
| DeepDDS | 0,536 [0,529–0,544] | 0,191 | 0,483 | 0,459 | 0,606 |
| chỉ thuốc | 0,409 | — | — | — | — |
| chỉ tế bào | 0,098 | — | — | — | — |
| majority | 0,000 | — | — | — | — |

Nhầm cực (syn ↔ ant) của SynGT chỉ 0,3%. Ở leave_drug, SynGT nhỉnh hơn nhưng khoảng tin cậy
chồng nhau. DeepSynergy chưa được chạy ở các split khó (giới hạn của lưới, xem §9).

**Đọc kết quả:** SynGT hơn DeepDDS, mô hình GNN gần nó nhất, một cách có ý nghĩa thống kê;
cạnh tranh với baseline mạnh nhất; **không phải tốt nhất**.

## 4. RQ1 — cái giá của việc bỏ vùng trung tính (`rq1_gap_cost.csv`)

Cùng mô hình, cùng split. "Bỏ vùng" = giao thức DTSyn (loại 35,2% tam nguyên có Loewe ∈ [0, 10]);
"toàn bộ" = > 10 là dương, phần còn lại là âm.

| Mô hình | split | AUROC bỏ vùng → toàn bộ | AUPRC bỏ vùng → toàn bộ |
|---|---|---|---|
| DeepDDS | leave_combo | 0,907 → 0,847 (−0,060) | 0,625 → 0,344 (−0,281) |
| DeepSynergy | leave_combo | 0,922 → 0,866 (−0,055) | 0,679 → 0,405 (−0,273) |
| SynGT | leave_combo | 0,903 → 0,848 (−0,055) | 0,602 → 0,357 (−0,245) |
| one-hot | leave_combo | 0,923 → 0,869 (−0,054) | 0,693 → 0,421 (−0,272) |
| SynGT | random | 0,946 → 0,889 (−0,058) | 0,732 → 0,441 (−0,291) |
| DeepDDS | random | 0,945 → 0,889 (−0,056) | 0,754 → 0,452 (−0,302) |

**Kết luận RQ1:** con số đẹp của giao thức DTSyn có khoảng 0,055 AUROC và khoảng 0,25 AUPRC
đến từ việc loại bỏ chính những tam nguyên khó nhất. Hiệu ứng này nhất quán ở mọi mô hình và
mọi split, nên đây là thuộc tính của giao thức đánh giá, không phải của một mô hình cụ thể.

## 5. RQ2 — đầu ra có thứ tự (`rq2_ordinal_loss.csv`)

| Loss | QWK | MAE | Macro-F1 | Nhầm cực |
|---|---|---|---|---|
| **CORN** (15 run) | **0,589** | **0,219** | **0,660** | 0,3% |
| cross-entropy thường (6) | 0,580 | 0,227 | 0,655 | 0,4% |
| CE + chi phí kỳ vọng (6) | 0,580 | 0,223 | 0,658 | 0,3% |

CORN tốt nhất ở mọi chỉ số, nhưng chênh lệch nhỏ (khoảng 0,01 QWK). Nên viết là "lợi ích có
nhưng khiêm tốn". Lợi ích chính của CORN là thứ tự lớp được bảo đảm theo cấu trúc, và nó cho
target XAI `contrast` = logit có điều kiện thứ hai một cách chính xác (§7).

## 6. Ablation (`ablation.csv`, leave_combo, fold 0–2 × 2 seed)

| Biến thể | QWK |
|---|---|
| bỏ cả hai transformer | 0,591 |
| bỏ transformer mức mịn | 0,591 |
| **SynGT đầy đủ** | **0,589** |
| GCN thay GIN | 0,589 |
| bỏ embedding node2vec | 0,586 |
| node2vec trên STRING **xáo trộn** | 0,585 |
| bỏ transformer mức thô | 0,584 |
| SMILES hoán vị (chỉ giữ danh tính) | 0,574 |
| **chỉ đồ thị, bỏ fingerprint** | **0,565** |
| readout CLS gốc kiểu DTSyn | **0,483** |

1. **Transformer không giúp gì** (0,591 so với 0,589). DTSyn báo AUC tụt từ 0,89 xuống 0,69
   khi bỏ transformer; **chúng tôi không tái lập được điều đó**. Trong dữ liệu của chúng tôi,
   chính cách readout mới là thứ quyết định (CLS-only: 0,483).
2. **PPI không mang thông tin**: STRING thật và STRING xáo cho kết quả như nhau (0,586 / 0,585).
   Kết quả này khớp với lần chạy trước của repo.
3. **Cấu trúc hóa học đóng góp ít**: hoán vị SMILES chỉ làm mất 0,015. Fingerprint giúp được
   0,024 so với chỉ dùng đồ thị.

## 7. XAI (39 run giải thích; 40 syn + 40 ant tam nguyên test mỗi run)

### 7.1 Độ trung thực với mô hình — **tốt**

- **Fid+** (xóa top-k so với xóa ngẫu nhiên cùng số lượng): thắng null ở **97–99,8%** tam nguyên,
  cho cả gen lẫn mảnh BRICS và cả ba target. Ví dụ: xóa 25% gen theo `contrast` trên tam nguyên
  hiệp đồng làm điểm giảm 5,34, trong khi xóa ngẫu nhiên chỉ làm giảm 0,32.
- **Completeness** của IG: lệch ≤ 1,4% với gen, ≤ 0,6% với mảnh (`xai_completeness.csv`).
- **Faithfulness Violation Test** (Spearman giữa attribution và hiệu ứng xóa từng đơn vị):
  0,32–0,47; tỷ lệ vi phạm 12–27%.

### 7.2 RQ3 — ba target cho ba lời giải thích khác nhau (`rq3_levels.csv`)

Tương quan thứ hạng giữa các bản đồ attribution trên cùng tam nguyên:

| | contrast ↔ logit | contrast ↔ ant | logit ↔ ant |
|---|---|---|---|
| tam nguyên hiệp đồng | 0,887 | 0,095 | 0,091 |
| tam nguyên đối kháng | 0,727 | 0,084 | 0,053 |

Lời giải thích cho **đối kháng gần như trực giao** với lời giải thích cho hiệp đồng. Đây là câu
hỏi mà một mô hình nhị phân (đối kháng bị gộp vào lớp âm) không đặt ra được. `contrast` và
`logit` gần nhau trên tam nguyên hiệp đồng (0,89), nhưng tách ra rõ hơn trên tam nguyên đối
kháng (0,73).

> Lưu ý: trước khi sửa lỗi log-sigmoid (§8), target `logit` có vẻ "thua null" trên tam nguyên
> đối kháng. Sau khi sửa, hiện tượng đó biến mất. Kết luận cũ là sản phẩm của lỗi, không được
> dùng.

### 7.3 Attention có phải lời giải thích không?

Jaccard top-50 giữa attention (CLS → gen) và IG chỉ **0,04–0,05**. Attention mà DTSyn, MD-Syn
và AttenSyn trình bày như lời giải thích gần như không trùng với những gen thực sự thay đổi
quyết định khi bị xóa.

### 7.4 RQ5 — độ ổn định giữa các seed — **đạt** (kết luận đã được sửa)

Jaccard top-50 gen của *cùng* tam nguyên giữa 3 seed: **0,190–0,279**, so với null 0,026–0,033.
Cosine của vector quy gán 944 chiều: **0,473–0,593**, null từ −0,011 tới 0,058. Cả 6 tổ hợp
(lớp × target) đều vượt null, trên đúng 40 tam nguyên dùng chung (`rq5_stability.csv`, cột
`n_triples`).

**Bản trước của bảng này báo 0,032–0,044 so với null 0,027–0,040 và kết luận "không tái lập
được". Kết luận đó sai, và nó là sai số của phép đo, không phải của mô hình.** `pick_triples`
gieo rng bằng `hash(split)`, mà Python thêm muối ngẫu nhiên cho hash của chuỗi theo từng tiến
trình khi `PYTHONHASHSEED` không được đặt. Mỗi lần gọi `run_explain` là một tiến trình riêng,
nên ba seed của cùng một fold giải thích ba tập tam nguyên khác nhau: giao nhau 0 tới 2 trên 40.
Bảng vẫn đem chúng ra so theo *vị trí* trong danh sách. Vì `stability_null` được định nghĩa là
"ghép các tam nguyên khác nhau", hàm đo và hàm đối chứng khi đó tính đúng cùng một đại lượng,
nên việc chúng bằng nhau là hệ quả bắt buộc của cách cài đặt.

Đã sửa: rng gieo bằng một bảng offset cố định; lời giải thích được khớp theo id tam nguyên chứ
không theo vị trí; bảng có thêm cột `n_triples`; và ba test hồi quy trong `src/tests/test_all.py`
chặn cả hai nguyên nhân. Toàn bộ 39 run giải thích cùng 15 run chéo quy ước đã chạy lại
(23/11/2026); bản trước khi sửa giữ ở `runs_xai_prehashfix/`.

Giả thuyết cũ (37 dòng tế bào so với 944 gen nên mỗi seed chọn một tập gen khác) không còn cần
thiết để giải thích gì cả.

### 7.5 Ý nghĩa sinh học — **không đạt**

- Enrichment KEGG trong top-50 gen: 0,2–0,3% tam nguyên, null là 0% (`xai_plausibility.csv`).
- Case study khai báo trước (`case_study.csv`):
  - SynGT dự đoán đúng 5/8 tam nguyên trên cả 3 seed.
  - **0/8** vượt null về pathway khai báo trước.
  - **0/8** có gen đích của chính hai thuốc trong top-50.
- Ví dụ của DTSyn (ETOPOSIDE + MK-2206): 5 gen họ công bố (SNAP25, GALE, PRKCD, PIK3R3, DDIT4)
  xếp hạng **163–917 trên 944** trong giải thích của chúng tôi, tức không tái lập. Thêm nữa,
  dưới Loewe ±10, CAOV3 có nhãn **additive** chứ không phải hiệp đồng như mô tả của DTSyn.

### 7.6 Đồ thị hay fingerprint quyết định? (`xai_graph_vs_fp.csv`)

- Theo IG chung trên [mảnh BRICS, fp_A, fp_B]: fingerprint mang **51–55%**.
- Theo xóa trực tiếp: tắt fingerprint làm điểm thay đổi khoảng 2 lần so với tắt toàn bộ đồ thị,
  và fingerprint "thắng" ở **65–76%** tam nguyên.
- Tương tác cặp mảnh BRICS (bậc hai, chính xác) chỉ bằng **2–4%** hiệu ứng bậc một: mô hình gần
  như cộng tính theo mảnh.

## 8. Kiểm chứng ngoài — NCI-ALMANAC (`external_almanac.csv`)

### 8.1 Dữ liệu lấy từ đâu, và vì sao không lấy file gốc của NCI

ALMANAC được lấy từ **chính bảng `summary_table_v1.4.csv` của DrugComb** mà O'Neil đã lấy ra,
không phải từ `ComboDrugGrowth_Nov2017.zip` của NCI. Lý do là nhãn phải so được: DrugComb chạy
một pipeline SynergyFinder duy nhất cho mọi nghiên cứu, nên `synergy_loewe` ở ALMANAC có đúng
nghĩa như `synergy_loewe` trong nhãn huấn luyện. Tính lại Loewe từ ma trận phần trăm tăng trưởng
thô sẽ là so mô hình với một định nghĩa khác của mục tiêu.

Bản ghi trước trong nhật ký nói "DrugComb không lọc được theo study" nên phải tải file gốc. Điều
đó sai. DrugComb v1.4 không có cột `study_name`, nhưng mỗi nghiên cứu nằm trên một khoảng
`block_id` liền nhau: lấy từ vựng thuốc và dòng tế bào ở giữa nghiên cứu rồi nới ra đoạn liên tục
dài nhất chỉ dùng từ vựng đó, ALMANAC hiện ra ở **block 132.369–432.467**, đúng 300.099 khối tổ
hợp, 60 dòng NCI-60, 102 thuốc, không lẫn một khối đơn trị nào.

Số còn lại sau khi ánh xạ:

| Bước | Giữ lại | Mất | Lý do |
|---|---|---|---|
| khối tổ hợp có `css` | 300.099 | 0 | |
| dòng tế bào có biểu hiện DepMap | 49/60 | 11 dòng | 10 dòng có trong DepMap nhưng chưa có RNA-seq; NCI/ADR-RES không có trong DepMap |
| thuốc phân giải được cấu trúc | 101/102 | CISPLATINO | xem 8.2 |
| **bộ ba cuối** | **234.333** | | 4.934 cặp thuốc, 11 loại mô |

Phân bố nhãn khác hẳn O'Neil, và đây là điều phải đọc trước mọi con số mô hình:

| | đối kháng | cộng tính | hiệp đồng |
|---|---|---|---|
| O'Neil (18.870 bộ ba) | 23,3% | 70,0% | 6,7% |
| ALMANAC (234.333 bộ ba) | 32,1% | 66,4% | **1,5%** |

Một bộ ba ALMANAC là **một khối duy nhất** (trung vị 1 lần lặp), còn O'Neil có trung vị 4 lần
lặp. Nhãn ngoài vì thế là một phép đo đơn lẻ, không có IQR để lọc.

### 8.2 Platinum: một lỗi cũ trong chính dữ liệu huấn luyện

Bộ phân giải ALMANAC có một kiểm tra tự động: cảnh báo khi dạng chuẩn hóa mất hơn 40% nguyên tử
nặng. Cisplatin rơi từ 5 nguyên tử xuống **1**. Nguyên nhân là `rdMolStandardize.Cleanup` có
MetalDisconnector, nó cắt liên kết kim loại–ligand, rồi bước "giữ mảnh lớn nhất" giữ lại mảnh hữu
cơ. Truy lại `data/processed/smiles.csv` thì **carboplatin và oxaliplatin trong tập huấn luyện đã
mất platinum từ đầu**: carboplatin là axit cyclobutane-1,1-dicarboxylic (10 nguyên tử),
oxaliplatin là 1,2-diaminocyclohexane (8 nguyên tử). Không một nguyên tử Pt nào có trong 36 đồ thị
phân tử, dù cột đặc trưng cho Pt vẫn tồn tại. Hai thuốc này nằm trong 814 bộ ba mỗi thuốc, tức
3,8% bảng mỗi thuốc.

Cisplatin không có ligand hữu cơ nào để giữ lại, nên nó bị **loại khỏi tập ngoài** (4.770 bộ ba)
chứ không được trả lại platinum: cho mô hình một loại nguyên tử nó chưa từng thấy trong huấn
luyện thì tệ hơn. Carboplatin và oxaliplatin ở ALMANAC dùng lại đúng cấu trúc đã mất Pt của tập
huấn luyện, để hai bên nhất quán.

### 8.3 Phân giải SMILES khi ChEMBL sập

Tên thuốc ALMANAC là tên của NCI: tên gốc, tên thương mại, mã NSC, muối, một số CAS và một chuỗi
IUPAC. ChEMBL API, nguồn đã dùng cho 38 thuốc O'Neil, **không dùng được ngày 23/11/2026**:
`molecule.json?pref_name__iexact=` treo quá 60 giây, `molecule/<id>.json` trả HTTP 500. Tức
`src.data.smiles` hôm nay cũng không chạy lại được. PubChem thì bị NCBI chặn ở IP này, và Wikidata
Query Service đang giới hạn một truy vấn mỗi phút vì sự cố. Thứ tự nguồn cuối cùng:

| Tầng | Số thuốc | Ghi chú |
|---|---|---|
| `oneil` (dùng lại cấu trúc huấn luyện) | 18 | 14 trùng tên, 4 qua alias |
| `cactus` (NCI CACTUS resolver) | 73 | 57 trùng tên, 16 qua alias |
| `unichem` / `unichem_curated` | 9 | ChEMBL id qua UniChem, **kiểm bằng công thức phân tử** |
| `alias+manual` | 1 | oxaliplatin, phức platinum |
| `excluded` | 1 | cisplatin |

21 hợp chất ALMANAC là hợp chất O'Neil dưới tên khác (ADM HYDROCHLORIDE là DOXORUBICIN, GEMZAR
(LILLY) là GEMCITABINE), và chúng dùng lại đúng cấu trúc của tập huấn luyện, nên đặc trưng giống
từng byte. Bảy thuốc CACTUS không biết (sirolimus, crizotinib, vemurafenib, vismodegib,
ruxolitinib, nilotinib, cabazitaxel) được tra bằng ChEMBL id qua UniChem; mỗi id bị **ghim theo
công thức phân tử** trong code, và cái ghim đó đã bắt được một id sai: id đầu tiên tôi viết cho
cabazitaxel trả về C17H17N3O2S.ClH thay vì C45H57NO14.

### 8.4 Kết quả zero-shot, 3 lớp

Mỗi dòng là trung bình của các run đã huấn luyện xong, cùng những run dựng nên bảng chính ở §3.
Cột QWK nội bộ là số của chính các run đó trên test nội bộ, để đọc độ sụt trên một dòng.

| Mô hình | Split | n run | QWK ngoài | BACC ngoài | macro F1 | recall ant/add/syn | AUPRC hiệp đồng | QWK nội bộ |
|---|---|---|---|---|---|---|---|---|
| SynGT | leave_combo | 15 | 0,023 ± 0,009 | 0,341 | 0,338 | 0,27/0,72/0,04 | 0,018 | 0,589 |
| SynGT + label smoothing | leave_combo | 15 | 0,032 ± 0,008 | 0,342 | 0,341 | 0,28/0,72/0,02 | 0,019 | 0,627 |
| DeepDDS | leave_combo | 15 | 0,013 ± 0,006 | 0,334 | 0,330 | 0,36/0,60/0,04 | 0,017 | 0,536 |
| DeepSynergy | leave_combo | 15 | 0,017 ± 0,014 | 0,336 | 0,331 | 0,25/0,75/0,01 | 0,014 | 0,605 |
| XGBoost | leave_combo | 15 | 0,016 ± 0,005 | 0,334 | 0,319 | 0,15/0,84/0,01 | 0,015 | - |
| SynGT | random | 10 | 0,025 ± 0,008 | 0,342 | 0,338 | 0,26/0,72/0,04 | 0,018 | 0,628 |

n = 234.333 bộ ba. Tỷ lệ cơ sở của lớp hiệp đồng là 0,015.

Chia theo phần chồng lấn với O'Neil (SynGT, leave_combo, 15 run):

| Tập con | n bộ ba | QWK | BACC | recall hiệp đồng |
|---|---|---|---|---|
| toàn bộ | 234.333 | 0,023 ± 0,009 | 0,341 | 0,04 |
| cặp thuốc chưa thấy | 228.126 | 0,020 ± 0,010 | 0,340 | 0,04 |
| dòng tế bào chưa thấy | 190.783 | 0,019 ± 0,009 | 0,339 | 0,04 |
| cả cặp và dòng đều chưa thấy | 185.739 | 0,017 ± 0,010 | 0,338 | 0,04 |
| hóa học mới | 224.470 | 0,016 ± 0,010 | 0,339 | 0,04 |
| hai nghiên cứu cùng đo | 1.163 | 0,147 ± 0,016 | 0,406 | 0,12 |

### 8.5 Đối chứng đường ống: cùng một dự đoán, hai nhãn

1.163 bộ ba ALMANAC là cùng thí nghiệm với một bộ ba O'Neil (cùng cặp InChIKey, cùng dòng DepMap).
Cùng một vector dự đoán được chấm hai lần, một lần theo nhãn O'Neil, một lần theo nhãn ALMANAC.

| Mô hình | Tập con | n | QWK chấm theo nhãn O'Neil | QWK chấm theo nhãn ALMANAC |
|---|---|---|---|---|
| SynGT (leave_combo) | hai nghiên cứu cùng đo | 1.163 | 0,807 ± 0,038 | 0,147 ± 0,016 |
| SynGT + label smoothing (leave_combo) | hai nghiên cứu cùng đo | 1.163 | 0,799 ± 0,033 | 0,148 ± 0,018 |
| DeepDDS (leave_combo) | hai nghiên cứu cùng đo | 1.163 | 0,673 ± 0,045 | 0,151 ± 0,010 |
| DeepSynergy (leave_combo) | hai nghiên cứu cùng đo | 1.163 | 0,829 ± 0,030 | 0,140 ± 0,017 |
| XGBoost (leave_combo) | hai nghiên cứu cùng đo | 1.163 | 0,767 ± 0,020 | 0,123 ± 0,015 |
| SynGT (random) | hai nghiên cứu cùng đo | 1.163 | 0,836 ± 0,017 | 0,161 ± 0,017 |

Tách tiếp theo việc dòng O'Neil tương ứng nằm ở tập huấn luyện hay tập giữ lại của chính run đó:

| Mô hình | Split | Nhóm | n | QWK theo nhãn O'Neil | QWK theo nhãn ALMANAC |
|---|---|---|---|---|---|
| SynGT | leave_combo | dòng O'Neil bị giữ lại | 424 | 0,561 ± 0,038 | 0,139 ± 0,033 |
| SynGT | leave_combo | dòng O'Neil nằm trong tập huấn luyện | 739 | 0,967 ± 0,037 | 0,149 ± 0,025 |
| SynGT | random | dòng O'Neil bị giữ lại | 467 | 0,631 ± 0,031 | 0,175 ± 0,037 |
| SynGT | random | dòng O'Neil nằm trong tập huấn luyện | 696 | 0,971 ± 0,029 | 0,152 ± 0,031 |
| SynGT + label smoothing | leave_combo | dòng O'Neil bị giữ lại | 424 | 0,625 ± 0,039 | 0,136 ± 0,032 |
| SynGT + label smoothing | leave_combo | dòng O'Neil nằm trong tập huấn luyện | 739 | 0,909 ± 0,036 | 0,152 ± 0,024 |
| DeepDDS | leave_combo | dòng O'Neil bị giữ lại | 424 | 0,481 ± 0,038 | 0,139 ± 0,036 |
| DeepDDS | leave_combo | dòng O'Neil nằm trong tập huấn luyện | 739 | 0,800 ± 0,066 | 0,155 ± 0,025 |
| DeepSynergy | leave_combo | dòng O'Neil bị giữ lại | 424 | 0,605 ± 0,048 | 0,120 ± 0,020 |
| DeepSynergy | leave_combo | dòng O'Neil nằm trong tập huấn luyện | 739 | 0,974 ± 0,033 | 0,150 ± 0,028 |
| XGBoost | leave_combo | dòng O'Neil bị giữ lại | 424 | 0,489 ± 0,020 | 0,086 ± 0,029 |
| XGBoost | leave_combo | dòng O'Neil nằm trong tập huấn luyện | 739 | 0,937 ± 0,021 | 0,143 ± 0,024 |

### 8.6 Trần của bài kiểm chứng: hai nghiên cứu có đồng ý với nhau không

| Điểm synergy | n | Cùng lớp | QWK giữa hai bộ dữ liệu | kappa | đối kháng O'Neil còn là đối kháng | hiệp đồng O'Neil còn là hiệp đồng |
|---|---|---|---|---|---|---|
| Loewe (nhãn đang dùng) | 1.163 | 0,571 | 0,149 | 0,135 | 280 → 165 (0,589) | 42 → 1 (0,024) |
| Bliss | 1.163 | 0,696 | 0,065 | 0,018 | 280 → 10 (0,036) | 42 → 5 (0,119) |
| ZIP | 1.163 | 0,698 | 0,010 | 0,002 | 280 → 6 (0,021) | 42 → 2 (0,048) |
| HSA | 1.163 | 0,705 | 0,076 | 0,041 | 280 → 19 (0,068) | 42 → 2 (0,048) |
| Loewe, chỉ 1/4 dòng O'Neil có IQR lặp chặt nhất | 291 | 0,533 | 0,102 | 0,090 | - | - |

Trên cùng 1.163 thí nghiệm đó, Loewe của hai nghiên cứu tương quan Pearson 0,208, Spearman 0,221; trung bình -7,12 ở O'Neil và -13,99 ở ALMANAC. ALMANAC gọi 515 dòng là đối kháng còn O'Neil gọi 280, và chỉ 9 dòng là hiệp đồng còn O'Neil gọi 42.

### 8.7 Có phải chỉ là lệch phân phối đầu vào?

| fold | n dòng huấn luyện | khoảng cách tới dòng O'Neil giữ lại | tới dòng ALMANAC | z-sd O'Neil | z-sd ALMANAC |
|---|---|---|---|---|---|
| 0 | 21 | 36,21 | 36,70 | 1,071 | 1,206 |
| 1 | 22 | 36,19 | 36,43 | 1,087 | 1,196 |
| 2 | 23 | 35,45 | 36,44 | 1,120 | 1,217 |
| 3 | 23 | 33,63 | 36,44 | 1,095 | 1,219 |
| 4 | 22 | 36,46 | 34,97 | 1,077 | 1,187 |

| So sánh | n thuốc | Tanimoto lớn nhất (trung vị) | q25 | q75 | dưới 0,4 | từ 0,9 |
|---|---|---|---|---|---|---|
| thuốc ALMANAC so với thuốc huấn luyện | 101 | 0,222 | 0,169 | 0,867 | 0,653 | 0,218 |
| thuốc O'Neil so với 35 thuốc O'Neil còn lại | 36 | 0,191 | 0,162 | 0,261 | 0,889 | 0,000 |

### 8.8 Câu hỏi nhẹ hơn nhãn 3 lớp: mô hình có xếp hạng được ALMANAC không?

| Mô hình | Split | n run | Spearman với Loewe ALMANAC (toàn bộ) | trên 1.163 dòng chồng lấn: với Loewe O'Neil | với Loewe ALMANAC |
|---|---|---|---|---|---|
| SynGT | leave_combo | 15 | 0,058 ± 0,014 | 0,733 ± 0,016 | 0,193 ± 0,013 |
| SynGT + label smoothing | leave_combo | 15 | 0,073 ± 0,010 | 0,860 ± 0,019 | 0,225 ± 0,012 |
| DeepDDS | leave_combo | 15 | 0,033 ± 0,006 | 0,685 ± 0,022 | 0,207 ± 0,012 |
| DeepSynergy | leave_combo | 15 | 0,029 ± 0,023 | 0,739 ± 0,011 | 0,196 ± 0,014 |
| XGBoost | leave_combo | 15 | 0,072 ± 0,008 | 0,722 ± 0,010 | 0,175 ± 0,015 |
| SynGT | random | 10 | 0,059 ± 0,011 | 0,756 ± 0,008 | 0,219 ± 0,025 |

### 8.9 Giao thức nhị phân của DTSyn trên ALMANAC

DTSyn công bố BACC 0,57 khi chuyển từ O'Neil sang ALMANAC ở bài toán nhị phân bỏ vùng 0–10.
Đây là cùng giao thức đó, cùng ngưỡng, cùng split random.

| Mô hình | Tập con | n | AUROC | AUPRC | BACC | TPR | AUPRC nội bộ |
|---|---|---|---|---|---|---|---|
| SynGT | toàn bộ | 186.704 | 0,567 ± 0,023 | 0,025 ± 0,002 | 0,529 ± 0,015 | 0,128 | 0,732 |
| SynGT | cả cặp và dòng đều chưa thấy | 147.494 | 0,569 ± 0,026 | 0,026 ± 0,003 | 0,528 ± 0,016 | 0,123 | 0,732 |
| SynGT | hai nghiên cứu cùng đo | 991 | 0,630 ± 0,035 | 0,028 ± 0,009 | 0,592 ± 0,046 | 0,281 | 0,732 |
| DeepDDS | toàn bộ | 186.704 | 0,562 ± 0,020 | 0,021 ± 0,001 | 0,500 ± 0,005 | 0,076 | 0,754 |
| DeepDDS | cả cặp và dòng đều chưa thấy | 147.494 | 0,567 ± 0,022 | 0,022 ± 0,001 | 0,497 ± 0,005 | 0,070 | 0,754 |
| DeepDDS | hai nghiên cứu cùng đo | 991 | 0,640 ± 0,033 | 0,024 ± 0,008 | 0,576 ± 0,047 | 0,252 | 0,754 |

### 8.10 Đọc ra gì từ các bảng trên

Zero-shot sang ALMANAC, cả năm mô hình rơi về QWK 0,013–0,032, trong khi test nội bộ của đúng các
run đó là 0,536–0,628. Recall lớp hiệp đồng là 0,01–0,04, AUPRC hiệp đồng 0,014–0,019 trên tỷ lệ
cơ sở 0,015, tức không hơn bốc thăm. Đây không phải chuyện riêng của SynGT: XGBoost trên
fingerprint và DeepSynergy trên vector nối cũng rơi về cùng một mức, và thứ tự giữa các mô hình ở
bảng chính không còn nhìn thấy được ở đây.

Ba cách giải thích thường gặp đều không đứng được với số liệu:

1. **Lệch phân phối đầu vào.** Khoảng cách biểu hiện từ các dòng huấn luyện tới 49 dòng ALMANAC là
   34,97–36,70, còn tới các dòng O'Neil bị giữ lại là 33,63–36,46. Cùng một khoảng. Về phía hóa
   học, Tanimoto lớn nhất tới thuốc huấn luyện có trung vị 0,222 cho thuốc ALMANAC, còn thuốc
   O'Neil so với 35 thuốc O'Neil còn lại chỉ 0,191: thuốc ngoài **gần** tập huấn luyện hơn chính
   thuốc trong tập huấn luyện gần nhau. 22% thuốc ALMANAC có Tanimoto từ 0,9 (21 trong số đó là
   hợp chất O'Neil dưới tên khác).
2. **Đường ống chấm điểm sai.** Trên 424 bộ ba mà dòng O'Neil tương ứng **bị giữ lại** khỏi tập
   huấn luyện của chính run đó, cùng một vector dự đoán cho QWK 0,561 khi chấm theo nhãn O'Neil và
   0,139 khi chấm theo nhãn ALMANAC. Cùng thí nghiệm, cùng dự đoán, cùng mã chấm điểm, hai nhãn.
   Nếu featurization, chỉ số thuốc, buffer fingerprint hay scaler biểu hiện sai thì cột 0,561
   không thể có.
3. **Nhiễu đo của O'Neil.** Lấy 1/4 dòng O'Neil có IQR giữa các lần lặp chặt nhất (291 dòng, IQR ≤
   1,32) thì mức đồng thuận giữa hai nghiên cứu **xuống** 0,102 chứ không lên. Bất đồng không nằm
   ở độ ồn của phép lặp bên O'Neil.

Thứ còn lại là chính cái mục tiêu. Trên 1.163 thí nghiệm mà cả hai nghiên cứu đều chạy, Loewe của
hai bên tương quan Pearson 0,208 và đồng ý lớp 57,1%, QWK 0,149. Trong 42 dòng O'Neil gọi là hiệp
đồng, ALMANAC giữ lại **1**. Số 0,149 đó là trần: không mô hình nào, dù hoàn hảo trên nhãn O'Neil,
có thể vượt nó khi bị chấm bằng nhãn ALMANAC. Con số mô hình đo được (0,023 trên toàn bộ, 0,147
trên phần chồng lấn) phải đọc cạnh cái trần đó, không đọc cạnh 0,589.

Ở câu hỏi nhẹ hơn, chỉ xếp hạng chứ không gán lớp, mô hình vẫn có tín hiệu nhỏ và dương:
Spearman 0,058 với Loewe ALMANAC trên toàn bộ, 0,193 trên phần chồng lấn. Cùng các dòng đó, tương
quan với Loewe **của O'Neil** là 0,733. Tỷ số 0,193 so với 0,733 là một cách khác để viết ra cùng
một trần.

Ở giao thức nhị phân của DTSyn, nơi có một số công bố để so trực tiếp, SynGT đạt BACC 0,529 ±
0,015 và AUROC 0,567 ± 0,023 trên ALMANAC, DeepDDS đạt BACC 0,500 và AUROC 0,562. DTSyn tự báo
BACC 0,57 cho đúng phép chuyển này. Nghĩa là con số ngoài đã công bố của dòng mô hình này vốn đã
sát mức ngẫu nhiên, và kết quả ở đây tái lập đúng mức đó chứ không tệ hơn. Đây là chỗ duy nhất
trong §8 có một số bên ngoài để đối chiếu, và nó khớp.

Vậy phát biểu trung thực là: **ALMANAC trong tham số hóa Loewe của DrugComb không dùng được như
một bài kiểm chứng ngoài cho mô hình 3 lớp huấn luyện trên Loewe của O'Neil**, vì hai nghiên cứu
không đồng ý với nhau về chính các thí nghiệm trùng nhau. Kết quả này **không** chứng minh SynGT
tổng quát hóa được, cũng không chứng minh nó không tổng quát hóa được. Nó chỉ ra rằng bài kiểm tra
đã chọn không trả lời được câu hỏi, và chỉ ra chỗ phải sửa: dùng chính ma trận phần trăm tăng
trưởng thô của ALMANAC để tính lại một điểm synergy với cùng định nghĩa, hoặc chuyển sang mục tiêu
hồi quy liên tục rồi báo tương quan thay cho lớp, hoặc chọn một bộ ngoài có giao thức đo gần O'Neil
hơn (ví dụ các nghiên cứu Merck khác trong DrugComb).

## 9. Lỗi đã phát hiện và sửa trong quá trình chạy

| Lỗi | Hậu quả | Cách sửa |
|---|---|---|
| readout chỉ qua CLS | SynGT underfit, QWK 0,460 | readout skip, chọn theo val |
| `log(probs)` bị kẹp ở 1e-7 | gradient bằng 0 với tam nguyên đối kháng chắc chắn; `contrast` sai (−4,1 thay vì −9) | công thức log-sigmoid chính xác; 39 run giải thích chạy lại; bản cũ giữ ở `runs_v1_cls/explain_clamped/` |
| loss expected-cost thuần | luôn đoán additive (QWK 0) | CE + chi phí; bản cũ giữ ở `runs_v1_cls/cost_collapsed/` |
| SMILES hoán vị không hoán vị fingerprint | đối chứng bị rò thông tin hóa học | hoán vị cả hai |
| run dò HP và ablation lọt vào bảng chính | QWK SynGT sai lệch | lọc trong `report.py` |
| ngân sách 80/12 cho baseline, 120/20 cho SynGT | so sánh không công bằng | mọi mô hình 120/20 |

Có 20 test đơn vị, tất cả đều qua (`src/tests/test_all.py`), gồm: đối xứng A↔B tuyệt đối,
không rò thông tin giữa các split, và `contrast` = logit thứ hai kể cả khi logit cực trị.

## 10. Giới hạn

- O'Neil chỉ có 36 thuốc và 37 dòng tế bào, nên danh tính chi phối. Điều này giải thích việc
  transformer và PPI không đóng góp; nó **không** còn phải giải thích độ ổn định của lời giải
  thích, vì lời giải thích hóa ra là ổn định (§7.4).
- Lời giải thích ổn định với chính mô hình nhưng vẫn không khớp sinh học (§7.5). Đây mới là
  nghịch lý còn lại, và nó khó hơn: không thể quy cho nhiễu giữa các seed được nữa.
- Đợt dò siêu tham số được làm trên readout CLS, trước khi chốt readout skip.
- Nhánh fingerprint không đi qua mặt nạ mảnh BRICS. Phần này được đo riêng (§7.6), nhưng nó
  làm giải thích cấp mảnh yếu đi.
- Chưa có bằng chứng mô hình tổng quát hóa sang một nghiên cứu khác. Bài kiểm chứng ngoài đã chạy
  nhưng trần của nó là QWK 0,149, nên nó không trả lời được câu hỏi (§8.10). Muốn trả lời thì phải
  tính lại điểm synergy từ ma trận tăng trưởng thô của ALMANAC, hoặc đổi sang mục tiêu hồi quy, hoặc
  chọn một nghiên cứu có giao thức đo gần O'Neil hơn.
- Cisplatin bị loại khỏi tập ngoài, và carboplatin với oxaliplatin trong tập huấn luyện đã mất
  nguyên tử platinum từ bước chuẩn hóa SMILES (§8.2). Lỗi này có từ trước, chưa sửa lại tập huấn
  luyện.

## 11. Đề xuất cách viết bài

Không nên viết "mô hình mới tốt nhất". Có ba trục đứng được trên số liệu:

1. **RQ1 (mạnh nhất):** giao thức bỏ vùng trung tính thổi phồng AUROC khoảng 0,055 và AUPRC
   khoảng 0,25 ở mọi mô hình. Đề xuất bài toán 3 lớp có thứ tự, kèm QWK và tỷ lệ nhầm cực.
2. **Đối kháng có lời giải thích riêng (RQ3):** chỉ hỏi được khi có 3 lớp; trực giao với lời
   giải thích cho hiệp đồng.
3. **Trung thực ≠ có nghĩa sinh học (RQ5):** các giải thích trung thực với mô hình (Fid+
   thắng null ở 97–99%) và tái lập qua seed cũng như qua quy ước nhãn (§7.4), nhưng không có
   enrichment KEGG và 0/8 case study vượt null. Ví dụ của DTSyn không tái lập. Attention
   không trùng với IG. Đây là kết quả phản biện có kiểm soát (null, nhiều seed, khai báo
   trước) mà các bài trước không có, và nghịch lý nằm ở chỗ lời giải thích ổn định mà vẫn
   không chỉ vào pathway nào.

Phù hợp nhất: tạp chí hoặc hội nghị bioinformatics tầm trung, hoặc track về evaluation và
reproducibility.
