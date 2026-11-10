# Planner luận văn: lời giải thích đường dẫn trên mạng sinh học có thật sự là sinh học?

Năm 2025, nhóm SynVerse (Tasnina, Haghani, Murali, *Brief Bioinform* bbaf676) xáo trộn mạng PPI mà vẫn giữ nguyên số liên kết của mỗi protein, rồi cho 16 mô hình dự đoán hiệp đồng thuốc chạy lại trên mạng đã xáo đó. PCC gần như không giảm. Một MLP chỉ nhận vector one-hot (không biết gì về sinh học, chỉ biết "đây là thuốc số 7, cell line số 12") đứng ngang với cả 16 kiến trúc. Năm 2026, bài "One-hot news" (Çandır et al., *Bioinformatics* btag040) đi thêm một bước: khi bộ ba (thuốc A, thuốc B, cell line) lặp lại như trong mọi bộ dữ liệu thật, attribution chỉ tìm lại được đặc trưng thật với Jaccard 0,2 đến 0,4.

Trong khi đó, khoảng 25 bài thuộc nhóm "Graph & Network Path XAI" mà báo cáo [XAI đồ thị mạng sinh học.md](<XAI%20đồ%20thị%20mạng%20sinh%20học.md>) đã rà đều in ra những đường dẫn kiểu "thuốc A ức chế EGFR, tín hiệu đi qua MAPK1, gặp nhánh của thuốc B ở ERK" và gọi đó là cơ chế. Không bài nào đo xem đường dẫn ấy có trung thực với mô hình hay không, và không bài nào chạy lại explainer trên mạng đã xáo.

Đề xuất 1 của báo cáo chính là phép đo còn thiếu đó. Planner này biến nó thành một kế hoạch làm từ đầu, cho người chưa học tin sinh ngày nào.

Cách đọc: phần 1 đến phần 4 là kế hoạch (làm gì, dữ liệu gì, mô hình gì, train thế nào). Phần 5 là toàn bộ kiến thức nền, mỗi khái niệm có ví dụ tính tay. Nếu bạn chưa biết "cell line" hay "Loewe" là gì, đọc phần 5 trước rồi quay lại.

Project này viết mới từ đầu. Mục 3.6 là cấu trúc code sẽ dựng, mục 3.7 chia phạm vi thành phần lõi bắt buộc và phần mở rộng, vì làm đủ mọi thứ trong báo cáo thì 12 tháng không đủ.

---

## Phần 1. Hướng làm và cách giải quyết bài toán

### 1.1. Bài toán gốc

Đầu vào là một bộ ba: thuốc A, thuốc B, một dòng tế bào ung thư (cell line) c. Đầu ra là mức hiệp đồng: hai thuốc dùng chung giết tế bào nhiều hơn, bằng, hay ít hơn mức "cộng dồn" mong đợi. Luận văn xếp nhãn thành 3 lớp theo điểm Loewe:

| Điểm Loewe      | Nhãn              |
| ----------------- | ------------------ |
| > 10              | syn (hiệp đồng) |
| từ −10 đến 10 | add (cộng tính)  |
| < −10            | ant (đối kháng) |

Mô hình dự đoán là một GNN chạy trên mạng tương tác protein (PPI). Sau khi mô hình dự đoán, một explainer chỉ ra cạnh nào, đường dẫn nào trên mạng đã đẩy dự đoán về phía "syn".

### 1.2. Bài toán của luận văn (không phải bài toán dự đoán)

Luận văn **không** cố làm mô hình dự đoán giỏi hơn. Câu hỏi là:

> Đường dẫn mà explainer chỉ ra chứa bao nhiêu thông tin vượt quá (a) danh tính thuốc và cell line, và (b) topo ngẫu nhiên của mạng?

Ba câu hỏi nghiên cứu, lấy từ báo cáo:

- **RQ1.** Lời giải thích trên PPI thật có khác lời giải thích trên PPI đã xáo (degree-preserving rewiring) không? Chỉ số: rewiring-survival rate.
- **RQ2.** Giải thích ở cấp tương tác (trừ đi hiệu ứng riêng của từng thuốc) có bớt nhầm hiệu ứng chính thành cơ chế hiệp đồng ở cấp đường dẫn không?
- **RQ3.** Số cell line và mức lặp lại của bộ ba ảnh hưởng thế nào tới khả năng tìm lại cơ chế đã cài sẵn?

### 1.3. Chiến lược: dựng một "phòng thí nghiệm" có đáp án, rồi mới sang dữ liệu thật

Vấn đề cốt lõi của XAI trên dữ liệu thật là không ai biết đáp án. Không có danh sách "đường dẫn thật" cho cặp thuốc 5-FU + MK-2206 trên cell line A2058. Nên luận văn đi hai chặng:

```
Chặng 1: dữ liệu BÁN TỔNG HỢP                      Chặng 2: dữ liệu THẬT
───────────────────────────────                     ─────────────────────────
mạng PPI thật (STRING / KEGG)                        O'Neil + NCI-ALMANAC + DrugComb
+ biểu hiện gen thật hoặc mô phỏng                   biểu hiện gen DepMap
+ CƠ CHẾ CÀI SẴN (mình tự viết luật                  không có đáp án
  sinh nhãn, nên biết đường dẫn đúng)                → kiểm chứng gián tiếp: rewiring,
→ đo được recall, Jaccard, fidelity                    one-hot, DepMap, SynLethDB,
  so với đáp án                                        positive control BRAF/MEK
```

Chặng 1 trả lời "explainer có tìm được cơ chế khi cơ chế chắc chắn tồn tại không". Chặng 2 trả lời "trên dữ liệu thật, lời giải thích có sống sót qua các đối chứng không".

### 1.4. Vì sao hướng này không thể "thất bại"

Có hai kết cục và cả hai đều thành paper:

| Kết cục                                                                                                                          | Ý nghĩa                                                                                            | Kiểu paper                                                              |
| ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Explainer cấp tương tác tìm được cơ chế cài sẵn, và lời giải thích trên dữ liệu thật biến mất khi xáo mạng | Có cách giải thích đáng tin, kèm giao thức kiểm định                                      | Phương pháp + benchmark                                               |
| Mọi explainer đều thất bại, hoặc lời giải thích vẫn y nguyên trên mạng đã xáo                                      | Các "đường dẫn cơ chế" đã công bố có thể chỉ là sản phẩm của việc nhớ danh tính | Phản biện, giống One-hot news (đã được *Bioinformatics* nhận) |

Phần dễ sai là đọc kết quả: phải chạy đủ seed, đủ fold, đủ đối chứng thì kết cục nào cũng mới đứng được.

### 1.5. Đóng góp dự kiến

1. Một bộ dữ liệu bán tổng hợp có cơ chế cài sẵn **trên topo mạng thật**, mô phỏng đúng mẫu "Complementary Exposure" của Cheng et al. 2019.
2. Một giao thức kiểm định lời giải thích đường dẫn: kiểm tra Faber, fidelity Fid+/Fid−, ROAR, stability, rewiring-survival.
3. Toán tử giải thích cấp tương tác ở mức cạnh và đường dẫn (sai phân bậc hai kiểu Shapley interaction index), chưa ai làm cho GNN hiệp đồng.
4. Kết quả áp giao thức này lên các explainer đại diện (edge-IG, GNNExplainer, PaGE-Link hai nguồn, CF-GNNExplainer) và lên dữ liệu thật.

---

## Phần 2. Dataset sẽ dùng

Có bốn loại dữ liệu phải ghép lại: nhãn hiệp đồng, đặc trưng cell line, đích thuốc, và mạng. Thêm một nhóm dữ liệu chỉ dùng để kiểm chứng lời giải thích.

### 2.1. Nhãn hiệp đồng (bộ ba thuốc–thuốc–cell → điểm)

| Bộ                                                  | Quy mô (xấp xỉ)                                                                  | Điểm có sẵn                               | Dùng để                                                        |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------- |
| **O'Neil 2016** (Merck, *Mol Cancer Ther*)   | 38 thuốc, 39 cell line, khoảng 22–23 nghìn bộ ba                               | Loewe (qua DrugComb còn có Bliss, HSA, ZIP) | Bộ chính, vì mọi bài trong báo cáo đều so trên bộ này |
| **NCI-ALMANAC** (Holbeck 2017, *Cancer Res*) | khoảng 100 thuốc đã được FDA duyệt, 60 cell line NCI-60, hơn 5 nghìn cặp | ComboScore                                    | Tăng số cell line, giảm vấn đề "chỉ có 39 cell"           |
| **DrugComb** (drugcomb.org, Zheng et al.)      | gộp nhiều nghiên cứu, hàng trăm nghìn bộ ba, hàng nghìn cell line         | Loewe, Bliss, HSA, ZIP, S score               | Lấy lại O'Neil với đủ 4 loại điểm, và bổ sung cell line |

