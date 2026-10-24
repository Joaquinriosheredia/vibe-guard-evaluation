# Deviations — test-corpus-2

## 1. `cards.py` stops on binary matches of `git grep` (2026-10-15) — decided: option (a)

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

**Decision (Joaquín, 2026-10-15): option (a).**
- **What:** matches in binary files are listed as rows `binary file`, with their path and path
  class and no line number (`—`). **All matches are kept.**
- **Why:**
  - it keeps "every match … nothing filtered";
  - it happens before any verdict (no card, no verdict and no hash existed);
  - it affects 6 of the 158 cards.
- **Done:**
  - `literal_matches` in `scripts/cards.py` parses `Binary file <path> matches`;
  - `test/test_units.py` covers that git output with a committed binary file, both the
    parsed row and the card row;
  - the empty `cards/` was removed and phase 4 was re-run from the start.
- Nothing else in the pre-registration changes.

## 2. `cards.py` splits some `git grep` records wrongly (2026-10-15) — fixed with Joaquín's OK

**State when it happened:** deviation 1 was applied (`54931ff`), the empty `cards/` was
removed and phase 4 was re-run from the start.

**What happened:** `cards.py` stopped again on the first card (J001), in `literal_matches`, with
`ValueError: invalid literal for int()`. No card was written. `cards.py` recreated the empty
directory `cards/`, which is left as it was and is untracked.

**Cause:** `cards.py` reads the output of `git grep` in text mode (`text=True`) and splits it
with `str.splitlines()`. That breaks one `path:line:text` record into several when the matched
line contains:
- a `\r` (text mode applies universal newlines);
- a Unicode line separator that `splitlines()` honours (`\x85`, `\x1c`–`\x1e`, ` `…).

`git grep` itself ends each record with `\n` only. The fragments have no `path:line:` prefix.
Seen in minified CSS/JS files that the repositories track.

**Scope:** checked by re-running only the same literal searches, without writing any card.
- **3 of the 158** cards get records split this way.
- Splitting the raw bytes on `\n` only leaves **0** unparsable records over the whole review set.

**What was done:** nothing else. No card, no hash and no verdict exist. No threshold, query or
seed was touched.

**Why it stops here:** this is an implementation error, not a change of method. Every match is
still listed, with path and line. But the order was to stop on any error.

**Proposed fix (Joaquín decides):**
- In `literal_matches`, read `git grep` as bytes, split records on `\n` only and decode each
  record as UTF-8 with replacement.
- The table cell escapes control characters.
- Add a test with a committed text file whose matched line contains `\r` and `\x85`.
- Remove the empty `cards/` and re-run phase 4 from the start.

**Decision (Joaquín, 2026-10-15): OK to the proposed fix.**
- **What changed:**
  - `literal_matches` reads `git grep` as bytes, splits records on `\n` only and decodes each one as UTF-8 with replacement (`grep_records`, `parse_record`);
  - the table cell escapes control characters as `\xNN` / `\uNNNN`.
- **Tests:** `test/test_units.py` `CardsRecords`, with a committed file whose matched line contains `\r` and `\x85`; plus `parse_record` rejecting a fragment.
- **Method unchanged:** every match is still listed, with path, line or `binary file`, and path class.
- **Bounded permission (Joaquín, 2026-10-15):** for the rest of phase 4, an implementation error of `cards.py` that does **not** change the method may be fixed without stopping. Each one needs a test that reproduces it and a §N here with date, cause, scope and fix. Anything that changes the method, the content of the cards or the pre-registration stops the run.
- **Validation mode added:** `python3 scripts/cards.py --validate <WORK>` parses every `git grep` record of the review set, writes nothing, and exits 1 if any record is unparsable.
  - Result: **158 cards, 25,973 records, 0 unparsable**.
  - After that, the empty `cards/` was removed and the cards were generated once.


## 3. Review method changed: two independent AI reviews plus a human audit (2026-10-15) — decided by Joaquín

