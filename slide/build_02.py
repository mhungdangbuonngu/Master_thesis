# -*- coding: utf-8 -*-
"""Deck 2: tong quan du an SynGT. It chu, noi y chinh."""
from deck import (new_deck, cover, content, divider, card, box, table, lines,
                  arrow, note, save,
                  NAVY, RED, BLUE, GREEN, AMBER, SLATE, ML, CW)

prs = new_deck()

# 1. Bia
cover(prs,
      "SynGT: dự đoán hiệp đồng thuốc ba lớp và giải thích mô hình",
      "Graph neural network kết hợp transformer, đầu ra có thứ tự, giải thích ở cấp tương tác",
      ["Học viên: [Họ và tên] — [MSHV]",
       "Giảng viên hướng dẫn: [Tên giảng viên]",
       "Hà Nội, 2026"])

# 2. Mot trang
s = content(prs, "Dự án trong một trang")
W, H = 4.03, 2.3
X = [ML, 4.65, 8.93]
Y = [1.25, 3.85]
items = [
    ("Bài toán", ["Cặp thuốc trên một dòng tế bào", "Đối kháng / cộng tính / hiệp đồng", "Ba lớp có thứ tự"], NAVY),
    ("Dữ liệu", ["O'Neil: 18.870 bộ ba", "36 thuốc, 37 dòng tế bào", "ALMANAC để kiểm chứng ngoài"], AMBER),
    ("Mô hình", ["GIN trên đồ thị phân tử", "Hai transformer", "Đầu ra CORN có thứ tự"], GREEN),
    ("Giải thích", ["Integrated Gradients", "Nhắm vào phần dôi ra", "Mọi chỉ số có null"], SLATE),
    ("So sánh", ["DeepSynergy, DeepDDS, XGBoost", "One-hot và baseline tầm thường", "Ablation từng thành phần"], BLUE),
    ("Đầu ra", ["Một bài báo chuẩn format", "Luận văn sáu chương", "Mã nguồn tái lập được"], RED),
]
for i, (h, its, c) in enumerate(items):
    card(s, X[i % 3], Y[i // 3], W, H, h, its, accent=c, size=14, after=10)

# 3. Dong luc
s = content(prs, "Vì sao làm bài toán này")
card(s, ML, 1.25, 4.03, 2.5, "Vùng trung tính bị xóa", [
    "DTSyn bỏ bộ ba có điểm 0–10",
    "Mất 42,6% dữ liệu",
    "Chưa ai đo cái giá của việc này",
], accent=RED, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.5, "Giải thích sai câu hỏi", [
    "Các bài giải thích dự đoán tổng",
    "Hiệp đồng là phần dôi ra so với cộng tính",
    "Phải nhắm vào hiệu hai logit",
], accent=SLATE, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.5, "Attention chưa kiểm định", [
    "Ba bài coi attention là lời giải thích",
    "Không so với attribution thật",
    "Không có null, không đo ổn định",
], accent=AMBER, size=14.5)
box(s, ML, 4.05, CW, 0.9,
    "Phạm vi giữ hẹp có chủ ý: theo sát khung DTSyn, chỉ dùng O'Neil",
    "để con số đặt cạnh bài đã đăng được", fill=NAVY, ts=17, bs=14)
lines(s, ML, 5.25, CW, 1.3, [
    "Không đặt mục tiêu dẫn đầu bảng xếp hạng",
    "Đóng góp nằm ở cách đặt bài toán và ở phần giải thích",
], size=15, after=10)

# 4. Cau hoi
s = content(prs, "Sáu câu hỏi nghiên cứu")
table(s, [
    ["", "Câu hỏi", "Trả lời bằng cách nào"],
    ["RQ1", "Giữ lại vùng trung tính thì hiệu năng tụt bao nhiêu?", "chạy ba thiết lập nhãn trên cùng dữ liệu"],
    ["RQ2", "Đầu ra có thứ tự có giảm lỗi nhầm cực không?", "so CORN với cross-entropy, đo QWK và lỗi nhầm cực"],
    ["RQ3", "Giải thích cấp tương tác có khác cấp logit không?", "Jaccard giữa hai tập gen và hai tập mảnh"],
    ["RQ4", "Attention có trung thực không?", "Fid+ và Fid− có null, so với IG"],
    ["RQ5", "Giải thích có ổn định hay chỉ là ảnh của quy ước?", "lặp qua seed, fold, bốn điểm và ba ngưỡng"],
    ["RQ6", "Cơ chế đối kháng có khác hiệp đồng không?", "attribution phía đối kháng, so pathway"],
], ML, 1.30, CW, [0.9, 5.9, 5.79], size=13.5, head_size=13, rowh=0.62)
note(s, ML, 5.90, CW, "RQ1 và RQ4 giải thích một vấn đề nằm ngay trong bài đã đăng, nên kết quả theo chiều nào cũng đăng được")

# 5. Du lieu
s = content(prs, "Dữ liệu nào dùng cho phần nào")
table(s, [
    ["Nguồn", "Quy mô", "Dùng cho"],
    ["O'Neil qua DrugComb v1.4", "18.870 bộ ba · 36 thuốc · 37 dòng", "huấn luyện và đánh giá chính"],
    ["Điểm Loewe, ngưỡng ±10", "4.391 ant / 13.207 add / 1.272 syn", "nhãn ba lớp"],
    ["ZIP, Bliss, HSA · ngưỡng ±5, ±20", "4 điểm × 3 ngưỡng", "kiểm độ ổn định của giải thích"],
    ["DepMap, gen landmark L1000", "37 × 944 gen", "đặc trưng dòng tế bào"],
    ["STRING v12, score ≥ 700", "16.201 nút · 236.930 cạnh", "node2vec cho token gen"],
    ["NCI-ALMANAC", "234.333 bộ ba", "kiểm chứng ngoài, zero-shot"],
], ML, 1.30, CW, [3.6, 4.4, 4.59], size=13.5, head_size=13, rowh=0.56)
note(s, ML, 5.60, CW, "KEGG chỉ dùng để chấm plausibility, không bao giờ làm đầu vào của mô hình")

# 6. Nhan va split
s = content(prs, "Ba thiết lập nhãn và năm cách chia")
table(s, [
    ["Thiết lập nhãn", "Cách gán"],
    ["(a) nhị phân, bỏ vùng giữa", "đúng như DTSyn"],
    ["(b) nhị phân, giữ toàn bộ", "không vứt bộ ba nào"],
    ["(c) ba lớp có thứ tự", "ant / add / syn, đo bằng QWK"],
], ML, 1.30, 6.1, [3.2, 2.9], size=14, head_size=13.5, rowh=0.56)
box(s, ML, 3.70, 6.1, 0.95,
    "So (a) với (b) trên cùng mô hình, cùng fold, cùng seed",
    "cho ra đúng cái giá của việc xóa vùng trung tính", fill=NAVY, ts=15, bs=13)
splits = [("random", RED), ("leave_combo", NAVY), ("leave_drug", BLUE),
          ("leave_cell", GREEN), ("leave_tumor", SLATE)]
for i, (t, c) in enumerate(splits):
    box(s, 6.86, 1.30 + i * 0.7, 6.1, 0.58, t, fill=c, ts=15)
lines(s, ML, 4.95, CW, 1.6, [
    "Giao giữa tập cặp thuốc của train và test phải rỗng",
    "Z-score chỉ fit trên train của từng fold",
    "Mọi mô hình cùng ngân sách: 120 epoch, patience 20",
], size=14.5, after=8)

# ================= KIEN TRUC =================
divider(prs, "KIẾN TRÚC", "Mô hình SynGT", "Khoảng 4,16 triệu tham số, theo sát khung DTSyn")

s = content(prs, "Luồng dữ liệu của một bộ ba")
box(s, ML, 1.30, 3.0, 0.85, "Thuốc A, B", "đồ thị phân tử", fill=NAVY, ts=15, bs=12)
arrow(s, 3.42, 1.72, 3.78, 1.72)
box(s, 3.82, 1.30, 2.6, 0.85, "GIN 2 lớp", "token nguyên tử", fill=BLUE, ts=15, bs=12)
arrow(s, 6.47, 1.72, 6.83, 1.72)
box(s, 6.87, 1.30, 3.1, 0.85, "Transformer mịn", "nguyên tử gặp gen", fill=BLUE, ts=15, bs=12)
box(s, ML, 2.35, 3.0, 0.85, "Dòng tế bào", "944 gen landmark", fill=NAVY, ts=15, bs=12)
arrow(s, 3.42, 2.77, 3.78, 2.77)
box(s, 3.82, 2.35, 2.6, 0.85, "Token gen", "node2vec trên PPI", fill=BLUE, ts=15, bs=12)
arrow(s, 6.47, 2.77, 6.83, 2.77)
box(s, 6.87, 2.35, 3.1, 0.85, "Transformer thô", "thuốc gặp tế bào", fill=BLUE, ts=15, bs=12)
box(s, ML, 3.40, 9.6, 0.72, "Readout: hai token CLS, tổng và hiệu hai thuốc, vector tế bào, cộng nhánh fingerprint",
    fill=GREEN, ts=15)
arrow(s, 5.17, 4.14, 5.17, 4.42)
box(s, ML, 4.46, 9.6, 0.72, "Đầu CORN: hai logit có điều kiện, cho ra thứ tự ant < add < syn", fill=RED, ts=15)
card(s, 10.25, 1.30, 2.71, 3.88, "Tham số", [
    "GIN: 547 nghìn",
    "Fingerprint: 590 nghìn",
    "Tế bào: 681 nghìn",
    "Tổng: 4,16 triệu",
], accent=SLATE, size=13.5, after=8)
lines(s, ML, 5.45, CW, 1.2, [
    "Đổi chỗ A và B thì dự đoán không đổi, vì mô hình chỉ dùng tổng và hiệu tuyệt đối",
    "Hiệu hai logit chính là đầu ra có điều kiện thứ hai, nên giải thích cấp tương tác là chính xác",
], size=14.5, after=8)

# 9. Ordinal
s = content(prs, "Vì sao đầu ra có thứ tự")
card(s, ML, 1.25, 6.1, 2.4, "Đầu CORN thay softmax", [
    "Softmax coi ba nhãn là rời rạc",
    "Nhầm syn thành ant bị phạt bằng nhầm thành add",
    "CORN bảo đảm thứ tự ngay trong cấu trúc",
], accent=GREEN, size=15)
card(s, 6.86, 1.25, 6.1, 2.4, "Label smoothing tại ngưỡng", [
    "Điểm 10,3 và 9,7 bị gán hai nhãn khác nhau",
    "Nhiễu thí nghiệm còn lớn hơn khoảng cách đó",
    "Nên làm mềm nhãn quanh ngưỡng",
], accent=AMBER, size=15)
box(s, ML, 3.95, CW, 0.95,
    "Label smoothing thắng trên validation ở cả bốn kiểu chia",
    "nhưng đổi recall lớp hiệp đồng để lấy QWK — một đánh đổi phải viết rõ", fill=NAVY, ts=16, bs=13)
lines(s, ML, 5.20, CW, 1.3, [
    "Mọi lựa chọn đều quyết theo validation, không bao giờ theo test",
], size=15)

# 10. Nguon goc
s = content(prs, "Thành phần nào lấy từ đâu")
table(s, [
    ["Thành phần", "Nguồn"],
    ["Hai transformer, token nguyên tử và token gen, node2vec", "DTSyn — khung chính"],
    ["Đặc trưng nguyên tử 78 chiều, cách ghép readout", "DeepDDS"],
    ["Nhánh fingerprint Morgan", "DeepSynergy"],
    ["GIN thay GCN", "thay đổi của chúng tôi"],
    [("Đầu CORN ba lớp, đánh giá bằng QWK", {"bold": True}), ("mới trong lĩnh vực", {"bold": True, "color": RED})],
    [("Giải thích ở cấp tương tác, có kiểm định", {"bold": True}), ("mới trong lĩnh vực", {"bold": True, "color": RED})],
], ML, 1.30, CW, [7.6, 4.99], size=14, head_size=13.5, rowh=0.50)
box(s, ML, 5.15, CW, 0.95,
    "Không định vị bài báo là kiến trúc mới",
    "ablation cho thấy bỏ hai transformer cũng không làm kết quả giảm", fill=AMBER, ts=16, bs=13)

# 11. So sanh
s = content(prs, "So sánh với những gì")
card(s, ML, 1.25, 4.03, 2.3, "Baseline tầm thường", [
    "majority, chỉ tế bào, chỉ thuốc",
    "one-hot: chỉ biết tên",
], accent=NAVY, size=14.5)
card(s, 4.65, 1.25, 4.03, 2.3, "Bài đã công bố", [
    "DeepSynergy, DeepDDS",
    "XGBoost trên fingerprint",
], accent=BLUE, size=14.5)
card(s, 8.93, 1.25, 4.03, 2.3, "Ablation", [
    "GIN ↔ GCN, bỏ transformer, bỏ PPI",
    "CORN ↔ cross-entropy",
], accent=GREEN, size=14.5)
table(s, [
    ["Chặn G1: tái lập số công bố", "Của chúng tôi", "Số công bố"],
    ["DeepDDS", "0,9447", "khoảng 0,93"],
    ["DeepSynergy", "0,9581", "khoảng 0,90"],
    [("one-hot, chỉ biết tên", {"bold": True}), ("0,9566", {"bold": True}), ("split ngẫu nhiên không phân biệt được mô hình", {"color": RED})],
], ML, 3.95, CW, [4.2, 2.8, 5.59], size=14, head_size=13.5, rowh=0.56)

# 12. XAI
s = content(prs, "Phần giải thích mô hình")
card(s, ML, 1.25, 6.1, 2.3, "Giải thích cái gì", [
    "Gen, mảnh BRICS, nguyên tử",
    "Nhắm vào phần dôi ra so với cộng tính",
    "Có cả phía đối kháng",
], accent=NAVY, size=15)
card(s, 6.86, 1.25, 6.1, 2.3, "Đo bằng gì", [
    "Fid+ và Fid−: có phản ánh mô hình không",
    "Jaccard qua seed và qua quy ước: có ổn định không",
    "Pathway và case study: có nghĩa sinh học không",
], accent=GREEN, size=15)
box(s, ML, 3.85, CW, 0.95,
    "Mỗi chỉ số đi kèm một null, và null phải đi qua đúng đường ống như kết quả thật",
    fill=NAVY, ts=17)
note(s, ML, 5.10, CW, "Case study khai báo trước khi chạy: ETOPOSIDE + MK-2206 trên CAOV3 và NCIH23, đúng ví dụ duy nhất mà DTSyn đem ra giải thích")

# 13. Ky vong
s = content(prs, "Kết quả mong đợi")
table(s, [
    ["Câu hỏi", "Mức kỳ vọng", "Ý nghĩa nếu đúng"],
    ["RQ1", "ROC-AUC tụt 0,05–0,12", "số đã công bố đo trên tập dễ hơn thực tế"],
    ["RQ2", "lỗi nhầm cực giảm 20–40%", "đóng góp thực dụng của đầu ra có thứ tự"],
    ["RQ3", "Jaccard 0,2–0,5", "hai cấp giải thích trả lời hai câu khác nhau"],
    ["RQ4", "attention yếu hơn IG", "attention không phải lời giải thích"],
    ["RQ5", "Jaccard 0,1–0,4 khi đổi điểm", "cơ chế công bố phần lớn là ảnh của quy ước"],
    ["RQ6", "pathway khác nhau", "lớp đối kháng mang cơ chế riêng"],
], ML, 1.30, CW, [1.4, 4.2, 6.99], size=14, head_size=13.5, rowh=0.6)
box(s, ML, 5.10, CW, 0.95,
    "Đầu ra: một bài báo chuẩn format và luận văn sáu chương",
    "kết quả theo chiều nào cũng viết ra, kể cả khi bất lợi cho mô hình của mình", fill=NAVY, ts=16, bs=13)

# 14. Da chay toi dau
s = content(prs, "Đã chạy tới đâu")
table(s, [
    ["Mô hình", "leave_combo", "leave_drug", "leave_cell"],
    [("SynGT + label smoothing", {"bold": True}), ("0,627", {"bold": True}), "0,214", "0,489"],
    ["DeepSynergy", "0,605", "0,051", "0,456"],
    ["one-hot", "0,573", "0,190", "0,478"],
    ["XGBoost", "0,546", "0,194", ("0,504", {"bold": True})],
    ["DeepDDS", "0,536", "0,191", "0,483"],
], ML, 1.30, 6.1, [2.5, 1.3, 1.2, 1.1], size=13.5, head_size=12.5, rowh=0.46)
card(s, 6.86, 1.30, 6.1, 2.9, "Bốn điều đáng nói", [
    "RQ1 vững: giữ vùng trung tính làm AUROC giảm 0,05",
    "SynGT không đứng đầu mọi cột",
    "Transformer và PPI không đóng góp",
    "DeepSynergy sụp khi gặp thuốc mới",
], accent=BLUE, size=14)
box(s, ML, 4.40, CW, 1.0,
    "Giải thích trung thực với mô hình và ổn định giữa các seed",
    "nhưng chưa có ý nghĩa sinh học: không enrichment, 0 trên 8 case study vượt null",
    fill=AMBER, ts=16, bs=13)
note(s, ML, 5.65, CW, "Zero-shot trên ALMANAC chỉ đạt QWK 0,023, nhưng trần của phép thử đó cũng chỉ là 0,149")

# 15. Gioi han
s = content(prs, "Giới hạn và cách định vị")
card(s, ML, 1.25, 6.1, 2.6, "Giới hạn đã biết", [
    "O'Neil quá nhỏ nên danh tính chi phối",
    "ALMANAC không trả lời được câu hỏi tổng quát hóa",
    "DTSyn chưa được tái lập riêng",
], accent=RED, size=15)
card(s, 6.86, 1.25, 6.1, 2.6, "Ba trục đứng được", [
    "Giao thức bỏ vùng trung tính thổi kết quả lên",
    "Ba lớp có thứ tự cho phép hỏi về đối kháng",
    "Trung thực không đồng nghĩa có nghĩa sinh học",
], accent=GREEN, size=15)
lines(s, ML, 4.15, CW, 1.8, [
    "Viết bài theo hướng phản biện giao thức, không viết là dẫn đầu bảng xếp hạng",
    "Tái lập DTSyn như một mô hình độc lập",
    "Kiểm chứng giả thuyết nhớ danh tính bằng một thí nghiệm riêng",
], size=15, after=12)
box(s, ML, 5.90, CW, 0.7,
    "828 run huấn luyện · 54 run giải thích · 20 test đơn vị đều qua", fill=NAVY, ts=16)

save(prs, "02_tong_quan_du_an.pptx")
