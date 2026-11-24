# Gợi ý cách nhấn: 01_kien_thuc_nen.pptx

Bản này nói nên nhấn chỗ nào, chuyển slide thế nào, slide nào bỏ được.
Lời đọc đầy đủ nằm ở `script_01_kien_thuc_nen.md` và trong ô Notes của
chính file pptx. Cả hai file do `slide/notes_01.py` sinh ra, sửa trong
script rồi chạy lại chứ đừng sửa file này.

Tổng thời lượng: **53 phút 10 giây**. Hụt giờ thì bỏ
ba slide đánh dấu `[CÓ THỂ BỎ]` (21, 37, 42), còn khoảng 50 phút.

---

## Slide 1: Hiệp đồng thuốc: kiến thức nền · ~60s

Mở đầu.
Tự giới thiệu, rồi nói ngay deck này là gì: không phải báo cáo kết quả, mà là
phần kiến thức nền để thầy cô thấy em hiểu bài toán trước khi nghe phương pháp.
Nói trước cấu trúc: sáu phần, 50 phút, câu hỏi để cuối cho tiện.
Nếu hội đồng muốn cắt ngang để hỏi thì càng tốt, cứ mời.

## Slide 2: Nội dung · ~75s

Bản đồ của cả buổi.
Đi nhanh tên sáu phần, đừng đọc hết các dòng con. Chỉ nhấn hai chỗ: phần 4
(hiệp đồng thuốc) là nơi bài toán được định nghĩa, phần 6 (giải thích) là nơi
luận văn của em đóng góp. Bốn phần còn lại là nền.
Câu nên nói: ba phần đầu trả lời "dữ liệu là gì", ba phần sau trả lời "đo thế
nào và tin được tới đâu".
→ Chuyển: bắt đầu từ chỗ cơ bản nhất, dữ liệu sinh học.

## Slide 3: Tin sinh học cơ bản · ~15s

Slide ngăn phần. Chỉ cần một câu: phần này trả lời câu hỏi
"dòng tế bào này là ai", vì đó là tất cả những gì phía sinh học đóng góp vào
bài toán.

## Slide 4: Từ DNA tới protein · ~60s

Ba mức dữ liệu, và vì sao chọn mức giữa.
DNA là bộ mã giống nhau ở mọi tế bào, nên nó không phân biệt được dòng tế bào
này với dòng kia về trạng thái. RNA là bản sao của gen đang được đọc, nên nó
mới nói lên tế bào đang làm gì. Protein là thứ thi hành, gần sinh học nhất,
nhưng dữ liệu công khai quá ít.
Chốt lại đúng một câu, đây là câu quan trọng nhất của slide: mô hình dùng biểu
hiện gen không phải vì nó tốt nhất, mà vì nó là lớp duy nhất có đủ dữ liệu.

## Slide 5: Gen, protein, tế bào · ~75s

Slide định nghĩa đơn vị dự đoán.
Nói rõ: trong dữ liệu, gen và protein coi như một, vì mình đo gen nhưng thứ
thuốc bám vào là protein.
Rồi vào ý chính: cùng một cặp thuốc có thể hiệp đồng ở dòng tế bào này và đối
kháng ở dòng kia. Nên đơn vị dự đoán không phải cặp thuốc, mà là bộ ba thuốc A,
thuốc B, dòng tế bào.
Dừng lại ở câu cuối: số bộ ba thì lớn, nhưng số thuốc và số dòng tế bào rất nhỏ.
Đây là gốc của mọi khó khăn ở phần sau, nhất là chuyện chia dữ liệu.

## Slide 6: Các lớp dữ liệu omics · ~60s

Bảng năm lớp omics. Đừng đọc cả bảng.
Chỉ vào hai dòng: transcriptomics là đầu vào chính, proteomics gần sinh học hơn
nhưng thiếu dữ liệu.
Câu chốt: cả lĩnh vực hiệp đồng gần như chỉ dùng transcriptomics, và lý do là
độ phủ chứ không phải sinh học.
Nếu bị hỏi vì sao không dùng đột biến: có dùng được, nhưng đột biến là vector
thưa và gần như không đổi giữa các thí nghiệm, nên nó mô tả tế bào tốt hơn là
làm đầu vào.

## Slide 7: Biểu hiện gen và chuẩn hóa · ~75s