Cách lấy: tải bảng summary của DrugComb, lọc cột `study_name == "ONEIL"` để có O'Neil, lọc `"ALMANAC"` để có NCI-ALMANAC. Số liệu quy mô ở bảng trên là xấp xỉ, đếm lại sau khi lọc vì phiên bản DrugComb thay đổi theo thời gian.

Một dòng sau khi lọc trông như sau (ví dụ minh họa, số không lấy từ file thật):

| drug_row | drug_col | cell_line_name | synergy_loewe | synergy_bliss | synergy_zip |
| -------- | -------- | -------------- | ------------- | ------------- | ----------- |
| 5-FU     | MK-2206  | A2058          | 14,2          | 8,9           | 6,1         |

Dòng này có Loewe 14,2 nên nhãn là syn, nhưng ZIP chỉ 6,1 nên theo ZIP nó là add. Đây không phải lỗi nhập liệu: các mô hình hiệp đồng định nghĩa "mức mong đợi" khác nhau (phần 5.3). Báo cáo trích một preprint cho thấy Loewe chỉ tương quan r = 0,28 với ZIP trên DrugComb, nên luận văn phải chạy phân tích độ nhạy theo loại điểm.

### 2.2. Đặc trưng cell line

| Nguồn                                              | File                                              | Nội dung                                                                                  |
| --------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **DepMap / CCLE** (depmap.org, tab Downloads) | `OmicsExpressionProteinCodingGenesTPMLogp1.csv` | Biểu hiện gen: hàng là cell line (mã ACH-xxxxxx), cột là gen, giá trị log2(TPM+1) |
| DepMap                                              | `Model.csv`                                     | Bảng map mã ACH sang tên cell line (A2058, MCF7, ...)                                   |
| DepMap (tùy chọn)                                 | mutation, CNV                                     | Đột biến và số bản sao gen, nếu muốn thêm đặc trưng                            |

Biểu hiện gen được z-score theo từng gen (trừ trung bình, chia độ lệch chuẩn qua các cell line), để giá trị 0 nghĩa là "mức trung bình". Mốc 0 này quan trọng vì Integrated Gradients dùng nó làm baseline (phần 5.6).

Việc khớp tên cell line giữa DrugComb và DepMap tốn công hơn bạn nghĩ: "NCI-H460", "NCIH460", "H460" là cùng một dòng. Dành riêng vài ngày cho bước này và lưu lại bảng map thủ công.

### 2.3. Đích thuốc (drug target)

| Nguồn                                           | Ghi chú                                                                                    |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| **DrugBank**                               | Đầy đủ nhất, cần đăng ký license học thuật (miễn phí, duyệt mất vài ngày)  |
| **ChEMBL**, **DGIdb**, **TTD** | Thay thế không cần license; ChEMBL cho ái lực, có thể lọc ≤ 10 µM như Cheng 2019 |
| Chú giải thuốc của DrugComb                  | Nhanh, nhưng kiểm tra lại với DrugBank                                                  |

Định dạng cuối: bảng hai cột `drug, gene`. Ví dụ: `trametinib, MAP2K1` và `trametinib, MAP2K2` (trametinib ức chế MEK1 và MEK2).

O'Neil có vài thuốc thí nghiệm của Merck (mã MK-xxxx) với đích ít được chú giải. Ghi lại thuốc nào không có đích; chúng sẽ bị loại khỏi phần giải thích đường dẫn, vì không có điểm bắt đầu trên mạng.

### 2.4. Mạng sinh học

| Mạng                                                                               | Kích thước                                                                          | Có hướng? | Có dấu?                              | Vai trò                                       |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------ | -------------------------------------- | ---------------------------------------------- |
| **STRING v12** (người, mã loài 9606)                                      | khoảng 19 nghìn protein; lọc `combined_score ≥ 700` còn vài trăm nghìn cạnh | Không       | Không                                 | Mạng lớn, dùng như phần lớn bài Nhóm 3 |
| **KEGG** (khoảng 46–48 pathway tín hiệu ung thư, như DeepSignalingFlow) | khoảng 1,3 đến 2 nghìn gen                                                         | Có          | Có trong KGML (activation/inhibition) | Mạng nhỏ, dễ đọc đường dẫn            |
| **OmniPath** (tùy chọn, gói `omnipath` cho Python)                       | gộp SIGNOR, SignaLink, ...                                                            | Có          | Có                                    | Cho phần mở rộng knockout (Đề xuất 2)    |

STRING tải ở string-db.org: file `9606.protein.links.v12.0.txt.gz` (cạnh, dùng mã ENSP) và `9606.protein.info.v12.0.txt.gz` (map ENSP sang tên gen). KEGG lấy qua REST API, ví dụ `https://rest.kegg.jp/get/hsa04010/kgml` là pathway MAPK. KEGG có điều khoản riêng cho tải hàng loạt, đọc trước khi dùng.

Để GNN chạy nổi trên laptop, giới hạn mạng: chỉ giữ gen có trong cả mạng, bảng biểu hiện và nằm trong vòng 2 bước quanh tập đích thuốc. Báo cáo nêu đây là cách giảm chi phí tính toán trên STRING toàn bộ.

### 2.5. Dữ liệu chỉ dùng để kiểm chứng lời giải thích

| Nguồn                                                             | Câu hỏi nó trả lời                                                                                                                 |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| **DepMap CRISPR** (`CRISPRGeneEffect.csv`, điểm Chronos) | Gen trong đường dẫn có "quan trọng" thật với cell line đó không? (điểm càng âm, tế bào càng cần gen đó để sống) |
| **SynLethDB**                                                | Cặp gen trong lời giải thích có phải cặp gây chết tổng hợp đã biết không?                                                |
| **MSigDB** (Hallmark, C2 KEGG/Reactome)                      | Gen trong lời giải thích có làm giàu pathway của cơ chế tác dụng đã biết không?                                          |
| **Interactome Cheng 2019** (16.677 protein, 243.603 cạnh)   | Để tính baseline s_AB đúng như bài gốc                                                                                          |

### 2.6. Dữ liệu bán tổng hợp (tự sinh)

Đây là dữ liệu quan trọng nhất của chặng 1, và bạn tự viết script sinh ra nó. Thiết kế chi tiết ở phần 4.2.

---

## Phần 3. Cấu trúc mô hình sẽ xây dựng

Hệ thống có năm khối. Mô hình dự đoán chỉ là một khối, và không phải khối quan trọng nhất.

```
          ┌──────────────── dữ liệu (thật hoặc bán tổng hợp) ────────────────┐
          │                                                                   │
   [A] Mô hình dự đoán            [B] Baseline                [C] Biến thể mạng
   GCN đối xứng / GAT /           one-hot MLP,                mạng thật, xáo giữ bậc,
   GSAT-style                     MLP kiểu DeepSynergy,       xáo giữ strength, ngẫu nhiên
          │                       s_AB Cheng, đường ngắn nhất
          ▼
   [D] Explainer: edge-IG, GNNExplainer, PaGE-Link hai nguồn, CF-GNNExplainer
       mỗi cái có 3 cấp: logit / contrast / interaction
          │
          ▼
   [E] Bộ đo: kiểm tra Faber, recall@k, main@k, path-Jaccard, Fid+, Fid−, ROAR,
       stability, rewiring-survival, kiểm chứng sinh học
```

### 3.1. Khối A: mô hình dự đoán SynergyGNN

Mỗi bộ ba (A, B, c) được biến thành một đồ thị: chính mạng PPI, nhưng mỗi gen g mang ba con số.

```
đặc trưng node của gen g =  [ expr_c(g),   tA(g) + tB(g),   tA(g) · tB(g) ]
                              biểu hiện     g là đích của     g là đích của
                              trong cell c  ít nhất 1 thuốc   CẢ HAI thuốc
```

`tA(g) = 1` nếu g là đích của thuốc A, ngược lại bằng 0. Dùng tổng và tích để mô hình tự động đối xứng: hoán đổi A và B không đổi đầu vào, nên không đổi dự đoán. Hiệp đồng là quan hệ đối xứng (A+B giống B+A), nên mô hình phải đối xứng ngay từ thiết kế, không phải học điều đó.

```
X (n_gen × 3)
   │  GCN lớp 1:  H1 = ReLU( Â_m · X  · W1 )        Â_m: ma trận kề chuẩn hóa,
   │  GCN lớp 2:  H2 = ReLU( Â_m · H1 · W2 )             nhân với mask cạnh m (mặc định m = 1)
   │  chiếu mỗi gen xuống 4 chiều rồi flatten (giữ danh tính từng gen)
   │  ghép embedding thuốc [eA + eB, eA · eB]
   ▼
 MLP → 3 logit (ant, add, syn) → softmax
```

Ba quyết định cần ghi vào luận văn kèm lý do:

