"""Kraken OCR of Kahana 1896 scan pages (PP-OCRv6 medium), resumable.
  py -3.13 scripts/ocr_kraken.py FIRST LAST [WORKERS]
Writes data/raw/sNNN.png (600 dpi grey), data/kraken/sNNN.vis.txt (Kraken visual order) and
data/kraken/sNNN.txt (logical order). Skips pages that already have sNNN.txt."""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "kahana_1896_hb37017.pdf"
KRAKEN = Path(r"C:\Users\ezrab\Ezra Brandt\Claude\syriac-ocr\.venv\Scripts\kraken.exe")
MODEL = Path(r"C:\Users\ezrab\AppData\Local\htrmopo\htrmopo\1980fa54-b49e-5256-95b6-928290bc48f8\medium.safetensors")
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "kraken"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")


def one(n: int) -> str:
    txt = OUT / f"s{n:03d}.txt"
    if txt.exists():
        return f"s{n:03d} skip"
    img, vis = RAW / f"s{n:03d}.png", OUT / f"s{n:03d}.vis.txt"
    if not img.exists():
        d = pymupdf.open(PDF)
        d[n - 1].get_pixmap(dpi=600, colorspace=pymupdf.csGRAY).save(img)
    t = time.time()
    r = subprocess.run([str(KRAKEN), "-i", str(img), str(vis), "segment", "-bl", "ocr", "-m", str(MODEL)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if r.returncode or not vis.exists():
        return f"s{n:03d} FAILED: {r.stderr[-400:]}"
    lines = vis.read_text(encoding="utf-8").splitlines()
    txt.write_text("\n".join(l[::-1] for l in lines) + "\n", encoding="utf-8")
    return f"s{n:03d} ok {time.time() - t:.0f}s {len(lines)} lines"


if __name__ == "__main__":
    a, b = int(sys.argv[1]), int(sys.argv[2])
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    pages = list(range(a, b + 1))
    done = 0
    with ThreadPoolExecutor(w) as ex:
        for msg in ex.map(one, pages):
            done += 1
            print(f"{done}/{len(pages)} {msg}", flush=True)
    print("finished", flush=True)
