"""Dung slide tren dung file template HUST (python-pptx).

Khac voi ban truoc (pptxgenjs + anh nen mo phong): o day slide duoc them vao
chinh file template, nen ke thua kho slide 13,333 x 7,5 inch, slide master,
slide layout, logo truong va so trang cua truong.
"""
import copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

TEMPLATE = "Copy of HUST_PPT_template_2022_Blue_16x9.pptx"

# bang mau lay tu template
NAVY = RGBColor(0x00, 0x37, 0x6F)
RED = RGBColor(0xC0, 0x00, 0x00)
BLUE = RGBColor(0x1C, 0x6E, 0xA4)
GREEN = RGBColor(0x15, 0x7B, 0x6E)
AMBER = RGBColor(0xB0, 0x7A, 0x00)
SLATE = RGBColor(0x5A, 0x6B, 0x7B)
PALE = RGBColor(0xED, 0xF1, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x1A, 0x1A, 0x1A)

FONT = "Arial"
TITLE_SIZE = 28

# vung an toan: thanh navy het o y=0.66, chan trang bat dau o y=6.95
ML, CW = 0.37, 12.59
Y0, Y1 = 1.15, 6.72

LAYOUT_COVER = 0      # nen toi, logo HUST lon
LAYOUT_TITLE = 2      # hoa tiet cham tron, dung cho slide bia phu
LAYOUT_CONTENT = 5    # thanh navy + duong ke do + logo + so trang


def new_deck():
    """Mo template roi xoa sach 25 slide mau."""
    prs = Presentation(TEMPLATE)
    ids = prs.slides._sldIdLst
    for sld in list(ids):
        prs.part.drop_rel(sld.get(qn("r:id")))
        ids.remove(sld)
    return prs


def _drop(shape):
    shape._element.getparent().remove(shape._element)


def _flat(sp):
    """Bo bong do va vien theo theme ma python-pptx gan mac dinh cho autoshape."""
    el = sp._element
    for st in el.findall(qn("p:style")):
        el.remove(st)
    spPr = el.spPr
    for eff in spPr.findall(qn("a:effectLst")):
        spPr.remove(eff)
    spPr.append(spPr.makeelement(qn("a:effectLst"), {}))


def _style(run, size=14, bold=False, italic=False, color=INK):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = FONT
    run.font.color.rgb = color


def _bullet(p, on=True, marL=0.22):
    """python-pptx khong co API cho dau chaám dau dong, phai sua thang XML."""
    pPr = p._p.get_or_add_pPr()
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    if on:
        pPr.set("marL", str(int(marL * 914400)))
        pPr.set("indent", str(-int(marL * 914400)))
        bu = pPr.makeelement(qn("a:buChar"), {"char": "•"})
        pPr.append(bu)
    else:
        pPr.set("marL", "0")
        pPr.set("indent", "0")
        pPr.append(pPr.makeelement(qn("a:buNone"), {}))


def _space(p, before=0, after=4):
    pPr = p._p.get_or_add_pPr()
    pPr.set("spcBef", "")
    for tag, val in (("a:spcBef", before), ("a:spcAft", after)):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
        el = pPr.makeelement(qn(tag), {})
        pts = el.makeelement(qn("a:spcPts"), {"val": str(int(val * 100))})
        el.append(pts)
        pPr.append(el)
    if "spcBef" in pPr.attrib:
        del pPr.attrib["spcBef"]


def textbox(slide, x, y, w, h, anchor="t"):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE}[anchor]
    return tb


