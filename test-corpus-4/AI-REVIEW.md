# Optional AI review — declaration (committed before it runs)

`PREREGISTRATION.md`, "Optional AI review": comparison only, it **never decides**. Joaquín's decisions
of 2026-10-28: the AI review is run, **proposer only** (chain-v1), with the few-shot examples of the
2026-10-28 calibration. If the subscription's usage limit is reached, it is **not run at all**: no
partial review is sealed, and that is recorded here.

## Tool

- vibe-guard-scan **`v0.4.1`**: annotated tag object `80bee76454241b2b983a916448ee3e46c583291a`, commit
  `094d1ddb630e4c0b5ab83705689d2b9fb66c95c0`. It adds `review --reviewer-b none` to `v0.4.0`;
  `scan` and the engines are unchanged.
  - It runs from a separate worktree with `npm ci` and a clean tree; `--version` prints
    `vibe-guard 0.4.1 (java-vibe-guard 3.1.0; pyvibe 0.16.0)`.
  - The scans of this corpus stay on `v0.4.0` (`FROZEN.json`).
- Reviewer: Claude Code 2.1.312 (`claude` CLI), headless, on the logged-in Max subscription. The
  wrapper removes `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` from the reviewer's environment.
- **Model: `claude-opus-5-5`**, set explicitly with `--model-a`.
- **Protocol: chain-v1.**
  - A plan with no tools comes before any code is read.
  - The review then uses Read/Grep/Glob and the name-based callers tool.
  - The answer is a call chain from an entry point, one `path:line` per hop, with the v1
    criterion numbers.
  - The chain is verified. Rule e applies: a chain or an unreachability claim that does not
    verify becomes U, never FP.
- **Proposer only:** `--reviewer-b none`. No refuter is asked, and no `review-b.json` exists.

## Inputs (vibe-guard-evaluation)

| Input | File | sha256 |
|---|---|---|
| Instructions | `REVIEW-AI-INSTRUCTIONS.md` (root, v1, corpus-neutral) | `4ebc50215e45ab5d9b3ae7c6f59f5551bbcba2b41fddfb449fab1b75d8421b9e` |
| Few-shot examples | `calibration-v1-2026-10-28/examples-tc2.md`: 7 test-corpus-2 cases with Joaquín's verdict and reason; development data only, nothing from test-corpus-4 | `784e91efa7a7cd85203cfa73330203a33e2846840d140c2da0ab1441f475491c` |
| Cards | `test-corpus-4/cards/`, generated once by `scripts/cards.py` | the committed sha256 of `cards/SHA256SUMS` |
| Checkouts | the pinned commits kept by `run.mjs` (`<WORK>/{java,python}/<owner>__<repo>`) | — |

## Command

    vibe-guard review test-corpus-4/cards \
      --instructions REVIEW-AI-INSTRUCTIONS.md \
      --examples calibration-v1-2026-10-28/examples-tc2.md \
      --checkouts <WORK> --out <OUT> \
      --protocol chain-v1 --reviewer-a claude --model-a claude-opus-5-5 --reviewer-b none \
      --concurrency 3

- **`<OUT>` is outside the repository:** `~/vibe-guard-evaluation-work/tc4/ai-review/`. Its log goes
  to a file there.
- The output **is not opened** by Joaquín, by this assistant or by anyone helping him until
  `audit-joaquin.json` and `audit-joaquin.sha256` are committed. This covers `review-a.json`,
  `review-sheet.md` and the log. The assistant reads only:
  - the run's final count line (reviewed, skipped, invalid);
  - its exit code;
  - whether a usage-limit stop occurred.
- **Exit 3** (usage limit) means the AI review is **abandoned**. It is not resumed, and nothing is
  sealed.
- Exit 0 or 1 means the review completed (exit 1: some answer invalid, which counts as
  disagreement). `review-a.json` is then sealed with `scripts/ai_compare.py seal <OUT>`, which writes
  `ai-review.sha256`. That hash is committed **before** `scripts/review_sheet.py sheet` generates
  Joaquín's `REVIEW-SHEET.md`.

## Outcome

**Completed and sealed, 2026-10-28:**
- run from 12:31 to 13:06 (+01:00);
- exit 1: 160 reviewed, 0 skipped, 1 invalid answer (counts as disagreement);
- no usage-limit stop.

`review-a.json` sha256 `6710560ae7747edc96c259b8df9f0261370026b6880d5dfd7769222ff07744ac`
(`ai-review.sha256`, committed with this line, before `REVIEW-SHEET.md`). Not opened.
