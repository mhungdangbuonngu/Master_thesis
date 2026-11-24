// Dung lai de_cuong_de_xuat_1.pptx theo planner_de_xuat_2.md
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("C:/Users/hung/.claude/skills/synced/effdbcd2-bb45-40b7-bc24-4e93d3730cd1_165f13a5-ead1-4f78-b896-cd2077ad7dad/pptx/scripts/apply_theme.js");

const THEME = {
  name: "Ocean Gradient",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "21295C", lt1: "FFFFFF", dk2: "065A82", lt2: "EEF3F7",
    accent1: "1C7293", accent2: "065A82", accent3: "D79B00", accent4: "B85450",
    accent5: "5B8C5A", accent6: "7B5EA7", hlink: "1C7293", folFlink: "7B5EA7",
    folHlink: "7B5EA7",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Luan van thac si";
pres.company = "Dai hoc Bach khoa Ha Noi";
pres.title = "De cuong luan van — XAI duong dan tren mang PPI";
const C = pres.SchemeColor;

const W = 13.3, H = 7.5;
const FOOT = "Đường dẫn giải thích trên PPI: có phụ thuộc mạng thật và đặc hiệu theo cặp không?";

pres.defineSlideMaster({
  title: "DARK_TITLE",
  background: { color: C.text1 },
  objects: [
    { rect: { x: 0, y: 2.55, w: 0.14, h: 1.7, fill: { color: C.accent3 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.75, y: 2.5, w: 10.9, h: 1.8, fontSize: 34, bold: true, color: C.background1, valign: "middle" }, text: " " } },
    { placeholder: { options: { name: "body", type: "body", x: 0.78, y: 4.5, w: 10.9, h: 1.7, fontSize: 14, color: C.accent1, valign: "top" }, text: " " } },
  ],
});

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { rect: { x: 0, y: 0, w: W, h: 0.09, fill: { color: C.accent1 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.52, y: 0.3, w: 12.3, h: 0.72, fontSize: 24, bold: true, color: C.text1, valign: "middle", align: "left" }, text: " " } },
    { placeholder: { options: { name: "body", type: "body", x: 0.52, y: 1.18, w: 12.3, h: 5.6, fontSize: 14, color: C.text1, valign: "top" }, text: " " } },
    { text: { text: FOOT, options: { x: 0.52, y: 6.95, w: 10.6, h: 0.32, fontSize: 9, color: C.accent1, italic: true, isTextBox: true, margin: 0 } } },
    { rect: { x: 0.52, y: 6.9, w: 12.3, h: 0.015, fill: { color: C.background2 } } },
    { slideNumber: { x: 12.4, y: 6.95, w: 0.42, h: 0.32, fontSize: 10, color: C.accent1, align: "right" } },
  ],
});

pres.defineSlideMaster({
  title: "DARK_END",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 2.3, w: 11.5, h: 1.1, fontSize: 30, bold: true, color: C.background1, valign: "middle" }, text: " " } },
    { placeholder: { options: { name: "body", type: "body", x: 0.93, y: 3.5, w: 11.5, h: 2.2, fontSize: 15, color: C.accent1, valign: "top" }, text: " " } },
  ],
});

// ---------- helpers ----------
let N = 0;
const oid = (p) => `${p}-${++N}`;

function S(masterName, sectionTitle, title) {
  const s = pres.addSlide({ masterName, sectionTitle });
  if (title) s.addText(title, { placeholder: "title" });
  return s;
}

function bullets(slide, items, opt = {}) {
  const runs = items.map((it, i) => {
    const t = typeof it === "string" ? it : it.t;
    const o = {
      bullet: typeof it === "string" ? true : (it.b !== false),
      breakLine: i < items.length - 1,
      paraSpaceAfter: opt.gap ?? 9,
      fontSize: opt.fontSize ?? 14,
      bold: typeof it === "object" && it.bold ? true : false,
      color: typeof it === "object" && it.color ? it.color : C.text1,
      indentLevel: typeof it === "object" && it.lvl ? it.lvl : 0,
    };
    return { text: t, options: o };
  });
  if (opt.x !== undefined) {
    slide.addText(runs, { x: opt.x, y: opt.y, w: opt.w, h: opt.h, isTextBox: true, margin: 0, valign: "top", objectName: oid("list") });
  } else {
    slide.addText(runs, { placeholder: "body" });
  }
}

// khoi chu nhat cho so do
function box(slide, x, y, w, h, title, body, kind = "data", opt = {}) {
  const K = {
    data: { fill: C.accent1, line: C.accent1, tc: C.background1, bc: C.background1 },
    compute: { fill: C.accent5, line: C.accent5, tc: C.background1, bc: C.background1 },
    note: { fill: "FDF4DC", line: C.accent3, tc: C.text1, bc: C.text1 },
    out: { fill: C.accent4, line: C.accent4, tc: C.background1, bc: C.background1 },
    src: { fill: C.accent6, line: C.accent6, tc: C.background1, bc: C.background1 },
    pale: { fill: C.background2, line: C.accent1, tc: C.text1, bc: C.text1 },
    null_: { fill: "FFF0E0", line: C.accent3, tc: C.text1, bc: C.text1 },
  }[kind];
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: K.fill }, line: { color: K.line, width: 1.2 },
    objectName: opt.name || oid("box"),
  });
  const runs = [];
  if (title) runs.push({ text: title, options: { bold: true, fontSize: opt.ts ?? 11, color: K.tc, breakLine: !!body } });
  if (body) runs.push({ text: body, options: { fontSize: opt.bs ?? 9.5, color: K.bc } });
  slide.addText(runs, { x, y, w, h, isTextBox: true, align: "center", valign: "middle", margin: 2, objectName: oid("boxt") });
}

function arrow(slide, x1, y1, x2, y2, color) {
  slide.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    line: { color: color || C.accent2, width: 1.5, endArrowType: "triangle",
      beginArrowType: "none" },
    flipH: x2 < x1, flipV: y2 < y1,
    objectName: oid("arw"),
  });
}

function caption(slide, x, y, w, t, opt = {}) {
  slide.addText(t, { x, y, w, h: opt.h ?? 0.3, isTextBox: true, margin: 0,
    fontSize: opt.fontSize ?? 10, italic: opt.italic !== false, color: opt.color || C.accent2,
    align: opt.align || "left", valign: "top", objectName: oid("cap") });
}

function stat(slide, x, y, w, big, lab, color) {
  slide.addText(big, { x, y, w, h: 0.95, isTextBox: true, margin: 0, fontSize: 44, bold: true,
    color: color || C.accent1, align: "center", valign: "middle", objectName: oid("stat") });
  slide.addText(lab, { x, y: y + 0.95, w, h: 0.9, isTextBox: true, margin: 0, fontSize: 11,
    color: C.text1, align: "center", valign: "top", objectName: oid("statl") });
}

function table(slide, rows, opt) {
  slide.addTable(rows, {
    x: opt.x, y: opt.y, w: opt.w, colW: opt.colW,
    fontSize: opt.fontSize ?? 11, color: C.text1, fontFace: THEME.bodyFontFace,
    border: { type: "solid", color: C.background2, pt: 1 },
    fill: { color: C.background1 }, valign: "middle",
    rowH: opt.rowH, margin: opt.margin ?? 5,
    objectName: oid("tbl"),
  });
}
const TH = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, fontSize: 11 } });

// ================= SLIDES =================

pres.addSection({ title: "Mở đầu" });

// 1 — title
{
  const s = S("DARK_TITLE", "Mở đầu", "Đường dẫn giải thích trên mạng PPI có phụ thuộc mạng thật và có đặc hiệu theo cặp không?");
  s.addText([
    { text: "Đề cương luận văn thạc sĩ  ·  bản rút gọn (đề xuất 2)", options: { fontSize: 15, color: "FFFFFF", breakLine: true, paraSpaceAfter: 10 } },
    { text: "Học viên: [Họ và tên]        Giảng viên hướng dẫn: [Tên giảng viên]", options: { fontSize: 13, color: THEME.colors.accent1, breakLine: true } },
    { text: "Hà Nội, 2026", options: { fontSize: 12, color: THEME.colors.accent1 } },
  ], { placeholder: "body" });
  s.addNotes("Luan van khong lam mo hinh du doan gioi hon. No kiem dinh xem loi giai thich duong dan co dang tin khong.");
}

// 2 — noi dung
{
  const s = S("CONTENT", "Mở đầu", "Nội dung");
  const items = [
    ["1", "Bài toán và khoảng trống", "Hiệp đồng thuốc, và vì sao các \"đường dẫn cơ chế\" đã công bố chưa được kiểm chứng"],
    ["2", "Hai câu hỏi nghiên cứu", "RQ1 topo, RQ2 danh tính, cùng một điều kiện tiên quyết"],
    ["3", "Dữ liệu", "O'Neil, DepMap, đích thuốc, STRING — tất cả đã công bố"],
    ["4", "Khung thí nghiệm", "SynergyGNN, edge-IG ba cấp, và cách ra đường dẫn"],
    ["5", "Null cho mọi chỉ số", "Phần mới, và là phần quan trọng nhất"],
    ["6", "Lộ trình 12 tháng", "Ba mốc ra quyết định, hai kết cục đều đăng được"],
  ];
  items.forEach(([n, t, d], i) => {
    const y = 1.35 + i * 0.88;
    s.addShape(pres.shapes.OVAL, { x: 0.62, y: y + 0.06, w: 0.52, h: 0.52, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: oid("num") });
    s.addText(n, { x: 0.62, y: y + 0.06, w: 0.52, h: 0.52, isTextBox: true, margin: 0, fontSize: 15, bold: true, color: C.background1, align: "center", valign: "middle", objectName: oid("numt") });
    s.addText([
      { text: t, options: { bold: true, fontSize: 15, color: C.text1, breakLine: true } },
      { text: d, options: { fontSize: 11.5, color: C.accent2 } },
    ], { x: 1.35, y, w: 11.3, h: 0.72, isTextBox: true, margin: 0, valign: "middle", objectName: oid("secl") });
  });
}

