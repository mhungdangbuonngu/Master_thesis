# SynGT: làm gì, làm thế nào, và cái gì không chạy

Ghi lại ngày 22/11/2026. Số liệu lấy từ 828 run trong `runs/` và các bảng trong `reports/tables/`.

## Mô hình thua một bảng tra cứu

Giữa dự án có một kết quả làm tôi phải dừng lại. Baseline one-hot, tức là mô hình chỉ biết
"thuốc số 7 + thuốc số 22 trên dòng tế bào số 13" mà không biết gì về hóa học hay sinh học,
đạt QWK 0,573. SynGT lúc đó được 0,460.

Một mạng 4 triệu tham số đọc đồ thị phân tử và 944 gen, thua một bảng tra danh tính.

Chuyện này đáng kể lại trước, vì nó định hình phần còn lại. Nó không phải lỗi dữ liệu (tôi đã
kiểm, mục dưới). Nó là lỗi kiến trúc: bản đầu bắt mọi thông tin chen qua hai token CLS, nên mô
hình underfit. Train loss của nó là 0,279 trong khi DeepSynergy xuống tới 0,063. Sửa bằng cách
cho ba khối đi thẳng vào readout, QWK lên 0,589. Thêm label smoothing ở ngưỡng, lên 0,627.

Nhưng one-hot ở 0,573 vẫn là một con số phải nhìn thẳng. Nó nói rằng trên bộ dữ liệu này,
danh tính thuốc và danh tính tế bào đã giải thích được phần lớn câu trả lời.

## Dữ liệu: lấy ở đâu, làm gì với nó

Nguồn là **DrugComb v1.4** (Zenodo 11102665), lấy phần **O'Neil 2016**. Đây là bộ sàng lọc
oncology lớn nhất còn công khai cả ma trận liều.

Có một chỗ khó ngay từ đầu. DrugComb v1.4 **không có cột `study_name`**, nên không có cách nào
lọc ra O'Neil bằng một dòng lệnh sạch sẽ. Cách duy nhất là dựa vào `block_id`: O'Neil là study
đầu tiên trong file, block 1 tới 92208, sau đó là study KBM-7.

Giả định này tôi không yên tâm, nên kiểm lại bằng cách đếm:

| Đếm từ dữ liệu | Được | O'Neil 2016 công bố |
|---|---|---|
| Số cặp thuốc | 583 | 583 |
| Số thuốc | 38 | 38 |
| Số dòng tế bào | 39 | 39 |

Con số 583 khớp tuyệt đối. Nếu ranh giới block sai, gần như chắc chắn nó sẽ lệch. Thêm nữa, mỗi
cặp thuốc có đúng 37 dòng tế bào sau khi lọc, min bằng median bằng max, tức lưới hoàn toàn cân
bằng, chuyện sẽ không xảy ra nếu lẫn sang study khác.

Từ 92208 block xuống 18870 bộ ba, đường đi như sau.

**Gộp bản lặp.** Mỗi bộ ba xuất hiện dưới nhiều block: bản lặp thí nghiệm, và cả hai thứ tự
thuốc. Trung vị 4 block một bộ ba. Tôi chuẩn hóa thứ tự cặp bằng min/max theo tên **trước khi**
gộp, nên (A,B) và (B,A) rơi vào cùng một hàng, rồi lấy **median** của từng điểm synergy. Kết quả:
0 bộ ba trùng, 0 cặp tự thân. Tôi giữ lại cả `n_replicates` và khoảng tứ phân vị của điểm Loewe,
vì sau này cần đến (mục label smoothing).

**Dòng tế bào.** 39 dòng trong DrugComb, ánh xạ sang DepMap qua một bảng tự tra tay
(`src/data/cell_line_map.csv`). 35 khớp chính xác, 2 khớp dòng chị em (COLO320DM dùng COLO-320,
EFM192B dùng EFM-192A, vì DepMap không có bản DM và bản B), 2 bị loại. Một trong hai cái bị loại
đáng nói: UWB1289+BRCA1 là dòng UWB1.289 đã được phục hồi BRCA1. Tái dùng biểu hiện của UWB1.289
cho nó thì nhanh, nhưng sẽ tạo ra hai dòng tế bào có đầu vào y hệt nhau và nhãn khác nhau, nên
tôi bỏ nó.

**Thuốc.** 38 thuốc, tra SMILES qua ChEMBL, 34 tra được bằng ID, 2 phải tra tay, 2 không có cấu
trúc công khai (MK-4541 và MRK-003) nên bị loại. Mất 12,5% bộ ba vì chuyện này, và tôi có kiểm
xem nó có làm lệch nhãn không: phần bị loại có tỉ lệ ant/add/syn là 25,2/69,6/5,2 so với phần giữ
lại 23,3/70,0/6,7. Lệch nhẹ, không đủ để lo.

**Biểu hiện gen.** 978 gen landmark của L1000, lấy log2(TPM+1) từ DepMap, còn 944 gen có dữ liệu.
Z-score fit **chỉ trên các dòng tế bào trong tập train** của từng fold.

**Mạng PPI.** STRING ở ngưỡng confidence 700, 16.201 nút, 236.930 cạnh. Chạy node2vec 128 chiều
trên đó để mỗi gen có một vector. 911 trong 944 gen tìm được vector, 33 gen còn lại nhận vector 0.
Tôi cũng làm sẵn một bản **xáo mạng nhưng giữ nguyên bậc từng nút**, để sau này trả lời được câu
hỏi: mạng PPI thật có hơn một mạng giả cùng phân bố bậc không.

