# Exclusion sources — test-corpus-4

`exclusions.json` lists every repository that must not enter test-corpus-4. It implements
exclusion a of `PREREGISTRATION.md` ("Exclusions"). It is the union of:
1. test-corpus-3's `exclusions.json`, 1,277 repositories. It already covers test-corpus-1 and
   test-corpus-2, every repository they processed, the development labels and sets, and the
   URLs pinned there.
2. **Every repository test-corpus-3 processed**, included and excluded: 877, from
   `corpus-java.json` (579) and `corpus-python.json` (298), `processed[]`.
3. Every GitHub URL in the docs, READMEs, fixtures and tests of the seven repositories below.

`scripts/build-exclusions.mjs` builds it. It reads each source with `git show` at the pinned
commit below, never from a working tree, and makes no network call. **Result: 1,625
repositories**, built on 2026-10-28:
- 1 and 2 overlap in 530 repositories, because test-corpus-3's `processed[]` also records the
  candidates it excluded as "used before". 2 adds 347.
- 3 adds one: `acme/shop`, a made-up URL in a vibe-guard-scan test
  (`test/review-chain.test.js`). It is kept because the rule takes every URL.

**Pinned commits:** the `main`/`master` of each repository on 2026-10-28.
- For the private engines, this is the master with the test-corpus-3 fixes merged; for
  vibe-guard-evaluation, the merge of this pre-registration.
- `FROZEN.json` is not filled yet. The tagged commits Joaquín freezes must be these engine
  commits or descendants that only add release metadata (`PREREGISTRATION.md`), which add no
  GitHub URL of another repository.

| Source | Pinned commit | What is read |
|---|---|---|
| pyvibe-pro (private) | `ec317f9c1c4fd0d269913079413c561b483e925d` (master, test-corpus-3 fixes merged) | `research/datasets/{100,250,1000}-repos.json`, `validation/aggregate.json`, `validation/breakdown.json` (4 short names mapped); every GitHub URL in `README.md`, `CHANGELOG.md`, `research/**/*.md`, `validation/*.md`, `tests/**` and `demo/**` |
| java-vibe-guard-pro (private) | `18e585cbed5a689ba3191beb689dccc5954bca98` (master, test-corpus-3 fixes merged) | `validation/repos.json`, `validation/b0-corpus/corpus.json`; every GitHub URL in `README.md`, `CHANGELOG.md`, `cli/README.md`, `validation/**/*.md`, `cli/test-fixtures/**`, `cli/test/**` and `mcp-server/src/test/**` |
| [python-vibe-guard](https://github.com/Joaquinriosheredia/python-vibe-guard) | `1fef001d32827852ebef9090700abd6b6977a9d8` (master) | as pyvibe-pro |
| [java-vibe-guard](https://github.com/Joaquinriosheredia/java-vibe-guard) | `724b834311d3eefe7b7569252788df03dc856f75` (master) | as java-vibe-guard-pro |
| vibe-guard (coordination, private) | `6cb970e26101c1ac3bafaf32971793192b8f11f4` (main) | every GitHub URL in `docs/**/*.md` and the root `*.md` |
| vibe-guard-scan (wrapper, private) | `8422586d88547dde75fbdb288832ea60f534d11c` (main) | every GitHub URL in `*.md` and `test/**` |
| vibe-guard-evaluation (this repository) | `acbcaab57014867fcf7b3a89121d53fd640d394a` (main, with this pre-registration) | `test-corpus-3/exclusions.json` (the 1,277), `test-corpus-3/corpus-java.json` and `corpus-python.json` (**all 877 processed**); every GitHub URL in `test-corpus-1/**/*.md`, the top-level `*.md` of `test-corpus-2/`, `test-corpus-3/` and `test-corpus-4/`, every file of `calibration-*/`, and the root `*.md` |
| The audit trial of 2026-10-12 (development set) | — | `halo-dev/halo`, `YunaiV/ruoyi-vue-pro`, `open-webui/open-webui` (already in 1) |
| The "Found in the Wild" audit of OpenLegislation | — | `nysenate/OpenLegislation` (already in 1) |

- **`test-corpus-{2,3}/cards/*.md` are not read.** They quote the code of the reviewed
  repositories, and a URL inside that code is not a repository used before. The reviewed
  repositories themselves are in 1 and 2.
- Repositories owned by `Joaquinriosheredia` are excluded separately (rule b).

**Checks** (`test/units.test.mjs`) confirm that the list includes:
- all 1,277 names of test-corpus-3's list;
- all 877 repositories test-corpus-3 processed;
- all 529 repositories test-corpus-2 processed;
- all 204 repositories test-corpus-1 processed;
- the development set and OpenLegislation.

## Not excluded (`PREREGISTRATION.md`)

- **test-corpus-3 candidates that were never processed.** Nobody saw their code or their
  findings.
  - In Java, test-corpus-3 processed all 579 of its candidates, so none is left over there.
  - In Python, the candidates past its frozen batch are left over.
- Candidates of earlier corpora that were never processed, and test-corpus-1's quarantined
  accidental search, as in test-corpus-3.

## Known limit

Inherited from test-corpus-2: `research/datasets/100-repos.json` keeps only aggregates per
rule, not its full list of 100 repositories. The repositories it names are excluded. One of the
others could enter the corpus, and that cannot be detected.
