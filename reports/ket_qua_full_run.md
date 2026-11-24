# Kết quả chạy đầy đủ pipeline planner_de_xuat_2 (16/11/2026)

Chạy toàn bộ mục 5.4 của [planner_de_xuat_2.md](planner_de_xuat_2.md) trên O'Neil, Loewe ±10, split leave-combo, 5 seed × 5 fold. Mọi con số dưới đây lấy từ [tables/tables.md](tables/tables.md), do `python -m src.eval.report` sinh ra từ `runs/*/metrics.json` và `runs/*/explain.pt`, không chép tay. Khoảng trong ngoặc vuông là CI 95% bootstrap của **hiệu** qua 25 run (seed × fold); riêng stability là CI qua 5 fold.

## Tóm tắt

1. **Mạng không giúp dự đoán.** GNN trên mạng thật không hơn GNN train lại với m = 0 (QWK hiệu −0,016 [−0,034; 0,001]) và không hơn GNN trên mạng xáo (−0,007 [−0,027; 0,010]). One-hot MLP, chỉ nhớ danh tính, thắng mọi mô hình có mạng: QWK 0,569 so với 0,369. Bảng độ nhạy cho cùng kết luận ở Bliss ±10 và Loewe ±5.
2. **Nhưng mô hình đã train vẫn dựa vào cạnh để tính.** Network share khoảng 0,5; đặt m = 0 làm 47% dự đoán trên tập test đổi lớp. Mô hình dùng đồ thị như một phần của phép tính, nhưng đồ thị thật không cho nó lợi thế gì so với một đồ thị xáo giữ bậc.
3. **Lời giải thích trung thực với mô hình.** Xóa 700 cạnh top theo edge-IG làm f tụt mạnh hơn hẳn xóa 700 cạnh ngẫu nhiên, ở cả ba cấp. Trên mạng thật, lời giải thích ổn định giữa các seed hơn hẳn trên mạng xáo (cosine 0,44 so với 0,05).
4. **RQ1: ở cấp gen, lời giải thích có phụ thuộc mạng thật, nhưng yếu, và mất đi ở cấp interaction.** Survival giữa mạng thật và mạng xáo thấp hơn survival giữa hai mạng xáo khoảng 0,07–0,085 (cấp logit và contrast). Ở cấp interaction và cấp đường dẫn, hiệu không khác 0.
5. **RQ2: kết quả trái chiều theo đơn vị đo.** Ở cấp đường dẫn, cấp interaction đặc hiệu theo cặp hơn cấp logit (+0,027 [0,022; 0,031]). Ở cấp top-k gen, cấp interaction lại kém cấp logit (−0,036 [−0,063; −0,003]) và không vượt explainer đường ngắn nhất.
6. **Case study không ủng hộ edge-IG hơn explainer ngây thơ.** Ở cả ba cặp, đường ngắn nhất giữa hai tập đích rơi vào pathway KEGG kỳ vọng nhiều hơn top-k gen của edge-IG.

Theo mục 1.4 của planner, kết quả nghiêng về **kết cục phản biện**: mạng không đóng góp cho dự đoán, nên "đường dẫn cơ chế" trên PPI không có cơ sở dự đoán đứng sau. Có một sắc thái đáng viết. Lời giải thích vẫn trung thực với mô hình, ổn định hơn trên mạng thật, và ở cấp gen có khác mạng xáo vượt null. Vậy explainer "nhìn thấy" mạng thật dù mạng thật không giúp mô hình dự đoán tốt hơn. Đây chính là tình huống mục 5.4 gọi là kết quả mạnh: mô hình không cần mạng, nhưng explainer vẫn in ra đường dẫn trông hợp lý.

## 1. Điều kiện tiên quyết

