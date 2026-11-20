"""Merge a batch of OCR fixes into data/fixes.json.
  py -3.13 scripts/merge_fixes.py BATCH.json
BATCH.json: {"31": {"body": [[old, new], ...], "notes": [...], "move_to_notes": [...]}, ...}; pages replace earlier entries."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "data" / "fixes.json"
f = json.loads(p.read_text(encoding="utf-8"))
new = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
f.update(new)
p.write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
print("merged pages:", ", ".join(new))
