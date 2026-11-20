"""Build the GitHub Pages reader in docs/ from the checked Hebrew text and the English translation.
  py -3.13 scripts/build_site.py
Inputs: translation/*.md (sections '## Page N (scan M)' or '## Typed insert ... (scan M) ...'),
data/text/sMMM.he.txt + sMMM.notes.txt, data/scholem/notes_pilot.tsv (+ notes_*.tsv).
Output: docs/index.html (one page, all book pages in order, Hebrew and English side by side)."""
import csv
import html
import re
import sys
from pathlib import Path

import markdown

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)
HB = "https://hebrewbooks.org/pdfpager.aspx?req=37017&pgnum={}"
SEC = re.compile(r"^## (.+?)\s*$", re.M)


def sections():
    out = {}
    for f in sorted((ROOT / "translation").glob("*.md")):
        t = f.read_text(encoding="utf-8")
        parts = SEC.split(t)
        for title, body in zip(parts[1::2], parts[2::2]):
            m = re.search(r"\(scan (\d+)\)", title)
            if not m:
                continue
            body = body.strip().rstrip("-").strip()
            eng, _, notes = body.partition("**Kahana's notes**")
            out[int(m.group(1))] = {"title": title, "en": eng.strip(), "kahana_en": notes.strip()}
    return out


def scholem():
    rows = {}
    for f in sorted((ROOT / "data" / "scholem").glob("notes_*.tsv")):
        with f.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                rows.setdefault(int(r["scan_page"]), []).append(r)
    return rows