Chuẩn hóa. Slide có một điểm phải nói bằng được.
Đi nhanh chuỗi RNA-seq → TPM → log2 → z-score, giải thích ngắn vì sao phải nén:
giá trị gốc chênh nhau hàng nghìn lần.
Rồi nhấn mạnh câu cuối: z-score chỉ được tính trên tập huấn luyện. Tính trên
toàn bộ dữ liệu là rò rỉ thông tin, mà kiểu rò rỉ này không thể phát hiện khi
đọc bảng kết quả, vì bảng vẫn đẹp.
Nói thêm 978 gen landmark L1000 là ai: tập đại diện, phần còn lại suy ra được.

## Slide 8: Định danh gen và chú giải · ~60s

Định danh gen. Kể bằng ví dụ, đừng đọc danh sách.
MAP2K1 và MEK1 là cùng một gen, hai tên. NCI-H460, NCIH460, H460 là cùng một
dòng tế bào, ba cách viết.
Câu chốt: một ánh xạ sai là một nhãn sai âm thầm, chạy suốt mọi thí nghiệm về
sau. Nên quy tắc trong dự án là chỉ khớp chính xác, không bao giờ khớp mờ theo
tên gần giống.

## Slide 9: Khâu xử lý dữ liệu · ~60s

Năm bước xử lý dữ liệu, và cái giá nếu bỏ qua.
Chỉ dừng ở hai dòng: hiệu chỉnh lô, vì nếu bỏ thì mô hình học lô thí nghiệm
chứ không học sinh học; và ghim phiên bản, vì chạy lại sau sáu tháng ra số khác
thì không tái lập được.
Kết bằng câu cuối slide, nó là kinh nghiệm thật: phần lớn thời gian của một dự
án tin sinh nằm ở khâu này, không nằm ở khâu mô hình.

## Slide 10: Ung thư, đột biến, dòng tế bào · ~75s

Ung thư, đột biến, dòng tế bào.
Định nghĩa ung thư gọn trong hai câu: phân chia không ngừng, không chịu chết
khi đã hỏng. Ví dụ BRAF V600E là một chữ sai làm protein kẹt ở chế độ bật.
Phần DepMap nói chậm hơn: CRISPR tắt lần lượt từng gen, điểm Chronos gần 0 là
không sao, gần −1 là tế bào chết.
Rồi nói cái bẫy: có nhóm gen thiết yếu với mọi tế bào, chúng luôn âm nên không
nói gì về một cặp thuốc cụ thể. Đây là lý do về sau mọi đối chứng null đều phải
loại nhóm gen này ra.

## Slide 11: Oncogene và gen ức chế khối u · ~60s

Oncogene và gen ức chế khối u. Đối xứng nên dễ nhớ:
oncogene bật quá mức thì thúc phân chia, gen ức chế mất chức năng thì tế bào
hết phanh, và gen ức chế cần hỏng cả hai bản sao.
Phân biệt driver với passenger trong một câu, kèm ý phần lớn đột biến là
passenger.
Chốt bằng khái niệm nghiện oncogene: nó giải thích vì sao cùng một thuốc nhắm
đích lại hiệu quả ở dòng tế bào này và vô dụng ở dòng kia.

## Slide 12: Chu kỳ tế bào và chết theo chương trình · ~60s

Chu kỳ tế bào và apoptosis.
Bốn pha nói thật nhanh, đừng sa vào chi tiết. TP53 là chốt kiểm soát quan trọng
nhất, mất chốt thì tế bào mang lỗi vẫn chia tiếp.
Ý chính nằm ở câu cuối: thuốc không giết tế bào trực tiếp, nó đẩy tế bào tới
chỗ tự hủy. Vì vậy hai thuốc đánh vào hai điểm khác nhau của cùng một lộ trình
có thể cộng hưởng. Đây là lần đầu trong deck xuất hiện cơ chế của hiệp đồng,
nên nói rõ để slide 15 và 18 nối vào được.

## Slide 13: Pathway và bộ gen chức năng · ~60s

Bốn nguồn pathway. Phân biệt cho đúng: KEGG do người vẽ,
có hướng và có dấu; GO rất rộng, dùng để chú giải; MSigDB là kho bộ gen gộp,
dùng để chấm làm giàu.
Định nghĩa bộ gen trong một câu, vì phần 6 sẽ dùng lại nó làm đơn vị đánh giá
lời giải thích.
Câu cuối là một cảnh báo về chính thiết kế của luận văn: vừa dùng KEGG làm đầu
vào mô hình vừa dùng KEGG để chấm điểm thì thành vòng lặp tự khen. Nói ra chủ
động thì tốt hơn để hội đồng chỉ ra.

## Slide 14: Phân tích làm giàu · ~60s

