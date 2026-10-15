# Exclusion sources — test-corpus-2

`exclusions.json` lists every repository that must not enter test-corpus-2:
- every repository used before in any vibe-guard corpus, trial, audit, fixture or label;
- every repository test-corpus-1 processed.

`scripts/build-exclusions.mjs` builds it, reading each source with `git show` at the pinned
commit below (never a working tree, no network call). **Result: 1,021 repositories**, built on
2026-10-15.

| Source | Pinned commit | What is read |
|---|---|---|
| [python-vibe-guard](https://github.com/Joaquinriosheredia/python-vibe-guard) | `4af3ce75f4b896a77c94e58b685fad4f5c6ff669` (v0.14.0) | `research/datasets/{100,250,1000}-repos.json`, `validation/aggregate.json`, `validation/breakdown.json` (4 short names mapped to `tiangolo/fastapi`, `celery/celery`, `aio-libs/aiohttp`, `encode/httpx`); every GitHub URL in `README.md`, `research/**/*.md`, `validation/*.md`, `tests/**` and `demo/**` |
| [java-vibe-guard](https://github.com/Joaquinriosheredia/java-vibe-guard) | `a4c5380761ded82da6581dca79d02f39ff057a18` | `validation/repos.json`, `validation/b0-corpus/corpus.json`; every GitHub URL in `README.md`, `validation/**/*.md`, `cli/test-fixtures/**`, `cli/test/**` and `mcp-server/src/test/**` |
| vibe-guard (coordination, private) | `97ed6564f2acd0d3662584267ea461cbc1603fa2` | every GitHub URL in `docs/**/*.md` and the root `*.md` |
| vibe-guard-scan (wrapper, private) | `f39dc7dcc2180a28cacd125039bba40e5be97bb4` | every GitHub URL in `*.md` and `test/**` |
| vibe-guard-evaluation (this repository) | `b0242054b8d4c08b1c1a8d8fa94d6aed3f6b7fc0` | `test-corpus-1/exclusions.json` (the 962), `test-corpus-1/corpus.json` (**all 204 processed**, included and excluded), `test-corpus-1/dev-labels.json`; every GitHub URL in `test-corpus-1/**/*.md` |
| The audit trial of 2026-10-12 (development set) | — | `halo-dev/halo`, `YunaiV/ruoyi-vue-pro`, `open-webui/open-webui` |
| The "Found in the Wild" audit of OpenLegislation | — | `nysenate/OpenLegislation` |

Repositories owned by `Joaquinriosheredia` are excluded separately (rule b).

**Checks** (`test/units.test.mjs`):
- all 962 names of test-corpus-1's list are included;
- all 204 processed repositories of test-corpus-1 are included;
- the development set and OpenLegislation are included.

## Not excluded (decision of 2026-10-15)

- **test-corpus-1 candidates that were never processed:** names in its `candidates.json`
  beyond the processed ones.
- **The quarantined accidental search** (`test-corpus-1/accidental-search/`), which was never
  opened.

Nobody saw their code or their findings.

## Known limit

`research/datasets/100-repos.json` of python-vibe-guard keeps only aggregates per rule
(`top_repos`), not the full list of its 100 repositories. The repositories it names are
excluded. One of the others could enter the corpus, and that cannot be detected. The results
state this.
