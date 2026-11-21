# Conventions for checking and translating *Megillat Sefer*

For anyone (human or agent) continuing the work page by page. Follow the files that already exist
(`translation/*.md`, `data/scholem/notes_*.tsv`, `data/fixes.json`) when in doubt; they are the model.

## 1. Hebrew: check the OCR against the scan

Per batch of 2-4 scan pages (FIRST..LAST):

1. `py -3.13 scripts/align_pninim.py FIRST LAST` — splits each Kraken page (`data/kraken/sNNN.txt`) into body
   (`data/body/`) and Kahana's footnotes (`data/notes_kahana/`), and lists differences from the Pninim text of Bick's
   edition (`data/align/diffs_FIRST-LAST.tsv`). Pninim modernises spelling and expands abbreviations: it is only a
   pointer to places to look, never a source of readings. Kahana's print, as seen on the scan, is the text.
2. Look at the scan: `py -3.13 scripts/render_view.py N --box 0 0 1 0.52 --name top` and
   `... --box 0 0.48 1 1 --name bot` (220 dpi halves; whole page: no `--box`). Read every line of `data/body/sNNN.txt`
   and `data/notes_kahana/sNNN.txt` against the image. Read at most about 8 images per message.
3. Write fixes as JSON in the format of `data/fixes.json`:
   `{"N": {"body": [[old, new], ...], "notes": [[old, new], ...], "move_to_notes": [line, ...]}}`.
   `old` must occur exactly in the split file (copy it). Remove junk lines that are the handwritten margin notes read
   as print (Kraken turns them into short nonsense lines) and stray page numbers or running heads. Typical Kraken
   errors: ב/כ, ס/ם, ה/ח, ו/ז/י, ר/ד, ן/ו, lost gershayim; Kraken also mirrors ( and ), which apply_fixes handles.
4. `py -3.13 scripts/apply_fixes.py FIRST LAST` writes `data/text/sNNN.he.txt` and `.notes.txt`, and reports any fix
   whose `old` string was not found. Fix until there are no such messages. Then re-read the output once.

Typed or handwritten sheets bound into the copy and blank pages: put `{"N": {"manual": true}}` in the fixes and write
`data/text/sNNN.he.txt` by hand (first line a bracketed description, e.g. `[TYPED INSERT bound into Scholem's copy,
headed "...". Transcribed from the scan.]`), and an empty `sNNN.notes.txt`. A blank page gets an empty `.he.txt`
and no translation section.

## 2. Margin readings in Scholem's copy (the Wirszubski collation)

The handwritten notes are in the RIGHT margin, next to the line they belong to, with a mark in the printed line.
A key sheet in the copy says: readings follow the Oxford manuscript; **V** (a caret, ^) = omission (words missing in
the print); **X** = substitution (the MS has the margin words instead of the printed ones); collated by Ḥayyim
Wirszubski. Read them at 300-400 dpi with a box that takes in the margin and the adjacent printed words
(`--box 0.70 Y0 1 Y1 --dpi 350`). `py -3.13 scripts/margin_ink.py FIRST LAST` lists ink bands in the margins if you
need help finding them. The scan crops part of the right margin: say "cut off" when it is.