Phân tích làm giàu. Phân biệt ORA với GSEA trong hai câu:
ORA lấy top-k rồi kiểm định chồng lấn, GSEA xếp hạng toàn bộ gen.
Nhấn phần thống kê: thử hàng nghìn bộ gen thì kiểu gì cũng có vài bộ p < 0,05,
nên không hiệu chỉnh FDR là tự lừa mình.
Và một câu phải nói: làm giàu chỉ cho thấy liên quan thống kê, không chứng minh
cơ chế.

## Slide 15: Pathway tín hiệu và cơ chế bù trừ · ~90s

Đây là slide quan trọng nhất của phần 1, nói chậm.
Dẫn theo hình: nhánh tăng sinh EGFR → KRAS → BRAF → MEK → ERK, nhánh sống sót
EGFR → PI3K → AKT → mTOR, hai nhánh nối nhau bằng crosstalk, ô đỏ là nơi thuốc
chặn.
Rồi kể câu chuyện cơ chế: chặn MEK thì tế bào bật nhánh AKT để bù, chặn một
nhánh tế bào vẫn sống, chặn cả hai thì hết lối thoát.
Chốt: đó chính là hiệp đồng, nhìn từ phía sinh học. Mọi phần sau chỉ là cách đo
và cách dự đoán hiện tượng này.

## Slide 16: Các nhóm thuốc ung thư · ~60s

Năm nhóm thuốc, đọc tên vài thuốc trong O'Neil để thầy cô
thấy dữ liệu thật trông thế nào: cisplatin, gemcitabine, paclitaxel, MK-2206,
PD325901.
Nhấn sự khác biệt: hóa trị kinh điển đánh mọi tế bào đang phân chia nên độc
tính cao, thuốc nhắm đích chọn lọc hơn nhưng dễ bị kháng.
Câu chốt nối sang phần XAI: biết thuốc thuộc nhóm nào là điều kiện để đọc được
lời giải thích của mô hình.

## Slide 17: Kháng thuốc: vì sao phải phối hợp · ~60s

Ba cơ chế kháng thuốc. Nói cơ chế đường vòng kỹ nhất vì nó
hay gặp nhất và trùng với ví dụ MEK–AKT ở slide 15.
Câu chốt là lập luận biện minh cho cả đề tài: một thuốc đơn gần như luôn bị
kháng, nên phối hợp là cách chặn nhiều lối thoát cùng lúc, không phải chỉ để
tăng liều.

## Slide 18: Bốn lý do sinh học khiến tổ hợp hiệu quả · ~75s

Bốn lý do sinh học khiến tổ hợp hiệu quả. Slide này sẽ
được gọi lại ở phần 6, nên nói rõ từng cái, mỗi cái một câu kèm ví dụ: chặn
song song (MEK và AKT), chặn đường thoát, synthetic lethality (PARP trên khối u
đột biến BRCA), thay đổi phơi nhiễm.
Câu chốt: bốn cơ chế này là thứ mà lời giải thích của mô hình nên trỏ tới, nếu
nó thật sự có ý nghĩa sinh học. Nói câu này rõ, vì nó là tiêu chí đánh giá XAI
của luận văn, phát biểu bằng ngôn ngữ sinh học.

## Slide 19: Từ đĩa nuôi cấy tới bệnh nhân · ~60s

Thang bậc từ đĩa nuôi cấy tới bệnh nhân. Mục đích của
slide này là tự giới hạn phạm vi trước khi hội đồng hỏi.
Nói PK và PD trong một câu mỗi cái, rồi khái niệm cửa sổ điều trị: phối hợp thì
độc tính cũng cộng lại, hiệp đồng về hiệu lực mà cũng hiệp đồng về độc thì vô
dụng.
Chốt dứt khoát: mọi kết quả trong luận văn nằm ở mức dòng tế bào 2D, đây là
bước sàng lọc đầu tiên, không phải bằng chứng lâm sàng.

## Slide 20: PHẦN 2 · ~15s

Ngăn phần 2. Một câu: protein không làm việc một mình, nên
dữ liệu cũng là một đồ thị.

## Slide 21: Đồ thị: từ vựng tối thiểu · ~45s

[CÓ THỂ BỎ] Từ vựng đồ thị. Hội đồng tin học biết hết, nên
đi rất nhanh, chỉ dừng ở hai dòng có nghĩa sinh học: hub là protein nối hàng
trăm protein khác, và k-hop là vùng lân cận quanh đích thuốc.
Một câu nối sang GNN: ma trận kề là dạng mà mạng nơ-ron đồ thị nhận vào.

## Slide 22: PPI: tương tác protein–protein · ~60s