def para(tf, first, text, size=14, bold=False, italic=False, color=INK,
         bullet=False, after=6, align=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    r = p.add_run()
    r.text = text
    _style(r, size, bold, italic, color)
    _bullet(p, bullet)
    _space(p, 0, after)
    if align:
        p.alignment = align
    return p


def lines(slide, x, y, w, h, items, size=14, color=INK, after=7, bullet=True):
    """Mot khoi gach dau dong. items: chuoi, hoac (chuoi, dict tuy chon)."""
    tf = textbox(slide, x, y, w, h).text_frame
    for i, it in enumerate(items):
        txt, opt = (it, {}) if isinstance(it, str) else it
        para(tf, i == 0, txt,
             size=opt.get("size", size), bold=opt.get("bold", False),
             italic=opt.get("italic", False), color=opt.get("color", color),
             bullet=opt.get("bullet", bullet), after=opt.get("after", after))
    return tf


def _page_no(prs, s):
    n = len(prs.slides._sldIdLst)
    tf = textbox(s, 11.9, 6.95, 1.06, 0.34, anchor="m").text_frame
    para(tf, True, str(n), size=11, color=NAVY, align=PP_ALIGN.RIGHT, after=0)


def content(prs, title, lead=None):
    """Slide noi dung: tieu de nam tren thanh navy cua template."""
    s = prs.slides.add_slide(prs.slide_layouts[LAYOUT_CONTENT])
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 0:
            ph.width, ph.height = Inches(CW), Inches(0.52)
            ph.top, ph.left = Inches(0.08), Inches(ML)
            tf = ph.text_frame
            tf.word_wrap = False
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title
            _style(r, TITLE_SIZE, True, False, WHITE)
        elif ph.placeholder_format.idx == 1:
            _drop(ph)
    _page_no(prs, s)
    s.__dict__["y"] = Y0
    if lead:
        tf = textbox(s, ML, Y0, CW, 0.3).text_frame
        para(tf, True, lead, size=13, italic=True, color=SLATE, after=0)
        s.__dict__["y"] = Y0 + 0.44
    return s


def divider(prs, label, title, note=None):
    s = prs.slides.add_slide(prs.slide_layouts[LAYOUT_CONTENT])
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 0:
            ph.width, ph.height = Inches(CW), Inches(0.52)
            ph.top, ph.left = Inches(0.08), Inches(ML)
            ph.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
            r = ph.text_frame.paragraphs[0].add_run()
            r.text = label
            _style(r, TITLE_SIZE, True, False, WHITE)
        elif ph.placeholder_format.idx == 1:
            _drop(ph)
    _page_no(prs, s)
    tf = textbox(s, ML, 2.9, CW, 1.0, anchor="m").text_frame
    para(tf, True, title, size=34, bold=True, color=NAVY, align=PP_ALIGN.CENTER, after=0)
    if note:
        tf2 = textbox(s, 2.2, 4.0, 8.93, 0.6).text_frame
        para(tf2, True, note, size=15, color=SLATE, align=PP_ALIGN.CENTER, after=0)
    return s


def cover(prs, title, sub, meta):
    """Slide bia: hoa tiet va logo cua template."""
    s = prs.slides.add_slide(prs.slide_layouts[LAYOUT_TITLE])
    s.shapes.add_picture("assets/hust_logo.png", Inches(0.42), Inches(0.36),
                         Inches(3.47), Inches(1.04))
    tf = textbox(s, 0.42, 2.25, 8.3, 1.5).text_frame
    para(tf, True, title, size=32, bold=True, color=RED, after=0)
    tf2 = textbox(s, 0.42, 3.95, 8.3, 0.7).text_frame
    para(tf2, True, sub, size=16, color=NAVY, after=0)
    tf3 = textbox(s, 0.42, 4.95, 8.3, 1.5).text_frame
    for i, t in enumerate(meta):
        para(tf3, i == 0, t, size=14, color=INK, after=9)
    return s


def box(slide, x, y, w, h, title, body=None, fill=NAVY, tc=WHITE,
        ts=15, bs=12, align=PP_ALIGN.CENTER):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = fill
    _flat(sp)
    try:
        sp.adjustments[0] = 0.08
    except Exception:
        pass
    tf = sp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, True, title, size=ts, bold=True, color=tc, align=align, after=0)
    if body:
        para(tf, False, body, size=bs, color=tc, align=align, after=0)
    return sp


def card(slide, x, y, w, h, head, items, accent=NAVY, size=14, after=8):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = PALE
    sp.line.color.rgb = PALE
    _flat(sp)
    try:
        sp.adjustments[0] = 0.06
    except Exception:
        pass
    sp.text_frame.word_wrap = True
    if head:
        tf = textbox(slide, x + 0.26, y + 0.16, w - 0.5, 0.36).text_frame
        para(tf, True, head, size=16, bold=True, color=accent, after=0)
    if items:
        lines(slide, x + 0.26, y + 0.62, w - 0.52, h - 0.78, items,
              size=size, after=after)
    return sp


def table(slide, rows, x, y, w, colw, size=13, head_size=13, rowh=0.42):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w),
                                Inches(rowh * nr)).table
    gt.first_row = True
    gt.horz_banding = False
    for i, cwid in enumerate(colw):
        gt.columns[i].width = Inches(cwid)
    for r in range(nr):
        gt.rows[r].height = Inches(rowh)
        for c in range(nc):
            cell = gt.cell(r, c)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            val = rows[r][c]
            txt, opt = (val, {}) if isinstance(val, str) else val
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = txt
            if r == 0:
                _style(run, head_size, True, False, WHITE)
                cell.fill.solid()
                cell.fill.fore_color.rgb = NAVY
            else:
                _style(run, opt.get("size", size), opt.get("bold", False),
                       False, opt.get("color", INK))
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE
            _space(p, 0, 0)
    return gt


def arrow(slide, x1, y1, x2, y2, color=SLATE):
    from pptx.enum.shapes import MSO_CONNECTOR
    cn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1),
                                    Inches(y1), Inches(x2), Inches(y2))
    cn.line.color.rgb = color
    cn.line.width = Pt(1.75)
    ln = cn.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle"})
    ln.append(tail)
    return cn


def stat(slide, x, y, w, big, label, color=RED):
    tf = textbox(slide, x, y, w, 0.8, anchor="m").text_frame
    para(tf, True, big, size=36, bold=True, color=color, align=PP_ALIGN.CENTER, after=0)
    tf2 = textbox(slide, x, y + 0.8, w, 0.8).text_frame
    para(tf2, True, label, size=13, color=INK, align=PP_ALIGN.CENTER, after=0)


def note(slide, x, y, w, text, size=12, color=SLATE):
    tf = textbox(slide, x, y, w, 0.34).text_frame
    para(tf, True, text, size=size, italic=True, color=color, after=0)


def save(prs, path):
    prs.save(path)
    print("OK " + path)