**Nhãn.** Bốn điểm synergy (Loewe, Bliss, ZIP, HSA), ba ngưỡng (±5, ±10, ±20), ba cách gán nhãn.
Mặc định là Loewe ±10 cho ba lớp: 4.391 đối kháng, 13.207 cộng tính, 1.272 hiệp đồng.

### Chia dữ liệu

Năm kiểu, vì mỗi kiểu hỏi một câu khác nhau:

| Kiểu | Giữ lại cái gì | Câu hỏi nó trả lời |
|---|---|---|
| random | bộ ba ngẫu nhiên | gần như không hỏi gì, xem bên dưới |
| leave_combo | cặp thuốc | cặp mới, hai thuốc đã biết |
| leave_drug | thuốc | thuốc hoàn toàn mới |
| leave_cell | dòng tế bào | bệnh nhân mới |
| leave_tumor | cả loại mô | loại ung thư mới |

Tôi kiểm rò rỉ trên cả 27 fold: 0 chồng hàng giữa train/val/test, phủ đủ 18.870 bộ ba, 0 trùng.
Và kiểm ở mức đơn vị chứ không chỉ mức hàng. `leave_drug` có **0 bộ ba test mà cả hai thuốc đều
đã thấy trong train**, tức là bản nghiêm chứ không phải bản dễ. `leave_combo` thì ngược lại,
3.774 trên 3.774 bộ ba test có cả hai thuốc đã biết nhưng cặp thì chưa.

Validation luôn chia theo cùng đơn vị với split ngoài. Nếu test giữ lại dòng tế bào thì val cũng
phải giữ lại dòng tế bào, không thì việc chọn epoch đã mượn thông tin.

Về split random: tôi vẫn chạy nó vì các bài báo đều báo số trên đó, nhưng nó không phân biệt được
mô hình nào với mô hình nào. One-hot đạt ROC-AUC 0,957 trên random, ngang DeepSynergy 0,958. Mọi
con số dùng để so sánh trong luận văn đều lấy từ leave_combo trở đi.

## Đưa vào mô hình như thế nào

Một bộ ba đi qua bốn đường song song.

Hai thuốc thành **đồ thị phân tử**: nguyên tử là nút, liên kết là cạnh, mỗi nguyên tử mang vector
78 chiều one-hot (ký hiệu nguyên tố 44, bậc 11, số H 11, hóa trị ẩn 11, tính thơm 1). Đây đúng
vector của GraphDRP và DeepDDS, chọn giống để nhánh thuốc so được trực tiếp với các bài đó.

Hai thuốc cũng thành **fingerprint Morgan** bán kính 2, 2048 bit, đi theo một nhánh riêng không
qua đồ thị.

Dòng tế bào thành **944 token gen**, mỗi token là node2vec 128 chiều ghép với một giá trị biểu
hiện. Cách ghép này tách bạch "gen này là gen gì" (không đổi giữa các tế bào) với "gen này đang
bật mạnh hay yếu ở đây" (đổi theo từng bộ ba).

Dòng tế bào cũng thành **một vector tế bào** qua một MLP nén 944 chiều xuống 256.

## Mô hình xây những gì

SynGT, 4.161.156 tham số. Sơ đồ chi tiết ở `reports/figures/syngt_architecture.png`, giải thích
từng lớp ở `reports/kien_truc_syngt.md`. Ở đây chỉ nói ý.

**GIN 2 lớp** trên đồ thị phân tử, ra một token cho mỗi nguyên tử. Chọn GIN vì nó dùng phép tổng
nên phân biệt được cấu trúc mà GCN gộp lại. Thực nghiệm sau đó cho thấy GCN và GIN bằng nhau
(0,589 cả hai), nên lý do lý thuyết này không được dữ liệu ủng hộ.

**Transformer mịn** 2 lớp 4 đầu, chạy trên chuỗi `[CLS | nguyên tử A | nguyên tử B | 944 gen]`,
tối đa 1083 token. Ý tưởng là cho một nhóm nguyên tử cụ thể nhìn thấy một gen cụ thể.

**Transformer thô** 2 lớp, chạy trên 4 token `[CLS | thuốc A | thuốc B | tế bào]`. Ý tưởng là mô
hình tương tác ở mức cả phân tử với cả phân tử.

**Readout** nối 5 khối: hai CLS, cộng `p_A + p_B`, `|p_A − p_B|` và vector tế bào. Ba khối sau
lấy từ DeepDDS.

**Đầu CORN** ra 2 logit có điều kiện, từ đó suy ra xác suất ba lớp sao cho thứ tự ant < add < syn
không bao giờ bị vi phạm.

Có một tính chất tôi cố ý ép vào: **không chỗ nào trong mô hình phân biệt thuốc A với thuốc B**.
Nguyên tử của A và B dùng chung một type embedding, p_A và p_B cũng vậy, và hai khối readout thêm
vào đều đối xứng (tổng, và trị tuyệt đối của hiệu). Nên f(A,B,c) = f(B,A,c) đúng theo cấu trúc,
không phải nhờ augmentation. DTSyn chỉ kiểm chuyện này bằng thực nghiệm.

### Các baseline

