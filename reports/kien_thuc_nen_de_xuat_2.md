# Kiến thức nền cho đề xuất 2: từ con số 0 đến hiểu toàn bộ bài toán

Tài liệu này đi kèm [planner_de_xuat_2.md](planner_de_xuat_2.md). Planner là kế hoạch, còn file này giải thích mọi khái niệm mà planner dùng, viết cho người chưa từng học sinh học hay tin sinh. Nếu bạn biết chút Python và đã nghe tới "mạng nơ-ron" thì đủ để đọc. Phần nào bạn đã biết thì cứ lướt qua.

Mình dùng một ví dụ xuyên suốt cả tài liệu: **bộ ba (PD325901, MK-2206, A2058)**. PD325901 và MK-2206 là hai thuốc ung thư, A2058 là một dòng tế bào ung thư da. Tới cuối tài liệu, bạn sẽ thấy bộ ba này đi qua toàn bộ pipeline ra sao.

---

## Phần 0. Bài toán trong một trang

Đọc các bài báo về dự đoán phối hợp thuốc bằng học máy trên đồ thị, bạn sẽ gặp rất nhiều hình kiểu này:

```
thuốc A ức chế EGFR → tín hiệu đi qua MAPK1 → gặp nhánh của thuốc B ở ERK
→ "đây là cơ chế giải thích vì sao A và B hiệp đồng"
```

Mô hình dự đoán "A và B hiệp đồng", rồi một công cụ giải thích (explainer) in ra một đường đi trên mạng protein, và bài báo gọi đường đó là cơ chế sinh học. Khoảng 25 bài trong báo cáo tổng quan làm đúng như vậy.

Năm 2025 và 2026 có hai bài làm lung lay cách làm này:

- **SynVerse (2025)** xáo trộn mạng protein (giữ số liên kết của mỗi protein nhưng nối lung tung) rồi cho 16 mô hình chạy lại. Độ chính xác gần như không giảm. Một mô hình chỉ biết **tên** thuốc, không biết gì về sinh học, đứng ngang cả 16 mô hình.
- **One-hot news (2026)** cho thấy khi dữ liệu lặp đi lặp lại cùng các thuốc, công cụ giải thích chỉ tìm lại được đặc trưng thật ở mức trùng khớp 20 đến 40%.

Nghĩa là: có thể mô hình chỉ **nhớ tên thuốc**, và "đường dẫn cơ chế" in ra chỉ là thứ trông hợp lý mà thôi. Chưa ai kiểm tra điều này ở cấp **đường dẫn trên mạng**. Luận văn làm việc đó.

Luận văn **không** cố làm mô hình dự đoán giỏi hơn. Nó hỏi hai câu:

- **RQ1.** Đường dẫn giải thích trên mạng protein thật có khác đường dẫn trên mạng đã xáo không? Nếu y nguyên thì đường dẫn không đến từ sinh học.
- **RQ2.** Đường dẫn có thuộc về **cặp** thuốc (A, B) không, hay chỉ là thứ của riêng thuốc A, xuất hiện với bất kỳ đối tác nào?

Và mọi câu trả lời phải so với một **mốc ngẫu nhiên** (gọi là null), vì không ai biết đáp án đúng.

Để hiểu trọn mấy câu trên, bạn cần bốn mảng kiến thức: sinh học tế bào và thuốc (phần 1, 2), mạng sinh học (phần 3), học máy và học máy trên đồ thị (phần 5, 6), giải thích mô hình XAI (phần 8). Phần 9 là cách kiểm định khi không có đáp án, phần 10 ghép tất cả thành một flow chạy hoàn chỉnh.

---

## Phần 1. Sinh học tối thiểu

### 1.1. Tế bào, DNA, gen, protein

Cơ thể bạn có khoảng 37 nghìn tỷ tế bào. Mỗi tế bào chứa cùng một bộ **DNA**, một chuỗi rất dài gồm bốn "chữ cái" A, T, G, C, dài khoảng 3 tỷ chữ.

**Gen** là một đoạn DNA mang công thức để làm ra một **protein**. Người có khoảng 20 nghìn gen mã hóa protein. Bạn có thể hình dung DNA là một cuốn sách nấu ăn khổng lồ, mỗi gen là một công thức, còn protein là món ăn được nấu ra từ công thức đó.

**Protein** là thứ làm việc thật sự trong tế bào: nhận tín hiệu từ bên ngoài, chuyền tín hiệu vào trong, cắt nối phân tử, bật tắt gen khác. Mỗi protein có tên viết tắt, ví dụ:

| Tên | Làm gì (rất đơn giản hóa) |
|---|---|
| EGFR | "Ăng-ten" trên màng tế bào, nhận tín hiệu tăng trưởng |
| KRAS, BRAF | Trạm chuyển tín hiệu ngay dưới ăng-ten |
| MAP2K1, MAP2K2 (hay MEK1, MEK2) | Trạm chuyển tiếp ở giữa dây chuyền |
| MAPK1, MAPK3 (hay ERK2, ERK1) | Trạm cuối, mang lệnh "phân chia đi" vào nhân |
| AKT1, AKT2, AKT3 | Trạm trung tâm của một dây chuyền khác, ra lệnh "đừng chết, tiếp tục lớn" |
| TP53 | "Phanh khẩn cấp", ra lệnh tế bào hỏng tự hủy |

Trong dữ liệu và trong luận văn, người ta thường coi gen và protein do nó mã hóa là **một thứ**, một node trên mạng. Bạn sẽ thấy chữ "gen" và "protein" dùng lẫn nhau, và điều đó chấp nhận được.

### 1.2. Biểu hiện gen (gene expression)

Mọi tế bào có cùng DNA, nhưng tế bào gan và tế bào da làm những việc khác nhau vì chúng **đọc** những gen khác nhau, với cường độ khác nhau. Mức một gen đang được đọc gọi là **biểu hiện gen**.

Người ta đo biểu hiện bằng kỹ thuật RNA-seq, ra đơn vị TPM (số bản sao trên một triệu). Vì TPM chênh nhau rất xa (có gen 0, có gen 10 nghìn), dữ liệu thường được lấy log: `log2(TPM + 1)`.

Ví dụ: gen EGFR có log2(TPM+1) khoảng 7,8 ở dòng tế bào A431 (dòng này nổi tiếng có rất nhiều EGFR) và chỉ khoảng 1,2 ở một dòng tế bào máu. Cùng một gen, hai tế bào, hai mức rất khác.

Trong luận văn, **biểu hiện gen là thứ mô tả "tế bào này là ai"**. Mỗi dòng tế bào là một vector khoảng 20 nghìn con số.

### 1.3. Ung thư, đột biến

Ung thư là khi tế bào phân chia không ngừng và không chịu chết. Thường nguyên nhân là **đột biến**: một chữ cái sai trong gen làm protein hỏng theo kiểu nguy hiểm.

Ví dụ nổi tiếng: **BRAF V600E**. Ở vị trí 600 của protein BRAF, axit amin valine (V) bị đổi thành glutamate (E). Kết quả: BRAF bị "kẹt ở chế độ bật", liên tục gửi tín hiệu "phân chia đi" kể cả khi không có ai ra lệnh. Khoảng một nửa ca u hắc tố (ung thư da) có đột biến này.

**CNV** (copy number variation) là khi một gen bị nhân bản thành nhiều bản hoặc bị mất. Đề xuất 2 không dùng đột biến hay CNV làm đầu vào, nhưng bạn cần biết để đọc bài báo.

### 1.4. Dòng tế bào (cell line)

Tế bào ung thư lấy từ một bệnh nhân, nuôi được vô hạn trong phòng thí nghiệm. Mỗi dòng có tên riêng:

- **A2058**: u hắc tố, mang BRAF V600E. Đây là dòng trong ví dụ xuyên suốt.
- **MCF7**: ung thư vú.
- **A549**: ung thư phổi.

Vì mỗi dòng có hồ sơ biểu hiện và đột biến riêng, **cùng một cặp thuốc có thể hiệp đồng ở MCF7 mà đối kháng ở A549**. Đó là lý do đơn vị của bài toán là **bộ ba (thuốc A, thuốc B, dòng tế bào c)**, không phải cặp thuốc.

Một chuyện nhỏ nhưng tốn thời gian: cùng một dòng có thể được viết "NCI-H460", "NCIH460", "H460" ở các cơ sở dữ liệu khác nhau. Khớp tên giữa các nguồn mất vài ngày làm tay.

### 1.5. Pathway tín hiệu

Protein không làm việc một mình. Chúng chuyền tín hiệu cho nhau theo chuỗi, gọi là **pathway** (đường tín hiệu). Hai pathway bạn sẽ gặp nhiều nhất:

```
Pathway MAPK:    EGFR → KRAS → BRAF → MEK1/2 → ERK1/2 → (nhân tế bào: phân chia)

Pathway PI3K-Akt: EGFR → PI3K → AKT → mTOR → (tế bào lớn lên, không tự hủy)
```

Bạn hình dung đây là hai dây chuyền sản xuất trong một nhà máy, cùng nhận đơn hàng từ EGFR ở cổng. Chúng không tách biệt hoàn toàn: có những "hành lang nối" giữa hai dây chuyền, gọi là **crosstalk**.

Chi tiết này quan trọng cho ví dụ xuyên suốt. Khi bạn chặn dây chuyền MAPK (bằng thuốc ức chế MEK), tế bào thường **tự bật mạnh dây chuyền PI3K-Akt lên** để bù lại. Đây là cơ chế phản hồi đã được mô tả nhiều trong tài liệu. Nên nếu chỉ chặn MEK, tế bào ung thư vẫn sống qua đường AKT. Chặn cả MEK lẫn AKT thì tế bào mất cả hai lối thoát.

### 1.6. Gen thiết yếu và DepMap CRISPR

**CRISPR** là kỹ thuật "cắt" một gen cụ thể để tắt nó. Dự án **DepMap** tắt lần lượt từng gen trong hàng nghìn dòng tế bào, rồi đo tế bào còn sống được không. Kết quả là **điểm Chronos**:

- Khoảng 0: tắt gen này tế bào vẫn sống bình thường.
- Khoảng −1: tắt gen này tế bào chết, giống như tắt các gen thiết yếu phổ biến.