1. **Mask cạnh m nằm sẵn trong forward.** Mỗi cạnh e có trọng số m_e, mặc định bằng 1. Mọi explainer cấp cạnh (edge-IG, GNNExplainer, PaGE-Link) đều cần đạo hàm theo m_e, nên viết nó vào mô hình từ đầu thay vì vá sau. Cụ thể: Â được dựng lại từ danh sách cạnh nhân m mỗi lần forward, và chuẩn hóa bậc tính trên mạng đã nhân mask. Viết một test: m = 1 phải cho đúng đầu ra của GCN thường với Â cố định.
2. **Flatten thay vì pooling trung bình.** Pooling trung bình trộn mọi gen thành một vector, danh tính gen biến mất, attribution lên gen mất nghĩa. Cái giá: số tham số tăng theo số gen, nên phải giới hạn mạng (mục 2.4).
3. **Embedding thuốc.** Có embedding thuốc thì mô hình có đường tắt để nhớ danh tính. Giữ nó (vì các mô hình đã công bố đều có), nhưng chạy thêm biến thể bỏ embedding để xem lời giải thích thay đổi ra sao.

Hai biến thể kiến trúc để so:

| Biến thể           | Khác ở đâu                                                                       | Lý do đưa vào                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **GAT**        | Thay Â bằng attention học được                                                 | Nhiều bài Nhóm 3 lấy attention làm lời giải thích; cần kiểm tra điều đó                                                           |
| **GSAT-style** | Thêm một nhánh học xác suất giữ mỗi cạnh, phạt theo information bottleneck | Mô hình tự giải thích; Azzolin et al. (ICLR 2025) cho rằng kiểu mô-đun này thoát khỏi nghịch lý "trung thực thì vô thông tin" |

### 3.2. Khối B: baseline

| Baseline                           | Đầu vào                                       | Câu hỏi nó trả lời                                                                                                          |
| ---------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **One-hot MLP**              | vector one-hot của A, B, c                      | Mô hình nhớ danh tính đạt được bao nhiêu? GNN không thắng cái này thì mạng không đóng góp gì cho dự đoán |
| **MLP kiểu DeepSynergy**    | biểu hiện gen của c + vector đích của A, B | Có đặc trưng sinh học nhưng không có mạng                                                                               |
| **s_AB của Cheng**          | đích A, đích B, mạng                        | Explainer phi học máy: đường dẫn giữa đích hai thuốc theo khoảng cách ngắn nhất                                    |
| **Đường đi ngắn nhất** | đích A, đích B, mạng                        | Explainer "ngây thơ nhất". Explainer GNN không thắng được nó thì đó đã là một phát hiện                        |

### 3.3. Khối C: biến thể mạng

| Biến thể         | Cách tạo                                                                   | Giữ lại gì                | Phá gì              |
| ------------------ | ---------------------------------------------------------------------------- | ---------------------------- | --------------------- |
| Thật              | STRING / KEGG                                                                | tất cả                     | không                |
| Xáo giữ bậc     | `networkx.double_edge_swap` lặp khoảng 10 × số cạnh lần              | số liên kết của mỗi gen | đường đi cụ thể |
| Xáo giữ strength | như trên, nhưng giữ tổng trọng số cạnh của mỗi gen (theo SynVerse) | độ mạnh mỗi node         | đường đi cụ thể |
| Ngẫu nhiên       | Erdős–Rényi cùng số cạnh                                               | số node, số cạnh          | mọi thứ             |

### 3.4. Khối D: explainer

Bốn explainer, mỗi cái cho ra một điểm trên mỗi cạnh (hoặc mỗi gen), từ đó trích k đường dẫn tốt nhất giữa đích A và đích B.

| Explainer                      | Ý tưởng                                                                                                    | Đầu ra                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------- | -------------------------- |
| **edge-IG**              | Integrated Gradients theo mask m, từ m = 0 (mạng rỗng) đến m = 1 (mạng đầy đủ)                      | điểm mỗi cạnh          |
| **GNNExplainer**         | Học mask mềm sao cho giữ được dự đoán mà ít cạnh nhất                                            | mask mỗi cạnh            |
| **PaGE-Link hai nguồn** | Học mask có ràng buộc ép cạnh được chọn tạo thành đường dẫn; nguồn là đích A và đích B | k đường dẫn            |
| **CF-GNNExplainer**      | Tìm tập cạnh nhỏ nhất mà xóa đi làm lật syn thành add                                              | tập cạnh phản thực tế |

Trích đường dẫn từ điểm cạnh: đặt chi phí mỗi cạnh = −log(điểm chuẩn hóa về khoảng (0,1]), rồi chạy k đường ngắn nhất (`networkx.shortest_simple_paths`) giữa mọi cặp (đích A, đích B).

Mỗi explainer có ba cấp, chỉ khác ở **đại lượng được giải thích**:

| Cấp              | Đại lượng f                                           | Câu hỏi                                                                              |
| ----------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| (i) logit         | z_syn                                                     | Cạnh nào đẩy logit syn lên? Cách các bài đang làm                            |
| (ii) contrast     | Δ = z_syn − z_add                                       | Vì sao syn **thay vì** add?                                                    |
| (iii) interaction | Δ(A,B) − E_r Δ(A,r) − E_r Δ(r,B) + E_{r,r'} Δ(r,r') | Phần nào thuộc về **cặp** A+B, sau khi trừ hiệu ứng riêng từng thuốc? |

r là thuốc tham chiếu, lấy trung bình qua mọi thuốc khác. Cấp (iii) có cùng cấu trúc với sai phân bậc hai trong Shapley interaction index (Grabisch & Roubens 1999). Ví dụ tính tay ở mục 5.6.

