# SynGT — tài liệu chủ: dữ liệu, kiến trúc và XAI

Cập nhật 23/11/2026. File này gộp ba câu hỏi lại một chỗ: dùng dữ liệu nào và dùng vào đâu,
kiến trúc lấy từ bài nào và **vì sao** phải như vậy, XAI dùng gì và về mặt lý thuyết nó trả lời
được câu hỏi gì.

Nguồn số liệu: `reports/ket_qua_syngt.md` (kết quả), `reports/kiem_tra_du_lieu.md` (kiểm tra dữ
liệu), `reports/kien_truc_syngt.md` (kiến trúc), `data/processed/provenance_*.json` (xuất xứ),
code trong `src/`. Mọi con số trong file này đều đã chạy thật, không có số ước lượng.

Bài toán một câu: cho bộ ba (thuốc A, thuốc B, dòng tế bào ung thư), dự đoán cặp thuốc đó là
**đối kháng < cộng tính < hiệp đồng** trên dòng tế bào đó, rồi chỉ ra mô hình dựa vào gen nào và
mảnh phân tử nào để quyết định.

---

# Phần 1. Dữ liệu

## 1.1. Các tập dữ liệu và chỗ dùng của từng tập

| Tập | Nội dung | Kích thước thực tế | Dùng cho phần nào |
|---|---|---|---|
| **O'Neil 2016** qua DrugComb v1.4 | ma trận liều của cặp thuốc trên dòng tế bào ung thư | 18.870 bộ ba · 36 thuốc · 510 cặp · 37 dòng · 7 loại mô | nhãn và toàn bộ huấn luyện, đánh giá, XAI |
| **ChEMBL + DrugBank** | SMILES của thuốc | 36/38 thuốc tra được | nhánh đồ thị phân tử và nhánh fingerprint |
| **L1000 landmark** giao với **DepMap/CCLE** | biểu hiện gen của dòng tế bào, log2(TPM+1) | 944 gen × 37 dòng, 0 giá trị thiếu | token gen và vector tế bào |
| **STRING v12** | mạng tương tác protein, lọc score ≥ 700 | 16.201 nút · 236.930 cạnh | node2vec 128 chiều làm định danh cho từng gen |
| **STRING xáo trộn giữ bậc** | đối chứng âm cho mạng PPI | cùng cỡ | ablation: mạng thật có hơn mạng giả không |
| **KEGG** | nhóm gen theo pathway | — | **chỉ dùng để chấm điểm XAI**, không đưa vào mô hình |
| **Đích thuốc (DrugBank)** | gen mà chính hai thuốc tác động | — | chấm điểm plausibility trong case study |
| **NCI-ALMANAC** (trong DrugComb v1.4, block 132.369–432.467) | bộ tổ hợp thuốc độc lập | 234.333 bộ ba · 101 thuốc · 49 dòng · 4.934 cặp | kiểm chứng ngoài, **đã chạy 23/11/2026**, QWK 0,023 trên trần 0,149 |

Vì sao chỉ O'Neil: đây đúng là bộ mà DTSyn, DeepDDS, AttenSyn và MD-Syn dùng, nên mọi con số
trong bảng so sánh là so được. Mở rộng lên DrugComb đầy đủ (466.033 khối tổ hợp cũng đã có trên
máy) nằm ở phần hướng phát triển, cố ý để ngoài phạm vi.

## 1.2. Đường đi của số lượng mẫu

| Bước | Còn lại |
|---|---|
| Khối tổ hợp O'Neil trong DrugComb v1.4 (`block_id ≤ 92208`) | 92.208 khối |
| Ánh xạ dòng tế bào sang DepMap | 39 → 37 dòng |
| Gộp bản lặp theo trung vị, chuẩn hóa thứ tự cặp trước khi gộp | 21.571 bộ ba, trung vị 4 bản lặp mỗi bộ ba |
| Loại bộ ba không có SMILES công khai | **18.870 bộ ba · 36 thuốc · 510 cặp** |

Hai thuốc bị loại là MK-4541 và MRK-003, mã nội bộ Merck không có cấu trúc công khai. Phần bị
loại gần như không làm lệch phân bố nhãn: ant/add/syn của nó là 25,2/69,6/5,2% so với 23,3/70,0/6,7%
của phần giữ lại.

Bằng chứng mạnh nhất cho việc trích đúng bộ O'Neil: DrugComb v1.4 không có cột `study_name`, nên
phải dựa vào ranh giới `block_id`. Pipeline cho ra **583 cặp thuốc, 38 thuốc, 39 dòng tế bào**,
khớp tuyệt đối với số công bố của O'Neil 2016, và mọi cặp đều có đủ 37 dòng tế bào. Ranh giới sai
thì con số này gần như chắc chắn lệch.

## 1.3. Ba thiết lập nhãn trên cùng một bộ dữ liệu

Đây là thiết kế trung tâm của câu hỏi nghiên cứu thứ nhất, không phải chi tiết kỹ thuật.

| Thiết lập | Quy tắc | Dữ liệu dùng |
|---|---|---|
| `bin_gap` (giao thức DTSyn) | Loewe > 10 dương, < 0 âm, **bỏ vùng 0–10** | 12.223 bộ ba, bỏ 35,2% |
| `bin_all` | > 10 dương, phần còn lại âm | 100% |
| `ord3` (**thiết lập chính**) | > 10 syn, −10…10 add, < −10 ant | 100%, **4.391 ant / 13.207 add / 1.272 syn** |

Lớp hiệp đồng chỉ 6,7%, nên accuracy vô nghĩa ở đây. Chỉ số chính là **QWK** (quadratic weighted
kappa, có tính đến khoảng cách giữa các lớp), phụ là macro-F1, MAE, balanced accuracy và riêng
**tỷ lệ nhầm cực** syn ↔ ant, loại lỗi đắt nhất về mặt sinh học.

Phân tích độ nhạy phủ 4 điểm synergy × 3 ngưỡng. Tỷ lệ dữ liệu mà giao thức DTSyn xóa đi thay đổi
rất mạnh theo điểm: Loewe 35,2% · Bliss 49,7% · ZIP 52,7% · HSA 59,7%.

## 1.4. Năm kiểu chia dữ liệu, mỗi kiểu trả lời một câu khác nhau

| Kiểu chia | Giữ lại cái gì | Câu hỏi nó trả lời |
|---|---|---|
| random (5 fold) | hàng ngẫu nhiên | gần như không trả lời gì, xem bên dưới |
| **leave_combo** (5) | **cặp thuốc** mới, hai thuốc đều đã thấy | cột quan trọng nhất: sàng cặp mới từ thuốc đã biết |
| leave_drug (5) | **thuốc** mới hoàn toàn | mô hình có hiểu hóa học không |
| leave_cell (5) | **dòng tế bào** mới | mô hình có hiểu bối cảnh sinh học không |
| leave_tumor (7) | **loại mô** mới, một fold mỗi mô | tổng quát hóa xa nhất |

Tập validation **luôn chia theo cùng đơn vị với split ngoài**: leave_drug thì validation cũng theo
thuốc. Có test đơn vị cho việc này. Kiểm toán 27 fold: 0 hàng chồng nhau, phủ đủ 18.870/18.870,
0 cặp thuốc trùng giữa train và test ở leave_combo, 0 bộ ba test có cả hai thuốc đã thấy ở
leave_drug.

**Random split không phân biệt được mô hình.** Baseline one-hot, không dùng SMILES, không dùng
biểu hiện gen, đạt ROC-AUC 0,957 trên random split, ngang DeepSynergy 0,958. Khi một cặp thuốc
xuất hiện trên 37 dòng tế bào và 30 dòng nằm trong train, đoán 7 dòng còn lại không đòi hỏi hiểu
hóa học. Vì vậy bảng chính của luận văn dùng leave_combo, và random chỉ xuất hiện ở chặn tái lập.