def hebrew(scan):
    p = ROOT / "data" / "text" / f"s{scan:03d}.he.txt"
    if not p.exists():
        return ""
    lines = [l.rstrip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    lines = [l for l in lines if not (l.startswith("[TYPED INSERT") or l.startswith("[HANDWRITTEN SHEET"))]
    text = ""
    for l in lines:
        if text.endswith("-"):
            text = text[:-1] + l
        else:
            text += (" " if text else "") + l
    text = html.escape(text)
    return re.sub(r"\[([א-ט])\]", r'<sup class="fn">\1</sup>', text)


def hebrew_notes(scan):
    p = ROOT / "data" / "text" / f"s{scan:03d}.notes.txt"
    if not p.exists():
        return ""
    t = p.read_text(encoding="utf-8").strip()
    if not t:
        return ""
    notes, cur = [], ""
    for l in t.splitlines():
        if re.match(r"^\[[א-ט]\]", l) and cur:
            notes.append(cur)
            cur = l
        else:
            cur = (cur + " " + l).strip()
    notes.append(cur)
    return "".join(f"<li>{html.escape(n)}</li>" for n in notes if n)


def md(s):
    s = s.replace("⟨S:", '<span class="sch">⟨S:').replace("⟩", "⟩</span>")
    return markdown.markdown(s, extensions=["extra"])


def main():
    secs, sch = sections(), scholem()
    toc, body = [], []
    for scan in sorted(secs):
        s = secs[scan]
        m = re.match(r"Page (\d+)", s["title"])
        label = f"p. {m.group(1)}" if m else "insert"
        anchor = f"p{m.group(1)}" if m else f"s{scan}"
        toc.append(f'<a href="#{anchor}">{label}</a>')
        sn = sch.get(scan, [])
        sch_html = ""
        if sn:
            sch_html = "<details class='schbox'><summary>Scholem's marks on this page ({})</summary><table><tr><th>Printed anchor</th><th>Mark</th><th>Reading</th><th>Certainty</th></tr>{}</table></details>".format(
                len(sn), "".join(f"<tr><td dir='rtl'>{html.escape(r['anchor_in_print'])}</td><td>{html.escape(r['mark'])}</td>"
                                 f"<td dir='rtl'>{html.escape(r['margin_text_reading'])}</td><td>{html.escape(r['certainty'])}</td></tr>" for r in sn))
        he_notes = hebrew_notes(scan)
        body.append(f"""
<section class="page" id="{anchor}">
  <header><h2>{html.escape(s['title'])}</h2>
  <a class="scan" href="{HB.format(scan)}" target="_blank" rel="noopener">scan {scan} ↗</a></header>
  <div class="cols">
    <div class="he" dir="rtl" lang="he"><p>{hebrew(scan)}</p>{f'<ol class="knotes">{he_notes}</ol>' if he_notes else ''}</div>
    <div class="en" lang="en">{md(s['en'])}{('<div class="knotes-en"><h3>Kahana' + "'" + 's notes</h3>' + md(s['kahana_en']) + '</div>') if s['kahana_en'] else ''}</div>
  </div>
  {sch_html}
</section>""")
    page = TEMPLATE.replace("{{TOC}}", " · ".join(toc)).replace("{{BODY}}", "\n".join(body))
    (DOCS / "index.html").write_text(page, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"docs/index.html: {len(secs)} sections")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Megillat Sefer Reader</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Hebrew:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#fbfaf7;--fg:#1d1c1a;--muted:#6b665e;--line:#e3dfd6;--accent:#8a3b12;--sch:#f4e7c8;--card:#fff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#17161a;--fg:#e9e6df;--muted:#a19b90;--line:#34313a;--accent:#e39a6c;--sch:#3a3220;--card:#1f1e23}}
:root[data-theme="dark"]{--bg:#17161a;--fg:#e9e6df;--muted:#a19b90;--line:#34313a;--accent:#e39a6c;--sch:#3a3220;--card:#1f1e23}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 "Noto Serif",Georgia,serif}
.wrap{max-width:1250px;margin:0 auto;padding:0 16px}
.top{border-bottom:1px solid var(--line);padding:24px 0 12px}
h1{font-size:1.7rem;margin:0 0 4px}.sub{color:var(--muted);margin:0 0 12px}
.toc{font-size:.9rem;color:var(--muted);line-height:2}.toc a{color:var(--accent);text-decoration:none}
details.about{margin:12px 0;font-size:.95rem}details.about summary{cursor:pointer;color:var(--accent)}
.page{border-bottom:1px solid var(--line);padding:24px 0}
.page header{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.page h2{font-size:1.15rem;margin:0}.scan{font-size:.85rem;color:var(--muted)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-top:12px}
.he{font-family:"Noto Serif Hebrew",serif;font-size:1.12rem;line-height:1.9;order:2}
.en{order:1}
.fn{color:var(--accent);font-size:.7em}
.knotes{font-size:.85rem;color:var(--muted);border-top:1px solid var(--line);padding-top:8px;list-style:none;padding-right:0}
.knotes-en{font-size:.88rem;color:var(--muted);border-top:1px solid var(--line);margin-top:12px}
.knotes-en h3{font-size:.9rem;margin:8px 0 0}
.sch{background:var(--sch);border-radius:3px;padding:0 3px}
blockquote{margin:12px 0;padding:4px 12px;border-left:3px solid var(--accent);color:var(--muted);font-size:.92rem}
.schbox{margin-top:12px;font-size:.85rem}.schbox summary{cursor:pointer;color:var(--accent)}
.schbox table{border-collapse:collapse;width:100%;margin-top:6px}.schbox td,.schbox th{border:1px solid var(--line);padding:4px 6px;vertical-align:top;text-align:left}
.themebtn{float:right;background:none;border:1px solid var(--line);color:var(--fg);border-radius:4px;padding:2px 8px;cursor:pointer;font:inherit;font-size:.85rem}
@media (max-width:800px){.cols{grid-template-columns:1fr;gap:16px}.he{order:1}.en{order:2}}
</style></head><body>
<div class="wrap">
<div class="top">
<button class="themebtn" id="tb" type="button">Theme</button>
<h1>Jacob Emden, <i>Megillat Sefer</i></h1>
<p class="sub">Hebrew (Kahana, Warsaw 1896/97) with an English draft translation · work in progress</p>
<details class="about"><summary>About this text</summary>
<p><b>Hebrew:</b> David Kahana's edition (Warsaw 1896/97), from the HebrewBooks scan no. 37017, which is Gershom
Scholem's copy (his library stamp is on scan p. 196). OCR by Kraken with the PP-OCRv6 model, then checked line by line
against the scan by Claude. Running heads and page numbers are removed; Kahana's footnote calls are shown as small
letters.</p>
<p><b>English:</b> draft translation by Claude (Anthropic), not yet reviewed. Biblical phrases are given in standard
wording with the reference. Kahana's own footnotes are translated under each page.</p>
<p><b>Scholem's copy:</b> the margins carry handwritten insertions, most of them words that Kahana left out of the
manuscript text (often harsh terms for non-Jews). They are shown as <span class="sch">⟨S: …⟩</span> where his caret
points, and listed with their certainty under each page. A typed sheet bound in after p. 8 copies a slip of the Oxford
manuscript. Some notes are cut off at the edge of the scan.</p>
<p><b>Not the manuscript:</b> Kahana's text is not a full transcription of the Oxford manuscript (Bodleian, Neubauer
1723:2). A critical edition by Jacob J. Schacter has been announced.</p>
<p>Source and scripts: <a href="https://github.com/EzraBrand/emden-megillat-sefer">github.com/EzraBrand/emden-megillat-sefer</a>.</p>
</details>
<nav class="toc">{{TOC}}</nav>
</div>
{{BODY}}
<p class="sub" style="padding:24px 0">Draft. Corrections welcome on GitHub.</p>
</div>
<script>
(function(){var k='ms-theme',r=document.documentElement,b=document.getElementById('tb'),o=['auto','light','dark'];
function g(){try{return localStorage.getItem(k)||'auto'}catch(e){return 'auto'}}
function s(v){if(v==='auto')r.removeAttribute('data-theme');else r.setAttribute('data-theme',v);b.textContent='Theme: '+v;try{localStorage.setItem(k,v)}catch(e){}}
s(g());b.onclick=function(){s(o[(o.indexOf(g())+1)%3])};})();
</script>
</body></html>
"""

if __name__ == "__main__":
    main()
