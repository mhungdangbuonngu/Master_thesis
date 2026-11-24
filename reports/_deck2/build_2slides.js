// Hai slide: (1) nen tang hiep dong thuoc, (2) tong quan du an SynGT
// Dung lai theme cua de_cuong_de_xuat_1.pptx (build.js)
const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/effdbcd2-bb45-40b7-bc24-4e93d3730cd1_165f13a5-ead1-4f78-b896-cd2077ad7dad/pptx/scripts/apply_theme.js");

const THEME = {
  name: "Ocean Gradient",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "21295C", lt1: "FFFFFF", dk2: "065A82", lt2: "EEF3F7",
    accent1: "1C7293", accent2: "065A82", accent3: "D79B00", accent4: "B85450",
    accent5: "5B8C5A", accent6: "7B5EA7", hlink: "1C7293", folHlink: "7B5EA7",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Luan van thac si";
pres.company = "Dai hoc Bach khoa Ha Noi";
pres.title = "Nen tang hiep dong thuoc va tong quan du an SynGT";
const C = pres.SchemeColor;

const W = 13.3;
const FOOT = "Luận văn thạc sĩ · Đại học Bách Khoa Hà Nội";

pres.defineSlideMaster({
  title: "LIGHT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.52, y: 0.32, w: 12.3, h: 0.72, fontSize: 26, bold: true, color: C.text1, valign: "middle", align: "left" }, text: " " } },
    { text: { text: FOOT, options: { x: 0.52, y: 6.95, w: 10.6, h: 0.32, fontSize: 9, color: C.accent1, italic: true, isTextBox: true, margin: 0 } } },
    { rect: { x: 0.52, y: 6.9, w: 12.3, h: 0.015, fill: { color: C.background2 } } },
    { slideNumber: { x: 12.4, y: 6.95, w: 0.42, h: 0.32, fontSize: 10, color: C.accent1, align: "right" } },
  ],
  slideNumber: { x: 12.4, y: 6.95 },
});

let N = 0;
const oid = (p) => `${p}-${++N}`;

// the: o bo tron nhat, so trong vong tron mau
function card(slide, x, y, w, h, num, head, items, opt = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.05,
    fill: { color: opt.fill || THEME.colors.lt2 },
    line: { color: opt.line || THEME.colors.lt2, width: 1 },
    objectName: oid("card"),
  });
  const cd = 0.38;
  slide.addShape(pres.shapes.OVAL, {
    x: x + 0.18, y: y + 0.13, w: cd, h: cd,
    fill: { color: opt.accent || C.accent1 }, line: { color: opt.accent || C.accent1 },
    objectName: oid("dot"),
  });
  slide.addText(num, {
    x: x + 0.18, y: y + 0.13, w: cd, h: cd, isTextBox: true, margin: 0,
    fontSize: 11.5, bold: true, color: C.background1, align: "center", valign: "middle",
    objectName: oid("dott"),
  });
  slide.addText(head, {
    x: x + 0.68, y: y + 0.12, w: w - 0.86, h: 0.42, isTextBox: true, margin: 0,
    fontSize: opt.hs || 13, bold: true, color: THEME.colors.dk2, valign: "middle",
    objectName: oid("cardh"),
  });
  const runs = items.map((it, i) => ({
    text: typeof it === "string" ? it : it.t,
    options: {
      bullet: true, breakLine: i < items.length - 1,
      paraSpaceAfter: opt.gap ?? 4,
      fontSize: opt.fontSize ?? 11,
      bold: typeof it === "object" && it.bold === true,
      color: C.text1,
    },
  }));
  slide.addText(runs, {
    x: x + 0.3, y: y + 0.56, w: w - 0.52, h: h - 0.68, isTextBox: true, margin: 0,
    valign: "top", objectName: oid("cardb"),
  });
}

