# Pre-registration — test-corpus-4: vibe-guard precision and noise, per language

Committed **before any search, selection, download, scan or review** of test-corpus-4. Its
sha256 is committed with it (`PREREGISTRATION.sha256`).

The text is **frozen when this directory is merged to `main`**:
- Departures go to `DEVIATIONS.md`, with the original text, the new text, what was observed
  and when.
- Both the original and the deviating evaluation are reported, and the original decides.
- Thresholds are never relaxed.

**Why there is a test-corpus-4:**
- test-corpus-3 did not meet criterion 1 in either language (`../test-corpus-3/METRICS.md`):
  - Java 0.6667, with n 24 of the 50 required: its candidates ran out;
  - Python 0.77;
  - the AI review was declared NOT RELIABLE (Joaquín changed 5 of the 20 audited).
- Its review set is now **development data**: the rules were fixed against it
  (`../test-corpus-3/FP-ANALYSIS.md`), so they can only be measured on repositories never
  used to tune them.
- The verdict criterion is now written down: `../REVIEW-CRITERIA.md` v1.

**Changes from test-corpus-3**, each detailed below:
1. **Official metric:** only Joaquín's own review of **every** CRITICAL in the review set.
   No AI review is required, and none decides anything.
2. **Verdict criterion:** REVIEW-CRITERIA.md v1. §1, §5 and exclusion c2 are copied
   verbatim, and the version is cited.
3. **Tools:** commits of the private engines `pyvibe-pro` and `java-vibe-guard-pro`, plus the
   wrapper `vibe-guard-scan`. Each has an annotated tag, and the wheel/tgz built locally is
   identified by its sha256.
4. **Java search widened**, with queries fixed here; the Java cap is now 500 included
   repositories.
5. **Optional AI review**, for comparison only: sealed before Joaquín starts, it never
   decides.
6. **Severity changes since test-corpus-3** are declared below.
7. **New seeds.**

**Values open on purpose:** the identities of the tools under test ("Tools under test").
- They are filled in **one commit that changes nothing else**, after Joaquín has tagged the
  three repositories and **before any search**.
- `scripts/select.mjs` and `scripts/run.mjs` refuse to run while `FROZEN.json` holds a
  `TO-FILL` value.

## Explicit conditions

1. **Sample sizes.**
   - **Python: n = 100** CRITICAL reviewed.
   - **Java: ≥ 50** CRITICAL reviewed, with a cap of **500** included Java repositories.
   - **If a language does not reach its sample, criterion 1 is NOT MET for that language**,
     not "pending", and no deviation is opened to extend it.
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
   - Volume (D2) is always published and does not decide.
4. **Review method:** **Joaquín reviews every finding in the review set himself.** His
   verdicts are the only ones that enter the metrics. **No assessment from any assistant**
   (see "Assistance during the review").
5. **New repositories only:** every repository of test-corpus-1, test-corpus-2 and
   test-corpus-3, and every repository any of them processed, is excluded (exclusion a).
6. **No criterion is modified after observing any result of test-corpus-4.**
7. **The rules under test do not change during test-corpus-4.** A fix made after the
   versions are frozen does not change the measurement. If its effect is evaluated, it is
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

| Tool | Identity (all **TO-FILL** until Joaquín tags) | Checked before every run (`run.mjs`) |
|---|---|---|
| pyvibe-pro (private repository; package `python-vibe-guard`) | annotated tag, commit, the wheel file name and its sha256 | the wheel is built locally from the tagged commit; installed with `pip install --require-hashes` in a dedicated venv and passed to the wrapper with `VIBE_GUARD_PYVIBE` |
| java-vibe-guard-pro (private repository; package `java-vibe-guard`) | annotated tag, commit, the `.tgz` file name, its sha256 and its npm `integrity` (sha512) | the `.tgz` is built locally from the tagged commit with `npm pack`; the wrapper's lockfile pins it by that `integrity` |
| vibe-guard-scan (wrapper, private repository) | annotated tag, commit, exact `vibe-guard --version` line | installed with `npm ci` at that commit |

**Checks:**
- Each tag is **annotated** (`git cat-file -t <tag>` = `tag`), and each tag resolves to the
  frozen commit.
