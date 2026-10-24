# Pre-registration — test-corpus-3: vibe-guard precision and noise, per language

Committed **before any rule is changed** for this measurement, and before any search,
selection, download or scan. Its sha256 is committed with it (`PREREGISTRATION.sha256`).

The text is **frozen when this directory is merged to `main`**:
- Departures go to `DEVIATIONS.md`, with the original text, the new text, what was observed
  and when.
- Both the original and the deviating evaluation are reported, and the original decides.
- Thresholds are never relaxed.

**Why there is a test-corpus-3:**
- test-corpus-2 did not meet criterion 1 in either language: Java 0.6724, Python 0.66.
- It did not meet criterion 2 in Python: 13.43 FP/1000.
- Its review set is now **development data**: the rules are fixed against it
  (`../test-corpus-2/FP-ANALYSIS.md`). A fixed rule can only be measured on repositories that
  were never used to tune it.

**Values open on purpose:** the versions under test (see "Tools under test").
- They are filled in **one commit that changes nothing else**, after the rule fixes are
  merged and released and **before any search**.
- `scripts/select.mjs` and `scripts/run.mjs` refuse to run while `FROZEN.json` holds a
  `TO-FILL` value.

## Explicit conditions

1. **Sample sizes (unchanged from test-corpus-2).**
   - **Python: n = 100** CRITICAL reviewed.
   - **Java: ≥ 50** CRITICAL reviewed, with a cap of **300** included Java repositories.
   - **If a language does not reach its sample, criterion 1 is NOT MET for that language**,
     not "pending".
   - The languages are evaluated separately. **Neither compensates for the other.**
2. **Precision (unchanged).**
   - The **primary point estimate ≥ 90 %** decides.
   - The Wilson 95 % interval and n are always published next to it.
   - **Reaching 90 % as a point estimate does NOT show with 95 % confidence that the true
     precision is ≥ 90 %.**
3. **Noise (unchanged).**
   - **FP/1000 = (FP + U) / reviewed × CRITICAL / files × 1000**, threshold **≤ 5 per
     language**.
   - U counts as FP.
   - The original D2 volume is published always and does not decide.
4. **Review method:** the one test-corpus-2 ended with (its `DEVIATIONS.md` §3, §3a and §3b),
   fixed here before anything runs.
   - Two independent sealed AI reviews, A and B.
   - Joaquín decides the disagreements and audits **20** agreeing cases.
   - **No assessment from any assistant.**
5. **New repositories only:** every repository of test-corpus-1 and test-corpus-2 is excluded.
6. **No criterion is modified after observing any result of test-corpus-3.**
7. **The rules under test are not changed during test-corpus-3.** A fix made after the
   versions are frozen does not change the measurement; if its effect is evaluated, it is
   reported as exploratory.

## Question

Definition of done criteria 1, 2 and 9 (as amended for test-corpus-2, unchanged):
- **1.** For each language, is the precision of vibe-guard's CRITICAL findings ≥ 90 %? It is
  measured on repositories never used to tune any rule, with the minimum n of that language.
- **2.** For each language, how many false CRITICAL alarms per 1,000 source files does a user
  get (FP/1000, which decides)? How many CRITICAL and WARNING findings in total (volume,
  published)?
- **9.** The precision is published with n, the review method and the confidence interval.

## Tools under test (frozen in `FROZEN.json`)

| Tool | Version | Identity checked |
|---|---|---|
| vibe-guard-scan (wrapper, private repository) | **TO-FILL** | commit, installed with `npm ci` at that commit; its lockfile pins java-vibe-guard by version and npm `integrity` |
| java-vibe-guard | **TO-FILL** | npm version and `integrity` |
| python-vibe-guard (pyvibe) | **TO-FILL** | PyPI wheel name and sha256, installed with `pip install --require-hashes` in a dedicated venv and passed with `VIBE_GUARD_PYVIBE` |

- They are the first releases that contain the fixes of `../test-corpus-2/FP-ANALYSIS.md`
  (python-vibe-guard and java-vibe-guard PRs of 2026-10-24).
- **Checked before every run** (`run.mjs`):
  - the wrapper checkout's `HEAD` equals the frozen commit;
  - `vibe-guard --version` prints exactly the frozen version line.
- Node, Python, OS and CPU are recorded in `env.txt`.
- No result is generalised beyond these versions.

