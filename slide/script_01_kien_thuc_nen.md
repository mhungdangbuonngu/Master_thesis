# Lời đọc: 01_kien_thuc_nen.pptx

Kịch bản nói cho 53 slide, tổng khoảng 50 phút. Đây là lời để nói, không phải
lời để đọc nguyên văn: cứ đổi chữ cho vào miệng mình. Chỗ in nghiêng là việc
làm, không phải việc nói. Ba slide 21, 37, 42 bỏ được nếu hụt giờ.

File này là nguồn duy nhất của lời đọc. Sửa ở đây rồi chạy
`python3 slide/notes_01.py` để đẩy vào ô Notes của file pptx.

Gợi ý cách nhấn và cách chuyển slide nằm ở `slide/notes_01_kien_thuc_nen.md`.

---

## Slide 1 · Bìa · ~60s

Em xin phép bắt đầu. Em là Nguyễn Mạnh Hưng, học viên khóa 2025, mã 20252276M,
làm luận văn dưới sự hướng dẫn của thầy Lê Đức Hậu.

Hôm nay em chưa báo cáo kết quả. Buổi này em trình bày phần kiến thức nền của
đề tài dự đoán hiệp đồng thuốc, để thầy cô thấy em hiểu bài toán tới đâu trước
khi nghe phương pháp. Em xin khoảng 50 phút cho sáu phần. Thầy cô muốn hỏi giữa
bài thì cứ ngắt lời em, em thấy như vậy dễ trao đổi hơn là dồn hết xuống cuối.

## Slide 2 · Nội dung · ~75s

Sáu phần theo thứ tự này.

Ba phần đầu trả lời câu hỏi dữ liệu là gì. Phần một là sinh học của tế bào ung
thư. Phần hai là mạng tương tác protein. Phần ba là cách mô tả một phân tử
thuốc cho máy tính.

Ba phần sau trả lời câu hỏi đo thế nào và tin được tới đâu. Phần bốn là định
nghĩa hiệp đồng. Phần năm là dữ liệu và học máy. Phần sáu là giải thích mô hình.

Nếu thầy cô chỉ theo một phần, em xin đề nghị phần bốn và phần sáu. Phần bốn là
chỗ bài toán được định nghĩa, và em sẽ cho thấy định nghĩa đó lỏng hơn nhiều so
với vẻ ngoài của nó. Phần sáu là chỗ luận văn của em đóng góp.

Em bắt đầu từ chỗ cơ bản nhất.

## Slide 3 · Ngăn phần 1 · ~15s

Phần một, sinh học. Cả phần này chỉ để trả lời một câu hỏi: dòng tế bào trong
bộ ba của em là ai. Đó là tất cả những gì phía sinh học đóng góp vào đầu vào
của mô hình.

## Slide 4 · Từ DNA tới protein · ~60s

Có ba mức dữ liệu để mô tả một tế bào.

DNA là bộ mã, và nó giống nhau ở mọi tế bào trong cùng một cơ thể, nên nó không
cho em biết tế bào đang ở trạng thái nào. RNA là bản sao của những gen đang
được đọc, nên nó mới nói lên tế bào đang làm gì. Protein là thứ thi hành mọi
việc, gần sinh học nhất.

Vậy đáng ra phải đo protein. Nhưng proteome đo đắt, dữ liệu công khai rất ít,
trong khi transcriptome đo rẻ và phủ hàng nghìn dòng tế bào.

Em nói thẳng chỗ này vì nó quyết định cả thiết kế đầu vào: mô hình của em dùng
biểu hiện gen không phải vì đó là lớp dữ liệu tốt nhất, mà vì đó là lớp duy
nhất có đủ dữ liệu.

## Slide 5 · Gen, protein, tế bào · ~75s

Gen là công thức, protein là thứ thi hành công thức đó. Thuốc nhắm đích bám vào
protein. Nhưng trong dữ liệu em có, gen và protein coi như một, vì em đo mức
đọc của gen rồi suy ra protein tương ứng.

Mỗi dòng tế bào là một vector gen, thường rút về 978 gen landmark. A2058, MCF7,
A549 là tên của mấy dòng hay gặp, mỗi dòng lấy từ một bệnh nhân rồi nuôi vô hạn
trong phòng thí nghiệm, nên mỗi dòng có một hồ sơ riêng.

Chỗ quan trọng là đây. *Chỉ vào câu cuối slide.* Cùng một cặp thuốc có thể hiệp
đồng ở dòng tế bào này và đối kháng ở dòng kia. Nên đơn vị dự đoán không phải
là cặp thuốc, mà là bộ ba: thuốc A, thuốc B, dòng tế bào.

Và một chi tiết sẽ quay lại ám em suốt phần năm: số bộ ba thì lớn, hàng chục
nghìn, nhưng số thuốc và số dòng tế bào thì rất nhỏ.

## Slide 6 · Các lớp dữ liệu omics · ~60s

Bảng này có năm lớp, em xin dừng ở hai dòng.

Transcriptomics là đầu vào chính của em. Proteomics gần sinh học hơn, nhưng
thiếu dữ liệu nên gần như không ai dùng trong lĩnh vực này.

Genomics, tức đột biến và số bản sao gen, thì mô tả tế bào rất tốt nhưng ít
được dùng làm đầu vào, vì nó là vector thưa và gần như không đổi giữa các thí
nghiệm trên cùng một dòng.

Cả lĩnh vực hiệp đồng thuốc gần như chỉ dùng transcriptomics. Lý do là độ phủ
dữ liệu, không phải lý do sinh học.

## Slide 7 · Biểu hiện gen và chuẩn hóa · ~75s

Đường đi của dữ liệu biểu hiện: RNA-seq đo mức đọc từng gen, đổi sang TPM là số
bản sao trên một triệu, rồi lấy log2 của TPM cộng một để nén khoảng giá trị, rồi
z-score để so với trung bình.

Phải nén vì giá trị gốc chênh nhau hàng nghìn lần giữa các gen. Phải chuẩn hóa
vì khác lô thí nghiệm là khác thang đo, cái đó gọi là batch effect.

Một điểm em muốn nói rõ. Z-score chỉ được tính trên tập huấn luyện. Tính trung
bình và độ lệch trên toàn bộ dữ liệu rồi mới chia tập là rò rỉ thông tin, mà
kiểu rò rỉ này không ai phát hiện được khi đọc bảng kết quả, vì bảng vẫn đẹp,
thậm chí đẹp hơn.