Ví dụ: tắt BRAF ở A2058 (dòng phụ thuộc BRAF V600E) cho điểm âm rõ, còn ở một dòng không có đột biến BRAF thì điểm gần 0.

Bẫy cần biết: có những gen thiết yếu với **mọi** tế bào (gen làm ribosome, nhà máy sản xuất protein). Chúng luôn có điểm âm, chẳng nói gì về cặp thuốc cụ thể. Phải loại nhóm này trước khi dùng DepMap để chấm lời giải thích.

---

## Phần 2. Thuốc và hiệp đồng thuốc

### 2.1. Đích thuốc (drug target)

Thuốc nhắm đích là phân tử nhỏ bám vào một protein cụ thể và thay đổi hoạt động của nó (thường là chặn lại). Protein bị bám gọi là **đích**.

Hai thuốc trong ví dụ xuyên suốt:

| Thuốc | Đích | Tác dụng |
|---|---|---|
| PD325901 | MAP2K1, MAP2K2 (MEK1, MEK2) | Chặn dây chuyền MAPK ở giữa |
| MK-2206 | AKT1, AKT2, AKT3 | Chặn dây chuyền PI3K-Akt ở trạm trung tâm |

Một thuốc có thể có nhiều đích, và có thể bám cả những protein ngoài ý muốn (off-target). Các cơ sở dữ liệu lưu đích thuốc: **DrugBank** (đầy đủ nhất, cần license học thuật), **ChEMBL**, **DGIdb**, **TTD**. Cuối cùng bạn chỉ cần một bảng hai cột:

```
drug,      gene
PD325901,  MAP2K1
PD325901,  MAP2K2
MK-2206,   AKT1
MK-2206,   AKT2
MK-2206,   AKT3
```

Vài thuốc trong bộ O'Neil mang mã nội bộ của Merck (MK-xxxx) và ít được chú giải đích. Thuốc nào không có đích thì bị loại khỏi phần giải thích đường dẫn, vì đường dẫn phải bắt đầu từ đích.

### 2.2. Đường cong liều–đáp ứng và IC50

Cho tế bào uống thuốc ở nhiều mức liều, đo phần trăm tế bào bị ức chế. Vẽ lên, bạn thường được một đường cong hình chữ S: liều thấp gần như không tác dụng, liều cao ức chế gần hết, ở giữa tăng nhanh.

**IC50** là liều làm ức chế 50%. Thuốc mạnh có IC50 nhỏ. Ví dụ thuốc A có IC50 = 10 µM, thuốc B có IC50 = 20 µM: A mạnh gấp đôi B.

**Monotherapy** là dữ liệu dùng một thuốc riêng lẻ. Cần nó để tính mức "mong đợi" khi trộn hai thuốc.

### 2.3. Hiệp đồng, cộng tính, đối kháng

Trộn hai thuốc, có ba khả năng:

- **Hiệp đồng (synergy, syn)**: hiệu quả **hơn** mức mong đợi. 1 + 1 > 2.
- **Cộng tính (additive, add)**: đúng mức mong đợi. 1 + 1 = 2.
- **Đối kháng (antagonism, ant)**: **kém** mức mong đợi. 1 + 1 < 2.

Câu hỏi khó là "mức mong đợi" bằng bao nhiêu. Có bốn định nghĩa phổ biến, cho bốn con số khác nhau trên cùng một thí nghiệm.

**Ví dụ tính tay.** Ở một mức liều: A một mình ức chế 40%, B một mình ức chế 50%, trộn A + B ức chế 85%.

**HSA (Highest Single Agent).** Mong đợi = thuốc tốt hơn trong hai = max(40%, 50%) = 50%. Dư = 85 − 50 = **+35**. Định nghĩa dễ dãi nhất.

**Bliss independence.** Coi hai thuốc tác động độc lập, như hai lần tung xúc xắc. Xác suất một tế bào thoát được cả hai là (1 − 0,4) × (1 − 0,5) = 0,3, vậy mong đợi ức chế = 1 − 0,3 = 70%. Công thức gọn: E = E_A + E_B − E_A·E_B = 0,4 + 0,5 − 0,2 = 0,7. Dư = 85 − 70 = **+15**.

**Loewe additivity.** Coi B như "một bản pha loãng của A". Dùng chỉ số tổ hợp:

```
CI = d_A / D_A + d_B / D_B
```

d là liều đang dùng trong hỗn hợp, D là liều mỗi thuốc cần để **một mình** đạt cùng mức hiệu quả. Ví dụ: để ức chế 50%, A một mình cần 10 µM, B một mình cần 20 µM. Hỗn hợp 2 µM A + 4 µM B đã đạt 50%. CI = 2/10 + 4/20 = 0,4. CI < 1 là hiệp đồng (chỉ cần 40% "lượng thuốc tương đương"), CI = 1 là cộng tính, CI > 1 là đối kháng.

Lưu ý: cột `synergy_loewe` trong DrugComb không phải CI, mà là chênh lệch phần trăm ức chế so với mức Loewe mong đợi. Nên ngưỡng ±10 áp lên đơn vị phần trăm.

**ZIP.** Kết hợp ý của Loewe và Bliss: xem độ mạnh của từng thuốc thay đổi bao nhiêu khi có mặt thuốc kia.

**Ví dụ đối kháng.** Nếu A + B chỉ ức chế 45%: HSA cho 45 − 50 = −5 (cộng tính nếu ngưỡng là ±10), Bliss cho 45 − 70 = −25 (đối kháng). Cùng một thí nghiệm, hai nhãn khác nhau.

### 2.4. Từ ma trận liều tới nhãn ba lớp

Bộ dữ liệu O'Neil đo mỗi cặp thuốc ở một lưới 4 × 4 liều. Mỗi ô là phần trăm ức chế. Một điểm hiệp đồng (ví dụ Loewe) tóm cả lưới thành **một con số** cho mỗi bộ ba.

Luận văn biến con số đó thành nhãn ba lớp:

| Điểm Loewe | Nhãn |
|---|---|
| > 10 | syn |
| từ −10 đến 10 | add |
| < −10 | ant |

Ba lớp có thứ tự tự nhiên: ant < add < syn. Thứ tự này dùng lại ở metric QWK (phần 5.7).

Vì nhãn phụ thuộc định nghĩa (một preprint báo Loewe và ZIP chỉ tương quan r = 0,28, và 21 đến 34% ma trận bị phương pháp này gọi là syn, phương pháp kia gọi là ant), luận văn chạy thêm một **bảng độ nhạy**: lặp lại kết quả chính với Bliss, và với ngưỡng ±5, ±20. Nếu kết luận đổi hẳn khi đổi ngưỡng, kết luận đó yếu.

### 2.5. Vì sao PD325901 + MK-2206 là ví dụ tốt

Nhớ lại phần 1.5: chặn MEK thì tế bào bật AKT lên để bù. PD325901 chặn MEK, MK-2206 chặn AKT. Trên giấy, đây là cặp hiệp đồng kinh điển, với pathway kỳ vọng là MAPK (KEGG hsa04010) và PI3K-Akt (hsa04151).

Nhưng "trên giấy" khác "trong dữ liệu". Luận văn chỉ giữ cặp này làm **đối chứng dương** nếu O'Neil thật sự ghi nhận nó là syn ở phần lớn dòng tế bào. Nếu dữ liệu nói add, mô hình không có lý do gì để giải thích nó là syn.

---

## Phần 3. Mạng sinh học

### 3.1. Đồ thị là gì

Một **đồ thị** gồm **node** (đỉnh) và **cạnh** (nối hai node). Mạng xã hội là đồ thị: người là node, "là bạn bè" là cạnh.

Vài khái niệm bạn sẽ gặp:

- **Bậc (degree)** của một node: số cạnh nối vào nó. Người có 500 bạn có bậc 500.
- **Hub**: node có bậc rất cao.
- **Đường đi (path)**: chuỗi node nối nhau bằng cạnh. Độ dài = số cạnh.
- **Khoảng cách** giữa hai node: độ dài đường đi ngắn nhất.
- **k-hop**: các node cách một node trong vòng k bước. "2-hop quanh đích thuốc" là mọi gen cách một đích nào đó tối đa 2 bước.

### 3.2. Mạng PPI và STRING

**PPI (protein–protein interaction)** là đồ thị mà node là protein, cạnh là "hai protein này tương tác với nhau" (bám vào nhau, hoặc có bằng chứng liên quan về chức năng).

**STRING** là cơ sở dữ liệu PPI lớn nhất. Mỗi cạnh có `combined_score` từ 0 đến 1000, gộp bằng chứng từ thí nghiệm, cơ sở dữ liệu khác, khai phá văn bản khoa học. Lọc `combined_score ≥ 700` nghĩa là chỉ giữ cạnh "độ tin cậy cao".

```
9606.protein.links.v12.0.txt.gz   (9606 là mã loài người)

protein1               protein2               combined_score
9606.ENSP00000...      9606.ENSP00000...      912
```

Hai điều quan trọng về STRING:

1. **Không có hướng.** Cạnh MEK1 — ERK2 chỉ nói hai protein liên quan, không nói ai kích hoạt ai. Khác với pathway ở phần 1.5 có mũi tên.
2. **Có hub rất lớn.** TP53 hay AKT1 nối với hàng trăm protein khác. Hub nằm trên rất nhiều đường đi, ở **bất kỳ** mạng nào có cùng phân bố bậc. Đây là lý do mọi chỉ số trong luận văn phải có null (phần 9).

Để chạy được trên máy phổ thông, luận văn chỉ giữ gen có trong cả STRING và bảng biểu hiện, và nằm trong vòng 2 bước quanh tập đích thuốc. Mạng còn dưới khoảng 3 nghìn gen.

### 3.3. KEGG: chỉ dùng để chấm điểm

**KEGG** là cơ sở dữ liệu pathway do con người vẽ tay, có hướng và có dấu (kích hoạt hay ức chế). Mỗi pathway có mã, ví dụ hsa04010 là MAPK, hsa04151 là PI3K-Akt. Bạn có thể lấy danh sách gen của mỗi pathway (gọi là **gene set**) qua MSigDB.

Bản 1 của planner dùng KEGG vừa làm mạng vừa làm thước chấm. Đó là vòng lặp: đường dẫn chạy trên mạng KEGG thì đương nhiên rơi vào pathway KEGG, chấm kiểu gì cũng đẹp. Giống như cho học sinh làm bài bằng sách giáo khoa rồi chấm điểm bằng chính sách đó. Bản 2 sửa: **STRING làm mạng, KEGG chỉ làm thước chấm**.

