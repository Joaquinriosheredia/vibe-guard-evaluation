# Exclusion sources — test-corpus-3

`exclusions.json` lists every repository that must not enter test-corpus-3
(`PREREGISTRATION.md`, "Changes from test-corpus-2", exclusion a). It is the union of:
1. test-corpus-2's `exclusions.json`, 1,021 repositories: test-corpus-1, its processed
   repositories, development labels and sets, and the URLs pinned there;
2. **every repository test-corpus-2 processed**, included and excluded: 529, from
   `corpus-java.json` and `corpus-python.json`, `processed[]`;
3. every GitHub URL in the docs, READMEs, fixtures and tests of the five repositories below.

`scripts/build-exclusions.mjs` builds it, reading each source with `git show` at the pinned
commit below (never a working tree, no network call). **Result: 1,277 repositories**, built on
2026-10-24.
- 1 and 2 overlap in 273 repositories: test-corpus-2's `processed[]` also records the
  candidates it excluded as "used before".
- 3 adds none that 1 and 2 do not already hold.

The commits are the `main`/`master` of each repository after the test-corpus-2 fixes were
merged. `FROZEN.json` is not filled yet: the release commits that follow only bump versions
and changelogs, which add no GitHub URL of another repository.

| Source | Pinned commit | What is read |
|---|---|---|
| [python-vibe-guard](https://github.com/Joaquinriosheredia/python-vibe-guard) | `19571da57830573a1e7b5f8ac264f31d317e4c0f` (master, fixes merged) | `research/datasets/{100,250,1000}-repos.json`, `validation/aggregate.json`, `validation/breakdown.json` (4 short names mapped, as in test-corpus-2); every GitHub URL in `README.md`, `CHANGELOG.md`, `research/**/*.md`, `validation/*.md`, `tests/**` and `demo/**` |
| [java-vibe-guard](https://github.com/Joaquinriosheredia/java-vibe-guard) | `67314dadff41a4a146b5ce8e0a0307a765368094` (master, fixes merged) | `validation/repos.json`, `validation/b0-corpus/corpus.json`; every GitHub URL in `README.md`, `CHANGELOG.md`, `cli/README.md`, `validation/**/*.md`, `cli/test-fixtures/**`, `cli/test/**` and `mcp-server/src/test/**` |
| vibe-guard (coordination, private) | `6cb970e26101c1ac3bafaf32971793192b8f11f4` | every GitHub URL in `docs/**/*.md` and the root `*.md` |
| vibe-guard-scan (wrapper, private) | `0367d22da5f5e3e63b591885f16238ce1ac979a5` | every GitHub URL in `*.md` and `test/**` |
| vibe-guard-evaluation (this repository) | `a05e1f4101e56a6f826556adc9d2f58a1815194b` (main, with this pre-registration) | `test-corpus-2/exclusions.json` (the 1,021), `test-corpus-2/corpus-java.json` and `corpus-python.json` (**all 529 processed**); every GitHub URL in `test-corpus-1/**/*.md`, the top-level `*.md` of `test-corpus-2/` and `test-corpus-3/`, and the root `*.md` |
| The audit trial of 2026-10-12 (development set) | — | `halo-dev/halo`, `YunaiV/ruoyi-vue-pro`, `open-webui/open-webui` (already in 1) |
| The "Found in the Wild" audit of OpenLegislation | — | `nysenate/OpenLegislation` (already in 1) |

- **`test-corpus-2/cards/*.md` are not read:** they quote the code of the reviewed
  repositories, and a URL inside that code is not a repository used before. Those
  repositories themselves are in 2.
- Repositories owned by `Joaquinriosheredia` are excluded separately (rule b).

**Checks** (`test/units.test.mjs`):
- all 1,021 names of test-corpus-2's list are included;
- all 529 repositories test-corpus-2 processed are included;
- all 204 repositories test-corpus-1 processed are included;
- the development set and OpenLegislation are included.

## Not excluded (`PREREGISTRATION.md`)

- **test-corpus-2 candidates that were never processed.** Nobody saw their code or their
  findings. The queries are the same and capped at 1,000 results, so excluding every candidate
  would leave almost nothing.
- **test-corpus-1 candidates never processed** and its **quarantined accidental search**, as
  in test-corpus-2.

## Known limit

Inherited from test-corpus-2: `research/datasets/100-repos.json` of python-vibe-guard keeps
only aggregates per rule, not its full list of 100 repositories. The repositories it names are
excluded. One of the others could enter the corpus, and that cannot be detected.