## 1.5. Hai giới hạn của dữ liệu phải nêu trong luận văn

**Nhiễu nhãn ngay tại ngưỡng.** 2.195 bộ ba, tức **10,2%**, có nửa khoảng IQR giữa các bản lặp
vắt qua ngưỡng ±10: lớp của chúng có thể đổi nếu lấy mẫu lại. IQR ở phân vị 99 là 12,0, lớn hơn
cả ngưỡng. Con số này về sau thành căn cứ cho hàm mất mát label smoothing ở §2.9.

**Quy ước toán học đổi thì bài toán đổi.** Cùng dữ liệu thực nghiệm, chuyển từ Loewe sang Bliss
làm QWK rơi từ 0,589 xuống 0,390. Y văn báo Loewe chỉ tương quan r = 0,28 với ZIP.

---

# Phần 2. Mô hình SynGT: từng lớp, và vì sao lớp đó có mặt

**SynGT** (Synergy Graph-Transformer), 4.161.156 tham số huấn luyện, cộng hai bảng tra đóng băng
(`gene_emb` 944×128, `drug_fp` 36×2048). Code: `src/model/syngt.py`, `src/model/corn.py`.

## 2.0. Trước khi nói lớp nào: ba yêu cầu sinh ra kiến trúc này

Hiệp đồng là thuộc tính của **bộ ba**, không phải của thuốc và cũng không phải của tế bào. Hai đối
chứng tầm thường cho thấy điều đó bằng số: mô hình chỉ dùng thông tin thuốc đạt QWK 0,409, mô hình
chỉ dùng tế bào đạt 0,098. Không nhánh nào tự đứng được, nên kiến trúc buộc phải có ba việc:

1. **Biểu diễn từng thuốc** sao cho tổng quát được sang thuốc chưa thấy. Nếu chỉ cần nội suy trong
   36 thuốc đã biết thì one-hot là đủ, và one-hot đạt 0,573, gần bằng mọi mô hình phức tạp. Phần
   duy nhất mà cấu trúc hóa học thật sự kiếm được là leave_drug: SynGT giữ 0,21–0,22 trong khi
   DeepSynergy tụt từ 0,605 xuống **0,051**. Đó là lý do tồn tại của nhánh thuốc.
2. **Biểu diễn bối cảnh tế bào.** Cùng một cặp thuốc cho nhãn khác nhau trên 37 dòng khác nhau,
   nên một phần biến thiên của nhãn chỉ giải thích được bằng thông tin tế bào.
3. **Một chỗ để hai thứ trên gặp nhau.** Hiệp đồng không phải tổng của hai tác động đơn lẻ, nó là
   phần dôi ra. Mô hình phải có lớp trộn, và vị trí đặt lớp trộn quyết định XAI hỏi được câu gì.

Yêu cầu thứ ba còn kéo theo một ràng buộc mà phần lớn bài báo bỏ qua: **thứ tự hai thuốc không
được ảnh hưởng tới kết quả**. Hiệp đồng là quan hệ đối xứng. SynGT đạt f(A,B,c) = f(B,A,c) **theo
cấu trúc**, không phải nhờ augmentation: điều này quyết định cách gộp token ở §2.5 và cách nối
vector ở §2.7, và có test đơn vị kiểm.

## 2.1. Toàn bộ luồng, kèm hình dạng tensor

Với batch B bộ ba, A_max là số nguyên tử lớn nhất trong batch (số nguyên tử thực 8–69, trung vị 29):

| # | Lớp | Vào | Ra | Tham số |
|---|---|---|---|---|
| 1 | đặc trưng hóa phân tử (không học) | SMILES | `x` (N_atom, 78) · `edge_index` (2, 2E) | 0 |
| 2 | **MolEncoder GIN 2 lớp** | (N_atom, 78) | (N_atom, 256) một token mỗi nguyên tử | 547.074 |
| 3 | **fp_mlp** | fingerprint Morgan (B, 2048) mỗi thuốc | (B, 256) mỗi thuốc | 590.336 |
| 4 | **gene_in** | (B, 944, 129) = node2vec ‖ biểu hiện | (B, 944, 256) 944 token gen | 33.280 |
| 5 | **cell_mlp** | (B, 944) biểu hiện | (B, 256) một vector tế bào | 680.960 |
| 6 | **transformer mịn** 2 lớp 4 đầu | (B, 1 + 2·A_max + 944, 256) | `CLS_f` (B, 256) + ma trận attention | 791.552 |
| 7 | **transformer thô** 2 lớp 4 đầu | (B, 4, 256) | `CLS_c` (B, 256) | 791.552 |
| 8 | **readout skip + MLP** | (B, 1280) | (B, 128) | ~724.000 |
| 9 | **đầu CORN** | (B, 128) | (B, 2) logit lũy tích | 258 |

Chuỗi của transformer mịn dài tối đa 1083 token. Khi huấn luyện, code dùng
`scaled_dot_product_attention` hợp nhất nên **không bao giờ tạo ma trận 1083×1083 trong bộ nhớ**.
Chỉ khi XAI cần trọng số attention tường minh thì mới tính softmax thủ công, lúc đó batch size là 1.

## 2.2. Lớp 1 — đặc trưng hóa, và vì sao chọn hai biểu diễn hóa học thay vì một

### Đồ thị phân tử, đặc trưng nguyên tử 78 chiều

Mỗi phân tử thành một đồ thị: nguyên tử là nút, liên kết là cạnh vô hướng (lưu cả hai chiều). Mỗi
nguyên tử mang vector 78 chiều, toàn bộ là one-hot:

| Khối | Chiều | Nói lên điều gì |
|---|---|---|
| ký hiệu nguyên tố | 44 | C, N, O, S, halogen, kim loại |
| bậc | 11 | nối với mấy nguyên tử khác |
| tổng số H | 11 | mức bão hòa hydro |
| hóa trị ẩn | 11 | còn chỗ cho liên kết nữa không |
| tính thơm | 1 | có trong vòng thơm không |

Đây đúng là vector của GraphDRP và DeepDDS, DTSyn cũng dùng. Chọn giống **không phải vì nó tối
ưu**, mà vì nếu nhánh thuốc của tôi dùng đặc trưng khác thì mọi chênh lệch so với DeepDDS sẽ không
biết quy cho kiến trúc hay quy cho đặc trưng.

### Morgan fingerprint 2048 bit, bán kính 2

Mỗi bit cho biết một mẫu vòng tròn quanh một nguyên tử có xuất hiện trong phân tử hay không.
Trung vị 54 bit bật trên 2048.

**Vì sao giữ nhánh này khi đã có GNN.** Đây là câu hỏi quan trọng nhất trong phần kiến trúc, và
câu trả lời là về cỡ dữ liệu, không phải về biểu diễn nào "tốt hơn".

GNN trên đồ thị phân tử học biểu diễn hóa học **từ đầu**, nên nó cần đủ thuốc để học. Ở đây chỉ có
**36 thuốc**. Hai thuốc bị tráo đổi vai trong leave_drug nghĩa là mô hình phải suy ra tính chất
của một phân tử chưa từng thấy từ 28 phân tử đã thấy. Fingerprint thì ngược lại: nó là biểu diễn
**đã cố định sẵn**, không có tham số nào phải học, độ chệch cao nhưng phương sai thấp. Hai nhánh
đặt cạnh nhau là một đánh đổi chệch–phương sai có chủ đích: nhánh GNN linh hoạt nhưng dễ quá khớp
trên 36 thuốc, nhánh fingerprint cứng nhưng ổn định.

