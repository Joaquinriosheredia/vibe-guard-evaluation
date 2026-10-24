# Metrics — test-corpus-2

Assisted verdicts (`DEVIATIONS.md` §3b): J015, J038, J056, J036, J001, J020, J023, J052, J021, P145, P083, P099, P098, P072. Rule: criteria 1 and 2 computed (a) with all verdicts and (b) without the assisted IDs in the audit sample; if they differ, the less favourable is taken (DEVIATIONS.md §3b).

| language | criterion | (a) all verdicts | (b) without assisted | **decides** |
|---|---|---|---|---|
| java | 1 | NOT MET | NOT MET | **NOT MET** |
| java | 2 | MET | MET | **MET** |
| python | 1 | NOT MET | NOT MET | **NOT MET** |
| python | 2 | NOT MET | NOT MET | **NOT MET** |

- **In (b) no java audit case remains: the java audit exists only in the assisted version (a).**

## (a) All verdicts

Rendered by `scripts/evaluate.py` from `metrics.json`.

Reviewed by two independent AIs; disagreements and a sample of 20 audited by the author (`DEVIATIONS.md` §3/§3a).

Reaching 90 % as a point estimate does **not** show with 95 % confidence that the true precision is ≥ 90 %; the Wilson interval is published next to it.

### java

- Corpus: 75 repositories; frozen: 58 java CRITICAL >= 50
- CRITICAL: 58; reviewed 58 (required 50; every CRITICAL finding)
- **Criterion 1 (precision): NOT MET** — primary 0.6724, Wilson 95 % 0.5442–0.7792, n 58 (TP 39, FP 19, U 0); secondary 0.6724 0.5442–0.7792; AI review NOT RELIABLE: Joaquín changed 3 of 20 in the audit (>= 3); primary precision 0.6724 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): MET** — 0.1782 (Wilson-scaled 95 % 0.1201–0.2479; repository bootstrap 0.0349–0.4614; without U 0.1782; CRITICAL density 0.5439/1000)
- Volume (original D2, does not decide): 106639 files; CRITICAL 0.5439/1000, WARNING 1.6504/1000; within D2: {'critical': True, 'warning': True}
- Clustering cap 10/repository (informational): primary 0.4545, n 33
- Messages overstated: 55

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| blocking | 8 | 2 | 6 | 0 | 0.25 | 0.0715–0.5907 |
| kafka-send-timeout | 2 | 2 | 0 | 0 | 1.0 | 0.3424–1.0 |
| transactions | 48 | 35 | 13 | 0 | 0.7292 | 0.59–0.8343 |

### python

- Corpus: 20 repositories; frozen: 168 python CRITICAL >= 100
- CRITICAL: 168; reviewed 100 (required 100; random.Random(20261021).sample of 100)
- **Criterion 1 (precision): NOT MET** — primary 0.66, Wilson 95 % 0.5628–0.7454, n 100 (TP 66, FP 34, U 0); secondary 0.66 0.5628–0.7454; AI review NOT RELIABLE: Joaquín changed 3 of 20 in the audit (>= 3); primary precision 0.66 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): NOT MET** — 13.4305 (Wilson-scaled 95 % 10.0571–17.2701; repository bootstrap 6.3052–17.7102; without U 13.4305; CRITICAL density 39.5015/1000)
- Volume (original D2, does not decide): 4253 files; CRITICAL 39.5015/1000, WARNING 24.4533/1000; within D2: {'critical': False, 'warning': False}
- Clustering cap 10/repository (informational): primary 0.5455, n 44
- Messages overstated: 42

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| PYVIBE-001 | 1 | 1 | 0 | 0 | 1.0 | 0.2065–1.0 |
| PYVIBE-005 | 13 | 0 | 13 | 0 | 0.0 | 0.0–0.2281 |
| PYVIBE-007 | 8 | 8 | 0 | 0 | 1.0 | 0.6756–1.0 |
| PYVIBE-008 | 3 | 1 | 2 | 0 | 0.3333 | 0.0615–0.7923 |
| PYVIBE-009 | 36 | 30 | 6 | 0 | 0.8333 | 0.6811–0.9213 |
| PYVIBE-011 | 2 | 0 | 2 | 0 | 0.0 | 0.0–0.6576 |
| PYVIBE-012 | 22 | 22 | 0 | 0 | 1.0 | 0.8513–1.0 |
| PYVIBE-013 | 10 | 2 | 8 | 0 | 0.2 | 0.0567–0.5098 |
| PYVIBE-017 | 1 | 0 | 1 | 0 | 0.0 | 0.0–0.7935 |
| PYVIBE-018 | 4 | 2 | 2 | 0 | 0.5 | 0.15–0.85 |

### Review

- Agreement A–B: n 158, raw 0.9557, kappa 0.9028; disagreements 7, decided by Joaquín.
- Corrections in the audit: 3/20 (Wilson 95 % 0.0524–0.3604) — AI review **NOT RELIABLE** (rule: >= 3 of 20 changed -> AI review NOT RELIABLE, criterion 1 NOT MET in both languages).
  - java: 1/7 (Wilson 95 % 0.0257–0.5131)
  - python: 2/13 (Wilson 95 % 0.0433–0.4223)