### Rule changes declared before the fixes (reason from test-corpus-2)

**Demoted from CRITICAL to WARNING**, so they are no longer part of criterion 1 or 2:

| Rule | test-corpus-2 | Reason |
|---|---|---|
| PYVIBE-005 (Celery task without a time limit) | 0 TP / 13 | 13 FPs were Procrastinate tasks taken for Celery. Beyond that detection bug, the rule cannot see a global `task_time_limit`, and a missing per-task limit only hurts if the wrapped work never returns. The rule cannot show that. |
| PYVIBE-013 (`asyncio.gather` without `return_exceptions`) | 2 TP / 10 | 8 FPs: the gathered awaitables contain their exceptions in other functions or modules, or an enclosing `gather` collects them. This cannot be decided within one file. |

**No rule is eliminated.**

**The other rules stay CRITICAL** and are narrowed as listed in `FP-ANALYSIS.md` §1:
- PYVIBE-008/009 and every blocking rule: the `asyncio.run()` entry coroutine becomes
  WARNING.
- PYVIBE-011: `waitpid` with `WNOHANG`.
- PYVIBE-017: an enclosing handler that re-raises.
- PYVIBE-018: a bounded "first free name" search.
- `transactions`: string literals and `@interface`.
- `blocking`: Spring's `@Scheduled` only, and start-up `@EventListener` events become WARNING.

The messages are reworded as in `FP-ANALYSIS.md` §2. Each narrowing has a regression test
that reproduces its test-corpus-2 FP. What exactly is under test is the frozen versions.

## Populations and search (fixed before any search)

**The search, pools, code-signal gate, ordering, toy filter and exclusions b–g are those of
test-corpus-2** (`../test-corpus-2/PREREGISTRATION.md`, "Populations and search"), word for
word, with the changes below:
- Java pool: the same 11 topic queries, `stars:>=50`.
- Python: python-A (`topic:fastapi`, `stars:>=100`), then python-B (fastapi, aiohttp,
  starlette, litestar, sanic, quart; `stars:>=50`) only after python-A is exhausted.
- `size:100..1000000`, `pushed:>=<D>`.
- `<D>` = the selection date (UTC) minus 183 days.
- Every query runs once, at selection time.

### Changes from test-corpus-2

- **Exclusion a (used before)** is `exclusions.json` of this directory. `scripts/build-exclusions.mjs`
  builds it from pinned local sources and makes no network call. It is the union of:
  1. `../test-corpus-2/exclusions.json` (1,021 repositories: test-corpus-1, its processed
     repositories, development labels and sets, and the GitHub URLs pinned there);
  2. **every repository test-corpus-2 processed**, included and excluded:
     `../test-corpus-2/corpus-java.json` and `corpus-python.json`, `processed[]`, 529
     repositories;
  3. every GitHub URL in the docs, READMEs, fixtures and tests of python-vibe-guard,
     java-vibe-guard, vibe-guard, vibe-guard-scan and vibe-guard-evaluation, at the commits
     frozen in `FROZEN.json` (or their `main`/`master` at that time). This includes the
     regression tests written from test-corpus-2.

  Matching is by GitHub repository id after `GET /repos` (renames followed), or by
  case-insensitive `full_name`.
- **Not excluded:** test-corpus-2 candidates that were never processed. Nobody saw their code
  or findings.
  - Excluding every candidate would leave almost nothing: the queries are the same and are
    capped at 1,000 results.
  - Since the processed ones are excluded, the new pool continues down each query's star
    ranking.

### Pinned commit, run, stopping rule

As in test-corpus-2 ("Pinned commit", "Run", "Stopping rule"):
- the SHA of the default branch when processed;
- the default `vibe-guard scan` with the defaults a user gets;
- a pool measures only its own language;
- Java: first batch of 25 included, then batches of 25, frozen at ≥ 50 Java CRITICAL, cap 300;
- Python: first batch of 20 included, then batches of 10, frozen at ≥ 100 Python CRITICAL,
  cap 150;
- no finding is reviewed before both pools are frozen;
- Java phase 2 as in test-corpus-2, and it never changes the verdict.

## Review set and seeds (fixed here)