### 3.4. Dược lý mạng: khoảng cách giữa hai thuốc (s_AB của Cheng)

Cheng, Kovács và Barabási (*Nat Commun* 2019) đo xem đích của hai thuốc nằm gần hay xa nhau trên mạng:

```
s_AB = ⟨d_AB⟩ − ( ⟨d_AA⟩ + ⟨d_BB⟩ ) / 2
```

- ⟨d_AA⟩: với mỗi đích của A, tìm khoảng cách tới đích **khác** gần nhất của A, rồi lấy trung bình. Đo độ "chụm" của các đích A.
- ⟨d_AB⟩: với mỗi đích (của A hoặc B), khoảng cách tới đích gần nhất của thuốc kia, lấy trung bình.
- s_AB < 0: hai cụm đích chồng lên nhau. s_AB ≥ 0: tách biệt.

**Ví dụ.** Mạng là một đường thẳng `a1 — a2 — x — b1`. Thuốc A có đích {a1, a2}, thuốc B có đích {b1}.

- ⟨d_AA⟩ = 1 (a1 cách a2 một bước, và ngược lại).
- ⟨d_BB⟩ = 0 (B chỉ có một đích, quy ước bằng 0).
- ⟨d_AB⟩: a1 → b1 mất 3, a2 → b1 mất 2, b1 → a2 mất 2. Trung bình = 7/3 ≈ 2,33.
- s_AB = 2,33 − (1 + 0)/2 ≈ 1,83 > 0: tách biệt.

Phát hiện của Cheng: các tổ hợp hiệu quả thường có hai cụm đích **tách nhau** nhưng cùng chạm vùng bệnh. Nhưng khi dùng s_AB để **dự đoán**, độ chính xác chỉ AUC 0,589, gần đoán mò (0,5). Mạng giải thích tốt hơn là dự đoán. Luận văn đứng ở đúng lập trường này: mạng là ngôn ngữ để giải thích, và ngôn ngữ đó cần được kiểm định.

Trong luận văn, s_AB là một **baseline giải thích không dùng học máy**: nếu một explainer học máy không làm tốt hơn một công thức khoảng cách, nó chẳng có giá trị gì thêm.

### 3.5. Đường đi ngắn nhất làm explainer

Explainer "ngây thơ nhất" có thể nghĩ ra: nối đích A với đích B bằng đường đi ngắn nhất trên mạng, rồi bảo đó là cơ chế. Không cần mô hình, không cần dữ liệu hiệp đồng.

Ví dụ với cặp trong ví dụ xuyên suốt, một đường ngắn nhất **minh họa** (chưa kiểm tra trên STRING thật) có thể là:

```
MAP2K1 (đích PD325901) — MAPK1 — RPS6KB1 — MTOR — AKT1 (đích MK-2206)
```

Explainer này quan trọng vì nó là **null của RQ2** (phần 9.5). Nó tự động đổi khi đổi thuốc đối tác, vì điểm cuối đổi. Nên bất cứ explainer nào muốn khoe "đặc hiệu theo cặp" đều phải vượt nó.

### 3.6. Xáo mạng giữ bậc (degree-preserving rewiring)

Đây là công cụ trung tâm của RQ1. Thuật toán rất đơn giản:

```
1. Chọn ngẫu nhiên hai cạnh (a, b) và (c, d).
2. Đổi thành (a, d) và (c, b).
3. Lặp lại thật nhiều lần (luận văn dùng 10 × số cạnh).
```

**Ví dụ.** Mạng có cạnh MEK1 — ERK2 và AKT1 — MTOR. Sau một lần đổi: MEK1 — MTOR và AKT1 — ERK2. MEK1 vẫn có đúng số cạnh như cũ, AKT1 cũng vậy, nhưng đường MEK1 → ERK2 không còn.

Lặp đủ nhiều thì **mọi đường đi cụ thể bị phá**, nhưng **mỗi protein giữ đúng số liên kết**. Hub vẫn là hub. Đích thuốc vẫn là đích thuốc. Thứ duy nhất mất đi là "ai nối với ai", tức chính phần thông tin sinh học.

Vì sao phải giữ bậc? Nếu xáo kiểu hoàn toàn ngẫu nhiên (Erdős–Rényi), hub biến mất, và khi kết quả đổi bạn không biết là do mất sinh học hay mất hub. Giữ bậc thì chỉ một thứ thay đổi.

Trong Python: `networkx.double_edge_swap(G, nswap=10*G.number_of_edges(), seed=...)`.

---

## Phần 4. Dữ liệu cụ thể của luận văn

### 4.1. O'Neil 2016 qua DrugComb

O'Neil et al. (Merck, *Mol Cancer Ther* 2016) đo **38 thuốc** trên **39 dòng tế bào**, ra khoảng **22–23 nghìn bộ ba**. Mọi bài báo trong lĩnh vực đều so trên bộ này, nên kết quả có chỗ đối chiếu.

Lấy qua **DrugComb** (một kho tổng hợp nhiều bộ dữ liệu phối hợp thuốc), lọc `study_name == "ONEIL"`, vì bản ở DrugComb có sẵn cả bốn loại điểm (Loewe, Bliss, HSA, ZIP).

Một dòng dữ liệu trông đại khái thế này:

```
drug_row   drug_col   cell_line_name   synergy_loewe   synergy_bliss ...
PD325901   MK-2206    A2058            [số]            [số]
```

### 4.2. DepMap / CCLE: biểu hiện gen

- `OmicsExpressionProteinCodingGenesTPMLogp1.csv`: ma trận dòng tế bào × gen, giá trị log2(TPM+1).
- `Model.csv`: bảng đổi mã nội bộ (ACH-000xxx) sang tên dòng tế bào.

### 4.3. Z-score

Biểu hiện được **chuẩn hóa z-score theo từng gen**: trừ trung bình, chia độ lệch chuẩn, tính qua các dòng tế bào.

**Ví dụ.** Gen EGFR có giá trị 2, 4, 6, 8 ở bốn dòng tế bào. Trung bình = 5, độ lệch chuẩn = √((9+1+1+9)/4) = √5 ≈ 2,24. Dòng có giá trị 8 thành z = (8 − 5)/2,24 ≈ 1,34, tức cao hơn trung bình 1,34 độ lệch chuẩn. Dòng có giá trị 5 thành z = 0.

Nhờ z-score, **số 0 nghĩa là "mức trung bình"**. Chi tiết này quan trọng cho Integrated Gradients (phần 8.3): khi cần một điểm "không có gì đặc biệt" để so sánh, z = 0 là lựa chọn tự nhiên.

### 4.4. Dữ liệu chỉ dùng để chấm điểm

| Nguồn | Dùng làm gì |
|---|---|
| Gene set KEGG (qua MSigDB) | Top gen trong lời giải thích có rơi vào pathway kỳ vọng không |
| DepMap CRISPR (`CRISPRGeneEffect.csv`) | Gen trên đường dẫn có thật sự cần cho dòng tế bào đó không |
| Interactome của Cheng 2019 | Tính s_AB đúng như bài gốc |

Mấy nguồn này **không bao giờ** đi vào mô hình. Nếu đi vào, bạn lại rơi vào vòng lặp như chuyện KEGG ở phần 3.3.

---

## Phần 5. Học máy cơ bản

Phần này dành cho người chưa học máy học bài bản. Nếu bạn đã quen PyTorch thì nhảy sang phần 6.

### 5.1. Mô hình là một hàm có tham số

Mô hình học máy là một hàm `f(x; θ)`: nhận đầu vào x, trả ra dự đoán, và có một đống tham số θ (trọng số). "Train" là chỉnh θ để dự đoán khớp với nhãn thật trên dữ liệu.

Trong luận văn: x là thông tin về bộ ba (A, B, c), dự đoán là một trong ba nhãn ant, add, syn.

### 5.2. Logit, softmax, cross-entropy

Mô hình phân loại ba lớp không trả ra nhãn ngay. Nó trả ra ba con số tùy ý, gọi là **logit**: z_ant, z_add, z_syn. Logit lớn nghĩa là mô hình nghiêng về lớp đó.

**Softmax** biến logit thành xác suất (dương, tổng bằng 1):

```
p_i = exp(z_i) / Σ_j exp(z_j)
```

**Ví dụ.** Logit = (ant 0,5; add 1,0; syn 2,0).
exp: 1,65; 2,72; 7,39. Tổng 11,76.
Xác suất: ant 0,14; add 0,23; syn 0,63. Mô hình đoán syn.

**Cross-entropy** đo mô hình sai bao nhiêu: loss = −log(xác suất của lớp đúng). Nếu nhãn thật là syn, loss = −log(0,63) ≈ 0,46. Nếu mô hình chỉ cho syn 0,05 thì loss = 3,0, phạt nặng.

**Trọng số lớp.** Ở ngưỡng ±10, lớp add thường chiếm đa số. Nếu không làm gì, mô hình lười sẽ đoán add mọi lúc. Luận văn nhân loss mỗi lớp với 1/tần suất của lớp đó, để lỗi ở lớp hiếm bị phạt nặng hơn.

Một điểm đáng nhớ: phần giải thích của luận văn làm việc trên **logit** (ví dụ z_syn), không phải trên xác suất. Logit là thứ "thô" hơn, cộng trừ được, nên dễ phân tích.

### 5.3. Gradient và optimizer

**Gradient** ∂loss/∂θ cho biết nếu nhích tham số θ một chút thì loss tăng hay giảm, nhanh cỡ nào. Train là lặp đi lặp lại: tính gradient, nhích θ ngược hướng gradient một bước nhỏ (bước này gọi là **learning rate**, lr).

**AdamW** là một cách nhích thông minh hơn (tự điều chỉnh bước cho từng tham số, có thêm weight decay để chống tham số phình to). Luận văn dùng lr 1e-3, weight decay 1e-4, và thử lr trong {3e-4, 1e-3, 3e-3}.

Gradient còn xuất hiện lại ở XAI (phần 8): gradient của **đầu ra theo đầu vào** cho biết đầu vào nào mô hình nhạy nhất. Đó là nền của Integrated Gradients.