**State when decided:** phases 1–6 were done and sealed (`audit-claude.sha256`, `repeat-sample.sha256`).
Review materials for Joaquín were merged (PR #8, `a80d9ab`). **No verdict had been opened:**
`audit-claude.json` was still sealed and unread, and no human verdict existed.

**Reason (Joaquín):** a full review of the 158 cards by Joaquín (about 25 h) is not feasible.
It is replaced by a double AI review plus a human audit.

**New method:**
1. **Review A** = `audit-claude.json`, already sealed (sha256 `6aeb6e7f…5dda`). It is not touched.
2. **Review B:** new, independent AI sessions that do **not** see A.
   - Model: **Claude Sonnet 5.5** (`claude-sonnet-5-5`). Review A was written by Claude Opus 5.5.
   - Instructions: `REVIEW-B-INSTRUCTIONS.md`, committed before B starts. They require:
     - applying the pre-registration rules to the letter;
     - always following callers to the end (tests, scripts, dead code = FP by reachability);
     - checking whether exceptions are already contained;
     - U when the repository does not let the case be decided;
     - file:line for every claim, with no guessing or inventing;
     - test-corpus-1's known failures, as a warning.
   - Output: `audit-claude-B.json`, same format as A. It is kept outside the repository and only
     its sha256 is committed (`audit-claude-B.sha256`).
3. **Opening:**
   - A's file is checked against its committed hash, then A and B are opened.
   - Final verdict: if A = B, that verdict; if A ≠ B, Joaquín decides from the card, logging
     any help in `REVIEW-LOG.md`.
   - "A = B" compares the `verdict` field (TP/FP/U).
4. **Audit:** 20 cases drawn at random from the agreeing ones and reviewed by Joaquín without
   seeing A or B.
   - Draw: `random.Random(20261025).sample(agreeing, 20)`, where `agreeing` lists the agreeing
     IDs in review-set order. The 20 are listed in review-set order.
   - **Rule:** if Joaquín changes **≥ 3 of the 20**, the AI review is declared **NOT RELIABLE**
     and **criterion 1 is NOT MET in the affected language**.
   - The change rate is published with its 95 % Wilson interval.
5. **Repeatability is dropped:** the 10-case repeat review (`random.Random(20261023)`) is not
   done. `repeat-sample.sha256` stays committed. The sample is not used and is not opened.
6. **Honest publication:** "reviewed by two independent AIs; disagreements and a sample of 20
   audited by the author; A–B agreement X, kappa Y; corrections in the audit Z/20".
7. **Everything else in the pre-registration does not change:** thresholds, n, metrics, U
   counted as FP.

**What this replaces in the pre-registration:**
- **"Official verdicts: Joaquín only":** the official verdicts are the final verdicts of point 3.
- **Steps 4–7 of "Order of the steps":** replaced by points 2–5.
- **Agreement:** the published agreement is A against B. It is no longer Claude against
  Joaquín.
- `REVIEW-SHEET.md` and `scripts/review_sheet.py` (PR #8) were written for a full review by
  Joaquín. How they are used for the disagreements and the audit is still to be adapted.
- `evaluate.py` still requires `audit-joaquin.json` for all 158. It must be adapted to read
  the final verdicts before it runs. Nothing is run until then.

**Open points, not decided here (Joaquín decides before they are applied):**
- **Which language is affected by the audit rule.** The rule names "the affected language"
  but the sample of 20 is drawn over both languages together. The decision text does not
  say how ≥ 3 changes split between Java and Python map to a language.
- **The message-accuracy flag (`overstated`) in the final verdict** when A and B agree on the
  verdict but differ on this flag.

**Order:** this section frozen → `REVIEW-B-INSTRUCTIONS.md` committed → review B sealed →
A and B opened → list of disagreements and audit sample (IDs only, no verdicts).

### 3a. Decisions on the open points (Joaquín, 2026-10-15), before the audit and before `evaluate.py`

**State when decided:**
- A and B were opened (`f19f025`), and `REVIEW-AB.md` lists IDs and counts only.
- A and B agree on 151 of 158 verdicts, with 7 disagreements.
- 69 agreeing cases differ on `overstated`.
- No human verdict exists and `evaluate.py` has not run.

1. **Audit rule:** if Joaquín changes **≥ 3 of the 20 in total**, the AI review is declared
   **NOT RELIABLE** and **criterion 1 is NOT MET in BOTH languages**.
   - A change means that Joaquín's verdict (TP/FP/U) differs from the A = B verdict.
   - The changes are also published separately for Java (of 7) and Python (of 13), each with
     its 95 % Wilson interval, next to the total (of 20).
2. **`overstated`:**
   - Where A and B agree on the verdict but not on `overstated`, the final flag is **yes**
     (conservative).
   - Where both say no, it is no; where both say yes, it is yes.
   - The number of cases in dispute (69) is published.
   - In the 27 cases Joaquín reviews, Joaquín decides.
3. **Joaquín's sheet and the final verdicts:**
   - `REVIEW-SHEET.md` holds **only the 27 IDs** (the 7 disagreements and the 20 of the
     audit), with the same empty fields.
   - The sheet does not say which ID is a disagreement and which is part of the audit.
     (`REVIEW-AB.md`, committed in `f19f025`, does list both groups.)
   - **Order:** the 27 IDs are taken in review-set order and shuffled with
     `random.Random(20261026).shuffle`. The seed is fixed here, before the sheet is generated.
   - The converter produces `audit-joaquin.json` with exactly those 27 IDs.
   - **Final verdict of each finding:**
     - Joaquín's verdict wherever he reviewed: the 7 disagreements and the 20 of the audit;
     - the A = B verdict for the other 131.
   - `evaluate.py` reads A, B (both checked against their committed sha256) and Joaquín's
     27 verdicts. It checks that the disagreements and the audit sample match
     `REVIEW-AB.md`, builds the final verdicts and applies rule 1.
   - Repeatability is no longer an input, and A against B is published as the agreement.
4. **Disclosure (Joaquín), recorded 2026-10-16:**
   "Joaquín vio los 7 IDs de desacuerdo en el informe de Code (2026-10-15 11:16) antes de
   revisar; el barajado de la hoja no oculta qué casos son desacuerdo. No conoce los
   veredictos de A ni de B. J001 lo empezó a mirar durante el método anterior
   (REVIEW-LOG.md)."
   - Nota: estas entradas se registran el 2026-10-16, con retraso, a partir de la
     conversación del 2026-10-15.

### 3b. Assisted verdicts (Joaquín, 2026-10-24), before the end of the review and before `evaluate.py`

**State when decided:**
- The review of the 27 IDs is not finished.
- `REVIEW-SHEET.md` is not touched by this section.
- Nobody running this change has seen a verdict of A or B, and `evaluate.py` has not run.

**Text (Joaquín, 2026-10-24):**
"2026-10-24. Según REVIEW-LOG.md, los veredictos de Joaquín en J015, J038, J056, J036,
J001, J020, J023, J052, J021, P145, P083, P099, P098 y P072 se emitieron después de recibir
valoraciones de un asistente de IA (fuera de la regla 'solo navegación factual') y un
porcentaje provisional. Esos 14 se marcan como 'asistidos con valoración'. Los 13
restantes se revisan sin ayuda más allá de navegación factual.
Regla fijada antes de terminar la revisión: evaluate.py calcula la auditoría y la
precisión (a) con todos los veredictos y (b) excluyendo los 14 asistidos de la muestra
de auditoría; si la conclusión del criterio 1 difiere entre (a) y (b), se toma la más
desfavorable. Ambas se publican."

**Where the 14 fall** (from `REVIEW-AB.md`, IDs only):
- **4 disagreements:** J056, J001, P145, P072.
- **10 of the audit sample:** J015, J038, J036, J020, J023, J052, J021 (Java) and P083, P099, P098 (Python).
- **(b) keeps 10 audit cases, all Python:** P002, P046, P057, P065, P073, P077, P090, P116, P153, P161.

**Details of (b) (Joaquín, 2026-10-24):**
1. **Audit threshold:** the original rule is ≥ 3 of 20 (15 %).
   - In (b) the threshold is proportional and conservative: **≥ 2 of 10 changes → AI review NOT RELIABLE**.
   - It applies globally, like the original rule: criterion 1 is NOT MET in both languages.
2. **Java:** in (b) no Java audit case remains, so the Java audit exists only in the assisted version (a). The results say so explicitly.
3. **Precision in (b):**
   - The 10 assisted audit IDs keep the A = B verdict.
   - The 4 assisted disagreements cannot be left out, because every finding needs a verdict. In (b) they count as **U**, which counts against the primary metric.
4. **Final rule (unchanged):** if the conclusion of criterion 1 differs between (a) and (b), the less favourable is taken. Both are published.
5. Criterion 2 (FP/1000) (Joaquín, 2026-10-24, before running
   evaluate.py): same rule as criterion 1 — if it differs between (a)
   and (b), the less favourable is taken. Both are published.

**Done:**
- `scripts/evaluate.py`:
  - `ASSISTED` lists the 14 IDs.
  - `final_verdicts_unassisted` builds version (b).
  - `audit_max_changes(n)` = ⌈3·n/20⌉, which gives 3 for 20 and 2 for 10.
  - `both` takes the less favourable criterion 1 and criterion 2 per language and adds the Java note.
  - `metrics.json` and `METRICS.md` publish (a), (b) and the criterion 1 that decides.
- `test/test_units.py` `EvaluateAssisted` covers this.
- `evaluate.py` has **not** been run.

### 3c. `review_sheet.py audit` reads `Overstated` with a note (Joaquín, 2026-10-24)

Change of the parser's format, not of the method. Reason: Joaquín's sheet includes a justification in `Overstated`. Valid values: exactly `Sí` or `No`, optionally followed by ` — ` and text. Only that first word decides, and the full text is kept in `audit-joaquin.json` as `overstated_note`. Anything else still fails, for example `Si` without the accent, `No,` or `Quizá`.
