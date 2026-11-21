"""Render a scan page (or part of it) as PNG for reading.
  py -3.13 scripts/render_view.py SCAN [--dpi 220] [--box X0 Y0 X1 Y1] [--name SUFFIX]
--box takes fractions of the page (0-1), e.g. "--box 0 0 1 0.5" = top half, "--box 0.75 0 1 0.35" = right margin, top.
Writes data/view/sNNN_SUFFIX.png and prints the path. Defaults: whole page at 110 dpi (suffix "full").
Tips: read the text in halves at 220 dpi (top: 0 0 1 0.52, bottom: 0 0.48 1 1). The handwritten notes are in the
RIGHT margin; read them at 300-400 dpi with a box that also takes in the adjacent printed words."""
import argparse
import sys
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("scan", type=int)
ap.add_argument("--dpi", type=int, default=None)
ap.add_argument("--box", type=float, nargs=4, default=None)
ap.add_argument("--name", default=None)
a = ap.parse_args()
doc = pymupdf.open(ROOT / "kahana_1896_hb37017.pdf")
page = doc[a.scan - 1]
r = page.rect
clip = None
if a.box:
    x0, y0, x1, y1 = a.box
    clip = pymupdf.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
dpi = a.dpi or (110 if not a.box else 220)
name = a.name or ("full" if not a.box else "crop")
out = ROOT / "data" / "view" / f"s{a.scan:03d}_{name}.png"
out.parent.mkdir(parents=True, exist_ok=True)
page.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csGRAY).save(out)
print(out)
