# Pre-registration — vibe-guard precision and noise on a fresh TEST corpus

Committed and pushed before the official search, selection or any scan. Frozen after this
commit; departures go to `DEVIATIONS.md` (original text, new text, what was observed,
when). Both the original and the deviating evaluation are reported; the original decides.
Thresholds are never relaxed.

The decisions D1-D7 in brackets were taken by Joaquín Ríos Heredia on 2026-10-14 (vibe-guard
`DECISIONS.md`), after reviewing a draft and before this commit.

**Read `DEVIATIONS.md` first.** One search ran by accident before this commit
(2026-10-14, 08:00–08:01 +02:00). It is void: its output is published unopened in
`accidental-search/`, and the official search after this commit is the only one that
decides.

## Question

Definition of done of vibe-guard, criteria 1, 2 and 9:
1. Is the precision of vibe-guard's CRITICAL findings ≥ 90 % on repositories never used
   to tune any rule, with at least 50 CRITICAL findings reviewed by hand?
2. How many CRITICAL and WARNING findings does it produce per 1,000 source files of each
   language, against thresholds fixed here?
9. Publish the precision with n, the review method and the confidence interval.

## Tools under test (frozen)

- **vibe-guard-scan** (vibe-guard's wrapper; private repository) at commit `88c4724`,
  installed with `npm ci`. Its lockfile pins **java-vibe-guard 2.4.0** (npm integrity
  `sha512-YawOnqjT9X48nqWwjwbl31xecv6jDoqQAUQD0Ohpy4aI1iiReO/QYXm+KKQJeyi0yGvhKuiAhwAuh6b3UubEyQ==`).
- **python-vibe-guard (pyvibe) 0.13.0** from PyPI, installed with `--require-hashes`
  (wheel sha256 `337e14d1334e11f794c0eef387a9cb0838d4e60d9da92dc4feab80c29993d7a2`) in a
  dedicated venv, passed with `VIBE_GUARD_PYVIBE`.
- Node, Python, OS and CPU are recorded in `env.txt`. No result is generalised beyond
  these versions.
- A rule change after this commit does not change the measured precision. If its effect
  is evaluated, it is reported as exploratory.

## Corpus selection (fixed before looking at any result)

Two pools, selected the same way: **Java/Spring** and **Python/FastAPI**.

1. **Search** (`scripts/select.mjs`, run once): GitHub REST repository search
   (`GET /search/repositories`), `sort=stars`, `order=desc`, 100 per page, every page up
   to the API cap of 1,000. Query strings, exactly, with `<D>` the selection date (UTC)
   minus 183 days, as `YYYY-MM-DD`:
   - Java: `topic:spring-boot language:Java fork:false archived:false is:public stars:>=100 size:100..1000000 pushed:>=<D>`
   - Python: `topic:fastapi language:Python fork:false archived:false is:public stars:>=100 size:100..1000000 pushed:>=<D>`

   Raw responses, UTC times and `total_count` are saved to `search-raw/`.
2. **Ordering:** `stargazers_count` descending, as returned at search time; ties by
   `full_name` ascending. The ordered list is saved as `candidates.json`, with stars,
   default branch, size, description and `pushed_at`. **That file is frozen:** the search
   is not re-run, and every expansion takes the next candidates from it.
3. **Exclusions,** applied in this order, each excluded repository recorded with its
   reason in `corpus.json` [D6]:
   a. **Used before:** the repository is in `exclusions.json`, built by
      `scripts/build-exclusions.mjs` from the pinned sources in `EXCLUSION-SOURCES.md`
      (962 repositories). Matched by GitHub repository id after resolving each listed
      name with `GET /repos` (follows renames), or by case-insensitive `full_name`. Known
      limit: see `EXCLUSION-SOURCES.md` (`100-repos.json`).
   b. **Owned by `Joaquinriosheredia`.**
   c. **Toy repositories** [D6]: a token of the name or of the description is in this
      fixed list. Tokens: split on camelCase boundaries and on every non-alphanumeric
      character, lowercased.

      `tutorial tutorials example examples sample samples demo demos course courses
      workshop boilerplate template templates starter starters scaffold interview exercise
      exercises homework awesome cheatsheet kata playground bootcamp`
   d. **In both pools:** kept in the Java pool only.
   e. **Stack not present at the pinned commit,** checked on the checkout before the
      scan with `scripts/count-files.mjs` (the file definition of "Noise" below):
      - Java: no `pom.xml`, `build.gradle` or `build.gradle.kts` containing
        `spring-boot`, or fewer than 20 `.java` files;
      - Python: no `.py` file with a line starting `from fastapi` or `import fastapi`, or
        fewer than 20 `.py` files.
   f. **Cannot be fetched, or the scan exits 2 or times out:** recorded with the error
      and **replaced** by the next candidate, because no finding was observed.
4. **Initial N** [D3]: the first **20** eligible repositories of each pool.
5. **Pinned commit:** the SHA of the default branch when the repository is processed
   (`GET /repos/{owner}/{repo}/commits/{default_branch}`). It is saved to `corpus.json`
   with the batch number.

Known limits, stated in the results:
- topics are self-assigned, so a Spring or FastAPI project without the topic is not a
  candidate;
- the search ranking and the 1,000 cap mean "most starred among the search results";
- `stars:>=100` and the activity window bias the corpus towards maintained, popular
  projects;
- the toy filter is lexical and can exclude a production repository whose description
  uses one of the words.

## Run

`scripts/run.mjs`, for each repository:
1. Shallow fetch of the pinned commit; HEAD must equal the pinned SHA.
2. Exclusion 3e.
3. Exactly this, with the defaults a user gets (default exclusions on, `--fail-on
   critical`, no `--exclude`):

       node <vibe-guard-scan>/bin/vibe-guard.js scan <checkout> --format json --output results/<owner>__<repo>.json

- Exit 0 or 1 is a valid scan.
- Exit 2 is exclusion 3f.
- Per-repository timeout: 30 minutes. The whole process group is killed and the
  repository is treated as 3f.

All scripts and `test/import-is-inert.test.mjs` are committed with this
pre-registration. Importing any script makes no network call, starts no process and
writes no file; running it does.

## Stopping rule (decided by counts only, never by verdicts)

1. After each batch is scanned, count the CRITICAL findings across all scanned
   repositories of both pools. **No finding is reviewed before the corpus is frozen.**
2. If the count is **≥ 50**, the corpus is frozen.
3. Otherwise, add the next **10 + 10** eligible repositories [D3] and go back to 1.
   - Both pools grow in every batch.
   - A pool that reached its cap or ran out of candidates stops growing; the other one
     continues.
4. **Cap:** 150 repositories per pool [D3]. If both pools stop with fewer than 50 CRITICAL
   findings, criterion 1 is **not met**, and the report says so with the count reached.
   The threshold is never lowered and the query never changed.

## Review protocol (after the corpus is frozen)

**Unit:** one entry with `severity: "critical"` in a repository's `findings[]`.
`scripts/sample.py review-set` sorts them by (language, repository, file, line, ruleId,
message) and numbers them `C001…`.

**Review set** [D4]: every CRITICAL finding if there are ≤ 150. Otherwise a sample of
150, stratified by language:
- each language gets 150 × its share of the CRITICAL findings, rounded, with Python
  taking the remainder;
- one `random.Random(20261014)` draws Java first, then Python, each with `.sample` from
  that language's sorted list.

**Verdicts,** from the source at the pinned commit. Callers and configuration are
followed anywhere in the repository.

- **TP** when all three hold:
  1. **Detection:** the code has the pattern the rule names, where it names it;
  2. **Context:** the conditions the message states for the impact hold there (the rule
     criteria below);
  3. **Reachability:** the code runs in the application's normal operation, as
     production code, not only in tests, examples, scripts or dead code.
- **FP** when any of 1-3 is false and the repository shows it.
- **Undetermined (U)** when the repository does not let 1-3 be decided: for example, the
  caller, the thread or the configuration lives outside the repository.

**Message accuracy** (criterion 8) is recorded separately, as overstated yes or no. A TP
whose message overstates the impact stays a TP for precision, and is counted apart.

**Rule criteria** (condition 2). The impact each CRITICAL claims must be possible in
context:

| Rule | TP context | FP context (examples, not exhaustive) |
|---|---|---|
| `blocking`, `blocking-kafka` | the blocking call runs on the anchored pool (an `@Async` executor with `@EnableAsync`, a scheduler, an event, a Kafka listener thread) on a normal path | the anchor is inert, or the call does not block (a completed future) |
| `kafka-send-timeout` | an untimed `.send(..).get()` on a normal path | the producer is configured so the call cannot wait beyond the message's bound |
| `transactions` (critical) | `@Transactional` and Spring's `@Async` on the same proxied method | not a Spring proxy, or not Spring's annotations |
| `reactor-block` (critical) | the call can run on a non-blocking Reactor thread (event loop, `parallel`, `single`) | it runs on a thread that may block (virtual, `@Async`, `boundedElastic`, startup, servlet worker) |
| PYVIBE-001/002/004/007/008/009/010/011/016/018 (blocking in `async def`) | the call runs on the event loop on a request or task path | the code runs only at startup or shutdown, in a thread (`to_thread`, executor), or in a `def` only called off the loop |
| PYVIBE-003/015 (nested loop) | reachable while a loop is running | only reachable with no running loop |
| PYVIBE-005 (Celery without a time limit) | the task can hang on external I/O and no global limit is set in the repository | a global `task_time_limit`/`task_soft_time_limit` covers it |
| PYVIBE-006 (ContextVar without reset) | the value can leak to later work sharing the context | the context is discarded after the call |
| PYVIBE-012/014 (discarded task) | no reference to the task is kept anywhere | a reference is kept (a set, a registry, a callback attaching it) |
| PYVIBE-013 (gather) | some gathered awaitable can raise on a normal failure, and the others then run unobserved | every awaitable contains its exceptions |
| PYVIBE-017 (empty `except`) | it can swallow `KeyboardInterrupt`/`SystemExit`, or errors that matter on a normal path | — |

A rule not listed falls back to conditions 1-3. For each finding,
`audit-claude.json` records:
- the verdict and a one-line reason citing file:line evidence;
- main or test path;
- message accuracy.

**Blindness of the second review** [D5]:
- When the first review (Claude) is complete, `audit-claude.json` stays **outside this
  repository**. Only its sha256 is committed (`audit-claude.sha256`).
- Then `scripts/sample.py blind` writes:
  - `blind-sample.md` / `.json`: 20 findings drawn with `random.Random(20261015).sample`
    from the sorted review set, **without verdicts**;
  - `undetermined.json`: every U not among those 20.
- Joaquín reviews the 20 blind, and then every U, and his verdicts are committed
  (`audit-joaquin.json`). Only then is `audit-claude.json` committed, matching the
  published hash.
- **Agreement on the 20 blind findings** is published: raw agreement and Cohen's kappa
  over TP/FP/U, plus the IDs that changed. For the U, the IDs he resolved to TP or FP
  are published.
- Joaquín's verdict decides wherever he reviewed.

## Metrics (`scripts/evaluate.py`)

- **Precision (primary, decides criterion 1):** TP / (TP + FP + U), U counted against.
- **Precision (secondary):** TP / (TP + FP).
- **Interval:** Wilson score at 95 % for both.
- **Criterion 1 is met** [D1] if, and only if, the **primary point estimate is ≥ 90.0 %**
  and at least 50 CRITICAL findings were reviewed. The Wilson 95 % interval and n are
  always published next to it (criterion 9), and never replace the point estimate in the
  verdict.
- **Clustering:** findings per repository, and the primary precision recomputed with each
  repository capped at 10 findings (`random.Random(20261016)`, repositories in sorted
  order). Informational only.
- **Per language and per rule:** the same metrics, for Java and for Python.
  - Criterion 1 is global, but a language with fewer than 20 reviewed CRITICAL findings
    has its per-language precision labelled "not conclusive (n < 20)".
  - The per-language figures are reported whether or not the global criterion is met.

## Noise (criterion 2; thresholds fixed here, before measuring)

- **What counts as a finding:** one entry of `findings[]` in vibe-guard's JSON, after its
  default exclusions, the engines' suppressions and deduplication, as a user sees it.
  Severity as reported. Suppressed findings do not count.
- **What counts as a file:** a `.java` (Java) or `.py` (Python) file of the checkout,
  counted by `scripts/count-files.mjs`. It uses the frozen wrapper's own `detect.js`, and
  excludes:
  - the engines' default directories;
  - the folders vibe-guard excluded for that repository (`excludes.applied`).

  `run.mjs` records whether those folders match the scan's. The engines' own
  `filesScanned` is not used, because it includes the excluded folders.
- **Rate:** per language, the sum of findings over all corpus repositories divided by the
  sum of files of that language, × 1,000. A language's findings count only against that
  language's files.
- **Thresholds** [D2], per language:
  - **CRITICAL ≤ 5 per 1,000 files;**
  - **WARNING ≤ 20 per 1,000 files.**

  These are judgement thresholds based on the review effort they allow (a 2,000-file
  service gives at most 10 CRITICAL to review by hand and 40 WARNING, which the text
  report groups by rule). They are not derived from data. MAJOR and INFO are reported
  without a threshold.
- **Also reported:** per-repository rates, with the median and the maximum per language.
- Criterion 2 is met only if both thresholds hold for both languages.

## Third-party code [D7]

- Every finding is cited with its repository, its pinned commit and its file:line.
- Nothing is opened in those repositories: no issue, no PR, no comment.
- Checkouts stay outside this repository; only vibe-guard's outputs are committed.

## Outcome → consequences

- **Criterion 1 met:** the precision is published with n, the method and the interval
  (criterion 9), pinned to this directory's commit.
- **Criterion 1 not met:** the report lists the FP and U by rule and by reason.
  - Each rule fix is a separate PR, designed on the development set (never on this
    corpus).
  - Re-measuring after a fix needs a **new** test corpus under a new pre-registration:
    this one is spent once reviewed.
- **Criterion 2 not met:** the report names the rules that drive the rate. Fixes follow
  the same rule.
- Nothing in this directory changes a rule.
