"""Align Kraken OCR of Kahana 1896 pages with the Pninim (Bick 1979) text and list the differences.
  py -3.13 scripts/align_pninim.py FIRST LAST
Inputs: data/kraken/sNNN.txt, source/pninim/{פתיחה,א,...}.txt
Outputs: data/body/sNNN.txt (main text, header and footnotes split off), data/notes_kahana/sNNN.txt (Kahana's footnotes),
data/align/diffs_FIRST-LAST.tsv (one row per difference, with scan page and line), printed summary.
Spelling differences that vanish after normalisation (matres lectionis ו/י, gershayim, punctuation) are not listed."""
import csv
import difflib
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
KR, PN = ROOT / "data" / "kraken", ROOT / "source" / "pninim"
BODY, NOTES, AL = ROOT / "data" / "body", ROOT / "data" / "notes_kahana", ROOT / "data" / "align"
for d in (BODY, NOTES, AL):
    d.mkdir(parents=True, exist_ok=True)
PN_FILES = ["פתיחה", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "נספחים"]
FN_START = re.compile(r"^\s*[א-ט]\s*[\(\)]")  # Kahana footnote line: "א( ..." (Kraken renders the paren reversed)


def split_page(lines):
    """Drop the running head (first line), split body from Kahana's footnotes."""
    lines = [l for l in lines if l.strip()]
    if lines and re.search(r"מג[י]?לת\s*ספר", lines[0]):
        lines = lines[1:]
    for i, l in enumerate(lines):
        if FN_START.match(l) and i > len(lines) * 0.4:
            return lines[:i], lines[i:]
    return lines, []


FN_MARK = re.compile(r"(?<![א-ת])[א-ט]\(|(?<=[א-ת\"'])[א-ט]\((?=[,.;:\s]|$)")


def is_abbrev_of(abbr, words):
    """True if an OCR abbreviation (with " or ') is expanded in Pninim, e.g. ש"ע -> שולחן ערוך,
    לפ"ק -> לפרט קטן, ב"ד -> בית דין, הק"ה -> הקצין הפרנס (initials match, prefix letters allowed)."""
    if '"' not in abbr and "'" not in abbr and "״" not in abbr and "׳" not in abbr:
        return False
    a = re.sub(r"[^א-ת]", "", abbr).translate(str.maketrans("ךםןףץ", "כמנפצ"))
    ws = [re.sub(r"[^א-ת]", "", w).translate(str.maketrans("ךםןףץ", "כמנפצ")) for w in words]
    ws = [w for w in ws if w]
    if not ws or not a:
        return False
    if len(ws) == 1:  # single-word expansion: ס' -> ספר, ק' -> קהל, ר' -> ר׳ אליהו handled below
        return ws[0].startswith(a) or a == ws[0][:len(a)]
    init = "".join(w[0] for w in ws)
    # allow prefix letters (ב, ו, ל, ה, מ, כ, ש) glued to the first word of the expansion
    return a == init or a.endswith(init) or init.endswith(a) or a == ws[0][:len(a) - len(ws) + 1] + init[1:]


def abbrev_row(ocr_words, pn_words):
    """A replace row is only abbreviation expansion if each OCR abbreviation can eat a run of Pninim words."""
    i = 0
    for k, w in enumerate(ocr_words):
        rest = len(ocr_words) - k - 1
        for j in range(len(pn_words) - rest, i, -1):
            if (j - i == 1 and norm(w) == norm(pn_words[i])) or is_abbrev_of(w, pn_words[i:j]):
                i = j
                break
        else:
            return False
    return i == len(pn_words)


def norm(w):
    w = w.replace("״", '"').replace("׳", "'")
    w = re.sub(r"[^א-ת]", "", w)  # letters only
    w = w.translate(str.maketrans("ךםןףץ", "כמנפצ"))
    return re.sub(r"[וי]", "", w)  # ignore plene/defective spelling


def pninim_tokens():
    toks = []
    for f in PN_FILES:
        t = (PN / f"{f}.txt").read_text(encoding="utf-8")
        t = re.sub(r"(?m)^\[\^\d+\]:?\s.*$", "", t)  # Bick's footnote bodies ("[^n] text" on its own line)
        t = re.sub(r"\[\^\d+\]", "", t)
        t = re.sub(r"(?m)^%.*$", "", t)
        t = t.replace("*", "").replace("-", " ")
        toks += [(w, f) for w in t.split()]
    return toks


def main(a, b):
    ocr = []  # (word, page, line_no)
    for n in range(a, b + 1):
        lines = (KR / f"s{n:03d}.txt").read_text(encoding="utf-8").splitlines()
        body, fn = split_page(lines)
        (BODY / f"s{n:03d}.txt").write_text("\n".join(body) + "\n", encoding="utf-8")
        (NOTES / f"s{n:03d}.txt").write_text("\n".join(fn) + "\n", encoding="utf-8")
        for li, l in enumerate(body, 1):
            l = FN_MARK.sub(" ", l)  # Kahana's footnote calls "א(", also glued to a word: ז"קד(
            ocr += [(w, n, li) for w in l.replace("-", " ").split() if norm(w)]
    pn = [(w, f) for w, f in pninim_tokens() if norm(w)]
    on, pnn = [norm(w) for w, *_ in ocr], [norm(w) for w, _ in pn]
    # locate the Pninim window: best start for the first 30 OCR words
    probe = " ".join(on[:30])
    best, start = 0, 0
    for s in range(0, len(pnn) - 30):
        r = difflib.SequenceMatcher(None, probe, " ".join(pnn[s:s + 30]), autojunk=False).ratio()
        if r > best:
            best, start = r, s
        if best > 0.9:
            break
    window = pnn[start:start + int(len(on) * 1.4) + 200]
    sm = difflib.SequenceMatcher(None, on, window, autojunk=False)
    rows, same = [], 0
    last_j = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            same += i2 - i1
            last_j = j2
            continue
        pg, ln = (ocr[i1][1], ocr[i1][2]) if i1 < len(ocr) else (ocr[-1][1], ocr[-1][2])
        ow = [w for w, *_ in ocr[i1:i2]]
        pw = [w for w, _ in pn[start + j1:start + j2]]
        if tag == "replace" and abbrev_row(ow, pw):
            n_abbr = globals().setdefault("N_ABBR", [0])
            n_abbr[0] += 1
            continue
        rows.append({"scan_page": pg, "line": ln, "type": tag,
                     "kahana_ocr": " ".join(ow),
                     "pninim": " ".join(pw),
                     "pninim_file": pn[start + j1][1] if start + j1 < len(pn) else ""})
    # trailing Pninim text past the last OCR word is not a difference
    if rows and rows[-1]["type"] == "insert" and rows[-1]["kahana_ocr"] == "":
        rows.pop()
    out = AL / f"diffs_{a:03d}-{b:03d}.tsv"
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["scan_page"], delimiter="\t")
        wr.writeheader()
        wr.writerows(rows)
    print(f"Pninim window starts at token {start} (probe ratio {best:.2f}), file {pn[start][1]}")
    print(f"OCR words {len(on)}; equal {same} ({same / len(on):.1%}); abbreviation expansions skipped "
          f"{globals().get('N_ABBR', [0])[0]}; differences {len(rows)} -> {out}")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