pres.addSection({ title: "1. Bài toán" });

// 3 — bai toan
{
  const s = S("CONTENT", "1. Bài toán", "Bài toán: dự đoán và giải thích hiệp đồng thuốc");
  box(s, 0.62, 1.4, 3.3, 1.0, "Một mẫu", "bộ ba (thuốc A, thuốc B, cell line c)", "src", { ts: 13, bs: 11 });
  arrow(s, 3.92, 1.9, 4.5, 1.9);
  box(s, 4.5, 1.4, 3.1, 1.0, "Điểm Loewe", "đo mức hiệp đồng thực nghiệm", "compute", { ts: 13, bs: 11 });
  arrow(s, 7.6, 1.9, 8.18, 1.9);
  box(s, 8.18, 1.4, 4.5, 1.0, "Nhãn 3 lớp", "syn > 10   ·   add −10…10   ·   ant < −10", "out", { ts: 13, bs: 11 });

  caption(s, 0.62, 2.55, 12.0, "Phần dự đoán là việc đã có 16 mô hình làm. Phần luận văn quan tâm là bước sau đó:");
  box(s, 0.62, 2.95, 12.06, 0.85, "Mô hình nói \"syn\" rồi in ra một đường dẫn trên mạng protein và gọi đó là cơ chế", "A ức chế EGFR → tín hiệu qua MAPK1 → gặp nhánh của B ở ERK", "pale", { ts: 13, bs: 11 });

  bullets(s, [
    { t: "Khoảng 25 bài trong tổng quan in ra những đường như vậy.", bold: true },
    "Không bài nào kiểm tra xem đường đó có thật sự đến từ mạng sinh học hay không.",
    "Cũng không bài nào kiểm tra đường đó thuộc về cặp (A, B) hay chỉ thuộc về riêng từng thuốc.",
  ], { x: 0.62, y: 4.1, w: 12.06, h: 1.4, fontSize: 14 });

  box(s, 0.62, 5.55, 12.06, 1.05, "Luận văn không cố làm mô hình dự đoán giỏi hơn", "Luận văn hỏi: lời giải thích đó có đáng tin không, và kiểm định bằng một giao thức có hiệu chỉnh null", "data", { ts: 14, bs: 12 });
  s.addNotes("Nhan mot lan: day la luan van ve XAI, khong phai ve hieu nang du doan.");
}

// 4 — mang co giup khong
{
  const s = S("CONTENT", "1. Bài toán", "Hai bài 2025–2026 đã làm lung lay nền móng");
  s.addText([{ text: "SynVerse", options: { bold: true, fontSize: 16, color: C.accent2, breakLine: true } },
    { text: "Tasnina, Haghani, Murali · Brief Bioinform 2025", options: { fontSize: 10.5, italic: true, color: C.accent1 } }],
    { x: 0.62, y: 1.3, w: 5.9, h: 0.72, isTextBox: true, margin: 0, objectName: oid("h") });
  s.addText([{ text: "One-hot news", options: { bold: true, fontSize: 16, color: C.accent2, breakLine: true } },
    { text: "Çandır et al. · Bioinformatics 2026", options: { fontSize: 10.5, italic: true, color: C.accent1 } }],
    { x: 6.78, y: 1.3, w: 5.9, h: 0.72, isTextBox: true, margin: 0, objectName: oid("h") });

  s.addShape(pres.shapes.LINE, { x: 6.68, y: 1.3, w: 0, h: 4.6, line: { color: C.background2, width: 1 }, objectName: oid("div") });

  stat(s, 0.62, 2.15, 2.8, "16", "mô hình hiệp đồng chạy lại trên mạng PPI đã xáo giữ bậc");
  stat(s, 3.62, 2.15, 2.8, "≈ 0", "mức PCC bị giảm. Xáo mạng gần như không ảnh hưởng");
  stat(s, 6.78, 2.15, 2.8, "0,2–0,4", "Jaccard giữa attribution và đặc trưng thật", THEME.colors.accent4);
  stat(s, 9.88, 2.15, 2.8, "one-hot", "MLP chỉ nhận mã thuốc đứng ngang cả 16 kiến trúc", THEME.colors.accent4);

  box(s, 0.62, 4.35, 5.9, 1.45, "Mạng có thể không đóng góp gì cho dự đoán", "Nếu mô hình không dùng mạng thì mọi đường dẫn đọc ra từ nó đều vô nghĩa", "pale", { ts: 12, bs: 11 });
  box(s, 6.78, 4.35, 5.9, 1.45, "Attribution có thể chỉ đang nhớ danh tính", "Khi bộ ba (A, B, cell) lặp lại, mô hình học thuộc mã thuốc chứ không học cơ chế", "pale", { ts: 12, bs: 11 });

  caption(s, 0.62, 6.0, 12.06, "Cả hai bài đều đo hiệu năng dự đoán và attribution trên đặc trưng. Chưa bài nào làm điều tương tự cho đường dẫn trên mạng.", { fontSize: 12, color: THEME.colors.accent4, italic: false });
}

// 5 — khoang trong
{
  const s = S("CONTENT", "1. Bài toán", "Khoảng trống: chưa ai kiểm định đường dẫn");
  const rows = [
    [TH("Đã có ai làm"), TH("Ở mức đặc trưng"), TH("Ở mức đường dẫn trên mạng")],
    ["Mô hình có thật sự dùng tín hiệu đó không?", "SynVerse 2025 — có", { text: "chưa ai", options: { bold: true, color: THEME.colors.accent4 } }],
    ["Giải thích có trung thực với mô hình không?", "One-hot news 2026 — có", { text: "chưa ai", options: { bold: true, color: THEME.colors.accent4 } }],
    ["Giải thích có đặc hiệu theo cặp không?", "chưa ai", { text: "chưa ai", options: { bold: true, color: THEME.colors.accent4 } }],
    ["Có mốc ngẫu nhiên để so không?", "một phần", { text: "chưa ai", options: { bold: true, color: THEME.colors.accent4 } }],
  ];
  table(s, rows, { x: 0.62, y: 1.4, w: 12.06, colW: [5.0, 3.4, 3.66], rowH: 0.52, fontSize: 12 });

  box(s, 0.62, 4.5, 12.06, 1.0, "Ba khoảng trống gộp lại thành một câu hỏi", "Đường dẫn mà GNN XAI in ra có đến từ mạng sinh học thật, và có thuộc về cặp thuốc không?", "data", { ts: 14, bs: 12 });
  bullets(s, [
    "Không ai biết đường dẫn thật cho cặp 5-FU + MK-2206 trên A2058. Luận văn không bịa đáp án.",
    "Thay vào đó: mỗi khẳng định phải vượt một mốc ngẫu nhiên tương ứng.",
  ], { x: 0.62, y: 5.75, w: 12.06, h: 1.0, fontSize: 13 });
}

pres.addSection({ title: "2. Câu hỏi" });

// 6 — hai cau hoi
{
  const s = S("CONTENT", "2. Câu hỏi", "Hai câu hỏi, và một điều kiện tiên quyết trước cả hai");
  box(s, 2.3, 1.35, 8.7, 1.0, "Điều kiện tiên quyết — mô hình có dùng mạng không?", "network share khác 0 rõ   VÀ   QWK(m=1) > QWK(m=0)", "null_", { ts: 13, bs: 11.5 });
  arrow(s, 6.65, 2.35, 6.65, 2.75);

  box(s, 0.62, 2.75, 5.9, 1.75,
    "RQ1 — Topo",
    "Đường dẫn trên PPI thật có khác đường dẫn trên PPI đã xáo giữ bậc không,\nsau khi trừ mức trùng lặp giữa hai mạng xáo độc lập?", "compute", { ts: 14, bs: 11.5 });
  box(s, 6.78, 2.75, 5.9, 1.75,
    "RQ2 — Danh tính",
    "Giải thích ở cấp tương tác có cho đường dẫn đặc hiệu theo cặp hơn cấp logit không,\nsau khi trừ mức đặc hiệu của explainer đường ngắn nhất?", "compute", { ts: 14, bs: 11.5 });

  caption(s, 0.62, 4.62, 5.9, "Đo bằng rewiring-survival, trừ null xáo₁ vs xáo₂. Thấp hơn null là tốt.", { fontSize: 11 });
  caption(s, 6.78, 4.62, 5.9, "Đo bằng partner-specificity, trừ null đường ngắn nhất. Cao hơn null là tốt.", { fontSize: 11 });

  box(s, 0.62, 5.2, 12.06, 1.35,
    "Câu mạnh nhất luận văn được phép viết",
    "\"Lời giải thích trung thực với mô hình, phụ thuộc vào mạng thật vượt mức ngẫu nhiên,\nvà đặc hiệu theo cặp vượt mức baseline.\"   Không bao giờ nói \"explainer tìm đúng cơ chế\".", "pale", { ts: 13, bs: 11.5 });
  s.addNotes("Gioi han nay phai ghi ro trong chuong thao luan.");
}

