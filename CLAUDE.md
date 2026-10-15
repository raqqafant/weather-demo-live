# CLAUDE.md

Project: an agentic workflow harness for a recurring information workflow in Innlandet (KIUA-2003, pair project).

## Run checks
- Each task in `tasks/NNN-*.md` lists its acceptance command; it must print PASS / exit 0.
- Checks live in `eval/`; run them with `python3 eval/<check>.py`.

## Rules
- Never edit anything in `eval/` without asking first.
- No personal data. Public sources only; follow each source's terms (User-Agent, caching, rate limits).
- Never read or print `.env`; secret names go in `.env.example`, never values.
- One task = one branch = one PR. Stay inside the task's scope.
- Save real inputs to `fixtures/` so runs are reproducible offline.
- Write UTF-8 (æ, ø, å). Use `python3`, not `python`.
- Run the acceptance check yourself before saying a task is done.
