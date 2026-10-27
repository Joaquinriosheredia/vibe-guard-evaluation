# Metrics — test-corpus-3

Assisted verdicts (`REVIEW-LOG.md`): none. Rule: no assisted verdict declared in REVIEW-LOG.md: (a) all verdicts decides.

## All verdicts

Rendered by `scripts/evaluate.py` from `metrics.json`.

Reviewed by two independent AIs; disagreements and a sample of 20 audited by the author (`PREREGISTRATION.md`, "Review method").

Reaching 90 % as a point estimate does **not** show with 95 % confidence that the true precision is ≥ 90 %; the Wilson interval is published next to it.

### java

- Corpus: 60 repositories; frozen: candidates exhausted with 24 java CRITICAL < 50: criterion 1 NOT MET for java
- CRITICAL: 24; reviewed 24 (required 50; every CRITICAL finding)
- **Criterion 1 (precision): NOT MET** — primary 0.6667, Wilson 95 % 0.4671–0.8203, n 24 (TP 16, FP 7, U 1); secondary 0.6957 0.4913–0.844; AI review NOT RELIABLE: Joaquín changed 5 of 20 in the audit (>= 3); only 24 CRITICAL reviewed, 50 required; primary precision 0.6667 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): MET** — 0.3185 (Wilson-scaled 95 % 0.1717–0.5092; repository bootstrap 0.0–0.7781; without U 0.2908; CRITICAL density 0.9556/1000)
- Volume (original D2, does not decide): 25115 files; CRITICAL 0.9556/1000, WARNING 3.1057/1000; within D2: {'critical': True, 'warning': True}
- Clustering cap 10/repository (informational): primary 0.6667, n 24
- Messages overstated: 12

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| blocking | 10 | 5 | 5 | 0 | 0.5 | 0.2366–0.7634 |
| kafka-send-timeout | 5 | 2 | 2 | 1 | 0.4 | 0.1176–0.7693 |
| transactions | 9 | 9 | 0 | 0 | 1.0 | 0.7009–1.0 |

### python

- Corpus: 20 repositories; frozen: 102 python CRITICAL >= 100
- CRITICAL: 102; reviewed 100 (required 100; random.Random(20261101).sample of 100)
- **Criterion 1 (precision): NOT MET** — primary 0.77, Wilson 95 % 0.6785–0.8416, n 100 (TP 77, FP 23, U 0); secondary 0.77 0.6785–0.8416; AI review NOT RELIABLE: Joaquín changed 5 of 20 in the audit (>= 3); primary precision 0.77 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): MET** — 3.315 (Wilson-scaled 95 % 2.283–4.6337; repository bootstrap 0.5873–6.6858; without U 3.315; CRITICAL density 14.4129/1000)
- Volume (original D2, does not decide): 7077 files; CRITICAL 14.4129/1000, WARNING 25.4345/1000; within D2: {'critical': False, 'warning': False}
- Clustering cap 10/repository (informational): primary 0.8305, n 59
- Messages overstated: 48

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| PYVIBE-002 | 1 | 1 | 0 | 0 | 1.0 | 0.2065–1.0 |
| PYVIBE-006 | 6 | 1 | 5 | 0 | 0.1667 | 0.0301–0.5635 |
| PYVIBE-007 | 1 | 1 | 0 | 0 | 1.0 | 0.2065–1.0 |
| PYVIBE-008 | 2 | 0 | 2 | 0 | 0.0 | 0.0–0.6576 |
| PYVIBE-009 | 56 | 47 | 9 | 0 | 0.8393 | 0.7219–0.9131 |
| PYVIBE-010 | 5 | 5 | 0 | 0 | 1.0 | 0.5655–1.0 |
| PYVIBE-012 | 19 | 18 | 1 | 0 | 0.9474 | 0.7536–0.9906 |
| PYVIBE-014 | 1 | 1 | 0 | 0 | 1.0 | 0.2065–1.0 |
| PYVIBE-017 | 4 | 0 | 4 | 0 | 0.0 | 0.0–0.4899 |
| PYVIBE-018 | 5 | 3 | 2 | 0 | 0.6 | 0.2307–0.8824 |

### Review

- Agreement A–B: n 124, raw 0.9597, kappa 0.9017; disagreements 5, decided by Joaquín.
- Corrections in the audit: 5/20 (Wilson 95 % 0.1119–0.4687) — AI review **NOT RELIABLE** (rule: >= 3 of 20 changed -> AI review NOT RELIABLE, criterion 1 NOT MET in both languages).
  - java: 2/3 (Wilson 95 % 0.2077–0.9385)
  - python: 3/17 (Wilson 95 % 0.0619–0.4103)
- Overstated in dispute between A and B (set to yes): 22.