Thực nghiệm xác nhận: bỏ fingerprint làm QWK rơi từ 0,589 xuống **0,565**, còn hoán vị SMILES
(giữ danh tính thuốc, xóa toàn bộ thông tin cấu trúc của cả hai nhánh) chỉ mất 0,015. Tức là phần
cấu trúc hóa học đóng góp ít, và trong phần ít đó thì **nhánh cổ điển còn hữu ích hơn nhánh GNN**.

Bằng chứng ngoài đi cùng, và phải đọc cẩn thận: benchmark PAIRWISE trên 2.614 thuốc báo đồ thị
phân tử học từ đầu đạt AUPRC 0,321, thấp hơn cả Morgan fingerprint 0,336, trong khi mô hình nền
hóa học tiền huấn luyện đạt 0,710. Nhưng trên **O'Neil** thì GNN học từ đầu lại chạy tốt (DTSyn
0,89, DeepDDS khoảng 0,93 ROC-AUC). Nên bảng đó **không phải lý do bỏ GNN trong phạm vi hiện tại**;
nó là lý do để ghi vào hướng phát triển.

### Vì sao fingerprint đi vào ở đúng chỗ đó, không sớm hơn và không muộn hơn

Có ba vị trí khả dĩ để cắm nhánh fingerprint. Chọn vị trí nào là một quyết định kiến trúc thật, và
nó bị XAI chi phối:

| Vị trí | Hệ quả | Quyết định |
|---|---|---|
| nối vào đặc trưng nguyên tử (lớp 1) | mỗi bit fingerprint là một mẫu vòng tròn trải trên **nhiều** nguyên tử, không ánh xạ 1-1 về nguyên tử nào. Cắm ở đây thì quy gán cấp nguyên tử và cấp mảnh BRICS mất nghĩa | **loại** |
| **cộng vào vector gộp của mỗi thuốc, trước transformer thô** | fingerprint tham gia được vào tương tác thuốc ↔ thuốc ↔ tế bào, nhưng không chạm vào token nguyên tử nên đơn vị giải thích cấp nguyên tử vẫn sạch | **chọn** |
| nối thêm vào readout cuối (lớp 8) | fingerprint chỉ ảnh hưởng tuyến tính ở đầu ra, không bao giờ gặp vector tế bào qua attention, nên không mô hình được "chất này hợp với tế bào kiểu này" | loại |

Và **cộng** chứ không nối: cộng giữ hai nhánh trong cùng không gian 256 chiều nên chúng bù trừ
được cho nhau, giữ nguyên số chiều đầu vào của transformer thô, và giữ tính đối xứng A↔B. Cái giá
phải trả là nhánh này không giải thích được theo mảnh cấu trúc, nên nó được cấp một mặt nạ XAI
riêng `μ_fp` để đo đúng phần quyết định chạy qua nó. Kết quả đo: fingerprint mang **51–55%** quyết
định theo Integrated Gradients và "thắng" ở 65–76% bộ ba theo phép xóa trực tiếp. Đây là con số
phải báo cáo, không phải giấu.

## 2.3. Lớp 2 — GIN hai lớp trên đồ thị phân tử

Mỗi lớp cập nhật biểu diễn của một nguyên tử bằng chính nó cộng tổng các lân cận:

```
h ← LayerNorm( h + Dropout(ReLU( MLP( (1+ε)·h + Σ_lân_cận h ) )) )
```

**Vào:** (N_atom, 78) → **ra:** (N_atom, 256), một token cho mỗi nguyên tử.

Vì sao **GIN thay vì GCN**: GIN dùng phép **tổng** chứ không phải trung bình có chuẩn hóa, nên nó
phân biệt được hai cấu trúc lân cận mà GCN gộp thành một. Về lý thuyết GIN mạnh bằng phép kiểm
Weisfeiler-Lehman, GCN thì không. ε là tham số học được, để mô hình tự chọn mức coi trọng chính
nguyên tử đó so với lân cận. Thực nghiệm: GCN cho 0,589, GIN cho 0,589, **không khác gì**. Lựa
chọn này có lý thuyết đứng sau nhưng không mua được gì trên bộ dữ liệu 36 thuốc, và phải viết đúng
như vậy trong luận văn.

Vì sao **chỉ hai lớp**: hai vòng truyền tin nghĩa là mỗi nguyên tử nhìn thấy lân cận trong bán
kính 2 liên kết, cùng bán kính với fingerprint Morgan r = 2, nên hai nhánh nhìn cùng một thang
cấu trúc. Thêm lớp thì bán kính tăng nhưng oversmoothing cũng tăng, và phân tử ở đây chỉ trung vị
29 nguyên tử.

Vì sao có **residual và LayerNorm ở mỗi lớp**: giữ cho danh tính của từng nguyên tử không bị xóa
sau hai vòng truyền tin. Đây không phải chi tiết trang trí mà là điều kiện cần cho XAI: quy gán
được gắn vào từng nguyên tử, nên nếu sau hai lớp mọi token trong một phân tử đã gần như nhau thì
không còn gì để quy gán.

## 2.4. Lớp 4 và 5 — hai cách dùng biểu hiện gen, chạy song song

Cùng một vector biểu hiện 944 chiều đi vào hai nhánh khác nhau, và đây là một lựa chọn kiến trúc
có lý do rõ ràng.

### Nhánh token gen (`gene_in`): 944 token, mỗi gen một token

Mỗi gen thành vector 129 chiều `[node2vec 128 ‖ biểu hiện đã z-score 1]`, rồi một phép chiếu tuyến
tính dùng chung đưa về 256 chiều.

Vì sao phải ghép node2vec vào chứ không chỉ dùng giá trị biểu hiện: nếu mỗi token chỉ là một số
thực đi qua cùng một lớp tuyến tính dùng chung, thì **944 token sẽ chỉ khác nhau về độ lớn trên
cùng một tia**, tức transformer không thể phân biệt gen nào là gen nào. Nhánh này cần một thứ
đóng vai trò như positional embedding, và node2vec trên PPI là một ứng viên vừa làm được việc đó
vừa mang nghĩa sinh học: hai gen tương tác nhau thì có vector gần nhau.

Cách ghép tách bạch hai loại thông tin: **gen này là gen gì** (node2vec, giống nhau ở mọi dòng tế
bào) và **gen này đang bật mạnh hay yếu ở dòng này** (biểu hiện, thay đổi theo bộ ba). 33 trong
944 gen không có trong STRING ở ngưỡng score ≥ 700 nên nhận vector toàn 0, nhưng vẫn giữ được giá
trị biểu hiện của mình.

node2vec được **đóng băng**, không cập nhật trong lúc huấn luyện. Lý do: nó là kiến thức ngoài, và
nếu để nó học thì nó có thể học thuộc đặc điểm của 37 dòng tế bào trong train.

Thực nghiệm nói gì: bỏ hẳn node2vec chỉ làm QWK giảm 0,003 (0,589 → 0,586), và **node2vec trên
STRING xáo trộn giữ bậc cho 0,585, bằng với mạng thật**. Kết luận trung thực là nhánh này đang
hoạt động **như một positional embedding, không như một tiên nghiệm sinh học**: mô hình chỉ cần
biết "gen này khác gen kia", còn biết "gen này tương tác với gen kia" thì không giúp gì. Đây là
một kết quả âm có đối chứng và nên viết vào bài, không nên lặng lẽ bỏ nhánh đi.

### Nhánh vector tế bào (`cell_mlp`): nén 944 gen thành một vector

`944 → 512 → ReLU → Dropout → 256 → ReLU → 256`.