function box(slide, x, y, w, h, title, body, kind, opt = {}) {
  const K = {
    data: { fill: THEME.colors.accent1, tc: "FFFFFF" },
    compute: { fill: THEME.colors.accent5, tc: "FFFFFF" },
    out: { fill: THEME.colors.accent4, tc: "FFFFFF" },
    xai: { fill: THEME.colors.accent6, tc: "FFFFFF" },
    pale: { fill: THEME.colors.lt2, tc: THEME.colors.dk1 },
  }[kind];
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: K.fill }, line: { color: K.fill, width: 1 },
    objectName: oid("box"),
  });
  const runs = [];
  if (title) runs.push({ text: title, options: { bold: true, fontSize: opt.ts ?? 10.5, color: K.tc, breakLine: !!body } });
  if (body) runs.push({ text: body, options: { fontSize: opt.bs ?? 9, color: K.tc } });
  slide.addText(runs, { x, y, w, h, isTextBox: true, align: "center", valign: "middle", margin: 2, objectName: oid("boxt") });
}

function arrow(slide, x1, y1, x2, y2) {
  slide.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
    line: { color: THEME.colors.accent2, width: 1.5, endArrowType: "triangle", beginArrowType: "none" },
    flipH: x2 < x1, flipV: y2 < y1,
    objectName: oid("arw"),
  });
}

function caption(slide, x, y, w, t, opt = {}) {
  slide.addText(t, {
    x, y, w, h: opt.h ?? 0.32, isTextBox: true, margin: 0,
    fontSize: opt.fontSize ?? 10, italic: opt.italic !== false,
    color: opt.color || THEME.colors.accent2, align: opt.align || "left", valign: "top",
    objectName: oid("cap"),
  });
}

function head(slide, x, y, w, t) {
  slide.addText(t, {
    x, y, w, h: 0.28, isTextBox: true, margin: 0, fontSize: 13, bold: true,
    color: THEME.colors.dk2, valign: "middle", objectName: oid("sec"),
  });
}

const TH = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 }, fontSize: 9 } });

// ======================= SLIDE 1 =======================
pres.addSection({ title: "Nen tang" });
const s1 = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Nen tang" });
s1.addText("Hiệp đồng thuốc: khái niệm, dữ liệu, mô hình", { placeholder: "title" });
caption(s1, 0.52, 1.02, 12.3, "Tổ hợp hai thuốc trên một dòng tế bào: mạnh hơn, yếu hơn, hay đúng bằng mức cộng tính kỳ vọng", { fontSize: 11 });

const CW = 3.9, CH = 2.45, R1 = 1.38, R2 = 3.96;
const CX = [0.52, 4.70, 8.88];

card(s1, CX[0], R1, CW, CH, "1", "Khái niệm và ba vùng nhãn", [
  "Hiệp đồng (synergy): tổ hợp vượt mức cộng tính",
  "Đối kháng (antagonism): tổ hợp kém hơn kỳ vọng",
  "Cộng tính (additive): vùng giữa, chiếm đa số dữ liệu",
  "Thang điểm liên tục, nhãn do con người cắt ngưỡng",
], { accent: THEME.colors.accent1 });

card(s1, CX[1], R1, CW, CH, "2", "Mô hình tham chiếu", [
  "Loewe additivity · Bliss independence",
  "HSA (hiệu lực thuốc đơn mạnh nhất) · ZIP",
  "Chou–Talalay: chỉ số CI, đường đồng hiệu lực",
  "Bốn điểm cho cùng một thí nghiệm, không trùng nhau",
], { accent: THEME.colors.accent2 });

card(s1, CX[2], R1, CW, CH, "3", "Dữ liệu công khai", [
  "Ma trận liều chéo: % ức chế theo từng cặp nồng độ",
  "O'Neil (Merck 2016): 38 thuốc, 39 dòng tế bào",
  "NCI-ALMANAC: 104 thuốc, 60 dòng NCI-60",
  "DrugComb v1.4 gom lại, có sẵn cả bốn điểm synergy",
  "AstraZeneca–DREAM: thi đấu dự đoán có che nhãn",
], { accent: THEME.colors.accent3, fontSize: 10.5 });

