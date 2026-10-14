# vibe-guard-evaluation

Pre-registered evaluations of [vibe-guard](https://github.com/Joaquinriosheredia/java-vibe-guard)'s
engines ([java-vibe-guard](https://github.com/Joaquinriosheredia/java-vibe-guard) and
[python-vibe-guard](https://github.com/Joaquinriosheredia/python-vibe-guard)) on repositories
never used to tune their rules.

Each evaluation lives in its own directory and starts with a `PREREGISTRATION.md`
committed before any search, selection or run. Departures from it go to `DEVIATIONS.md`.

| Directory | What | Status |
|---|---|---|
| [`test-corpus-1/`](test-corpus-1/) | Precision of CRITICAL findings (≥ 90 %, ≥ 50 reviewed) and noise per 1,000 files, Java/Spring and Python/FastAPI | pre-registered 2026-10-14 · see its `DEVIATIONS.md` |

Third-party code is cited by repository, pinned commit and file:line. Nothing is opened in
those repositories. Checkouts are not stored here; only vibe-guard's outputs are.

Tests of the evaluation scripts: `node --test test-corpus-1/test/*.test.mjs`.

MIT License.