Bảy cái, từ ngớ ngẩn tới mạnh: đoán lớp đa số, chỉ dùng tế bào, chỉ dùng thuốc, one-hot danh tính,
XGBoost trên fingerprint cộng biểu hiện, DeepSynergy, DeepDDS.

Trước khi tin bất cứ con số nào của SynGT, tôi đặt một chặn: **phải tái lập được số đã công bố
của baseline trước đã**. Kết quả trên split random, ROC-AUC nhị phân: DeepDDS 0,945 (bài báo ~0,93),
DeepSynergy 0,958 (bài báo 0,90). Qua chặn.

Chi tiết này quan trọng hơn vẻ ngoài của nó. Nếu pipeline có lỗi ngầm, baseline sẽ ra số thấp hơn
công bố, và tôi sẽ không biết lỗi nằm ở pipeline hay ở mô hình của mình.

## XAI hỏi gì, và trả lời được tới đâu

Phương pháp chính là Integrated Gradients, trên ba loại đơn vị: 944 gen, các mảnh BRICS của phân
tử, và nhánh fingerprint. Ba mục tiêu quy gán: `z_syn`, `z_syn − z_add` (nghiêng về hiệp đồng
bao nhiêu), `z_ant − z_add` (nghiêng về đối kháng bao nhiêu).

Tôi tách ba câu hỏi mà tài liệu XAI hay trộn vào nhau, mỗi câu có đối chứng ngẫu nhiên riêng.

**Trung thực với mô hình.** Xóa các đơn vị được xếp hạng cao có làm dự đoán đổi nhiều hơn xóa
ngẫu nhiên không? **Có, rõ ràng.** Tỉ lệ thắng đối chứng 97 tới 99% tùy loại đơn vị. Sai số
completeness của IG dưới 1,4% với gen và dưới 0,6% với mảnh.

**Ổn định.** Huấn luyện lại với seed khác thì lời giải thích có giống không? **Có.** Jaccard của
top 50 gen giữa ba seed là 0,190 tới 0,279, đối chứng 0,026 tới 0,033. Cosine của vector quy gán
944 chiều là 0,473 tới 0,593, đối chứng quanh 0. Cả sáu tổ hợp lớp và mục tiêu đều vượt đối
chứng, trên đúng 40 bộ ba dùng chung.

Tôi để nguyên đoạn này dài hơn cần thiết vì cho tới ngày 23/11 tôi vẫn tin điều ngược lại. Bản
trước của bảng cho Jaccard 0,032 tới 0,044 với đối chứng 0,027 tới 0,040, và tôi đã viết vào
báo cáo rằng lời giải thích cấp gen không tái lập được khi đổi seed. Tôi còn dựng cả một giả
thuyết cho nó: 37 dòng tế bào mà 944 gen thì tập gen nào cũng đủ nhận ra dòng tế bào, nên mỗi
seed chọn một tập. Giả thuyết nghe hợp lý, và nó giải thích một hiện tượng không tồn tại. Nguyên
nhân thật nằm ở mục dưới, chỗ `hash(split)`.

**Hợp lý về sinh học.** Các gen được chọn có tụm vào pathway KEGG nào không? **Gần như không**:
0,2 tới 0,3% số bộ ba có enrichment, trung bình 0,08 gen trúng. Tám case study tôi khai báo trước
khi chạy, không cái nào vượt đối chứng. Năm gen mà DTSyn công bố cho cặp ETOPOSIDE + MK-2206 xếp
hạng 163 tới 917 trên 944 trong kết quả của tôi.

Ngoài ba câu đó, có vài thứ đo được mà tôi không định trước:

Nhánh fingerprint mang **51 tới 55%** quyết định, và chiếm ưu thế ở 65 tới 76% số bộ ba. Nghĩa là
giải thích theo mảnh cấu trúc chỉ kể được nửa câu chuyện. Tôi báo con số này thay vì bỏ nhánh
fingerprint đi, vì bỏ nó thì QWK rơi từ 0,589 xuống 0,565.

Attention gần như không trùng với IG, Jaccard 0,041 tới 0,051. Ai coi trọng số attention là lời
giải thích thì nên xem lại. Con số này không bị ảnh hưởng bởi lỗi chọn bộ ba, vì nó so attention
với IG trong cùng một run, trên cùng những bộ ba.

Giải thích cho đối kháng gần **trực giao** với giải thích cho hiệp đồng, tương quan 0,08 tới 0,10.
Không phải cùng một câu trả lời đảo dấu. Đây là câu hỏi mà mô hình nhị phân không đặt ra được, và
là lý do chính để làm bài toán ba lớp.

Tương tác bậc hai giữa các cặp mảnh chỉ bằng 2 tới 4% hiệu ứng bậc một. Mô hình gần như cộng tính
theo mảnh.

## Kết quả

QWK ba lớp, điểm Loewe, ngưỡng ±10:

| Mô hình | leave_combo | leave_drug | leave_cell | leave_tumor |
|---|---|---|---|---|
| SynGT + label smoothing | **0,627** | 0,214 | 0,489 | 0,474 |
| DeepSynergy | 0,605 | 0,051 | 0,456 | 0,433 |
| SynGT (CORN thường) | 0,589 | **0,224** | 0,478 | 0,459 |
| one-hot | 0,573 | 0,190 | 0,478 | 0,460 |
| XGBoost | 0,546 | 0,194 | **0,504** | **0,489** |
| DeepDDS | 0,536 | 0,191 | 0,483 | 0,459 |
| chỉ thuốc | 0,409 | | | |
| chỉ tế bào | 0,098 | | | |
| đoán đa số | 0,000 | | | |