Vì sao cần nhánh thứ hai này khi đã có 944 token gen: vì transformer mịn chỉ trả ra **một** token
CLS, nên mọi thông tin tế bào muốn tới được đầu ra đều phải chen qua attention. `cell_mlp` mở một
đường đi thẳng. Lớp này được dùng **hai lần** với cùng trọng số, không phải hai bản sao: một lần
làm token thứ tư của transformer thô, một lần làm khối thứ năm của readout.

Vì sao dùng **944 gen landmark** chứ không toàn bộ transcriptome: chỉ có 37 dòng tế bào. Với 20.000
gen thì p lớn hơn n gấp hàng trăm lần, mô hình sẽ nhớ dòng tế bào thay vì học bối cảnh. Ngay cả với
944 gen thì tỷ lệ này đã là vấn đề, và đó chính là giả thuyết giải thích tại sao XAI cấp gen không
ổn định (§3.6).

Vì sao **z-score chỉ fit trên các dòng tế bào trong train của từng fold**: đây là chỗ dễ rò thông
tin nhất trong cả pipeline. Trung bình và độ lệch chuẩn không bao giờ nhìn thấy dòng tế bào trong
test. Có test đơn vị, và cùng một hàm được dùng cho cả SynGT lẫn XGBoost nên so sánh là công bằng.

## 2.5. Lớp 6 — transformer mịn: nguyên tử gặp gen

```
[ CLS_f │ nguyên tử của A (≤69) │ nguyên tử của B (≤69) │ 944 token gen ]  → tối đa 1083 token
```

2 lớp, 4 đầu, pre-LayerNorm, feed-forward 256.

**Lớp này để làm gì:** cho một nhóm nguyên tử cụ thể "nhìn thấy" một gen cụ thể. Ví dụ một nhóm
thế gắn ở vị trí ATP có thể chú ý tới gen mã hóa kinase đó. Đây là mức giải thích mà người làm sinh
học muốn có, và cũng chính là ma trận attention mà DTSyn, MD-Syn và AttenSyn trình bày như lời giải
thích của mình. Giữ lại nó là điều kiện để kiểm định xem cách trình bày đó có đứng được không.

**Chi tiết quyết định tính đối xứng:** nguyên tử của A và nguyên tử của B dùng **chung một type
embedding (id 1)**, gen dùng id 2, CLS dùng id 0. Trong chuỗi này **không có gì đánh dấu đâu là
thuốc A đâu là thuốc B**. Self-attention vốn bất biến với hoán vị, nên đổi A↔B chỉ đổi thứ tự các
token cùng loại và cho ra kết quả giống hệt. Đối xứng đúng theo cấu trúc, không phải nhờ may mắn.

## 2.6. Lớp 7 — transformer thô: thuốc gặp thuốc trong bối cảnh tế bào

Gộp về mức phân tử trước:

```
p_A = mean( token nguyên tử của A )  +  fp_mlp( fingerprint của A )
p_B = mean( token nguyên tử của B )  +  fp_mlp( fingerprint của B )
```

rồi một transformer 2 lớp trên đúng 4 token:

```
[ CLS_c │ p_A │ p_B │ cell_mlp(expr) ]
```

**Lớp này để làm gì:** transformer mịn trả lời "nhóm nguyên tử nào quan trọng", transformer thô
trả lời "hai thuốc này có bổ trợ cho nhau trên tế bào này không". Chỉ 4 token nên gần như miễn phí.
`p_A` và `p_B` lại dùng chung type id 1 nên đối xứng được giữ.

**Ablation nói gì, và phải nói thẳng:** bỏ cả hai transformer cho QWK **0,591**, bằng với bản đầy
đủ 0,589. Bỏ riêng transformer mịn cho 0,591, bỏ riêng transformer thô cho 0,584. DTSyn báo ROC-AUC
tụt từ 0,89 xuống 0,69 khi bỏ cả hai transformer; **tôi không tái lập được điều đó**. Hệ quả cho
cách viết bài: SynGT **không thể** được định vị theo hướng "kiến trúc transformer". Hai transformer
ở đây giữ lại vì chúng cung cấp **chỗ cắm cho XAI** (ma trận attention nguyên tử–gen để đối chứng
với Integrated Gradients), không vì chúng cải thiện độ chính xác.

## 2.7. Lớp 8 — readout "skip": thay đổi quan trọng nhất của toàn dự án

Nối **5 khối, mỗi khối 256 chiều, thành 1280 chiều**:

```
[ CLS_f ‖ CLS_c ‖ p_A + p_B ‖ |p_A − p_B| ‖ cell_mlp(expr) ]
```

| Khối | Mang thông tin gì | Đối xứng A↔B |
|---|---|---|
| `CLS_f` | tóm tắt tương tác nguyên tử ↔ gen | có |
| `CLS_c` | tóm tắt tương tác thuốc ↔ thuốc ↔ tế bào | có |
| `p_A + p_B` | hai thuốc này **là gì** | có, vì là tổng |
| `|p_A − p_B|` | hai thuốc này **khác nhau thế nào** | có, vì lấy trị tuyệt đối |
| `cell_mlp(expr)` | tế bào này là tế bào gì | có |

Ba khối cuối lấy từ **DeepDDS**, và cả ba đều đối xứng nên không phá tính chất ở §2.5.

**Vì sao đây là thay đổi lớn nhất.** Bản đầu tiên chỉ đọc qua `[CLS_f ‖ CLS_c]`, đúng như DTSyn,
nghĩa là **mọi** thông tin phải chen qua hai token CLS, tức phải đi hết qua attention. Đó là một
nút cổ chai thông tin, và nó gây underfit thật: val QWK 0,486, test 0,460, **thua cả one-hot**;
ở epoch 40 train loss còn 0,28 trong khi DeepSynergy đã xuống 0,06. Mô hình không thiếu dung lượng,
nó thiếu đường dẫn.

Hành trình kiến trúc, chọn theo **val** QWK (và thứ tự theo val trùng với thứ tự theo test):

| Biến thể | val QWK | test QWK |
|---|---|---|
| bản đầu, chỉ đọc qua CLS như DTSyn | 0,486 | 0,460 |
| + readout skip | 0,552 | 0,553 |
| + head rộng hơn, attention dropout = 0 | 0,581 | 0,564 |
| **+ nhánh fingerprint Morgan (bản chốt)** | **0,605** | **0,587** |

Readout CLS gốc cho 0,483 trong bảng ablation cuối. Khoảng cách 0,483 → 0,589 lớn hơn mọi thay đổi
về transformer hay GNN gộp lại.

Sau readout là MLP `LayerNorm → 1280 → 512 → ReLU → Dropout → 128 → ReLU`.

## 2.8. Lớp 9 — đầu ra CORN, và vì sao không dùng softmax ba lớp

Ba lớp ant < add < syn **có thứ tự**. Softmax thường coi chúng là ba nhãn rời rạc không liên quan,
nên nó có thể cho P(syn) cao trong khi P(add) thấp, một kết quả vô nghĩa về thứ tự. Nó cũng phạt
nhầm ant thành add và nhầm ant thành syn như nhau, trong khi lỗi thứ hai đắt hơn nhiều.

**CORN** (Cao, Mirjalili, Raschka 2022) biến K lớp có thứ tự thành K−1 = 2 bài toán nhị phân **có
điều kiện**:

```
ℓ₀ → q₀ = P(y > ant)                huấn luyện trên mọi mẫu
ℓ₁ → q₁ = P(y > add │ y > ant)      huấn luyện CHỈ trên mẫu có y > ant
```

Xác suất lớp lấy bằng tích lũy:

```
P(ant) = 1 − q₀      P(add) = q₀(1 − q₁)      P(syn) = q₀·q₁
```

Vì `q₀q₁ ≤ q₀` luôn đúng, **thứ tự không bao giờ bị vi phạm, đúng theo cấu trúc**. Đầu này chỉ có
**258 tham số**.

