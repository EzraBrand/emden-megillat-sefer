"""Find handwritten notes in the margins of the scan: report ink blobs outside the printed text block.
  py -3.13 scripts/margin_ink.py FIRST LAST [--crops]
For each scan page, renders at 150 dpi, finds the text block from the PDF text layer, and reports vertical bands of
ink in the right and left margins (as fraction of page height). With --crops, writes data/scholem/cropNNN_k.png
(margin band plus the adjacent text, 2x) for each band, for reading."""
import sys
from pathlib import Path

import pymupdf
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "kahana_1896_hb37017.pdf"
OUT = ROOT / "data" / "scholem"


def bands(rows, gap=6):
    out, start, prev = [], None, None
    for y in rows:
        if start is None:
            start = prev = y
        elif y - prev > gap:
            out.append((start, prev))
            start = y
        prev = y
    if start is not None:
        out.append((start, prev))
    return out


def main(a, b, crops):
    d = pymupdf.open(PDF)
    for n in range(a, b + 1):
        p = d[n - 1]
        bl = [x for x in p.get_text("blocks") if x[4].strip()]
        if not bl:
            print(f"s{n:03d}: no text layer")
            continue
        x0, x1 = min(x[0] for x in bl), max(x[2] for x in bl)
        s = 150 / 72
        pix = p.get_pixmap(dpi=150, colorspace=pymupdf.csGRAY)
        im = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        W, H = im.size
        px = im.load()
        found = []
        for side, (ca, cb) in {"R": (int(x1 * s) + 6, int(W * 0.97)), "L": (int(W * 0.03), int(x0 * s) - 6)}.items():
            if cb - ca < 8:
                continue
            rows = []
            for y in range(int(H * 0.04), int(H * 0.96)):
                dark = sum(1 for x in range(ca, cb) if px[x, y] < 110)
                if dark >= 2:
                    rows.append(y)
            for (ya, yb) in bands(rows):
                if yb - ya < 4:
                    continue
                # skip long thin vertical rules (scan edge / binding)
                cols = [x for x in range(ca, cb) if any(px[x, y] < 110 for y in range(ya, yb + 1))]
                if cols and max(cols) - min(cols) < 6 and yb - ya > 40:
                    continue
                found.append((side, ya / H, yb / H))
                if crops:
                    big = p.get_pixmap(dpi=400)
                    bim = Image.frombytes("RGB", (big.width, big.height), big.samples)
                    k = 400 / 150
                    if side == "R":
                        box = (int((x1 * s - 220) * k), int((ya - 14) * k), big.width, int((yb + 14) * k))
                    else:
                        box = (0, int((ya - 14) * k), int((x0 * s + 220) * k), int((yb + 14) * k))
                    bim.crop(box).save(OUT / f"crop{n:03d}_{len(found)}.png")
        desc = ", ".join(f"{sd} {ya:.2f}-{yb:.2f}" for sd, ya, yb in found) or "-"
        print(f"s{n:03d}: {desc}")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), "--crops" in sys.argv)