**Chi phí của cấp (iii) trên cạnh.** IG tuyến tính theo f, nên attribution của interaction bằng IG(A,B) − trung bình IG(A,r) − trung bình IG(r,B) + trung bình IG(r,r'), tất cả cùng cell c. Với 38 thuốc của O'Neil, số hạng cuối cần khoảng 700 lần IG cho mỗi cell. Không tính lại cho từng bộ ba: số hạng E_{r,r'} chỉ phụ thuộc c nên tính một lần cho mỗi cell, số hạng E_r Δ(A,r) tính một lần cho mỗi cặp (thuốc, cell) rồi lưu lại. Nếu vẫn chậm, lấy mẫu 8 thuốc tham chiếu thay vì dùng hết, và báo kết quả thay đổi bao nhiêu khi tăng lên 16.

Explainer học mask (GNNExplainer, PaGE-Link) không tuyến tính theo f như IG, nên không tách số hạng ra được. Với chúng, cấp (iii) nghĩa là tối ưu mask cho chính đại lượng interaction, và mỗi bước tối ưu phải chạy mô hình trên cả các cặp tham chiếu. Đây là lý do mục 3.7 đặt cấp (iii) cho explainer học mask vào phần mở rộng.

### 3.5. Khối E: bộ đo

| Chỉ số                      | Dùng ở        | Tốt khi                                               |
| ----------------------------- | --------------- | ------------------------------------------------------ |
| Kiểm tra Faber               | bán tổng hợp | xóa cơ chế cài sẵn thì độ chính xác sụp     |
| recall@k                      | bán tổng hợp | cao                                                    |
| main@k                        | bán tổng hợp | thấp (không nhầm hiệu ứng chính)                 |
| path-Jaccard                  | bán tổng hợp | cao                                                    |
| Fid+ / Fid−                  | cả hai         | Fid+ cao, Fid− thấp                                  |
| ROAR                          | cả hai         | xóa top cạnh rồi train lại, hiệu năng vẫn giảm |
| Stability                     | cả hai         | cosine giữa các seed cao                             |
| Rewiring-survival             | cả hai         | **thấp**                                        |
| DepMap, SynLethDB, enrichment | thật           | có ý nghĩa thống kê hơn baseline ngẫu nhiên    |

Định nghĩa và ví dụ từng chỉ số ở phần 5.7.

### 3.6. Cấu trúc code sẽ viết

Chỉ cần torch, numpy, pandas, scikit-learn và networkx. GCN và IG tự viết, mỗi phần vài chục dòng; với mạng dưới 3 nghìn gen thì không cần PyG hay Captum.

```
src/
  data/
    prepare.py         CSV thô (nhãn, biểu hiện, đích, mạng) -> một file .pt
    make_synthetic.py  dữ liệu bán tổng hợp trên mạng thật + ground truth cấp cạnh
    rewire.py          xáo giữ bậc, xáo giữ strength, Erdős–Rényi
    dataset.py         split random / leave-combo / leave-drug / leave-cell
  model/
    gnn.py             SynergyGNN có mask cạnh m; GAT, GSAT-style cùng giao diện
  training/
    train.py           train + early stopping theo QWK, lưu config.json và metrics.json
    baselines.py       one-hot MLP, MLP kiểu DeepSynergy
  explain/
    edge_ig.py         IG theo m, 3 cấp logit / contrast / interaction
    gnnexplainer.py
    paths.py           trích k đường dẫn từ điểm cạnh
    network_baselines.py   s_AB của Cheng, đường ngắn nhất
  eval/
    metrics.py         QWK, macro-F1, polar error
    explain_metrics.py recall@k, main@k, path-Jaccard, Fid±, stability, rewiring-survival
  tests/
    test_all.py        đối xứng A↔B, m = 1 khớp GCN thường, split không rò rỉ,
                       completeness của IG, interaction = 0 với mô hình cộng tính,
                       rewiring giữ bậc
```

Viết `tests/test_all.py` song song với từng file, không để dồn đến cuối. Năm test đầu mỗi cái chỉ vài dòng nhưng bắt được đúng những lỗi làm hỏng toàn bộ kết quả giải thích.

### 3.7. Phần lõi và phần mở rộng

Làm đủ 3 kiến trúc × 4 explainer × 3 cấp × 4 mạng × 3 split là quá sức một luận văn. Chia như sau:

| | Phần lõi (bắt buộc, đủ để bảo vệ) | Phần mở rộng (làm nếu còn thời gian) |
| --- | --- | --- |
| Mô hình | GCN đối xứng | GAT, GSAT-style |
| Explainer | edge-IG 3 cấp, GNNExplainer cấp (i)(ii) | GNNExplainer cấp (iii), PaGE-Link hai nguồn, CF-GNNExplainer |
| Baseline | one-hot MLP, MLP DeepSynergy, s_AB, đường ngắn nhất | RWR |
| Mạng | thật, xáo giữ bậc | xáo giữ strength, Erdős–Rényi |
| Split | leave-combo | leave-cell, leave-drug |
| Bộ đo | Faber, recall@k, main@k, path-Jaccard, Fid±, stability, rewiring-survival | ROAR (phải train lại, tốn nhất) |
| Dữ liệu thật | O'Neil, KEGG | NCI-ALMANAC, STRING toàn bộ |

Phần lõi đã trả lời đủ RQ1 đến RQ3. Nếu đến tháng 6 phần lõi chưa xong, cắt phần mở rộng chứ không kéo dài lộ trình.

---

## Phần 4. Quá trình training và thí nghiệm

### 4.1. Pipeline dữ liệu

```
DrugComb summary ──lọc ONEIL──┐
DepMap expression ────────────┼─ khớp tên cell line ─┐
DrugBank / ChEMBL targets ────┘                      ├─ giữ gen ∈ (mạng ∩ biểu hiện ∩ 2-hop quanh đích)
STRING ≥ 700 / KEGG ──────────────────────────────────┘
        │
        ▼
   một file .pt: danh sách gen, ma trận kề, ma trận biểu hiện (cell × gen, đã z-score),
                 ma trận đích (thuốc × gen), danh sách bộ ba, nhãn 3 lớp
        │
        ▼
   chia train / val / test theo split (mục 4.4)
```

Viết script kiểm tra ngay sau bước này: số bộ ba bị loại vì thiếu biểu hiện, số thuốc không có đích, phân bố nhãn ở ngưỡng 5, 10, 20. Với O'Neil ở ngưỡng ±10, lớp add thường chiếm đa số, nên phải biết tỷ lệ chính xác trước khi chọn loss.

### 4.2. Thiết kế dữ liệu bán tổng hợp

Ý tưởng: dùng mạng thật, cell line giả, thuốc giả, và một luật sinh điểm mà mình biết rõ.

**Cơ chế hiệp đồng cài sẵn, theo mẫu Complementary Exposure của Cheng:**

1. Trên mạng thật, chọn một gen hội tụ g\*.
2. Chọn hai đường dẫn rời nhau P_A = a → x1 → x2 → g\* và P_B = b → y1 → g\*.
3. Nhóm thuốc S_A có đích a, nhóm thuốc S_B có đích b.
4. Điểm hiệp đồng tăng khi A ∈ S_A, B ∈ S_B **và** các gen trên cả hai đường cùng biểu hiện cao trong cell c:

```
score(A,B,c) = 30 · [A∈S_A, B∈S_B] · relu( mean expr_c(P_A ∪ P_B) )      ← tương tác thật
             − 30 · [A∈S_A, B∈S_C] · relu( mean expr_c(P_W) )            ← đối kháng, đường khác
             + 20 · ([A∈S_M] + [B∈S_M]) · mean expr_c(M)                 ← hiệu ứng chính, KHÔNG phải tương tác
             + N(0, 4)                                                    ← nhiễu
```

Gọi ba nhóm gen này là Z (trên P_A ∪ P_B), W (trên P_W) và M (một cụm gen nằm xa cả hai đường). Đặt chúng lên mạng thật là điểm khác với các benchmark XAI đồ thị thông thường, vốn cài motif lên đồ thị ngẫu nhiên: ở đây "đường dẫn" có nghĩa vì nó đi trên topo sinh học thật. Để thấy topo đóng góp bao nhiêu, chạy thêm một bản đặt cùng ba nhóm lên mạng ngẫu nhiên cùng số node và cạnh.

Ground truth là tập cạnh của P_A ∪ P_B (cho syn) và P_W (cho ant). Nhóm M là bẫy: thuốc thuộc S_M đẩy điểm lên với **mọi** đối tác, nên explainer tốt ở cấp interaction phải bỏ qua M. Cho S_M giao một phần với S_A và S_B, để có những cặp mang cả tương tác thật lẫn hiệu ứng chính.

**Bẫy cần tránh:** đích a và b là hai đầu của đường dẫn, nên explainer nào cũng dễ "trúng" chúng chỉ vì chúng có cờ tA = 1. Khi chấm recall, chỉ chấm **các gen và cạnh trung gian** (x1, x2, y1, g\* và cạnh giữa chúng), bỏ qua đích.

**Ba kiểu cơ chế** để reviewer khó bắt bẻ "dữ liệu do mình tự thiết kế cho dễ": (1) hội tụ hai nhánh như trên, (2) một nhánh bù trừ (thuốc B chặn đường vòng mà tế bào dùng để thoát thuốc A), (3) cặp gây chết tổng hợp lấy từ SynLethDB.

**Các núm vặn để trả lời RQ3:** số cell line (40, 100, 300), số thuốc, tỷ lệ bộ ba lặp lại, mức nhiễu.

### 4.3. Kiểm tra Faber (bắt buộc trước khi chấm recall)

Faber, Moghaddam & Wattenhofer (KDD 2021) chỉ ra rằng GNN có thể dự đoán đúng mà không hề dùng motif đã cài, và khi đó recall thấp là lỗi của mô hình chứ không phải của explainer. Cách kiểm tra: ở tập test, đặt biểu hiện các gen trên P_A ∪ P_B về 0 (mức trung bình). Nếu F1 lớp syn không giảm rõ, mô hình không dùng cơ chế, và mọi con số recall sau đó vô nghĩa. Ghi kết quả này thành một bảng riêng trong luận văn.

### 4.4. Ba kiểu chia dữ liệu

Ví dụ với 4 thuốc (A, B, C, D) và 2 cell line (c1, c2):

| Split       | Test chứa       | Ví dụ test       | Train không bao giờ thấy                                                         |
| ----------- | ---------------- | ------------------ | ----------------------------------------------------------------------------------- |
| leave-combo | cặp thuốc mới | (A,B,c1), (A,B,c2) | cặp (A,B) ở bất kỳ cell nào; nhưng A và B vẫn xuất hiện với thuốc khác |
| leave-drug  | thuốc mới      | mọi bộ ba có D  | thuốc D                                                                            |
| leave-cell  | cell line mới   | mọi bộ ba ở c2  | cell c2                                                                             |

Split ngẫu nhiên (trộn bộ ba) chỉ dùng để so với số liệu đã công bố, vì cùng cặp (A,B) ở cell khác nhau rơi vào cả train lẫn test, mô hình chỉ cần nhớ. Viết một test tự động: giao giữa tập cặp thuốc của train và test phải rỗng trong leave-combo. Leave-drug cũng có test tương tự: không thuốc nào của test xuất hiện trong train.

Với leave-drug có một điểm riêng cho bài toán giải thích: thuốc mới vẫn có đích đã biết, nên GNN vẫn đặt được cờ tA trên mạng, còn one-hot MLP thì không có gì để dùng. Nếu GNN có lợi thế thật nhờ mạng, đây là split nó phải thể hiện ra. Hai benchmark trong báo cáo cho PCC leave-drug chỉ khoảng 0,10 đến 0,13, nên đừng kỳ vọng số cao, chỉ cần so tương đối với one-hot.

### 4.5. Cấu hình train

| Thành phần      | Lựa chọn                                                | Lý do                                                          |
| ----------------- | --------------------------------------------------------- | --------------------------------------------------------------- |
| Loss              | Cross-entropy có trọng số lớp (1 / tần suất)        | Lớp add chiếm đa số                                         |
| Optimizer         | AdamW, lr khoảng 1e-3, weight decay 1e-4                 | Mặc định an toàn; dò lr trong {3e-4, 1e-3, 3e-3} trên val |
| Batch             | 256 bộ ba                                                | Vừa GPU phổ thông                                            |
| Early stopping    | theo QWK trên val, dừng sau 10 epoch không cải thiện | QWK phạt nặng nhầm syn ↔ ant                                |
| Seed × fold      | 5 × 5 cho kết quả chính                               | Một seed một fold không đủ để viết vào luận văn      |
| Metric dự đoán | QWK, macro-F1, F1 từng lớp, polar error (syn ↔ ant)    | Polar error là lỗi nguy hiểm nhất                           |

Ước lượng số lần train. Phần lõi của chặng 1: 1 kiến trúc × 2 mạng (thật, xáo giữ bậc) × 1 split × 25 (seed × fold) = 50 lần GNN, cộng 25 lần cho mỗi baseline học máy. Nếu một lần mất khoảng 2 phút trên GPU (đo lại sau lần chạy đầu), tổng chưa tới 4 giờ máy, chạy qua đêm là xong. Làm đủ cả phần mở rộng thì thành 3 kiến trúc × 4 mạng × 3 split × 25 = 900 lần, khoảng 30 đến 45 giờ. Mạng xáo phải tạo lại mỗi seed (seed khác, phép xáo khác), nếu không thì kết quả rewiring chỉ phản ánh một lần xáo may hay rủi.

Lần nào cũng lưu `config.json` (seed, fold, split, mạng, ngưỡng, loại điểm) cạnh `metrics.json`. Đến tháng 8 bạn sẽ có vài trăm thư mục trong `runs/`, và bảng kết quả trong luận văn được dựng bằng một script đọc các file này, không chép tay.

### 4.6. Quy trình một thí nghiệm hoàn chỉnh

```
1. sinh dữ liệu (bán tổng hợp) hoặc chuẩn bị (thật)
2. train mô hình trên mạng thật              → lưu checkpoint, metrics.json
3. train cùng mô hình trên 3 mạng đã xáo     → lưu checkpoint
4. train 4 baseline trên cùng split
5. kiểm tra Faber (chỉ bán tổng hợp)          → dừng ở đây nếu không qua
6. chạy 4 explainer × 3 cấp trên tập test
7. chấm: recall@k, main@k, path-Jaccard, Fid±, stability
8. so điểm giải thích giữa mạng thật và mạng xáo → rewiring-survival
9. ROAR: xóa top cạnh, train lại, đo hiệu năng
```

### 4.7. Các mốc ra quyết định (gate)

| Gate | Thời điểm   | Điều kiện                                                                                       | Nếu không qua                                                                                                  |
| ---- | -------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1    | cuối tháng 2 | Phân bố nhãn đủ lớp syn và ant ở ngưỡng chọn                                            | Đổi ngưỡng, hoặc gộp ALMANAC                                                                               |
| 2    | cuối tháng 4 | Kiểm tra Faber qua trên bán tổng hợp                                                          | Sửa luật sinh nhãn hoặc kiến trúc cho đến khi mô hình dùng cơ chế                                   |
| 3    | cuối tháng 6 | GNN trên mạng thật có thắng one-hot không, lời giải thích có sống qua xáo mạng không | Không thắng và vẫn sống: chuyển trọng tâm paper sang hướng phản biện, ngừng cải thiện kiến trúc |

---

## Phần 5. Kiến thức nền từ A đến Z, có ví dụ

Phần này viết cho người học máy nhưng chưa học sinh học. Mỗi mục trả lời: nó là gì, vì sao luận văn cần nó, và một ví dụ.

### 5.1. Sinh học tối thiểu

**Gen và protein.** Gen là một đoạn DNA mang công thức làm một protein. Protein là cỗ máy làm việc trong tế bào: nhận tín hiệu, truyền tín hiệu, cắt, nối, bật tắt gen khác. Trong dữ liệu, bạn gặp tên gen (EGFR, KRAS, BRAF, TP53) và thường coi "gen" với "protein do nó mã hóa" là một node.

**Biểu hiện gen (gene expression).** Mức độ một gen đang được "đọc" để làm protein trong tế bào, đo bằng RNA-seq, đơn vị TPM. Ví dụ: EGFR có log2(TPM+1) = 7,8 ở cell line A431 (rất cao, A431 nổi tiếng nhiều EGFR) và 1,2 ở một cell line máu. Đây là đặc trưng chính của cell line trong luận văn.

**Đột biến và CNV.** Đột biến là chữ cái sai trong gen (BRAF V600E: vị trí 600 đổi từ valine thành glutamate, làm BRAF luôn bật). CNV là số bản sao của gen bị tăng hoặc mất. Luận văn có thể chưa cần, nhưng cần biết để đọc bài.

**Cell line (dòng tế bào).** Tế bào ung thư lấy từ một bệnh nhân, nuôi được vô hạn trong phòng thí nghiệm. MCF7 là ung thư vú, A549 là ung thư phổi, A2058 là u hắc tố. Mỗi cell line có hồ sơ biểu hiện và đột biến riêng, nên cùng một cặp thuốc có thể hiệp đồng ở MCF7 mà đối kháng ở A549. Đó là lý do bài toán là bộ ba chứ không phải cặp.

**Đích thuốc (drug target).** Protein mà thuốc bám vào và thay đổi hoạt động. Trametinib bám MEK1/MEK2 và chặn chúng. Một thuốc có thể có nhiều đích, và có đích "ngoài ý muốn" (off-target).

**Pathway tín hiệu.** Chuỗi protein truyền tín hiệu, giống dây chuyền. Pathway MAPK, ví dụ quen nhất:

```
EGFR → RAS → BRAF → MEK1/2 → ERK1/2 → (nhân tế bào: tăng sinh)
```

BRAF bị đột biến V600E thì dây chuyền luôn chạy, tế bào phân chia không ngừng. Dabrafenib chặn BRAF, trametinib chặn MEK. Dùng chung, chúng chặn hai trạm trên cùng một dây chuyền. Đây là cặp thuốc đã được duyệt cho u hắc tố có BRAF V600, và là positive control của luận văn: đường dẫn kỳ vọng là BRAF → MEK1/2 → ERK. Cần kiểm tra cặp này có trong DrugComb không, và chỉ đánh giá trên cell line mang BRAF V600.

**Mạng PPI (protein–protein interaction).** Đồ thị: node là protein, cạnh là "hai protein này tương tác với nhau" (bám vào nhau, hoặc có bằng chứng liên quan). STRING cho mỗi cạnh một điểm tin cậy 0–1000; lọc ≥ 700 là "độ tin cậy cao". PPI của STRING không có hướng: nó không nói ai kích hoạt ai.

**Mạng có hướng, có dấu.** KEGG và OmniPath nói thêm chiều tín hiệu (BRAF → MEK, không phải ngược lại) và dấu (kích hoạt +, ức chế −). Thông tin giàu hơn nhưng phủ ít gen hơn.

**Gây chết tổng hợp (synthetic lethality).** Hai gen mà mất một cái thì tế bào vẫn sống, mất cả hai thì chết. Ví dụ kinh điển: BRCA1 và PARP1. Ung thư mất BRCA1 rất nhạy với thuốc ức chế PARP (olaparib). SynLethDB lưu các cặp như vậy, dùng để kiểm chứng cặp gen trong lời giải thích.

**DepMap CRISPR gene effect.** Người ta dùng CRISPR tắt từng gen trong từng cell line rồi đo tế bào sống được không. Điểm Chronos khoảng 0 là "tắt cũng chẳng sao", khoảng −1 là "giống các gen thiết yếu phổ biến". Nếu explainer nói gen X là mắt xích cơ chế ở cell c, thì X nên có điểm âm hơn ở các cell mà cặp thuốc hiệp đồng.

### 5.2. Dược lý: đo hiệu quả thuốc

**Đường cong liều–đáp ứng.** Cho tế bào nhiều mức liều, đo phần trăm tế bào bị ức chế. Đường cong thường hình chữ S.

**IC50.** Liều làm ức chế 50%. Thuốc mạnh có IC50 nhỏ. Ví dụ thuốc A có IC50 = 10 µM, thuốc B có IC50 = 20 µM.

**Ma trận liều tổ hợp.** O'Neil đo mỗi cặp ở lưới 4 × 4 liều. Mỗi ô là phần trăm ức chế khi trộn liều i của A với liều j của B. Điểm hiệp đồng tóm cả ma trận thành một con số.

**Monotherapy.** Dữ liệu đơn thuốc (chỉ A, hoặc chỉ B). Cần có để tính mức "mong đợi".

### 5.3. Các mô hình hiệp đồng, với một ví dụ tính tay

Ở một ô liều: A một mình ức chế 40%, B một mình ức chế 50%, A+B cùng lúc ức chế 85%. Có hiệp đồng không? Tùy bạn định nghĩa "mong đợi".

**HSA (Highest Single Agent).** Mong đợi = thuốc tốt hơn trong hai: max(0,40; 0,50) = 0,50. Dư = 0,85 − 0,50 = +0,35. Định nghĩa dễ dãi nhất.

**Bliss independence.** Coi hai thuốc tác động độc lập như hai sự kiện xác suất: E = E_A + E_B − E_A·E_B = 0,40 + 0,50 − 0,20 = 0,70. Dư = 0,85 − 0,70 = +0,15, tức điểm Bliss khoảng +15.

**Loewe additivity.** Coi B như "một phiên bản pha loãng của A". Tổ hợp là cộng tính nếu chỉ số tổ hợp CI = d_A/D_A + d_B/D_B = 1, trong đó d là liều đang dùng trong tổ hợp và D là liều mỗi thuốc cần để một mình đạt cùng mức hiệu quả. Ví dụ: để đạt 50% ức chế, A một mình cần 10 µM, B một mình cần 20 µM. Tổ hợp 2 µM A + 4 µM B đạt 50%. CI = 2/10 + 4/20 = 0,4 < 1, tức hiệp đồng mạnh (chỉ cần 40% "lượng thuốc tương đương"). CI > 1 là đối kháng. Điểm "synergy_loewe" trong DrugComb là một dạng chênh lệch phần trăm ức chế so với bề mặt Loewe, không phải CI, nên ngưỡng ±10 áp lên đơn vị phần trăm.

**ZIP.** Kết hợp ý tưởng của Loewe và Bliss, so sự thay đổi độ mạnh của từng thuốc khi có thuốc kia.

Bốn định nghĩa cho bốn con số khác nhau trên cùng một ô liều. Ví dụ trên: HSA nói +35, Bliss nói +15. Với ngưỡng 10, cả hai gọi là syn; nhưng nếu tổ hợp chỉ đạt 0,75 thì HSA cho +25 (syn) còn Bliss chỉ +5 (add). Nhãn của luận văn phụ thuộc vào lựa chọn này, nên phải báo cáo độ nhạy theo Loewe, Bliss, ZIP và ngưỡng 5, 10, 20.

### 5.4. Dược lý mạng: separation score của Cheng 2019

Cheng, Kovács & Barabási (*Nat Commun* 2019) đo xem đích của hai thuốc nằm gần hay xa nhau trên mạng:

```
s_AB = ⟨d_AB⟩ − ( ⟨d_AA⟩ + ⟨d_BB⟩ ) / 2
```

- ⟨d_AA⟩: với mỗi đích của A, khoảng cách ngắn nhất tới đích **khác** gần nhất của A; lấy trung bình.
- ⟨d_AB⟩: với mỗi đích (của A hoặc B), khoảng cách ngắn nhất tới đích gần nhất của thuốc kia; lấy trung bình.
- s_AB < 0: hai module đích chồng lấn. s_AB ≥ 0: tách biệt.

**Ví dụ.** Mạng đường thẳng: a1 — a2 — x — b1. Thuốc A có đích {a1, a2}, thuốc B có đích {b1}.

- ⟨d_AA⟩ = 1 (a1 cách a2 một bước, và ngược lại).
- ⟨d_BB⟩ = 0 (B chỉ có một đích, quy ước bằng 0).
- ⟨d_AB⟩: a1 → b1 mất 3 bước, a2 → b1 mất 2, b1 → a2 mất 2. Trung bình = 7/3 ≈ 2,33.
- s_AB = 2,33 − (1 + 0)/2 ≈ 1,83 > 0: tách biệt.

Phát hiện của Cheng: tổ hợp hiệu quả thường thuộc lớp "Complementary Exposure", hai module đích tách nhau nhưng cùng chạm module bệnh (p < 10⁻⁴). Nhưng AUC dự đoán chỉ 0,589. Topo mạng giải thích tốt hơn dự đoán, và đó là lập trường của cả luận văn: mạng là ngôn ngữ giải thích, cần được kiểm định, không phải bộ dự đoán.

**Random walk with restart (RWR).** Thả một người đi bộ ngẫu nhiên từ đích thuốc; mỗi bước có xác suất α quay về điểm xuất phát. Sau nhiều bước, xác suất người đó đứng ở mỗi gen cho ra "profile lan truyền" của thuốc. TranSynergy dùng α = 0,5 trên STRING. Có thể dùng RWR làm thêm một baseline explainer phi học máy.

### 5.5. Học máy trên đồ thị

**One-hot.** Thuốc số 2 trong 4 thuốc: [0, 1, 0, 0]. Không chứa thông tin sinh học nào, chỉ là tên. MLP one-hot giỏi nghĩa là bài toán giải được bằng cách nhớ.

**GCN (Kipf & Welling 2017).** Mỗi lớp, mỗi node lấy trung bình có trọng số đặc trưng của chính nó và hàng xóm:

```
H' = ReLU( Â · H · W ),    Â = D^(-1/2) (A + I) D^(-1/2)
```

A + I thêm cạnh tự vòng; D là ma trận bậc (đã tính tự vòng).

Ví dụ: mạng 1 — 2 — 3, đặc trưng h = [1, 0, 0] (chỉ node 1 "sáng"), W = 1. Bậc kể cả tự vòng: node 1 là 2, node 2 là 3, node 3 là 2.

- Â₁₁ = 1/2 = 0,5; Â₁₂ = 1/√(2·3) ≈ 0,408; Â₂₂ = 1/3 ≈ 0,333; Â₂₃ ≈ 0,408; Â₃₃ = 0,5.
- Sau lớp 1: node 1 = 0,5; node 2 ≈ 0,408; node 3 = 0. Tín hiệu mới lan một bước.
- Sau lớp 2: node 3 = Â₃₂ · 0,408 ≈ 0,167. Hai lớp thì tín hiệu đi được hai bước.

Vì vậy 2 lớp GCN chỉ "thấy" được đường dẫn dài tối đa 2 bước quanh mỗi node. Nếu bạn cài cơ chế dài 4 bước mà mô hình chỉ có 2 lớp, mô hình không thể dùng trọn cơ chế, và kiểm tra Faber sẽ báo điều đó.

**GAT.** Thay trọng số cố định Â bằng attention học được: mỗi node tự quyết hàng xóm nào quan trọng. Attention này hay bị đem ra làm lời giải thích, nhưng TranSynergy tự viết rằng attention có thể không giải thích được dự đoán, và Hu et al. (2024) cho thấy nhiễu nhỏ làm attention GAT đổi nhiều.

**Data leakage.** Thông tin tập test lọt vào train. Trong hiệp đồng thuốc, dạng phổ biến nhất là cùng cặp (A,B) ở cell khác nhau nằm cả hai bên khi chia ngẫu nhiên. Mô hình "dự đoán" giỏi nhờ nhớ cặp.

**Ghi nhớ danh tính, và vì sao one-hot thắng cả khi không rò rỉ.** Leave-combo chặn việc nhớ cặp, nhưng không chặn việc nhớ từng thuốc. O'Neil có 38 thuốc, nên mỗi thuốc ghép với 37 đối tác trên 39 cell line, tức xuất hiện trong khoảng 1.400 dòng. Ví dụ minh họa ở cell c1, điểm trung bình mọi cặp là 5. Trong train, thuốc A ghép với các thuốc khác cho trung bình 15, thuốc B cho trung bình 5. Cặp (A,B) chưa từng xuất hiện. Một mô hình chỉ biết tên đoán: 15 + 5 − 5 = 15, tức syn. Nếu điểm thật là 14, nó đúng mà không cần biết một gen nào.

Đây gọi là lặp lại bộ ba: mỗi thuốc và mỗi cell xuất hiện quá nhiều lần, nên mô hình học được "độ hiệp đồng trung bình" của từng thực thể. Con số dự đoán đó hoàn toàn cộng tính (phần của A cộng phần của B cộng phần của c), nên nó là hiệu ứng chính, đúng thứ cấp (iii) được thiết kế để trừ đi. Hệ quả cho luận văn: một mô hình đạt hiệu năng cao nhờ hiệu ứng chính sẽ có attribution cấp (iii) gần 0, và đó là một cách đo xem mô hình có học tương tác hay không.

### 5.6. XAI: giải thích mô hình

**Integrated Gradients (IG).** Đi từ một baseline x' (ví dụ toàn 0) tới đầu vào thật x theo đường thẳng, cộng dồn gradient dọc đường:

```
IG_i = (x_i − x'_i) · ∫₀¹ ∂f( x' + α(x − x') ) / ∂x_i  dα
```

Ví dụ: f(x₁, x₂) = x₁·x₂, x = (2, 3), x' = (0, 0).

- ∂f/∂x₁ tại αx là α·3, nên IG₁ = 2 · ∫₀¹ 3α dα = 2 · 1,5 = 3.
- Tương tự IG₂ = 3 · ∫₀¹ 2α dα = 3.
- IG₁ + IG₂ = 6 = f(x) − f(x'). Tính chất này gọi là completeness: tổng attribution bằng đúng mức thay đổi đầu ra. Viết test tự động kiểm tra nó.

**edge-IG.** Như trên, nhưng biến là mask cạnh m: baseline m = 0 (mạng rỗng), đầu vào m = 1. Điểm IG trên mỗi cạnh là mức đóng góp của cạnh đó.

Khác với IG trên biểu hiện gen: ở baseline m = 0, mọi gen chỉ còn tự vòng, GCN không truyền tin được, nên đầu ra baseline là "mô hình không có mạng". Tổng điểm IG trên cạnh vì vậy bằng đúng phần dự đoán mà mạng đóng góp. Nếu tổng này nhỏ so với logit, mô hình gần như không dùng mạng, và báo cáo con số đó trước khi đọc bất kỳ đường dẫn nào.

**Từ điểm cạnh sang đường dẫn, ví dụ.** Điểm cạnh đã chuẩn hóa về (0,1]. Đường 1 gồm hai cạnh điểm 0,9 và 0,8. Đường 2 gồm ba cạnh, mỗi cạnh 0,9. Chi phí −log: đường 1 là 0,105 + 0,223 = 0,328; đường 2 là 3 × 0,105 = 0,316. Đường 2 thắng dù dài hơn, vì −log biến tổng chi phí thành tích các điểm (0,729 so với 0,72). Muốn ưu tiên đường ngắn thì cộng thêm một hằng số phạt cho mỗi cạnh, và ghi giá trị đó vào luận văn vì nó đổi kết quả.

**Ba cấp giải thích, ví dụ cấp interaction.** Giả sử mô hình hoàn toàn cộng tính: Δ(X,Y) = u(X) + u(Y), với u(A) = 5, u(B) = 3, và trung bình u qua các thuốc tham chiếu là ū = 2.

```
Δ(A,B)          = 5 + 3     = 8
E_r Δ(A,r)      = 5 + 2     = 7
E_r Δ(r,B)      = 2 + 3     = 5
E_{r,r'} Δ(r,r')= 2 + 2     = 4
interaction     = 8 − 7 − 5 + 4 = 0
```

Mô hình cộng tính thì phần tương tác bằng 0, đúng như mong muốn. Nếu cặp (A,B) có thêm một số hạng riêng +20, interaction gần bằng 20 (trừ một hiệu chỉnh nhỏ khi E_r có tính cả A hoặc B). Cấp (ii) contrast sẽ cho 28 và không tách được phần nào là của riêng thuốc A. Đó là lý do cấp (iii) được kỳ vọng giảm main@k.

**Shapley interaction index.** Với hai "người chơi" i, j và một liên minh S: v(S∪{i,j}) − v(S∪{i}) − v(S∪{j}) + v(S). Cấp (iii) có cùng dạng, với "người chơi" là thuốc A và B.

**GNNExplainer (Ying et al. 2019).** Học một mask mềm trên cạnh, tối đa hóa việc giữ nguyên dự đoán, kèm phạt tổng mask (để ít cạnh) và phạt entropy (để mask gần 0 hoặc 1).

**PaGE-Link (Zhang et al., WWW 2023).** Explainer cho bài toán dự đoán liên kết: ép các cạnh được chọn phải nối thành đường dẫn từ nguồn tới đích, rồi trích k đường ngắn nhất trên đồ thị đã đánh trọng số theo mask. Bài toán hiệp đồng là bộ ba chứ không phải cặp, nên phải chỉnh: hai nguồn là đích A và đích B, mask được đối xứng hóa (m_e lấy trung bình khi hoán đổi A và B), ngữ cảnh cell nằm ở đặc trưng node. SDCInterpreter (*JCIM* 2026) cũng dựa trên PaGE-Link nhưng chạy trên đồ thị dị cấu, và metric đánh giá của họ chưa rõ.

**CF-GNNExplainer (Lucic et al., AISTATS 2022).** Tìm tập cạnh nhỏ nhất mà xóa đi làm đổi dự đoán. Ví dụ: xóa 3 cạnh BRAF–MEK1, BRAF–MEK2, MEK1–ERK2 làm dự đoán đổi từ syn sang add. Đây là "knockout trong máy tính", có thể đối chiếu với DepMap CRISPR.

### 5.7. Đánh giá lời giải thích, có ví dụ số

**recall@k.** Trong k gen (hoặc cạnh) có điểm cao nhất, bao nhiêu phần thuộc ground truth. Ground truth trung gian {x1, x2, y1, g\*}, top-3 của explainer {x1, g\*, EGFR}: recall@3 = 2/3 ≈ 0,67 tính trên 3 vị trí. Nhớ ghi rõ mẫu số (chia cho k hay cho kích thước ground truth) vì các bài dùng khác nhau.

**main@k.** Tỷ lệ gen hiệu ứng chính M lọt top-k. Càng thấp càng tốt.

**path-Jaccard.** Tập cạnh trên đường dẫn trích ra là E₁, tập cạnh ground truth là E₂: |E₁ ∩ E₂| / |E₁ ∪ E₂|. Ví dụ E₁ có 5 cạnh, E₂ có 6 cạnh, chung 4: 4 / (5 + 6 − 4) = 4/7 ≈ 0,57.

**Fid+ và Fid− (GraphFramEx, Amara et al. 2022).** Xác suất syn ban đầu là 0,82.

- Xóa top-5 cạnh của lời giải thích, xác suất còn 0,31: Fid+ = 0,82 − 0,31 = 0,51. Cao nghĩa là các cạnh đó **cần thiết**.
- Chỉ giữ top-5 cạnh, xóa phần còn lại, xác suất còn 0,74: Fid− = 0,82 − 0,74 = 0,08. Thấp nghĩa là các cạnh đó **đủ**.

**ROAR.** Fid± có một vấn đề: đồ thị bị xóa cạnh là thứ mô hình chưa từng thấy lúc train (out-of-distribution), nên xác suất tụt có thể chỉ vì đầu vào lạ. ROAR xóa top cạnh ở **cả** train và test, train lại từ đầu, rồi đo. Nếu hiệu năng vẫn giảm hơn so với xóa ngẫu nhiên cùng số cạnh, các cạnh đó mang thông tin thật.

**Stability.** Train 5 seed, lấy vector điểm cạnh của mỗi seed, tính cosine từng cặp. Janizek et al. (*Nat Biomed Eng* 2023) cho thấy ensemble nâng cosine từ 0,77 lên 0,98, nên báo thêm một baseline ensemble.

**Rewiring-survival rate.** Lấy top-k gen nằm trên các đường dẫn giải thích khi chạy trên mạng thật (T_thật) và trên mạng đã xáo (T_xáo, với mô hình train lại trên mạng xáo). Survival = |T_thật ∩ T_xáo| / k. Ví dụ k = 10, chung 8 gen: survival = 0,8. Con số này cao là **xấu**: lời giải thích gần như không phụ thuộc mạng thật, tức nó đến từ danh tính hoặc từ đích thuốc. Tính thêm một bản bỏ đích thuốc khỏi top-k, vì đích luôn "sống sót" (chúng có cờ tA = 1 trên mọi mạng).

**Degree-preserving rewiring, ví dụ.** Chọn hai cạnh (a, b) và (c, d), đổi thành (a, d) và (c, b). Mỗi node vẫn giữ đúng số cạnh, nhưng đường đi a → b không còn. Lặp đủ nhiều thì mọi đường dẫn cụ thể bị phá, còn phân bố bậc giữ nguyên.

### 5.8. Thống kê và metric dự đoán

**QWK (quadratic weighted kappa).** Đo độ khớp giữa nhãn dự đoán và nhãn thật cho nhãn có thứ tự (ant < add < syn), phạt lỗi theo bình phương khoảng cách. Nhầm syn thành ant (cách 2 bậc) bị phạt gấp 4 lần nhầm syn thành add (cách 1 bậc). QWK = 1 là khớp hoàn toàn, 0 là ngang đoán theo phân bố.

**Macro-F1.** Tính F1 cho từng lớp rồi lấy trung bình không trọng số, để lớp add chiếm đa số không che lớp syn và ant.

**Polar error.** Tỷ lệ nhầm giữa syn và ant. Báo riêng, vì khuyên dùng một cặp thuốc thực chất đối kháng là lỗi tệ nhất.

**PCC (Pearson).** Khi làm hồi quy điểm liên tục. Các bài trong báo cáo dùng PCC, nên tính thêm để so.

**Permutation test.** Để biết recall 0,35 có hơn ngẫu nhiên không: xáo ngẫu nhiên điểm cạnh 1.000 lần, tính recall mỗi lần, p-value là tỷ lệ lần recall ngẫu nhiên ≥ 0,35.

**Mean ± std qua seed × fold, và kiểm định ghép cặp.** So hai explainer trên cùng 25 lần chạy thì dùng Wilcoxon signed-rank, không dùng t-test hai mẫu độc lập.

---

## Phần 6. Lộ trình 12 tháng

| Tháng | Việc                                                                                                                                                                                                         | Sản phẩm cuối tháng                                         |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| 1      | Học phần 5. Đọc Cheng 2019, SynVerse, One-hot news, Faber 2021. Tải DrugComb, DepMap, STRING; đăng ký DrugBank. Dựng khung thư mục mục 3.6 | Notebook đọc dữ liệu, bảng map tên cell line |
| 2      | Viết `prepare.py` cho O'Neil, xem phân bố nhãn theo Loewe/Bliss/ZIP × ngưỡng 5/10/20. Viết SynergyGNN có mask cạnh, one-hot MLP, MLP DeepSynergy, bốn kiểu split; test đối xứng, test không rò rỉ | **Gate 1**; mô hình chạy được trên O'Neil |
| 3      | Viết `make_synthetic.py`: Z/W/M trên STRING/KEGG thật, 3 kiểu cơ chế, ground truth cấp cạnh. Viết `rewire.py` | Bộ dữ liệu bán tổng hợp + ground truth |
| 4      | Train trên bán tổng hợp; kiểm tra Faber; chỉnh số lớp GCN theo độ dài cơ chế                                                                                                                     | **Gate 2**                                                |
| 5      | Phần lõi: edge-IG 3 cấp, GNNExplainer cấp (i)(ii), trích đường dẫn; baseline s_AB và đường ngắn nhất; test completeness của IG theo m, test interaction = 0 với mô hình cộng tính. PaGE-Link và CF-GNNExplainer chỉ bắt đầu nếu phần lõi xong sớm | Bảng recall@k, main@k, path-Jaccard |
| 6      | Bốn biến thể mạng; Fid±, ROAR, stability, rewiring-survival; đủ 5 seed × 5 fold; trả lời RQ1–RQ3 trên bán tổng hợp                                                                             | **Gate 3**, bản nháp chương kết quả bán tổng hợp |
| 7      | Dữ liệu thật: O'Neil + ALMANAC/DrugComb, ba split                                                                                                                                                          | Bảng hiệu năng GNN vs baseline trên dữ liệu thật         |
| 8      | Explainer trên dữ liệu thật; rewiring-survival; độ nhạy theo loại điểm                                                                                                                              | Bảng survival trên dữ liệu thật                            |
| 9      | Kiểm chứng sinh học: DepMap, SynLethDB, enrichment MSigDB, positive control BRAF/MEK. Tùy chọn: lát cắt CF-GNNExplainer có dấu (Đề xuất 2)                                                        | Chương kiểm chứng sinh học                                 |
| 10     | Bản ngắn gửi workshop hoặc hội nghị (IEEE BIBM, ACM-BCB, workshop ML for drug discovery)                                                                                                                | Bản nộp                                                       |
| 11–12 | Viết luận văn; bản journal (*Bioinformatics*, *BIB*, *PLOS Comput Biol*); dọn code, công bố repo                                                                                                 | Luận văn hoàn chỉnh                                         |

---

## Phần 7. Rủi ro và cách xử lý

| Rủi ro                                                  | Dấu hiệu sớm                               | Xử lý                                                                                                               |
| -------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Mô hình không dùng cơ chế cài sẵn                | Kiểm tra Faber không qua                    | Tăng tín hiệu cơ chế, giảm nhiễu, thêm lớp GCN, bỏ embedding thuốc để chặn đường tắt                |
| Recall sụp khi ít cell line                            | Recall gần 0 khi giảm số cell xuống cỡ O'Neil (39) | Đây là một kết quả cho RQ3, không phải lỗi. Trên dữ liệu thật thì gộp ALMANAC/DrugComb để tăng cell |
| PaGE-Link không chuyển được sang bộ ba             | Mask không hội tụ, đường dẫn rời rạc | Giữ edge-IG và GNNExplainer làm kết quả chính, đưa PaGE-Link thành phần thử nghiệm                        |
| STRING quá lớn                                         | Hết bộ nhớ GPU                             | Giới hạn 2-hop quanh đích; dùng KEGG làm mạng chính                                                           |
| Reviewer chê dữ liệu bán tổng hợp "tự thiết kế" |                                               | Ba kiểu cơ chế, công bố script, bắt buộc kèm thí nghiệm rewiring trên dữ liệu thật                      |
| Thuốc thí nghiệm của O'Neil không có đích        | Nhiều thuốc MK-xxxx bị loại               | Báo số thuốc bị loại; phân tích giải thích chỉ trên thuốc có đích                                      |
| Nhãn nhiễu do khác loại điểm                       | Nhãn đổi nhiều giữa Loewe và ZIP        | Phân tích độ nhạy, báo lời giải thích ổn định đến đâu khi đổi loại điểm                          |

---

## Phần 8. Đọc gì, theo thứ tự

Tuần 1–2, nền tảng:

1. Cheng, Kovács & Barabási, *Nat Commun* 10:1197 (2019). Đọc phần định nghĩa s_AB và sáu lớp exposure.
2. O'Neil et al., *Mol Cancer Ther* (2016). Chỉ cần phần thiết kế thí nghiệm để hiểu dữ liệu đến từ đâu.
3. Preuer et al., DeepSynergy, *Bioinformatics* (2018). Baseline MLP mà mọi bài đều so.

Tuần 3–4, vấn đề của lĩnh vực:

4. SynVerse, Tasnina et al., *Brief Bioinform* 26(6):bbaf676 (2025).
5. One-hot news, Çandır et al., *Bioinformatics* 42(3):btag040 (2026).
6. Faber, Moghaddam & Wattenhofer, KDD 2021, về cạm bẫy khi so lời giải thích với ground truth.

Tháng 2, XAI trên đồ thị:

7. Sundararajan et al., Integrated Gradients, ICML 2017.
8. Ying et al., GNNExplainer, NeurIPS 2019.
9. Zhang S. et al., PaGE-Link, WWW 2023 (arXiv 2302.12465).
10. Amara et al., GraphFramEx, LoG 2022.
11. Azzolin et al., ICLR 2025, về giới hạn của metric faithfulness.

Khi viết chương liên quan:

12. TranSynergy (*PLOS CB* 2021), DeepSignalingFlow (*npj SBA* 2024), CASynergy (*PLOS CB* 2025), SDCInterpreter (*JCIM* 2026). Đây là bốn bài bạn sẽ đặt mình cạnh.
13. Janizek et al., *Nat Biomed Eng* 2023, về Shapley interaction và stability.

---

## Phụ lục: bảng thuật ngữ

| Tiếng Anh                 | Tiếng Việt / nghĩa trong luận văn                                 |
| -------------------------- | ---------------------------------------------------------------------- |
| drug synergy               | hiệp đồng thuốc                                                    |
| antagonism                 | đối kháng                                                           |
| additivity                 | cộng tính                                                            |
| cell line                  | dòng tế bào                                                         |
| drug target                | đích thuốc                                                          |
| gene expression            | biểu hiện gen                                                        |
| PPI network                | mạng tương tác protein–protein                                    |
| signaling pathway          | đường truyền tín hiệu                                            |
| synthetic lethality        | gây chết tổng hợp                                                  |
| monotherapy                | đơn trị liệu                                                       |
| dose–response             | liều–đáp ứng                                                      |
| leave-combination-out      | chia để test chứa cặp thuốc chưa thấy                           |
| ground truth               | đáp án đã biết (chỉ có ở dữ liệu bán tổng hợp)           |
| fidelity / faithfulness    | độ trung thực của lời giải thích với mô hình                 |
| degree-preserving rewiring | xáo mạng giữ nguyên bậc mỗi node                                 |
| counterfactual             | phản thực tế: "nếu xóa X thì dự đoán đổi"                   |
| main effect                | hiệu ứng chính: phần đóng góp riêng của một thuốc           |
| interaction effect         | hiệu ứng tương tác: phần chỉ xuất hiện khi có cả hai thuốc |

Một quyết định nên chốt từ bây giờ: đường dẫn giải thích nối từ đâu tới đâu. Chọn **từ đích A tới đích B**, như cách Cheng đo khoảng cách. Với kiểu cơ chế hội tụ, hai lựa chọn hóa ra trùng nhau: đi từ a qua x1, x2 tới g\* rồi ngược về y1 và b chính là P_A ∪ P_B, nên explainer không cần biết trước g\* nằm ở đâu. Với kiểu bù trừ, đường nối a với b thường đi qua điểm mà nhánh chính và nhánh vòng tách ra hoặc nhập lại, nên định nghĩa vẫn dùng được, miễn là lúc sinh dữ liệu bạn chọn nhánh vòng sao cho điều đó đúng. Kiểu gây chết tổng hợp thì khác: hai gen SL có thể không nối nhau trên mạng, nên ở kiểu này chỉ chấm recall cấp gen, không chấm path-Jaccard. Ghi rõ điều đó trong bảng kết quả, đừng để ô path-Jaccard của kiểu SL trống mà không giải thích.

Còn một câu planner này chưa trả lời: thuốc có nhiều đích (các thuốc ức chế đa kinase trong O'Neil như sorafenib, sunitinib, dasatinib) thì lấy cặp (đích A, đích B) nào để trích đường. Lấy hết thì số đường nổ theo tích số đích, lấy cặp gần nhất thì thiên vị đường ngắn. Chưa có lựa chọn nào rõ ràng tốt hơn, nên thử cả hai trên dữ liệu bán tổng hợp ở tháng 5 rồi mới quyết.
