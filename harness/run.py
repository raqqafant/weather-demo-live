"""Whole chain in one command: fetch (stage 1) -> render page (stage 2).

  python3 harness/run.py            # network, respects MET caching
  python3 harness/run.py --offline  # from fixtures/ only
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe   # noqa: E402
import render  # noqa: E402

if __name__ == "__main__":
    probe.main(sys.argv[1:])
    render.main()
