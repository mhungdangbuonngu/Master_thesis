# -*- coding: utf-8 -*-
"""Deck 1: kien thuc nen. Day du khai niem tin sinh, van giu it chu."""
from deck import (new_deck, cover, content, divider, card, box, table, lines,
                  arrow, stat, note, save,
                  NAVY, RED, BLUE, GREEN, AMBER, SLATE, ML, CW)

prs = new_deck()

# ===================== BIA =====================
cover(prs,
      "Hiệp đồng thuốc: kiến thức nền",
      "Tin sinh học, hóa tin, học máy và giải thích mô hình",
      ["Học viên: [Họ và tên] — [MSHV]",
       "Giảng viên hướng dẫn: [Tên giảng viên]",
       "Hà Nội, 2026"])

s = content(prs, "Nội dung")
W, H = 4.03, 2.3
X = [ML, 4.65, 8.93]
Y = [1.25, 3.85]
items = [
    ("1. Tin sinh học", ["Từ DNA tới protein", "Dữ liệu omics, chuẩn hóa", "Pathway, làm giàu, thuốc"], NAVY),
    ("2. Mạng sinh học", ["Đồ thị và PPI", "STRING, hub, module", "Dược lý mạng"], BLUE),
    ("3. Hóa tin", ["SMILES và đồ thị phân tử", "Fingerprint, Tanimoto", "Đích thuốc"], GREEN),
    ("4. Hiệp đồng thuốc", ["Liều–đáp ứng, IC50", "Loewe, Bliss, HSA, ZIP", "Nhãn, nhiễu, lâm sàng"], AMBER),
    ("5. Dữ liệu, học máy", ["GDSC, L1000, O'Neil", "Chia dữ liệu, chỉ số", "Mô hình đã công bố"], SLATE),
    ("6. Giải thích", ["Attribution, null", "Trung thực và ổn định", "Chỗ lĩnh vực còn yếu"], RED),
]
for i, (h, its, c) in enumerate(items):
    card(s, X[i % 3], Y[i // 3], W, H, h, its, accent=c, size=14, after=10)

# ===================== PHAN 1: TIN SINH HOC =====================
divider(prs, "PHẦN 1", "Tin sinh học cơ bản", "Dữ liệu sinh học đến từ đâu và được mô tả bằng gì")

s = content(prs, "Từ DNA tới protein")
box(s, ML, 1.35, 3.3, 1.0, "DNA", "bộ mã, giống nhau ở mọi tế bào", fill=NAVY, ts=18, bs=13)
arrow(s, 3.75, 1.85, 4.15, 1.85)
box(s, 4.20, 1.35, 3.3, 1.0, "RNA", "bản sao của gen đang được đọc", fill=BLUE, ts=18, bs=13)
arrow(s, 7.60, 1.85, 8.00, 1.85)
box(s, 8.05, 1.35, 4.91, 1.0, "Protein", "thứ thi hành mọi việc trong tế bào", fill=GREEN, ts=18, bs=13)
card(s, ML, 2.70, 4.03, 2.0, "Ba mức dữ liệu", [
    "Genome: toàn bộ DNA",
    "Transcriptome: mức đọc từng gen",
    "Proteome: lượng protein thật sự",
], accent=NAVY, size=14)
card(s, 4.65, 2.70, 4.03, 2.0, "Đo được cái nào", [
    "Transcriptome đo rẻ và phổ biến nhất",
    "Proteome đắt, ít dữ liệu công khai",
    "Nên mô hình thường dùng biểu hiện gen",
], accent=BLUE, size=14)
card(s, 8.93, 2.70, 4.03, 2.0, "Tin sinh học làm gì", [
    "Chuẩn hóa và ghép các nguồn dữ liệu",
    "Chú giải: gen này là ai, làm gì",
    "Thống kê và mô hình hóa",
], accent=GREEN, size=14)
box(s, ML, 5.00, CW, 0.85,
    "Trong bài toán hiệp đồng, dữ liệu sinh học trả lời đúng một câu: dòng tế bào này là ai",
    fill=NAVY, ts=17)

s = content(prs, "Gen, protein, tế bào")
card(s, ML, 1.25, 4.03, 2.4, "Protein làm việc", [
    "Gen là công thức, protein là thứ thi hành",
    "Thuốc nhắm đích bám vào protein",
    "Trong dữ liệu, gen và protein là một",
], accent=NAVY, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.4, "Biểu hiện gen", [
    "Mỗi dòng tế bào là một vector gen",
    "Thường rút về 978 gen landmark",
    "Đây là bối cảnh sinh học của bài toán",
], accent=BLUE, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.4, "Dòng tế bào", [
    "Tế bào bệnh nhân, nuôi vô hạn",
    "Mỗi dòng một hồ sơ riêng",
    "A2058, MCF7, A549",
], accent=GREEN, size=14.5)
box(s, ML, 4.05, CW, 0.8,
    "Cùng một cặp thuốc có thể hiệp đồng ở dòng này và đối kháng ở dòng kia",
    "nên đơn vị dự đoán là bộ ba: thuốc A, thuốc B, dòng tế bào", fill=NAVY, ts=17, bs=14)
lines(s, ML, 5.20, CW, 1.4, [
    "Số bộ ba thì lớn, nhưng số thuốc và số dòng tế bào thì rất nhỏ",
    "Vì vậy mô hình có thể đoán giỏi chỉ bằng cách nhớ tên",
], size=15, after=10)

s = content(prs, "Các lớp dữ liệu omics")
table(s, [
    ["Lớp dữ liệu", "Đo cái gì", "Vai trò trong bài toán này"],
    ["Genomics", "đột biến, số bản sao gen", "mô tả tế bào, ít dùng làm đầu vào"],
    ["Transcriptomics", "mức đọc của từng gen", "đầu vào chính cho phía tế bào"],
    ["Proteomics", "lượng protein thật sự", "gần sinh học nhất, nhưng thiếu dữ liệu"],
    ["Epigenomics", "methyl hóa, trạng thái chromatin", "ít dùng trong lĩnh vực hiệp đồng"],
    ["Perturbation", "tế bào phản ứng khi tắt gen hoặc cho thuốc", "DepMap CRISPR, LINCS L1000"],
], ML, 1.30, CW, [2.8, 4.6, 5.19], size=14, head_size=13.5, rowh=0.56)
note(s, ML, 4.95, CW, "Multi-omics là ghép nhiều lớp lại; càng nhiều lớp càng khó chuẩn hóa và càng dễ rò rỉ thông tin")
box(s, ML, 5.45, CW, 0.9,
    "Lĩnh vực hiệp đồng thuốc gần như chỉ dùng transcriptomics",
    "vì đó là lớp duy nhất phủ đủ hàng nghìn dòng tế bào", fill=NAVY, ts=16, bs=13)

s = content(prs, "Biểu hiện gen và chuẩn hóa")
box(s, ML, 1.30, 2.9, 0.85, "RNA-seq", "đo mức đọc từng gen", fill=NAVY, ts=15, bs=12)
arrow(s, 3.32, 1.72, 3.66, 1.72)
box(s, 3.70, 1.30, 2.9, 0.85, "TPM", "bản sao trên một triệu", fill=NAVY, ts=15, bs=12)
arrow(s, 6.65, 1.72, 6.99, 1.72)
box(s, 7.03, 1.30, 2.9, 0.85, "log2(TPM + 1)", "nén khoảng giá trị", fill=BLUE, ts=15, bs=12)
arrow(s, 9.98, 1.72, 10.32, 1.72)
box(s, 10.36, 1.30, 2.6, 0.85, "z-score", "so với trung bình", fill=BLUE, ts=15, bs=12)
card(s, ML, 2.45, 6.1, 2.1, "Vì sao phải chuẩn hóa", [
    "Giá trị gốc chênh nhau hàng nghìn lần",
    "Khác lô thí nghiệm thì khác thang đo (batch effect)",
    "Z-score chỉ được tính trên tập huấn luyện",
], accent=BLUE, size=14.5)
card(s, 6.86, 2.45, 6.1, 2.1, "Gen landmark L1000", [
    "978 gen đại diện, chọn từ dự án LINCS",
    "Phần còn lại của transcriptome suy ra được",
    "Giảm chiều dữ liệu mà giữ phần lớn thông tin",
], accent=GREEN, size=14.5)
box(s, ML, 4.85, CW, 0.9,
    "Chuẩn hóa trên toàn bộ dữ liệu là một kiểu rò rỉ thông tin âm thầm",
    "và gần như không thể phát hiện khi đọc bảng kết quả", fill=RED, ts=16, bs=13)

s = content(prs, "Định danh gen và chú giải")
card(s, ML, 1.25, 6.1, 2.3, "Một gen có nhiều tên", [
    "Ký hiệu HGNC: MAP2K1",
    "Tên quen dùng: MEK1",
    "Mã số: Entrez 5604, Ensembl ENSG00000169032",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.3, "Nguồn chú giải", [
    "HGNC: tên chuẩn của gen người",
    "UniProt: protein và chức năng",
    "NCBI, Ensembl: toạ độ và mã số",
], accent=BLUE, size=14.5)
box(s, ML, 3.85, CW, 0.9,
    "Khớp tên giữa các nguồn là việc tốn thời gian nhất của khâu dữ liệu",
    "NCI-H460, NCIH460 và H460 là cùng một dòng tế bào", fill=AMBER, ts=16, bs=13)
lines(s, ML, 5.05, CW, 1.5, [
    "Một ánh xạ sai là một nhãn sai âm thầm, chạy suốt mọi thí nghiệm về sau",
    "Quy tắc: chỉ khớp chính xác, không bao giờ khớp mờ theo tên gần giống",
], size=15, after=10)

s = content(prs, "Khâu xử lý dữ liệu")
table(s, [
    ["Bước", "Làm gì", "Rủi ro nếu bỏ qua"],
    ["Kiểm tra chất lượng", "loại mẫu hỏng, mẫu nhiễm", "nhiễu đi thẳng vào nhãn"],
    ["Hiệu chỉnh lô", "ComBat hoặc mô hình tuyến tính", "mô hình học lô thí nghiệm thay vì học sinh học"],
    ["Xử lý thiếu dữ liệu", "điền hoặc loại gen, loại mẫu", "điền sai làm méo tương quan"],
    ["Giảm chiều", "PCA, UMAP để nhìn cấu trúc dữ liệu", "không phát hiện được cụm bất thường"],
    ["Ghim phiên bản", "ghi rõ phiên bản mỗi cơ sở dữ liệu", "chạy lại sau sáu tháng ra số khác"],
], ML, 1.30, CW, [2.9, 4.6, 5.09], size=13.5, head_size=13, rowh=0.52)
box(s, ML, 4.80, CW, 0.95,
    "Dòng tế bào cũng cần định danh chuẩn: Cellosaurus và Cell Model Passports",
    "đó là cách duy nhất để chắc hai bộ dữ liệu đang nói về cùng một dòng", fill=NAVY, ts=16, bs=13)
note(s, ML, 6.05, CW, "Phần lớn thời gian của một dự án tin sinh nằm ở khâu này, không nằm ở khâu mô hình")

s = content(prs, "Ung thư, đột biến, dòng tế bào")
card(s, ML, 1.25, 4.03, 2.5, "Ung thư", [
    "Tế bào phân chia không ngừng",
    "Không chịu chết khi đã hỏng",
], accent=RED, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.5, "Đột biến", [
    "Một chữ sai làm protein hỏng",
    "BRAF V600E: kẹt ở chế độ bật",
    "CNV: gen bị nhân bản hoặc mất",
], accent=AMBER, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.5, "Dòng tế bào", [
    "Lấy từ bệnh nhân, nuôi vô hạn",
    "Mỗi dòng một hồ sơ riêng",
    "CCLE và DepMap cung cấp dữ liệu",
], accent=NAVY, size=14.5)
card(s, ML, 4.05, 6.1, 2.1, "Gen thiết yếu và DepMap", [
    "CRISPR tắt lần lượt từng gen rồi xem tế bào còn sống không",
    "Điểm Chronos: gần 0 là không sao, gần −1 là chết",
], accent=GREEN, size=14.5)
card(s, 6.86, 4.05, 6.1, 2.1, "Cái bẫy", [
    "Có nhóm gen thiết yếu với mọi tế bào",
    "Chúng luôn âm, nên không nói gì về một cặp thuốc cụ thể",
], accent=RED, size=14.5)

s = content(prs, "Oncogene và gen ức chế khối u")
card(s, ML, 1.25, 4.03, 2.5, "Oncogene", [
    "Bật quá mức thì thúc tế bào phân chia",
    "Thường do đột biến hoặc nhân bản gen",
    "KRAS, BRAF, EGFR, MYC",
], accent=RED, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.5, "Gen ức chế khối u", [
    "Mất chức năng thì tế bào hết phanh",
    "Cần hỏng cả hai bản sao",
    "TP53, RB1, PTEN, BRCA1/2",
], accent=NAVY, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.5, "Driver và passenger", [
    "Driver: đột biến thật sự gây bệnh",
    "Passenger: đi kèm, không gây bệnh",
    "Phần lớn đột biến là passenger",
], accent=BLUE, size=14.5)
box(s, ML, 4.05, CW, 0.95,
    "Nghiện oncogene: khối u phụ thuộc vào một oncogene duy nhất",
    "đó là lý do thuốc nhắm đích hiệu quả ở một số dòng tế bào và vô dụng ở dòng khác", fill=NAVY, ts=16, bs=13)
lines(s, ML, 5.30, CW, 1.3, [
    "Hồ sơ đột biến của dòng tế bào giải thích phần lớn khác biệt về đáp ứng thuốc",
], size=15)

s = content(prs, "Chu kỳ tế bào và chết theo chương trình")
box(s, ML, 1.35, 2.75, 0.85, "G1", "chuẩn bị", fill=NAVY, ts=16, bs=12)
arrow(s, 3.17, 1.77, 3.51, 1.77)
box(s, 3.55, 1.35, 2.75, 0.85, "S", "nhân đôi DNA", fill=NAVY, ts=16, bs=12)
arrow(s, 6.37, 1.77, 6.71, 1.77)
box(s, 6.75, 1.35, 2.75, 0.85, "G2", "kiểm tra lỗi", fill=NAVY, ts=16, bs=12)
arrow(s, 9.57, 1.77, 9.91, 1.77)
box(s, 9.95, 1.35, 3.01, 0.85, "M", "phân chia", fill=BLUE, ts=16, bs=12)
card(s, ML, 2.50, 6.1, 2.2, "Chốt kiểm soát", [
    "Tế bào dừng lại nếu DNA hỏng",
    "TP53 là chốt quan trọng nhất",
    "Mất chốt thì tế bào mang lỗi vẫn chia tiếp",
], accent=BLUE, size=14.5)
card(s, 6.86, 2.50, 6.1, 2.2, "Apoptosis", [
    "Chết theo chương trình, tế bào tự tháo dỡ",
    "Đích cuối cùng của phần lớn thuốc ung thư",
    "Tế bào ung thư thường chặn được đường này",
], accent=GREEN, size=14.5)
box(s, ML, 4.95, CW, 0.95,
    "Thuốc không giết tế bào trực tiếp, mà đẩy tế bào tới chỗ tự hủy",
    "nên hai thuốc đánh vào hai điểm khác nhau của cùng một lộ trình có thể cộng hưởng", fill=NAVY, ts=16, bs=13)

s = content(prs, "Pathway và bộ gen chức năng")
table(s, [
    ["Nguồn", "Nội dung", "Đặc điểm"],
    ["KEGG", "pathway vẽ tay, có hướng và có dấu", "hsa04010 là MAPK, hsa04151 là PI3K-Akt"],
    ["Reactome", "phản ứng sinh hóa chi tiết", "phân cấp, cập nhật thường xuyên"],
    ["Gene Ontology", "chức năng, quá trình, vị trí trong tế bào", "rất rộng, dùng để chú giải"],
    ["MSigDB", "kho bộ gen gộp từ nhiều nguồn", "định dạng chuẩn để chấm làm giàu"],
], ML, 1.30, CW, [2.4, 5.0, 5.19], size=14, head_size=13.5, rowh=0.6)
box(s, ML, 4.45, CW, 0.9,
    "Bộ gen (gene set) là một danh sách gen cùng tham gia một chức năng",
    "đây là đơn vị để nói lời giải thích có ý nghĩa sinh học hay không", fill=NAVY, ts=16, bs=13)
note(s, ML, 5.60, CW, "Nếu vừa dùng KEGG làm đầu vào mô hình vừa dùng KEGG để chấm điểm thì thành vòng lặp tự khen")

s = content(prs, "Phân tích làm giàu")
card(s, ML, 1.25, 6.1, 2.3, "Hai cách làm", [
    "ORA: lấy top-k gen rồi kiểm định chồng lấn",
    "GSEA: xếp hạng toàn bộ gen, xem bộ gen dồn về đầu hay cuối",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.3, "Thống kê đi kèm", [
    "p-value từ kiểm định Fisher hoặc hoán vị",
    "Hiệu chỉnh đa kiểm định: FDR, Benjamini–Hochberg",
    "Báo cả kích thước hiệu ứng, không chỉ p",
], accent=BLUE, size=14.5)
box(s, ML, 3.85, CW, 0.95,
    "Thử hàng nghìn bộ gen thì kiểu gì cũng có vài bộ p < 0,05",
    "nên không hiệu chỉnh đa kiểm định là tự lừa mình", fill=RED, ts=16, bs=13)
lines(s, ML, 5.10, CW, 1.5, [
    "Làm giàu chỉ nói lên mối liên quan thống kê, không chứng minh cơ chế",
    "Phải so với một tập gen ngẫu nhiên cùng kích thước, đã loại gen thiết yếu phổ biến",
], size=15, after=10)

s = content(prs, "Pathway tín hiệu và cơ chế bù trừ")
lane1 = ["EGFR", "KRAS", "BRAF", "MEK1/2", "ERK1/2"]
lane2 = ["EGFR", "PI3K", "AKT", "mTOR", "Sống sót"]
w, h = 2.1, 0.72
for i, t in enumerate(lane1):
    x = ML + i * (w + 0.36)
    box(s, x, 1.55, w, h, t, fill=RED if i == 3 else NAVY, ts=15)
    if i < len(lane1) - 1:
        arrow(s, x + w, 1.91, x + w + 0.34, 1.91)
for i, t in enumerate(lane2):
    x = ML + i * (w + 0.36)
    box(s, x, 2.72, w, h, t, fill=RED if i == 2 else NAVY, ts=15)
    if i < len(lane2) - 1:
        arrow(s, x + w, 3.08, x + w + 0.34, 3.08)
note(s, ML, 1.22, 6.0, "Nhánh tăng sinh")
note(s, ML, 3.52, 8.0, "Nhánh sống sót · hai nhánh nối nhau bằng crosstalk")
note(s, 11.0, 1.22, 2.0, "ô đỏ: nơi thuốc chặn", color=RED)
card(s, ML, 4.05, 6.1, 1.95, "Vì sao hai thuốc hiệp đồng", [
    "Chặn MEK thì tế bào bật nhánh AKT để bù",
    "Chặn một nhánh: tế bào vẫn sống",
    "Chặn cả hai: tế bào hết lối thoát",
], accent=GREEN, size=14.5)
card(s, 6.86, 4.05, 6.1, 1.95, "Cơ chế khác hay gặp", [
    "Synthetic lethality",
    "Chặn đường vòng kháng thuốc",
    "Thay đổi phơi nhiễm thuốc",
], accent=SLATE, size=14.5)

s = content(prs, "Các nhóm thuốc ung thư")
table(s, [
    ["Nhóm", "Cơ chế", "Ví dụ trong O'Neil"],
    ["Gây tổn thương DNA", "cắt hoặc nối sai DNA, chặn topoisomerase", "cisplatin, carboplatin, etoposide, doxorubicin"],
    ["Kháng chuyển hóa", "giả làm nguyên liệu, chặn tổng hợp DNA", "gemcitabine, 5-FU, methotrexate"],
    ["Chặn phân bào", "phá bộ khung vi ống khi tế bào chia", "paclitaxel, vinblastine"],
    ["Nhắm đích kinase", "chặn một protein tín hiệu cụ thể", "MK-2206 chặn AKT, PD325901 chặn MEK"],
    ["Chặn sửa chữa DNA", "khóa đường sửa chữa dự phòng", "nhóm ức chế PARP"],
], ML, 1.30, CW, [2.9, 4.5, 5.19], size=13.5, head_size=13, rowh=0.52)
box(s, ML, 4.80, CW, 0.95,
    "Hóa trị kinh điển đánh vào mọi tế bào đang phân chia nên độc tính cao",
    "thuốc nhắm đích chọn lọc hơn nhưng dễ bị kháng", fill=NAVY, ts=16, bs=13)
note(s, ML, 6.05, CW, "Biết thuốc thuộc nhóm nào là điều kiện để đọc được lời giải thích của mô hình")

s = content(prs, "Kháng thuốc: vì sao phải phối hợp")
card(s, ML, 1.25, 4.03, 2.5, "Đột biến ở đích", [
    "Protein đổi hình, thuốc không bám được nữa",
    "Thường xuất hiện sau vài tháng điều trị",
], accent=RED, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.5, "Đường vòng", [
    "Tế bào bật một nhánh khác để bù",
    "Chặn MEK thì AKT bật lên",
    "Đây là cơ chế hay gặp nhất",
], accent=AMBER, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.5, "Bơm đẩy thuốc", [
    "Bơm ABC tống thuốc ra khỏi tế bào",
    "Làm giảm nồng độ thuốc bên trong",
], accent=BLUE, size=14.5)
box(s, ML, 4.05, CW, 0.95,
    "Một thuốc đơn gần như luôn bị kháng",
    "phối hợp là cách chặn nhiều lối thoát cùng lúc, không phải chỉ để tăng liều", fill=NAVY, ts=16, bs=13)
lines(s, ML, 5.30, CW, 1.3, [
    "Đó là lý do dự đoán hiệp đồng đáng làm: tìm cặp chặn được cả lối chính lẫn lối thoát",
], size=15)

s = content(prs, "Bốn lý do sinh học khiến tổ hợp hiệu quả")
card(s, ML, 1.25, 6.1, 2.2, "1. Chặn song song", [
    "Hai thuốc chặn hai nhánh của cùng một hệ",
    "Ví dụ MEK và AKT",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.2, "2. Chặn đường thoát", [
    "Thuốc thứ hai chặn đúng cơ chế kháng của thuốc thứ nhất",
], accent=BLUE, size=14.5)
card(s, ML, 3.65, 6.1, 2.2, "3. Synthetic lethality", [
    "Hỏng một gen thì tế bào vẫn sống",
    "Hỏng cả hai thì chết",
    "Kinh điển: ức chế PARP trên khối u đột biến BRCA",
], accent=GREEN, size=14.5)
card(s, 6.86, 3.65, 6.1, 2.2, "4. Thay đổi phơi nhiễm", [
    "Thuốc này làm thuốc kia vào tế bào nhiều hơn",
    "Hoặc chậm bị đào thải hơn",
], accent=SLATE, size=14.5)
note(s, ML, 6.05, CW, "Bốn cơ chế này là thứ mà lời giải thích của mô hình nên trỏ tới, nếu nó thật sự có ý nghĩa sinh học")

s = content(prs, "Từ đĩa nuôi cấy tới bệnh nhân")
box(s, ML, 1.35, 2.9, 0.9, "Dòng tế bào 2D", "rẻ, chạy được hàng chục nghìn tổ hợp", fill=NAVY, ts=15, bs=11)
arrow(s, 3.32, 1.80, 3.66, 1.80)
box(s, 3.70, 1.35, 2.9, 0.9, "Organoid", "giữ cấu trúc mô, gần bệnh nhân hơn", fill=BLUE, ts=15, bs=11)
arrow(s, 6.65, 1.80, 6.99, 1.80)
box(s, 7.03, 1.35, 2.9, 0.9, "PDX, in vivo", "ghép khối u người lên chuột", fill=GREEN, ts=15, bs=11)
arrow(s, 9.98, 1.80, 10.32, 1.80)
box(s, 10.36, 1.35, 2.6, 0.9, "Lâm sàng", "thử nghiệm trên người", fill=RED, ts=15, bs=11)
card(s, ML, 2.55, 6.1, 2.2, "Dược động và dược lực", [
    "PK: thuốc đi đâu, còn bao lâu trong máu",
    "PD: ở nồng độ đó thuốc làm được gì",
    "Nồng độ trong đĩa nuôi cấy có thể không đạt được trên người",
], accent=BLUE, size=14.5)
card(s, 6.86, 2.55, 6.1, 2.2, "Cửa sổ điều trị", [
    "Khoảng giữa liều có tác dụng và liều gây độc",
    "Phối hợp thì độc tính cũng cộng lại",
    "Hiệp đồng về hiệu lực mà cũng hiệp đồng về độc thì vô dụng",
], accent=RED, size=14.5)
box(s, ML, 5.00, CW, 0.9,
    "Mọi kết quả trong luận văn này nằm ở mức dòng tế bào 2D",
    "đó là bước sàng lọc đầu tiên, không phải bằng chứng lâm sàng", fill=NAVY, ts=16, bs=13)

# ===================== PHAN 2: MANG SINH HOC =====================
divider(prs, "PHẦN 2", "Mạng sinh học", "Protein không làm việc một mình, nên dữ liệu cũng là một đồ thị")

s = content(prs, "Đồ thị: từ vựng tối thiểu")
table(s, [
    ["Khái niệm", "Nghĩa", "Trong mạng sinh học"],
    ["Node (đỉnh)", "một thực thể", "một protein hoặc một gen"],
    ["Cạnh (edge)", "quan hệ giữa hai node", "hai protein có tương tác"],
    ["Bậc (degree)", "số cạnh nối vào một node", "protein này tương tác với bao nhiêu protein khác"],
    ["Hub", "node có bậc rất cao", "TP53, AKT1 nối hàng trăm protein"],
    ["Đường đi, khoảng cách", "chuỗi cạnh nối hai node", "đích thuốc A cách đích thuốc B mấy bước"],
    ["k-hop", "các node trong vòng k bước", "vùng lân cận quanh đích thuốc"],
], ML, 1.30, CW, [2.8, 3.8, 5.99], size=13.5, head_size=13, rowh=0.50)
box(s, ML, 5.15, CW, 0.9,
    "Ma trận kề là cách viết đồ thị thành bảng số",
    "đó là dạng mà mạng nơ-ron đồ thị nhận vào", fill=NAVY, ts=16, bs=13)

s = content(prs, "PPI: tương tác protein–protein")
card(s, ML, 1.25, 4.03, 2.6, "Là gì", [
    "Hai protein bám vào nhau",
    "Hoặc cùng tham gia một phức hợp",
    "Hoặc có bằng chứng liên quan chức năng",
], accent=NAVY, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.6, "Đo bằng cách nào", [
    "Y2H: thử từng cặp trong nấm men",
    "AP-MS: kéo một protein xuống, xem ai đi cùng",
    "Suy ra từ đồng biểu hiện hoặc từ văn bản khoa học",
], accent=BLUE, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.6, "Nguồn dữ liệu", [
    "STRING: lớn nhất, có điểm tin cậy",
    "BioGRID, IntAct: tương tác thực nghiệm",
    "HuRI: bản đồ Y2H quy mô lớn",
], accent=GREEN, size=14.5)
box(s, ML, 4.15, CW, 0.9,
    "Cạnh PPI không có hướng và không có dấu",
    "nó chỉ nói hai protein liên quan, không nói ai kích hoạt ai", fill=NAVY, ts=16, bs=13)
note(s, ML, 5.35, CW, "Khác với pathway KEGG: pathway do người vẽ, có mũi tên và có dấu kích hoạt hay ức chế")

s = content(prs, "STRING và điểm tin cậy")
card(s, ML, 1.25, 6.1, 2.4, "Điểm combined_score", [
    "Thang 0 đến 1000, gộp nhiều loại bằng chứng",
    "Thực nghiệm, cơ sở dữ liệu, đồng biểu hiện, khai phá văn bản",
    "Lọc ≥ 700 nghĩa là chỉ giữ cạnh tin cậy cao",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.4, "Quy mô dùng trong luận văn", [
    "STRING v12, người, mã loài 9606",
    "16.201 nút và 236.930 cạnh sau khi lọc",
    "Giao với gen có trong bảng biểu hiện",
], accent=BLUE, size=14.5)
box(s, ML, 4.00, CW, 0.9,
    "Hạ ngưỡng thì mạng dày lên nhưng nhiễu cũng tăng",
    "nên ngưỡng lọc là một lựa chọn phải báo cáo, không phải chi tiết kỹ thuật", fill=AMBER, ts=16, bs=13)
note(s, ML, 5.20, CW, "Một phần lớn cạnh STRING đến từ khai phá văn bản, nên mạng phản ánh cả thói quen nghiên cứu của con người")

s = content(prs, "Tính chất của mạng PPI")
card(s, ML, 1.25, 4.03, 2.5, "Phân bố bậc lệch", [
    "Phần lớn protein có ít cạnh",
    "Một số ít hub có hàng trăm cạnh",
    "Gọi là mạng không tỷ lệ",
], accent=NAVY, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.5, "Module", [
    "Các cụm protein nối dày với nhau",
    "Thường tương ứng một chức năng",
    "Bệnh hay gắn với một module",
], accent=BLUE, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.5, "Hệ quả", [
    "Hub nằm trên hầu hết đường đi",
    "Lời giải thích trỏ vào hub chưa nói lên gì",
    "Mọi chỉ số trên mạng đều cần null",
], accent=RED, size=14.5)
box(s, ML, 4.05, CW, 0.95,
    "Đối chứng chuẩn: xáo mạng giữ nguyên bậc từng node",
    "mọi đường đi cụ thể bị phá, nhưng hub vẫn là hub", fill=NAVY, ts=16, bs=13)
lines(s, ML, 5.30, CW, 1.3, [
    "Nếu kết quả không đổi khi xáo mạng thì mô hình không dùng sinh học của mạng",
], size=15)

s = content(prs, "Dược lý mạng")
card(s, ML, 1.25, 6.1, 2.5, "Ý tưởng", [
    "Mỗi thuốc có một cụm đích trên mạng",
    "Mỗi bệnh có một module",
    "Đo khoảng cách giữa hai cụm đích: chỉ số s_AB",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.5, "Phát hiện của Cheng và cộng sự", [
    "Tổ hợp hiệu quả thường có hai cụm đích tách nhau",
    "Nhưng cùng chạm vào module bệnh",
    "Hai cụm chồng lên nhau thì hay vô ích hoặc độc",
], accent=BLUE, size=14.5)
box(s, ML, 4.10, CW, 0.95,
    "Dùng chính s_AB để dự đoán chỉ đạt AUC 0,589, gần với đoán mò",
    "mạng giải thích tốt hơn là dự đoán", fill=RED, ts=16, bs=13)
note(s, ML, 5.35, CW, "Vì vậy trong luận văn, s_AB được dùng làm mốc so sánh cho lời giải thích, không phải làm mô hình dự đoán")

s = content(prs, "Đưa mạng vào mô hình")
card(s, ML, 1.25, 4.03, 2.6, "node2vec", [
    "Đi bộ ngẫu nhiên trên mạng",
    "Học một vector cho từng gen",
    "Gen tương tác nhau thì vector gần nhau",
], accent=NAVY, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.6, "GNN trên mạng", [
    "Mỗi gen cập nhật theo hàng xóm",
    "L lớp chỉ nhìn được L bước",
    "Đích hai thuốc cách xa thì không gặp nhau",
], accent=BLUE, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.6, "Lan truyền đích thuốc", [
    "Vector đích lan ra các gen lân cận",
    "Cách đơn giản mà hiệu quả bất ngờ",
    "Mạnh hơn hẳn fingerprint ở quy mô lớn",
], accent=GREEN, size=14.5)
box(s, ML, 4.15, CW, 0.95,
    "Đưa mạng vào thì phải chứng minh mạng có ích",
    "bằng cách chạy lại với mạng đã xáo và so hai kết quả", fill=NAVY, ts=16, bs=13)
note(s, ML, 5.40, CW, "Quan sát đáng chú ý: PPI dùng để lan truyền đích thì có ích, nhưng PPI dùng làm toàn bộ biểu diễn thuốc thì không")

# ===================== PHAN 3: HOA TIN =====================
divider(prs, "PHẦN 3", "Hóa tin", "Mô tả một phân tử thuốc cho máy tính")

s = content(prs, "Biểu diễn phân tử")
box(s, ML, 1.30, 3.9, 0.95, "SMILES", "chuỗi ký tự mã hóa cấu trúc", fill=NAVY, ts=16, bs=12)
arrow(s, 4.32, 1.78, 4.70, 1.78)
box(s, 4.75, 1.30, 3.9, 0.95, "Đồ thị phân tử", "nguyên tử là node, liên kết là cạnh", fill=BLUE, ts=16, bs=12)
arrow(s, 8.70, 1.78, 9.08, 1.78)
box(s, 9.12, 1.30, 3.84, 0.95, "Đặc trưng nguyên tử", "nguyên tố, bậc, hóa trị, tính thơm", fill=GREEN, ts=16, bs=12)
card(s, ML, 2.55, 6.1, 2.2, "RDKit làm gì", [
    "Đọc SMILES và dựng đồ thị",
    "Chuẩn hóa: dạng chuẩn, trạng thái ion hóa",
    "Cắt phân tử thành mảnh theo quy tắc BRICS",
], accent=NAVY, size=14.5)
card(s, 6.86, 2.55, 6.1, 2.2, "Bẫy cần biết", [
    "Một phân tử có nhiều chuỗi SMILES hợp lệ",
    "Ký tự SMILES không ánh xạ một–một về nguyên tử",
    "Phức platin như carboplatin hay thiếu trong cơ sở dữ liệu",
], accent=RED, size=14.5)
box(s, ML, 5.05, CW, 0.9,
    "Giải thích ở cấp nguyên tử chỉ làm được khi mô hình nhận đồ thị",
    "nếu mô hình nhận chuỗi ký tự thì không quy được về nguyên tử nào", fill=NAVY, ts=16, bs=13)

s = content(prs, "Fingerprint, descriptor, độ tương tự")
table(s, [
    ["Cách mô tả", "Hình dạng", "Điểm mạnh, điểm yếu"],
    ["Morgan fingerprint (ECFP)", "vector nhị phân 1024 hoặc 2048 bit", "nhanh, mạnh bất ngờ, nhưng mỗi bit là một mảnh băm"],
    ["Descriptor lý hóa", "khối lượng, logP, số vòng, số liên kết quay", "gọn, hợp với mô hình cây"],
    ["Đồ thị phân tử", "nguyên tử và liên kết", "giải thích được tới từng nguyên tử"],
    ["Mảnh BRICS", "vài mảnh lớn cho mỗi phân tử", "đơn vị giải thích dễ đọc hơn nguyên tử"],
], ML, 1.30, CW, [3.2, 4.4, 4.99], size=13.5, head_size=13, rowh=0.6)
box(s, ML, 4.45, CW, 0.9,
    "Độ tương tự Tanimoto: hai phân tử chung bao nhiêu bit trên tổng số bit",
    "dùng để biết tập test có thật sự khác tập train hay không", fill=NAVY, ts=16, bs=13)
note(s, ML, 5.60, CW, "Trong O'Neil, Tanimoto trung vị giữa các thuốc chỉ khoảng 0,19: các thuốc khá khác nhau về cấu trúc")

s = content(prs, "Đích thuốc và cơ chế tác động")
card(s, ML, 1.25, 6.1, 2.4, "Đích là gì", [
    "Protein mà thuốc bám vào và thường là chặn lại",
    "Một thuốc có thể có nhiều đích",
    "Bám cả protein ngoài ý muốn: off-target",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.4, "Nguồn dữ liệu đích", [
    "DrugBank: đầy đủ nhất, cần license học thuật",
    "ChEMBL: mở, có cơ chế tác động",
    "DGIdb, TTD: gom từ nhiều nguồn",
], accent=BLUE, size=14.5)
box(s, ML, 4.00, CW, 0.9,
    "Vector đích là cầu nối duy nhất giữa hóa học của thuốc và sinh học của tế bào",
    fill=NAVY, ts=17)
lines(s, ML, 5.15, CW, 1.4, [
    "Hóa trị kinh điển thường không có đích hẹp, nên vector đích rỗng",
    "Thuốc mang mã nội bộ của hãng hay thiếu cả cấu trúc lẫn chú giải đích",
], size=15, after=10)

# ===================== PHAN 4: HIEP DONG =====================
divider(prs, "PHẦN 4", "Hiệp đồng thuốc", "Định nghĩa, cách đo, và chỗ các định nghĩa không đồng ý")

s = content(prs, "Liều–đáp ứng và IC50")
card(s, ML, 1.25, 6.1, 2.4, "Thí nghiệm cơ bản", [
    "Cho tế bào tiếp xúc thuốc ở nhiều mức liều",
    "Đo phần trăm tế bào bị ức chế",
    "Vẽ lên được một đường cong hình chữ S",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.4, "Các đại lượng", [
    "IC50: liều làm ức chế 50%, thuốc mạnh thì nhỏ",
    "Monotherapy: dữ liệu dùng một thuốc riêng lẻ",
    "Cần monotherapy mới tính được mức mong đợi",
], accent=BLUE, size=14.5)
box(s, ML, 4.00, CW, 0.95,
    "Tổ hợp được đo trên một lưới liều, ví dụ 4 × 4, mỗi ô là một phần trăm ức chế",
    "rồi cả lưới được tóm lại thành một con số duy nhất", fill=NAVY, ts=16, bs=13)
lines(s, ML, 5.25, CW, 1.3, [
    "Bước tóm tắt đó làm mất thông tin, và nhiễu giữa các bản lặp thì vẫn còn",
], size=15)

s = content(prs, "Ba khả năng khi trộn hai thuốc")
box(s, ML, 1.35, 4.03, 2.1, "Hiệp đồng", "hơn mức mong đợi · 1 + 1 > 2", fill=GREEN, ts=22, bs=16)
box(s, 4.65, 1.35, 4.03, 2.1, "Cộng tính", "đúng mức mong đợi · 1 + 1 = 2", fill=NAVY, ts=22, bs=16)
box(s, 8.93, 1.35, 4.03, 2.1, "Đối kháng", "kém mức mong đợi · 1 + 1 < 2", fill=RED, ts=22, bs=16)
lines(s, ML, 3.95, CW, 2.6, [
    "Câu khó không phải ba khả năng, mà là mức mong đợi bằng bao nhiêu",
    "Có bốn định nghĩa phổ biến, cho bốn con số khác nhau trên cùng một thí nghiệm",
    "Hiệp đồng là quan hệ đối xứng: đổi chỗ A và B thì kết quả không đổi",
], size=17, after=20)

s = content(prs, "Bốn cách tính mức mong đợi",
            "Ví dụ: A ức chế 40%, B ức chế 50%, trộn A + B ức chế 85%")
table(s, [
    ["Định nghĩa", "Mức mong đợi", "Phần dôi ra"],
    ["HSA — thuốc đơn mạnh nhất", "50%", ("+35", {"bold": True, "color": GREEN})],
    ["Bliss — hai thuốc độc lập", "70%", ("+15", {"bold": True, "color": GREEN})],
    ["Loewe — quy về liều tương đương", "tính theo liều", "tùy liều"],
    ["ZIP — kết hợp Loewe và Bliss", "tính theo liều", "tùy liều"],
], ML, 1.75, CW, [5.2, 3.6, 3.79], size=15, head_size=14, rowh=0.72)
note(s, ML, 5.50, CW,
     "Điểm Loewe trong DrugComb là chênh lệch phần trăm ức chế so với mức mong đợi, nên ngưỡng ±10 là đơn vị phần trăm")

s = content(prs, "Bốn điểm số không đồng ý với nhau")
stat(s, ML, 1.40, 3.6, "r = 0,28", "tương quan giữa điểm Loewe và điểm ZIP")
stat(s, 4.30, 1.40, 3.6, "21–34%", "số ma trận bị hai phương pháp gán nhãn ngược nhau")
card(s, 8.50, 1.30, 4.46, 2.2, "Ví dụ", [
    "Trộn chỉ ức chế 45%",
    "HSA: −5 → cộng tính",
    "Bliss: −25 → đối kháng",
], accent=RED, size=14.5)
box(s, ML, 3.90, CW, 0.85,
    "Nhãn hiệp đồng là một lựa chọn quy ước, không phải một sự thật đo được",
    fill=NAVY, ts=18)
lines(s, ML, 5.10, CW, 1.5, [
    "Hai bài báo dùng hai điểm khác nhau thì con số không so trực tiếp được",
    "Cách xử lý: chạy lại với một điểm thứ hai và với ngưỡng khác, rồi báo cả bảng độ nhạy",
], size=15, after=12)

s = content(prs, "Hiệp đồng không đồng nghĩa hiệu quả")
card(s, ML, 1.25, 6.1, 2.3, "Hai câu hỏi khác nhau", [
    "Tổ hợp này có mạnh không: nhìn phần trăm ức chế tuyệt đối",
    "Tổ hợp này có hiệp đồng không: nhìn phần dôi ra so với mức mong đợi",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.3, "Hai trường hợp dễ nhầm", [
    "Hai thuốc yếu, cộng lại vẫn yếu, nhưng điểm hiệp đồng rất cao",
    "Hai thuốc mạnh, cộng lại diệt gần hết, nhưng điểm hiệp đồng bằng không",
], accent=RED, size=14.5)
box(s, ML, 3.85, CW, 0.95,
    "Điểm hiệp đồng cao mà hiệu lực thấp thì không dùng được trên lâm sàng",
    "nên luôn đọc điểm hiệp đồng kèm với độ nhạy tuyệt đối", fill=NAVY, ts=16, bs=13)
lines(s, ML, 5.10, CW, 1.5, [
    "DrugComb có cột riêng cho độ nhạy, thường gọi là điểm S",
    "Phần lớn bài báo chỉ báo điểm hiệp đồng, nên bảng xếp hạng của họ chưa chắc là bảng tổ hợp đáng dùng",
], size=15, after=10)

s = content(prs, "Chou–Talalay và đường đồng hiệu lực")
card(s, ML, 1.25, 6.1, 2.4, "Chỉ số tổ hợp CI", [
    "CI = d_A/D_A + d_B/D_B",
    "d là liều dùng trong hỗn hợp, D là liều cần khi dùng một mình",
    "CI nhỏ hơn 1 là hiệp đồng, bằng 1 là cộng tính, lớn hơn 1 là đối kháng",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.4, "Đường đồng hiệu lực", [
    "Vẽ mọi cặp liều cho cùng một mức hiệu quả",
    "Đường thẳng là cộng tính theo Loewe",
    "Cong vào trong là hiệp đồng, cong ra ngoài là đối kháng",
], accent=BLUE, size=14.5)
box(s, ML, 4.00, CW, 0.95,
    "Ví dụ: để ức chế 50%, A cần 10 µM, B cần 20 µM",
    "hỗn hợp 2 µM A và 4 µM B đã đạt 50%, nên CI = 0,4: hiệp đồng rõ", fill=NAVY, ts=16, bs=13)
note(s, ML, 5.20, CW, "Cách này đòi đường cong liều–đáp ứng đầy đủ cho từng thuốc, nên không dùng được khi dữ liệu thưa")

s = content(prs, "Thiết kế thí nghiệm và nhiễu")
card(s, ML, 1.25, 4.03, 2.5, "Lưới liều", [
    "Mỗi cặp thuốc đo trên lưới 4 × 4 hoặc dày hơn",
    "Có cả hàng và cột đơn trị làm đối chứng",
], accent=NAVY, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.5, "Tỷ lệ cố định", [
    "Trộn hai thuốc theo một tỷ lệ rồi pha loãng dần",
    "Rẻ hơn lưới, nhưng chỉ nhìn được một lát cắt",
], accent=BLUE, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.5, "Kiểm soát chất lượng", [
    "Bản lặp sinh học và bản lặp kỹ thuật",
    "Z-factor đo mức tách giữa đối chứng dương và âm",
], accent=GREEN, size=14.5)
box(s, ML, 4.05, CW, 0.95,
    "Nhiễu giữa các bản lặp thường lớn hơn khoảng cách giữa hai bên ngưỡng ±10",
    "nên nhãn của bộ ba nằm sát ngưỡng gần như là ngẫu nhiên", fill=RED, ts=16, bs=13)
lines(s, ML, 5.30, CW, 1.3, [
    "Đây là lý do kỹ thuật để làm mềm nhãn quanh ngưỡng, thay vì tin tuyệt đối vào đường cắt",
], size=15)

s = content(prs, "Từ điểm số sang nhãn ba lớp")
table(s, [
    ["Điểm Loewe", "Nhãn", "Ý nghĩa"],
    ["lớn hơn +10", "syn", "hiệp đồng"],
    ["từ −10 đến +10", "add", "cộng tính, vùng trung tính"],
    ["nhỏ hơn −10", "ant", "đối kháng"],
], ML, 1.30, 6.1, [2.2, 1.3, 2.6], size=14.5, head_size=13.5, rowh=0.52)
card(s, 6.86, 1.30, 6.1, 2.1, "Hệ quả", [
    "Ngưỡng ±10 là quy ước, không phải sinh học",
    "Lớp cộng tính chiếm đa số",
    "Ba lớp có thứ tự: ant < add < syn",
], accent=NAVY, size=14.5)
box(s, ML, 3.70, CW, 0.9,
    "Nhiều bài báo vứt hẳn vùng trung tính rồi mới huấn luyện",
    "DTSyn mất 42,6% dữ liệu: từ 23.052 bộ ba còn 13.243", fill=AMBER, ts=17, bs=14)
lines(s, ML, 4.95, CW, 1.6, [
    "Bài toán còn lại dễ hơn hẳn bài toán thật",
    "Không bài nào đo xem việc này thổi kết quả lên bao nhiêu",
], size=15, after=12)

s = content(prs, "Vì sao ít tổ hợp vào được lâm sàng")
card(s, ML, 1.25, 4.03, 2.5, "Độc tính cộng lại", [
    "Hai thuốc cùng đánh vào tủy xương thì bệnh nhân không chịu nổi",
    "Phải giảm liều, và hiệp đồng biến mất",
], accent=RED, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.5, "Không đạt nồng độ", [
    "Nồng độ hiệp đồng trong đĩa nuôi cấy không đạt được trong máu",
    "Hoặc hai thuốc không cùng có mặt một lúc",
], accent=AMBER, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.5, "Dòng tế bào khác bệnh nhân", [
    "Khối u thật không đồng nhất",
    "Có mô đệm, miễn dịch, mạch máu",
], accent=BLUE, size=14.5)
box(s, ML, 4.05, CW, 0.95,
    "Lớp đối kháng cũng có giá trị lâm sàng: biết cặp nào làm giảm hiệu quả thì tránh kê cùng nhau",
    fill=NAVY, ts=16)
lines(s, ML, 5.25, CW, 1.4, [
    "Dự đoán hiệp đồng là bước sàng lọc để chọn cặp đáng đem đi thí nghiệm tiếp",
    "Hướng ứng dụng gần nhất là tái định vị thuốc: tìm công dụng mới cho thuốc đã được duyệt",
], size=15, after=10)

# ===================== PHAN 5: DU LIEU VA HOC MAY =====================
divider(prs, "PHẦN 5", "Dữ liệu và học máy", "Bộ dữ liệu, cách chia, chỉ số, và các mô hình đã có")

s = content(prs, "Dữ liệu đáp ứng thuốc đơn")
table(s, [
    ["Nguồn", "Nội dung", "Đặc điểm"],
    ["GDSC", "hàng trăm thuốc trên khoảng 1.000 dòng tế bào", "có IC50 và đường cong đầy đủ"],
    ["CTRP", "hợp chất nhỏ trên dòng tế bào CCLE", "chú trọng cơ chế tác động"],
    ["PRISM", "sàng lọc hàng nghìn thuốc bằng mã vạch", "rẻ, phủ rộng, nhiễu hơn"],
    ["CCLE, DepMap", "biểu hiện, đột biến, phụ thuộc gen", "nền chung để ghép mọi nguồn trên"],
], ML, 1.30, CW, [2.4, 5.4, 4.79], size=13.5, head_size=13, rowh=0.54)
card(s, ML, 4.45, 6.1, 1.7, "Hai cách tóm tắt đáp ứng", [
    "IC50: liều ức chế một nửa",
    "AUC của đường cong: tính cả vùng liều thấp",
], accent=NAVY, size=14.5)
card(s, 6.86, 4.45, 6.1, 1.7, "Vì sao cần dữ liệu đơn trị", [
    "Không có đơn trị thì không tính được mức mong đợi",
    "Nên không định nghĩa được hiệp đồng",
], accent=BLUE, size=14.5)

s = content(prs, "LINCS L1000 và Connectivity Map")
card(s, ML, 1.25, 6.1, 2.4, "Chữ ký biểu hiện", [
    "Cho tế bào tiếp xúc một thuốc rồi đo lại 978 gen",
    "Kết quả là một chữ ký: gen nào lên, gen nào xuống",
    "Hơn một triệu chữ ký đã công khai",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.4, "Connectivity Map dùng để làm gì", [
    "So chữ ký của thuốc với chữ ký của bệnh",
    "Thuốc đảo ngược được chữ ký bệnh là ứng viên",
    "Cơ sở cho tái định vị thuốc",
], accent=BLUE, size=14.5)
box(s, ML, 4.00, CW, 0.95,
    "Trong dự đoán hiệp đồng, chữ ký L1000 là một khung nhìn thứ ba về thuốc",
    "bên cạnh cấu trúc hóa học và danh sách đích", fill=NAVY, ts=16, bs=13)
note(s, ML, 5.20, CW, "Luận văn này chỉ mượn danh sách 978 gen landmark của L1000, không dùng chữ ký đáp ứng")

s = content(prs, "Bộ dữ liệu tổ hợp thuốc")
table(s, [
    ["Nguồn", "Quy mô", "Vai trò"],
    ["O'Neil (Merck, 2016)", "23.000 bộ ba · 38 thuốc · 39 dòng", "bộ chuẩn để so sánh mô hình"],
    ["NCI-ALMANAC", "hơn 300.000 bộ ba · 104 thuốc", "kiểm chứng ngoài"],
    ["DrugComb v1.4", "466.033 khối tổ hợp", "gom nhiều nghiên cứu, đủ bốn điểm"],
    ["AstraZeneca–DREAM", "11.576 thí nghiệm", "thi đấu có che nhãn"],
], ML, 1.30, CW, [3.3, 4.6, 4.69], size=14, head_size=13.5, rowh=0.56)
box(s, ML, 4.55, CW, 0.9,
    "Trên 1.163 thí nghiệm mà O'Neil và ALMANAC cùng đo",
    "hai nghiên cứu chỉ đồng thuận ở mức QWK khoảng 0,15", fill=RED, ts=17, bs=14)
lines(s, ML, 5.80, CW, 0.9, [
    "Đó là trần thực tế của mọi phép kiểm chứng chéo giữa hai bộ dữ liệu",
], size=15)

s = content(prs, "Khung bài toán học máy")
box(s, ML, 1.35, 3.7, 1.0, "Đầu vào", "thuốc A, thuốc B, dòng tế bào", fill=NAVY, ts=16, bs=13)
arrow(s, 4.15, 1.85, 4.55, 1.85)
box(s, 4.60, 1.35, 3.7, 1.0, "Mô hình", "hàm có tham số học được", fill=BLUE, ts=16, bs=13)
arrow(s, 8.40, 1.85, 8.80, 1.85)
box(s, 8.85, 1.35, 4.11, 1.0, "Đầu ra", "ant / add / syn", fill=RED, ts=16, bs=13)
lines(s, ML, 2.75, 6.1, 2.4, [
    "Lớp cộng tính chiếm đa số, nên phải cân lại trọng số lớp",
    "Chọn siêu tham số theo validation, test chỉ dùng một lần",
    "Mỗi cấu hình chạy nhiều fold và nhiều seed",
], size=15, after=14)
card(s, 6.86, 2.75, 6.1, 2.4, "Hai điều kiện để bảng so sánh có giá trị", [
    "Mọi mô hình cùng ngân sách huấn luyện",
    "Mọi mô hình cùng ngân sách dò siêu tham số",
], accent=GREEN, size=14.5)
box(s, ML, 5.45, CW, 0.85,
    "Baseline phải tái lập được số đã công bố, nếu không thì cả bảng mất giá trị",
    fill=NAVY, ts=17)

s = content(prs, "Chia dữ liệu: nơi hiệu năng bị thổi phồng")
labels = [("random", "chia ngẫu nhiên", RED), ("leave-combo", "cặp thuốc mới", NAVY),
          ("leave-drug", "thuốc mới", BLUE), ("leave-cell", "dòng tế bào mới", GREEN),
          ("leave-tumor", "loại mô mới", SLATE)]
w = 2.43
for i, (a, b, c) in enumerate(labels):
    x = ML + i * (w + 0.11)
    box(s, x, 1.30, w, 1.5, a, b, fill=c, ts=15, bs=13)
lines(s, ML, 3.15, CW, 1.8, [
    "Chia ngẫu nhiên để cùng một cặp thuốc nằm ở cả train và test",
    "Mô hình chỉ cần nhớ cặp đó là đoán đúng, mà không hiểu gì",
    "Leave-drug mới là tình huống dùng thật: một thuốc chưa từng gặp",
], size=15, after=14)
box(s, ML, 5.10, CW, 1.1,
    "Trên split ngẫu nhiên, mô hình chỉ biết tên đạt ROC-AUC 0,9566",
    "ngang với DeepSynergy 0,9581 — split này không phân biệt được mô hình",
    fill=AMBER, ts=17, bs=14)

s = content(prs, "Chỉ số đánh giá")
table(s, [
    ["Chỉ số", "Bẫy cần biết"],
    ["Accuracy", "vô dụng khi lệch lớp: đoán lớp đông nhất đã được 80%"],
    ["Macro-F1", "lộ ngay mô hình lười, vì tính đều cho cả ba lớp"],
    ["ROC-AUC", "so được giữa các bài, nhưng lạc quan khi lớp dương hiếm"],
    ["AUPRC", "không so trực tiếp được giữa hai bài khác tỷ lệ dương"],
    ["QWK", "tôn trọng thứ tự: nhầm syn thành ant bị phạt gấp bốn"],
    ["Polar error", "tỷ lệ nhầm syn với ant, lỗi nguy hiểm nhất về lâm sàng"],
], ML, 1.30, CW, [2.8, 9.79], size=14.5, head_size=13.5, rowh=0.62)
note(s, ML, 5.90, CW,
     "Quy tắc: chọn một chỉ số chính trước khi chạy, dùng nó cho early stopping và cho mọi so sánh")

s = content(prs, "Các mô hình đã công bố")
table(s, [
    ["Mô hình", "Ý tưởng chính", "Số công bố"],
    ["DeepSynergy (2018)", "MLP trên fingerprint và biểu hiện gen", "ROC-AUC ≈ 0,90"],
    ["DeepDDS (2022)", "GCN trên đồ thị phân tử, kèm attention", "ROC-AUC ≈ 0,93"],
    ["DTSyn (2022)", "hai transformer, token nguyên tử và token gen", "ROC-AUC 0,89"],
    ["AttenSyn, MD-Syn", "attention trên thuốc và trên bối cảnh tế bào", "≈ 0,90"],
    ["XGBoost", "fingerprint và biểu hiện, không học sâu", "khó vượt ở split khó"],
], ML, 1.30, CW, [3.0, 6.6, 2.99], size=14, head_size=13.5, rowh=0.54)
box(s, ML, 5.05, CW, 1.0,
    "Điểm chung: dùng nhãn nhị phân, thường bỏ vùng trung tính,",
    "và trình bày attention như lời giải thích mà không kiểm định", fill=NAVY, ts=17, bs=14)

# ===================== PHAN 6: GIAI THICH =====================
divider(prs, "PHẦN 6", "Giải thích mô hình", "Attribution, đối chứng thống kê, và các tiêu chí dễ nhầm")

s = content(prs, "Giải thích mô hình là gì")
card(s, ML, 1.25, 6.1, 2.3, "Attribution", [
    "Chia điểm công lao cho từng thành phần đầu vào",
    "Ở đây là gen, nguyên tử, mảnh cấu trúc, hoặc cạnh mạng",
], accent=NAVY, size=15)
card(s, 6.86, 1.25, 6.1, 2.3, "Hai tiêu chí hay bị nhầm", [
    "Trung thực: có phản ánh đúng mô hình không",
    "Đúng sinh học: có khớp tri thức đã biết không",
], accent=BLUE, size=15)
card(s, ML, 3.85, 6.1, 2.3, "Phương pháp hay dùng", [
    "Integrated Gradients: có tính chất completeness",
    "GNNExplainer: học mặt nạ cho từng mẫu",
    "Attention: sẵn có, nhưng không phải attribution",
], accent=GREEN, size=15)
card(s, 6.86, 3.85, 6.1, 2.3, "Điều phải nhớ", [
    "Mô hình chỉ nhớ tên thì lời giải thích trung thực của nó vẫn sai sinh học",
    "Kiểm tra mô hình trước, rồi mới trách phương pháp giải thích",
], accent=RED, size=15)

s = content(prs, "Thống kê và đối chứng null")
card(s, ML, 1.25, 6.1, 2.3, "Null là gì", [
    "Giá trị mà chỉ số sẽ có nếu không có gì đặc biệt",
    "Tung đồng xu 10 lần ra 6 ngửa: con số 6 đứng một mình không nói gì",
], accent=NAVY, size=14.5)
card(s, 6.86, 1.25, 6.1, 2.3, "Cách dựng null", [
    "Hoán vị nhãn, xáo mạng giữ bậc, chọn ngẫu nhiên cùng số đơn vị",
    "Null phải đi qua đúng đường ống như kết quả thật",
], accent=BLUE, size=14.5)
box(s, ML, 3.85, CW, 0.95,
    "Mọi chỉ số đều báo dưới dạng: giá trị thật, giá trị null, và hiệu giữa hai cái",
    fill=NAVY, ts=17)
lines(s, ML, 5.10, CW, 1.5, [
    "Thử nhiều giả thuyết thì phải hiệu chỉnh đa kiểm định bằng FDR",
    "Báo khoảng tin cậy qua nhiều seed và nhiều fold, không báo một con số lẻ",
], size=15, after=10)

s = content(prs, "Đo chất lượng một lời giải thích")
table(s, [
    ["Câu hỏi", "Chỉ số", "Null để so"],
    ["Có phản ánh mô hình không", "Fid+ và Fid−", "xóa ngẫu nhiên cùng số đơn vị"],
    ["Có ổn định giữa các lần chạy", "Jaccard@k qua seed và fold", "ghép hai bộ ba khác nhau"],
    ["Có ổn định khi đổi quy ước", "Jaccard@k qua điểm và ngưỡng", "như trên"],
    ["Có khớp sinh học không", "làm giàu pathway, case study", "tập gen ngẫu nhiên cùng cỡ"],
], ML, 1.30, CW, [3.6, 4.6, 4.39], size=14, head_size=13.5, rowh=0.56)
box(s, ML, 4.60, CW, 1.0,
    "Trung thực, ổn định và đúng sinh học là ba tính chất riêng biệt",
    "đạt được cái này không kéo theo cái kia", fill=NAVY, ts=17, bs=14)
note(s, ML, 5.90, CW, "Case study phải được chọn trước khi chạy, nếu không thì chỉ là tìm ví dụ hợp ý sau khi đã thấy kết quả")

s = content(prs, "Lĩnh vực đang yếu ở đâu")
W, H = 4.03, 2.15
X = [ML, 4.65, 8.93]
Y = [1.25, 3.70]
weak = [
    ("Quy ước nhãn", ["Bốn điểm chỉ tương quan lỏng lẻo", "Ngưỡng là thói quen"], AMBER),
    ("Vùng trung tính", ["Bị xóa để dữ liệu dễ hơn", "Chưa ai đo cái giá"], RED),
    ("Nhớ danh tính", ["38 thuốc là quá ít", "One-hot gần bằng học sâu"], NAVY),
    ("Split quá dễ", ["Số đẹp lấy từ split ngẫu nhiên", "Leave-drug mới là thật"], BLUE),
    ("Attention", ["Được coi là lời giải thích", "Không ai kiểm định"], SLATE),
    ("Thiếu đối chứng", ["Không có null để so", "Ba tiêu chí bị gộp làm một"], GREEN),
]
for i, (h, its, c) in enumerate(weak):
    card(s, X[i % 3], Y[i // 3], W, H, h, its, accent=c, size=14, after=10)

save(prs, "01_kien_thuc_nen.pptx")
