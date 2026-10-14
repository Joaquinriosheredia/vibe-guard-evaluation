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