| Use | Seed |
|---|---|
| Review set: one `random.Random`, Java first, then Python; every CRITICAL if ≤ 100, else `.sample` of 100 | **20261101** |
| Clustering cap of 10 per repository (informational) | **20261102** |
| Repository bootstrap of FP/1000 (2,000 resamples, informational) | **20261103** |
| Audit sample: `random.Random(s).sample(agreeing, 20)`, `agreeing` in review-set order, listed in review-set order | **20261104** |
| Order of Joaquín's sheet: the reviewed IDs in review-set order, `random.Random(s).shuffle` | **20261105** |

- Unit, sorting and numbering (J001…, P001…) are as in test-corpus-2.
- **Required reviewed:** Python 100, Java 50; fewer means criterion 1 is NOT MET for that
  language.
- Repeatability is not part of this method.

## Verdicts

The rules of test-corpus-2 apply **unchanged**: TP / FP / U from Detection, Context and
Reachability. They are in its "Verdicts" section, with its rule-criteria table, and the
demoted rules are no longer reviewed.
- U when the repository does not let them be decided.
- Message accuracy (`overstated`) recorded apart.

## Review method (test-corpus-2 `DEVIATIONS.md` §3, §3a, §3b, fixed before the run)

**Cards:** generated by `scripts/cards.py` exactly as in test-corpus-2:
- the whole enclosing function;
- every literal match of its name, with path class;
- binary matches as rows; records split on `\n` only.

They are generated once, and the sha256 of `cards/SHA256SUMS` is committed before any review.

**Review A and review B:**
- Two independent AI reviews of the whole review set, each in its own sessions. Neither sees
  the other, Joaquín's verdicts, or any test-corpus-2 verdict or analysis.
- **Models:** A = **Claude Opus 5.5** (`claude-opus-5-5`), B = **Claude Sonnet 5.5**
  (`claude-sonnet-5-5`).
- **Instructions:** both receive the same `REVIEW-AI-INSTRUCTIONS.md`. It is test-corpus-2's
  `REVIEW-B-INSTRUCTIONS.md` with only the paths changed and test-corpus-2's known reviewer
  failures added to the warning. It is committed before review A starts.
- **Output:** `audit-claude-A.json` and `audit-claude-B.json`, in the verdict format.
  - They are kept outside the repository, and only their sha256 is committed, both before
    either is opened.
  - They are committed after Joaquín's verdicts and must match the hashes.
- **"A = B"** compares the `verdict` field (TP/FP/U).

**Opening:**
- Both files are checked against their hashes.
- `REVIEW-AB.md` lists counts and IDs only, never a verdict:
  - the disagreeing IDs;
  - the audit sample of 20 agreeing IDs (seed above).

**Joaquín:**
- He reviews the disagreements and the 20 audit IDs, without seeing A or B.
- `REVIEW-SHEET.md` holds only those IDs, in the shuffled order (seed above), with no group
  labels.
- The converter produces `audit-joaquin.json`.

**Final verdict:**
- Joaquín's where he reviewed;
- otherwise the A = B verdict;
- `overstated`: yes if A or B says yes, Joaquín's flag where he reviewed.

**Audit rule:**
- If Joaquín changes **≥ 3 of the 20** (a change = his verdict differs from A = B), the AI
  review is **NOT RELIABLE** and **criterion 1 is NOT MET in both languages**.
- The change rate is published with its Wilson 95 % interval, in total and per language.

**Assistance during the review:**
- Only **factual navigation** is allowed: where a file is, what a line contains, what a search
  returns.
- **Never** a verdict, an assessment, an opinion on a case, or a provisional precision or
  percentage.