// 7 — chien luoc
{
  const s = S("CONTENT", "2. Câu hỏi", "Chiến lược khi không có đáp án: bốn phép thử, mỗi phép thử một null");
  box(s, 3.9, 1.3, 5.5, 0.72, "Điều kiện tiên quyết", "mô hình có dùng mạng không?", "null_", { ts: 12, bs: 10 });
  arrow(s, 6.65, 2.02, 6.65, 2.3);
  arrow(s, 6.65, 2.3, 3.0, 2.3);
  arrow(s, 6.65, 2.3, 10.3, 2.3);

  box(s, 0.9, 2.42, 4.2, 1.35, "(1) Trung thực", "Fid± so với xóa cạnh ngẫu nhiên cùng số lượng\nstability giữa 5 seed", "compute", { ts: 12, bs: 10 });
  box(s, 8.2, 2.42, 4.2, 1.35, "(2) Topo → RQ1", "survival(thật, xáo)\ntrừ survival(xáo₁, xáo₂)\nthấp là tốt", "compute", { ts: 12, bs: 10 });
  arrow(s, 3.0, 3.77, 3.0, 4.05);
  arrow(s, 10.3, 3.77, 10.3, 4.05);
  arrow(s, 3.0, 4.05, 6.65, 4.05);
  arrow(s, 10.3, 4.05, 6.65, 4.05);
  arrow(s, 6.65, 4.05, 6.65, 4.3);

  box(s, 3.6, 4.3, 6.1, 1.2, "(3) Danh tính → RQ2", "partner-specificity của edge-IG trừ specificity của đường ngắn nhất\ncấp (iii) có cao hơn cấp (i)?", "compute", { ts: 12, bs: 10 });
  arrow(s, 6.65, 5.5, 6.65, 5.78);
  box(s, 2.3, 5.78, 8.7, 0.95, "(4) Case study — chương riêng, không phải phép thử chính", "2–3 cặp đối chứng dương, chấm bằng gene set KEGG, so với đường ngẫu nhiên cùng độ dài", "pale", { ts: 11.5, bs: 10 });
}

pres.addSection({ title: "3. Dữ liệu" });

// 8 — bon nguon
{
  const s = S("CONTENT", "3. Dữ liệu", "Bốn nguồn phải ghép, cộng một nhóm chỉ để chấm điểm");
  const items = [
    ["Nhãn hiệp đồng", "O'Neil 2016 qua DrugComb", "38 thuốc · 39 cell line · ~22–23 nghìn bộ ba", "src"],
    ["Đặc trưng cell line", "DepMap / CCLE", "biểu hiện gen log2(TPM+1), z-score theo từng gen", "src"],
    ["Đích thuốc", "DrugBank / ChEMBL / DGIdb", "bảng hai cột drug, gene → cờ tA(g), tB(g)", "src"],
    ["Mạng", "STRING v12, combined_score ≥ 700", "lọc 2 bước quanh tập đích thuốc — là mạng DUY NHẤT", "compute"],
  ];
  items.forEach(([t, src, d, k], i) => {
    const y = 1.35 + i * 1.03;
    box(s, 0.62, y, 2.9, 0.88, t, null, k, { ts: 13 });
    s.addText([
      { text: src, options: { bold: true, fontSize: 12.5, color: C.text1, breakLine: true } },
      { text: d, options: { fontSize: 11, color: C.accent2 } },
    ], { x: 3.72, y, w: 9.0, h: 0.88, isTextBox: true, margin: 0, valign: "middle", objectName: oid("srcl") });
  });
  box(s, 0.62, 5.5, 12.06, 1.1, "Mọi nguồn đều đã công bố. Không sinh dữ liệu, không dùng luật sinh nhãn.",
    "Dữ liệu tự sinh sẽ không được kiểm chứng và không có giá trị khoa học để đánh giá.", "pale", { ts: 13, bs: 11.5 });
}

// 9 — nhan
{
  const s = S("CONTENT", "3. Dữ liệu", "Nhãn: chỉ O'Neil, ba lớp theo điểm Loewe");
  const rows = [
    [TH("Lớp"), TH("Điều kiện Loewe"), TH("Ý nghĩa")],
    [{ text: "syn", options: { bold: true, color: THEME.colors.accent5 } }, "> 10", "hiệp đồng — hai thuốc mạnh hơn tổng riêng lẻ"],
    [{ text: "add", options: { bold: true, color: THEME.colors.dk2 } }, "−10 đến 10", "cộng tính — thường chiếm đa số"],
    [{ text: "ant", options: { bold: true, color: THEME.colors.accent4 } }, "< −10", "đối kháng"],
  ];
  table(s, rows, { x: 0.62, y: 1.35, w: 7.4, colW: [1.3, 2.1, 4.0], rowH: 0.5, fontSize: 12 });

  box(s, 8.3, 1.35, 4.38, 2.0, "Vì sao chỉ O'Neil?", "Mọi bài trong tổng quan đều so trên bộ này, nên kết quả có chỗ đối chiếu.\nALMANAC và DrugComb đầy đủ để sau.", "pale", { ts: 12, bs: 10.5 });

  box(s, 0.62, 3.6, 12.06, 1.05, "Một cảnh báo phải xử lý", "Preprint trên DrugComb: Loewe chỉ tương quan r = 0,28 với ZIP, và 21–34% ma trận bị một phương pháp gọi là syn trong khi phương pháp khác gọi là ant.", "null_", { ts: 13, bs: 11 });
  arrow(s, 6.65, 4.65, 6.65, 4.95);
  box(s, 2.3, 4.95, 8.7, 0.9, "Bảng độ nhạy ở phụ lục", "lặp lại chỉ số chính với Bliss, và với ngưỡng ±5 và ±20 — một bảng phụ lục, không phải một nhánh thí nghiệm riêng", "compute", { ts: 12.5, bs: 10.5 });
  caption(s, 0.62, 6.1, 12.06, "Ở ngưỡng ±10 lớp add thường chiếm đa số, nên phải biết tỷ lệ trước khi chọn loss: cross-entropy có trọng số lớp = 1 / tần suất.", { fontSize: 11.5 });
}

// 10 — cell line + dich thuoc
{
  const s = S("CONTENT", "3. Dữ liệu", "Cell line và đích thuốc: hai chỗ tốn công nhất");
  box(s, 0.62, 1.35, 5.9, 0.62, "Đặc trưng cell line — DepMap", null, "src", { ts: 14 });
  bullets(s, [
    "OmicsExpressionProteinCodingGenesTPMLogp1.csv — biểu hiện gen",
    "Model.csv — map mã ACH sang tên cell line",
    { t: "Z-score theo từng gen: mốc 0 = mức trung bình.", bold: true },
    { t: "Mốc 0 này chính là baseline của Integrated Gradients.", b: false, lvl: 1 },
  ], { x: 0.72, y: 2.12, w: 5.7, h: 1.9, fontSize: 12, gap: 7 });
  box(s, 0.62, 4.1, 5.9, 1.3, "Bẫy: khớp tên cell line", "\"NCI-H460\", \"NCIH460\", \"H460\" là cùng một dòng.\nDành vài ngày và lưu bảng map thủ công.", "null_", { ts: 12, bs: 10.5 });

  box(s, 6.78, 1.35, 5.9, 0.62, "Đích thuốc — DrugBank / ChEMBL", null, "src", { ts: 14 });
  bullets(s, [
    "DrugBank đầy đủ nhất nhưng cần license học thuật",
    "ChEMBL, DGIdb, TTD thay thế được",
    { t: "Định dạng cuối: bảng hai cột drug, gene", bold: true },
    { t: "tA(g) = 1 nếu g là đích của thuốc A", b: false, lvl: 1 },
  ], { x: 6.88, y: 2.12, w: 5.7, h: 1.9, fontSize: 12, gap: 7 });
  box(s, 6.78, 4.1, 5.9, 1.3, "Bẫy: thuốc Merck mã MK-xxxx", "ít được chú giải đích. Ghi lại thuốc nào không có đích;\nchúng bị loại khỏi phần giải thích vì không có điểm bắt đầu trên mạng.", "null_", { ts: 12, bs: 10.5 });

  caption(s, 0.62, 5.6, 12.06, "Chỉ giữ gen có trong cả mạng và bảng biểu hiện, và nằm trong vòng 2 bước quanh tập đích thuốc — còn khoảng 2.000 gen, đủ chạy trên máy phổ thông.", { fontSize: 11.5 });
}

// 11 — mang
{
  const s = S("CONTENT", "3. Dữ liệu", "Mạng: chỉ STRING. KEGG bị gỡ khỏi vai trò mạng.");
  box(s, 0.62, 1.35, 5.9, 1.85, "STRING v12 — mạng duy nhất", "người, mã loài 9606\ncombined_score ≥ 700\nlọc 2 bước quanh tập đích thuốc\n9606.protein.links.v12.0.txt.gz + protein.info", "compute", { ts: 14, bs: 11 });
  box(s, 6.78, 1.35, 5.9, 1.85, "KEGG — chỉ dùng để chấm điểm", "gene set qua MSigDB C2 hoặc KEGG REST\nxuất hiện duy nhất ở chương case study\nkhông bao giờ là mạng để chạy đường dẫn", "null_", { ts: 14, bs: 11 });

  box(s, 0.62, 3.5, 12.06, 1.5, "Vì sao đây là chỗ sửa quan trọng so với bản 1",
    "Bản 1 dùng mạng KEGG cho phần lõi, rồi lại dùng gene set KEGG để kiểm chứng lời giải thích.\nĐó là vòng lặp: đường dẫn chạy trên mạng KEGG thì đương nhiên rơi vào pathway KEGG, nên con số kiểm chứng không có giá trị.", "out", { ts: 14, bs: 12 });

  bullets(s, [
    { t: "Xáo giữ bậc: networkx.double_edge_swap, lặp 10 × số cạnh", bold: true },
    "Mạng xáo phải tạo lại ở MỖI seed. Dùng một mạng xáo duy nhất cho mọi lần chạy thì kết quả chỉ phản ánh một lần xáo may hay rủi.",
  ], { x: 0.62, y: 5.25, w: 12.06, h: 1.3, fontSize: 13 });
}