Còn 978 gen landmark là tập gen đại diện do dự án LINCS chọn, phần còn lại của
transcriptome suy ra được từ chúng. Em mượn đúng danh sách này để giảm chiều.

## Slide 8 · Định danh gen và chú giải · ~60s

Một gen có nhiều tên. MAP2K1 là ký hiệu chuẩn theo HGNC, MEK1 là tên quen dùng
trong các bài về thuốc, rồi còn mã số Entrez 5604 và Ensembl. Cả bốn cách viết
chỉ về một gen.

Dòng tế bào cũng vậy. NCI-H460, NCIH460 và H460 là cùng một dòng, viết theo ba
nguồn khác nhau.

Khớp tên giữa các nguồn là việc tốn thời gian nhất của khâu dữ liệu, và cũng là
chỗ dễ sai nhất. Một ánh xạ sai cho ra một nhãn sai âm thầm, rồi nhãn đó chạy
suốt mọi thí nghiệm về sau mà không báo lỗi.

Nên quy tắc trong dự án của em là chỉ khớp chính xác. Không bao giờ khớp mờ
theo tên gần giống.

## Slide 9 · Khâu xử lý dữ liệu · ~60s

Năm bước, em xin dừng ở hai bước.

Hiệu chỉnh lô, bằng ComBat hoặc một mô hình tuyến tính. Bỏ bước này thì mô hình
học lô thí nghiệm chứ không học sinh học, và nó vẫn cho số đẹp.

Ghim phiên bản từng cơ sở dữ liệu. Bỏ bước này thì chạy lại sau sáu tháng ra số
khác, và lúc đó không biết số nào đúng.

Dòng tế bào cũng cần định danh chuẩn, em dùng Cellosaurus và Cell Model
Passports. Đó là cách duy nhất để chắc hai bộ dữ liệu đang nói về cùng một dòng.

Phần lớn thời gian của một dự án tin sinh nằm ở khâu này, không nằm ở khâu mô
hình. Em nói vậy vì đó là điều em gặp thật khi chuẩn bị dữ liệu cho luận văn.

## Slide 10 · Ung thư, đột biến, dòng tế bào · ~75s

Ung thư, nói gọn, là tế bào phân chia không ngừng và không chịu chết khi đã
hỏng.

Đột biến điểm là một chữ sai trong bộ mã làm protein hỏng. Ví dụ kinh điển là
BRAF V600E, một chữ sai làm protein kẹt ở chế độ bật. Còn CNV là gen bị nhân
bản hoặc bị mất hẳn.

Dòng tế bào thì lấy từ bệnh nhân rồi nuôi vô hạn. CCLE và DepMap là hai nguồn
cung cấp hồ sơ của chúng.

Nói thêm về gen thiết yếu, vì phần sáu sẽ dùng lại. DepMap dùng CRISPR tắt lần
lượt từng gen rồi xem tế bào còn sống không. Điểm Chronos gần 0 là tắt gen đó
không sao, gần âm một là tế bào chết.

Và đây là cái bẫy. Có một nhóm gen thiết yếu với mọi tế bào, nhóm đó luôn âm,
nên nó không nói gì về một cặp thuốc cụ thể. Mọi đối chứng của em về sau đều
phải loại nhóm này ra, nếu không thì lời giải thích nào cũng trỏ vào chúng.

## Slide 11 · Oncogene và gen ức chế khối u · ~60s

Hai loại gen đối xứng nhau.

Oncogene bị bật quá mức thì thúc tế bào phân chia, thường do đột biến hoặc do
nhân bản gen. KRAS, BRAF, EGFR, MYC là những cái tên hay gặp.

Gen ức chế khối u thì ngược lại, mất chức năng là tế bào hết phanh, và thường
phải hỏng cả hai bản sao mới có hậu quả. TP53, RB1, PTEN, BRCA1 và BRCA2 thuộc
nhóm này.

Trong một khối u có hàng nghìn đột biến, nhưng chỉ vài cái thật sự gây bệnh,
gọi là driver. Số còn lại là passenger, đi kèm mà không gây bệnh.

Có một hiện tượng gọi là nghiện oncogene: khối u phụ thuộc vào đúng một
oncogene. Đó là lý do cùng một thuốc nhắm đích lại hiệu quả ở dòng tế bào này
và vô dụng ở dòng kia, và cũng là lý do hồ sơ đột biến của dòng tế bào giải
thích được phần lớn khác biệt về đáp ứng thuốc.

## Slide 12 · Chu kỳ tế bào và chết theo chương trình · ~60s

Tế bào chia theo bốn pha: G1 chuẩn bị, S nhân đôi DNA, G2 kiểm tra lỗi, M phân
chia.

Giữa các pha có chốt kiểm soát, tế bào phải dừng lại nếu DNA hỏng. TP53 là chốt
quan trọng nhất. Mất chốt thì tế bào mang lỗi vẫn chia tiếp.

Apoptosis là chết theo chương trình, tế bào tự tháo dỡ chính nó. Đó là đích
cuối cùng của phần lớn thuốc ung thư, và tế bào ung thư thường chặn được đường
này.

Chỗ này đáng để ý: thuốc không giết tế bào trực tiếp, nó đẩy tế bào tới chỗ tự
hủy. Nên hai thuốc đánh vào hai điểm khác nhau của cùng một lộ trình có thể
cộng hưởng với nhau. Đây là lần đầu khái niệm hiệp đồng xuất hiện trong bài của
em, và slide 15 sẽ nói kỹ.

## Slide 13 · Pathway và bộ gen chức năng · ~60s

Bốn nguồn, khác nhau ở cách dữ liệu được tạo ra.

KEGG là pathway vẽ tay, có hướng và có dấu, nên nó nói được ai kích hoạt ai.
hsa04010 là MAPK, hsa04151 là PI3K-Akt, hai pathway em sẽ dùng ở slide sau.
Reactome chi tiết hơn và có phân cấp. Gene Ontology rất rộng, dùng để chú giải.
MSigDB là kho bộ gen gộp từ nhiều nguồn, định dạng chuẩn để chấm làm giàu.

Bộ gen là một danh sách gen cùng tham gia một chức năng. Phần sáu sẽ dùng bộ gen
làm đơn vị để nói lời giải thích có ý nghĩa sinh học hay không.

Và em xin nói trước một chỗ yếu trong thiết kế của mình: nếu vừa dùng KEGG làm
đầu vào mô hình, vừa dùng KEGG để chấm điểm lời giải thích, thì thành vòng lặp
tự khen. Em đang tách hai việc đó ra bằng cách chỉ chấm trên bộ gen không tham
gia vào đầu vào.