| Chỉ số | Thật | Null | Hiệu [CI 95%] |
|---|---|---|---|
| QWK GNN thật vs GNN m=0 train lại | 0,369 | 0,385 | −0,016 [−0,034; 0,001] |
| QWK GNN thật vs GNN xáo (TB xáo₁, xáo₂) | 0,369 | 0,375 | −0,007 [−0,027; 0,010] |
| QWK GNN thật vs one-hot MLP | 0,369 | 0,569 | −0,201 [−0,219; −0,185] |
| QWK GNN thật vs MLP kiểu DeepSynergy | 0,369 | 0,222 | +0,147 [0,125; 0,167] |
| Network share (contrast) | 0,484 | 0 | 0,484 [0,471; 0,501] |
| Network share (interaction) | 0,501 | 0 | 0,501 [0,478; 0,528] |
| Flip rate khi đặt m = 0, cùng mô hình | 0,468 | 0 | 0,468 [0,421; 0,522] |

Hai điểm cần đọc kỹ:

- GNN m = 0 (0,385) hơn MLP kiểu DeepSynergy (0,222), dù cả hai đều không có mạng. Chênh lệch này đến từ kiến trúc: phép chiếu dùng chung trọng số cho mọi gen và BatchNorm, không phải từ mạng. Vì vậy mốc so sánh đúng cho câu "mạng có giúp không" là GNN m = 0, không phải DeepSynergy.
- Network share và flip rate cao không mâu thuẫn với dòng 1–2. Mô hình train trên mạng nào thì học dựa vào mạng đó. Gỡ cạnh ra thì nó hỏng, nhưng một mô hình train từ đầu không có cạnh cũng làm tốt ngang.

## 2. Trung thực

| Cấp | Fid+ (xóa top-K) | Null (K ngẫu nhiên) | Hiệu [CI] | Completeness gap (trung vị) |
|---|---|---|---|---|
| logit | 6,58 | 0,002 | 6,58 [5,39; 7,83] | 5,8% |
| contrast | 8,99 | 0,001 | 8,99 [7,46; 10,67] | 5,5% |
| interaction | 1,74 | 0,000 | 1,74 [1,37; 2,15] | 19% |

- **Fid− không dùng được.** Khi chỉ giữ 700 cạnh top, logit tăng thay vì giữ nguyên (Fid− cỡ −30). Đồ thị chỉ còn 1% cạnh là ngoài phân phối, nên con số này phản ánh hành vi của mô hình trên đầu vào lạ chứ không đo độ trung thực. Báo trong bảng nhưng không dùng để kết luận.
- **Completeness ở cấp interaction kém hơn.** Cấp này là hiệu của bốn tích phân IG, mỗi tích phân mang sai số Riemann riêng, trong khi giá trị f của cấp này nhỏ.

| Stability (cosine giữa 5 seed) | Mạng thật | Xáo₁ | Xáo₂ |
|---|---|---|---|
| logit | 0,436 (null 0,092) | 0,053 | 0,043 |
| contrast | 0,409 (null 0,080) | 0,053 | 0,039 |
| interaction | 0,187 (null 0,027) | 0,012 | 0,015 |

Trên mạng thật, các seed khác nhau cho lời giải thích giống nhau gấp khoảng 8 lần trên mạng xáo, dù hiệu năng dự đoán ngang nhau. Đây là bằng chứng rõ nhất trong lần chạy này rằng cấu trúc của mạng thật để lại dấu vết trong lời giải thích. Mạng xáo phải tạo lại cho từng seed, nên một phần độ thấp ở cột xáo là do mỗi seed dùng một mạng xáo khác nhau. Vì vậy so sánh này nên đọc như "lời giải thích trên một mạng cố định có cấu trúc thì ổn định", chưa phải phép thử sạch.

## 3. RQ1: rewiring-survival

Thật = ½[s(thật, xáo₁) + s(thật, xáo₂)]; null = s(xáo₁, xáo₂). Hiệu âm nghĩa là lời giải thích phụ thuộc mạng thật.

| Cấp | Top-20 gen | Top-20 gen, bỏ đích | Gen trên đường dẫn | Gen trên đường dẫn, bỏ đích |
|---|---|---|---|---|
| logit | −0,067 [−0,086; −0,049] | **−0,085 [−0,110; −0,060]** | +0,008 [0,001; 0,014] | −0,007 [−0,012; −0,002] |
| contrast | −0,067 [−0,081; −0,054] | −0,076 [−0,094; −0,058] | +0,006 [−0,002; 0,014] | −0,003 [−0,008; 0,002] |
| interaction | −0,017 [−0,028; −0,008] | −0,007 [−0,018; 0,005] | 0,000 [−0,008; 0,008] | +0,002 [−0,002; 0,005] |