PPI. Định nghĩa gọn, rồi nói cách đo chỉ ở mức tên:
Y2H thử từng cặp, AP-MS kéo một protein xuống xem ai đi cùng.
Điểm phải nhấn: cạnh PPI không có hướng và không có dấu, nó chỉ nói hai protein
liên quan, không nói ai kích hoạt ai. Khác hẳn pathway KEGG do người vẽ, có mũi
tên và có dấu.
Đây là lý do mạng PPI không thay được pathway khi muốn nói về cơ chế.

## Slide 23: STRING và điểm tin cậy · ~60s

STRING, và con số thật của luận văn.
combined_score thang 0 đến 1000, gộp nhiều loại bằng chứng. Lọc ≥ 700 là chỉ
giữ cạnh tin cậy cao. Sau khi lọc và giao với bảng biểu hiện còn 16.201 nút và
236.930 cạnh, STRING v12, người, mã loài 9606. Thuộc mấy con số này, thầy cô
hay hỏi đúng chỗ đó.
Hai câu chốt: ngưỡng lọc là một lựa chọn phải báo cáo chứ không phải chi tiết
kỹ thuật; và một phần lớn cạnh STRING đến từ khai phá văn bản, nên mạng phản
ánh cả thói quen nghiên cứu của con người.

## Slide 24: Tính chất của mạng PPI · ~75s

Tính chất mạng PPI, và slide này dựng nên khái niệm null.
Phân bố bậc lệch: phần lớn protein ít cạnh, một số ít hub có hàng trăm cạnh.
Module là cụm nối dày, thường ứng với một chức năng.
Hệ quả quan trọng: hub nằm trên hầu hết đường đi, nên lời giải thích trỏ vào
hub chưa nói lên gì.
Giới thiệu đối chứng chuẩn, nói chậm: xáo mạng nhưng giữ nguyên bậc từng node,
khi đó mọi đường đi cụ thể bị phá nhưng hub vẫn là hub. Nếu kết quả không đổi
sau khi xáo thì mô hình không dùng sinh học của mạng. Phần 6 sẽ dùng lại ý này.

## Slide 25: Dược lý mạng · ~75s

Dược lý mạng và chỉ số s_AB của Cheng và cộng sự.
Ý tưởng: mỗi thuốc có một cụm đích trên mạng, mỗi bệnh có một module. Tổ hợp
hiệu quả thường có hai cụm đích tách nhau nhưng cùng chạm vào module bệnh; hai
cụm chồng lên nhau thì hay vô ích hoặc độc.
Rồi nói con số, đây là điểm đáng nhớ nhất: dùng chính s_AB để dự đoán chỉ đạt
AUC 0,589, gần với đoán mò. Mạng giải thích tốt hơn là dự đoán.
Nên trong luận văn, s_AB được dùng làm mốc so sánh cho lời giải thích, không
phải làm mô hình dự đoán. Nói chủ động để tránh bị hỏi sao không dùng s_AB.

## Slide 26: Đưa mạng vào mô hình · ~75s

Ba cách đưa mạng vào mô hình.
node2vec: đi bộ ngẫu nhiên, học một vector cho từng gen, gen tương tác nhau thì
vector gần nhau. Đây là cách luận văn dùng.
GNN trên mạng: nói kèm giới hạn, L lớp chỉ nhìn được L bước, nên đích hai thuốc
cách xa thì không gặp nhau.
Lan truyền đích thuốc: đơn giản mà hiệu quả bất ngờ.
Hai câu chốt: đưa mạng vào thì phải chứng minh mạng có ích, bằng cách chạy lại
với mạng đã xáo; và quan sát riêng của em là PPI dùng để lan truyền đích thì có
ích, còn PPI dùng làm toàn bộ biểu diễn thuốc thì không.

## Slide 27: PHẦN 3 · ~15s

Ngăn phần 3. Một câu: làm sao mô tả một phân tử thuốc cho
máy tính hiểu.

## Slide 28: Biểu diễn phân tử · ~75s

Biểu diễn phân tử.
SMILES là chuỗi ký tự, đồ thị phân tử là nguyên tử làm node và liên kết làm
cạnh, đặc trưng nguyên tử gồm nguyên tố, bậc, hóa trị, tính thơm. RDKit đọc
SMILES, chuẩn hóa, và cắt phân tử thành mảnh theo quy tắc BRICS.
Ba cái bẫy nói nhanh, nhưng đừng bỏ cái cuối: phức platin như carboplatin hay
thiếu trong cơ sở dữ liệu, đó là vấn đề thật đã gặp khi lấy SMILES.
Câu chốt nối sang XAI: giải thích ở cấp nguyên tử chỉ làm được khi mô hình nhận
đồ thị, mô hình nhận chuỗi ký tự thì không quy được về nguyên tử nào. Đây là lý
do luận văn chọn GNN chứ không chọn mô hình trên chuỗi.

