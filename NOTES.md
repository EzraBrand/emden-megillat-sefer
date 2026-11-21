# Emden, Megillat Sefer: translation project

Started 20-Nov-2026.

## Base text decision (20-Nov-2026)

- **Base: Kahana, Warsaw 1896/97 (תרנ"ז)**, scan HebrewBooks 37017 (https://hebrewbooks.org/37017, 254 pp.).
  A reader comment on Dunner's review says this copy has handwritten notes, reportedly by Scholem,
  that compare it with the Oxford manuscript. Check them.
- **Pninim text** (GitLab `pninim.org/pninim`, folder `קורות_חיים/מגילת_ספר`, GFDL 1.3) is from Bick 1979.
  Use only as an OCR / alignment aid. Do not use as base. Log every Kahana/Pninim difference.
- Bick 1979 is rejected by Schacter, Leiman, Goldstein, Bombach (sources in Dunner 2012 review).
- Kahana is flawed: he cut passages he took as repetitions (marked in his text) and softened at
  least one reading: MS p. 122b "ובשעי דבית הכסא" -> Kahana "ובשעות פנויות" (Schacter, Ḥakirah 34, 2023).
  Pninim (Bick) also has "ובשעות פנויות" (chapter א).
- The Oxford MS (Neubauer 1723:2) is a copy, not an autograph. Schacter's critical edition
  (Zalman Shazar Center) is announced, not yet out as of Nov-2026.

## The scan (downloaded by the owner 20-Nov-2026)

- `kahana_1896_hb37017.pdf`, 7.2 MB, 254 pages, bilevel page images 2721x4276 px, HebrewBooks OCR text layer
  (poor: ס/ם confusions, broken word order; do not use as text).
- **Gershom Scholem's copy**: library stamp "גרשום שלום" on scan p. 196. Handwritten marginal insertions with
  caret marks in the text, e.g. scan p. 66 (book p. 54) and scan p. 196 (book p. 176). These look like
  readings restored from the Oxford MS. Pages with most margin ink (candidates): 66, 196, 75, 25, 74, 23, 27,
  56, 117, 54, 133, 76, 135 (ranking only, not checked one by one).
- Scan page to book page: scan 13 = p. 5 (+8); scan 18 is a blank page; scan 19-27 = pp. 9-17 (+10); scan 66 = p. 54 (+12). Check per section.
- Test passage "ובשעות פנויות" (Ḥakham Tzvi) is on scan p. 27.

## Kraken test (20-Nov-2026, scan p. 13 = book p. 5)

- Kraken 7.1.1 from `Claude\syriac-ocr\.venv`; set `PYTHONIOENCODING=utf-8` or it fails on the ✓ mark.
  Page rendered at 600 dpi grey. Output is visual order: reverse each line.
- **PP-OCRv6 medium** (Kiessling, zenodo 21788410, Apache-2.0, in htrmopo cache `1980fa54...`): best. Keeps
  punctuation, gershayim, final letters, footnote marks. About 5 errors in ~400 words (נם/נס, בך/כך, lost ז in ז"ל).
  90 s a page on CPU.
- BiblIA_01 and Italian_01 (medieval MS models): worse, drop punctuation and gershayim. 40 s a page.
- Problem: Scholem's pen brackets come through as ( ) [ ] inside the text, and margin notes come out as junk
  lines (e.g. "קופאון" for his "קויפמאן"). Handwritten notes need a separate pass (scan check or LLM).
- Test files: `kraken_test\`.

## Sources

- Dunner review: https://seforimblog.com/2012/03/megillat-sefer-translation-review-by/
- Schacter, Ḥakirah 34: https://hakirah.org/Vol34Schacter.pdf
- Schacter, "Why Did Rabbi Jacob Emden Not Publish His Megillat Sefer?":
  https://repository.yu.edu/server/api/core/bitstreams/1ac84e03-9114-4414-966d-f1e2e3f4ec32/content
- English translation: Leperer and Wise, Shaftek 2011 (weak, from Bick).
- French: Hayoun, Mémoires de Jacob Emden, Cerf 1992.

## Pilot, scan pp. 11-27 = book pp. 3-17 (20-Nov-2026)

Pipeline: `scripts/ocr_kraken.py` (Kraken PP-OCRv6, 17 pages in 19 min, 3 workers) -> `scripts/align_pninim.py`
(split running head and Kahana footnotes, align with Pninim, ignore ו/י spelling and abbreviation expansions)
-> page-by-page check on the scan, fixes in `data/fixes.json` -> `scripts/apply_fixes.py` -> `data/text/sNNN.he.txt`
+ `.notes.txt`. Scholem's notes: `data/scholem/notes_pilot.tsv`. Translation: `translation/pilot_pp03-08.md`,
`translation/pilot_pp09-17.md` (by Claude in session).

- Kraken quality: about 1-3 real errors a page in the main text; most noise is page numbers, running heads,
  Scholem's pen marks read as letters, and his margin notes read as junk lines.
- Pninim is a weak second reader: it modernises spelling and expands abbreviations (ש"ע -> שולחן ערוך); 73-91%
  of words match. Still useful: it confirmed the typed insert (p. 17) and showed Bick omits a whole sentence on
  book p. 14 (matzah fee) that Kahana prints, and has word-order differences (p. 5).
- **Scholem's copy layers:**
  1. Margin insertions with carets. They restore words that Kahana left out, most of them **anti-gentile
     epithets**: p. 6 "היונים הארורים ... האכזרים" (at Kahana's "חרב היונה"), "הטמאים הערלים" (after "הפוחזים"),
     p. 7 "היונים הארורים", p. 14 "של סתם יינם". So Kahana's edition has a censorship layer for language about
     non-Jews, not only the "free hours" softening. Also p. 17: Kahana's "ס"ח" (his note: ספרי חן) vs MS "ספר הזהר".
  2. A **typed sheet bound in after p. 8** (scan 17): transcription of a half-page slip in the Oxford MS
     (leaf 117) about the grandfather's last years in Jerusalem. Bick has the same text in brackets after p. 10.
  3. Some notes are conjectures, not MS readings (p. 8 "אולי: מגלוגא").
  4. Many marks at the right edge of the scan are cut off (pp. 8, 10, 14): the HebrewBooks scan crops the
     margin. A better scan of Scholem's copy (NLI, Scholem Library) would recover them.
- Scholem did not mark "ובשעות פנויות" (p. 17), so his collation is selective, not complete.
- Margin crops: render the page with pymupdf, crop with PIL (pymupdf clip at x=0 gave blank crops). The notes are
  in the RIGHT margin (beside line starts).

## Chapter 2 (20-Nov-2026): book pp. 54-99, scan 66-115

- Done and pushed: 101 reader sections in total (pp. 3-99 plus inserts). Chapter 3 starts on scan 115, line 37
  ("אחר זאת נסעתי מאמשטרדם"); Kraken OCR of scan 116+ not yet run.
- Inserts in Scholem's copy: typed sheets at scan 17 (for p. 8), 52 (for p. 41), 85 (for p. 70); a sheet in
  Scholem's own hand at scan 72 (for p. 59). Blank pages: scan 18, 51, 71, 86. Inserts are flagged "manual" in
  data/fixes.json; their text is data/text/sNNN.he.txt (edited by hand).
- Scholem marks: 168 logged in all (pilot 21, ch1 69, ch2 78); 44 sure or fairly sure.
- Pattern in chapter 2: the same censorship as chapter 1 (ערלים, גויה, כלבים, הפושעים for gentiles; curses on
  Eybeschütz and his circle; the converted sons of Mordecai Kohen; "whores"); more long notes that are only partly
  read (pp. 60, 82, 98, 104-105).
- Workflow per batch: align_pninim.py -> read data/view/sNNN_full.png -> fixes JSON in scratchpad ->
  merge_fixes.py -> apply_fixes.py -> append translation -> build_site.py -> commit + push.

## Translation fixes (21-Nov-2026)

- "Klaus" -> "Kloyz" everywhere (the Altona kloyz, קלויז; see https://en.wikipedia.org/wiki/Kloyz).
- p. 4 (scan 12): Hebrew "בת הרב יצחקי ז"ל, מרא דארעא ישראל" is R. Abraham Yitzḥaki of Jerusalem, not "R. Isaac
  Tsaḥaki". Now "R. [Abraham] Yitzḥaki".
- p. 39 (scan 49) and p. 59 (scan 72): ברודא is Brod (Uherský Brod, Moravia), not Brody. "R. Eleazar of Brody" in
  Kahana's notes (scan 83 etc., בראדי) is correct and unchanged.

## NLI scan of the same copy, and the key sheet (21-Nov-2026)

- NLI Rosetta IE12757688 (https://rosetta.nli.org.il/delivery/DeliveryManagerServlet?dps_pid=IE12757688): 258 images,
  colour, full margins. Same copy as HebrewBooks 37017: the owner's screenshots show the same margin notes on p. 6 and
  the typed insert after p. 8. HebrewBooks has 254 pages and crops the right margin.
- Access from here: rosetta.nli.org.il and www.nli.org.il show a Cloudflare challenge to both the built-in browser and
  the chrome-devtools Chrome; the IIIF manifest https://iiif.nli.org.il/IIIFv21/DOCID/IE12757688/manifest returns 403.
  The owner can open the viewer in a normal browser. Not used yet for the readings.
- **Key sheet** (in the NLI scan, not in HebrewBooks; owner's screenshot), my reading:
  "…ר הספר (…) תקי"ז–תקי"ט" (first word cut off; perhaps a date of composition 1757–59) /
  "הגירסאות שבשוליים לפי כ"י אוקספורד" / "הסימן V פירושו השמטה" / "X פירושו החלפה" /
  "הושוה עם כ"י ע"י חיים וירשובסקי".
  So: margin readings = Oxford MS; V = omission (addition to the print); X = substitution; collated by Ḥayyim
  Wirszubski. The site now says this, with a note that the reading of the sheet is not certain in every word.
- The handwritten sheet at scan 72 looks like the same hand as the key sheet (not checked further); NOTES above call it
  "Scholem's hand", which is probably wrong.
- Site: inline readings are matched to the TSV rows in order per page (scripts/build_site.py, align_marks) and styled
  V or X; pp. 15, 75, 96 do not match and are shown untyped.

## The Oxford manuscript: shelfmark and access (21-Nov-2026)

- Shelfmark given in the literature: Bodleian **MS. Mich. 587** (Michael collection, bought 1848), e.g. "fols.
  163b-165a" for the introduction (Fordham Early Modern Workshop source,
  https://research.library.fordham.edu/emw/emw2011/emw2011/8/). Neubauer's catalogue number 1723:2 is presumably the
  same manuscript (not checked against Neubauer). A copy, not Emden's autograph; the autograph is lost.
- **Not online** as far as I can find: Digital Bodleian has only 13 Michael manuscripts digitized, and 587 is not one
  of them; the Bodleian Hebrew catalogue online (hebrew.bodleian.ox.ac.uk) has no record for it.
- Not checked: NLI Ktiv (IMHM microfilm of the Bodleian MS; Ktiv is behind the same Cloudflare check). The owner can
  search ktiv.nli.org.il for "מגלת ספר" / Mich. 587 in a normal browser; if images are viewable there, they would allow
  a check of Kahana's text and of the Wirszubski collation against the manuscript itself.
- Other route: order a digital copy from Bodleian Imaging Services.