For each mark, one row in your TSV (columns, tab-separated, header as in `data/scholem/notes_ch2.tsv`):
`scan_page  book_page  anchor_in_print  mark  margin_text_reading  certainty  crop`
- `anchor_in_print`: the printed words at the mark, with `^` or `x` where it stands.
- `mark`: must START with `caret` or `x mark` (or `v mark`), then a short description ("caret; 2-line note in right
  margin"). Use other wording only for marks that are neither (brackets, underlining).
- `margin_text_reading`: the Hebrew as read, `(?)` for doubtful words, `...` for unread parts; `not read` if nothing
  could be read; `-` if there is no margin text (a mark only).
- `certainty`: `sure`, `fairly sure`, `uncertain`, `partial`, `not read`.
- `crop`: e.g. `view s130_crop` (the image you read it from).

In the English, every row that has margin text gets exactly one inline reading, in the same order as the rows, at
the place the mark points: `⟨S: "the uncircumcised"⟩`, `⟨S: a word, not read⟩`, `⟨S: a three-line note, partly read:
"…"⟩`, `⟨S: "the wicked"(?)⟩`. Rows with `-` (no margin text) get no inline reading. The site matches inline readings
to rows by order, so the counts per page must agree. Translate the printed text as printed; never merge a margin
reading into it.

## 3. English translation

File layout (see `translation/ch2_pp55-99.md`):

```
## Page 100 (scan 116)

English of the whole page, in paragraphs. A page may begin or end in the middle of a sentence: keep it so.
Kahana's footnote call at its place: **[a]**, **[b]** … (Hebrew א=a, ב=b, ג=c, ד=d, ה=e, ו=f, ז=g, ח=h, ט=i).

**Kahana's notes**
- [a] English of the note.
```

- Book page number = the number printed in the running head of the scan page. Inserted sheets: `## Typed insert for
  p. N (scan M)` or `## Handwritten sheet for p. N (scan M)`, with a short italic headnote saying what it is and where
  its caret is, then the English.
- Chapter breaks are Bick's (Kahana has none). Where Bick's next chapter begins, put on its own line
  `[*Here chapter N begins in Bick's edition.*]`. Openings of Bick's chapters 4-8 (Pninim files ד..ח):
  4 "אשוב לספר כסדר מתחילה ישיבתי באלטונא"; 5 "חוזרני לעניין לספר קורותי באלטונא"; 6 "עתה אחזור לעניין מלאכת
  הדפוס"; 7 "בסוף אייר תקי"א ברחתי לילה"; 8 "עתה אספר מה שקרה לי עם הבתים שקניתי באלטונא". Bick may order the
  text differently from Kahana; mark a break only where the opening words really occur.
- Faithful, plain, readable English; keep Emden's tone (bitter, ironic, pious). No paraphrase, no added explanation in
  the text. A short `**Translator's note.**` paragraph only where a reader would otherwise be misled.
- Biblical phrases woven into the prose: wording of the verse in quotation marks, reference at the first strong
  allusion: `(Ps. 40:6)`, `(Job 19:23–24)`, `(1 Sam. 2:3)`. Book abbreviations: Gen. Ex. Lev. Num. Deut. Josh. Judg.
  1 Sam. 2 Sam. 1 Kgs. 2 Kgs. Isa. Jer. Ezek. Hos. Joel Amos Obad. Jon. Mic. Nah. Hab. Zeph. Hag. Zech. Mal. Ps. Prov.
  Job Song Ruth Lam. Eccl. Esth. Dan. Ezra Neh. 1 Chr. 2 Chr. Rabbinic: `(b. Shabbat 66b)`, `(m. Avot 2:4)`,
  `(cf. b. Bava Metzia 59a)`. Use "cf." when it is an allusion, not a quotation.
- Dates: Hebrew year, then the civil year in brackets: 5511 [1751]; "the year [5]457 [1697]" for short forms.
- Words supplied for sense in square brackets [ ]; doubtful readings or senses (?).
- Fixed terms: ר' = R.; הגאון = the gaon; אב"ד = head of the court; ק"ק = the holy community of; קצין = leader;
  פרנס = parnas (pl. parnassim); ז"ל = of blessed memory; ימ"ש = may his name be blotted out; שר"י = may the name
  of the wicked rot; קלויז = the Kloyz (never "Klaus"); ג' קהלות = the Three Communities; ר"ט = Reichstaler;
  אמ"ה (אבי מורי הגאון) = my father and teacher the gaon, or "my father, of blessed memory" by context.
- Names and places as in `data/site/entities.json` (Eybeschütz, Ḥakham Tzvi, Ḥayon, Altona, Brod for ברודא,
  Brody only for בראדי, Ofen/Buda …). Transliteration: ח = ḥ, צ = tz, כ/ך = kh, א/ע inside a word = ' (Ya'avetz,
  Ta'anit). Hebrew book titles in italics: *She'ilat Ya'avetz*.