Ba chỗ đáng đọc kỹ.

SynGT với label smoothing đứng đầu ở leave_combo, cột quan trọng nhất vì nó là tình huống thực tế
hay gặp nhất (hai thuốc đã biết, chưa ai thử phối hợp).

DeepSynergy rơi từ 0,605 xuống **0,051** khi gặp thuốc mới. Nó thắng ở leave_combo nhờ nhớ danh
tính thuốc, không phải nhờ hiểu hóa học. SynGT giữ được 0,21 tới 0,22 ở đó, cao nhất bảng.

XGBoost thắng ở leave_cell và leave_tumor. Một mô hình cây trên fingerprint cộng biểu hiện, không
đồ thị, không transformer, chạy xong 89 run trong 47 phút.

### Kết quả mạnh nhất không nằm ở bảng trên

Giao thức bỏ vùng trung tính, cái mà DTSyn dùng (chỉ giữ bộ ba có điểm > 10 hoặc < 0, vứt dải
0 tới 10), làm **ROC-AUC tăng 0,054 tới 0,060 và AUPRC tăng 0,21 tới 0,30 ở mọi mô hình và mọi
split**. Vứt đi 35% dữ liệu khó nhất thì con số đẹp lên, và đó là 35% nằm đúng chỗ biên giới nơi
quyết định lâm sàng thực sự khó.

Kèm với nó là một bảng tôi làm sau, không cần train gì cả, chỉ đếm trên dữ liệu:

| Đổi quy ước | Bộ ba đối kháng còn giữ nhãn | Bộ ba hiệp đồng còn giữ | Kappa |
|---|---|---|---|
| Loewe sang Bliss | 12,5% | 56,7% | 0,250 |
| Loewe sang ZIP | 6,0% | 52,5% | 0,194 |
| Loewe sang HSA | 9,7% | 99,2% | 0,262 |
| ±10 sang ±20 | 56,4% | 11,4% | 0,560 |

Bốn điểm synergy phổ biến nhất gần như không đồng ý với nhau về lớp đối kháng. Đây là trần trên
cho mọi thứ: không lời giải thích nào ổn định hơn được chính nhãn mà nó giải thích.

Và chuyện này quay lại giải thích tại sao label smoothing có tác dụng. Khi kiểm dữ liệu tôi đếm
được **10,2% bộ ba có nhiễu giữa các bản lặp vắt qua ngưỡng ±10**, tức lớp của chúng có thể đổi
nếu lấy mẫu lại thí nghiệm. Phạt mô hình toàn phần vì những bộ ba mà bản thân nhãn đã mơ hồ là
phạt sai. Làm mềm nhãn theo khoảng cách tới ngưỡng thì thắng 6 trên 6 cặp fold, trên cả validation
lẫn test.

### Ablation: cái gì thực sự đóng góp

| Bỏ đi | QWK | So với đầy đủ 0,589 |
|---|---|---|
| bỏ cả hai transformer | 0,591 | không đổi |
| GCN thay GIN | 0,589 | không đổi |
| node2vec trên mạng xáo | 0,586 | không đổi |
| bỏ hẳn node2vec | 0,586 | không đổi |
| hoán vị SMILES (giữ danh tính) | 0,574 | giảm 0,015 |
| bỏ nhánh fingerprint | 0,565 | giảm 0,024 |
| readout chỉ CLS | 0,483 | giảm 0,106 |

Bỏ cả hai transformer không làm gì cả. Mạng PPI thật không hơn mạng giả. Hoán vị SMILES, tức phá
sạch hóa học mà giữ nguyên danh tính thuốc, chỉ tốn 0,015.

DTSyn báo rằng bỏ hai transformer làm AUROC của họ rơi từ 0,89 xuống 0,69. Tôi không tái lập được
chuyện đó.

## Những gì đã sai

Vài lỗi đáng ghi lại vì chúng dễ tái phạm.

**Lỗi làm sai toàn bộ XAI trên một lớp.** `class_logits` tính `log P(c)` bằng `log(probs())`,
mà `probs()` kẹp ở 1e-7. Với bộ ba đối kháng rõ ràng (logit `[-12, -9]`), `log P(syn)` bị kẹp
phẳng, gradient bằng 0, và contrast trả về −4,1 thay vì −9. Mọi quy gán trên những bộ ba đó đều
sai. Lỗi lộ ra qua kiểm tra completeness của IG. Sửa bằng log-sigmoid, chạy lại cả 39 run XAI.
Một kết luận tôi đã viết ra trước đó ("mục tiêu logit thua đối chứng trên bộ ba đối kháng") hóa
ra là sản phẩm của lỗi này, và đã bị rút.

**Đối chứng bị rò.** Đối chứng hoán vị SMILES nhằm phá hóa học mà giữ danh tính, nhưng nhánh
fingerprint vẫn tra theo chỉ số thuốc gốc nên hóa học vẫn lọt qua. Phải hoán vị cả `drug_fp` bằng
đúng hoán vị đó.