## Slide 29: Fingerprint, descriptor, độ tương tự · ~60s

Bảng bốn cách mô tả thuốc. Dừng ở hai dòng: Morgan
fingerprint nhanh và mạnh bất ngờ nhưng mỗi bit là một mảnh băm nên không đọc
được, còn mảnh BRICS là đơn vị giải thích dễ đọc hơn nguyên tử.
Tanimoto: hai phân tử chung bao nhiêu bit trên tổng số bit, dùng để biết tập
test có thật sự khác tập train hay không.
Con số nên nhớ: trong O'Neil, Tanimoto trung vị giữa các thuốc chỉ khoảng 0,19,
nghĩa là 38 thuốc này khá khác nhau về cấu trúc.

## Slide 30: Đích thuốc và cơ chế tác động · ~60s

Đích thuốc. Một thuốc có thể có nhiều đích, và bám cả
protein ngoài ý muốn gọi là off-target.
Nguồn: DrugBank đầy đủ nhất nhưng cần license, ChEMBL mở và có cơ chế tác động.
Câu chốt quan trọng: vector đích là cầu nối duy nhất giữa hóa học của thuốc và
sinh học của tế bào.
Rồi nói ngay giới hạn, vì nó liên quan tới dữ liệu thật: hóa trị kinh điển
thường không có đích hẹp nên vector đích rỗng, và thuốc mang mã nội bộ của hãng
hay thiếu cả cấu trúc lẫn chú giải đích.

## Slide 31: PHẦN 4 · ~20s

Ngăn phần 4. Nói một câu có sức nặng: phần này là nơi bài
toán được định nghĩa, và cũng là nơi các định nghĩa không đồng ý với nhau.

## Slide 32: Liều–đáp ứng và IC50 · ~60s

Thí nghiệm gốc. Mô tả đúng trình tự: cho tế bào tiếp xúc
thuốc ở nhiều mức liều, đo phần trăm ức chế, vẽ ra đường cong hình chữ S.
IC50 là liều ức chế 50%, thuốc mạnh thì IC50 nhỏ. Monotherapy là dữ liệu dùng
một thuốc riêng lẻ, và phải có nó mới tính được mức mong đợi.
Câu chốt: tổ hợp được đo trên một lưới liều, ví dụ 4 × 4, rồi cả lưới bị tóm
lại thành một con số duy nhất. Bước tóm tắt đó làm mất thông tin, mà nhiễu giữa
các bản lặp thì vẫn còn.

## Slide 33: Ba khả năng khi trộn hai thuốc · ~45s

Ba khả năng khi trộn hai thuốc. Slide dễ, đi nhanh.
Nhưng dừng hẳn ở câu chốt, vì nó mở ra slide sau: câu khó không phải ba khả
năng, mà là mức mong đợi bằng bao nhiêu. Có bốn định nghĩa phổ biến, cho bốn
con số khác nhau trên cùng một thí nghiệm.
Nhắc luôn hiệp đồng là quan hệ đối xứng, đổi chỗ A và B thì kết quả không đổi.
Đây là lý do kiến trúc mô hình phải đối xứng theo hai thuốc.

## Slide 34: Bốn cách tính mức mong đợi · ~75s

Bốn cách tính mức mong đợi. Dẫn bằng ví dụ trên slide, nói
thành lời chứ đừng để hội đồng tự đọc bảng:
A ức chế 40%, B ức chế 50%, trộn lại ức chế 85%. HSA lấy thuốc mạnh nhất nên
mong đợi 50%, dôi ra 35. Bliss coi hai thuốc độc lập nên mong đợi 70%, chỉ dôi
ra 15. Loewe và ZIP tính theo liều nên tùy liều.
Cùng một thí nghiệm, hai định nghĩa cho hai kết luận khác nhau về mức độ.
Nói rõ quy ước của luận văn: điểm Loewe trong DrugComb là chênh lệch phần trăm
ức chế, nên ngưỡng ±10 là đơn vị phần trăm, không phải đơn vị tùy ý.

## Slide 35: Bốn điểm số không đồng ý với nhau · ~75s

