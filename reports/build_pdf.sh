#!/usr/bin/env bash
# Dựng PDF từ reports/du_dinh_trien_khai.md
#   bash reports/build_pdf.sh
# Sơ đồ kiến trúc nằm gọn trong một trang dọc, ngay sau mục 2.
set -euo pipefail
cd "$(dirname "$0")"

SRC=du_dinh_trien_khai.md
OUT=du_dinh_trien_khai.pdf
TMP=$(mktemp -t du_dinh_XXXXXX.md)
trap 'rm -f "$TMP"' EXIT

# Thay dòng ảnh markdown bằng một trang hình riêng của LaTeX
python3 - "$SRC" "$TMP" <<'PY'
import sys, re
src, tmp = sys.argv[1], sys.argv[2]
block = r"""
\clearpage
\newgeometry{margin=1.2cm}
\thispagestyle{empty}
\null\vfill
\begin{center}
\includegraphics[width=\linewidth,height=0.9\textheight,keepaspectratio]{kien_truc_syngt.png}

\vspace{0.5cm}
\small\textbf{Hình 1.} Kiến trúc dự định xây dựng
\end{center}
\vfill
\clearpage
\restoregeometry
"""

text = open(src, encoding="utf-8").read()
text, n = re.subn(r"!\[Kiến trúc dự định xây dựng\]\(kien_truc_syngt\.png\)\{[^}]*\}",
                  lambda m: block, text)
if n != 1:
    sys.exit(f"Không tìm thấy dòng ảnh kiến trúc trong {src} (khớp {n} lần)")
open(tmp, "w", encoding="utf-8").write(text)
PY

pandoc "$TMP" -o "$OUT" \
  --pdf-engine=xelatex \
  -V mainfont="DejaVu Serif" \
  -V sansfont="DejaVu Sans" \
  -V monofont="Noto Sans Mono" \
  -V geometry:"a4paper,margin=2.2cm" \
  -V fontsize=11pt \
  -V linkcolor=blue \
  -V header-includes='\usepackage{graphicx}' \
  --toc --toc-depth=2 \
  --resource-path=.

echo "Xong: reports/$OUT"