**Hàm mất mát sụp.** Phiên bản chi phí thuần (expected cost) sụp về luôn đoán cộng tính, QWK
0,000, ma trận nhầm lẫn `[[0,823,0],[0,2733,0],[0,218,0]]`. Đổi thành cross-entropy cộng lambda
nhân chi phí thì ra 0,580.

**So chéo quy ước trên các bộ ba khác nhau.** Khi so độ ổn định của giải thích giữa Loewe và
Bliss, ban đầu mỗi quy ước lấy mẫu bộ ba theo nhãn của chính nó, nên chỉ còn 2 tới 4 bộ ba chung.
Jaccard ra gần đối chứng và tôi suýt kết luận "giải thích không ổn định giữa các quy ước". Tôi
thêm cờ `--ref-setting` để ép mọi quy ước giải thích cùng một tập bộ ba tham chiếu, chạy lại 15
run, thấy con số đảo, và tưởng đã xong. Nó chưa xong, vì cờ đó không hoạt động, lý do ở mục kế
tiếp. Số đúng chỉ có từ 23/11: cả 30 dòng chéo quy ước đều vượt đối chứng, Jaccard 0,077 tới
0,283 so với đối chứng 0,026 tới 0,034, trên đúng 40 bộ ba chung. Kể cả lớp đối kháng, mà bản
trước tôi ghi là "vẫn bằng đối chứng".

**Một dòng gieo số ngẫu nhiên làm sai toàn bộ phần đo độ ổn định.** Hàm chọn bộ ba để giải thích
gieo rng bằng `10_000 + 97 * fold + hash(split) % 1000`. Dòng đó trông như xác định, nhưng Python
thêm muối ngẫu nhiên vào hash của chuỗi theo từng tiến trình khi `PYTHONHASHSEED` không được đặt,
và tôi không đặt nó ở đâu cả. Mỗi lần gọi `run_explain` là một tiến trình riêng, nên mỗi run chọn
một tập bộ ba khác. Ba seed của cùng một fold chung nhau 0 tới 2 bộ ba trên 40.

Bảng độ ổn định vẫn đem chúng ra so, theo vị trí trong danh sách: bản ghi thứ i của seed 0 với
bản ghi thứ i của seed 1, mà hai bản ghi đó là hai bộ ba không liên quan. Chỗ cay đắng nhất là
hàm đối chứng được định nghĩa đúng bằng "ghép các bộ ba khác nhau". Nghĩa là hàm đo và hàm đối
chứng khi đó tính cùng một đại lượng, nên việc chúng bằng nhau không phải phát hiện gì, nó là
điều bắt buộc phải xảy ra.

Tôi tìm ra nó vì đi kiểm lại mục "đã sửa" ngay phía trên và thấy `n_triples` trong bảng chéo quy
ước chỉ có 2 tới 9 chứ không phải 40. Nếu cột đó không được in ra thì tôi vẫn đang tin lời giải
thích của mình không tái lập được.

Sửa: bảng offset cố định thay cho `hash`, khớp lời giải thích theo id bộ ba thay vì theo vị trí,
in `n_triples` vào mọi bảng ổn định, và một test chạy hàm chọn bộ ba trong ba tiến trình con với
`PYTHONHASHSEED` khác nhau rồi đòi ba kết quả giống nhau. Chạy lại 39 run giải thích cộng 15 run
chéo quy ước, hết bốn giờ bốn mươi bảy phút.

**Mốc so sánh là một mô hình ablation.** Bảng chéo quy ước tra mô hình gốc bằng khóa
`(quy ước, kiểu chia, fold, seed)`. Nhưng run chính và ba run ablation `_nofp`, `_nogeneemb`,
`_rewired` có đúng bốn giá trị đó giống nhau, nên cái cuối theo thứ tự chữ cái thắng chỗ. Suốt
thời gian đó, mốc để so không phải SynGT mà là bản node2vec huấn luyện trên mạng STRING đã xáo.

**Một con số tôi đưa ra mà pipeline không hề tính.** Tôi từng báo cosine giữa các seed là 0,436
so với đối chứng 0,092. Trong `src/eval/xai_metrics.py` không có hàm cosine nào. Con số đó tôi
tính tay ở một phiên trước, trên những bộ ba lệch nhau, rồi viết vào tài liệu như thể nó ra từ
bảng. Giờ cosine là một phần của hàm `stability`, và giá trị thật là 0,473 tới 0,593.

**Đối chứng hoán vị SMILES rò lần thứ hai.** Lần đầu là nhánh fingerprint. Lần này là `n_frag`,
số mảnh BRICS của mỗi thuốc, cũng đánh theo chỉ số thuốc và cũng bị hoán vị bỏ sót, và chính nó
được mặt nạ mảnh trong phần XAI đọc. Thêm nữa, phần XAI dựng lại kho phân tử từ dữ liệu gốc, nên
đem một run hoán vị đi giải thích thì mô hình chưa từng thấy hóa học thật mà phân tử đưa vào quy
gán lại là phân tử thật. Chưa run nào bị như vậy, nên đây là bẫy chưa nổ. Giờ cả hoán vị kho phân
tử lẫn hoán vị fingerprint đi qua một hàm duy nhất, và hàm đó `assert` rằng không còn tensor nào
đánh theo chỉ số thuốc bị bỏ lại.

**Ngân sách không đồng đều.** Lúc đầu chặn G1 chạy 120 epoch còn các stage sau chạy 80, nên so
sánh không công bằng. Thống nhất lại 120 epoch, patience 20 cho mọi mô hình.