- Every piece of help, from any Claude session or other AI (Joaquín's adviser included), is
  logged in `REVIEW-LOG.md` with its date, question and answer.
- **If an assessment is given anyway** (pre-registered from test-corpus-2 §3b):
  - every verdict given after it on the cases it touched is marked **"assisted"** in
    `REVIEW-LOG.md`;
  - `evaluate.py` computes criteria 1 and 2 **(a)** with all verdicts and **(b)** with the
    assisted audit IDs left out of the audit, where they keep the A = B verdict, and the
    assisted disagreements counted as **U**;
  - in (b) the audit threshold is proportional: **⌈3·n/20⌉** changes of the remaining n;
  - if a criterion's conclusion differs between (a) and (b), **the less favourable is taken**;
  - both are published, and so is any language left with no audit case in (b).

**Published:**
- "reviewed by two independent AIs; disagreements and a sample of 20 audited by the author";
- A–B agreement and Cohen's kappa;
- the disagreements;
- the corrections in the audit, Z/20;
- the number of `overstated` disputes set to yes.

## Metrics and acceptance criteria (`scripts/evaluate.py`), per language

As in test-corpus-2, unchanged:
- **Precision:** primary = TP / (TP + FP + U), secondary = TP / (TP + FP), Wilson 95 % for
  both.
- **Criterion 1:** MET for a language if, and only if, the required n was reviewed **and**
  the primary point estimate ≥ 90.0 % **and** the audit rule did not declare the AI review
  NOT RELIABLE.
- **Criterion 2:** MET if the point estimate of FP/1000 ≤ 5.0, with CRITICAL and files counted
  over the frozen pool.
  - Also published: the Wilson-scaled interval, the repository bootstrap and FP/1000
    without U.
- **Volume (D2):** published always, does not decide.
- **"Finding" and "file":** as in test-corpus-2.
- **Informational, never deciding:**
  - precision per rule, repository, Java family and Python subpool;
  - precision with each repository capped at 10;
  - messages overstated;
  - A–B agreement.

`evaluate.py` writes `metrics.json` and renders `METRICS.md`.

## Scripts

- The scripts and tests are test-corpus-2's, copied into this directory with only these
  changes:
  - the paths;
  - the seeds above;
  - the exclusion sources;
  - the review files (`audit-claude-A.json`, `audit-claude-B.json`);
  - the (a)/(b) rule applied only when `REVIEW-LOG.md` marks assisted IDs.
- They are committed, with their tests, **after this pre-registration and before
  `FROZEN.json` is filled**. Nothing runs before that.
- Every script acts only when executed directly (test-corpus-1 `DEVIATIONS.md` §1).

## Freezing rule

**No acceptance criterion, threshold, sample size, query, gate, seed, verdict rule or review
rule is modified after observing any result of test-corpus-3.**
- A result is a search output, a scan output, a count or a verdict.
- A criterion that is not met is documented as NOT MET; it is never adjusted.
- Any departure goes to `DEVIATIONS.md`.

## Known limits (stated in the results)

- **Every limit of test-corpus-2 applies:**
  - self-assigned topics;
  - the 1,000-result cap;
  - popularity bias;
  - a lexical toy filter;
  - a directed Java pool that requires `spring-boot`;
  - the limits of the literal caller search.
- **The fixes were designed on test-corpus-2.** A pattern that test-corpus-2 did not contain
  is not covered by them.
- Excluding the 529 processed repositories pushes the new pools further down the star ranking
  than test-corpus-2's.
- With fewer Java CRITICAL rules firing (`@Scheduled` narrowed), **Java may need more
  repositories to reach 50**, within the same cap of 300.
- **Both AI reviews are Claude models.** Their errors may be correlated: test-corpus-2's A–B
  kappa was 0.90, while the audit changed 3 of 20.

## Files

| File | What | When |
|---|---|---|
| `PREREGISTRATION.md`, `PREREGISTRATION.sha256` | this pre-registration | now, before any rule change |
| `scripts/`, `test/`, `FROZEN.json` (`TO-FILL`), `EXCLUSION-SOURCES.md`, `exclusions.json`, `REVIEW-AI-INSTRUCTIONS.md` | the method's code and inputs | after this commit, before the versions are filled |
| `FROZEN.json` (filled) | versions under test | after the fixes are released, before the search |
| `search-raw/`, `exclusions-resolved.json`, `candidates.json` | search and ordering | `select.mjs`, once |
| `corpus-java.json`, `corpus-python.json`, `results/<pool>/`, `env.txt` | runs and stopping | `run.mjs` |
| `review-set.json`, `cards/`, `cards/SHA256SUMS` (hash committed) | review set and cards | after both pools are frozen |
| `audit-claude-A.sha256`, `audit-claude-B.sha256`, then the files | the AI reviews | hashes before opening; files after Joaquín |
| `REVIEW-AB.md`, `REVIEW-SHEET.md`, `REVIEW-LOG.md`, `audit-joaquin.json` | opening, Joaquín's review, help received | review |
| `metrics.json`, `METRICS.md`, `RESULTS.md`, `DEVIATIONS.md` | results | `evaluate.py` |
