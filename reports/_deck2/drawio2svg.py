# Chuyen file .drawio (tap con style tu viet) sang SVG.
# Chi ho tro nhung style dung trong kien_truc_de_xuat_2.drawio:
# rect / rounded / shape=note / shape=hexagon / text, canh orthogonal.
import re, sys, html
from xml.etree import ElementTree as ET

CW = 0.515  # he so rong ky tu tren fontSize, uoc luong cho Segoe UI


def parse_style(s):
    d = {}
    for part in (s or "").split(";"):
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            d[k.strip()] = v.strip()
        else:
            d[part.strip()] = "1"
    return d


def label_lines(value, width, fontsize, pad):
    """Tra ve danh sach (text, bold, italic) cho tung dong, da wrap theo chieu rong."""
    if not value:
        return []
    v = html.unescape(value)
    v = re.sub(r"<br\s*/?>", "\n", v, flags=re.I)
    out = []
    avail = max(width - 2 * pad, 20)
    maxch = max(int(avail / (CW * fontsize)), 8)
    for raw in v.split("\n"):
        bold = bool(re.search(r"<b>", raw, re.I))
        ital = bool(re.search(r"<i>", raw, re.I))
        txt = re.sub(r"<[^>]+>", "", raw).strip()
        if not txt:
            out.append(("", bold, ital))
            continue
        words, cur = txt.split(" "), ""
        for w in words:
            cand = (cur + " " + w).strip()
            if len(cand) <= maxch or not cur:
                cur = cand
            else:
                out.append((cur, bold, ital))
                cur = w
        out.append((cur, bold, ital))
    while out and out[-1][0] == "":
        out.pop()
    return out


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def shape_svg(st, x, y, w, h):
    fill = st.get("fillColor", "none")
    stroke = st.get("strokeColor", "#000000")
    if fill == "none" or st.get("shape") == "" and "text;" in str(st):
        fill = "none"
    if st.get("shape") == "note":
        f = float(st.get("size", 14))
        return (f'<path d="M{x},{y} L{x+w-f},{y} L{x+w},{y+f} L{x+w},{y+h} L{x},{y+h} Z" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>'
                f'<path d="M{x+w-f},{y} L{x+w-f},{y+f} L{x+w},{y+f}" fill="none" '
                f'stroke="{stroke}" stroke-width="1.3"/>')
    if st.get("shape") == "hexagon":
        c = h * 0.28
        return (f'<path d="M{x+c},{y} L{x+w-c},{y} L{x+w},{y+h/2} L{x+w-c},{y+h} '
                f'L{x+c},{y+h} L{x},{y+h/2} Z" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
    r = 8 if st.get("rounded") == "1" else 0
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')


def text_svg(st, x, y, w, h, value, is_text_only):
    fs = float(st.get("fontSize", 12))
    align = st.get("align", "center")
    valign = st.get("verticalAlign", "middle")
    pad = float(st.get("spacingLeft", 0)) or 10
    color = st.get("fontColor", "#1a1a1a")
    lines = label_lines(value, w, fs, pad if align == "left" else 8)
    if not lines:
        return ""
    lh = fs * 1.42
    total = len(lines) * lh
    if valign == "top":
        top = y + float(st.get("spacingTop", 0) or 6) + fs
    else:
        top = y + (h - total) / 2 + fs * 0.92
    if align == "left":
        tx, anchor = x + pad, "start"
    elif align == "right":
        tx, anchor = x + w - pad, "end"
    else:
        tx, anchor = x + w / 2, "middle"
    base_italic = st.get("fontStyle") == "2"
    parts = []
    for i, (t, b, it) in enumerate(lines):
        if not t:
            continue
        wt = ' font-weight="bold"' if b else ""
        sty = ' font-style="italic"' if (it or base_italic) else ""
        parts.append(f'<text x="{tx}" y="{top + i * lh:.1f}" text-anchor="{anchor}" '
                     f'font-family="Segoe UI, Arial, sans-serif" font-size="{fs}" '
                     f'fill="{color}"{wt}{sty}>{esc(t)}</text>')
    return "\n".join(parts)


def edge_svg(st, src, tgt, pts):
    if not src or not tgt:
        return ""
    sx, sy, sw, sh = src
    tx, ty, tw, th = tgt
    scx, scy, tcx, tcy = sx + sw / 2, sy + sh / 2, tx + tw / 2, ty + th / 2
    stroke = st.get("strokeColor", "#666666")
    dash = ' stroke-dasharray="7,5"' if st.get("dashed") == "1" else ""
    def anchor(box, pt):
        bx, by, bw, bh = box
        cx, cy = bx + bw / 2, by + bh / 2
        if abs(pt[0] - cx) * bh > abs(pt[1] - cy) * bw:
            return (bx + bw if pt[0] > cx else bx, cy)
        return (cx, by + bh if pt[1] > cy else by)

    if pts:
        p = [anchor(src, pts[0])] + pts + [anchor(tgt, pts[-1])]
        d = "M" + " L".join(f"{a:.0f},{b:.0f}" for a, b in p)
        end = p[-1]
        prev = p[-2]
    elif abs(tcy - scy) > max(sh, th) / 2:
        if tcy > scy:
            y1, y2 = sy + sh, ty
        else:
            y1, y2 = sy, ty + th
        my = (y1 + y2) / 2
        d = f"M{scx:.0f},{y1:.0f} L{scx:.0f},{my:.0f} L{tcx:.0f},{my:.0f} L{tcx:.0f},{y2:.0f}"
        end, prev = (tcx, y2), (tcx, my)
    else:
        if tcx > scx:
            x1, x2 = sx + sw, tx
        else:
            x1, x2 = sx, tx + tw
        d = f"M{x1:.0f},{scy:.0f} L{x2:.0f},{tcy:.0f}"
        end, prev = (x2, tcy), (x1, scy)
    import math
    ang = math.atan2(end[1] - prev[1], end[0] - prev[0])
    a1 = (end[0] - 11 * math.cos(ang - 0.42), end[1] - 11 * math.sin(ang - 0.42))
    a2 = (end[0] - 11 * math.cos(ang + 0.42), end[1] - 11 * math.sin(ang + 0.42))
    head = (f'<path d="M{end[0]:.0f},{end[1]:.0f} L{a1[0]:.0f},{a1[1]:.0f} '
            f'L{a2[0]:.0f},{a2[1]:.0f} Z" fill="{stroke}"/>')
    lbl = ""
    if st.get("_label"):
        mx, my = (prev[0] + end[0]) / 2, (prev[1] + end[1]) / 2 - 6
        lbl = (f'<text x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" font-family="Segoe UI, Arial" '
               f'font-size="10" fill="{stroke}">{esc(st["_label"])}</text>')
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.5"{dash}/>{head}{lbl}'


def convert(path, out_prefix):
    root = ET.parse(path).getroot()
    made = []
    for idx, dia in enumerate(root.findall("diagram"), 1):
        model = dia.find("mxGraphModel")
        W = int(model.get("pageWidth", 1169))
        H = int(model.get("pageHeight", 1654))
        geo, vcells, ecells = {}, [], []
        for c in model.find("root").findall("mxCell"):
            g = c.find("mxGeometry")
            st = parse_style(c.get("style", ""))
            if c.get("vertex") == "1" and g is not None:
                box = (float(g.get("x", 0)), float(g.get("y", 0)),
                       float(g.get("width", 10)), float(g.get("height", 10)))
                geo[c.get("id")] = box
                vcells.append((c, st, box))
            elif c.get("edge") == "1":
                pts = []
                arr = g.find("Array") if g is not None else None
                if arr is not None:
                    for p in arr.findall("mxPoint"):
                        pts.append((float(p.get("x")), float(p.get("y"))))
                st["_label"] = html.unescape(re.sub(r"<[^>]+>", "", c.get("value", "") or ""))
                ecells.append((st, c.get("source"), c.get("target"), pts))
        body = [f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
        for st, s, t, pts in ecells:
            body.append(edge_svg(st, geo.get(s), geo.get(t), pts))
        for c, st, (x, y, w, h) in vcells:
            text_only = st.get("shape") is None and "text" in (c.get("style") or "")[:5]
            if not text_only:
                body.append(shape_svg(st, x, y, w, h))
            body.append(text_svg(st, x, y, w, h, c.get("value", ""), text_only))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
               f'viewBox="0 0 {W} {H}">\n' + "\n".join(body) + "\n</svg>\n")
        name = f"{out_prefix}_{idx}.svg"
        open(name, "w", encoding="utf-8").write(svg)
        made.append(name)
    return made


if __name__ == "__main__":
    for f in convert(sys.argv[1], sys.argv[2]):
        print(f)