**Món quà cho XAI, và đây là lý do thật sự để chọn CORN:**

```
z_syn − z_add = log P(syn) − log P(add) = ℓ₁    (chính xác, không xấp xỉ)
```

Đại lượng "bộ ba này nghiêng về hiệp đồng hơn cộng tính bao nhiêu" **chính là một logit mà mạng
tính ra trực tiếp**. Quy gán trên nó rẻ hơn và ít nhiễu hơn so với quy gán trên hiệu của hai logit
softmax. Có test đơn vị kiểm đẳng thức này đúng kể cả khi logit cực trị.

Về số thì CORN chỉ nhỉnh hơn cross-entropy thường khoảng 0,01 QWK (0,589 so với 0,580), nên phải
viết là "lợi ích có nhưng khiêm tốn". Giá trị thật của nó nằm ở hai chỗ phi số: thứ tự lớp bảo đảm
theo cấu trúc, và nó cho target XAI `contrast` một định nghĩa chính xác.

## 2.9. Hàm mất mát: label smoothing tại ngưỡng

Mặc định hiện tại của mô hình. Thay vì nhãn cứng 0/1 cho hai bài toán có điều kiện, mục tiêu mềm là

```
target_k = sigmoid( (điểm_synergy − ngưỡng_k) / τ ),   τ = 5
```

Một bộ ba có Loewe = 10,2 nhận mục tiêu ≈ 0,51 chứ không phải 1,0.

**Căn cứ:** 10,2% bộ ba có nhiễu giữa các bản lặp vắt qua ngưỡng ±10 (§1.5). Phạt mô hình toàn
phần vì những bộ ba mà bản thân nhãn đã mơ hồ là phạt sai. Chú ý rằng chỗ này cần **điểm synergy
thô**, không chỉ cần nhãn rời rạc, nên pipeline giữ lại cả hai.

Kết quả: thắng **6/6 cặp fold** trên cả validation lẫn test, QWK leave_combo từ 0,589 lên **0,627**,
vượt DeepSynergy 0,605.

Cộng thêm trọng số lớp nghịch tần suất (1,39 / 0,48 / 5,11 cho ant/add/syn), AdamW weight decay
1e-4, warmup 5% rồi cosine, gradient clipping 1,0, bf16 autocast. Siêu tham số từ đợt dò 16 cấu
hình: d = 256, GIN 2 lớp, transformer 2+2 lớp, 4 đầu, FFN 256, dropout 0,15, lr 3,29e-4, batch 256.
Dừng sớm theo **QWK trên validation**, patience 20, ngân sách 120 epoch **giống nhau cho mọi mô
hình**. Chọn mô hình luôn theo val, không bao giờ theo test.

## 2.10. Thành phần nào lấy từ bài nào

| Thành phần | Nguồn |
|---|---|
| Hai transformer mịn/thô, token nguyên tử + token gen, node2vec trên PPI | **DTSyn** (*Brief Bioinform* 2022;23(5):bbac302) — khung chính |
| Đặc trưng nguyên tử 78 chiều; readout `[p_A+p_B ‖ \|p_A−p_B\| ‖ cell]` | **DeepDDS** (*Brief Bioinform* 2022;23(1):bbab390) |
| Nhánh fingerprint Morgan | **DeepSynergy** (*Bioinformatics* 2018;34(9):1538) |
| GIN thay GCN | thay đổi của tôi, GCN giữ làm ablation |
| Đối xứng A↔B theo cấu trúc | DTSyn chỉ kiểm bằng thực nghiệm, đây là chi tiết nhỏ |
| **Đầu CORN ba lớp có thứ tự, đánh giá bằng QWK** | **mới trong lĩnh vực hiệp đồng thuốc** (cần tra lại trước khi nộp) |
| **Label smoothing tại ngưỡng, căn cứ từ nhiễu bản lặp** | **mới**, và là cải thiện lớn nhất về số |

**SynGT không nên được định vị là kiến trúc mới.** Nó là tổ hợp các ý đã công bố, và ablation của
chính tôi bác bỏ hướng định vị đó. Hai đóng góp thật nằm ở cách **đặt bài toán** (ba lớp có thứ tự,
cho phép giải thích riêng cho lớp đối kháng) và cách **xử lý nhãn** (label smoothing tại ngưỡng,
có căn cứ từ 10,2% nhiễu đo được).

## 2.11. Mô hình để so sánh

Tất cả dùng chung trainer, chung ngân sách 120 epoch / patience 20.

| Mô hình | Thuộc bài nào | Vai trò |
|---|---|---|
| DeepSynergy | Preuer 2018 | fingerprint + descriptor + biểu hiện → MLP 2048-1024-256. Baseline mạnh nhất ở leave_combo |
| DeepDDS | Wang 2022 | GCN 2 lớp + MLP biểu hiện. Mô hình GNN gần SynGT nhất |
| XGBoost | thực hành phổ biến | fingerprint + biểu hiện → gradient boosting |
| **one-hot** | SynVerse, One-hot news | one-hot thuốc A + B + dòng tế bào → MLP. **Bắt buộc có trong mọi bảng** |
| chỉ thuốc / chỉ tế bào / majority | đối chứng tầm thường | chứng minh nhánh nào thật sự cần, và accuracy vô nghĩa ở đây |

DTSyn **chưa được tái lập thành một mô hình riêng**: SynGT dùng khung của nó nhưng bảng không có
cột "DTSyn". Đây là thiếu sót phải ghi rõ ở phần giới hạn.

## 2.12. Kết quả hiện tại, QWK ba lớp

| Mô hình | leave_combo | leave_drug | leave_cell | leave_tumor |
|---|---|---|---|---|
| **SynGT + label smoothing** | **0,627** | 0,214 | 0,489 | 0,474 |
| DeepSynergy | 0,605 | 0,051 | 0,456 | 0,433 |
| SynGT (CORN thường) | 0,589 | **0,224** | 0,478 | 0,459 |
| one-hot | 0,573 | 0,190 | 0,478 | 0,460 |
| XGBoost | 0,546 | 0,194 | **0,504** | **0,489** |
| DeepDDS | 0,536 | 0,191 | 0,483 | 0,459 |

Ba điều phải đọc đúng từ bảng này:

1. SynGT + label smoothing tốt nhất ở **leave_combo**, cột quan trọng nhất về mặt ứng dụng.
2. DeepSynergy **sụp hoàn toàn khi gặp thuốc mới** (0,605 → 0,051). Nó thắng ở leave_combo nhờ nhớ
   danh tính thuốc, không nhờ hiểu hóa học. SynGT giữ 0,21–0,22 ở đó.
3. **XGBoost thắng ở leave_cell và leave_tumor.** Một mô hình cây trên fingerprint và biểu hiện,
   không đồ thị, không transformer. Cùng với ablation "bỏ hai transformer không đổi gì", đây là
   bằng chứng rằng độ phức tạp của kiến trúc chưa được trả công trên bộ dữ liệu 36 thuốc.

Chặn tái lập G1 **đạt**: ở giao thức nhị phân gốc trên random split, DeepSynergy 0,958 (công bố
0,90) và DeepDDS 0,945 (công bố ~0,93), nên pipeline đáng tin trước khi mọi bảng khác được đọc.

Tỷ lệ **nhầm cực** syn ↔ ant của SynGT chỉ 0,3%, thấp nhất bảng cùng DeepSynergy 0,27%, so với
DeepDDS 0,76% và chỉ tế bào 8,4%.

## 2.13. Ngoài O'Neil: NCI-ALMANAC, zero-shot