## Slide 14 · Phân tích làm giàu · ~60s

Có hai cách làm. ORA lấy top-k gen được chấm điểm cao rồi kiểm định xem chúng
chồng lấn với một bộ gen nào nhiều hơn mức ngẫu nhiên. GSEA thì xếp hạng toàn bộ
gen và xem bộ gen quan tâm dồn về đầu hay cuối bảng xếp hạng.

Phần thống kê đi kèm: p-value từ kiểm định Fisher hoặc từ hoán vị, rồi hiệu
chỉnh đa kiểm định bằng FDR theo Benjamini-Hochberg, và báo cả kích thước hiệu
ứng chứ không chỉ báo p.

Thử hàng nghìn bộ gen thì kiểu gì cũng có vài bộ p nhỏ hơn 0,05. Không hiệu
chỉnh đa kiểm định là tự lừa mình.

Một câu nữa để tránh hiểu sai về kết quả làm giàu: nó cho thấy mối liên quan
thống kê, nó không chứng minh cơ chế.

## Slide 15 · Pathway tín hiệu và cơ chế bù trừ · ~90s

Slide này là chỗ em muốn nói chậm, vì nó là sinh học của hiệp đồng.

*Chỉ theo hình.* Bên trái là nhánh tăng sinh: EGFR nhận tín hiệu từ ngoài, rồi
KRAS, BRAF, MEK1/2, ERK1/2. Bên phải là nhánh sống sót: EGFR, PI3K, AKT, mTOR.
Hai nhánh không độc lập, chúng nối nhau bằng crosstalk. Các ô đỏ là nơi thuốc
chặn được.

Giờ là cơ chế. Chặn MEK, nhánh bên trái tắt, nhưng tế bào bật nhánh AKT để bù,
và nó vẫn sống. Chặn AKT một mình cũng vậy, tế bào dựa vào nhánh ERK. Chặn cả
hai cùng lúc thì tế bào hết lối thoát.

Đó chính là hiệp đồng, nhìn từ phía sinh học. Toàn bộ phần sau của bài em chỉ là
cách đo hiện tượng này và cách dự đoán nó.

Ngoài cơ chế hai nhánh, còn vài cơ chế khác hay gặp: synthetic lethality, chặn
đường vòng kháng thuốc, và thay đổi phơi nhiễm thuốc. Slide 18 em quay lại đủ
bốn cái.

## Slide 16 · Các nhóm thuốc ung thư · ~60s

Năm nhóm, và em lấy ví dụ thuốc có thật trong bộ dữ liệu O'Neil để thầy cô thấy
dữ liệu trông thế nào.

Nhóm gây tổn thương DNA: cisplatin, carboplatin, etoposide, doxorubicin. Nhóm
kháng chuyển hóa, giả làm nguyên liệu để chặn tổng hợp DNA: gemcitabine, 5-FU,
methotrexate. Nhóm chặn phân bào, phá bộ khung vi ống khi tế bào chia:
paclitaxel, vinblastine. Nhóm nhắm đích kinase: MK-2206 chặn AKT, PD325901 chặn
MEK, đúng hai đích em vừa nói ở slide trước. Và nhóm chặn sửa chữa DNA, tức các
thuốc ức chế PARP.

Khác biệt lớn giữa hai nhóm đầu và nhóm nhắm đích: hóa trị kinh điển đánh vào
mọi tế bào đang phân chia nên độc tính cao, thuốc nhắm đích chọn lọc hơn nhưng
dễ bị kháng.

Biết thuốc thuộc nhóm nào là điều kiện để đọc được lời giải thích của mô hình.
Không biết nhóm thì không đánh giá được lời giải thích là hợp lý hay vô nghĩa.

## Slide 17 · Kháng thuốc · ~60s

Ba cơ chế kháng thuốc.

Đột biến ở đích: protein đổi hình, thuốc không bám được nữa, thường xuất hiện
sau vài tháng điều trị.

Đường vòng: tế bào bật một nhánh khác để bù, đúng chuyện chặn MEK thì AKT bật
lên. Đây là cơ chế hay gặp nhất.

Bơm đẩy thuốc: các bơm ABC tống thuốc ra khỏi tế bào, làm nồng độ bên trong
giảm xuống dưới mức có tác dụng.

Một thuốc đơn gần như luôn bị kháng. Nên phối hợp không phải để tăng liều, mà
để chặn nhiều lối thoát cùng lúc. Đó là lý do bài toán dự đoán hiệp đồng đáng
làm: tìm cặp chặn được cả lối chính lẫn lối thoát.

## Slide 18 · Bốn lý do sinh học khiến tổ hợp hiệu quả · ~75s

Bốn cơ chế, mỗi cái một câu.

Một, chặn song song. Hai thuốc chặn hai nhánh của cùng một hệ, như MEK với AKT.

Hai, chặn đường thoát. Thuốc thứ hai chặn đúng cơ chế kháng của thuốc thứ nhất.

Ba, synthetic lethality. Hỏng một gen thì tế bào vẫn sống, hỏng cả hai thì
chết. Ví dụ kinh điển là thuốc ức chế PARP trên khối u đã đột biến BRCA.

Bốn, thay đổi phơi nhiễm. Thuốc này làm thuốc kia vào tế bào nhiều hơn, hoặc
chậm bị đào thải hơn.

Em xin dừng lại ở bốn cái này một chút, vì nó là tiêu chí để đánh giá phần XAI
của em. Nếu lời giải thích của mô hình thật sự có ý nghĩa sinh học, nó phải trỏ
được về một trong bốn cơ chế này. Còn nếu nó trỏ vào một nhóm gen nào đó mà
không quy được về cơ chế nào, thì em coi lời giải thích đó chưa đạt.

## Slide 19 · Từ đĩa nuôi cấy tới bệnh nhân · ~60s

Có bốn bậc. Dòng tế bào 2D rẻ, chạy được hàng chục nghìn tổ hợp. Organoid giữ
được cấu trúc mô. PDX là ghép khối u người lên chuột. Trên nữa là thử nghiệm
lâm sàng.

Hai khái niệm dược lý cần cho phần sau. PK là thuốc đi đâu và còn trong máu bao
lâu. PD là ở nồng độ đó thuốc làm được gì. Nồng độ cho hiệp đồng trong đĩa nuôi
cấy có thể không bao giờ đạt được trong máu người.