**Run dò siêu tham số lọt vào bảng chính**, làm QWK của SynGT tụt từ 0,458 xuống 0,416 trong báo
cáo. Lọc bằng regex trên tên run.

**Tôi tự viết vào nhật ký một lý do sai để hoãn kiểm chứng ngoài.** Dòng cũ nói ALMANAC phải
chờ file gốc của NCI "vì DrugComb không lọc được theo study". Tôi dựa vào một điều đúng,
`summary_table_v1.4.csv` thật sự không có cột `study_name`, rồi nhảy sang một kết luận không
kiểm. Mỗi nghiên cứu trong DrugComb nằm trên một khoảng `block_id` liền nhau. Lấy từ vựng thuốc
và dòng tế bào ở giữa nghiên cứu, rồi nới ra đoạn liên tục dài nhất chỉ dùng từ vựng đó, ALMANAC
hiện ra ở block 132.369 tới 432.467: đúng 300.099 khối tổ hợp, 60 dòng NCI-60, 102 thuốc, không
một khối đơn trị nào lẫn vào. Mất mười phút để kiểm. Thiếu sót mà bản trước gọi là "nặng nhất"
nằm đó suốt, trong cùng cái file đã dùng để lấy O'Neil.

**Carboplatin và oxaliplatin trong tập huấn luyện không có platinum.** Bộ phân giải SMILES cho
ALMANAC có thêm một kiểm tra: cảnh báo khi dạng chuẩn hóa mất hơn 40% nguyên tử nặng. Cisplatin
rơi từ 5 nguyên tử xuống 1. Lần theo thì `rdMolStandardize.Cleanup` chứa MetalDisconnector, nó
cắt liên kết kim loại với ligand, rồi bước giữ mảnh lớn nhất bỏ nốt phần kim loại. Mở
`data/processed/smiles.csv` ra xem thì carboplatin đã là axit cyclobutane-1,1-dicarboxylic và
oxaliplatin đã là 1,2-diaminocyclohexane từ ngày dựng dữ liệu. Không nguyên tử Pt nào có trong
36 đồ thị phân tử, dù cột đặc trưng cho Pt vẫn nằm trong 78 chiều. Mỗi thuốc có mặt trong 814 bộ
ba, 3,8% bảng.

Chú thích trong code viết "RDKit parses the dative-free form", nghĩa là lúc đó tôi có kiểm rằng
RDKit đọc được chuỗi SMILES, nhưng không kiểm phân tử sau chuẩn hóa. Hai chuyện khác nhau, và chỗ
sai nằm ở chuyện thứ hai. Tôi không sửa tập huấn luyện: sửa nghĩa là chạy lại 828 run. Tập ngoài
dùng lại đúng cấu trúc đã mất Pt đó cho carboplatin và oxaliplatin để hai bên nhất quán, còn
cisplatin thì bị loại hẳn khỏi tập ngoài, 4.770 bộ ba, vì nó không còn gì hữu cơ để giữ lại.

## Phần kiến thức nền

Phần này dành cho người đọc chưa quen với lĩnh vực, hoặc cho chính tôi sáu tháng nữa.

### Hiệp đồng thuốc là gì

Hai thuốc dùng chung có thể cho hiệu quả lớn hơn tổng hiệu quả riêng lẻ (hiệp đồng), bằng đúng
tổng (cộng tính), hoặc nhỏ hơn (đối kháng). Trong ung thư, phối hợp thuốc là chuẩn điều trị ở
nhiều bệnh, nhưng số cặp có thể thử lớn hơn số thí nghiệm làm được rất nhiều lần, nên người ta
muốn một mô hình xếp hạng trước.

Câu hỏi khó là định nghĩa thế nào là "tổng hiệu quả riêng lẻ". Có bốn câu trả lời phổ biến, và
chúng dựa trên giả định khác nhau:

**Loewe** giả định thuốc tự phối với chính nó thì không sinh hiệp đồng. Nó hỏi: để đạt mức ức chế
này, cần bao nhiêu phần liều của A cộng bao nhiêu phần liều của B, nếu tổng phần nhỏ hơn 1 thì
hiệp đồng. Đây là định nghĩa được dùng nhiều nhất trong dược lý.

**Bliss** giả định hai thuốc tác động độc lập về mặt xác suất. Nếu A giết 30% tế bào và B giết
40%, độc lập thì còn lại 0,7 × 0,6 = 42%, tức giết 58%. Giết nhiều hơn 58% là hiệp đồng.

**HSA** (highest single agent) chỉ hỏi phối hợp có tốt hơn thuốc mạnh hơn trong hai thuốc không.
Đây là mức yêu cầu thấp nhất, nên HSA gán nhãn hiệp đồng rộng tay nhất (17,8% so với Loewe 6,5%).

**ZIP** nội suy giữa Loewe và Bliss, giả định cả hai đường cong liều đáp ứng đều không đổi khi
thêm thuốc kia.

Bốn định nghĩa này không phải bốn cách đo cùng một thứ. Chúng là bốn thứ khác nhau, và bảng khớp
nhãn ở trên cho thấy chúng đồng ý với nhau rất ít ở lớp đối kháng. Phần lớn bài báo chỉ chọn một
và không bàn tới chuyện này.

### Vì sao làm ba lớp có thứ tự