Slide thú thật của phần 4, nói chậm và rõ.
Tương quan giữa điểm Loewe và điểm ZIP chỉ r = 0,28. Có 21 đến 34% số ma trận
bị hai phương pháp gán nhãn ngược nhau.
Đọc ví dụ trên slide: trộn chỉ ức chế 45%, HSA cho −5 nên là cộng tính, Bliss
cho −25 nên là đối kháng. Cùng một thí nghiệm, hai nhãn trái ngược.
Chốt: nhãn hiệp đồng là một lựa chọn quy ước, không phải một sự thật đo được.
Và nói ngay cách xử lý, đừng để treo: luận văn chạy lại với một điểm thứ hai và
với ngưỡng khác, rồi báo cả bảng độ nhạy.

## Slide 36: Hiệp đồng không đồng nghĩa hiệu quả · ~60s

Phân biệt hiệp đồng với hiệu quả. Dùng đúng hai ví dụ trên
slide, chúng đủ thuyết phục: hai thuốc yếu cộng lại vẫn yếu mà điểm hiệp đồng
rất cao; hai thuốc mạnh diệt gần hết mà điểm hiệp đồng bằng không.
Chốt: điểm hiệp đồng cao mà hiệu lực thấp thì không dùng được trên lâm sàng,
nên luôn đọc điểm hiệp đồng kèm độ nhạy tuyệt đối, DrugComb có cột riêng cho nó.
Câu cuối là một nhận xét về cả lĩnh vực: phần lớn bài báo chỉ báo điểm hiệp
đồng, nên bảng xếp hạng của họ chưa chắc là bảng tổ hợp đáng dùng.

## Slide 37: Chou–Talalay và đường đồng hiệu lực · ~60s

[CÓ THỂ BỎ] Chou–Talalay. Nếu hụt giờ thì bỏ slide này,
vì luận văn không dùng CI.
Nếu nói thì dẫn theo ví dụ: để ức chế 50%, A cần 10 µM, B cần 20 µM; hỗn hợp
2 µM A với 4 µM B đã đạt 50%, nên CI = 0,4, hiệp đồng rõ.
Câu chốt giải thích vì sao không dùng: cách này đòi đường cong liều–đáp ứng đầy
đủ cho từng thuốc, nên không dùng được khi dữ liệu thưa.

## Slide 38: Thiết kế thí nghiệm và nhiễu · ~75s

Thiết kế thí nghiệm và nhiễu. Slide này biện minh cho một
lựa chọn kỹ thuật ở phần sau, nên đừng bỏ.
Nói lưới liều có cả hàng và cột đơn trị làm đối chứng, phân biệt bản lặp sinh
học với bản lặp kỹ thuật, Z-factor đo mức tách giữa đối chứng dương và âm.
Rồi câu quan trọng nhất: nhiễu giữa các bản lặp thường lớn hơn khoảng cách giữa
hai bên ngưỡng ±10, nên nhãn của bộ ba nằm sát ngưỡng gần như là ngẫu nhiên.
Chốt: đây là lý do kỹ thuật để làm mềm nhãn quanh ngưỡng, thay vì tin tuyệt đối
vào đường cắt.

## Slide 39: Từ điểm số sang nhãn ba lớp · ~75s

Từ điểm số sang nhãn ba lớp, và một con số nên nhớ.
Bảng ngưỡng đọc nhanh: trên +10 là syn, trong khoảng ±10 là add, dưới −10 là
ant.
Ba hệ quả, nói đủ cả ba: ngưỡng ±10 là quy ước chứ không phải sinh học; lớp
cộng tính chiếm đa số; và ba lớp có thứ tự ant < add < syn, đây là chỗ về sau
dẫn tới việc dùng đầu ra thứ tự thay cho softmax.
Rồi nói con số: nhiều bài vứt hẳn vùng trung tính trước khi huấn luyện, DTSyn
mất 42,6% dữ liệu, từ 23.052 bộ ba còn 13.243. Bài toán còn lại dễ hơn hẳn bài
toán thật, mà chưa bài nào đo xem việc này thổi kết quả lên bao nhiêu.

## Slide 40: Vì sao ít tổ hợp vào được lâm sàng · ~60s

Vì sao ít tổ hợp vào được lâm sàng. Ba lý do nói mỗi cái
một câu, nhấn cái đầu: hai thuốc cùng đánh vào tủy xương thì phải giảm liều, và
hiệp đồng biến mất.
Rồi hai câu nâng lại giá trị của đề tài, đừng kết phần này bằng giọng tiêu cực:
lớp đối kháng cũng có giá trị lâm sàng, vì biết cặp nào làm giảm hiệu quả thì
tránh kê cùng nhau; và dự đoán hiệp đồng là bước sàng lọc để chọn cặp đáng đem
đi thí nghiệm tiếp.