Cửa sổ điều trị là khoảng giữa liều có tác dụng và liều gây độc. Phối hợp hai
thuốc thì độc tính cũng cộng lại. Hiệp đồng về hiệu lực mà cũng hiệp đồng về
độc thì vô dụng.

Nên em xin nói rõ phạm vi: mọi kết quả trong luận văn này nằm ở mức dòng tế bào
2D. Đây là bước sàng lọc đầu tiên, không phải bằng chứng lâm sàng.

## Slide 20 · Ngăn phần 2 · ~15s

Phần hai, mạng sinh học. Protein không làm việc một mình, nên dữ liệu của em
cũng là một đồ thị.

## Slide 21 · Từ vựng đồ thị · ~45s · bỏ được

Em đi nhanh phần từ vựng vì thầy cô đã quen.

Node là một protein hoặc một gen, cạnh là hai protein có tương tác, bậc là số
cạnh nối vào một node.

Hai khái niệm có nghĩa sinh học thì em xin nói rõ. Hub là node bậc rất cao,
TP53 hay AKT1 nối tới hàng trăm protein. Và k-hop là các node trong vòng k
bước, tức vùng lân cận quanh đích thuốc, khái niệm này sẽ quay lại khi em nói
về GNN.

Ma trận kề là cách viết đồ thị thành bảng số, và đó là dạng mà mạng nơ-ron đồ
thị nhận vào.

## Slide 22 · PPI · ~60s

PPI là tương tác protein với protein: hai protein bám vào nhau, hoặc cùng tham
gia một phức hợp, hoặc có bằng chứng liên quan về chức năng.

Đo bằng ba cách chính. Y2H thử từng cặp trong nấm men. AP-MS kéo một protein
xuống rồi xem những ai đi cùng. Và một phần được suy ra từ đồng biểu hiện hoặc
từ khai phá văn bản khoa học.

Nguồn thì có STRING là lớn nhất và có điểm tin cậy, BioGRID và IntAct là tương
tác thực nghiệm, HuRI là bản đồ Y2H quy mô lớn.

Một điểm phải nhớ về bản chất dữ liệu: cạnh PPI không có hướng và không có dấu.
Nó chỉ nói hai protein liên quan, nó không nói ai kích hoạt ai. Khác với pathway
KEGG do người vẽ, có mũi tên và có dấu kích hoạt hay ức chế. Nên mạng PPI không
thay được pathway khi em muốn nói về cơ chế.

## Slide 23 · STRING và điểm tin cậy · ~60s

STRING cho mỗi cạnh một điểm combined_score, thang 0 tới 1000, gộp nhiều loại
bằng chứng: thực nghiệm, cơ sở dữ liệu, đồng biểu hiện, và khai phá văn bản.

Cấu hình em dùng: STRING phiên bản 12, loài người, mã 9606, lọc combined_score
từ 700 trở lên, tức chỉ giữ cạnh tin cậy cao. Sau khi lọc và giao với tập gen có
trong bảng biểu hiện, mạng còn 16.201 nút và 236.930 cạnh.

Hạ ngưỡng thì mạng dày lên nhưng nhiễu cũng tăng. Nên ngưỡng lọc là một lựa
chọn phải báo cáo, không phải một chi tiết kỹ thuật để trong code.

Thêm một điểm về bản chất của STRING: một phần lớn cạnh đến từ khai phá văn
bản, nên mạng này phản ánh cả thói quen nghiên cứu của con người. Protein nào
được nghiên cứu nhiều thì có nhiều cạnh.

## Slide 24 · Tính chất của mạng PPI · ~75s

Ba tính chất, và cái thứ ba dẫn tới một việc em phải làm.

Phân bố bậc rất lệch. Phần lớn protein có ít cạnh, một số ít hub có hàng trăm
cạnh. Người ta gọi là mạng không tỷ lệ.

Mạng có module, là các cụm protein nối dày với nhau, thường ứng với một chức
năng, và bệnh hay gắn với một module.

Hệ quả thì hơi phiền. Hub nằm trên hầu hết đường đi của mạng, nên một lời giải
thích trỏ vào hub chưa nói lên điều gì, nó chỉ đang nói hub là hub.

Nên mọi chỉ số trên mạng đều cần đối chứng null. Đối chứng chuẩn là xáo mạng
nhưng giữ nguyên bậc của từng node. Khi đó mọi đường đi cụ thể bị phá, nhưng
hub vẫn là hub. Nếu kết quả không đổi sau khi xáo, nghĩa là mô hình không dùng
sinh học của mạng, nó chỉ dùng bậc. Phần sáu em dùng lại đúng phép thử này.

## Slide 25 · Dược lý mạng · ~75s

Ý tưởng của dược lý mạng: mỗi thuốc có một cụm đích trên mạng, mỗi bệnh có một
module, và vị trí tương đối của chúng nói lên điều gì đó.

Cheng và cộng sự đo khoảng cách giữa hai cụm đích bằng một chỉ số gọi là s_AB.
Phát hiện của họ là tổ hợp hiệu quả thường có hai cụm đích tách nhau, nhưng cả
hai cùng chạm vào module bệnh. Còn hai cụm chồng lên nhau thì hay vô ích hoặc
độc.

Nhưng đây là con số em muốn thầy cô nhớ. Dùng chính s_AB để dự đoán chỉ đạt AUC
0,589, gần với đoán mò. Mạng giải thích tốt hơn là dự đoán.

Nên trong luận văn, em dùng s_AB làm mốc so sánh cho lời giải thích, không dùng
nó làm mô hình dự đoán. Em nói trước để tránh câu hỏi sao không dùng luôn s_AB
cho gọn.

## Slide 26 · Đưa mạng vào mô hình · ~75s

Ba cách đưa mạng vào.

node2vec: đi bộ ngẫu nhiên trên mạng, học một vector cho từng gen, gen nào hay
đi cùng nhau thì vector gần nhau. Đây là cách em dùng.

GNN chạy thẳng trên mạng PPI: mỗi gen cập nhật theo hàng xóm. Cách này có một
giới hạn phải biết, L lớp chỉ nhìn được L bước, nên nếu đích của hai thuốc cách
nhau xa thì thông tin của chúng không gặp nhau trong mô hình.

Lan truyền đích thuốc: lấy vector đích rồi lan ra các gen lân cận. Đơn giản mà
hiệu quả bất ngờ, ở quy mô lớn còn mạnh hơn hẳn fingerprint.

Đưa mạng vào thì phải chứng minh mạng có ích, bằng cách chạy lại với mạng đã
xáo rồi so hai kết quả. Và một quan sát em thấy đáng chú ý khi đọc các bài: PPI
dùng để lan truyền đích thì có ích, nhưng PPI dùng làm toàn bộ biểu diễn thuốc
thì không.