- The wrapper checkout's `HEAD` equals the frozen commit.
- `vibe-guard --version` prints exactly the frozen line.
- The sha256 of the wheel and of the `.tgz` actually installed equal the frozen values.

**Build record:** the build commands, tool versions (Python `build`, npm) and the resulting
hashes go to `BUILD.md` when `FROZEN.json` is filled. Node, Python, OS and CPU go to `env.txt`.

**No result is generalised beyond these builds.**

### Severity and rule changes since test-corpus-3 (declared before the freeze)

test-corpus-3 measured python-vibe-guard 0.15.0 and java-vibe-guard 3.0.0 (wrapper 0.3.0,
`66ec8f4`). The engines under test add the fixes of `../test-corpus-3/FP-ANALYSIS.md`, which
are merged in:
- `pyvibe-pro` master `ec317f9c1c4fd0d269913079413c561b483e925d` (PR #1);
- `java-vibe-guard-pro` master `18e585cbed5a689ba3191beb689dccc5954bca98` (PR #1).

The frozen commits must be these, or descendants whose only further changes are release
metadata: version, changelog, tags. **Any other rule change goes to `DEVIATIONS.md` before
`FROZEN.json` is filled**, with the reason.

**Demoted from CRITICAL to WARNING** (no longer part of criterion 1 or 2):

| Rule / scope | What changes | Reason (test-corpus-3) |
|---|---|---|
| **PYVIBE-009** (`open()` in `async def`, synchronous file I/O) | the whole rule is WARNING | the author judged the impact overstated in 11 of 12 TPs; 9 of 56 were FPs by reachability that no AST check can see (P024, P045–P049, P051–P053) |
| **Java non-production modules** (`blocking`, `blocking-kafka`, `kafka-send-timeout`) | WARNING when the module directory, before the first `src/` segment, is named playground, demo, example or sample (`playgrounds/`, `hp-demo/`, `foo-examples/`); the directory is named in the message; Java packages are never read | J002, J004–J006 (axelix `playgrounds/`), J014, J015 (hp-soa `hp-demo/`) |
| **Python non-production paths** | `scratch/` and `.scratch/` join the non-production path segments (WARNING) | P094, P095 (PYVIBE-008 in a manual script) |
| **PYVIBE-017** (empty `except BaseException` around an `await`) | WARNING when the `try` only reaps a task that this coroutine cancelled or waits for until done; still CRITICAL inside a handler of the coroutine's own cancellation that does not re-raise | P035, P063, P077, P078 |
| **PYVIBE-006** (`ContextVar.set()` without reset) | WARNING when the module sets the variable back to its default elsewhere | P023, P039 |

**No longer reported:**
- **PYVIBE-006:**
  - a `set()` of the declared constant default (P099);
  - a `set()` whose token is stored on an attribute that a `finally` of the module passes to
    `reset()` (P043, P025).
- **`blocking`:** a Spring `@Async` method called only from its own class (unqualified or via
  `this`) is no longer an anchor (J009).

**Unchanged and still CRITICAL:**
- PYVIBE-001/002/004/007/008/010/011/016/018. This includes PYVIBE-008, `sqlite3.connect`,
  which is also synchronous I/O but was **not** demoted.
- PYVIBE-012/014, PYVIBE-003/015, PYVIBE-019.
- Java `transactions` and `reactor-block`.
- PYVIBE-018's drain loop (P073, P097) and PYVIBE-012 (P026) were not fixed.

**Carried over from test-corpus-3 unchanged:** the demotions and narrowings declared in
`../test-corpus-3/PREREGISTRATION.md`:
- PYVIBE-005 and PYVIBE-013 are WARNING;
- start-up `asyncio.run()` entry coroutines are WARNING;
- the PYVIBE-011/017/018 and `transactions`/`blocking` narrowings.

**No rule is eliminated:** every change above keeps the finding as a WARNING or removes only
a non-anchor.

## Verdict criterion: REVIEW-CRITERIA.md v1

The verdicts follow **`REVIEW-CRITERIA.md` version v1** (2026-10-28):
- vibe-guard-evaluation commit `bc0a3c6`;
- file sha256 `c1ff60e770e586f3afbc99d8121f72cfab6f77ef0c4a92a2883e057f34e1b77d`.

How the parts apply:
- §1 (the three conditions) and §5 (rule criteria) are copied **verbatim** in the appendix.
  A test (`test/units.test.mjs`) checks they match the file at that commit byte for byte.
- §2 and §3, which §1 and §5 refer to, apply as written in that version of the file.
- §6 does not apply: it re-labels earlier corpora only.
- Rules demoted to WARNING are not reviewed. A rule not listed in §5 falls back to §1.
- U when the repository does not let a condition be decided.
- **Overstated** is recorded apart and never makes a finding FP.

## Populations and search (fixed before any search)

`scripts/select.mjs` runs **once**, after this pre-registration is merged and `FROZEN.json`
is filled. It uses the GitHub REST repository search (`GET /search/repositories`) with:
- `sort=stars`, `order=desc`, 100 per page, up to the API cap of 1,000 results per query;
- throttling within the API rate limit.

Raw responses, UTC times and `total_count` per query go to `search-raw/`. A query whose
`total_count` exceeds 1,000 is recorded as **truncated**; it is not split further.

Every query of every pool runs at selection time, once. No search runs later.

Common qualifiers (`<D>` = the selection date in UTC minus 183 days, `YYYY-MM-DD`):

    Q_JAVA = language:Java fork:false archived:false is:public size:100..1000000 pushed:>=<D>
    Q_PY   = language:Python fork:false archived:false is:public size:100..1000000 pushed:>=<D>

### Java pool (directed sample, not representative of all Java)

test-corpus-3 ran out of Java candidates:
- 579 processed, of which 256 were used before;
- 60 included, giving 24 CRITICAL.

The pool is therefore widened with more topics and lower star bands. Two topic sets:

    T1 = spring-boot, spring-kafka, kafka, apache-kafka, spring-webflux, webflux,
         project-reactor, reactor, reactive, spring-cloud, microservices          (test-corpus-3's 11)
    T2 = spring, spring-boot-3, spring-cloud-stream, kafka-streams, kafka-consumer,
         kafka-producer, event-driven, event-driven-architecture, event-sourcing, cqrs,
         r2dbc, reactive-programming, reactive-streams, rsocket                     (14 new)

Four subpools, each one query per topic, in this order:

| Subpool | Query, for each topic `<T>` in the order listed | Topics | Queries |
|---|---|---|---|
| java-A | `topic:<T> Q_JAVA stars:>=50` | T1 | 11 |
| java-B | `topic:<T> Q_JAVA stars:>=50` | T2 | 14 |
| java-C | `topic:<T> Q_JAVA stars:20..49` | T1 then T2 | 25 |
| java-D | `topic:<T> Q_JAVA stars:10..19` | T1 then T2 | 25 |

- **75 queries.** A repository belongs to the first subpool, in the order A, B, C, D, whose
  query it matches. Every query it matched is recorded.
- Results are also published per subpool.

**Code-signal gate (exclusion g)**, unchanged from test-corpus-2/3:
- checked on the checkout at the pinned commit, before the scan;
- at least one family of ASYNC (`@EnableAsync` and `@Async`), KAFKA (`KafkaTemplate`
  import, `@KafkaListener`, or `KafkaProducer`/`Producer` import) or REACTOR (`Mono`/`Flux`/`*`
  import of `reactor.core.publisher`);
- regular expressions as in `../test-corpus-3/scripts/count-files.mjs` (`JAVA_SIGNAL_RES`).

### Python pool (unchanged from test-corpus-3)

- **python-A:** `topic:fastapi Q_PY stars:>=100`.
- **python-B**, only after python-A is exhausted: `topic:<T> Q_PY stars:>=50`, with `<T>` ∈
  fastapi, aiohttp, starlette, litestar, sanic, quart (in this order).

### Ordering (`candidates.json`, frozen)

- Within a subpool, the union of its queries is taken by repository id and ordered by
  `stargazers_count` descending as returned at search time, ties by `full_name` ascending
  (case-insensitive).
- Subpools are concatenated in order:
  - Java: A, B, C, D;
  - Python: A, B.
- **The file is frozen:** the search is not re-run, and every batch takes the next
  candidates from it.

### Exclusions, applied in this order (each recorded with its reason)

**a. Used before:** the repository is in **`exclusions.json`**.
- `scripts/build-exclusions.mjs` builds it from the pinned local sources in
  `EXCLUSION-SOURCES.md`. It reads only git objects and makes no network call.
- It is the union of:
  1. `../test-corpus-3/exclusions.json` (1,277 repositories). It covers test-corpus-1 and
     test-corpus-2, every repository they processed, the development labels and sets, and
     the GitHub URLs pinned there.
  2. **Every repository test-corpus-3 processed**, included and excluded:
     `../test-corpus-3/corpus-java.json` (579) and `corpus-python.json` (298), `processed[]`.
  3. Every GitHub URL in the docs, READMEs, fixtures and tests of: pyvibe-pro,
     java-vibe-guard-pro, python-vibe-guard, java-vibe-guard, vibe-guard, vibe-guard-scan
     and vibe-guard-evaluation. They are read at the commits in `FROZEN.json` (or each
     repository's `main`/`master` at that time). This includes the regression tests written
     from test-corpus-3 and the calibration directories.
- Matching is by GitHub repository id after `GET /repos` (renames followed), or by
  case-insensitive `full_name`.
- **Not excluded:** test-corpus-3 candidates that were never processed. Nobody saw their code
  or findings.

**b. Owned by `Joaquinriosheredia`.**

**c. Toy repositories (unchanged):** a token of the name or of the description is in the
fixed list of test-corpus-1. Tokens are split on camelCase boundaries and on every
non-alphanumeric character, then lowercased:

    tutorial tutorials example examples sample samples demo demos course courses workshop
    boilerplate template templates starter starters scaffold interview exercise exercises
    homework awesome cheatsheet kata playground bootcamp

**c2. Study repositories (new):** REVIEW-CRITERIA.md v1 §2.4, verbatim:

<!-- BEGIN VERBATIM REVIEW-CRITERIA.md v1 (bc0a3c6) §2.4 exclusion c2 -->
**Exclusion c2 — study repositories.** A candidate is excluded when any of these holds
(case-insensitive):

1. **Name:** the **last** token of the repository name, split on non-alphanumeric
   characters only (not on camelCase), is `study`, `studies`, `learning` or `notes`, and the
   token before it is not one of `machine deep reinforcement federated transfer meta active
   contrastive online incremental`.
2. **Description:** its tokens (split as in the toy filter) contain one of the consecutive
   pairs `study notes`, `learning notes`, `for learning`, `for study`, `learning purpose`,
   `learning purposes`, `learning project`, `study project`; or the description contains
   one of the substrings `学习笔记`, `学习记录`, `学习项目`, `练手`.
3. **Topics:** a topic is exactly `study`, `studies`, `study-notes`, `learning-notes` or
   `notes`.
<!-- END VERBATIM -->

Name, description and topics are those of the search response (`name`, `description`,
`topics`).

**d. Pool overlap:**
- A repository in the Java pool is kept there only.
- A repository in python-A is not repeated in python-B.
- Within Java, it stays in its first subpool.

**e. Stack not present at the pinned commit** (unchanged), checked on the checkout before the
scan with `scripts/count-files.mjs`:
- Java: no `pom.xml`, `build.gradle` or `build.gradle.kts` containing `spring-boot`, or fewer
  than 20 `.java` files.
- python-A: no `.py` line starting `from fastapi` / `import fastapi`, or fewer than 20 `.py`
  files.
- python-B: no such line for any of its six frameworks, or fewer than 20 `.py` files.

**f. Cannot be fetched, the scan exits 2, or it times out:** the error is recorded and the
repository is **replaced** by the next candidate, because no finding was observed.

**g. Java only:** no code-signal family (above).

### Pinned commit, run, stopping rule

As in test-corpus-2/3:
- **Pinned commit:** the SHA of the default branch when the repository is processed.
- **Run:** the default `vibe-guard scan` with the defaults a user gets. Exit 0 or 1 is
  valid; exit 2 is f. The timeout is 30 minutes per repository.
- A pool measures **only its own language**.
- Checkouts are kept only for repositories with a CRITICAL of the pool's language.

**Stopping rule** (per pool, decided by counts only, never by verdicts):

| Pool | First batch | Next batches | Frozen when | Cap |
|---|---|---|---|---|
| Java | 25 included | 25 included | ≥ **50** Java CRITICAL | **500** included repositories |
| Python | 20 included | 10 included | ≥ **100** Python CRITICAL | **150** included repositories |

- A pool that reaches its cap or runs out of candidates is frozen with the count reached.
  **Criterion 1 is then NOT MET for that language.** This is reported with the count. No
  deviation, extension or later phase changes it.
- The pools stop independently.
- **No finding is reviewed before both pools are frozen.**

The expected yield is not a criterion. From test-corpus-3's 0.40 Java CRITICAL per included
repository, about 125–150 included repositories are needed, and the demotions above lower
that rate. Python reached 102 CRITICAL with 20 repositories, 57 of them PYVIBE-009, now
WARNING.

## Review set and seeds (new, fixed here)

| Use | Seed |
|---|---|
| Review set: one `random.Random`, Java first, then Python; per language every CRITICAL if ≤ 100, else `.sample` of 100 | **20261201** |
| Clustering cap of 10 per repository (informational) | **20261202** |
| Repository bootstrap of FP/1000 (2,000 resamples, informational) | **20261203** |
| Order of Joaquín's sheet: the review-set IDs in review-set order, `random.Random(s).shuffle` | **20261204** |

- Unit, sorting and numbering (J001…, P001…) are as in test-corpus-2/3.
- **Required reviewed:** Python 100, Java 50. Fewer means criterion 1 is NOT MET for that
  language.
- Repeatability is not part of this method.

## Review method

**Cards:**
- Generated by `scripts/cards.py` as in test-corpus-3: the whole enclosing function, and
  every literal match of its name with its path class.
- Generated once. The sha256 of `cards/SHA256SUMS` is committed before any review.

**Joaquín** reviews **every** ID of the review set:
- `REVIEW-SHEET.md` lists them in the shuffled order (seed above), with no rule-group labels
  beyond the card.
- His verdicts follow REVIEW-CRITERIA v1: TP / FP / U, the condition that fails for an FP,
  and Overstated.
- The converter produces `audit-joaquin.json` with a `file:line` reason per verdict. Its
  sha256 is committed when he finishes, before `evaluate.py` runs.

**Final verdict:** Joaquín's, for every ID. **No other verdict enters criteria 1, 2 or 9.**

**Assistance during the review:**
- Only **factual navigation** is allowed: where a file is, what a line contains, what a
  search returns, what a deterministic callers tool lists.
- **Never** a verdict, an assessment, an opinion on a case, or a provisional precision or
  percentage.
- Every piece of help, from any Claude session or other AI (Joaquín's adviser included), is
  logged in `REVIEW-LOG.md` with its date, the IDs it concerns, the question and the answer.
- **If an assessment is given anyway:**
  - every verdict given after it on the cases it touched is marked **"assisted"** in
    `REVIEW-LOG.md`;
  - `evaluate.py` computes criteria 1 and 2 **(a)** with all verdicts and **(b)** with the
    assisted verdicts counted as **U**;
  - if a criterion's conclusion differs between (a) and (b), **the less favourable is
    taken**;
  - both are published.

### Optional AI review (comparison only, never decides)

An AI review of the review set may be run, but only under all of these conditions; otherwise
test-corpus-4 has none.
- **Before it runs**, the following are committed:
  - the tool (vibe-guard-scan `vibe-guard review` at a tagged commit) and the protocol;
  - the models;
  - the instructions file (`../REVIEW-AI-INSTRUCTIONS.md` v1) with its sha256;
  - the few-shot file, if any, with its sha256. It may hold development data only (test-corpus-2/3), **never test-corpus-4**.
- **It is sealed before Joaquín starts:**
  - its outputs are kept outside the repository;
  - their sha256 is committed **before `REVIEW-SHEET.md` is delivered to Joaquín**;
  - an AI review not sealed by then is not run for test-corpus-4.
- **Nobody opens the outputs** (Joaquín, or anyone or anything assisting him) until
  `audit-joaquin.json` and its sha256 are committed. Then the files are committed and must
  match their hashes.
- **It never decides:** not a verdict, not criterion 1, 2 or 9, not a tie-break.
- **Published, informative:**
  - agreement with Joaquín's verdict (TP/FP/U), per configuration (A, A+B if run) and per
    language, with Wilson 95 % and n;
  - an invalid or missing answer counts as disagreement;
  - Cohen's kappa;
  - the disagreeing IDs.
- **Informative reliability threshold: agreement ≥ 95 %** (point estimate) with Joaquín, per
  language. Meeting it says only that, on this corpus, the AI review agreed that often. It
  does **not** make the AI review a measurement method for this or any later corpus without
  a new pre-registration.

## Metrics and acceptance criteria (`scripts/evaluate.py`), per language

As in test-corpus-3, without the audit rule:
- **Precision:**
  - primary = TP / (TP + FP + U);
  - secondary = TP / (TP + FP);
  - Wilson 95 % for both.
- **Criterion 1:** MET for a language if, and only if, the required n was reviewed by
  Joaquín **and** the primary point estimate ≥ 90.0 %.
- **Criterion 2:** MET if the point estimate of FP/1000 ≤ 5.0, with CRITICAL and files
  counted over the frozen pool. Also published:
  - the Wilson-scaled interval;
  - the repository bootstrap;
  - FP/1000 without U.
- **Volume (D2):** always published, does not decide.
- **"Finding" and "file":** as in test-corpus-2/3.
- **Informational, never deciding:**
  - precision per rule, repository, Java family, Java subpool (A–D) and Python subpool;
  - precision with each repository capped at 10;
  - messages Overstated;
  - the optional AI comparison.

`evaluate.py` writes `metrics.json` and renders `METRICS.md`.

## Scripts

- The scripts and tests are test-corpus-3's, copied into this directory with only these
  changes:
  - the paths;
  - the seeds;
  - the exclusion sources;
  - the Java subpools and cap;
  - exclusion c2;
  - the identity checks of `FROZEN.json` (annotated tags, wheel/tgz sha256);
  - no AI audit, and the optional AI comparison.
- They are committed, with their tests (including the verbatim check of the appendix and
  unit tests of c2), **after this pre-registration and before `FROZEN.json` is filled**.
  Nothing runs before that.
- Every script acts only when executed directly.

## Freezing rule

**No acceptance criterion, threshold, sample size, query, gate, exclusion, seed, verdict
rule or review rule is modified after observing any result of test-corpus-4.**
- A result is a search output, a scan output, a count or a verdict.
- A criterion that is not met is documented as NOT MET; it is never adjusted.
- Any departure goes to `DEVIATIONS.md`.

## Known limits (stated in the results)

- **The limits of test-corpus-2/3 apply:**
  - self-assigned topics;
  - the 1,000-result cap per query;
  - popularity bias;
  - a lexical toy filter;
  - a directed Java pool that requires `spring-boot` and a code-signal family;
  - the limits of the literal caller search.
- **The Java pool now reaches down to 10 stars and 14 more topics.** It is less selected for
  popularity and more likely to hold small or personal projects that filters c and c2 do not
  catch.
- **The fixes were designed on test-corpus-3.** A pattern it did not contain is not covered.
- **One reviewer:** the official metric rests on Joaquín's judgement alone, with
  REVIEW-CRITERIA v1 as the written rule. There is no second human reviewer.
- **Private engines:** `pyvibe-pro` and `java-vibe-guard-pro` are private; the results apply
  to the builds identified in `FROZEN.json`, not to any public release.

## Files

| File | What | When |
|---|---|---|
| `PREREGISTRATION.md`, `PREREGISTRATION.sha256` | this pre-registration | now, before anything runs |
| `FROZEN.json` (`TO-FILL`) | tool identities to fill | with this pre-registration |
| `scripts/`, `test/`, `EXCLUSION-SOURCES.md`, `exclusions.json` | the method's code and inputs | after this commit, before the identities are filled |
| `FROZEN.json` (filled), `BUILD.md` | tagged commits, wheel/tgz hashes | after Joaquín tags, before the search |
| `search-raw/`, `exclusions-resolved.json`, `candidates.json` | search and ordering | `select.mjs`, once |
| `corpus-java.json`, `corpus-python.json`, `results/<pool>/`, `env.txt` | runs and stopping | `run.mjs` |
| `review-set.json`, `cards/`, `cards/SHA256SUMS` (hash committed) | review set and cards | after both pools are frozen |
| `ai-review.sha256` (optional), then the files | the sealed AI comparison | hashes before `REVIEW-SHEET.md`; files after `audit-joaquin.json` |
| `REVIEW-SHEET.md`, `REVIEW-LOG.md`, `audit-joaquin.json`, `audit-joaquin.sha256` | Joaquín's review, help received | review |
| `metrics.json`, `METRICS.md`, `RESULTS.md`, `DEVIATIONS.md` | results | `evaluate.py` |

## Appendix — REVIEW-CRITERIA.md v1, verbatim (commit `bc0a3c6`)

<!-- BEGIN VERBATIM REVIEW-CRITERIA.md v1 (bc0a3c6) §1 -->
## 1. The three conditions

- **TP** when all three hold, each with `file:line` evidence opened at the pinned commit:
  1. **Detection:** the pattern the rule names is there.
  2. **Context:** the conditions the rule's impact needs hold there (§3 and §5).
  3. **Reachability:** the code runs in the normal operation of an application (§2).
- **FP** when the repository shows that one of 1–3 is false.
- **U** when the repository does not let 1–3 be decided (the caller, the thread or the
  configuration lives outside it).
- **Overstated** is recorded apart and is never a reason for FP. Of the 12 calibration
  failures that Joaquín judged TP, 7 are TP *and* Overstated.
<!-- END VERBATIM -->

<!-- BEGIN VERBATIM REVIEW-CRITERIA.md v1 (bc0a3c6) §5 -->
## 5. Rule criteria v1 (condition 2)

The test-corpus-2/3 table, with the v1 changes in **bold**.

| Rule | TP context | FP context (examples, not exhaustive) |
|---|---|---|
| `blocking`, `blocking-kafka` | the blocking call runs on the anchored pool (an `@Async` executor with `@EnableAsync`, a scheduler, an event, a Kafka listener thread) on a normal path | the anchor is inert, or the call does not block (a completed future); **a designed wait on the scheduler thread with no starvation (§3.1)** |
| `kafka-send-timeout` | an untimed `.send(..).get()` on a normal path | the producer is configured so the call cannot wait beyond the message's bound |
| `transactions` (critical) | `@Transactional` and Spring's `@Async` on the same proxied method | not a Spring proxy, or not Spring's annotations |
| `reactor-block` (critical) | the call can run on a non-blocking Reactor thread (event loop, `parallel`, `single`) | it runs on a thread that may block (virtual, `@Async`, `boundedElastic`, startup, servlet worker) |
| PYVIBE-001/002/004/007/008/009/010/011/016/018 (blocking in `async def`) | the call runs on the event loop on a request or task path, **including a shutdown or self-uninstall path triggered while the loop serves other work** | the code runs only at **process startup or final shutdown with no other work on the loop**, in a thread (`to_thread`, executor), or in a `def` only called off the loop |
| PYVIBE-003/015 (nested loop) | reachable while a loop is running | only reachable with no running loop |
| PYVIBE-005 (Celery without a time limit) | the task can hang on external I/O and no global limit is set in the repository | a global `task_time_limit`/`task_soft_time_limit` covers it |
| PYVIBE-006 (ContextVar without reset) | the value can leak to later work sharing the context, **including later steps of the same task** | the context is discarded after the call |
| PYVIBE-012/014 (discarded task) | no reference to the task is kept anywhere, **whether or not the body catches its exceptions** | a reference is kept (a set, a registry, a callback attaching it) |
| PYVIBE-013 (gather) | some gathered awaitable can raise on a normal failure, and the others then run unobserved | every awaitable contains its exceptions |
| PYVIBE-017 (empty `except`) | it can swallow `KeyboardInterrupt`/`SystemExit`, or errors that matter on a normal path | — |

A rule not listed falls back to conditions 1–3.
<!-- END VERBATIM -->
