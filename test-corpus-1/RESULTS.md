# Results — test-corpus-1

Precision of CRITICAL findings and noise per 1,000 files, on repositories never used to tune
the rules. Pre-registration: `PREREGISTRATION.md`. Departures: `DEVIATIONS.md`. Numbers from
`metrics.json` (`scripts/evaluate.py`), rendered in `METRICS.md`.

Corpus: batch 1, frozen at the stopping rule (≥ 50 CRITICAL in a batch) with **244 CRITICAL**
across 40 included repositories. Language split of the 244: **243 Python, 1 Java**. Review
set: a stratified random sample of **150 of 244** (seed 20261014): 149 Python, 1 Java.

## Both pre-registered criteria are NOT met

**Criterion 1 — precision (D1): NOT met.** D1 requires the primary point estimate ≥ 90 % with
≥ 50 reviewed.

| Measure | n | TP | FP | U | primary | Wilson 95 % CI | secondary |
|---|---|---|---|---|---|---|---|
| Overall | 150 | 106 | 43 | 1 | **0.7067** | 0.6294–0.7736 | 0.7114 |
| Python | 149 | 105 | 43 | 1 | 0.7047 | 0.6270–0.7721 | 0.7095 |
| Java (not conclusive, n = 1) | 1 | 1 | 0 | 0 | 1.0000 | 0.2065–1.0000 | 1.0000 |

Primary counts U in the denominator; secondary excludes it. The whole Wilson interval lies
below 0.90.

**Criterion 2 — noise (D2): NOT met.** D2 caps CRITICAL at 5 and WARNING at 20 per 1,000 files
per language.

| Language | files | CRITICAL / 1,000 | WARNING / 1,000 | within D2 |
|---|---|---|---|---|
| Java | 22,741 | 0.044 | 0.967 | yes |
| Python | 5,776 | **42.071** | **110.111** | no |

Python is far over both thresholds (per-repo CRITICAL median 17.6, max 1,535.7). Java is
within thresholds but rests on a single CRITICAL finding.

## Precision by rule

| Rule | n | TP | FP | U | primary |
|---|---|---|---|---|---|
| PYVIBE-012 (create_task discarded) | 24 | 23 | 1 | 0 | 0.9583 |
| PYVIBE-009 (sync open in async) | 47 | 39 | 8 | 0 | 0.8298 |
| PYVIBE-005 | 9 | 9 | 0 | 0 | 1.0000 |
| PYVIBE-016 | 4 | 4 | 0 | 0 | 1.0000 |
| transactions (Java) | 1 | 1 | 0 | 0 | 1.0000 |
| PYVIBE-007 (subprocess in async) | 5 | 2 | 3 | 0 | 0.4000 |
| PYVIBE-013 (gather without return_exceptions) | 55 | 28 | 27 | 0 | 0.5091 |
| PYVIBE-004 | 2 | 0 | 1 | 1 | 0.0000 |
| PYVIBE-008 | 1 | 0 | 1 | 0 | 0.0000 |
| PYVIBE-017 | 1 | 0 | 1 | 0 | 0.0000 |
| PYVIBE-018 | 1 | 0 | 1 | 0 | 0.0000 |

PYVIBE-013 (55 findings, almost half FP) and PYVIBE-007 are the main drag on overall
precision; PYVIBE-012 and PYVIBE-009 carry most of the true positives.

**Clustering cap (10 findings per repository, seed 20261016):** with each repository
contributing at most 10 findings, precision is **0.5895** (56 TP / 95; Wilson 95 %
0.4890–0.6830). The uncapped figure benefits from a few repositories that each contribute many
findings; capping removes that leverage and precision falls further.

## Two reviews, and why the published figure is probably optimistic

The final verdict for each finding is Joaquín's where he reviewed it (the 20-finding blind
sample plus the one undetermined case), and the first review's otherwise. **129 of the 150
final verdicts come from the first review**, which was not independently checked.

On the 20 findings both reviewers judged independently (the blind sample):

- raw agreement **0.60** (12 of 20), Cohen's kappa **0.20** (weak);
- the first review called **16 TP**, the second **10 TP** on the same 20;
- 8 verdicts changed: **7 went TP → FP** (dead code or test-only paths, experimental scripts,
  or exceptions already contained upstream) and **1 went FP → TP**.

So on the only part measured twice, the first review over-called true positives by a factor of
16/10. The same reviewer produced 129 of the 150 final verdicts. **The published precision
(0.7067) is therefore likely an overestimate**; a fully independent review of all 150 would be
expected to score lower.

The one undetermined finding (C077, PYVIBE-004) was re-reviewed and **remains U**. Two final
verdicts carry an overstated-message flag.

## Status of this corpus

Because its findings have now been read and reasoned about in detail, **test-corpus-1 becomes a
development corpus**: it is no longer unseen, so it cannot serve as a clean precision
measurement again. The next measurement will be run on a **new, separately pre-registered
`test-corpus-2`**, with its own search, cut-off and exclusion of every repository used here.
