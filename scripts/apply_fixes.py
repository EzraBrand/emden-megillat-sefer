"""Apply data/fixes.json to the split OCR and write the checked text.
  py -3.13 scripts/apply_fixes.py FIRST LAST
Fixes: data/fixes.json plus data/fixes_parts/*.json (same format, one file per page range).
Reads data/body/sNNN.txt + data/notes_kahana/sNNN.txt, writes data/text/sNNN.he.txt (main text) and
data/text/sNNN.notes.txt (Kahana's footnotes). Kahana's footnote calls "א(" are written as "[א]".
Reports fixes whose 'old' string was not found (so a stale fix is never silent)."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
FIX = json.loads((ROOT / "data" / "fixes.json").read_text(encoding="utf-8"))
# per-range fix files written by parallel workers (data/fixes_parts/sAAA-BBB.json) add to / override fixes.json
for _p in sorted((ROOT / "data" / "fixes_parts").glob("*.json")):
    FIX.update(json.loads(_p.read_text(encoding="utf-8")))
OUT = ROOT / "data" / "text"
OUT.mkdir(parents=True, exist_ok=True)


GLUED = re.compile(r"(?<=[א-ת])([א-ט])\((?=[,.;:\s]|$)", re.M)


def glued_calls(t):
    """A footnote call glued to the end of a word: ז"קד( -> ז"ק [ד]. Kraken mirrors parentheses, so in its text an
    opening bracket is ")" and a closing one "(". A "(" that closes an open ")" on the same line is a bracket, not a
    call (רזה( closing "(…רזה)" stays a word)."""
    out, pos = [], 0
    for line in t.split("\n"):
        depth, res, i = 0, [], 0
        for m in GLUED.finditer(line):
            seg = line[i:m.start()]
            depth = max(0, depth + seg.count(")") - seg.count("("))
            res.append(seg)
            if depth > 0:          # closes a bracket opened earlier on this line
                res.append(m.group(0))
                depth -= 1
            else:
                res.append(f" [{m.group(1)}]")
            i = m.end()
        res.append(line[i:])
        out.append("".join(res))
    return "\n".join(out)


def clean(t):
    # footnote call / label: a letter א-ט (Kraken may add a vowel sign) + "(", standing alone, or glued to the
    # end of a word (ז"קד( = ז"ק + call ד). Not after a gershayim/geresh: ע"ב( closes a page reference.
    t = re.sub(r"(?<![א-ת\"'])([א-ט])[ְ-ׇ]?\(", r"[\1]", t)
    t = glued_calls(t)
    t = t.replace(")", "\u0000").replace("(", ")").replace("\u0000", "(")  # Kraken mirrors parentheses
    t = re.sub(r"\[([א-ט])\)", r"[\1]", t)
    return t


def main(a, b):
    for n in range(a, b + 1):
        f = FIX.get(str(n), {})
        if f.get("manual"):  # transcribed by hand (typed inserts, blank pages): data/text/sNNN.he.txt is the master
            continue
        if not (ROOT / "data" / "body" / f"s{n:03d}.txt").exists():  # blank page, never split
            continue
        body = (ROOT / "data" / "body" / f"s{n:03d}.txt").read_text(encoding="utf-8")
        notes = (ROOT / "data" / "notes_kahana" / f"s{n:03d}.txt").read_text(encoding="utf-8")
        for line in f.get("move_to_notes", []):
            if line in body:
                body = body.replace(line + "\n", "").replace(line, "")
                notes = line + "\n" + notes
            else:
                print(f"s{n:03d} move_to_notes not found: {line[:40]}")
        for old, new in f.get("body", []):
            if old in body:
                body = body.replace(old, new)
            else:
                print(f"s{n:03d} body fix not found: {old[:40]!r}")
        for old, new in f.get("notes", []):
            if old in notes:
                notes = notes.replace(old, new)
            else:
                print(f"s{n:03d} notes fix not found: {old[:40]!r}")
        (OUT / f"s{n:03d}.he.txt").write_text(clean(body).strip() + "\n", encoding="utf-8")
        (OUT / f"s{n:03d}.notes.txt").write_text(clean(notes).strip() + "\n", encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