## Slide 27 · Ngăn phần 3 · ~15s

Phần ba, hóa tin. Câu hỏi của phần này là mô tả một phân tử thuốc cho máy tính
bằng cách nào.

## Slide 28 · Biểu diễn phân tử · ~75s

Ba cách mô tả một phân tử.

SMILES là một chuỗi ký tự mã hóa cấu trúc. Đồ thị phân tử lấy nguyên tử làm
node và liên kết làm cạnh. Và trên mỗi nguyên tử em gắn đặc trưng: nguyên tố,
bậc, hóa trị, tính thơm.

RDKit là thư viện làm ba việc: đọc SMILES và dựng đồ thị, chuẩn hóa về dạng
chuẩn và trạng thái ion hóa, rồi cắt phân tử thành mảnh theo quy tắc BRICS.

Ba cái bẫy em đã gặp. Một phân tử có nhiều chuỗi SMILES hợp lệ khác nhau. Ký tự
trong SMILES không ánh xạ một trên một về nguyên tử. Và các phức platin như
carboplatin hay thiếu trong cơ sở dữ liệu, cái này em gặp thật khi lấy SMILES
cho O'Neil.

Chỗ quyết định cho phần sáu: giải thích ở cấp nguyên tử chỉ làm được khi mô
hình nhận đồ thị. Mô hình nhận chuỗi ký tự thì không quy lời giải thích về
nguyên tử nào được. Đó là lý do em chọn mạng đồ thị chứ không chọn mô hình trên
chuỗi.

## Slide 29 · Fingerprint, descriptor, độ tương tự · ~60s

Bốn cách mô tả, em dừng ở hai.

Morgan fingerprint, còn gọi là ECFP, là vector nhị phân 1024 hoặc 2048 bit.
Nhanh và mạnh bất ngờ, nhưng mỗi bit là một mảnh đã băm, nên không đọc ra được
bit đó là mảnh gì. Đó là lý do nhánh fingerprint không giải thích được.

Mảnh BRICS thì ngược lại, vài mảnh lớn cho mỗi phân tử, và là đơn vị giải thích
dễ đọc hơn nguyên tử.

Độ tương tự Tanimoto đo hai phân tử chung bao nhiêu bit trên tổng số bit. Em
dùng nó để biết tập test có thật sự khác tập train hay không.

Con số cho bộ dữ liệu của em: trong O'Neil, Tanimoto trung vị giữa các thuốc chỉ
khoảng 0,19. Nghĩa là 38 thuốc này khá khác nhau về cấu trúc, và đó là tin tốt
cho phép chia theo thuốc.

## Slide 30 · Đích thuốc và cơ chế tác động · ~60s

Đích là protein mà thuốc bám vào, thường là để chặn lại. Một thuốc có thể có
nhiều đích, và khi nó bám cả protein ngoài ý muốn thì gọi là off-target.

Nguồn dữ liệu đích: DrugBank đầy đủ nhất nhưng cần license học thuật, ChEMBL mở
và có cả cơ chế tác động, DGIdb và TTD gom từ nhiều nguồn.

Vector đích là cầu nối duy nhất giữa hóa học của thuốc và sinh học của tế bào.
Không có nó thì hai phía chỉ ghép cạnh nhau chứ không nói chuyện với nhau.

Nhưng nó có hai lỗ. Hóa trị kinh điển thường không có đích hẹp nên vector đích
rỗng. Và thuốc mang mã nội bộ của hãng thì hay thiếu cả cấu trúc lẫn chú giải
đích.

## Slide 31 · Ngăn phần 4 · ~20s

Phần bốn, hiệp đồng thuốc. Đây là chỗ bài toán của em được định nghĩa, và cũng
là chỗ các định nghĩa không đồng ý với nhau.

## Slide 32 · Liều đáp ứng và IC50 · ~60s

Thí nghiệm gốc rất đơn giản. Cho tế bào tiếp xúc thuốc ở nhiều mức liều, đo
phần trăm tế bào bị ức chế, rồi vẽ ra một đường cong hình chữ S.

Từ đường cong đó lấy ra IC50, là liều làm ức chế 50%. Thuốc mạnh thì IC50 nhỏ.
Dữ liệu dùng một thuốc riêng lẻ gọi là monotherapy, và phải có nó mới tính được
mức mong đợi khi trộn hai thuốc.

Với tổ hợp, thí nghiệm đo trên một lưới liều, ví dụ 4 nhân 4, mỗi ô là một phần
trăm ức chế. Rồi cả lưới đó bị tóm lại thành một con số duy nhất.

Bước tóm tắt ấy làm mất thông tin, mà nhiễu giữa các bản lặp thì vẫn còn nguyên
trong con số còn lại.

## Slide 33 · Ba khả năng khi trộn hai thuốc · ~45s

Trộn hai thuốc thì có ba khả năng. Hơn mức mong đợi là hiệp đồng, đúng mức mong
đợi là cộng tính, kém mức mong đợi là đối kháng.

Nhưng câu khó không nằm ở ba khả năng. Câu khó là mức mong đợi bằng bao nhiêu.
Có bốn định nghĩa phổ biến, và chúng cho bốn con số khác nhau trên cùng một thí
nghiệm.

Một tính chất nữa cần nhớ vì nó ràng buộc kiến trúc mô hình: hiệp đồng là quan
hệ đối xứng. Đổi chỗ A và B thì kết quả không đổi, nên mô hình cũng phải đối
xứng theo hai thuốc.

## Slide 34 · Bốn cách tính mức mong đợi · ~75s

Em xin lấy ví dụ trên slide để nói cho cụ thể. Thuốc A một mình ức chế 40%,
thuốc B một mình ức chế 50%, trộn cả hai thì ức chế 85%.

Theo HSA, mức mong đợi là thuốc đơn mạnh nhất, tức 50%, nên phần dôi ra là 35.

Theo Bliss, hai thuốc coi như độc lập, mức mong đợi là 70%, nên phần dôi ra chỉ
còn 15.

Loewe quy về liều tương đương, ZIP kết hợp Loewe với Bliss, cả hai tính theo
liều nên kết quả tùy liều.

Cùng một thí nghiệm, bốn định nghĩa, bốn con số về mức độ hiệp đồng.

