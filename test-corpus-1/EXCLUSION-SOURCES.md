# Exclusion sources

`exclusions.json` lists every repository used before in any vibe-guard corpus, trial or
audit. `scripts/build-exclusions.mjs` builds it, reading each source with `git show` at
the pinned commit below (never a working tree). Result: **962 repositories**.

| Source | Pinned commit | What is read |
|---|---|---|
| [python-vibe-guard](https://github.com/Joaquinriosheredia/python-vibe-guard) | `2511da27906f0eed1767d4cf1d05bbc79f87c22d` (v0.13.0) | `research/datasets/{100,250,1000}-repos.json` (every `repo`, including `top_repos`); `validation/aggregate.json` (the 902 repositories of the massive scan); `validation/breakdown.json` (4 short names, mapped to `tiangolo/fastapi`, `celery/celery`, `aio-libs/aiohttp`, `encode/httpx`); every GitHub URL in `README.md`, `research/**/*.md` and `validation/*.md` |
| [java-vibe-guard](https://github.com/Joaquinriosheredia/java-vibe-guard) | `a4c5380` | `validation/repos.json` (validate-public); `validation/b0-corpus/corpus.json` (the 50 of the B0 corpus); every GitHub URL in `README.md` ("Found in the Wild") and `validation/**/*.md` |
| vibe-guard (coordination, private) | `eb88a8d` | every GitHub URL in `docs/**/*.md`, `STATUS.md` and `DECISIONS.md` |
| The audit trial of 2026-10-12 (development set) | — | `halo-dev/halo`, `YunaiV/ruoyi-vue-pro`, `open-webui/open-webui` |
| The "Found in the Wild" audit of OpenLegislation | — | `nysenate/OpenLegislation`, named without a URL in vibe-guard `docs/FASE-3-b0-found-in-wild-openlegislation.md` (it is also in the B0 corpus) |

Repositories owned by `Joaquinriosheredia` are excluded separately (rule 3b).

## Known limit

`research/datasets/100-repos.json` of python-vibe-guard keeps only aggregates per rule
(`top_repos`), not the full list of its 100 repositories.
- The repositories it names are excluded.
- One of the others could enter the corpus, and that cannot be detected.
- The results state this.