- Ở cấp gen bỏ đích, survival thật là 0,13 so với null 0,215. Lời giải thích trên mạng thật khác lời giải thích trên mạng xáo nhiều hơn mức hai mạng xáo khác nhau.
- Ở cấp interaction, top-k gen gần như giống nhau trên mọi mạng (survival 0,45–0,64, cả thật lẫn null). Giả thuyết cần kiểm tra: số hạng tham chiếu E_{r,r'} chỉ phụ thuộc cell, nên đẩy cùng một nhóm gen vào top-k của mọi bộ ba trong cùng cell.
- Ở cấp đường dẫn bỏ đích, survival gần 0 ở mọi nơi (khoảng 0,01). Đường dẫn chủ yếu dài 2–3 cạnh, nên tập gen trung gian rất nhỏ và khác nhau giữa bất kỳ hai mạng nào. Chỉ số này không phân biệt được gì. Nên tăng K_PATHS hoặc đo ở cấp cạnh nếu muốn dùng cấp đường dẫn.

## 4. RQ2: partner-specificity

Null = explainer đường ngắn nhất trên cùng bộ ba, cùng đối tác, cùng k. Hiệu dương nghĩa là edge-IG đặc hiệu theo cặp hơn null.

| Cấp | Top-20 gen, bỏ đích | Gen trên đường dẫn, bỏ đích |
|---|---|---|
| logit | +0,033 [0,007; 0,056] | +0,041 [0,034; 0,048] |
| contrast | +0,040 [0,012; 0,066] | +0,036 [0,029; 0,043] |
| interaction | −0,003 [−0,016; 0,012] | +0,060 [0,056; 0,064] |
| **(iii) − (i)** | **−0,036 [−0,063; −0,003]** | **+0,019 [0,015; 0,024]** |

Giả thuyết RQ2 (cấp interaction đặc hiệu hơn cấp logit) đúng ở cấp đường dẫn và sai ở cấp gen. Kết quả không đổi khi chỉ giữ các bộ ba mà mô hình dự đoán là syn (xem bảng đầy đủ). Specificity ở cấp đường dẫn cao (0,93–0,96) một phần vì tập gen trung gian nhỏ, nên Jaccard dễ về 0. Hiệu so với null vẫn có ý nghĩa vì null chịu đúng cùng hiệu ứng trần đó, nhưng biên độ 0,02–0,06 là nhỏ.

## 5. Baseline s_AB (Cheng)

Tương quan Spearman giữa s_AB của cặp với tỷ lệ syn qua các cell line (462 cặp): **ρ = −0,144 (p = 0,002) trên mạng thật**, −0,070 (p = 0,13) trên mạng xáo. Đích của hai thuốc càng gần nhau trên STRING thì cặp càng hay hiệp đồng. Tín hiệu yếu, nhưng chỉ có trên mạng thật. Thông tin ở cấp mạng vì vậy có tồn tại; chỉ là GNN không khai thác được nó cho dự đoán.

## 6. Case study (mục 2.6, 4.4)

Không cặp nào trong ba cặp của planner qua quy tắc "syn ở phần lớn cell line":
- PD325901 + MK-2206 syn ở 27% cell line.
- MK-8776 + gemcitabine syn ở 43%.
- ABT-888 + temozolomide bị loại vì temozolomide không có đích trên mạng (thuốc alkyl hóa DNA, không có đích protein trong bảng đích).

Theo bảng rủi ro ở phần 7, case study chuyển sang **định tính**. Tôi thêm AZD1775 (WEE1) + MK-8776 (CHK1), syn ở 70% cell line và là cặp duy nhất qua quy tắc. **Cần đọc tài liệu để có trích dẫn trước khi dùng cặp này.**

Tỷ lệ top-k gen (bỏ đích) nằm trong gene set KEGG kỳ vọng, cấp logit; trung bình qua 5 seed × các cell line syn:

| Cặp | Pathway | Edge-IG | Null: điểm cạnh ngẫu nhiên | Null: đường ngắn nhất |
|---|---|---|---|---|
| PD325901 + MK-2206 | hsa04010 + hsa04151 | 0,51 | 0,41 | 0,85 |
| MK-8776 + gemcitabine | hsa04110 + hsa03030 | 0,36 | 0,26 | 0,60 |
| AZD1775 + MK-8776 | hsa04110 | 0,15 | 0,26 | 0,90 |

- Edge-IG vượt null điểm cạnh ngẫu nhiên ở hai cặp của planner, nhưng **thua explainer đường ngắn nhất ở cả ba cặp**. Đường ngắn nhất giữa đích MEK và đích AKT tất nhiên đi qua MAPK/PI3K-Akt. Edge-IG thêm vào những gen mà mô hình dùng nhưng không nằm trong pathway.
- Ở cấp đường dẫn, edge-IG vượt null đường ngẫu nhiên cùng độ dài ở cấp logit/contrast, rõ nhất ở MK-8776 + gemcitabine: 0,86 so với 0,53.
- Danh sách gen xuất hiện nhiều nhất cho từng cặp nằm ở [tables/case_genes.csv](tables/case_genes.csv), để dùng cho phần thảo luận sinh học.

## 7. Độ nhạy theo loại điểm và ngưỡng (phụ lục)

Seed 0 × 5 fold, GNN thật, GNN m=0 và one-hot.

| Nhãn | ant / add / syn | QWK thật | QWK m=0 | Hiệu [CI] | QWK one-hot |
|---|---|---|---|---|---|
| Loewe ±10 | 23 / 70 / 6% | 0,354 | 0,394 | −0,040 [−0,097; 0,009] | 0,568 |
| Bliss ±10 | 4 / 87 / 9% | 0,290 | 0,271 | +0,019 [−0,010; 0,047] | 0,406 |
| Loewe ±5 | 36 / 45 / 19% | 0,437 | 0,483 | −0,045 [−0,059; −0,032] | 0,596 |
| Loewe ±20 | 13 / 87 / 0,6% | 0,193 | 0,204 | −0,011 [−0,106; 0,050] | 0,556 |

Kết luận "mạng không giúp dự đoán, one-hot thắng" giữ ở mọi biến thể. Ở Loewe ±5, mô hình không mạng còn hơn rõ. Loewe ±20 không dùng được vì lớp syn chỉ còn 0,6%. Bảng này mới tính các chỉ số dự đoán và flip rate, chưa chạy lại edge-IG.

Ghi chú cho Gate 1: ở Loewe ±10, lớp syn chỉ chiếm 6,4% (khoảng 1.380 trên 21.571 bộ ba), ant chiếm 23%. Như vậy đủ để train với trọng số lớp, nhưng F1 của lớp syn (khoảng 0,35) là điểm yếu nhất của mọi mô hình.

## 8. Lệch so với planner và giới hạn của lần chạy này

| Mục | Planner | Lần chạy này | Lý do |
|---|---|---|---|
| Số bộ ba được giải thích | tập test | 50 bộ ba syn thật mỗi fold (1.250 tổng), cùng bộ cho mọi seed và mạng | Chi phí: khoảng 10 phút GPU cho mỗi mô hình mạng thật |
| Chọn bộ ba | dự đoán syn | syn thật (có thêm bảng con "dự đoán syn") | Để mọi mạng giải thích đúng cùng bộ ba |
| Lọc mạng | 2-hop | 1-hop, 3.299 gen | Đã quyết ở Gate 1, xem `prepare.py` |
| Dò siêu tham số | lr, wd, dropout trên val | **chưa dò**, dùng mặc định (lr 1e-3, wd 1e-4, dropout 0,4) | Chưa làm; nên dò ít nhất cho GNN thật và m=0 trước khi chốt kết luận RQ0 |
| Bản có embedding thuốc (rủi ro "hiệu năng thấp") | có | chưa chạy | |
| DepMap CRISPR trong case study | có | chưa tải | |
| s_AB | interactome Cheng 2019 | STRING ≥ 700 đã lọc | Chưa tải interactome |
| Cặp đối chứng | 3 cặp | 2 cặp của planner + 1 cặp thêm | Xem mục 6 |
| Thuốc tham chiếu cho cấp interaction | 8, báo đổi khi lên 16 | 8, **chưa chạy bản 16** | |
| Fid± | K không nêu | K = 700 cạnh (khoảng 1%), 20 lần ngẫu nhiên | |
| Trích đường dẫn | phạt mỗi cạnh | phạt 1,0, k = 5 đường, top-20 gen | Các giá trị này đổi kết quả và cần ghi vào luận văn |

Chi tiết kỹ thuật cần ghi trong phần phương pháp:
- **Đường tích phân của IG là α = t³ với 32 bước**, không phải lưới đều. Chuẩn hóa bậc của GCN làm đầu ra thay đổi gần hết khi α < 0,05. Lưới đều 20 bước để lại sai số completeness lớn ngang f(1) − f(0); lưới t³ với 32 bước còn khoảng 6% (cosine 0,999 so với tham chiếu 512 bước).
- Phép lan truyền GCN dùng sparse CSR. Các run train trước 16:40 ngày 16/11 dùng COO; cùng toán tử, và QWK test khi chạy lại hai mô hình cũ giống hệt.

Giới hạn chung: một kiến trúc, một cấu hình siêu tham số chưa dò, một bộ dữ liệu, một split. Mọi khẳng định trên chỉ ở mức "trên cấu hình này". Câu mạnh nhất được phép viết vẫn là câu ở mục 1.3 của planner, và lần chạy này mới đạt một phần của câu đó: trung thực (đạt), phụ thuộc mạng thật vượt null (đạt ở cấp gen cấp logit/contrast, không đạt ở cấp interaction), đặc hiệu theo cặp vượt null (đạt ở cấp đường dẫn, không đạt ở cấp gen cấp interaction).

## 9. Việc nên làm tiếp, theo thứ tự

1. Dò siêu tham số cho GNN thật và GNN m=0 trên val. Đây là phản biện đầu tiên reviewer sẽ đưa ra cho kết luận "mạng không giúp".
2. Kiểm tra giả thuyết ở mục 3: các số hạng tham chiếu E_{r,r'} có làm top-k của cấp interaction giống nhau giữa các bộ ba không (so sánh 8 với 16 thuốc tham chiếu, và nhìn top-k của riêng số hạng cell).
3. Sửa chỉ số cấp đường dẫn: tăng K_PATHS hoặc đo survival/specificity trên tập cạnh, vì tập gen trung gian hiện quá nhỏ.
4. Tìm trích dẫn cho cặp WEE1 + CHK1 và tải DepMap CRISPR cho case study.
5. Chạy edge-IG cho bảng độ nhạy nếu chương phụ lục cần nhiều hơn chỉ số dự đoán.

## Tái lập

```bash
python -m src.data.prepare                     # oneil.pt (đã có)
python -m src.training.sweep --workers 4       # 150 run: 4 mạng GNN + 2 baseline × 5 seed × 5 fold
python -m src.explain.sweep_explain --workers 4   # edge-IG cho 75 mô hình GNN (thật, xáo₁, xáo₂)
python -m src.explain.case_study
python -m src.training.sweep --workers 2 --seeds 0 --networks real none --baselines onehot --score bliss --threshold 10   # và loewe 5, loewe 20
python -m src.eval.report                      # reports/tables/*
python -m pytest src/tests -q                  # 10 test
```

Thời gian thực trên một A100 dùng chung: train khoảng 1–2 phút mỗi run GNN; explain khoảng 9 phút mỗi mô hình mạng thật và khoảng 3 phút mỗi mô hình mạng xáo; tổng cả pipeline khoảng 2,5 giờ với 4 worker.
