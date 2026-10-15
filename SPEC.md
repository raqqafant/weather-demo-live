# SPEC: Weather demo (MET Norway, Hamar)

## Problem
Practice repo for the KIUA-2003 loop (spec -> plan -> run -> verify -> commit),
mirroring the W40 lecture demo: fetch tomorrow's weather forecast for Hamar from the
MET Norway Locationforecast API and turn it into a checked output file.
The real Innlandet problem will be chosen from `docs/problem-candidates.md`.

## Users
The two of us (learning the workflow). Later: anyone in Hamar who wants a short daily forecast.

## Definition of success
- `python3 harness/probe.py && python3 eval/check_probe.py` exits 0 and prints PASS
- The same passes offline from `fixtures/met_hamar.json` (`--offline`)
- Every request follows MET's terms: identifying User-Agent, <= 4 coordinate decimals, cached responses
