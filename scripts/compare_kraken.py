"""Word-level comparison of Kraken OCR (data/kraken/sNNN.txt) with the current checked text (data/text/sNNN.he.txt +
.notes.txt). Lists short replacements (Kraken | text). Use it to check a hand transcription against Kraken.
  py -3.13 scripts/compare_kraken.py FIRST LAST [-v]"""
import sys, re, difflib
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\Users\ezrab\Ezra Brandt\Claude\emden-megillat-sefer\data")
def words(t):
    t = re.sub(r"[^\u05d0-\u05ea\s]", " ", t)
    return t.split()
for n in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    k, h = R / "kraken" / f"s{n:03d}.txt", R / "text" / f"s{n:03d}.he.txt"
    if not (k.exists() and h.exists()) or not h.read_text(encoding="utf-8").strip():
        continue
    kw = words(k.read_text(encoding="utf-8"))
    hw = words(h.read_text(encoding="utf-8") + " " + (R / "text" / f"s{n:03d}.notes.txt").read_text(encoding="utf-8"))
    sm = difflib.SequenceMatcher(None, kw, hw, autojunk=False)
    diffs = [(kw[a1:a2], hw[b1:b2]) for op, a1, a2, b1, b2 in sm.get_opcodes() if op == "replace" and a2 - a1 <= 2 and b2 - b1 <= 2]
    print(f"s{n}: kraken {len(kw)} words, text {len(hw)}, ratio {sm.ratio():.3f}, small replaces {len(diffs)}")
    if "-v" in sys.argv:
        for a, b in diffs[:80]:
            print("   K:", " ".join(a), "| T:", " ".join(b))