## Slide 41: PHẦN 5 · ~15s

Ngăn phần 5. Một câu: từ đây là phía tin học, dữ liệu nào,
chia thế nào, đo bằng gì.

## Slide 42: Dữ liệu đáp ứng thuốc đơn · ~45s

[CÓ THỂ BỎ phần bảng] Dữ liệu đáp ứng thuốc đơn. Bảng bốn
nguồn đi nhanh, chỉ cần nói CCLE và DepMap là nền chung để ghép mọi nguồn.
Phần phải nói là nửa dưới: IC50 và AUC là hai cách tóm tắt đáp ứng, và không có
dữ liệu đơn trị thì không tính được mức mong đợi, nên cũng không định nghĩa
được hiệp đồng. Đó là lý do dữ liệu đơn trị quan trọng dù bài toán là tổ hợp.

## Slide 43: LINCS L1000 và Connectivity Map · ~60s

L1000 và Connectivity Map. Chữ ký biểu hiện: cho tế bào
tiếp xúc một thuốc rồi đo lại 978 gen, kết quả là gen nào lên gen nào xuống.
CMap so chữ ký thuốc với chữ ký bệnh, thuốc đảo ngược được chữ ký bệnh là ứng
viên; đó là cơ sở cho tái định vị thuốc.
Phải nói rõ câu cuối để khỏi bị hiểu sai: luận văn chỉ mượn danh sách 978 gen
landmark của L1000, không dùng chữ ký đáp ứng. Nếu bị hỏi vì sao không dùng:
chữ ký L1000 cho O'Neil phủ không đủ, và đó là một hướng mở rộng chứ không phải
phạm vi hiện tại.

## Slide 44: Bộ dữ liệu tổ hợp thuốc · ~75s

Bốn bộ dữ liệu tổ hợp. Nói O'Neil kỹ nhất vì đó là bộ
chính: 23.000 bộ ba, 38 thuốc, 39 dòng tế bào, và nó là bộ chuẩn mà DeepSynergy,
DeepDDS, DTSyn, AttenSyn đều dùng, nên số của em so được với số của họ.
ALMANAC làm kiểm chứng ngoài, DrugComb v1.4 là nơi lấy đủ bốn điểm.
Rồi con số đáng nhớ nhất của cả deck: trên 1.163 thí nghiệm mà O'Neil và
ALMANAC cùng đo, hai nghiên cứu chỉ đồng thuận ở mức QWK khoảng 0,15. Đó là
trần thực tế của mọi phép kiểm chứng chéo giữa hai bộ dữ liệu, nên đừng ai kỳ
vọng mô hình vượt xa mức đó khi đổi bộ dữ liệu.

## Slide 45: Khung bài toán học máy · ~60s

Khung bài toán học máy. Đầu vào là bộ ba, đầu ra là một
trong ba nhãn.
Ba câu về thực hành: lớp cộng tính chiếm đa số nên phải cân lại trọng số lớp;
chọn siêu tham số theo validation còn test chỉ dùng một lần; mỗi cấu hình chạy
nhiều fold và nhiều seed.
Hai điều kiện để bảng so sánh có giá trị, nói rõ vì đây là cam kết về phương
pháp: mọi mô hình cùng ngân sách huấn luyện và cùng ngân sách dò siêu tham số.
Chốt: baseline phải tái lập được số đã công bố, nếu không thì cả bảng mất giá
trị.

## Slide 46: Chia dữ liệu: nơi hiệu năng bị thổi phồng · ~75s

Chia dữ liệu. Slide này và slide 35 là hai slide có sức
nặng nhất của deck.
Năm cách chia xếp từ dễ tới khó, giải thích cái dễ bị thổi phồng: chia ngẫu
nhiên để cùng một cặp thuốc nằm ở cả train và test, mô hình chỉ cần nhớ cặp đó
là đoán đúng mà không hiểu gì. Leave-drug mới là tình huống dùng thật, một
thuốc chưa từng gặp.
Rồi đưa bằng chứng: trên split ngẫu nhiên, một mô hình chỉ biết tên thuốc và
tên dòng tế bào đạt ROC-AUC 0,9566, ngang DeepSynergy 0,9581. Nghĩa là split
này không phân biệt được mô hình tốt với mô hình chỉ biết nhớ.

## Slide 47: Chỉ số đánh giá · ~60s

