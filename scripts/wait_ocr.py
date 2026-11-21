"""Wait until Kraken OCR exists for scan pages FIRST..LAST (OCR may still be running in the background).
  py -3.13 scripts/wait_ocr.py FIRST LAST [MAX_MINUTES=9]
Prints which pages are ready. Exit code 0 when all are ready, 1 on timeout (then run it again)."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
a, b = int(sys.argv[1]), int(sys.argv[2])
limit = float(sys.argv[3]) if len(sys.argv) > 3 else 9
t0 = time.time()
while True:
    missing = [n for n in range(a, b + 1) if not (ROOT / "data" / "kraken" / f"s{n:03d}.txt").exists()]
    if not missing:
        print(f"ready: s{a:03d}-s{b:03d}", flush=True)
        sys.exit(0)
    if time.time() - t0 > limit * 60:
        print(f"timeout after {limit} min; still missing: {missing}", flush=True)
        sys.exit(1)
    time.sleep(20)