Quy ước của em: dùng điểm Loewe trong DrugComb, và điểm đó là chênh lệch phần
trăm ức chế so với mức mong đợi. Nên khi em nói ngưỡng cộng trừ 10 ở slide sau,
đơn vị là điểm phần trăm, không phải một đơn vị tùy ý.

## Slide 35 · Bốn điểm số không đồng ý với nhau · ~75s

Slide này em nói chậm, vì đây là chỗ em thấy lĩnh vực đang mâu thuẫn với chính
nó.

Tương quan giữa điểm Loewe và điểm ZIP chỉ r bằng 0,28. Và 21 tới 34% số ma
trận bị hai phương pháp gán nhãn ngược nhau.

Ví dụ cụ thể trên slide: một tổ hợp chỉ ức chế 45%. Theo HSA, chênh lệch là âm
5, nằm trong vùng trung tính, nên nhãn là cộng tính. Theo Bliss, chênh lệch là
âm 25, nên nhãn là đối kháng. Cùng một thí nghiệm, hai nhãn trái ngược.

Nên nhãn hiệp đồng là một lựa chọn quy ước, không phải một sự thật đo được. Hai
bài báo dùng hai điểm khác nhau thì con số của họ không so trực tiếp được, dù
bảng kết quả trông như so được.

Cách em xử lý: chạy lại toàn bộ với một điểm thứ hai và với một ngưỡng khác,
rồi báo cả bảng độ nhạy. Em không coi đó là phần phụ, vì nếu kết quả đổi dấu khi
đổi quy ước thì mô hình của em chỉ đang học quy ước.

## Slide 36 · Hiệp đồng không đồng nghĩa hiệu quả · ~60s

Đây là hai câu hỏi khác nhau mà hay bị gộp. Tổ hợp này có mạnh không, thì nhìn
phần trăm ức chế tuyệt đối. Tổ hợp này có hiệp đồng không, thì nhìn phần dôi ra
so với mức mong đợi.

Hai trường hợp cho thấy chúng tách nhau. Hai thuốc yếu, cộng lại vẫn yếu, nhưng
điểm hiệp đồng rất cao. Hai thuốc mạnh, cộng lại diệt gần hết tế bào, nhưng
điểm hiệp đồng bằng không.

Điểm hiệp đồng cao mà hiệu lực thấp thì không dùng được trên lâm sàng. Nên phải
đọc điểm hiệp đồng kèm độ nhạy tuyệt đối, DrugComb có cột riêng cho nó, thường
gọi là điểm S.

Phần lớn bài báo chỉ báo điểm hiệp đồng. Nên bảng xếp hạng tổ hợp của họ chưa
chắc là bảng tổ hợp đáng đem đi thí nghiệm.

## Slide 37 · Chou-Talalay · ~60s · bỏ được

Chỉ số tổ hợp CI được tính bằng d_A chia D_A cộng d_B chia D_B, trong đó d là
liều dùng trong hỗn hợp và D là liều cần khi dùng một mình. CI nhỏ hơn 1 là
hiệp đồng, bằng 1 là cộng tính, lớn hơn 1 là đối kháng.

Ví dụ: để ức chế 50%, thuốc A cần 10 micromol, thuốc B cần 20 micromol. Nếu hỗn
hợp chỉ cần 2 micromol A với 4 micromol B đã đạt 50%, thì CI bằng 0,4, hiệp
đồng rõ.

Đường đồng hiệu lực là cách vẽ của cùng ý tưởng đó: nối mọi cặp liều cho cùng
một mức hiệu quả, đường thẳng là cộng tính theo Loewe, cong vào trong là hiệp
đồng.

Em không dùng CI trong luận văn, vì cách này đòi đường cong liều đáp ứng đầy đủ
cho từng thuốc, mà dữ liệu của em thưa hơn thế.

## Slide 38 · Thiết kế thí nghiệm và nhiễu · ~75s

Thí nghiệm tổ hợp hay làm theo hai kiểu. Lưới liều, mỗi cặp thuốc đo trên lưới
4 nhân 4 hoặc dày hơn, có cả hàng và cột đơn trị làm đối chứng. Hoặc tỷ lệ cố
định, trộn hai thuốc theo một tỷ lệ rồi pha loãng dần, rẻ hơn nhưng chỉ nhìn
được một lát cắt.

Kiểm soát chất lượng thì có bản lặp sinh học, bản lặp kỹ thuật, và Z-factor đo
mức tách giữa đối chứng dương với đối chứng âm.

Và đây là con số làm em suy nghĩ nhiều nhất về nhãn. Nhiễu giữa các bản lặp
thường lớn hơn khoảng cách giữa hai bên ngưỡng cộng trừ 10. Nghĩa là nhãn của
một bộ ba nằm sát ngưỡng gần như là ngẫu nhiên, nó phụ thuộc vào lần đo chứ
không phụ thuộc vào sinh học.

Đây là lý do kỹ thuật để em làm mềm nhãn quanh ngưỡng, thay vì tin tuyệt đối
vào đường cắt.

## Slide 39 · Từ điểm số sang nhãn ba lớp · ~75s

Quy tắc gán nhãn của em: điểm Loewe lớn hơn cộng 10 là syn, từ âm 10 tới cộng
10 là add, nhỏ hơn âm 10 là ant.

Ba hệ quả.

Ngưỡng cộng trừ 10 là quy ước, không phải sinh học. Không có gì trong tế bào
thay đổi tại mốc 10.

Lớp cộng tính chiếm đa số, nên bài toán lệch lớp và phải cân lại trọng số.

Và ba lớp này có thứ tự: ant nhỏ hơn add nhỏ hơn syn. Chỗ này quan trọng với
phương pháp của em, vì nó cho phép dùng đầu ra có thứ tự thay cho softmax ba
lớp rời rạc.

Còn đây là chỗ em thấy lĩnh vực đang tự làm dễ bài toán. Nhiều bài vứt hẳn vùng
trung tính rồi mới huấn luyện. DTSyn mất 42,6% dữ liệu, từ 23.052 bộ ba còn
13.243. Bài toán còn lại dễ hơn hẳn bài toán thật, vì hai lớp còn lại cách nhau
rất xa. Mà chưa bài nào đo xem việc đó thổi kết quả lên bao nhiêu.

## Slide 40 · Vì sao ít tổ hợp vào được lâm sàng · ~60s

Ba lý do.

Độc tính cộng lại. Hai thuốc cùng đánh vào tủy xương thì bệnh nhân không chịu
nổi, phải giảm liều, và khi giảm liều thì hiệp đồng biến mất.

