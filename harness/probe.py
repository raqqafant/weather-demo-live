"""Stage 1: fetch the MET Norway forecast for Hamar.

Follows MET's terms of service (https://api.met.no/doc/TermsOfService):
  - identifying User-Agent with a contact
  - coordinates truncated to max 4 decimals
  - no new request before the Expires time; If-Modified-Since otherwise

Writes:
  fixtures/met_hamar.json       raw API response (also the offline input)
  fixtures/met_hamar.meta.json  Last-Modified / Expires from the last fetch
  out/probe.json                normalised items, checked by eval/check_probe.py

Usage:
  python3 harness/probe.py            # network (respects cache)
  python3 harness/probe.py --offline  # fixture only
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "fixtures" / "met_hamar.json"
META = ROOT / "fixtures" / "met_hamar.meta.json"
OUT = ROOT / "out" / "probe.json"

LAT, LON = 60.7945, 11.0680
SOURCE_URL = (
    "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    f"?lat={LAT:.4f}&lon={LON:.4f}"
)
USER_AGENT = "weather-demo-hamar/2.0 github.com/raqqafant/weather-demo-live"


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _cache_still_fresh():
    if not (FIXTURE.exists() and META.exists()):
        return False
    expires = _load_json(META).get("expires")
    if not expires:
        return False
    try:
        return datetime.now(timezone.utc) < parsedate_to_datetime(expires)
    except (TypeError, ValueError):
        return False


def fetch():
    """Return the raw forecast, using the cached fixture when MET allows it."""
    if _cache_still_fresh():
        print("probe: cache fresh until Expires, no request sent", file=sys.stderr)
        return _load_json(FIXTURE)

    headers = {"User-Agent": USER_AGENT}
    if FIXTURE.exists() and META.exists():
        last_modified = _load_json(META).get("last_modified")
        if last_modified:
            headers["If-Modified-Since"] = last_modified

    req = urllib.request.Request(SOURCE_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
            meta = {
                "last_modified": res.headers.get("Last-Modified"),
                "expires": res.headers.get("Expires"),
            }
        _save_json(FIXTURE, data)
        _save_json(META, meta)
        print("probe: fetched new forecast", file=sys.stderr)
        return data
    except urllib.error.HTTPError as err:
        if err.code == 304 and FIXTURE.exists():
            meta = _load_json(META)
            meta["expires"] = err.headers.get("Expires") or meta.get("expires")
            _save_json(META, meta)
            print("probe: 304 not modified, using fixture", file=sys.stderr)
            return _load_json(FIXTURE)
        raise


def to_items(raw):
    items = []
    for step in raw["properties"]["timeseries"]:
        items.append({
            "title": f"Hamar {step['time']}",
            "date": step["time"],
            "air_temperature": step["data"]["instant"]["details"]["air_temperature"],
        })
    return items


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true", help="read fixtures/ only")
    args = parser.parse_args(argv)

    if args.offline:
        if not FIXTURE.exists():
            sys.exit("probe: no fixture yet; run once without --offline")
        raw = _load_json(FIXTURE)
    else:
        raw = fetch()

    _save_json(OUT, {
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": to_items(raw),
    })
    return raw


if __name__ == "__main__":
    main()