card(s1, CX[0], R2, CW, CH, "4", "Đầu vào mô hình thường dùng", [
  "Thuốc: SMILES, đồ thị phân tử, fingerprint Morgan",
  "Đích thuốc: ChEMBL mechanism, DrugBank",
  "Tế bào: biểu hiện gen CCLE/DepMap, đột biến, CNV",
  "Rút gọn về 978 gen landmark L1000",
  "Mạng: PPI STRING, pathway KEGG",
], { accent: THEME.colors.accent5, fontSize: 10.5 });

card(s1, CX[1], R2, CW, CH, "5", "Mô hình dự đoán đã công bố", [
  "DeepSynergy 2018: MLP trên fingerprint + biểu hiện",
  "DeepDDS: GCN trên đồ thị phân tử + attention",
  "DTSyn: hai transformer, token nguyên tử và token gen",
  "MatchMaker, AttenSyn, MD-Syn",
  "Cây tăng cường (XGBoost) vẫn là baseline khó vượt",
], { accent: THEME.colors.accent6, fontSize: 10.5 });

card(s1, CX[2], R2, CW, CH, "6", "Đánh giá và chỗ còn tranh luận", [
  "Chia dữ liệu: random, leave-combo, leave-drug, leave-cell, leave-tumor",
  "Chỉ số: ROC-AUC, AUPRC, QWK, lỗi nhầm cực",
  "Ngưỡng ±10 là quy ước, không phải sinh học",
  "Nhiều bài loại hẳn vùng trung tính rồi báo số cao",
  "Attention hay được trình bày như lời giải thích mà không kiểm định",
], { accent: THEME.colors.accent4, fontSize: 10.5 });

caption(s1, 0.52, 6.52, 12.3,
  "Cơ chế thường được viện dẫn: chặn song song hai nhánh của một pathway · synthetic lethality · chặn đường vòng kháng thuốc · thay đổi phơi nhiễm thuốc (dược động học)",
  { fontSize: 10 });

// ======================= SLIDE 2 =======================
pres.addSection({ title: "Du an" });
const s2 = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Du an" });
s2.addText("SynGT: bài toán, dữ liệu, kiến trúc, kỳ vọng", { placeholder: "title" });

// --- cot trai: kien truc + du lieu ---
head(s2, 0.52, 1.10, 7.3, "Kiến trúc SynGT (≈ 4,16 triệu tham số)");

box(s2, 0.52, 1.50, 2.30, 0.62, "Thuốc A, B", "SMILES → đồ thị phân tử, 78 đặc trưng nguyên tử", "data", { bs: 8 });
box(s2, 3.00, 1.50, 1.95, 0.62, "GIN 2 lớp", "d = 256 → token nguyên tử", "compute", { bs: 8 });
arrow(s2, 2.84, 1.81, 2.98, 1.81);

box(s2, 0.52, 2.30, 2.30, 0.62, "Dòng tế bào", "944 gen landmark, z-score fit trên train", "data", { bs: 8 });
box(s2, 3.00, 2.30, 1.95, 0.62, "Token gen", "node2vec trên PPI STRING + giá trị biểu hiện", "compute", { bs: 8 });
arrow(s2, 2.84, 2.61, 2.98, 2.61);

box(s2, 5.15, 1.50, 2.67, 0.62, "Transformer mịn (2 lớp, 4 đầu)", "nguyên tử ↔ gen", "compute", { bs: 8 });
box(s2, 5.15, 2.30, 2.67, 0.62, "Transformer thô (2 lớp)", "thuốc A ↔ thuốc B ↔ tế bào", "compute", { bs: 8 });
arrow(s2, 4.97, 1.81, 5.13, 1.81);
arrow(s2, 4.97, 2.61, 5.13, 2.61);

box(s2, 0.52, 3.10, 7.30, 0.52,
  "Readout: [CLS mịn ; CLS thô ; pA+pB ; |pA−pB| ; tế bào] + nhánh MLP fingerprint Morgan", "", "pale", { ts: 9.5 });