Không đạt nồng độ. Nồng độ cho hiệp đồng trong đĩa nuôi cấy không đạt được
trong máu, hoặc hai thuốc không cùng có mặt một lúc.

Và dòng tế bào khác bệnh nhân. Khối u thật không đồng nhất, có mô đệm, có miễn
dịch, có mạch máu.

Hai điều em muốn nói thêm. Lớp đối kháng cũng có giá trị lâm sàng, vì biết cặp
nào làm giảm hiệu quả thì tránh kê cùng nhau, mà phần lớn mô hình nhị phân
không trả lời được câu này. Và hướng ứng dụng gần nhất của dự đoán hiệp đồng là
sàng lọc để chọn cặp đáng đem đi thí nghiệm tiếp, cùng với tái định vị thuốc.

## Slide 41 · Ngăn phần 5 · ~15s

Phần năm, phía tin học. Dữ liệu nào, chia thế nào, đo bằng gì, và các mô hình
đã có làm tới đâu.

## Slide 42 · Dữ liệu đáp ứng thuốc đơn · ~45s · bỏ được

Bốn nguồn dữ liệu thuốc đơn. GDSC có hàng trăm thuốc trên khoảng 1.000 dòng tế
bào, kèm đường cong đầy đủ. CTRP chú trọng cơ chế tác động. PRISM sàng lọc hàng
nghìn thuốc bằng mã vạch, rẻ và phủ rộng nhưng nhiễu hơn. CCLE và DepMap là nền
chung để ghép mọi nguồn trên lại.

Đáp ứng được tóm lại theo hai cách: IC50, hoặc AUC của đường cong, cách thứ hai
tính cả vùng liều thấp.

Em để slide này ở đây vì một lý do. Không có dữ liệu đơn trị thì không tính
được mức mong đợi, nên cũng không định nghĩa được hiệp đồng. Bài toán của em là
tổ hợp, nhưng nó dựa trên dữ liệu đơn trị.

## Slide 43 · LINCS L1000 và Connectivity Map · ~60s

L1000 làm thế này: cho tế bào tiếp xúc một thuốc, rồi đo lại 978 gen landmark.
Kết quả là một chữ ký, gen nào lên, gen nào xuống. Hiện đã công khai hơn một
triệu chữ ký.

Connectivity Map dùng chữ ký đó để so thuốc với bệnh. Thuốc nào đảo ngược được
chữ ký của bệnh thì là ứng viên. Đó là cơ sở của tái định vị thuốc.

Trong dự đoán hiệp đồng, chữ ký L1000 là một khung nhìn thứ ba về thuốc, bên
cạnh cấu trúc hóa học và danh sách đích.

Nhưng em xin nói rõ để khỏi bị hiểu sai: luận văn của em chỉ mượn danh sách 978
gen landmark, em không dùng chữ ký đáp ứng. Lý do là chữ ký L1000 phủ không đủ
các thuốc trong O'Neil. Đó là một hướng mở rộng, không phải phạm vi hiện tại.

## Slide 44 · Bộ dữ liệu tổ hợp thuốc · ~75s

Bốn bộ dữ liệu tổ hợp.

O'Neil, của Merck năm 2016, khoảng 23.000 bộ ba từ 38 thuốc và 39 dòng tế bào.
Đây là bộ chính của em, và em chọn nó vì DeepSynergy, DeepDDS, DTSyn, AttenSyn
và MD-Syn đều dùng nó, nên số của em đặt cạnh số của họ được.

NCI-ALMANAC lớn hơn nhiều, hơn 300.000 bộ ba với 104 thuốc, em dùng làm tập
kiểm chứng ngoài. DrugComb phiên bản 1.4 gom 466.033 khối tổ hợp từ nhiều nghiên
cứu và cho đủ bốn điểm số. AstraZeneca-DREAM là cuộc thi có che nhãn.

Con số cuối slide là con số em nghĩ đáng nhớ nhất của cả phần năm. Trên 1.163
thí nghiệm mà O'Neil và ALMANAC cùng đo, hai nghiên cứu chỉ đồng thuận ở mức QWK
khoảng 0,15.

Hai phòng thí nghiệm đo cùng một thứ mà chỉ đồng ý tới mức đó. Nên đó là trần
thực tế của mọi phép kiểm chứng chéo giữa hai bộ dữ liệu, kể cả của em.

## Slide 45 · Khung bài toán học máy · ~60s

Đầu vào là bộ ba thuốc A, thuốc B, dòng tế bào. Mô hình là một hàm có tham số
học được. Đầu ra là một trong ba nhãn ant, add, syn.

Ba việc về thực hành. Lớp cộng tính chiếm đa số nên phải cân lại trọng số lớp.
Siêu tham số chọn theo tập validation, tập test chỉ dùng một lần ở cuối. Và mỗi
cấu hình chạy nhiều fold, nhiều seed, vì một con số lẻ không nói được gì.

Hai điều kiện để bảng so sánh có giá trị, em xin nói rõ vì đây là cam kết về
phương pháp. Mọi mô hình phải cùng ngân sách huấn luyện, và cùng ngân sách dò
siêu tham số. Nếu em dò kỹ cho mô hình của mình mà dò sơ cho baseline thì bảng
đó không nói gì.

Và baseline phải tái lập được số đã công bố. Không tái lập được thì cả bảng mất
giá trị.

## Slide 46 · Chia dữ liệu · ~75s

Năm cách chia, xếp từ dễ tới khó: chia ngẫu nhiên, giữ cặp thuốc ra, giữ thuốc
ra, giữ dòng tế bào ra, giữ cả loại mô ra.

Chia ngẫu nhiên có một vấn đề. Cùng một cặp thuốc nằm ở cả train và test, chỉ
khác dòng tế bào. Mô hình chỉ cần nhớ cặp đó là đoán đúng, mà không cần hiểu gì
về hóa học hay sinh học.

Leave-drug mới là tình huống dùng thật: một thuốc chưa từng gặp, mô hình phải
suy từ cấu trúc.

Và đây là bằng chứng cho điều em vừa nói. Trên split ngẫu nhiên, em dựng một mô
hình chỉ biết tên thuốc và tên dòng tế bào, không biết gì về hóa học, không biết
gì về biểu hiện gen. Nó đạt ROC-AUC 0,9566. DeepSynergy đạt 0,9581.

Hai con số gần như bằng nhau. Nghĩa là split ngẫu nhiên không phân biệt được mô
hình hiểu bài với mô hình chỉ biết nhớ.

## Slide 47 · Chỉ số đánh giá · ~60s

