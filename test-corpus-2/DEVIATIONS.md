# Deviations — test-corpus-2

## 1. OPEN: `cards.py` stops on binary matches of `git grep` (2026-10-15)

**State when it happened:** phases 1–3 were done and sealed.
- `be29edd`: search;
- `f49ad64`: Python pool;
- `0cb0a51`: Java pool and `env.txt`;
- `4fe14a7`: review set, 158 findings.

**What happened:** `python3 scripts/cards.py <WORK>` stopped on the first card (J001) with
`ValueError: not enough values to unpack` in `literal_matches`.
- **Cause:** for binary tracked files, `git grep -n -w -F` prints `Binary file <path> matches`
  instead of `path:line:text`. `cards.py` only parses the second form.
- **Scope:** checked by running only the same literal searches, without writing any card.
  **6 of the 158** review-set findings have at least one binary match, all in build artefacts
  committed to their repositories.
- The cards in the other 152 would be unaffected.

**What was done:** nothing.
- No card was written. `cards.py` had already created the empty directory `cards/`, which is
  left as it was and is untracked.
- No hash was published, no verdict exists, and no threshold, query or seed was touched.

**Why it stops here:** the pre-registration says "**every** match … nothing filtered, all
listed with path and line". A binary match has no line. Handling it changes the text of the
cards method, so it is a departure that Joaquín decides.

**Options (Joaquín decides):**
- **(a) List binary matches as rows** with path, line `—` and text `binary file`. Keeps "every
  match"; the only change is the format of 6 cards. **Claude's suggestion.**
- (b) Skip binary files with `git grep -I`. "Every match" becomes "every match in text files";
  6 cards lose rows that carry no code.

Either option needs:
- a code change in `cards.py`, plus a test;
- removing the empty `cards/`;
- re-running phase 4 from the start.

The text of this entry is updated with the decision.
