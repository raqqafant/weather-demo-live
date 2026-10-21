# Prompt log

Agent output we corrected, challenged or rejected. One line per event.

| Date | Task | What the agent did | What we did instead / why |
|------|------|--------------------|---------------------------|
| 2026-10-15 | index.html | Set User-Agent in a browser fetch; browsers drop it, so MET never saw it | Removed it, relied on Origin, added Expires cache |
| 2026-10-21 | python | Rewrote the page in Python: probe.py sends a real User-Agent, honours Expires + If-Modified-Since | Static page built hourly by GitHub Actions instead of JS in the browser |
| 2026-10-21 | render.py | Icon links pointed at api.met.no/images/weathericons/..., which does not exist (old JS hid this with an emoji fallback) | Vendored metno/weathericons SVGs (MIT) into harness/icons, copied to out/icons |
| 2026-10-21 | eval | check_page.py did not catch broken icons | Added check: every <img> is a local, non-empty file in out/ (red-tested with a missing and an external icon) |