### 5.4. Train, validation, test, early stopping

Dữ liệu chia ba phần:

- **Train**: mô hình học trên đây.
- **Validation (val)**: dùng để chọn siêu tham số và quyết định khi nào dừng.
- **Test**: chỉ dùng một lần cuối để báo kết quả.

**Overfitting** là khi mô hình học thuộc lòng train nhưng làm kém trên dữ liệu mới. **Early stopping**: theo dõi điểm trên val sau mỗi epoch (một lượt qua hết train), nếu 10 epoch liền không cải thiện thì dừng và lấy phiên bản tốt nhất.

### 5.5. Seed, fold, và vì sao chạy 25 lần

**Seed** là con số khởi tạo bộ sinh ngẫu nhiên. Đổi seed thì trọng số ban đầu khác, thứ tự dữ liệu khác, và kết quả hơi khác. Một kết quả chỉ đúng với một seed là kết quả may mắn.

**K-fold**: chia dữ liệu thành 5 phần, lần lượt lấy mỗi phần làm test. 5 seed × 5 fold = 25 lần chạy cho mỗi cấu hình. Từ 25 con số, bạn có trung bình và **khoảng tin cậy** (phần 9.9).

### 5.6. One-hot, MLP, embedding

**One-hot**: biểu diễn một thứ trong n thứ bằng vector n chiều, toàn 0 trừ một vị trí bằng 1. Thuốc số 2 trong 4 thuốc là [0, 1, 0, 0]. One-hot **chỉ chứa tên**, không có thông tin sinh học nào.

**MLP** (multi-layer perceptron) là mạng nơ-ron cơ bản nhất: vài lớp nhân ma trận xen kẽ hàm phi tuyến (ReLU, tức max(0, x)).

**Embedding** là một vector học được cho mỗi thực thể. Mỗi thuốc có một vector riêng, mô hình tự chỉnh vector đó trong lúc train. Về bản chất, embedding là one-hot nhân với một ma trận học được, nên nó cũng **chỉ là tên**, chỉ là tên được nén gọn.

Ba baseline học máy của luận văn:

| Baseline | Đầu vào | Câu hỏi nó trả lời |
|---|---|---|
| One-hot MLP | one-hot của A, B, c | Chỉ nhớ tên thì đạt bao nhiêu? |
| MLP kiểu DeepSynergy | biểu hiện gen của c + vector đích của A, B | Có sinh học nhưng không có mạng thì đạt bao nhiêu? |

Nếu mô hình đồ thị không thắng one-hot MLP, mạng không đóng góp gì cho dự đoán.

### 5.7. Metric dự đoán

**Vì sao không dùng accuracy.** Giả sử 100 bộ ba, 80 add, 10 syn, 10 ant. Mô hình lười đoán add hết: accuracy 80%, trông ổn, nhưng chẳng tìm được cặp syn nào.

**Macro-F1.** Tính F1 (trung bình điều hòa của precision và recall) cho từng lớp, rồi lấy trung bình **không trọng số**. Với mô hình lười trên: F1 của add ≈ 0,89, của syn = 0, của ant = 0, macro-F1 ≈ 0,30. Lộ ngay.

**QWK (quadratic weighted kappa).** Dành cho nhãn có thứ tự ant < add < syn. Phạt lỗi theo **bình phương khoảng cách**: nhầm syn thành ant (cách 2 bậc) bị phạt gấp 4 lần nhầm syn thành add (cách 1 bậc). QWK = 1 là khớp hoàn toàn, 0 là ngang đoán theo phân bố nhãn. Luận văn dùng QWK cho early stopping.

**Polar error.** Tỷ lệ nhầm giữa syn và ant. Báo riêng, vì khuyên bác sĩ dùng một cặp thuốc thật ra đối kháng là lỗi tệ nhất có thể.

### 5.8. Rò rỉ dữ liệu và split leave-combo

**Data leakage** là khi thông tin của test lọt vào train, làm điểm đẹp giả.

Ví dụ trong phối hợp thuốc: chia ngẫu nhiên các bộ ba, bộ (PD325901, MK-2206, MCF7) rơi vào train, bộ (PD325901, MK-2206, A2058) rơi vào test. Mô hình đã thấy cặp này hiệp đồng ở MCF7, đoán ở A2058 cũng hiệp đồng, và thường đúng. Nó không hiểu gì, nó nhớ cặp.

**Leave-combo** chặn điều này: mọi bộ ba của một cặp (A, B) phải nằm hết ở một phía. Test chỉ chứa cặp mà train **chưa từng thấy ở bất kỳ dòng tế bào nào**. Nhưng từng thuốc A, B vẫn xuất hiện trong train với đối tác khác.

```
train: (PD325901, gemcitabine, *), (MK-2206, ABT-888, *), ...
test:  (PD325901, MK-2206, *)     ← cặp mới, nhưng từng thuốc đã quen
```

Luận văn viết một test tự động: giao giữa tập cặp thuốc của train và test phải rỗng.

Leave-combo là split sát nhất với RQ2, vì nó buộc mô hình đối mặt với một **cặp** mới. Nhưng nó chưa chặn được kiểu nhớ thứ hai, nói ở phần 7.

---

## Phần 6. Học máy trên đồ thị

### 6.1. Ma trận kề

Đồ thị n node được viết thành **ma trận kề** A kích thước n × n: A[i][j] = 1 nếu có cạnh giữa i và j, ngược lại 0. Mạng không hướng thì A đối xứng.

Mạng `1 — 2 — 3`:

```
     1  2  3
1 [  0  1  0 ]
2 [  1  0  1 ]
3 [  0  1  0 ]
```

### 6.2. GCN: mỗi node hỏi ý kiến hàng xóm

**GCN** (Graph Convolutional Network, Kipf & Welling 2017). Mỗi lớp, mỗi node cập nhật đặc trưng bằng trung bình có trọng số của chính nó và các hàng xóm:

```
H' = ReLU( Â · H · W ),     Â = D^(-1/2) (A + I) D^(-1/2)
```

- A + I: thêm cạnh tự vòng, để node giữ lại thông tin của chính nó.
- D: ma trận bậc (đã tính cả tự vòng). Nhân D^(-1/2) hai bên để hub không lấn át (chuẩn hóa bậc).
- W: trọng số học được.

**Ví dụ tính tay.** Mạng `1 — 2 — 3`, mỗi node một đặc trưng h = [1, 0, 0] (chỉ node 1 "sáng"), W = 1. Bậc kể cả tự vòng: node 1 là 2, node 2 là 3, node 3 là 2.

- Â₁₁ = 1/2 = 0,5; Â₁₂ = 1/√(2·3) ≈ 0,408; Â₂₂ = 1/3 ≈ 0,333; Â₂₃ ≈ 0,408; Â₃₃ = 0,5.
- Sau lớp 1: node 1 = 0,5; node 2 ≈ 0,408; node 3 = 0. Tín hiệu lan đúng một bước.
- Sau lớp 2: node 3 = Â₃₂ × 0,408 ≈ 0,167. Tín hiệu tới được node cách 2 bước.

**Hệ quả quan trọng: L lớp GCN chỉ "thấy" được L bước.** GCN 2 lớp không thể kết hợp thông tin của hai node cách nhau 4 bước. Nếu đích của PD325901 và đích của MK-2206 cách nhau 4 bước trên STRING, thông tin "có thuốc A ở đây" và "có thuốc B ở kia" không bao giờ gặp nhau tại một gen nào. Vì vậy, **trước khi train**, luận văn đếm phân bố khoảng cách giữa đích hai thuốc trong mọi cặp của O'Neil. Thường cách nhau xa thì phải tăng số lớp.

### 6.3. Mô hình SynergyGNN của luận văn

Mỗi bộ ba (A, B, c) thành một đồ thị. Đồ thị **chính là mạng PPI**, lúc nào cũng như nhau. Thứ thay đổi giữa các bộ ba là **đặc trưng trên từng gen**. Mỗi gen g mang ba con số:

```
đặc trưng của gen g = [ expr_c(g),  tA(g) + tB(g),  tA(g) · tB(g) ]
```

- expr_c(g): biểu hiện (đã z-score) của gen g ở dòng tế bào c.
- tA(g) = 1 nếu g là đích của thuốc A, ngược lại 0. tB(g) tương tự.

**Ví dụ với bộ ba (PD325901, MK-2206, A2058):**

| Gen | expr | tA + tB | tA · tB | Ghi chú |
|---|---|---|---|---|
| MAP2K1 | [z ở A2058] | 1 | 0 | đích của PD325901 |
| AKT1 | [z ở A2058] | 1 | 0 | đích của MK-2206 |
| MAPK1 | [z ở A2058] | 0 | 0 | không phải đích |
| gen X giả định là đích của cả hai | ... | 2 | 1 | hai thuốc cùng đánh vào một gen |

**Vì sao dùng tổng và tích.** Đổi chỗ A và B thì tổng và tích không đổi. Mô hình **đối xứng sẵn**: (PD325901, MK-2206) và (MK-2206, PD325901) cho cùng đầu vào, cùng dự đoán. Hiệp đồng là quan hệ đối xứng, bắt mô hình tự học điều đó là lãng phí dữ liệu. Luận văn có một test: hoán đổi A và B, đầu ra phải y hệt.

Kiến trúc:

```
X (n_gen × 3)
   │  GCN lớp 1:  H1 = ReLU( Â_m · X  · W1 )
   │  GCN lớp 2:  H2 = ReLU( Â_m · H1 · W2 )
   │  chiếu mỗi gen xuống 4 chiều rồi nối tất cả lại (flatten)
   ▼
 MLP → 3 logit (ant, add, syn) → softmax
```

### 6.4. Ba quyết định thiết kế, và lý do

**1. Mask cạnh m nằm sẵn trong mô hình.** Mỗi cạnh e có một số m_e từ 0 đến 1, nhân vào ma trận kề trước khi chuẩn hóa bậc. m_e = 1 là cạnh còn nguyên, m_e = 0 là cạnh bị xóa, 0,5 là "nửa cạnh". Bình thường m = 1 hết, mô hình là GCN thường. Nhưng nhờ có m, ta tính được đạo hàm của đầu ra **theo từng cạnh**, và đó là thứ edge-IG cần (phần 8.4). Test: m = 1 phải cho đúng đầu ra của GCN thường.