Chỉ số đánh giá. Đừng đọc cả bảng, chỉ đi cột bẫy:
accuracy vô dụng khi lệch lớp, AUPRC không so trực tiếp được giữa hai bài khác
tỷ lệ dương.
Dừng ở hai dòng cuối vì đó là chỉ số của luận văn: QWK tôn trọng thứ tự, nhầm
syn thành ant bị phạt gấp bốn so với nhầm sang add; polar error là tỷ lệ nhầm
syn với ant, lỗi nguy hiểm nhất về lâm sàng.
Chốt bằng quy tắc: chọn một chỉ số chính trước khi chạy, rồi dùng nó cho cả
early stopping và mọi so sánh.

## Slide 48: Các mô hình đã công bố · ~60s

Các mô hình đã công bố, xếp theo thời gian để thấy đường đi:
DeepSynergy 2018 là MLP trên fingerprint và biểu hiện, DeepDDS 2022 đưa GCN
trên đồ thị phân tử, DTSyn 2022 dùng hai transformer với token nguyên tử và
token gen.
Nhắc dòng XGBoost, nó là lời cảnh báo hữu ích: không học sâu mà khó vượt ở
split khó.
Chốt bằng điểm chung, vì đây là khe hở mà luận văn nhắm vào: các bài đều dùng
nhãn nhị phân, thường bỏ vùng trung tính, và trình bày attention như lời giải
thích mà không kiểm định.

## Slide 49: PHẦN 6 · ~20s

Ngăn phần 6. Một câu: đây là phần em đầu tư nhiều nhất,
và là chỗ lĩnh vực còn yếu nhất.

## Slide 50: Giải thích mô hình là gì · ~75s

Giải thích mô hình là gì. Định nghĩa attribution: chia
điểm công lao cho từng thành phần đầu vào, ở đây là gen, nguyên tử, mảnh cấu
trúc hoặc cạnh mạng.
Phân biệt hai tiêu chí hay bị gộp, nói chậm: trung thực là có phản ánh đúng mô
hình không, đúng sinh học là có khớp tri thức đã biết không. Hai cái khác nhau.
Ba phương pháp nói ngắn, nhưng nhấn: attention sẵn có nhưng không phải
attribution.
Chốt bằng câu cuối, nó là luận điểm của em: mô hình chỉ nhớ tên thì lời giải
thích trung thực của nó vẫn sai sinh học, nên phải kiểm tra mô hình trước rồi
mới trách phương pháp giải thích.

## Slide 51: Thống kê và đối chứng null · ~60s

Đối chứng null. Dùng ví dụ đồng xu trên slide, nó dễ hiểu
với mọi người: tung 10 lần ra 6 ngửa, con số 6 đứng một mình không nói gì.
Ba cách dựng null: hoán vị nhãn, xáo mạng giữ bậc, chọn ngẫu nhiên cùng số đơn
vị. Và điều kiện bắt buộc: null phải đi qua đúng đường ống như kết quả thật.
Chốt bằng cam kết cách báo số: mọi chỉ số đều báo dưới dạng giá trị thật, giá
trị null, và hiệu giữa hai cái, kèm khoảng tin cậy qua nhiều seed và nhiều fold,
không báo một con số lẻ.

## Slide 52: Đo chất lượng một lời giải thích · ~75s

Bảng đánh giá lời giải thích. Đây là đóng góp về phương
pháp, nên đi đủ bốn dòng và nói kèm null của từng dòng: Fid+ và Fid− so với xóa
ngẫu nhiên cùng số đơn vị; Jaccard@k qua seed và fold để đo ổn định; Jaccard@k
qua điểm và ngưỡng để đo ổn định khi đổi quy ước; làm giàu pathway so với tập
gen ngẫu nhiên cùng cỡ.
Hai câu chốt: trung thực, ổn định và đúng sinh học là ba tính chất riêng biệt,
đạt cái này không kéo theo cái kia; và case study phải được chọn trước khi chạy,
nếu không thì chỉ là tìm ví dụ hợp ý sau khi đã thấy kết quả.

## Slide 53: Lĩnh vực đang yếu ở đâu · ~90s

Slide kết, cũng là slide nối sang buổi báo cáo về đề tài.
Đi sáu chỗ yếu, mỗi chỗ một câu, đừng đọc hết các dòng nhỏ: quy ước nhãn chỉ
tương quan lỏng lẻo; vùng trung tính bị xóa mà chưa ai đo cái giá; mô hình nhớ
danh tính vì chỉ có 38 thuốc; split quá dễ nên số đẹp; attention được coi là
lời giải thích mà không ai kiểm định; và ba tiêu chí đánh giá bị gộp làm một.
Kết bằng một câu của mình: sáu chỗ này là chỗ em chọn để làm, và deck thứ hai
nói em làm thế nào.
Rồi mời câu hỏi.
