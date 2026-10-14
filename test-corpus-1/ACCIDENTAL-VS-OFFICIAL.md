# Accidental search vs official search

Deviation 1 (`DEVIATIONS.md`). The official search is the only one that decides; this comparison changes nothing in it.

- Accidental: `selectedAt` 2026-10-14T05:59:31.749Z (07:59:31 +02:00, the start of the incident in DEVIATIONS.md), cut-off 2026-04-14 (void).
- Official: `selectedAt` 2026-10-14T06:15:56.353Z, cut-off 2026-04-14.
- Queries identical: True.

## java

| | Accidental | Official |
|---|---|---|
| total_count | 256 | 257 |
| candidates read | 256 | 257 |
| eligible by metadata | 178 | 179 |

- In both: 256. Only in the official (additions): 1. Only in the accidental (removals): 0.
- Same repository, different metadata exclusion: 0. Same repository, different rank: 0.
- The first 40 eligible-by-metadata candidates, in order, are identical in the two searches.

Additions:

- `devlive-community/grantforge` (rank 257, 100★, exclusion: none)

## python

| | Accidental | Official |
|---|---|---|
| total_count | 402 | 402 |
| candidates read | 402 | 402 |
| eligible by metadata | 115 | 115 |

- In both: 402. Only in the official (additions): 0. Only in the accidental (removals): 0.
- Same repository, different metadata exclusion: 0. Same repository, different rank: 11.
- The first 40 eligible-by-metadata candidates, in order, are identical in the two searches.

Rank changes (first 15 by official rank):

- `imfeh2/fora`: 243 → 239
- `mongodb-developer/FARM-Intro`: 239 → 240
- `phalt/clientele`: 240 → 241
- `zimingttkx/Network-Security-Based-On-ML`: 241 → 242
- `B0yko/tern`: 242 → 243
- `openclaw-easy/ViralMint`: 325 → 323
- `Zhongye1/KnowAgenticRAG`: 323 → 324
- `fabriziosalmi/wildbox`: 324 → 325
- `849879772/recruitops-agent`: 330 → 328
- `coady/lupyne`: 328 → 329
- `whichmen/dxl-commerce-agent`: 329 → 330
