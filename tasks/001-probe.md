# Task 001: Probe one public source (MET Norway forecast for Hamar)

## Goal
After this task, `harness/probe.py` fetches the MET Norway forecast for Hamar and
writes `out/probe.json`, which passes `eval/check_probe.py`.

## Context
- Source: MET Norway Locationforecast 2.0, compact:
  `https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=60.7945&lon=11.0680`
- Terms of service: https://api.met.no/doc/TermsOfService
  (human must verify both links exist before the task starts)
- Output format `out/probe.json` (UTF-8):
  ```json
  {
    "source_url": "https://api.met.no/...",
    "fetched_at": "2026-10-16T10:00:00Z",
    "items": [
      {"title": "Hamar 2026-10-16T12:00Z", "date": "2026-10-16T12:00:00Z", "air_temperature": 7.3}
    ]
  }
  ```
  One item per timestep in the response (`properties.timeseries[*]`);
  `air_temperature` from `data.instant.details.air_temperature`.

## Constraints
- Do not edit `eval/`.
- No personal data; follow MET's terms:
  - send an identifying `User-Agent` with a contact (e.g. `innlandet-harness/0.1 <your-github-url>`), never a generic one
  - coordinates with at most 4 decimals
  - cache: save the raw response to `fixtures/met_hamar.json`; do not hammer the API
- `--offline` flag: read `fixtures/met_hamar.json` instead of the network.
- Python 3 standard library only (`urllib.request`, `json`).
- Write output to `out/` (git-ignored); create the folder if missing.

## Acceptance (all must pass)
- `python3 harness/probe.py && python3 eval/check_probe.py` prints PASS
- `python3 harness/probe.py --offline && python3 eval/check_probe.py` prints PASS
- The check failed before this task started (red first)

## Out of scope
Summarisation, scheduling, If-Modified-Since caching (task 002), anything with an LLM.