- Overstated in dispute between A and B (set to yes): 69.

## (b) Without the assisted verdicts in the audit sample

Rendered by `scripts/evaluate.py` from `metrics.json`.

Reviewed by two independent AIs; disagreements and a sample of 20 audited by the author (`DEVIATIONS.md` §3/§3a).

Reaching 90 % as a point estimate does **not** show with 95 % confidence that the true precision is ≥ 90 %; the Wilson interval is published next to it.

### java

- Corpus: 75 repositories; frozen: 58 java CRITICAL >= 50
- CRITICAL: 58; reviewed 58 (required 50; every CRITICAL finding)
- **Criterion 1 (precision): NOT MET** — primary 0.6552, Wilson 95 % 0.5267–0.7644, n 58 (TP 38, FP 18, U 2); secondary 0.6786 0.5482–0.786; AI review NOT RELIABLE: Joaquín changed 2 of 10 in the audit (>= 2); primary precision 0.6552 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): MET** — 0.1875 (Wilson-scaled 95 % 0.1281–0.2574; repository bootstrap 0.0353–0.4665; without U 0.1748; CRITICAL density 0.5439/1000)
- Volume (original D2, does not decide): 106639 files; CRITICAL 0.5439/1000, WARNING 1.6504/1000; within D2: {'critical': True, 'warning': True}
- Clustering cap 10/repository (informational): primary 0.4242, n 33
- Messages overstated: 54

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| blocking | 8 | 1 | 5 | 2 | 0.125 | 0.0224–0.4709 |
| kafka-send-timeout | 2 | 2 | 0 | 0 | 1.0 | 0.3424–1.0 |
| transactions | 48 | 35 | 13 | 0 | 0.7292 | 0.59–0.8343 |

### python

- Corpus: 20 repositories; frozen: 168 python CRITICAL >= 100
- CRITICAL: 168; reviewed 100 (required 100; random.Random(20261021).sample of 100)
- **Criterion 1 (precision): NOT MET** — primary 0.64, Wilson 95 % 0.5424–0.7273, n 100 (TP 64, FP 34, U 2); secondary 0.6531 0.5547–0.7399; AI review NOT RELIABLE: Joaquín changed 2 of 10 in the audit (>= 2); primary precision 0.64 < 0.9
- **Criterion 2 (FP/1000 ≤ 5.0): NOT MET** — 14.2206 (Wilson-scaled 95 % 10.7721–18.0759; repository bootstrap 7.1873–18.7883; without U 13.7046; CRITICAL density 39.5015/1000)
- Volume (original D2, does not decide): 4253 files; CRITICAL 39.5015/1000, WARNING 24.4533/1000; within D2: {'critical': False, 'warning': False}
- Clustering cap 10/repository (informational): primary 0.5, n 44
- Messages overstated: 41

| rule | n | TP | FP | U | primary | Wilson 95 % |
|---|---|---|---|---|---|---|
| PYVIBE-001 | 1 | 1 | 0 | 0 | 1.0 | 0.2065–1.0 |
| PYVIBE-005 | 13 | 0 | 13 | 0 | 0.0 | 0.0–0.2281 |
| PYVIBE-007 | 8 | 8 | 0 | 0 | 1.0 | 0.6756–1.0 |
| PYVIBE-008 | 3 | 1 | 2 | 0 | 0.3333 | 0.0615–0.7923 |
| PYVIBE-009 | 36 | 30 | 6 | 0 | 0.8333 | 0.6811–0.9213 |
| PYVIBE-011 | 2 | 0 | 2 | 0 | 0.0 | 0.0–0.6576 |
| PYVIBE-012 | 22 | 21 | 0 | 1 | 0.9545 | 0.782–0.9919 |
| PYVIBE-013 | 10 | 2 | 8 | 0 | 0.2 | 0.0567–0.5098 |
| PYVIBE-017 | 1 | 0 | 1 | 0 | 0.0 | 0.0–0.7935 |
| PYVIBE-018 | 4 | 1 | 2 | 1 | 0.25 | 0.0456–0.6994 |

### Review

- Agreement A–B: n 158, raw 0.9557, kappa 0.9028; disagreements 7, decided by Joaquín.
- Corrections in the audit: 2/10 (Wilson 95 % 0.0567–0.5098) — AI review **NOT RELIABLE** (rule: >= 2 of 10 changed -> AI review NOT RELIABLE, criterion 1 NOT MET in both languages).
  - java: 0/0 (Wilson 95 % —)
  - python: 2/10 (Wilson 95 % 0.0567–0.5098)
- Overstated in dispute between A and B (set to yes): 69.

- Assisted IDs left out of the audit (A = B verdict): J015, J020, J021, J023, J036, J038, J052, P083, P098, P099; assisted disagreements counted as U: J001, J056, P072, P145.