Hầu hết bài báo làm nhị phân: hiệp đồng hay không. Cách đó gộp đối kháng với cộng tính vào một
lớp, trong khi với bác sĩ thì đối kháng là thông tin có giá trị riêng. Kê một cặp thuốc đối kháng
không phải là "không có lợi", nó là có hại.

Ba lớp ant < add < syn **có thứ tự**. Nhầm đối kháng thành hiệp đồng tệ hơn nhầm đối kháng thành
cộng tính. Một softmax ba lớp thường không biết điều đó: với nó ba nhãn là ba thứ rời rạc, và nó
có thể cho ra P(syn) cao trong khi P(add) thấp, một kết quả vô nghĩa về thứ tự.

### CORN

CORN (Cao, Mirjalili, Raschka 2022) biến K lớp có thứ tự thành K − 1 bài toán nhị phân **có điều
kiện**. Với ba lớp:

```
q0 = P(y > ant)                 huấn luyện trên mọi mẫu
q1 = P(y > add | y > ant)       huấn luyện chỉ trên mẫu có y > ant
```

Xác suất lớp lấy bằng tích lũy: `P(ant) = 1 − q0`, `P(add) = q0(1 − q1)`, `P(syn) = q0·q1`. Vì
`q0·q1 ≤ q0` luôn đúng, thứ tự không bao giờ bị vi phạm. Đây là ràng buộc theo cấu trúc, không
phải thứ mô hình phải học.

Có một hệ quả tiện cho XAI: `z_syn − z_add` bằng **đúng** logit điều kiện thứ hai. Nên đại lượng
"bộ ba này nghiêng về hiệp đồng hơn cộng tính bao nhiêu" là một số mà mạng tính ra trực tiếp, quy
gán trên nó rẻ và ít nhiễu hơn so với quy gán trên hiệu của hai logit softmax.

### QWK

Quadratic weighted kappa. Nó phạt lỗi theo bình phương khoảng cách giữa lớp đoán và lớp thật, nên
nhầm ant thành syn (khoảng cách 2) bị phạt gấp 4 lần nhầm ant thành add (khoảng cách 1). Và nó
chuẩn hóa theo mức ngẫu nhiên, nên đoán bừa được 0 bất kể phân bố lớp lệch tới đâu. Với dữ liệu
có 70% là một lớp, đây là tính chất cần thiết: accuracy của mô hình đoán đa số là 70%, QWK của nó
là 0,000.

### GNN và GIN

Mạng nơ-ron đồ thị cập nhật biểu diễn của mỗi nút bằng cách gộp thông tin từ các nút lân cận, lặp
lại vài vòng. Sau hai vòng, một nguyên tử "biết" về các nguyên tử cách nó hai liên kết.

Khác nhau giữa các loại GNN nằm ở phép gộp. GCN dùng trung bình có chuẩn hóa theo bậc. GIN dùng
tổng. Chuyện này không nhỏ: trung bình không phân biệt được một nút có 3 hàng xóm giống hệt nhau
với một nút có 6 hàng xóm giống hệt nhau, còn tổng thì phân biệt được. Về lý thuyết GIN mạnh ngang
phép kiểm đồng cấu Weisfeiler-Lehman, GCN thì yếu hơn.

Trên 36 thuốc thì khác biệt lý thuyết này không hiện ra: GIN và GCN cho cùng 0,589.

### Transformer và attention

Attention cho mỗi token tính một tổng có trọng số trên mọi token khác, trọng số do chính dữ liệu
quyết định. Trong SynGT, nó cho phép một nguyên tử cụ thể "chú ý" tới một gen cụ thể.

Hai điểm kỹ thuật đáng biết. Thứ nhất, attention **bất biến với hoán vị**: đổi thứ tự token không
đổi kết quả, trừ khi ta cộng thêm thông tin vị trí. SynGT lợi dụng tính chất này để ép đối xứng
A↔B, bằng cách không cộng gì phân biệt A với B. Thứ hai, chi phí là bình phương số token. Với 1083
token thì ma trận attention là 1083 × 1083 cho mỗi đầu mỗi mẫu, nên khi huấn luyện mã dùng kernel
hợp nhất không bao giờ tạo ma trận đó trong bộ nhớ, chỉ khi XAI cần trọng số tường minh mới tính
softmax thủ công với batch size 1.

Về attention như lời giải thích: nhiều bài vẽ heatmap attention và gọi đó là giải thích. Kết quả
của tôi cho thấy attention và IG gần như không trùng nhau (Jaccard 0,04 tới 0,05), và chuyện này
khớp với tài liệu đã có (Jain và Wallace 2019, "Attention is not Explanation").

### Integrated Gradients

IG trả lời câu "đặc trưng này đóng góp bao nhiêu vào đầu ra" bằng cách đi một đường thẳng từ một
**baseline** (trạng thái trung tính) tới đầu vào thật, lấy tích phân gradient dọc đường đó.

Tính chất quan trọng của nó là **completeness**: tổng mọi phần quy gán phải bằng đúng hiệu giữa
đầu ra ở đầu vào thật và đầu ra ở baseline. Đây là thứ kiểm được bằng số, và nó chính là cái đã
phát hiện ra lỗi log-sigmoid ở trên. Nếu completeness lệch nhiều thì quy gán sai, không cần tranh
luận gì thêm.

