# Prompt log

Agent output we corrected, challenged or rejected. One line per event.

| Date | Task | What the agent did | What we did instead / why |
|------|------|--------------------|---------------------------|
| 2026-10-15 | index.html | Set User-Agent in a browser fetch; browsers drop it, so MET never saw it | Removed it, relied on Origin, added Expires cache |
| 2026-10-21 | python | Rewrote the page in Python: probe.py sends a real User-Agent, honours Expires + If-Modified-Since | Static page built hourly by GitHub Actions instead of JS in the browser |