**2. Flatten thay vì pooling trung bình.** Nhiều GNN cuối cùng lấy trung bình mọi node thành một vector. Làm vậy thì "gen MAPK1 có giá trị 0,7" và "gen AKT1 có giá trị 0,7" trộn vào nhau, danh tính gen biến mất. Flatten giữ nguyên vị trí từng gen, nên sau này nói "gen này quan trọng" mới có nghĩa.

**3. Không có embedding thuốc.** Embedding thuốc là đường tắt để mô hình nhớ tên (phần 5.6), mà nhớ tên đúng là thứ luận văn muốn loại trừ. Bỏ nó thì cách duy nhất để mô hình biết "thuốc nào" là đi qua cờ đích tA, tB trên mạng. Giá phải trả: độ chính xác sẽ thấp hơn các bài đã công bố. Không sao, vì luận văn không thi độ chính xác. Luận văn vẫn chạy thêm một bản có embedding để đối chiếu.

---

## Phần 7. Vấn đề "nhớ danh tính"

Đây là phần nối học máy với câu hỏi nghiên cứu, nên mình viết kỹ.

### 7.1. Một mô hình chỉ biết tên vẫn đoán giỏi

O'Neil có 38 thuốc. Mỗi thuốc ghép với 37 đối tác trên 39 dòng tế bào, tức xuất hiện trong khoảng 1.400 bộ ba. Lặp lại nhiều như vậy, mô hình học được "tính cách" của từng thuốc.

**Ví dụ.** Ở dòng tế bào c1, điểm trung bình của mọi cặp là 5. Trong train, thuốc A ghép với các thuốc khác cho trung bình 15 (A là thuốc "dễ hiệp đồng"), thuốc B cho trung bình 5. Cặp (A, B) chưa từng xuất hiện (leave-combo đã chặn). Mô hình chỉ biết tên đoán:

```
dự đoán(A, B) = phần của A + phần của B − mức nền = 15 + 5 − 5 = 15  →  syn
```

Nếu điểm thật là 14, nó đúng, mà không cần biết một gen nào.

Dự đoán kiểu này hoàn toàn **cộng tính**: phần của A cộng phần của B cộng phần của c. Trong thống kê, những phần này gọi là **hiệu ứng chính** (main effect). Thứ thật sự thuộc về cặp, phần mà A và B làm được **cùng nhau** và không làm được với ai khác, gọi là **hiệu ứng tương tác** (interaction effect).

Leave-combo chặn được việc nhớ **cặp**, nhưng không chặn được việc nhớ **từng thuốc**.

### 7.2. Hệ quả cho lời giải thích

Giả sử mô hình chủ yếu dùng hiệu ứng chính. Bạn hỏi explainer "vì sao (PD325901, MK-2206) là syn?". Explainer sẽ chỉ ra những gen quanh MEK, vì đó là thứ làm PD325901 "dễ hiệp đồng" nói chung. Hỏi "vì sao (PD325901, gemcitabine) là syn?", explainer lại chỉ ra **đúng những gen đó**. Đường dẫn trông rất sinh học, nhưng nó là đường dẫn của PD325901, không phải của cặp.

Đây chính là thứ RQ2 đo (partner-specificity), và là lý do có giải thích cấp tương tác (phần 8.6).

### 7.3. Một kịch bản tệ hơn nữa

Còn có thể tệ hơn: mô hình chẳng dùng mạng chút nào (chỉ dùng cờ đích và biểu hiện tại chỗ), nhưng explainer vẫn in ra một đường dẫn trông hợp lý, vì đường dẫn nào nối MEK với AKT trên STRING mà chẳng đi qua vài gen nổi tiếng. Đây là lý do luận văn có một **điều kiện tiên quyết**: kiểm tra mô hình có dùng mạng không, trước khi đọc bất kỳ đường dẫn nào (phần 9.2).

---

## Phần 8. XAI: giải thích mô hình

### 8.1. XAI là gì

**XAI** (Explainable AI) là các phương pháp trả lời câu hỏi "vì sao mô hình đưa ra dự đoán này?". Có nhiều dạng câu trả lời; dạng luận văn dùng là **attribution**: chia điểm "công lao" cho từng thành phần đầu vào.

Ví dụ đời thường: một mô hình duyệt vay tiền từ chối bạn. Attribution có thể nói: thu nhập −0,4, nợ hiện tại −0,3, tuổi +0,1. Nợ và thu nhập là lý do chính.

Trong luận văn, "thành phần đầu vào" là **các cạnh của mạng PPI**. Câu trả lời có dạng: cạnh MEK1 — ERK2 đóng góp +0,12 vào logit syn, cạnh AKT1 — MTOR +0,08, và cứ thế.

### 8.2. Hai tiêu chí mà người ta hay nhầm lẫn

- **Trung thực (faithfulness)**: lời giải thích có phản ánh đúng **mô hình** làm gì không.
- **Đúng sinh học (plausibility)**: lời giải thích có khớp với **sự thật sinh học** không.

Hai thứ này khác nhau. Một mô hình học sai (chỉ nhớ tên) thì lời giải thích trung thực của nó cũng phải "sai" sinh học. Ngược lại, một lời giải thích trông rất sinh học nhưng không phản ánh mô hình thì vô dụng, nó chỉ là thứ người ta muốn thấy.

Bài Faber, Moghaddam, Wattenhofer (KDD 2021) nhấn mạnh: phải kiểm tra mô hình trước khi trách explainer. Luận văn làm theo tinh thần đó.

### 8.3. Integrated Gradients (IG)

Gradient đơn thuần (∂f/∂x) chỉ nói độ nhạy **tại một điểm**, và có thể bằng 0 ngay cả khi đầu vào rất quan trọng (ví dụ khi ReLU đã bão hòa). IG (Sundararajan, Taly, Yan, ICML 2017) sửa bằng cách đi từ một điểm **baseline** x' tới đầu vào thật x theo đường thẳng, và cộng dồn gradient dọc đường:

```
IG_i = (x_i − x'_i) · ∫₀¹ ∂f( x' + α(x − x') ) / ∂x_i  dα
```

Hình dung: bạn đi từ chân núi (baseline, chẳng có gì) lên đỉnh (đầu vào thật). Mỗi bước, ghi lại độ dốc theo từng hướng. Cộng hết lại thì biết hướng nào đã góp bao nhiêu độ cao.

**Ví dụ 1 (hàm nhân).** f(x₁, x₂) = x₁·x₂, x = (2, 3), baseline x' = (0, 0).

