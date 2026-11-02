# Metrics — test-corpus-4

Assisted verdicts (`REVIEW-LOG.md`): none. Rule: no assisted verdict declared in REVIEW-LOG.md: (a) all verdicts decides.

## All verdicts

Rendered by `scripts/evaluate.py` from `metrics.json`.

Every finding of the review set reviewed by the author (Joaquín) under REVIEW-CRITERIA.md v1; no AI verdict enters (`PREREGISTRATION.md`, "Review method").

Reaching 90 % as a point estimate does **not** show with 95 % confidence that the true precision is ≥ 90 %; the Wilson interval is published next to it.

### java

- Corpus: 150 repositories; frozen: 60 java CRITICAL >= 50
- CRITICAL: 60; reviewed 60 (required 50; every CRITICAL finding)
- **Criterion 1 (precision): NOT MET** — primary 0.3167, Wilson 95 % 0.2131–0.4423, n 60 (TP 19, FP 26, U 15); secondary 0.4222 0.2897–0.567; primary precision 0.3167 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): MET** — 0.6264 (Wilson-scaled 95 % 0.5113–0.7214; repository bootstrap 0.3149–1.0185; without U 0.5297; CRITICAL density 0.9167/1000)
- Volume (original D2, does not decide): 65450 files; CRITICAL 0.9167/1000, WARNING 4.2475/1000; within D2: {'critical': True, 'warning': True}
- Clustering cap 10/repository (informational): primary 0.3167, n 60
- Messages overstated: 56

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| blocking | 11 | 7 | 2 | 2 | 0.6364 | 0.3538–0.8483 |
| blocking-kafka | 1 | 1 | 0 | 0 | 1.0 | 0.2065–1.0 |
| kafka-send-timeout | 6 | 6 | 0 | 0 | 1.0 | 0.6097–1.0 |
| reactor-block | 3 | 0 | 0 | 3 | 0.0 | 0.0–0.5615 |
| transactions | 39 | 5 | 24 | 10 | 0.1282 | 0.056–0.2671 |

### python

- Corpus: 90 repositories; frozen: 104 python CRITICAL >= 100
- CRITICAL: 104; reviewed 100 (required 100; random.Random(20261201).sample of 100)
- **Criterion 1 (precision): NOT MET** — primary 0.85, Wilson 95 % 0.7672–0.9069, n 100 (TP 85, FP 8, U 7); secondary 0.914 0.8393–0.9558; primary precision 0.85 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): MET** — 0.8697 (Wilson-scaled 95 % 0.5398–1.3497; repository bootstrap 0.3992–1.3866; without U 0.4987; CRITICAL density 5.7977/1000)
- Volume (original D2, does not decide): 17938 files; CRITICAL 5.7977/1000, WARNING 30.9957/1000; within D2: {'critical': False, 'warning': False}
- Clustering cap 10/repository (informational): primary 0.8462, n 91
- Messages overstated: 62

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| PYVIBE-002 | 11 | 9 | 0 | 2 | 0.8182 | 0.523–0.9486 |
| PYVIBE-006 | 2 | 0 | 2 | 0 | 0.0 | 0.0–0.6576 |
| PYVIBE-007 | 11 | 11 | 0 | 0 | 1.0 | 0.7412–1.0 |
| PYVIBE-008 | 1 | 1 | 0 | 0 | 1.0 | 0.2065–1.0 |
| PYVIBE-010 | 3 | 3 | 0 | 0 | 1.0 | 0.4385–1.0 |
| PYVIBE-012 | 55 | 54 | 0 | 1 | 0.9818 | 0.9039–0.9968 |
| PYVIBE-014 | 2 | 1 | 1 | 0 | 0.5 | 0.0945–0.9055 |
| PYVIBE-016 | 3 | 2 | 1 | 0 | 0.6667 | 0.2077–0.9385 |
| PYVIBE-017 | 3 | 2 | 0 | 1 | 0.6667 | 0.2077–0.9385 |
| PYVIBE-018 | 9 | 2 | 4 | 3 | 0.2222 | 0.0632–0.5474 |