box(s2, 0.52, 3.76, 3.55, 0.56, "Đầu CORN ordinal", "ant < add < syn, thứ tự bảo đảm theo cấu trúc", "out", { bs: 8 });
box(s2, 4.27, 3.76, 3.55, 0.56, "XAI: Integrated Gradients", "gen · mảnh BRICS · nguyên tử, target z_syn − z_add", "xai", { bs: 8 });
caption(s2, 0.52, 4.38, 7.3, "Đối xứng tuyệt đối f(A,B,c) = f(B,A,c): không có embedding phân biệt A với B", { fontSize: 9 });

head(s2, 0.52, 4.72, 7.3, "Dữ liệu nào dùng cho phần nào");
s2.addTable([
  [TH("Dữ liệu"), TH("Dùng cho")],
  ["O'Neil qua DrugComb v1.4: 18.870 bộ ba, 36 thuốc, 37 dòng", "huấn luyện và đánh giá chính"],
  ["Điểm Loewe, ngưỡng ±10 (4.391 / 13.207 / 1.272)", "nhãn ba lớp"],
  ["ZIP, Bliss, HSA cùng file; ngưỡng ±5 / ±20", "kiểm độ ổn định của lời giải thích"],
  ["DepMap + 944 gen landmark L1000 · STRING v12 (≥ 700)", "đặc trưng tế bào · node2vec cho token gen"],
  ["NCI-ALMANAC: 234.333 bộ ba", "kiểm chứng ngoài, zero-shot"],
  ["KEGG pathway", "chỉ để chấm plausibility, không vào mô hình"],
], {
  x: 0.52, y: 5.02, w: 7.30, colW: [4.15, 3.15], rowH: 0.21,
  fontSize: 8.5, color: THEME.colors.dk1, fontFace: THEME.bodyFontFace,
  border: { type: "solid", color: THEME.colors.lt2, pt: 1 },
  fill: { color: "FFFFFF" }, valign: "middle", margin: 3,
  objectName: oid("tbl"),
});

// --- cot phai: bai toan, cau hoi, so sanh, ky vong ---
const RX = 8.18, RW = 4.64;

card(s2, RX, 1.06, RW, 1.08, "A", "Bài toán", [
  "Cặp thuốc + dòng tế bào → đối kháng / cộng tính / hiệp đồng",
  "Ba lớp có thứ tự: không nhị phân, không hồi quy",
], { accent: THEME.colors.accent1, fontSize: 10.5, hs: 12.5 });

card(s2, RX, 2.24, RW, 1.60, "B", "Trả lời câu hỏi gì", [
  "Bỏ vùng trung tính 0–10 thổi hiệu năng lên bao nhiêu? (DTSyn bỏ 42,6% dữ liệu)",
  "Đầu ra có thứ tự có giảm lỗi nhầm cực syn ↔ ant không?",
  "Giải thích ở cấp z_syn − z_add có trung thực, ổn định, có nghĩa sinh học không?",
], { accent: THEME.colors.accent3, fontSize: 10, hs: 12.5, gap: 3 });

card(s2, RX, 3.94, RW, 1.36, "C", "So sánh với gì", [
  "Baseline: majority, chỉ tế bào, chỉ thuốc, one-hot danh tính",
  "Bài đã công bố: DeepSynergy, DeepDDS, XGBoost fingerprint",
  "Ablation: GIN ↔ GCN, bỏ transformer, bỏ PPI, CORN ↔ CE",
], { accent: THEME.colors.accent5, fontSize: 10, hs: 12.5, gap: 3 });

card(s2, RX, 5.40, RW, 1.36, "D", "Kết quả mong đợi", [
  "QWK ba lớp vượt one-hot ở leave_combo",
  "ROC-AUC tụt 0,05–0,12 khi giữ vùng trung tính",
  "Giải thích vượt null; Jaccard@20 qua seed 0,3–0,6",
  "Đầu ra: một bài báo + luận văn sáu chương",
], { accent: THEME.colors.accent4, fontSize: 10, hs: 12.5, gap: 2 });

(async () => {
  const out = "/mnt/data/hung/Master_thesis/reports/slide_nen_tang_va_du_an.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("OK " + out);
})();
