# Deviations

## 1. An accidental search ran before the pre-registration was committed (2026-10-14)

**What happened.** The pre-registration requires the search to run only after this
directory is committed and pushed. Before that commit, while testing a helper
(`toyKeyword`) offline, Claude ran:

    node -e "import('./scripts/select.mjs')"

At that time, `select.mjs` ran the whole search at module top level, so importing it
executed the search. Timeline (+02:00, from the files' modification times):
- before 08:00:36: the names of `exclusions.json` were resolved with `GET /repos`;
- 08:00:36: `exclusions-resolved.json` written;
- 08:01:19: the last search page written;
- 08:01:22: `candidates.json` written.

The text of the pre-registration was not yet written in this repository. The decisions
D1-D7 had already been taken by Joaquín before the incident, and the incident changed
nothing in them.

**What was seen.** Only the summary the script prints, and nothing else:
- `java: total_count 256, 256 read, 178 eligible by metadata`;
- `python: total_count 402, 402 read, 115 eligible by metadata`.

No candidate list or name was read, no repository was fetched or scanned, and no finding
exists.

**What was done.**
1. Claude stopped, reported it to Joaquín and moved the outputs, unopened, to a
   quarantine directory outside the repository.
2. Joaquín chose to void the accidental search (option A): the official search, run
   after this commit with its own selection date and cut-off, is the only one that
   decides.
3. The quarantined files are published unopened in `accidental-search/`, with these
   sha256 (computed at quarantine time, before this commit):

```
f5118240bda3934818027197356735833c2078c19c6be5b42ddcfb5f055cbaf8  candidates.json
33b1e22dd88d0ccf65ddb0e1c3fdcf7466c752a5375bca296918a733a5b8699b  exclusions-resolved.json
c425af3a34b2b3e7852cc5cee35a3677a0c41623f37a538b72c6dc985d5f903c  search-raw/java-page-1.json
e2fbafb990644e8f9db0c4acc7501d03cc38ff232af407f92ac8de3049d9c09d  search-raw/java-page-2.json
b1eb5b406ab62485a0584ca009a5cfeb37cc664d23d4d8564e03c2a0bf3e3a54  search-raw/java-page-3.json
e9ec1e7f5d4ef74feff5f534379586811410e32c6e840017e41c5e0805bb5dda  search-raw/python-page-1.json
2c09d5a8a20851d9c14ae4ef21969889cb03e5250857e0a032ca3e10eb21d1ac  search-raw/python-page-2.json
88e08adf464247bf54ff72403f96c124914a29206bd05afb41166b9890292c98  search-raw/python-page-3.json
6db6151fb0cfdcfb53fbb055295373cf22e2a142d7e51580c055abb00c6bf16b  search-raw/python-page-4.json
4475d4d92cf2e492614b981378a8982e2a676ee0e265fffa8f13c5e6113f2a6d  search-raw/python-page-5.json
```

4. **Cause fixed.** Every script now does its work only when executed directly
   (`import.meta.url === argv[1]`, or `if __name__ == "__main__"`).
   - `count-files.mjs` loads the frozen wrapper lazily, inside `countFiles`, instead of
     on import.
   - `test/import-is-inert.test.mjs` imports every script in its own process with the
     network, child processes and file writes intercepted, and fails on any such call.
   - Positive controls prove the interception works. The test also fails on the original
     `select.mjs` (checked before this commit).
5. After the official search, `ACCIDENTAL-VS-OFFICIAL.md` publishes the comparison of
   the two candidate lists (common repositories, additions, removals). It changes
   nothing in the official selection.

**Effect on the evaluation.** None intended. The selection is mechanical and fixed above
(query, ordering, exclusions, batch sizes, cap), and the only information seen was the
pool sizes. Readers can verify the official lists against the accidental ones with the
comparison.

## 2. Blind-review "20/20 FP, line past end of file" reported — investigated, not reproduced (2026-10-14)

**What was reported.** After the blind review of the 20 criticals, Joaquín reported
that in all 20 the cited line did not contain the rule's pattern, and that for C124,
C171 and C231 the cited line was past the end of the file. He suspected a
line-localisation defect in the pipeline (engine → wrapper → sampling → link
generation), not a precision problem, and asked for a reproduction before any rerun.

**Investigation.** Nothing was fixed. Against the pinned commits already in the local
checkouts (no repository was re-fetched or opened), for C003, C124, C171, C203 and C231:

1. The frozen engines were run directly, without the wrapper
   (`pyvibe 0.13.0 --json` on the single file). Each emitted the finding at exactly
   the file:line recorded downstream:
   - C003 `src/compression/post_processor.py:179` PYVIBE-009
   - C124 `src/novelvideo/utils/bounded_concurrency.py:77` PYVIBE-013
   - C171 `apps/api/app/routers/resources.py:472` PYVIBE-012
   - C203 `packages/core/openexecutive/orchestrator/router.py:445` PYVIBE-013
   - C231 `backend/app/web/company_pages.py:1867` PYVIBE-013
2. The raw wrapper output (`results/<repo>.json`), `review-set.json`, `blind-sample.json`
   and the GitHub links in `blind-sample.md` all carry the same file, commit and line as
   the engine. No stage shifts the line.
3. The cited line in each file, at the pinned commit, contains the pattern and is within
   the file (`sed -n '<line>p'`, `wc -l`):
   - C124: file is 77 lines, line 77 is the last line (`return list(await asyncio.gather(...))`).
   - C171: file is 496 lines, line 472 is `asyncio.create_task(_answer_chat(...))`.
   - C231: file is 1881 lines, line 1867 is `... = await asyncio.gather(`.
   None is past the end of its file.
4. Across the full review set (all 150 findings, not only the 5): every cited line is
   within its file (**150/150 in-bounds, 0 out-of-bounds**). 132/150 cited lines contain
   the rule's literal token; the other 18 anchor on the enclosing construct the rule
   reports (PYVIBE-005 on the function `def` line, PYVIBE-016 on `with httpx.Client(...)`,
   PYVIBE-004/008/017/018 on the lock / connect / handler line) — each line does contain
   that construct.

**Conclusion.** The reported line-localisation defect does not reproduce. Engine, wrapper,
sampling and link generation agree with each other and with the source at the pinned
commit, for the 5 reproduced findings and for all 150 cited lines. Whether each finding is
a true or false positive is a separate (precision) question, untouched here; this entry
only records that the lines are correct.

**Unresolved.** The 20/20-FP / past-end-of-file observation from the blind review is not
explained by anything in the pipeline. The most likely benign cause is that the files were
viewed at the repositories' current state (default-branch HEAD, which for these very new,
low-star repositories can have changed or been force-pushed in the hours since the scan)
rather than at the immutable pinned-commit blob the links point to. This is a hypothesis;
the remotes were deliberately not re-fetched (pre-registration D7: nothing is opened in
those repositories). It can be confirmed cheaply by re-opening one pinned link
(e.g. C124's) and checking the SHA shown by GitHub matches `51cd2c4f833f`.

**Language split of the 244 criticals (for context).** 243 Python, 1 Java (the single Java
critical is `grimmory-tools/grimmory`, rule `transactions`). The pool is 99.6% Python, so a
blind sample of 20 coming out 20/20 Python is the expected outcome, not a sampling fault.

**Status.** No code, data or verdict changed. `evaluate.py` not run; `audit-claude.json`
untouched (sha256 still `4f5859c5…a6fd400`). Awaiting Joaquín's direction before any rerun
or re-review.

## 3. The first blind review was invalid (invented locations) and is superseded (2026-10-14)

**What happened.** A first attempt at the blind review of the 20 criticals was produced by
a different assistant and pushed to `main` (commit `1668e43`, "Update verdicts for multiple
PYVIBE issues"): all 20 marked FP, with no reasons. Its justifications relied on code
locations that do not exist at the pinned commits — e.g. file lengths that do not match the
file at the pinned SHA, and lines claimed to be past the end of a file. The independent
reproduction in Deviation #2 showed the opposite: engine, wrapper, sampling and links all
agree, every one of the 150 cited lines is within its file, and the five spot-checked
findings sit exactly on the cited line at the pinned commit.

**What was done.** That attempt is voided. The `main` commit `1668e43` (20 FP without
reasons) is superseded by the reviewed `blind-sample.md` on this branch, which carries each
verdict with a reason and file:line evidence checked against the pinned commit. No verdict
from the voided attempt is used.

## 4. The second (authoritative) blind review was assisted (2026-10-14)

**What happened.** For the authoritative review, a Claude session located the flagged code
and its callers at the pinned commits (reading only the frozen checkouts, opening nothing in
the live repositories). Joaquín then decided every verdict himself from that evidence. This
departs from a strictly unaided reviewer: the navigation was assisted, the judgement was
Joaquín's.

**Result.** 10 TP / 10 FP / 0 U over the 20. Each entry in `blind-sample.md` records the
verdict, a one-line reason with file:line evidence, and whether the message is overstated
(all 20: not overstated). Joaquín's verdicts are stored in `audit-joaquin.json` (kept
outside the repository, like `audit-claude.json`; only its sha256 is committed). `evaluate.py`
is not run yet: the single U from the first review (`undetermined.json`, C077) is still to be
reviewed by Joaquín.