Chọn baseline không hiển nhiên. Với biểu hiện gen đã z-score, baseline đúng là 0, vì 0 nghĩa là
"mức trung bình của tập train", chứ không phải "gen này tắt". Đây là lý do mặt nạ gen trong SynGT
nhân vào biểu hiện chứ không nhân vào token.

### Ba câu hỏi khác nhau về một lời giải thích

Đây là phần tôi nghĩ hay bị trộn nhất trong tài liệu XAI, nên tách riêng:

**Trung thực (faithfulness).** Lời giải thích có phản ánh đúng cái mô hình thực sự làm không?
Đo bằng cách xóa đơn vị được cho là quan trọng rồi xem đầu ra đổi bao nhiêu, so với xóa ngẫu
nhiên. Đây là câu về **mô hình**.

**Hợp lý (plausibility).** Lời giải thích có khớp với kiến thức sinh học đã biết không? Đo bằng
enrichment pathway, hoặc so với gen mà bài báo khác đã chỉ ra. Đây là câu về **thế giới**.

**Ổn định (stability).** Huấn luyện lại thì lời giải thích có giữ nguyên không? Đây là câu về
**quy trình**.

Ba thứ này độc lập với nhau. Một lời giải thích có thể trung thực hoàn toàn mà vẫn vô nghĩa về
sinh học, nếu mô hình học được một đường tắt. Đó đúng là tình huống của SynGT: trung thực 97 tới
99%, enrichment 0,2%.

Mỗi câu cần đối chứng ngẫu nhiên riêng, và tôi để chúng riêng trong báo cáo thay vì gộp thành một
"điểm XAI".

### Các kiểu chia dữ liệu nói lên điều gì

Một mô hình đạt điểm cao trên split ngẫu nhiên có thể chỉ đang nhớ. Nếu cặp (thuốc A, thuốc B)
xuất hiện trên 37 dòng tế bào và 30 dòng nằm trong train, thì đoán 7 dòng còn lại không đòi hỏi
hiểu hóa học.

Đây không phải lo xa. One-hot đạt 0,957 trên split ngẫu nhiên của chúng tôi, ngang DeepSynergy.
Và DeepSynergy rơi từ 0,605 xuống 0,051 khi chuyển sang leave_drug. Khoảng cách giữa hai con số
đó chính là phần mà mô hình đang nhớ chứ không đang hiểu.

## Còn gì chưa làm, và tôi chưa chắc về cái gì

Chưa làm: dò 40 cấu hình siêu tham số như kế hoạch ban đầu thay vì 16, và 5 seed thay vì 3. Phần dò
siêu tham số hiện tại còn làm trên kiến trúc readout cũ, chưa làm lại trên kiến trúc cuối. DTSyn vẫn
chưa được tái lập thành một mô hình riêng.

Kiểm chứng ngoài trên ALMANAC thì đã chạy ngày 23/11, và nó không cho câu trả lời tôi muốn. SynGT
rơi từ QWK 0,589 xuống 0,023. DeepDDS, DeepSynergy và XGBoost cũng rơi xuống 0,013 tới 0,017, nên ít
nhất đây không phải lỗi riêng của kiến trúc tôi dựng. Chỗ làm tôi bớt nghi đường ống của mình là
phép đối chứng: lấy 424 bộ ba mà dòng O'Neil tương ứng bị giữ lại khỏi tập huấn luyện, chấm cùng một
vector dự đoán hai lần, theo nhãn O'Neil được 0,561, theo nhãn ALMANAC được 0,139. Hai nghiên cứu
đang nói hai chuyện khác nhau về cùng một thí nghiệm: trong 42 tổ hợp O'Neil gọi là hiệp đồng,
ALMANAC giữ lại 1.

Chưa chắc: lời giải thích phản ánh đúng những gì mô hình làm, nó ổn định giữa các seed và ổn
định cả khi đổi quy ước nhãn, nhưng tôi không chứng minh được nó đúng với sinh học. Trước ngày
23/11 tôi có một câu chuyện gọn cho việc này: dữ liệu quá nhỏ nên mô hình học danh tính thay vì
cơ chế, và transformer vô dụng, PPI vô dụng, giải thích không ổn định đều là triệu chứng của cùng
một nguyên nhân. Câu chuyện đó mất một chân khi hóa ra giải thích là ổn định.

Thứ còn lại khó hơn. Mô hình quy gán một cách nhất quán, nó nhất quán với chính nó khi đổi seed,
nhất quán khi đổi từ Loewe sang Bliss hay ZIP, và những gen nó chỉ vào vẫn không tụm vào pathway
nào, vẫn không trùng với năm gen DTSyn công bố cho cùng cặp thuốc (hạng 163 tới 917 trên 944).
Một lời giải thích ổn định và sai thì khó bác hơn một lời giải thích nhiễu, vì không quy được cho
nhiễu nữa. Tôi chưa biết đó là giới hạn của bộ dữ liệu, của cách tôi đo tính hợp lý sinh học, hay
của chính việc dùng biểu hiện gen landmark làm đầu vào.

Và một câu hỏi tôi chưa trả lời được: nếu XGBoost trên fingerprint thắng ở hai trên bốn kiểu chia,
thì phần kiến trúc phức tạp đang mua được cái gì, ngoài việc nó cho phép đặt mặt nạ lên từng gen
và từng mảnh phân tử để hỏi câu hỏi XAI? Có thể đó đã là câu trả lời đủ cho một luận văn về XAI.
Có thể không.
