# Metrics — test-corpus-1

Generated from `metrics.json` by `scripts/render_metrics.py`. The numbers are computed by `scripts/evaluate.py` as pre-registered; this file only renders them.

Review set: 150 of 244 CRITICAL (stratified random sample: {'java': 1, 'python': 149}, seed 20261014).

## Criteria

- **Criterion 1 (precision, D1):** NOT met. Rule: primary point estimate >= 90% with >= 50 reviewed. Primary point estimate 0.7067 (Wilson 95% 0.6294–0.7736), n = 150.
- **Criterion 2 (noise, D2):** NOT met. Thresholds per 1,000 files per language: critical ≤ 5.0, warning ≤ 20.0.

## Precision

| Group | n | TP | FP | U | primary | primary 95% CI | secondary | secondary 95% CI |
|---|---|---|---|---|---|---|---|---|
| **overall** | 150 | 106 | 43 | 1 | 0.7067 | 0.6294–0.7736 | 0.7114 | 0.6341–0.7781 |
| language: java (not conclusive) | 1 | 1 | 0 | 0 | 1.0000 | 0.2065–1.0000 | 1.0000 | 0.2065–1.0000 |
| language: python | 149 | 105 | 43 | 1 | 0.7047 | 0.6270–0.7721 | 0.7095 | 0.6318–0.7766 |
| clustering cap 10/repo | 95 | 56 | 38 | 1 | 0.5895 | 0.4890–0.6830 | 0.5957 | 0.4947–0.6893 |

### By rule

| Group | n | TP | FP | U | primary | primary 95% CI | secondary | secondary 95% CI |
|---|---|---|---|---|---|---|---|---|
| PYVIBE-004 | 2 | 0 | 1 | 1 | 0.0000 | 0.0000–0.6576 | 0.0000 | 0.0000–0.7935 |
| PYVIBE-005 | 9 | 9 | 0 | 0 | 1.0000 | 0.7009–1.0000 | 1.0000 | 0.7009–1.0000 |
| PYVIBE-007 | 5 | 2 | 3 | 0 | 0.4000 | 0.1176–0.7693 | 0.4000 | 0.1176–0.7693 |
| PYVIBE-008 | 1 | 0 | 1 | 0 | 0.0000 | 0.0000–0.7935 | 0.0000 | 0.0000–0.7935 |
| PYVIBE-009 | 47 | 39 | 8 | 0 | 0.8298 | 0.6986–0.9111 | 0.8298 | 0.6986–0.9111 |
| PYVIBE-012 | 24 | 23 | 1 | 0 | 0.9583 | 0.7976–0.9926 | 0.9583 | 0.7976–0.9926 |
| PYVIBE-013 | 55 | 28 | 27 | 0 | 0.5091 | 0.3808–0.6362 | 0.5091 | 0.3808–0.6362 |
| PYVIBE-016 | 4 | 4 | 0 | 0 | 1.0000 | 0.5101–1.0000 | 1.0000 | 0.5101–1.0000 |
| PYVIBE-017 | 1 | 0 | 1 | 0 | 0.0000 | 0.0000–0.7935 | 0.0000 | 0.0000–0.7935 |
| PYVIBE-018 | 1 | 0 | 1 | 0 | 0.0000 | 0.0000–0.7935 | 0.0000 | 0.0000–0.7935 |
| transactions | 1 | 1 | 0 | 0 | 1.0000 | 0.2065–1.0000 | 1.0000 | 0.2065–1.0000 |

## Agreement of the two reviews (blind 20)

- n = 20, raw agreement 0.6000, Cohen's kappa 0.2000.
- Verdicts changed by the second review: C011, C093, C097, C103, C124, C170, C231, C240.
- Undetermined re-reviewed: n = 1, changed from U: none.
- Messages flagged overstated (final verdicts): 2.

## Noise per 1,000 files

| Language | files | critical/1000 | warning/1000 | per-repo critical (median/max) | per-repo warning (median/max) | within D2 |
|---|---|---|---|---|---|---|
| java | 22741 | 0.044 | 0.967 | 0.0/1.07 | 0.0/8.197 | yes |
| python | 5776 | 42.071 | 110.111 | 17.621/1535.714 | 73.394/1214.286 | no |