- Trên đường đi, điểm là (2α, 3α). ∂f/∂x₁ = x₂ = 3α. IG₁ = 2 × ∫₀¹ 3α dα = 2 × 1,5 = 3.
- Tương tự IG₂ = 3 × ∫₀¹ 2α dα = 3.
- IG₁ + IG₂ = 6 = f(x) − f(x') = 6 − 0.

**Completeness.** Tổng attribution luôn bằng đúng mức thay đổi đầu ra từ baseline tới đầu vào thật. Tính chất này giúp luận văn rất nhiều (phần 8.5). Luận văn có test tự động kiểm tra nó.

Trong thực tế, tích phân được xấp xỉ bằng tổng: chia đoạn [0, 1] thành khoảng 50 bước, tính gradient ở mỗi bước, lấy trung bình.

**Chọn baseline.** Baseline phải là điểm "không có thông tin". Với biểu hiện gen đã z-score, baseline là 0 (mức trung bình, phần 4.3). Với cạnh, baseline là m = 0 (không có cạnh nào).

### 8.4. edge-IG: IG trên mask cạnh

Áp IG lên mask m (phần 6.4): baseline m = 0 (mạng rỗng), đầu vào m = 1 (mạng đầy đủ). Mỗi cạnh nhận một điểm IG, là mức đóng góp của cạnh đó.

**Ví dụ 2 (hai cạnh).** Giả sử logit syn phụ thuộc mask hai cạnh như sau:

```
f(m₁, m₂) = 1 + 2·m₁ + m₁·m₂
```

f(0, 0) = 1 (không mạng), f(1, 1) = 4 (đủ mạng). Trên đường đi m = (α, α):

- ∂f/∂m₁ = 2 + m₂ = 2 + α. IG₁ = 1 × ∫₀¹ (2 + α) dα = 2,5.
- ∂f/∂m₂ = m₁ = α. IG₂ = 1 × ∫₀¹ α dα = 0,5.
- Tổng = 3 = f(1,1) − f(0,0). Completeness đúng.

Cạnh 1 quan trọng hơn hẳn cạnh 2. Để ý phần tương tác m₁·m₂ (cạnh 2 chỉ có tác dụng khi cạnh 1 có mặt) được IG chia đều 0,5 cho mỗi bên.

### 8.5. Network share: mô hình có dùng mạng không

Ở baseline m = 0, mọi gen chỉ còn tự vòng, GCN không chuyền tin được giữa các gen. Đầu ra ở baseline đúng bằng "mô hình không có mạng". Nhờ completeness:

```
tổng edge-IG trên mọi cạnh = z_syn(có mạng) − z_syn(không mạng)
                           = phần logit mà mạng đóng góp
```

**Network share** = tổng đó chia cho z_syn khi có mạng.

**Ví dụ.** z_syn = 2,4 khi có mạng, 1,9 khi m = 0. Tổng edge-IG = 0,5, network share ≈ 21%. Mạng đóng góp khoảng một phần năm. Nếu ra 1% thì mạng gần như không tham gia, và mọi đường dẫn đọc ra sau đó đều đáng ngờ.

Trong ví dụ 2 ở trên: network share = 3/4 = 75%.

### 8.6. Ba cấp giải thích

Đây là phần mới nhất của luận văn. Câu hỏi "vì sao là syn" có thể hỏi theo ba cách, mỗi cách tính IG trên một đại lượng f khác nhau.

| Cấp | f | Câu hỏi |
|---|---|---|
| (i) logit | z_syn | Cạnh nào đẩy logit syn lên? Cách các bài báo đang làm |
| (ii) contrast | Δ = z_syn − z_add | Vì sao syn **thay vì** add? |
| (iii) interaction | Δ(A,B) − E_r Δ(A,r) − E_r Δ(r,B) + E_{r,r'} Δ(r,r') | Phần nào thuộc về **cặp**, sau khi trừ hiệu ứng riêng của từng thuốc? |

**Cấp (i)** đơn giản nhất nhưng có vấn đề: một cạnh có thể đẩy cả z_syn lẫn z_add lên cùng lúc (ví dụ một cạnh chỉ làm mô hình "tự tin hơn" nói chung). Nó trông quan trọng mà chẳng giúp phân biệt gì.

**Cấp (ii)** sửa điều đó: chỉ những cạnh làm syn **hơn** add mới được điểm. Ví dụ z_syn = 2,4, z_add = 1,8, Δ = 0,6.

**Cấp (iii)** đi xa hơn: trừ đi phần của riêng từng thuốc. Ký hiệu:

- Δ(A, B): contrast của cặp thật, ở dòng tế bào c.
- E_r Δ(A, r): trung bình contrast khi giữ A, thay B bằng các thuốc tham chiếu r khác. Đây là "tính cách riêng của A".
- E_r Δ(r, B): tương tự cho B.
- E_{r,r'} Δ(r, r'): trung bình khi thay cả hai. Đây là "mức nền của dòng tế bào c".

Công thức giống hệt cách tính hiệu ứng tương tác trong thống kê hai yếu tố: cặp trừ hàng trừ cột cộng tổng.

**Ví dụ 1: mô hình hoàn toàn cộng tính.** Δ(X, Y) = u(X) + u(Y), với u(A) = 5, u(B) = 3, trung bình u của các thuốc tham chiếu là ū = 2.

```
Δ(A,B)            = 5 + 3 = 8
E_r Δ(A,r)        = 5 + 2 = 7
E_r Δ(r,B)        = 2 + 3 = 5
E_{r,r'} Δ(r,r')  = 2 + 2 = 4
interaction       = 8 − 7 − 5 + 4 = 0
```

Mô hình chỉ nhớ tính cách từng thuốc thì phần tương tác bằng 0. Đúng như mong muốn.

**Ví dụ 2: có hiệu ứng riêng của cặp.** Thêm một số hạng +20 chỉ xuất hiện khi A gặp B: Δ(A, B) = 5 + 3 + 20 = 28. Các số hạng kia gần như không đổi (lệch một chút nếu A hoặc B nằm trong tập tham chiếu). Interaction ≈ 28 − 7 − 5 + 4 = 20. Cấp (iii) bắt đúng phần +20. Cấp (ii) cho 28 và không tách được bao nhiêu trong đó là của riêng A.

Vì IG tuyến tính theo f, attribution của cấp (iii) chỉ là cộng trừ attribution của các thành phần:

```
IG_iii = IG(A,B) − trung bình IG(A,r) − trung bình IG(r,B) + trung bình IG(r,r')
```

**Chi phí tính toán.** Không cần tính lại cho từng bộ ba. Số hạng E_{r,r'} chỉ phụ thuộc dòng tế bào c, tính một lần mỗi dòng. Số hạng E_r Δ(A, r) tính một lần cho mỗi cặp (thuốc, dòng tế bào) rồi lưu. Nếu vẫn chậm, lấy mẫu 8 thuốc tham chiếu và báo kết quả đổi bao nhiêu khi tăng lên 16.

**Liên hệ với Shapley interaction index.** Trong lý thuyết trò chơi, giá trị Shapley chia công lao cho từng người chơi. Grabisch và Roubens (1999) mở rộng ra công lao của **cặp** người chơi i, j:

```
v(S ∪ {i,j}) − v(S ∪ {i}) − v(S ∪ {j}) + v(S)
```

Đọc là: hai người cùng có mặt mang lại bao nhiêu, trừ đi phần mỗi người tự mang lại. Cấp (iii) có đúng dạng này, với "người chơi" là thuốc A và thuốc B. Janizek et al. (*Nat Biomed Eng* 2023) đã làm ý tương tự ở cấp gen trên mô hình cây; chưa ai làm ở cấp **cạnh** cho GNN hiệp đồng. Đó là đóng góp thứ hai của luận văn.

### 8.7. Từ điểm cạnh sang đường dẫn

edge-IG cho mỗi cạnh một con số. Người đọc lại muốn một **đường dẫn** từ đích A tới đích B. Cách chuyển:

```
1. Chuẩn hóa điểm cạnh về khoảng (0, 1].
2. Đặt chi phí mỗi cạnh = −log(điểm). Cạnh điểm cao thì rẻ.
3. Tìm k đường rẻ nhất giữa mọi cặp (đích A, đích B):
   networkx.shortest_simple_paths
```

**Bẫy của −log.** Tổng các −log bằng −log của tích, nên chi phí đường dẫn tương đương tích các điểm. Đường dài vẫn có thể thắng.

Ví dụ: đường 1 có hai cạnh điểm 0,9 và 0,8, chi phí 0,105 + 0,223 = 0,328 (tích 0,72). Đường 2 có ba cạnh điểm 0,9, chi phí 3 × 0,105 = 0,316 (tích 0,729). Đường 2 thắng dù dài hơn.

Muốn ưu tiên đường ngắn thì cộng một hằng số phạt cho mỗi cạnh. Giá trị phạt làm đổi kết quả, nên phải ghi vào luận văn.

**Hai cấp báo cáo.** Từ k đường dẫn, lấy ra **top-k gen** (các gen xuất hiện nhiều nhất trên đường, thường bỏ chính các đích thuốc). Mọi chỉ số ở phần 9 đều tính hai lần: trên tập top-k gen và trên tập đường dẫn. Hai cấp có thể cho kết luận khác nhau, và sự khác nhau đó đáng viết.

### 8.8. Các explainer khác (đã bị hoãn)

Bạn sẽ gặp chúng khi đọc bài, nên biết qua:

- **GNNExplainer** (Ying 2019): học một mask mềm trên cạnh sao cho giữ được dự đoán mà dùng ít cạnh nhất.
- **PaGE-Link** (Zhang 2023): ép các cạnh được chọn phải nối thành đường dẫn từ nguồn tới đích.
- **CF-GNNExplainer** (Lucic 2022): tìm tập cạnh nhỏ nhất mà xóa đi làm đổi dự đoán. Kiểu "knockout trong máy tính".
- **Attention của GAT**: hay bị lấy làm lời giải thích, nhưng có bằng chứng là nhiễu nhỏ làm attention đổi nhiều.

Đề xuất 2 chỉ dùng edge-IG, vì nó có completeness (cho network share) và dễ mở rộng ra ba cấp. Các explainer còn lại để cho một bài benchmark sau bảo vệ.

---

## Phần 9. Kiểm định khi không có đáp án

### 9.1. Vì sao không có đáp án, và làm gì thay thế

Không ai biết đường dẫn **thật** trong tế bào A2058 khi gặp PD325901 + MK-2206 ở cấp từng cạnh. Không có "đáp án" để so. Luận văn không bịa đáp án.

Hình dung bạn chấm bài thi mà không có đáp án. Bạn vẫn kiểm tra được vài điều:

1. **Học sinh có đọc đề không?** Đổi đề (xáo mạng) mà bài làm y nguyên thì học sinh chép mẫu có sẵn. Đây là RQ1.
2. **Bài làm có trả lời đúng câu hỏi không?** Đổi câu hỏi phụ (đổi thuốc đối tác) mà câu trả lời y nguyên thì học sinh chỉ viết về một chủ đề quen. Đây là RQ2.
3. **Học sinh có thật sự nghĩ vậy không?** Bài viết có phản ánh cách học sinh giải không (trung thực, Fid±).

Mỗi kiểm tra cần một **mốc ngẫu nhiên** để so. Đó là null.

### 9.2. Null là gì

**Null** (giả thuyết không) là câu trả lời cho: "nếu không có gì đặc biệt xảy ra, con số này sẽ bằng bao nhiêu?"

Ví dụ đời thường: bạn tung một đồng xu 10 lần ra 6 mặt ngửa. Đồng xu có lệch không? Phải biết đồng xu công bằng thường ra bao nhiêu (5, dao động khoảng 3 đến 7) thì mới trả lời được. Con số 6 đứng một mình không nói gì.

Lỗi lớn nhất của bản 1 là báo con số trần. "Rewiring-survival = 0,8" là cao hay thấp? Không biết. Bản 2 quy định: **mọi chỉ số đều báo dưới dạng (giá trị thật, giá trị null, hiệu)**, và mọi null phải đi qua **đúng bộ trích đường dẫn** như kết quả thật. Nếu null tính ở cấp cạnh còn kết quả thật ở cấp đường dẫn, chênh lệch có thể do bước trích đường gây ra chứ không phải do explainer.

### 9.3. Điều kiện tiên quyết: mô hình có dùng mạng không

Hai phép đo:

| Chỉ số | Null | Tốt khi |
|---|---|---|
| Network share (phần 8.5) | 0 | khác 0 rõ |
| QWK của mô hình m = 1 so với m = 0 | mô hình m = 0 | m = 1 hơn rõ |

Mô hình m = 0 là SynergyGNN train với mask bằng 0 cố định, tức chỉ còn tự vòng, không có mạng.

Nếu không qua, luận văn **vẫn chạy tiếp** mọi bước sau. Vì "mô hình không dùng mạng, **mà** explainer vẫn in ra đường dẫn trông hợp lý" là một kết quả mạnh hơn nhiều so với chỉ "mô hình không dùng mạng".

### 9.4. RQ1: rewiring-survival và null của nó

**Cách đo.** Train mô hình trên mạng thật, lấy top-k gen giải thích T_thật. Train lại một mô hình khác trên mạng xáo giữ bậc, lấy T_xáo. Đo phần trùng:

```
survival = |T_thật ∩ T_xáo| / k
```

Ví dụ k = 10, chung 8 gen: survival = 0,8. Cao là **xấu**: lời giải thích gần như không đổi khi phá mạng.

**Vấn đề.** Survival không bao giờ về 0, kể cả khi lời giải thích chẳng dính gì tới sinh học. Đích thuốc giống nhau trên mọi mạng, hub vẫn là hub, nên hai mạng bất kỳ cũng chia sẻ một phần top-k gen.

**Cách sửa.** Tạo **hai** mạng xáo độc lập (seed khác nhau), train trên từng mạng, đo survival giữa chúng. Hai mạng xáo chỉ có chung "bộ khung" (đích thuốc, phân bố bậc), không có chung sinh học. Phần trùng giữa chúng là mức sàn mà bộ khung tự tạo ra.

```
survival_thật = survival( T(mạng thật),  T(mạng xáo₁) )
survival_null = survival( T(mạng xáo₁),  T(mạng xáo₂) )
kết quả báo   = survival_thật − survival_null
```

**Đọc kết quả, hai ví dụ:**

| | survival_thật | survival_null | hiệu | Nghĩa là |
|---|---|---|---|---|
| Kịch bản 1 | 0,80 | 0,78 | +0,02 | Mạng thật chẳng khác một mạng xáo bất kỳ. Lời giải thích đến từ bộ khung, không đến từ sinh học |
| Kịch bản 2 | 0,35 | 0,70 | −0,35 | Mạng thật kéo lời giải thích về những gen mà mạng xáo không có. Lời giải thích phụ thuộc mạng thật |

Nên nhìn cả con số null, không chỉ hiệu. survival_null bằng 0,78 tự nó đã nói phần lớn top-k là đích và hub.

Tính thêm một bản **bỏ đích thuốc khỏi top-k**, vì đích luôn sống sót (chúng có cờ tA = 1 trên mọi mạng).

Mạng xáo phải tạo lại ở mỗi seed. Dùng một mạng xáo duy nhất thì kết quả chỉ phản ánh một lần xáo may hay rủi.

### 9.5. RQ2: partner-specificity và null của nó

**Jaccard** đo độ giống nhau của hai tập: |giao| / |hợp|. Hai tập giống hệt cho 1, không chung gì cho 0.

**Cách đo specificity.** Với bộ ba (A, B, c) được dự đoán syn:

1. Lấy T(A, B, c) = top-k gen trên đường dẫn, bỏ đích của A và B.
2. Chọn vài thuốc đối tác r **không chung đích với B** (để chắc đường dẫn có lý do để đổi).
3. Với mỗi r, lấy T(A, r, c), tính Jaccard với T(A, B, c).
4. specificity phía A = 1 − trung bình Jaccard.
5. Làm tương tự phía B (giữ B, đổi A), rồi lấy trung bình hai phía.

**Ví dụ.** k = 5. T(A, B) = {MAPK1, MAPK3, RAF1, AKT1, PIK3CA}. Hai đối tác r1, r2:

- T(A, r1) = {MAPK1, MAPK3, RAF1, EGFR, SRC}: chung 3, hợp 7, Jaccard = 3/7 ≈ 0,43.
- T(A, r2) = {MAPK1, MAPK3, RAF1, AKT1, KRAS}: chung 4, hợp 6, Jaccard = 4/6 ≈ 0,67.
- Trung bình 0,55, specificity phía A = 0,45.

MAPK1, MAPK3, RAF1 lần nào cũng có mặt. Nhiều khả năng chúng là "tính cách riêng" của thuốc A (phần 7.2). Một explainer cấp (iii) tốt sẽ đẩy chúng ra khỏi top-k và nâng specificity.

**Vấn đề.** Đường đi ngắn nhất tự nó đã đặc hiệu: đổi đối tác là đổi điểm cuối, đường đổi theo. Specificity 0,45 có thể chẳng hơn gì một explainer không học gì.

**Cách sửa.** Chạy đúng quy trình trên với explainer đường ngắn nhất (phần 3.5), cùng bộ đích, cùng k:

```
specificity_thật = specificity( edge-IG cấp (i) hoặc (iii) )
specificity_null = specificity( đường ngắn nhất )
kết quả báo      = specificity_thật − specificity_null
```

**Ví dụ minh họa (số giả định):**

| Explainer | specificity | trừ null 0,40 |
|---|---|---|
| Đường ngắn nhất (null) | 0,40 | 0 |
| edge-IG cấp (i) | 0,45 | +0,05 |
| edge-IG cấp (iii) | 0,70 | +0,30 |

Giả thuyết RQ2: cấp (iii) cho hiệu lớn hơn cấp (i). Nếu cả hai đều quanh 0, explainer học máy không đặc hiệu hơn một đường ngắn nhất, và các "đường dẫn cơ chế" theo cặp đã công bố đáng nghi ngờ.

### 9.6. Trung thực: Fid+ và Fid−

Fidelity (GraphFramEx, Amara 2022) kiểm tra lời giải thích có phản ánh mô hình không, bằng cách xóa cạnh rồi xem mô hình phản ứng ra sao. Ví dụ xác suất syn ban đầu là 0,82.

- **Fid+**: xóa top-5 cạnh của lời giải thích, xác suất còn 0,31. Fid+ = 0,82 − 0,31 = 0,51. Cao nghĩa là các cạnh đó **cần thiết**.
- **Fid−**: chỉ giữ top-5 cạnh, xóa hết phần còn lại, xác suất còn 0,74. Fid− = 0,82 − 0,74 = 0,08. Thấp nghĩa là các cạnh đó **đủ**.

**Null.** Xóa bất kỳ 5 cạnh nào cũng làm xác suất tụt một chút. Nên xóa **5 cạnh ngẫu nhiên**, lặp 20 lần, lấy trung bình. Giả sử xác suất còn trung bình 0,70, tức tụt 0,12. Hiệu = 0,51 − 0,12 = 0,39. Lời giải thích chọn cạnh tốt hơn hẳn chọn bừa.

**Vì sao không dùng ROAR.** Đồ thị bị xóa cạnh là thứ mô hình chưa từng thấy lúc train, nên xác suất có thể tụt chỉ vì đầu vào lạ. ROAR sửa bằng cách xóa ở cả train lẫn test rồi train lại, nhưng tốn kém nhất trong bộ đo. Fid± có null đã đủ cho luận văn, ROAR để dành nếu reviewer đòi.

### 9.7. Stability giữa các seed

Train 5 seed, mỗi seed cho một vector điểm cạnh. Tính **cosine** giữa từng cặp vector.

**Ví dụ** với 3 cạnh: seed 1 cho [0,9; 0,1; 0,5], seed 2 cho [0,8; 0,2; 0,4]. Tích vô hướng = 0,72 + 0,02 + 0,20 = 0,94. Độ dài: √1,07 ≈ 1,034 và √0,84 ≈ 0,917. Cosine = 0,94 / (1,034 × 0,917) ≈ 0,99. Rất ổn định.

Nếu cosine thấp, lời giải thích phụ thuộc may rủi của seed, và một đường dẫn đơn lẻ in trong bài báo không nói lên gì. Janizek 2023 cho thấy ensemble (gộp nhiều seed) nâng cosine từ 0,77 lên 0,98.

### 9.8. Case study: đối chứng dương với KEGG và DepMap

Phần này cho luận văn có thảo luận sinh học, **không dùng để kết luận chính**.

Ba cặp ứng viên (đều có trong O'Neil):

| Cặp | Lớp thuốc | Pathway kỳ vọng |
|---|---|---|
| PD325901 + MK-2206 | ức chế MEK + ức chế AKT | MAPK (hsa04010), PI3K-Akt (hsa04151) |
| MK-8776 + gemcitabine | ức chế CHK1 + chất tương tự nucleoside | chu kỳ tế bào (hsa04110), sao chép DNA (hsa03030) |
| ABT-888 + temozolomide | ức chế PARP + gây tổn thương DNA | sửa chữa cắt base (hsa03410) |

**Positive-control hit** = tỷ lệ top-k gen thuộc gene set KEGG kỳ vọng. Ví dụ cặp MEK + AKT, k = 10, có 6 gen thuộc hsa04010 hoặc hsa04151: hit = 0,6.

**Null**: 1.000 đường ngẫu nhiên **cùng độ dài** nối đích A với đích B, tính hit mỗi lần. Ví dụ trung bình 0,35. Phải cùng độ dài, vì đường ngẫu nhiên nối MEK với AKT cũng dễ đi qua gen MAPK hay PI3K, chỉ vì chúng nằm gần nhau.

Báo theo từng cặp, không gộp, vì chỉ có 2–3 cặp.

DepMap dùng tương tự: gen trên đường dẫn có điểm Chronos âm hơn ở những dòng tế bào mà cặp hiệp đồng không? Nhớ loại gen thiết yếu chung và so với các gen cùng bậc, nếu không thì kết quả chỉ phản ánh đường dẫn đi qua hub.

### 9.9. Thống kê dùng trong luận văn

**Permutation test (p-value).** Hit 0,6 có hơn ngẫu nhiên không? Trong 1.000 đường ngẫu nhiên, đếm bao nhiêu lần hit ≥ 0,6. Ví dụ 23 lần: p ≈ 23/1.000 = 0,023. Nghĩa là nếu explainer chọn bừa đường cùng độ dài, chỉ khoảng 2,3% số lần đạt được mức này.

**Khoảng tin cậy.** Từ 25 lần chạy (5 seed × 5 fold), bạn có 25 giá trị hiệu. Lấy trung bình và một khoảng (ví dụ 95%) mà giá trị thật nhiều khả năng nằm trong đó. Nếu khoảng tin cậy của hiệu chứa 0 thì chưa thể nói kết quả khác null.

**Wilcoxon signed-rank.** So hai explainer (ví dụ cấp (i) với cấp (iii)) trên **cùng** 25 lần chạy thì dữ liệu là cặp. Dùng Wilcoxon signed-rank, không dùng t-test hai mẫu độc lập.

**Bảng kết quả** trong luận văn luôn có ba cột:

```
| chỉ số               | giá trị thật | giá trị null | hiệu [khoảng tin cậy 95%] |
| survival (top-k gen) | 0,35         | 0,70         | −0,35 [−0,42; −0,28]       |   ← số minh họa
```

Không bảng nào chỉ có một cột.

---

## Phần 10. Flow chạy toàn bộ

### 10.1. Sơ đồ tổng thể

```
 ┌──────────────── DỮ LIỆU ────────────────┐
 │ DrugComb (lọc ONEIL) → nhãn syn/add/ant  │
 │ DepMap → biểu hiện gen, z-score          │
 │ DrugBank/ChEMBL → đích thuốc             │
 │ STRING ≥ 700, 2-hop quanh đích → mạng    │
 └──────────────────┬──────────────────────┘
                    ▼
        một file .pt + split leave-combo
                    │
     ┌──────────────┼───────────────────────────────┐
     ▼              ▼                               ▼
 mạng thật     mạng xáo₁, mạng xáo₂            m = 0 (không mạng)
     │              │                               │
     └──── train SynergyGNN, 5 seed × 5 fold ───────┘
                    │      + train 2 baseline học máy
                    ▼
     ĐIỀU KIỆN TIÊN QUYẾT: network share, QWK m=1 so với m=0
                    │   (không qua vẫn chạy tiếp)
                    ▼
     edge-IG 3 cấp (logit / contrast / interaction) trên tập test
                    │
                    ▼
     trích k đường dẫn, lấy top-k gen
                    │
     ┌──────────────┼──────────────┬────────────────────┐
     ▼              ▼              ▼                    ▼
 Fid± so với    stability     survival thật         specificity
 xóa ngẫu nhiên  giữa seed    trừ xáo₁-vs-xáo₂      trừ đường ngắn nhất
 (trung thực)                  (RQ1)                 (RQ2)
                    │
                    ▼
     case study 2–3 cặp: KEGG hit, DepMap, so với đường ngẫu nhiên
                    │
                    ▼
     một trong hai kết cục (phần 10.3)
```

### 10.2. Đi theo bộ ba (PD325901, MK-2206, A2058)

**Bước 1: chuẩn bị dữ liệu.** Lấy dòng (PD325901, MK-2206, A2058) từ DrugComb, đọc điểm Loewe, đổi thành nhãn (giả sử > 10, nhãn syn). Lấy vector biểu hiện của A2058, z-score theo gen. Lấy đích: PD325901 → MAP2K1, MAP2K2; MK-2206 → AKT1, AKT2, AKT3. Cắt STRING còn những gen trong vòng 2 bước quanh mọi đích thuốc của O'Neil.

**Bước 2: dựng đặc trưng.** Mỗi gen trong mạng nhận [expr ở A2058, tA + tB, tA · tB]. MAP2K1 có cờ 1, AKT1 có cờ 1, MAPK1 có cờ 0.

**Bước 3: split.** Cặp (PD325901, MK-2206) rơi vào test ở fold này. Mọi bộ ba của cặp này, ở mọi dòng tế bào, đều nằm trong test. PD325901 vẫn có mặt trong train cùng thuốc khác.

**Bước 4: train.** Train bốn phiên bản SynergyGNN: trên mạng thật, mạng xáo₁, mạng xáo₂, và m = 0. Mỗi phiên bản 25 lần (seed × fold). Thêm one-hot MLP và MLP kiểu DeepSynergy. Tổng khoảng 100 lần train GNN, ước khoảng 5 giờ máy (nếu mỗi lần 2 phút, đo lại sau lần đầu).

**Bước 5: kiểm tra tiên quyết.** Với bộ ba này: z_syn khi có mạng, z_syn khi m = 0, ra network share. Trên toàn tập test: QWK của m = 1 có hơn m = 0 không.

**Bước 6: edge-IG ba cấp.**

- Cấp (i): IG của z_syn theo mask cạnh.
- Cấp (ii): IG của z_syn − z_add.
- Cấp (iii): IG(PD325901, MK-2206) − trung bình IG(PD325901, r) − trung bình IG(r, MK-2206) + trung bình IG(r, r'), tất cả trên A2058.

**Bước 7: trích đường dẫn.** Biến điểm cạnh thành chi phí −log (cộng phạt mỗi cạnh), tìm k đường rẻ nhất từ {MAP2K1, MAP2K2} tới {AKT1, AKT2, AKT3}, lấy top-k gen (bỏ chính các đích).

**Bước 8: đo kèm null.**

- Fid+: xóa top cạnh, xác suất syn tụt bao nhiêu, so với xóa ngẫu nhiên cùng số cạnh.
- Survival: top-k gen trên mạng thật so với trên mạng xáo₁, trừ xáo₁ so với xáo₂.
- Specificity: đổi MK-2206 thành vài thuốc không chung đích (ví dụ một thuốc hóa trị), đo Jaccard; làm cả phía ngược lại; trừ specificity của đường ngắn nhất.

**Bước 9: case study.** Bao nhiêu trong top-k gen thuộc hsa04010 hoặc hsa04151, so với 1.000 đường ngẫu nhiên cùng độ dài nối MEK với AKT. Gen trên đường có điểm Chronos âm ở A2058 không, sau khi loại gen thiết yếu chung.

**Bước 10: tổng hợp.** Gộp mọi bộ ba test, mọi seed, mọi fold. Dựng bảng ba cột bằng script đọc `metrics.json`, không chép tay.

### 10.3. Hai kết cục, kết cục nào cũng đăng được

| Kết cục | Nghĩa là | Kiểu bài |
|---|---|---|
| Lời giải thích cấp tương tác trung thực, đổi khi xáo mạng, đặc hiệu theo cặp vượt null | Có một cách giải thích đường dẫn đáng tin, kèm giao thức kiểm định | Phương pháp + benchmark |
| Lời giải thích y nguyên trên mạng xáo, hoặc không đặc hiệu hơn đường ngắn nhất | Các "đường dẫn cơ chế" đã công bố có thể chỉ là sản phẩm của việc nhớ tên thuốc | Phản biện, cùng dòng với One-hot news |

Giới hạn cần ghi rõ: luận văn **không bao giờ** nói được "explainer tìm đúng cơ chế". Câu mạnh nhất được phép viết là: lời giải thích trung thực với mô hình, phụ thuộc mạng thật vượt mức ngẫu nhiên, và đặc hiệu theo cặp vượt mức baseline.

Thú thật, chỗ mình thấy còn mở là kịch bản lửng lơ: survival vượt null rõ nhưng specificity cấp (iii) chỉ nhỉnh hơn đường ngắn nhất một chút, khoảng tin cậy chạm 0. Lúc đó bài nghiêng về phương pháp hay phản biện là chuyện phải quyết theo số thật, ở gate 3 (cuối tháng 7) của planner.

---

## Phụ lục: bảng thuật ngữ

| Thuật ngữ | Nghĩa ngắn | Xem phần |
|---|---|---|
| Gen / protein | Công thức trên DNA / cỗ máy làm từ công thức đó; trong luận văn là một node | 1.1 |
| Biểu hiện gen | Mức một gen đang được đọc, log2(TPM+1) | 1.2 |
| Cell line | Dòng tế bào ung thư nuôi trong phòng thí nghiệm | 1.4 |
| Pathway | Chuỗi protein chuyền tín hiệu | 1.5 |
| Crosstalk | Hành lang nối giữa hai pathway | 1.5 |
| Chronos (DepMap CRISPR) | Tắt gen thì tế bào còn sống không; −1 là thiết yếu | 1.6 |
| Đích thuốc | Protein mà thuốc bám vào | 2.1 |
| IC50 | Liều ức chế 50% | 2.2 |
| HSA, Bliss, Loewe, ZIP | Bốn định nghĩa "mức mong đợi" khi trộn thuốc | 2.3 |
| syn / add / ant | Hiệp đồng / cộng tính / đối kháng | 2.3, 2.4 |
| PPI, STRING | Mạng tương tác protein, cơ sở dữ liệu của nó | 3.2 |
| Bậc, hub | Số cạnh của node; node bậc rất cao | 3.1 |
| KEGG, gene set | Pathway vẽ tay; danh sách gen của mỗi pathway | 3.3 |
| s_AB | Độ tách biệt giữa đích hai thuốc trên mạng | 3.4 |
| Xáo giữ bậc | Đổi cặp cạnh, giữ số liên kết mỗi node | 3.6 |
| O'Neil, DrugComb | Bộ dữ liệu hiệp đồng chính; kho chứa nó | 4.1 |
| Z-score | Trừ trung bình, chia độ lệch chuẩn; 0 là mức trung bình | 4.3 |
| Logit, softmax | Điểm thô của mỗi lớp; biến điểm thô thành xác suất | 5.2 |
| Cross-entropy | Loss = −log xác suất của lớp đúng | 5.2 |
| Seed, fold | Khởi tạo ngẫu nhiên; một phần trong k phần chia dữ liệu | 5.5 |
| One-hot, embedding | Biểu diễn chỉ chứa tên; tên được nén học được | 5.6 |
| Macro-F1, QWK, polar error | Metric cho dữ liệu lệch lớp, nhãn có thứ tự, lỗi syn ↔ ant | 5.7 |
| Data leakage, leave-combo | Thông tin test lọt vào train; split giữ trọn mỗi cặp ở một phía | 5.8 |
| GCN | Mỗi node lấy trung bình hàng xóm; L lớp thấy L bước | 6.2 |
| Mask cạnh m | Số 0 đến 1 trên mỗi cạnh, để lấy đạo hàm theo cạnh | 6.4 |
| Hiệu ứng chính / tương tác | Phần của riêng từng thuốc / phần chỉ có khi hai thuốc gặp nhau | 7.1 |
| Attribution | Chia công lao dự đoán cho từng thành phần đầu vào | 8.1 |
| Trung thực / đúng sinh học | Phản ánh mô hình / phản ánh sự thật | 8.2 |
| Integrated Gradients, completeness | Cộng dồn gradient từ baseline; tổng attribution bằng mức đổi đầu ra | 8.3 |
| edge-IG | IG theo mask cạnh, từ m = 0 tới m = 1 | 8.4 |
| Network share | Phần logit do mạng đóng góp | 8.5 |
| Cấp logit / contrast / interaction | Ba cách hỏi "vì sao syn" | 8.6 |
| Shapley interaction index | Công lao của một cặp người chơi | 8.6 |
| Null | Giá trị của chỉ số khi không có gì đặc biệt | 9.2 |
| Rewiring-survival | Phần top-k gen giữ nguyên khi xáo mạng; thấp hơn null là tốt | 9.4 |
| Jaccard, partner-specificity | Độ giống hai tập; lời giải thích đổi bao nhiêu khi đổi đối tác | 9.5 |
| Fid+ / Fid− | Xóa cạnh giải thích thì dự đoán tụt bao nhiêu; chỉ giữ chúng thì còn bao nhiêu | 9.6 |
| Stability | Cosine giữa điểm cạnh của các seed | 9.7 |
| Positive-control hit | Tỷ lệ top-k gen rơi vào pathway kỳ vọng | 9.8 |
| Permutation test, Wilcoxon | p-value từ mẫu ngẫu nhiên; so cặp trên cùng các lần chạy | 9.9 |