// 12 — du lieu cham diem + doi chung duong
{
  const s = S("CONTENT", "3. Dữ liệu", "Dữ liệu chấm điểm và cặp đối chứng dương");
  const rows = [
    [TH("Nguồn"), TH("Dùng ở đâu")],
    ["Gene set KEGG (MSigDB C2 / KEGG REST)", "Case study: top-k gen có rơi vào pathway kỳ vọng không"],
    ["DepMap CRISPR (CRISPRGeneEffect.csv, Chronos)", "Case study: gen trên đường dẫn có cần cho cell đó không"],
    ["Interactome Cheng 2019", "Tính baseline s_AB đúng như bài gốc"],
  ];
  table(s, rows, { x: 0.62, y: 1.35, w: 12.06, colW: [5.0, 7.06], rowH: 0.46, fontSize: 11.5 });

  box(s, 0.62, 3.25, 12.06, 0.78, "Bẫy của DepMap CRISPR", "Nhiều gen thiết yếu với MỌI cell line (ribosome, spliceosome). Phải loại nhóm này trước và so với gen cùng bậc, nếu không kết quả chỉ phản ánh việc đường dẫn đi qua hub.", "null_", { ts: 12, bs: 10.5 });

  const rows2 = [
    [TH("Cặp ứng viên"), TH("Lớp thuốc"), TH("Pathway kỳ vọng (KEGG)")],
    ["PD325901 + MK-2206", "ức chế MEK + ức chế AKT", "MAPK (hsa04010), PI3K-Akt (hsa04151)"],
    ["MK-8776 + gemcitabine", "ức chế CHK1 + tương tự nucleoside", "chu kỳ tế bào (hsa04110), sao chép DNA (hsa03030)"],
    ["ABT-888 + temozolomide", "ức chế PARP + gây tổn thương DNA", "sửa chữa cắt base (hsa03410)"],
  ];
  table(s, rows2, { x: 0.62, y: 4.25, w: 12.06, colW: [3.3, 3.9, 4.86], rowH: 0.44, fontSize: 11 });
  caption(s, 0.62, 6.1, 12.06, "Cả ba đều nằm trong O'Neil. Chỉ giữ cặp có nhãn syn ở phần lớn cell line — cặp có cơ chế đã biết nhưng dữ liệu không ghi nhận hiệp đồng thì loại. Đây là kỳ vọng định tính ở mức pathway, không phải đáp án cấp cạnh.", { fontSize: 11 });
}

pres.addSection({ title: "4. Khung thí nghiệm" });

// 13 — khung A-E
{
  const s = S("CONTENT", "4. Khung thí nghiệm", "Khung thí nghiệm: năm khối, nhưng chỉ MỘT mô hình");
  box(s, 0.62, 1.35, 3.7, 1.5, "[A]  SynergyGNN", "GCN 2 lớp có mask cạnh m\n← đây là mô hình duy nhất bạn train", "compute", { ts: 14, bs: 11 });
  box(s, 4.52, 1.35, 3.95, 1.5, "[B]  Mốc so sánh", "one-hot MLP · MLP kiểu DeepSynergy\ns_AB Cheng · đường ngắn nhất", "pale", { ts: 14, bs: 11 });
  box(s, 8.67, 1.35, 4.01, 1.5, "[C]  Đầu vào của A", "mạng thật · xáo giữ bậc (2 lần độc lập)\nm = 0 (không mạng)", "pale", { ts: 14, bs: 11 });

  arrow(s, 2.47, 2.85, 2.47, 3.25);
  box(s, 0.62, 3.25, 12.06, 0.8, "[D]  edge-IG — ba cấp: logit / contrast / interaction", null, "data", { ts: 14 });
  arrow(s, 6.65, 4.05, 6.65, 4.45);
  box(s, 0.62, 4.45, 12.06, 1.0, "[E]  Bộ đo", "network share · Fid± · stability · rewiring-survival · partner-specificity\nmọi chỉ số đều trừ null", "out", { ts: 14, bs: 11.5 });

  box(s, 0.62, 5.7, 12.06, 0.9, "Năm chữ cái không phải năm mô hình",
    "B là mốc so sánh, C là các phiên bản đầu vào của chính A, D và E là công cụ đo. Một kiến trúc GCN duy nhất, train 100 lần.", "null_", { ts: 13, bs: 11.5 });
  s.addNotes("Day la cho de hieu nham nhat. Nhan manh: chi khoi A duoc train.");
}

// 14 — DIAGRAM kien truc
{
  const s = S("CONTENT", "4. Khung thí nghiệm", "Khối A — SynergyGNN, một lượt forward đầy đủ");
  caption(s, 0.62, 1.1, 12.06, "Số chiều là ví dụ cụ thể: 2.000 gen, 20.000 cạnh, hidden 32.", { fontSize: 10.5 });

  // hang 1: dau vao
  box(s, 0.62, 1.5, 2.55, 1.15, "X — đặc trưng node", "X[g] = [ expr_c(g), tA+tB, tA·tB ]\n[ 2000 × 3 ]", "data", { ts: 11, bs: 9.5 });
  box(s, 0.62, 2.9, 2.55, 1.0, "edge_index + mask m", "[ 2 × 20000 ] , m ∈ R^20000\nmặc định m = 1", "data", { ts: 11, bs: 9.5 });
  arrow(s, 3.17, 3.4, 3.72, 3.4);
  box(s, 3.72, 2.9, 2.5, 1.0, "Â_m", "A_m = A ⊙ m\nÂ_m = D^(−1/2)(A_m+I)D^(−1/2)", "compute", { ts: 11, bs: 9 });
  // X khong sinh ra edge_index: cho X di vong len tren roi xuong thang GCN lop 1
  s.addShape(pres.shapes.LINE, { x: 3.17, y: 2.07, w: 4.7, h: 0,
    line: { color: C.accent2, width: 1.5, endArrowType: "none", beginArrowType: "none" },
    objectName: oid("arw") });
  arrow(s, 7.87, 2.07, 7.87, 2.9);

  arrow(s, 6.22, 3.4, 6.77, 3.4);
  box(s, 6.77, 2.9, 2.2, 1.0, "GCN lớp 1", "H1 = ReLU(Â_m · X · W1)\nW1 [3×32] → [2000×32]", "compute", { ts: 11, bs: 9 });
  arrow(s, 8.97, 3.4, 9.5, 3.4);
  box(s, 9.5, 2.9, 2.2, 1.0, "GCN lớp 2", "H2 = ReLU(Â_m · H1 · W2)\nW2 [32×32] → [2000×32]", "compute", { ts: 11, bs: 9 });

  // hang 2
  arrow(s, 10.6, 3.9, 10.6, 4.25);
  box(s, 9.5, 4.25, 2.2, 0.95, "Chiếu + Flatten", "P = H2 · W3, W3 [32×4]\nvec(P) → h [ 8000 ]", "compute", { ts: 11, bs: 9 });
  arrow(s, 9.5, 4.72, 8.97, 4.72);
  box(s, 6.77, 4.25, 2.2, 0.95, "MLP đầu đọc", "8000 → 128 (ReLU, dropout 0,3) → 3", "compute", { ts: 11, bs: 9 });
  arrow(s, 6.77, 4.72, 6.22, 4.72);
  box(s, 3.72, 4.25, 2.5, 0.95, "z = (z_ant, z_add, z_syn)", "softmax → xác suất 3 lớp", "out", { ts: 11, bs: 9 });
  arrow(s, 3.72, 4.72, 3.17, 4.72);
  box(s, 0.62, 4.25, 2.55, 0.95, "→ sang explainer", "edge-IG lấy đạo hàm theo m", "data", { ts: 11, bs: 9 });

  box(s, 0.62, 5.45, 12.06, 1.15, "Hai điều kiện cài đặt phải test trước khi train",
    "m = 1 phải cho đúng đầu ra của GCN thường  ·  m = 0 → Â_m chỉ còn tự vòng, không gen nào nhận tin, đó là \"mô hình không có mạng\" và là baseline của IG\nD là bậc tính TRÊN A_m + I, không phải trên A gốc — dựng lại mỗi lượt forward", "null_", { ts: 12, bs: 10 });
}