234.333 bộ ba ALMANAC lấy từ chính `summary_table_v1.4.csv` của DrugComb (block 132.369–432.467),
để nhãn Loewe hai bên cùng đi qua một pipeline SynergyFinder. Mô hình không được huấn luyện lại:
`cell` sinh từ `cell_mlp(expr)` nên dòng tế bào mới vào được zero-shot, còn `drug_fp` là buffer
theo thuốc nên được thay bằng bảng fingerprint của 101 thuốc ALMANAC sau `load_state_dict`.

| Mô hình | QWK nội bộ | QWK trên ALMANAC | recall hiệp đồng | AUPRC hiệp đồng |
|---|---|---|---|---|
| SynGT + label smoothing | 0,627 | 0,032 | 0,02 | 0,019 |
| SynGT | 0,589 | 0,023 | 0,04 | 0,018 |
| DeepSynergy | 0,605 | 0,017 | 0,01 | 0,014 |
| XGBoost | 0,546 | 0,016 | 0,01 | 0,015 |
| DeepDDS | 0,536 | 0,013 | 0,04 | 0,017 |

Tỷ lệ cơ sở của lớp hiệp đồng ở ALMANAC là 0,015 (so với 0,067 ở O'Neil), nên AUPRC 0,014–0,019 là
ngang bốc thăm. Ở giao thức nhị phân của DTSyn, SynGT đạt BACC 0,529 ± 0,015 và AUROC 0,567 ±
0,023, đúng mức BACC 0,57 mà DTSyn tự báo cho phép chuyển này.

Con số phải đọc cùng với bảng trên là **trần** của bài kiểm tra. 1.163 bộ ba ALMANAC là cùng thí
nghiệm với một bộ ba O'Neil (cùng cặp InChIKey, cùng dòng DepMap). Trên chính 1.163 dòng đó, Loewe
của hai nghiên cứu tương quan Pearson 0,208, đồng ý lớp 57,1%, QWK 0,149; trong 42 tổ hợp O'Neil
gọi là hiệp đồng, ALMANAC giữ lại 1. Lọc còn 1/4 dòng O'Neil có IQR lặp chặt nhất thì mức đồng
thuận **giảm** xuống 0,102, nên bất đồng không nằm ở nhiễu đo bên O'Neil.

Đối chứng đường ống: lấy 424 bộ ba mà dòng O'Neil tương ứng bị giữ lại khỏi tập huấn luyện của
chính run đó, chấm cùng một vector dự đoán hai lần. Theo nhãn O'Neil: QWK 0,561 ± 0,038. Theo nhãn
ALMANAC: 0,139 ± 0,033. Featurization, chỉ số thuốc, buffer fingerprint và scaler biểu hiện đều
phải đúng để cột thứ nhất tồn tại, nên phần sụt thuộc về mục tiêu chứ không thuộc về mô hình.

---

# Phần 3. XAI

## 3.1. Vì sao mặt nạ nằm trong forward pass, không phải một công cụ gắn ngoài

Mọi đơn vị giải thích được cài thành một **mặt nạ mềm bên trong forward pass** (`src/xai/masks.py`).
Nhờ vậy cùng một đoạn code phục vụ cả gradient (Integrated Gradients) và cả phép xóa (Fidelity),
nên hai thứ đo được **trên cùng một thang**. Nếu attribution tính bằng gradient mà fidelity tính
bằng một cơ chế xóa khác thì không biết chênh lệch đến từ explainer hay từ hai định nghĩa "xóa"
khác nhau.

| Mặt nạ | Cắm ở đâu | Đơn vị giải thích | Vì sao chọn đơn vị đó |
|---|---|---|---|
| `μ_gene` (944) | nhân vào **biểu hiện**, trước mọi lớp | từng gen landmark | đơn vị mà TranSynergy và DTSyn dùng, nên so được với y văn. Vì biểu hiện đã z-score, μ = 0 đặt gen về **trung bình tập train**, đúng là baseline trung tính mà IG cần, không phải số 0 tùy ý |
| `μ_frag` | qua `μ_atom`, theo nhóm | **mảnh BRICS** (1–13 mảnh, trung vị 4,5) | xóa mảnh nguyên vẹn thay vì nguyên tử rời. Xóa nguyên tử lẻ tạo ra phân tử không tồn tại, nên Fid+ bị thổi phồng một cách giả tạo |
| `μ_atom` | sau GIN, trước khi gộp | từng nguyên tử | để đối chiếu trực tiếp với attention cấp nguyên tử |
| `μ_fp` (2) | nhân vào đầu ra `fp_mlp` | cả nhánh fingerprint của A và của B | mặt nạ mảnh không chạm tới nhánh này. Cấp mặt nạ riêng thì "tỷ lệ quyết định đến từ fingerprint" mới có định nghĩa chính xác |

## 3.2. Phương pháp chính: Integrated Gradients, và vì sao không phải một phương pháp khác

**Integrated Gradients** (Sundararajan, Taly, Yan, ICML 2017) là phương pháp attribution chính, dùng
cho cả ba đơn vị. Ba lý do:

1. **Có tiên đề completeness.** Tổng quy gán phải bằng `f(1) − f(0)`. Đây là thứ **kiểm được bằng
   số**, nên nó biến "lời giải thích có đúng không" từ chuyện cảm tính thành một phép kiểm. Trong
   dự án này chính phép kiểm đó đã phát hiện một lỗi thật (§3.5).
2. **Khớp với cơ chế mặt nạ.** IG cần một đường đi từ baseline tới đầu vào thật, và mặt nạ mềm
   `μ ∈ [0,1]` chính là đường đi đó. Không phải dựng thêm hạ tầng gì.
3. **Không đòi huấn luyện thêm.** GNNExplainer phải tối ưu một mặt nạ cho từng mẫu, nên nó mang
   theo siêu tham số và tính bất định riêng. Nó được giữ làm **explainer thứ hai để đối chiếu**,
   không làm phương pháp chính.

Chi tiết kỹ thuật đáng ghi: đường tích phân dùng `μ = α³` với 32 bước, không phải lưới α đều.
Chuẩn hóa bậc của phép truyền tin làm đầu ra gần như chỉ chuyển động khi α < 0,05, nên lưới đều cho
khoảng hụt completeness lớn tới mức bằng cả `f(1) − f(0)` ở 20 bước. Với `α = t³` và 32 bước,
khoảng hụt còn khoảng 0,1 và cosine 0,999 so với 512 bước.

## 3.3. Ba mục tiêu attribution, và vì sao có mục tiêu thứ ba

| Mục tiêu | Công thức | Ai đang làm |
|---|---|---|
| `logit` | `z_syn` | toàn bộ y văn hiện nay |
| `contrast` | `z_syn − z_add` | đề xuất của luận văn. Hiệp đồng là **phần dôi ra so với cộng tính**, nên đây mới đúng là "điều gì đẩy bộ ba này ra khỏi trạng thái cộng tính". Với đầu CORN, hiệu này bằng đúng logit có điều kiện thứ hai nên phép trừ miễn phí |
| `ant` | `z_ant − z_add` | chưa ai làm, vì thiết lập nhị phân gộp lớp đối kháng vào lớp âm |

Mục tiêu thứ ba là chỗ mà **đầu ra ba lớp mua được một câu hỏi mới**: "vì sao cặp thuốc này đối
kháng" chỉ hỏi được khi đối kháng là một lớp riêng. Trong thiết lập nhị phân của DTSyn, đối kháng
và cộng tính nằm cùng một bên nên câu hỏi không tồn tại.

Lưu ý ngược lại cũng phải ghi: chỉ giải thích lớp syn và lớp ant. "Gen nào khiến cặp thuốc này
*không* tương tác" là câu hỏi thoái hóa, nên nêu rõ trong chương phương pháp thay vì để hội đồng
phát hiện.

## 3.4. Bộ đo, mỗi chỉ số một đối chứng ngẫu nhiên riêng

Nguyên tắc nền: **tách faithfulness khỏi plausibility khỏi stability**. Ba thứ này độc lập với
nhau, và gộp chúng thành một "điểm XAI" là lỗi mà phần lớn y văn mắc phải.

| Câu hỏi | Hỏi về cái gì | Đo bằng |
|---|---|---|
| **Trung thực** (faithfulness) | về **mô hình**: lời giải thích có phản ánh đúng cái mô hình dùng không | Fid+, Fid−, completeness, Faithfulness Violation Test |
| **Hợp lý** (plausibility) | về **thế giới**: nó có khớp sinh học đã biết không | enrichment KEGG, đích thuốc, so với gen bài khác công bố |
| **Ổn định** (stability) | về **quy trình**: huấn luyện lại thì nó có giữ nguyên không | Jaccard@50 qua seed, qua fold, qua quy ước nhãn |

Trung thực nhưng không hợp lý nghĩa là **mô hình** học sai (nó tìm được đường tắt). Hợp lý nhưng
không trung thực nghĩa là **explainer** sai. Hai kết luận hoàn toàn khác nhau, nên hai chỉ số phải
để riêng.

Các phép đo cụ thể (`src/eval/xai_metrics.py`):

- **Fid+**: xóa top-k (10% và 25% gen; 1 và 2 mảnh) rồi đo độ đổi của mục tiêu, so với các phép xóa
  ngẫu nhiên **khớp số lượng**.
- **Fid−**: chỉ giữ top-k. Báo kèm cảnh báo vì đầu vào lạc phân phối nặng.
- **Completeness gap của IG**: `sum(attr) − (f(1) − f(0))`. Báo ra, không che.
- **Faithfulness Violation Test** (Liu et al., ICML 2022): Spearman giữa attribution và hiệu ứng
  xóa từng đơn vị, trên 10 đơn vị xếp cao nhất.
- **Attention có phải lời giải thích không**: Jaccard@50 giữa attention (CLS → gen) và IG.
- **Độ ổn định**: Jaccard@50 qua 3 seed, qua 5 fold, và qua 4 điểm synergy × 3 ngưỡng, mỗi cái một
  null hoán vị.
- **Plausibility**: làm giàu top-50 gen với pathway KEGG và với đích của chính hai thuốc
  (hypergeometric), null là tập gen ngẫu nhiên **khớp phân bố mức biểu hiện**.
- **Tương tác cặp mảnh**: `φ(i,j) = f(all) − f(−i) − f(−j) + f(−i,−j)`, một sai phân hữu hạn
  **chính xác** chứ không xấp xỉ, vì phân tử ở đây chỉ 1–13 mảnh nên cả ma trận tốn khoảng 200
  forward pass. Cùng dạng với Shapley interaction index của Grabisch và Roubens.
- **Đồ thị so với fingerprint**: IG chung trên `[mảnh, fp_A, fp_B]` trên một đường tích phân, cộng
  thêm phép xóa trực tiếp từng nhánh.

**Case study khai báo trước** (`src/eval/case_study.py`): bốn cặp thuốc, các dòng tế bào và pathway
kỳ vọng được ghi cứng trong file **trước khi** chạy giải thích và không sửa về sau. Cặp đầu là ví dụ
của chính DTSyn (ETOPOSIDE + MK-2206 trên CAOV3 và NCIH23) để so trực tiếp với 5 gen họ công bố.
Mỗi cặp được giải thích bằng 3 seed của fold mà tập test chứa cặp đó, nên mô hình bị chất vấn chưa
từng thấy tổ hợp đó khi huấn luyện. Kế hoạch yêu cầu **bắt buộc báo cáo ít nhất một ca giải thích
sai**.

## 3.5. Về mặt lý thuyết, XAI ở đây xử lý được cái gì

| Câu hỏi | Xử lý được không | Lý do lý thuyết |
|---|---|---|
| Lời giải thích có phản ánh cái mô hình dùng không | **được** | mặt nạ nằm trong forward pass nên gradient và phép xóa cùng một thang; completeness của IG kiểm được bằng số; mỗi chỉ số có null khớp số lượng |
| Attention có phải lời giải thích không | **được, và trả lời là không** | attention và IG là hai đại lượng khác nhau, đem so trực tiếp bằng Jaccard là một phép kiểm hợp lệ. Y văn XAI-GNN đã cảnh báo attention không bảo đảm faithfulness |
| Vì sao **đối kháng** | **được**, nhờ đầu ra ba lớp | `z_ant − z_add` là một đại lượng có nghĩa chỉ khi ant là lớp riêng |
| Phần quyết định nào đi qua đồ thị, phần nào qua fingerprint | **được** | hai nhánh có mặt nạ riêng và cộng vào cùng không gian, nên tắt một nhánh là một can thiệp sạch |
| Tương tác bậc hai giữa hai mảnh phân tử | **được, chính xác** | phân tử chỉ 1–13 mảnh nên tính được toàn bộ sai phân hữu hạn, không cần xấp xỉ Shapley |
| Lời giải thích có đúng với **sinh học** không | **chỉ kiểm định được, không bảo đảm được** | plausibility là câu về thế giới. XAI chỉ có thể **kiểm** xem top-k có làm giàu pathway hay không; nếu mô hình học đường tắt thì không explainer nào cứu được |
| Lời giải thích có **tái lập** không | **chỉ đo được, không sửa được bằng XAI** | độ ổn định là tính chất của quy trình huấn luyện và của cỡ dữ liệu, không phải của explainer. Đo được bằng Jaccard qua seed, nhưng muốn cải thiện thì phải đổi dữ liệu hoặc đổi mô hình |

Hai dòng cuối là chỗ cần nói rõ nhất trong luận văn, vì đó là ranh giới lý thuyết của toàn bộ phần
XAI: một lời giải thích có thể **trung thực hoàn toàn mà vẫn vô nghĩa về sinh học**, nếu mô hình đã
học được một đường tắt. Và đúng đó là tình huống của SynGT.

Một lỗi trong quá trình làm, ghi lại vì nó cho thấy vì sao tiên đề completeness không phải trang
trí: bản đầu tính `z_c` bằng `log(probs())`, mà `probs()` kẹp ở 1e-7. Với bộ ba đối kháng rõ ràng
(logit `[-12, -9]`), `log P(syn)` bị kẹp phẳng, gradient bằng 0, và `contrast` trả về −4,1 thay vì
−9. **Mọi quy gán trên những bộ ba đó đều sai.** Bản hiện tại dùng công thức log-sigmoid nên không
bao giờ bão hòa. Lỗi lộ ra qua kiểm tra completeness, và đã phải chạy lại toàn bộ 39 run giải
thích. Một kết luận trước đó ("target logit thua null") thực ra là sản phẩm của lỗi và đã bị loại.

## 3.6. Thực nghiệm nói gì (đặt ở đây để khỏi lẫn với phần lý thuyết)

**Trung thực: tốt.** Fid+ thắng null ở **97–99,8%** bộ ba, cho cả gen lẫn mảnh BRICS và cả ba
target. Ví dụ: xóa 25% gen theo `contrast` trên bộ ba hiệp đồng làm điểm giảm 5,34, xóa ngẫu nhiên
cùng số lượng chỉ giảm 0,32. Completeness lệch ≤ 1,4% với gen, ≤ 0,6% với mảnh. FVT Spearman
0,32–0,47, tỷ lệ vi phạm 12–27%.

**Attention không phải lời giải thích.** Jaccard@50 giữa attention (CLS → gen) và IG chỉ
**0,04–0,05**. Những gen mà DTSyn, MD-Syn và AttenSyn trình bày qua attention gần như không trùng
với những gen thực sự đổi quyết định khi bị xóa.

**Lớp đối kháng có lời giải thích riêng.** Tương quan thứ hạng `contrast ↔ ant` chỉ 0,084–0,095,
tức gần **trực giao**. Nhưng phải trung thực luôn: `contrast ↔ logit` là 0,887 trên bộ ba hiệp
đồng, nên đóng góp ở dạng mạnh ("phép trừ cho một lời giải thích khác") **không đứng được**; dạng
đứng được là "lớp ant cho lời giải thích riêng".

**Ổn định giữa các seed.** Jaccard@50 của *cùng* một bộ ba qua 3 seed: **0,19–0,28**, null
0,026–0,033; cosine giữa hai bản đồ attribution 0,47–0,59, null quanh 0. Qua quy ước nhãn, cả 30
dòng đều vượt null.

Bản trước ghi 0,032–0,044 với null 0,027–0,040 và kết luận "ngang ngẫu nhiên". Đó là lỗi đo: hàm
chọn bộ ba trong `src/xai/run_explain.py` lấy seed từ `hash(split) % 1000`, mà `hash()` trên chuỗi
bị Python muối lại mỗi tiến trình nếu không đặt `PYTHONHASHSEED`. Mỗi lần gọi `run_explain` là một
tiến trình riêng, nên ba seed của cùng một fold giải thích những bộ ba khác nhau, chỉ dùng chung 0
đến 2 trong 40. Đã cố định offset theo split, chạy lại 54 run giải thích, mỗi fold giờ dùng chung
40/40. Giả thuyết cũ (37 dòng tế bào, 944 gen, mỗi seed chọn một tập gen khác) không còn hiện tượng
nào để giải thích.

**Không chứng minh được ý nghĩa sinh học.** Enrichment KEGG trong top-50 gen: 0,19–0,26% bộ ba,
null 0%. Case study khai báo trước: đoán đúng 5/8 bộ ba trên cả 3 seed, nhưng **0/8** vượt null về
pathway khai báo trước và **0/8** có gen đích của chính hai thuốc trong top-50. Năm gen mà DTSyn
công bố cho ETOPOSIDE + MK-2206 (SNAP25, GALE, PRKCD, PIK3R3, DDIT4) xếp hạng **163–917 trên 944**
trong kết quả của tôi, tức không tái lập. Thêm nữa, dưới Loewe ±10 thì CAOV3 có nhãn **additive**,
không phải hiệp đồng như DTSyn mô tả.

**Đồ thị hay fingerprint quyết định.** Theo IG chung, fingerprint mang 51–55%; theo phép xóa trực
tiếp, fingerprint thắng ở 65–76% bộ ba. Tương tác cặp mảnh BRICS chỉ bằng 2–4% hiệu ứng bậc một,
tức mô hình gần như cộng tính theo mảnh. Hệ quả: giải thích cấp mảnh chỉ nói được một nửa câu
chuyện, và đó là một giới hạn của kiến trúc hai nhánh, phải nêu thẳng.

Một câu gọn cho phần kết luận: **XAI ở đây cho ra lời giải thích đúng với mô hình và tái lập được
qua seed cũng như qua quy ước nhãn, nhưng chưa chứng minh đúng với sinh học.** Một lời giải thích
ổn định mà vẫn không chỉ vào pathway nào thì khó bỏ qua hơn một lời giải thích nhiễu.

---

# Phần 4. Ba trục đứng được trên số liệu

Xếp theo độ mạnh, dùng để định hướng cách viết bài và luận văn:

1. **Giao thức bỏ vùng trung tính thổi phồng kết quả.** Cùng mô hình, cùng split, chỉ đổi cách gán
   nhãn: bỏ vùng 0–10 như DTSyn làm AUROC cao hơn khoảng **0,055** và AUPRC cao hơn khoảng 0,25, ở
   **mọi** mô hình và mọi split. Nhất quán trên 4 mô hình × 2 split, nên đây là thuộc tính của
   **giao thức đánh giá**, không phải của một mô hình. Kèm đề xuất thay bằng bài toán ba lớp có thứ
   tự với QWK và tỷ lệ nhầm cực.
   Phải tự phản biện trước: mức tụt AUPRC 0,25 không quy hết cho độ khó được, vì bỏ vùng trung tính
   cũng đổi tỷ lệ lớp dương từ 10,4% xuống 6,7%. Tính theo **lift trên tỷ lệ nền** thì mức tụt chỉ
   còn −5,6% đến −14,4%. Nên báo cả hai cách, lấy AUROC làm luận điểm chính.
2. **Trung thực ≠ ổn định ≠ có nghĩa sinh học.** Fid+ thắng null 97–99%, nhưng Jaccard qua seed
   bằng null, enrichment bằng 0, ví dụ của DTSyn không tái lập, attention không trùng IG. Đây là
   phần phản biện có null, nhiều seed và case study khai báo trước, thứ mà các bài trước không có.
3. **Lớp đối kháng có lời giải thích riêng**, trực giao với hiệp đồng (tương quan 0,08–0,10), câu
   hỏi chỉ đặt được khi có ba lớp.

**Không viết trong bài:** không viết SOTA, không viết "kiến trúc mới", không viết "phát hiện cơ chế
sinh học", không viết đóng góp `contrast` ở dạng mạnh. Mỗi câu trong bốn câu đó đều bị số liệu của
chính tôi bác bỏ.

Nơi gửi phù hợp: tạp chí hoặc hội nghị bioinformatics tầm trung, hoặc một track về evaluation và
reproducibility.

---

# Phần 5. Còn thiếu gì, theo thứ tự ảnh hưởng tới bài

1. **Kiểm chứng ngoài trên ALMANAC** đã chạy ngày 23/11/2026, lấy từ chính file DrugComb v1.4 chứ
   không cần `ComboDrugGrowth_Nov2017`. SynGT rơi về QWK 0,023 zero-shot, các mô hình khác 0,013–0,017,
   và BACC 0,529 ở giao thức nhị phân của DTSyn (họ báo 0,57). Nhưng trần của bài kiểm tra chỉ là QWK
   0,149: hai nghiên cứu không đồng ý với nhau trên 1.163 thí nghiệm trùng nhau. Việc còn lại không
   phải chạy lại mô hình mà là chọn một mục tiêu so được: tính lại điểm synergy từ ma trận tăng trưởng
   thô của ALMANAC, hoặc đổi sang hồi quy liên tục, hoặc chọn nghiên cứu khác trong DrugComb.
2. **DTSyn chưa được tái lập thành mô hình riêng**, bảng so sánh thiếu cột của chính bài làm khung.
3. **Dò lại siêu tham số cho kiến trúc cuối.** Đợt dò 16 cấu hình làm trên readout CLS cũ, trước
   khi chốt readout skip và nhánh fingerprint.
4. **Lệch so với kế hoạch:** 16 cấu hình thay vì 40, 3 seed thay vì 5, `N_RAND` = 10 trong code so
   với 20 trong kế hoạch.
5. **Số bộ ba 18.870 so với 23.052 của DTSyn**: phải đối chiếu từng bước lọc và ghi rõ lý do chênh
   lệch trong luận văn.
6. **Tra lại tính mới của đầu ra ordinal** ("ordinal drug synergy", "three-class synergy QWK")
   trước khi nộp.
7. **Code chưa commit.**

Quy mô đã chạy để tham chiếu: 656 run huấn luyện (613 lưới chính + 16 dò siêu tham số + 27 chẩn
đoán kiến trúc) và 39 run giải thích, 0 lỗi, 16 test đơn vị đều qua, gồm đối xứng A↔B tuyệt đối,
không rò thông tin giữa các split, z-score chỉ fit trên train, và `contrast` bằng logit thứ hai kể
cả khi logit cực trị. Chạy lại toàn bộ: `bash run_all.sh 4`.