Sáu chỉ số, em đi theo cột bẫy.

Accuracy vô dụng khi lệch lớp, đoán toàn lớp đông nhất đã được 80%. Macro-F1
thì lộ ngay mô hình lười vì tính đều cho cả ba lớp. ROC-AUC so được giữa các
bài nhưng lạc quan khi lớp dương hiếm. AUPRC thì ngược lại, không so trực tiếp
được giữa hai bài có tỷ lệ dương khác nhau.

Hai chỉ số cuối là của em. QWK tôn trọng thứ tự, nhầm syn thành ant bị phạt gấp
bốn so với nhầm syn thành add. Polar error là tỷ lệ nhầm thẳng syn với ant, lỗi
nguy hiểm nhất về lâm sàng vì nó kê sai hướng.

Quy tắc em tự đặt: chọn một chỉ số chính trước khi chạy, rồi dùng đúng nó cho
early stopping và cho mọi so sánh. Chọn sau khi thấy kết quả thì thành chọn cái
nào đẹp nhất.

## Slide 48 · Các mô hình đã công bố · ~60s

Xếp theo thời gian để thấy lĩnh vực đi đường nào.

DeepSynergy năm 2018 là MLP trên fingerprint với biểu hiện gen, ROC-AUC khoảng
0,90. DeepDDS năm 2022 đưa GCN vào, chạy trên đồ thị phân tử kèm attention,
khoảng 0,93. DTSyn cũng năm 2022 dùng hai transformer, một mức token nguyên tử
và một mức phân tử, báo 0,89. AttenSyn và MD-Syn đi tiếp hướng attention,
khoảng 0,90.

Dòng cuối đáng để ý: XGBoost trên fingerprint và biểu hiện, không học sâu gì,
mà khó vượt ở các split khó.

Điểm chung của cả bảng, và đây là khe hở em nhắm vào: các bài đều dùng nhãn nhị
phân, thường bỏ vùng trung tính, và trình bày attention như lời giải thích mà
không kiểm định xem lời giải thích đó có đúng không.

## Slide 49 · Ngăn phần 6 · ~20s

Phần sáu, giải thích mô hình. Đây là phần em đầu tư nhiều nhất, và cũng là phần
em thấy lĩnh vực còn yếu nhất.

## Slide 50 · Giải thích mô hình là gì · ~75s

Attribution là chia điểm công lao cho từng thành phần đầu vào. Trong bài của em,
thành phần đó là gen, nguyên tử, mảnh cấu trúc, hoặc cạnh mạng.

Có hai tiêu chí mà em thấy hay bị gộp làm một. Trung thực là lời giải thích có
phản ánh đúng mô hình không. Đúng sinh học là nó có khớp tri thức đã biết không.
Hai cái đó khác nhau, và một lời giải thích có thể đạt cái này mà không đạt cái
kia.

Về phương pháp, Integrated Gradients có tính chất completeness, nghĩa là tổng
điểm quy gán bằng đúng chênh lệch đầu ra. GNNExplainer học một mặt nạ cho từng
mẫu. Còn attention thì sẵn có trong mô hình, nhưng attention không phải
attribution, nó là trọng số nội bộ chứ không phải điểm công lao.

Và đây là luận điểm của em cho cả phần này. Nếu mô hình chỉ nhớ tên thuốc, thì
lời giải thích trung thực của nó vẫn sai sinh học, vì nó trung thực với một mô
hình đang nhớ. Nên phải kiểm tra mô hình trước, rồi mới trách phương pháp giải
thích.

## Slide 51 · Thống kê và đối chứng null · ~60s

Null là giá trị mà một chỉ số sẽ có nếu không có gì đặc biệt xảy ra. Tung đồng
xu 10 lần được 6 ngửa, con số 6 đứng một mình không nói gì, nó chỉ có nghĩa khi
đặt cạnh con số 5.

Ba cách dựng null cho bài của em: hoán vị nhãn, xáo mạng nhưng giữ bậc, và chọn
ngẫu nhiên đúng số đơn vị. Điều kiện bắt buộc là null phải đi qua đúng đường ống
như kết quả thật, cùng cách chuẩn hóa, cùng cách chia tập.

Cách em báo số: mỗi chỉ số báo ba con số, giá trị thật, giá trị null, và hiệu
giữa hai cái. Thử nhiều giả thuyết thì hiệu chỉnh FDR. Và báo khoảng tin cậy
qua nhiều seed nhiều fold, không báo một con số lẻ.

## Slide 52 · Đo chất lượng một lời giải thích · ~75s

Bốn câu hỏi, mỗi câu một chỉ số và một null.

Lời giải thích có phản ánh mô hình không: dùng Fid cộng và Fid trừ, so với xóa
ngẫu nhiên đúng số đơn vị.

Có ổn định giữa các lần chạy không: Jaccard@k qua các seed và các fold, null là
ghép hai bộ ba khác nhau.

Có ổn định khi đổi quy ước nhãn không: cũng Jaccard@k, nhưng qua các điểm số và
các ngưỡng khác nhau.

Có khớp sinh học không: làm giàu pathway và case study, so với một tập gen ngẫu
nhiên cùng kích thước.

Hai điều em muốn nhấn. Trung thực, ổn định và đúng sinh học là ba tính chất
riêng biệt, đạt được cái này không kéo theo cái kia, nên phải đo cả ba.

Và case study phải chọn trước khi chạy. Chọn sau khi thấy kết quả thì chỉ là
tìm ví dụ hợp ý mình.

## Slide 53 · Lĩnh vực đang yếu ở đâu · ~90s

Slide cuối, em gom lại sáu chỗ mà em thấy lĩnh vực này còn yếu.

Quy ước nhãn: bốn điểm số chỉ tương quan lỏng lẻo với nhau, mà ngưỡng thì theo
thói quen.

Vùng trung tính: bị xóa để bài toán dễ hơn, và chưa ai đo cái giá của việc đó.

Nhớ danh tính: 38 thuốc là quá ít, nên mô hình chỉ biết tên đã gần bằng học sâu.

Split quá dễ: số đẹp phần lớn lấy từ chia ngẫu nhiên, còn leave-drug mới là
tình huống thật.

Attention: được trình bày như lời giải thích mà không ai kiểm định.

Và thiếu đối chứng: không có null để so, ba tiêu chí đánh giá lời giải thích thì
bị gộp làm một.

Sáu chỗ này là chỗ em chọn để làm. Buổi báo cáo sau em trình bày em làm thế nào.

Em xin hết. Mời thầy cô cho ý kiến.