// 15 — ba quyet dinh
{
  const s = S("CONTENT", "4. Khung thí nghiệm", "Ba quyết định thiết kế, và lý do của từng cái");
  const items = [
    ["1", "Mask cạnh m nằm sẵn trong forward", "edge-IG cần đạo hàm của đầu ra theo từng m_e. Vá sau thì không lấy được. Test: m = 1 phải cho đúng GCN thường.", "compute"],
    ["2", "Flatten, KHÔNG mean-pool", "Pooling trộn mọi gen thành một vector, danh tính gen biến mất, attribution lên gen mất nghĩa — mà đó chính là thứ luận văn cần đọc. Giá phải trả: 8000 × 128 ≈ 1,02 triệu tham số.", "compute"],
    ["3", "KHÔNG có embedding thuốc", "Đây là chỗ khác bản 1. Embedding thuốc là đường tắt để mô hình nhớ danh tính, mà danh tính đúng là thứ RQ2 muốn loại trừ. Bỏ nó thì mô hình buộc phải đi qua cờ đích trên mạng.", "out"],
  ];
  items.forEach(([n, t, d, k], i) => {
    const y = 1.35 + i * 1.35;
    s.addShape(pres.shapes.OVAL, { x: 0.62, y: y + 0.2, w: 0.55, h: 0.55, fill: { color: k === "out" ? C.accent4 : C.accent1 }, line: { color: k === "out" ? C.accent4 : C.accent1 }, objectName: oid("n") });
    s.addText(n, { x: 0.62, y: y + 0.2, w: 0.55, h: 0.55, isTextBox: true, margin: 0, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle", objectName: oid("nt") });
    s.addText([
      { text: t, options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
      { text: d, options: { fontSize: 11.5, color: C.accent2 } },
    ], { x: 1.4, y, w: 11.3, h: 1.2, isTextBox: true, margin: 0, valign: "middle", objectName: oid("dl") });
  });
  box(s, 0.62, 5.5, 12.06, 1.1, "Hệ quả của quyết định 3 phải nói thẳng trong luận văn",
    "Hiệu năng dự đoán sẽ thấp hơn các bài đã công bố. Điều đó không sao — luận văn không so hiệu năng.\nNhưng phải báo cáo rõ, và chạy thêm một bản CÓ embedding để đối chiếu.", "null_", { ts: 13, bs: 11.5 });
}

// 16 — khoi B + C
{
  const s = S("CONTENT", "4. Khung thí nghiệm", "Khối B: mốc so sánh.  Khối C: bốn điều kiện mạng.");
  const rows = [
    [TH("Mốc so sánh"), TH("Đầu vào"), TH("Trả lời câu gì")],
    ["One-hot MLP", "one-hot của A, B, c", "Nhớ danh tính đạt bao nhiêu? GNN không thắng thì mạng không đóng góp"],
    ["MLP kiểu DeepSynergy", "biểu hiện gen của c + vector đích", "Có đặc trưng sinh học nhưng không có mạng"],
    ["s_AB của Cheng", "đích A, đích B, mạng", "Explainer phi học máy, theo khoảng cách"],
    [{ text: "Đường ngắn nhất", options: { bold: true, color: THEME.colors.accent4 } }, "đích A, đích B, mạng", { text: "Explainer ngây thơ nhất — và là NULL của partner-specificity", options: { bold: true, color: THEME.colors.accent4 } }],
  ];
  table(s, rows, { x: 0.62, y: 1.35, w: 12.06, colW: [2.9, 3.5, 5.66], rowH: 0.46, fontSize: 11 });

  const rows2 = [
    [TH("Điều kiện mạng"), TH("Cách tạo"), TH("Dùng để"), TH("Số lần train")],
    ["Thật", "STRING ≥ 700, lọc 2-hop", "kết quả chính", "25"],
    ["Xáo giữ bậc ①", "double_edge_swap, seed A", "RQ1", "25"],
    [{ text: "Xáo giữ bậc ②", options: { bold: true, color: THEME.colors.accent4 } }, "như trên, seed khác", { text: "NULL của RQ1", options: { bold: true, color: THEME.colors.accent4 } }, "25"],
    ["m = 0", "cố định mask bằng 0", "điều kiện tiên quyết", "25"],
  ];
  table(s, rows2, { x: 0.62, y: 3.85, w: 12.06, colW: [2.9, 3.9, 3.76, 1.5], rowH: 0.46, fontSize: 11 });
  caption(s, 0.62, 6.15, 12.06, "Tổng 100 lần train khối A + 25 lần cho mỗi baseline học máy. Một kiến trúc GCN duy nhất, bốn phiên bản đầu vào.", { fontSize: 11.5 });
}

pres.addSection({ title: "5. Explainer" });

// 17 — DIAGRAM edge-IG
{
  const s = S("CONTENT", "5. Explainer", "Khối D — edge-IG: Integrated Gradients theo mask cạnh");
  box(s, 3.6, 1.2, 6.1, 0.65, "Mô hình A đã train, đóng băng tham số", "toàn bộ trang này là hậu kiểm, không train thêm", "src", { ts: 12, bs: 9.5 });
  arrow(s, 6.65, 1.85, 6.65, 2.15);
  box(s, 0.62, 2.15, 5.8, 1.6, "edge-IG",
    "Đường tích phân: m(α) = α · 1, α đi từ 0 (mạng rỗng) tới 1 (mạng đầy đủ)\nφ_e = (1 − 0) · ∫₀¹ ∂f(m(α)) / ∂m_e dα\nXấp xỉ Riemann điểm giữa, S = 50: α_s = (s − 0,5) / S\n50 forward-backward cho một bộ ba", "compute", { ts: 13, bs: 10 });
  box(s, 6.78, 2.15, 5.9, 1.6, "Vì sao baseline là m = 0, không phải X = 0",
    "Câu hỏi của luận văn là MẠNG đóng góp gì, nên phải đi dọc trục mạng.\nỞ m = 0 mọi gen chỉ còn tự vòng, GCN không truyền tin — đầu ra baseline đúng là \"mô hình không có mạng\".", "null_", { ts: 13, bs: 10 });

  arrow(s, 3.5, 3.75, 3.5, 4.05);
  box(s, 1.4, 4.05, 4.2, 0.72, "φ ∈ R^20000 — điểm đóng góp của TỪNG CẠNH", null, "data", { ts: 12 });

  arrow(s, 3.5, 4.77, 3.5, 5.1);
  box(s, 0.62, 5.1, 5.8, 1.45, "Completeness → network share",
    "Σ_e φ_e = f(m=1) − f(m=0) — đẳng thức đúng, không phải xấp xỉ, nên dùng được làm phép kiểm tra cài đặt\nnetwork share = ( Σ_e φ_e ) / f(m=1)\nGần 0 → mô hình gần như không dùng mạng → mọi đường dẫn đọc ra sau đó là vô nghĩa", "out", { ts: 13, bs: 10 });

  box(s, 6.78, 4.05, 5.9, 2.5, "Chi phí của cấp (iii), và cách làm cho nó chạy được",
    "IG tuyến tính theo f, nên không cần chạy IG trên công thức ghép. Chạy IG riêng rồi cộng trừ:\nφ(iii) = φ(A,B) − mean_r φ(A,r) − mean_r φ(r,B) + mean_(r,r') φ(r,r')\n\nCache: số hạng cuối chỉ phụ thuộc cell c → tính một lần mỗi cell.\nSố hạng giữa tính một lần mỗi (thuốc, cell).\nNếu vẫn chậm: lấy mẫu 8 thuốc tham chiếu, rồi báo kết quả đổi bao nhiêu khi tăng lên 16.", "note", { ts: 13, bs: 10 });
}

// 18 — ba cap
{
  const s = S("CONTENT", "5. Explainer", "Ba cấp giải thích: logit, contrast, interaction");
  const kinds = ["pale", "data", "out"];
  const items = [
    ["Cấp (i) — logit", "f = z_syn", "Cạnh nào đẩy logit syn lên?", "Đây là cách gần như mọi bài đã công bố đang làm."],
    ["Cấp (ii) — contrast", "f = Δ = z_syn − z_add", "Vì sao là syn chứ không phải add?", "Trừ đi phần nền chung mà mọi lớp đều có."],
    ["Cấp (iii) — interaction", "f = Δ(A,B) − E_r Δ(A,r) − E_r Δ(r,B) + E_(r,r') Δ(r,r')", "Phần nào thuộc riêng về CẶP?", "Sau khi trừ hiệu ứng riêng của từng thuốc. r là thuốc tham chiếu, cùng cell c."],
  ];
  items.forEach(([t, f, q, d], i) => {
    const y = 1.35 + i * 1.3;
    box(s, 0.62, y, 3.3, 1.15, t, null, kinds[i], { ts: 14 });
    s.addText([
      { text: f, options: { fontSize: 12, bold: true, color: C.accent2, breakLine: true } },
      { text: q + "  ", options: { fontSize: 11.5, color: C.text1 } },
      { text: d, options: { fontSize: 11.5, italic: true, color: C.accent1 } },
    ], { x: 4.1, y, w: 8.6, h: 1.15, isTextBox: true, margin: 0, valign: "middle", objectName: oid("lv") });
  });
  box(s, 0.62, 5.35, 12.06, 1.25, "Cấp (iii) không phải công thức tự nghĩ ra",
    "Cùng cấu trúc với sai phân bậc hai của Shapley interaction index (Grabisch & Roubens 1999):  v(S∪{i,j}) − v(S∪{i}) − v(S∪{j}) + v(S)\nJanizek et al. (Nat Biomed Eng 2023) đã làm ở cấp gen trên ensemble cây. Chưa ai làm ở cấp cạnh cho GNN hiệp đồng — đây là đóng góp 2.", "note", { ts: 13, bs: 11 });
}

// 19 — tu diem canh sang duong dan
{
  const s = S("CONTENT", "5. Explainer", "Từ điểm cạnh sang đường dẫn");
  box(s, 0.62, 1.4, 2.7, 0.85, "φ_e trên mỗi cạnh", null, "data", { ts: 12 });
  arrow(s, 3.32, 1.82, 3.8, 1.82);
  box(s, 3.8, 1.4, 2.7, 0.85, "Chuẩn hóa |φ_e|", "về khoảng (0, 1] → p_e", "compute", { ts: 12, bs: 9.5 });
  arrow(s, 6.5, 1.82, 6.98, 1.82);
  box(s, 6.98, 1.4, 2.7, 0.85, "Chi phí cạnh", "c_e = − log(p_e) + λ", "compute", { ts: 12, bs: 9.5 });
  arrow(s, 9.68, 1.82, 10.16, 1.82);
  box(s, 10.16, 1.4, 2.52, 0.85, "k đường ngắn nhất", "shortest_simple_paths", "out", { ts: 12, bs: 9.5 });

  box(s, 0.62, 2.55, 6.0, 1.9, "Cái bẫy của − log",
    "− log biến tổng chi phí thành TÍCH các điểm, nên đường dài hơn vẫn có thể thắng.\n\nVí dụ: hai cạnh 0,9 và 0,8 cho 0,328.\nBa cạnh 0,9 cho 0,316 → đường ba cạnh thắng.\n\nλ là phạt cố định mỗi cạnh để ưu tiên đường ngắn. Nó đổi kết quả, nên phải ghi giá trị vào luận văn.", "null_", { ts: 13, bs: 10.5 });
  box(s, 6.88, 2.55, 5.8, 1.9, "Chạy giữa MỌI cặp (đích A, đích B)",
    "Gộp lại rồi xếp hạng theo tổng chi phí.\n\nTrước khi train, đếm phân bố khoảng cách giữa đích của A và đích của B trên mạng.\n\nGCN 2 lớp chỉ \"thấy\" 2 bước. Nếu phần lớn cặp cách nhau hơn 2 bước thì thông tin hai nhánh KHÔNG BAO GIỜ gặp nhau, và mọi đường dẫn đọc ra sau đó đều vô nghĩa.", "note", { ts: 13, bs: 10.5 });

  box(s, 0.62, 4.75, 12.06, 1.0, "Mọi chỉ số đều tính HAI lần",
    "một lần trên tập top-k GEN, một lần trên tập ĐƯỜNG DẪN. Hai cấp này có thể cho kết luận khác nhau, và sự khác nhau đó đáng viết.", "data", { ts: 14, bs: 11.5 });
  caption(s, 0.62, 5.95, 12.06, "Công cụ: torch, numpy, pandas, scikit-learn, networkx. GCN và IG tự viết, mỗi phần vài chục dòng. Mạng dưới 3 nghìn gen thì không cần PyG hay Captum.", { fontSize: 11 });
}

pres.addSection({ title: "6. Null" });

// 20 — bon null
{
  const s = S("CONTENT", "6. Null", "Null cho mọi chỉ số — phần mới và quan trọng nhất của bản 2");
  box(s, 0.62, 1.3, 12.06, 0.9, "Nguyên tắc chung", "Mọi null phải đi qua ĐÚNG bộ trích đường dẫn như kết quả thật.\nNếu null tính ở cấp cạnh mà kết quả thật ở cấp đường dẫn, thì chênh lệch có thể đến từ bước trích đường, không phải từ explainer.", "out", { ts: 14, bs: 11.5 });

  const rows = [
    [TH("Chỉ số"), TH("Phép thử"), TH("Null tương ứng"), TH("Tốt khi")],
    ["Network share", "điều kiện tiên quyết", "0", "khác 0 rõ"],
    ["QWK m=1 so m=0", "điều kiện tiên quyết", "mô hình m = 0", "m = 1 hơn rõ"],
    ["Fid+ / Fid−", "(1) trung thực", "xóa cạnh ngẫu nhiên cùng số lượng, 20 lần", "vượt null"],
    ["Stability", "(1) trung thực", "—", "cosine giữa 5 seed cao"],
    [{ text: "Rewiring-survival", options: { bold: true } }, "(2) topo — RQ1", "survival giữa hai mạng xáo độc lập", { text: "THẤP hơn null", options: { bold: true, color: THEME.colors.accent4 } }],
    [{ text: "Partner-specificity", options: { bold: true } }, "(3) danh tính — RQ2", "specificity của đường ngắn nhất", { text: "CAO hơn null, (iii) > (i)", options: { bold: true, color: THEME.colors.accent4 } }],
    ["Positive-control hit", "case study", "1.000 đường ngẫu nhiên cùng độ dài", "cao hơn null"],
  ];
  table(s, rows, { x: 0.62, y: 2.5, w: 12.06, colW: [2.6, 2.7, 4.3, 2.46], rowH: 0.42, fontSize: 10.5 });

  box(s, 0.62, 5.85, 12.06, 0.75, "Cách trình bày trong luận văn", "Mọi bảng kết quả đều có ba cột: giá trị thật, giá trị null, hiệu kèm khoảng tin cậy. Không bảng nào chỉ có một cột.", "pale", { ts: 13, bs: 11 });
}

// 21 — null RQ1
{
  const s = S("CONTENT", "6. Null", "Null của RQ1: vì sao survival 0,8 không nói lên điều gì");
  box(s, 0.62, 1.35, 12.06, 0.85, "Vấn đề", "survival = |T_thật ∩ T_xáo| / k không bao giờ về 0, kể cả khi lời giải thích hoàn toàn không phụ thuộc mạng — vì đích thuốc cố định trên mọi mạng, và gen bậc cao dễ nằm trên đường dẫn ở bất kỳ mạng nào.", "null_", { ts: 13, bs: 11 });

  box(s, 0.62, 2.5, 3.75, 1.5, "Mạng THẬT", "STRING ≥ 700\ntrain → explainer → T(thật)", "compute", { ts: 12, bs: 10 });
  box(s, 4.77, 2.5, 3.75, 1.5, "XÁO₁ (seed A)", "double_edge_swap\ntrain → explainer → T(xáo₁)", "note", { ts: 12, bs: 10 });
  box(s, 8.93, 2.5, 3.75, 1.5, "XÁO₂ (seed B)", "độc lập với XÁO₁\ntrain → explainer → T(xáo₂)", "note", { ts: 12, bs: 10 });
  arrow(s, 2.5, 4.0, 2.5, 4.3);
  arrow(s, 2.5, 4.3, 6.65, 4.3);
  arrow(s, 6.65, 4.0, 6.65, 4.3);
  arrow(s, 10.8, 4.0, 10.8, 4.3);

  s.addText("survival_thật = survival( T(thật), T(xáo₁) )     −     survival_null = survival( T(xáo₁), T(xáo₂) )",
    { x: 0.62, y: 4.4, w: 12.06, h: 0.45, isTextBox: true, margin: 0, fontSize: 13, bold: true, color: C.accent2, align: "center", objectName: oid("eq") });

  box(s, 0.62, 5.0, 5.9, 0.85, "Hiệu ≈ 0", "mạng thật không đặc biệt hơn một mạng xáo bất kỳ → lời giải thích không đến từ sinh học", "out", { ts: 12, bs: 10 });
  box(s, 6.78, 5.0, 5.9, 0.85, "Hiệu âm rõ", "lời giải thích CÓ phụ thuộc mạng thật", "compute", { ts: 12, bs: 10 });
  caption(s, 0.62, 6.0, 12.06, "Tính thêm một bản BỎ đích thuốc khỏi top-k, vì đích luôn sống sót — chúng có cờ tA = 1 trên mọi mạng.", { fontSize: 11.5 });
}

// 22 — null RQ2
{
  const s = S("CONTENT", "6. Null", "Null của RQ2: đường ngắn nhất tự nó đã đặc hiệu");
  box(s, 0.62, 1.35, 12.06, 0.85, "Vấn đề", "Đổi thuốc đối tác là đổi điểm cuối, nên đường ngắn nhất đổi theo mà không cần học gì. Nếu báo specificity của edge-IG mà không có mốc, con số 0,45 không nói lên điều gì.", "null_", { ts: 13, bs: 11 });

  box(s, 0.62, 2.45, 12.06, 1.3, "Cách đo partner-specificity",
    "Với bộ ba (A, B, c) được dự đoán syn: T(A,B,c) = top-k gen trên đường dẫn, đã BỎ đích của A và B.\nChọn vài thuốc đối tác r KHÔNG chung đích với B.   specificity = 1 − mean Jaccard( T(A,B,c), T(A,r,c) )   — làm cả hai phía rồi lấy trung bình.", "compute", { ts: 13, bs: 11 });

  s.addText("specificity_thật ( edge-IG cấp (i) hoặc (iii) )     −     specificity_null ( đường ngắn nhất, chung bộ đích và chung k )",
    { x: 0.62, y: 3.95, w: 12.06, h: 0.45, isTextBox: true, margin: 0, fontSize: 13, bold: true, color: C.accent2, align: "center", objectName: oid("eq") });

  box(s, 0.62, 4.6, 12.06, 1.0, "Giả thuyết RQ2", "Cấp (iii) — interaction — cho hiệu lớn hơn cấp (i) — logit.\nVì cấp (iii) đã trừ đi hiệu ứng riêng của từng thuốc, nên phần còn lại đáng ra phải thuộc về cặp.", "data", { ts: 14, bs: 11.5 });

  box(s, 0.62, 5.75, 12.06, 0.85, "Không cần ROAR cho phần lõi", "ROAR đòi train lại sau mỗi lần xóa, tốn nhất trong bộ đo. Fid± có null đã trả lời được câu hỏi trung thực ở mức đủ cho luận văn.", "pale", { ts: 12.5, bs: 10.5 });
}

pres.addSection({ title: "7. Thí nghiệm" });

// 23 — DIAGRAM toan bo thi nghiem
{
  const s = S("CONTENT", "7. Thí nghiệm", "Quy trình một thí nghiệm hoàn chỉnh");
  box(s, 2.9, 1.15, 7.5, 0.6, "Chuẩn bị dữ liệu → một file .pt  ·  split leave-combo", null, "src", { ts: 11.5 });
  arrow(s, 6.65, 1.75, 6.65, 2.0);

  const cond = [["Mạng THẬT", "25 lần train", "compute"], ["XÁO₁", "25 lần train", "note"], ["XÁO₂ — null", "25 lần train", "note"], ["m = 0", "25 lần train", "null_"]];
  cond.forEach(([t, d, k], i) => {
    box(s, 0.62 + i * 3.08, 2.0, 2.88, 0.8, t, d, k, { ts: 11.5, bs: 9.5 });
  });
  box(s, 0.62, 2.95, 12.06, 0.58, "Khối B — one-hot MLP · MLP kiểu DeepSynergy · s_AB Cheng · đường ngắn nhất (cùng split)", null, "pale", { ts: 11 });

  arrow(s, 6.65, 3.53, 6.65, 3.78);
  s.addShape(pres.shapes.HEXAGON, { x: 2.9, y: 3.78, w: 7.5, h: 0.75, fill: { color: "FDF4DC" }, line: { color: C.accent3, width: 1.5 }, objectName: oid("gate") });
  s.addText([{ text: "GATE — mô hình có dùng mạng không?   ", options: { bold: true, fontSize: 12, color: C.text1 } },
    { text: "network share ≠ 0 rõ VÀ QWK(m=1) > QWK(m=0)", options: { fontSize: 10, color: C.accent2 } }],
    { x: 2.9, y: 3.78, w: 7.5, h: 0.75, isTextBox: true, margin: 0, align: "center", valign: "middle", objectName: oid("gt") });

  arrow(s, 6.65, 4.53, 6.65, 4.78);
  box(s, 0.62, 4.78, 12.06, 0.6, "edge-IG 3 cấp trên tập test, cả ba mạng  →  trích top-k GEN và top-k ĐƯỜNG DẪN", null, "data", { ts: 11.5 });
  arrow(s, 6.65, 5.38, 6.65, 5.6);
  box(s, 0.62, 5.6, 3.9, 0.58, "RQ1 — topo", null, "out", { ts: 11.5 });
  box(s, 4.7, 5.6, 3.9, 0.58, "RQ2 — danh tính", null, "out", { ts: 11.5 });
  box(s, 8.78, 5.6, 3.9, 0.58, "Trung thực + case study", null, "out", { ts: 11.5 });

  box(s, 0.62, 6.3, 12.06, 0.5, "Không qua gate thì VẪN chạy tiếp — \"mô hình không dùng mạng VÀ explainer vẫn in ra đường dẫn trông hợp lý\" là kết quả mạnh hơn nhiều", null, "null_", { ts: 11 });
}

// 24 — split + cau hinh
{
  const s = S("CONTENT", "7. Thí nghiệm", "Split, cấu hình train, và chi phí máy");
  box(s, 0.62, 1.35, 12.06, 1.0, "Chỉ dùng split leave-combo",
    "Tập test chứa những cặp (A, B) mà train chưa từng thấy ở bất kỳ cell line nào, nhưng A và B vẫn xuất hiện với thuốc khác.\nĐây là split sát nhất với câu hỏi \"lời giải thích có thuộc về cặp không\". Viết test tự động: giao giữa tập cặp của train và test phải rỗng.", "compute", { ts: 14, bs: 11.5 });

  const rows = [
    [TH("Thành phần"), TH("Lựa chọn")],
    ["Loss", "Cross-entropy có trọng số lớp (1 / tần suất)"],
    ["Optimizer", "AdamW, lr 1e-3, weight decay 1e-4; dò lr trong {3e-4, 1e-3, 3e-3} trên val"],
    ["Batch", "256 bộ ba"],
    ["Early stopping", "theo QWK trên val, chờ 10 epoch"],
    ["Lặp", "5 seed × 5 fold cho kết quả chính"],
    ["Metric dự đoán", "QWK, macro-F1, F1 từng lớp, polar error (syn ↔ ant)"],
  ];
  table(s, rows, { x: 0.62, y: 2.6, w: 7.5, colW: [2.2, 5.3], rowH: 0.42, fontSize: 10.5 });

  box(s, 8.4, 2.6, 4.28, 1.4, "Chi phí máy", "1 kiến trúc × 4 điều kiện mạng × 25 (seed × fold)\n= 100 lần train GNN + 50 lần baseline", "data", { ts: 13, bs: 10.5 });
  stat(s, 8.4, 4.1, 4.28, "≈ 5 giờ", "tổng thời gian GPU — chạy qua đêm là xong", THEME.colors.accent5);
  caption(s, 8.4, 5.85, 4.28, "Bản 1 cần khoảng 900 lần train, tức 30–45 giờ.", { fontSize: 11 });
  caption(s, 0.62, 5.9, 7.5, "Mỗi lần chạy lưu config.json (seed, fold, split, mạng, ngưỡng, loại điểm) cạnh metrics.json. Bảng trong luận văn dựng bằng script đọc các file này, không chép tay.", { fontSize: 11 });
}

pres.addSection({ title: "8. Kết quả và lộ trình" });

// 25 — hai ket cuc
{
  const s = S("CONTENT", "8. Kết quả và lộ trình", "Hai kết cục, cả hai đều đăng được");
  box(s, 0.62, 1.4, 5.9, 0.75, "Kết cục 1 — bài phương pháp + benchmark", null, "compute", { ts: 15 });
  bullets(s, [
    "Lời giải thích cấp tương tác trung thực với mô hình",
    "Đổi khi xáo mạng — vượt null xáo₁ vs xáo₂",
    "Đặc hiệu theo cặp — vượt null đường ngắn nhất",
    { t: "→ Có một cách giải thích đáng tin, kèm giao thức kiểm định có hiệu chỉnh null", bold: true, b: false },
  ], { x: 0.75, y: 2.3, w: 5.65, h: 2.4, fontSize: 12.5 });

  box(s, 6.78, 1.4, 5.9, 0.75, "Kết cục 2 — bài phản biện", null, "out", { ts: 15 });
  bullets(s, [
    "Lời giải thích vẫn y nguyên trên mạng xáo",
    "Hoặc không đặc hiệu theo cặp",
    "Hiệu so với null gần 0 ở mọi chỉ số",
    { t: "→ Các \"đường dẫn cơ chế\" đã công bố có thể là sản phẩm của việc nhớ danh tính. Cùng dòng với One-hot news.", bold: true, b: false },
  ], { x: 6.91, y: 2.3, w: 5.65, h: 2.4, fontSize: 12.5 });

  box(s, 0.62, 4.9, 12.06, 1.0, "Phần dễ sai là đọc kết quả",
    "Phải đủ seed, đủ fold, đủ null thì kết cục nào cũng mới đứng được. Khoảng tin cậy lấy từ 5 seed × 5 fold.", "null_", { ts: 14, bs: 11.5 });
  caption(s, 0.62, 6.1, 12.06, "Null quá sát kết quả thật KHÔNG phải lỗi — đó là kết quả. Tăng số seed để biết hiệu có khác 0 có ý nghĩa không.", { fontSize: 11.5 });
}

// 26 — dong gop
{
  const s = S("CONTENT", "8. Kết quả và lộ trình", "Bốn đóng góp");
  const items = [
    ["Giao thức kiểm định lời giải thích đường dẫn có hiệu chỉnh null", "Không cần đáp án, chạy hoàn toàn trên dữ liệu đã công bố"],
    ["Toán tử giải thích cấp tương tác ở mức cạnh và đường dẫn", "Dạng sai phân bậc hai kiểu Shapley interaction index. Janizek et al. 2023 đã làm ở cấp gen trên ensemble cây; chưa ai làm ở cấp cạnh cho GNN hiệp đồng"],
    ["Chỉ số partner-specificity có hiệu chỉnh baseline", "Trừ specificity của explainer đường ngắn nhất, nên con số đọc được"],
    ["Kết quả trên O'Neil, kèm code và hạ tầng công khai", "Repo công khai ngay từ đầu, không đợi đến lúc nộp bài"],
  ];
  items.forEach(([t, d], i) => {
    const y = 1.45 + i * 1.3;
    s.addShape(pres.shapes.OVAL, { x: 0.62, y: y + 0.18, w: 0.55, h: 0.55, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: oid("n") });
    s.addText(String(i + 1), { x: 0.62, y: y + 0.18, w: 0.55, h: 0.55, isTextBox: true, margin: 0, fontSize: 16, bold: true, color: C.background1, align: "center", valign: "middle", objectName: oid("nt") });
    s.addText([
      { text: t, options: { bold: true, fontSize: 14, color: C.text1, breakLine: true } },
      { text: d, options: { fontSize: 11.5, color: C.accent2 } },
    ], { x: 1.4, y, w: 11.3, h: 1.15, isTextBox: true, margin: 0, valign: "middle", objectName: oid("cl") });
  });
}

// 27 — pham vi
{
  const s = S("CONTENT", "8. Kết quả và lộ trình", "Phạm vi: cái gì bị cắt, và khi nào thêm lại");
  const rows = [
    [TH(""), TH("Bản 1"), TH("Bản 2 — làm trong luận văn")],
    ["Kiến trúc trong khối A", "GCN, GAT, GSAT-style", { text: "GCN (1 mô hình)", options: { bold: true } }],
    ["Explainer", "4 explainer, mỗi cái 3 cấp", { text: "edge-IG, 3 cấp", options: { bold: true } }],
    ["Mạng", "STRING và KEGG, 4 biến thể", { text: "STRING; thật, xáo₁, xáo₂, m=0", options: { bold: true } }],
    ["Split", "leave-combo, leave-drug, leave-cell", { text: "leave-combo", options: { bold: true } }],
    ["Dữ liệu", "O'Neil, ALMANAC, DrugComb", { text: "O'Neil", options: { bold: true } }],
    ["Null", "không có", { text: "mọi chỉ số", options: { bold: true, color: THEME.colors.accent5 } }],
    ["KEGG", "vừa làm mạng vừa chấm điểm", { text: "chỉ chấm điểm", options: { bold: true, color: THEME.colors.accent5 } }],
    ["Số lần train", "900 nếu đủ mở rộng", { text: "100", options: { bold: true } }],
  ];
  table(s, rows, { x: 0.62, y: 1.35, w: 12.06, colW: [3.2, 4.4, 4.46], rowH: 0.41, fontSize: 10.5 });

  box(s, 0.62, 5.45, 12.06, 1.15, "Cắt không phải là bỏ",
    "Mọi thứ bị cắt đều ghi vào chương cuối như hướng phát triển, kèm điều kiện để thêm lại.\nThứ tự ưu tiên sau bảo vệ: RQ3 và nhiều dữ liệu hơn → benchmark explainer và kiến trúc → kiểm chứng sinh học sâu.", "pale", { ts: 14, bs: 11.5 });
}

// 28 — lo trinh
{
  const s = S("CONTENT", "8. Kết quả và lộ trình", "Lộ trình 12 tháng và ba mốc ra quyết định");
  const ms = [
    ["1–3", "Học nền, dựng hạ tầng: dữ liệu, GCN có mask, baseline, rewire, test", "Gate 1", C.accent1],
    ["4–5", "edge-IG 3 cấp, trích đường dẫn, module null, điều kiện tiên quyết và RQ1", "Gate 2", C.accent1],
    ["6–7", "partner-specificity và RQ2, chạy đủ 5 seed × 5 fold, bảng độ nhạy", "Gate 3", C.accent1],
    ["8–10", "Viết và nộp MỘT bài journal. Case study 2–3 cặp đối chứng dương", "Bài nộp", THEME.colors.accent5],
    ["11–12", "Viết luận văn", "Bảo vệ", THEME.colors.accent4],
  ];
  ms.forEach(([m, w, g, col], i) => {
    const y = 1.4 + i * 0.75;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.62, y, w: 1.15, h: 0.62, rectRadius: 0.05, fill: { color: col }, line: { color: col }, objectName: oid("m") });
    s.addText(m, { x: 0.62, y, w: 1.15, h: 0.62, isTextBox: true, margin: 0, fontSize: 13, bold: true, color: "FFFFFF", align: "center", valign: "middle", objectName: oid("mt") });
    s.addText(w, { x: 1.95, y, w: 8.6, h: 0.62, isTextBox: true, margin: 0, fontSize: 12, color: C.text1, valign: "middle", objectName: oid("mw") });
    s.addText(g, { x: 10.7, y, w: 1.98, h: 0.62, isTextBox: true, margin: 0, fontSize: 12, bold: true, color: col, align: "right", valign: "middle", objectName: oid("mg") });
  });

  const rows = [
    [TH("Gate"), TH("Điều kiện"), TH("Nếu không qua")],
    ["1 — cuối tháng 3", "Dữ liệu xong, đủ lớp syn và ant, pipeline chạy hết một vòng", "Đổi ngưỡng; vẫn thiếu thì gộp ALMANAC"],
    ["2 — cuối tháng 5", "Có bảng điều kiện tiên quyết và bảng RQ1 ĐẦY ĐỦ NULL", "Bổ sung null trước khi đi tiếp, đừng viết bài với con số trần"],
    ["3 — cuối tháng 7", "Có bảng RQ2, biết kết cục là phương pháp hay phản biện", "Chốt theo kết cục đang có, ngừng thử thêm kiến trúc"],
  ];
  table(s, rows, { x: 0.62, y: 5.25, w: 12.06, colW: [2.3, 5.4, 4.36], rowH: 0.42, fontSize: 10.5 });
}

// 29 — rui ro
{
  const s = S("CONTENT", "8. Kết quả và lộ trình", "Rủi ro và cách xử lý");
  const rows = [
    [TH("Rủi ro"), TH("Dấu hiệu sớm"), TH("Xử lý")],
    ["Mô hình không dùng mạng", "network share gần 0; m=0 ngang m=1", "Thêm lớp GCN, kiểm tra lại khoảng cách giữa đích. Vẫn vậy thì đây là kết cục phản biện"],
    ["Hiệu năng thấp vì bỏ embedding thuốc", "QWK kém hơn các bài đã công bố", "Không sao, luận văn không so hiệu năng. Báo cáo rõ và chạy thêm bản có embedding"],
    ["Null quá sát kết quả thật", "hiệu gần 0 ở mọi chỉ số", "Đó là kết quả, không phải lỗi. Tăng số seed"],
    ["Đích A và đích B cách nhau quá xa", "phân bố khoảng cách lệch phải", "Tăng số lớp GCN hoặc nới bán kính lọc lên 3 bước"],
    ["Ít cặp đối chứng dương trong O'Neil", "dưới 2 cặp qua quy tắc chọn", "Case study thành phân tích định tính một cặp, nói rõ giới hạn"],
    ["Nhãn nhiễu do loại điểm", "nhãn đổi nhiều giữa Loewe và Bliss", "Đã có bảng độ nhạy; báo cả hai"],
  ];
  table(s, rows, { x: 0.62, y: 1.35, w: 12.06, colW: [3.4, 3.4, 5.26], rowH: 0.6, fontSize: 10.5 });

  box(s, 0.62, 5.5, 12.06, 1.1, "Câu hỏi hội đồng chắc chắn sẽ hỏi: \"làm sao biết lời giải thích đúng?\"",
    "Trả lời bằng giới hạn đã đặt từ đầu: luận văn chỉ khẳng định trung thực, phụ thuộc mạng thật, và đặc hiệu theo cặp — mỗi cái vượt null tương ứng. Không bao giờ khẳng định tìm đúng cơ chế.", "null_", { ts: 13.5, bs: 11.5 });
}

pres.addSection({ title: "Kết" });

// 30 — tai lieu
{
  const s = S("CONTENT", "Kết", "Năm tài liệu không thể bỏ qua");
  const items = [
    ["Tasnina N., Haghani M., Murali T.M.  SynVerse", "Brief Bioinform 2025, bbaf676", "Lý do có luận văn này: xáo mạng giữ bậc gần như không làm giảm PCC của 16 mô hình"],
    ["Çandır E.B. et al.  One-hot news", "Bioinformatics 2026, btag040", "Mẫu để viết một bài phản biện: attribution chỉ tìm lại đặc trưng thật với Jaccard 0,2–0,4"],
    ["Faber L., Moghaddam A.K., Wattenhofer R.", "KDD 2021", "Vì sao phải kiểm tra mô hình trước khi trách explainer"],
    ["Sundararajan M., Taly A., Yan Q.  Integrated Gradients", "ICML 2017", "Completeness — nền của network share"],
    ["Grabisch M., Roubens M.  Shapley interaction index", "1999", "Nền của cấp (iii)"],
  ];
  items.forEach(([t, v, d], i) => {
    const y = 1.4 + i * 1.08;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.62, y: y + 0.05, w: 0.055, h: 0.85, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: oid("bar") });
    s.addText([
      { text: t + "   ", options: { bold: true, fontSize: 12.5, color: C.text1 } },
      { text: v, options: { fontSize: 11, italic: true, color: C.accent1, breakLine: true } },
      { text: d, options: { fontSize: 11, color: C.accent2 } },
    ], { x: 0.88, y, w: 11.8, h: 0.95, isTextBox: true, margin: 0, valign: "middle", objectName: oid("ref") });
  });
}

// 31 — ket
{
  const s = S("DARK_END", "Kết", "Luận văn hỏi một câu chưa ai hỏi cho đường dẫn");
  s.addText([
    { text: "Đường dẫn mà GNN XAI in ra có thật sự đến từ mạng sinh học, và có thuộc về cặp thuốc không?", options: { fontSize: 16, color: "FFFFFF", breakLine: true, paraSpaceAfter: 14 } },
    { text: "Một kiến trúc · một explainer ba cấp · một bộ dữ liệu · bốn điều kiện mạng · 100 lần train ≈ 5 giờ máy", options: { fontSize: 13, color: THEME.colors.accent1, breakLine: true, paraSpaceAfter: 14 } },
    { text: "Và mọi chỉ số đều trừ null.", options: { fontSize: 15, bold: true, color: THEME.colors.accent3, breakLine: true, paraSpaceAfter: 14 } },
    { text: "Cảm ơn thầy cô đã lắng nghe.", options: { fontSize: 13, color: "FFFFFF" } },
  ], { placeholder: "body" });
}

(async () => {
  const out = "C:/HUST/Master_thesis/reports/de_cuong_de_xuat_1.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("ok:", out);
})();
