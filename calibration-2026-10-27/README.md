# Calibration 2026-10-27 — AI review vs Joaquín (TC2 + TC3, 52 cases)

What: `vibe-guard review` (reviewers A and B, `claude` CLI) re-judged the 27 TC2 + 25 TC3 cases that Joaquín audited (`test-corpus-{2,3}/audit-joaquin.json`); `table.py` compares them with Wilson 95% CIs.
Result (`table-output.txt`): A agrees 38/52 = 0.73, B 37/52 = 0.71, consensus 37/49 = 0.76; Python 0.82 vs Java 0.50; 15 failures, analysed in `../REVIEW-CRITERIA.md`.
Cost: $23.77 actual (estimate was ~$10), concurrency 3, both corpora in parallel.
**Warning — instruction paths:** both runs used `test-corpus-3/REVIEW-AI-INSTRUCTIONS.md`, which hardcodes `~/vibe-guard-evaluation-work/tc3/` and forbids reading `tc2/`; the TC2 run was therefore not neutral (J052 was invalid for that reason; J017 invalid by a citation-path mismatch). Both fixed for new runs: `../REVIEW-AI-INSTRUCTIONS.md` (corpus-neutral) and vibe-guard-scan `fix/review-citation-hint`.
**Raw outputs lost:** `out-tc2/` and `out-tc3/` (review-a.json, review-b.json, review-sheet.md) lived in a session scratchpad under /tmp and were wiped; `table.py` and `table-output.txt` were recovered verbatim from the session transcript.
`table.py` therefore cannot be re-run as is: it needs `<S>/out-tc{2,3}/review-{a,b}.json` (`python3 table.py <S> ~/vibe-guard-evaluation`).
Command per corpus `c`: `vibe-guard review test-corpus-$c/cards --instructions test-corpus-3/REVIEW-AI-INSTRUCTIONS.md --checkouts ~/vibe-guard-evaluation-work/tc$c/checkouts --out <S>/out-tc$c --ids-file <S>/ids-tc$c.txt --concurrency 3`.
`ids-tc$c.txt` = the IDs of `test-corpus-$c/audit-joaquin.json`, sorted.
From now on run outputs go to `~/vibe-guard-evaluation-work/`, never only to /tmp or a scratchpad.
