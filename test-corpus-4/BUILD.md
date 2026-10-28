# Build record — test-corpus-4 tools (`FROZEN.json`)

The tools of `PREREGISTRATION.md` ("Tools under test"). Joaquín tagged each repository with an annotated
tag on the merge commit of its release PR, after a tree check. The engine artifacts were built locally
from a clean `git archive` export of each tag, never from a working tree. All on 2026-10-28.

## pyvibe-pro `v0.16.0` (package python-vibe-guard)

- Release PR #2 (version 0.16.0 and CHANGELOG only, on top of master `ec317f9`, the test-corpus-3
  fixes declared in the pre-registration). Tag object `f534107c0367007c96ddbc5cda4fdb02a59663c1` →
  commit `e449dd75a325fe2e9ec3ef624ec6b3be054636a5`.
- **Tree check:**
  - `HEAD` = that commit;
  - `git status --porcelain --untracked-files=all` empty;
  - `git diff --stat ec317f9 HEAD` = `CHANGELOG.md`, `README.md`, `pyproject.toml`,
    `pyvibe/__init__.py` only.
- **Build:**
  - `git archive v0.16.0 | tar -x`, then `python -m build --wheel` in a dedicated venv with
    `SOURCE_DATE_EPOCH=1793180889` (the tag commit's time).
  - Python 3.12.3, build 1.6.1, pip 24.0; isolated build environment setuptools 84.2.1, wheel 0.48.0.
- **`python_vibe_guard-0.16.0-py3-none-any.whl`**, 185,960 bytes, sha256
  `92bb8f7ead3ea8458cc8717be673d106689de6e9167011821d2cdc11b0bb8db6`.
- **Checks:**
  - METADATA `python-vibe-guard` `0.16.0`;
  - 62 entries, only `pyvibe/` and its dist-info, no tests;
  - the 56 `pyvibe/` files are byte-identical to the tag, and none is missing;
  - a second build from a fresh export gave the same sha256.

## java-vibe-guard-pro `v3.1.0` (package java-vibe-guard)

- Release PR #2 (version 3.1.0, CHANGELOG and README only, on top of master `18e585c`, the
  test-corpus-3 fixes declared in the pre-registration). Tag object
  `89fd75baa9c62a39fd8771bd63d0a302684338f1` → commit `118711684377b72381598fbfaba0b6fc48fb21ff`.
- **Tree check:**
  - `HEAD` = that commit;
  - status empty. A local mode-only change of `cli/bin/cli.js` (100644 → 100755), which predates
    this work, was discarded first;
  - `git diff --stat 18e585c HEAD` = `CHANGELOG.md`, `README.md`, `cli/README.md`,
    `cli/package-lock.json`, `cli/package.json` only.
- **Build:**
  - `git archive v3.1.0 cli | tar -x`, then `npm pack` in the exported `cli/`. The package has no
    `prepack`/`prepare` script.
  - Node v22.22.1, npm 10.9.4.
- **`java-vibe-guard-3.1.0.tgz`**, 85,026 bytes, 42 entries:
  - sha256 `f276c46c10e4a408287c82cde32844129e49fd795f60d60e3a8e7667b1a5f734`;
  - integrity `sha512-+U0cBni90rLYkPFueUrdi94mgG20WFv+FIn4oxQQl6+CoRQ5e311WGz65oF9dYlkz3j/Lnae6IG88gxSgi4kUA==`.
- **Checks:**
  - the integrity recomputed from the file is identical;
  - the tgz holds only `README.md`, `bin/`, `package.json`, `src/` and `verify/`, with no test or
    fixture;
  - every file is byte-identical to `cli/<file>` at the tag;
  - a second pack from a fresh export gave the same sha256.

## vibe-guard-scan `v0.4.0` (wrapper)

- Release PR #12. Tag object `478a6f65d10a6d274c8fc70715cfebb2b5a03724` → commit
  `9538b50a888018e6eb6e8810f5d39921b7b94fdb`.
- **The engines are in `vendor/`, byte-identical to the two artifacts above** (same sha256):
  - java-vibe-guard is the `file:vendor/java-vibe-guard-3.1.0.tgz` dependency. `package-lock.json`
    pins it by the integrity above, and it is bundled in the wrapper's own tarball;
  - the wheel is in `vendor/` for CI and installation; the wrapper's tarball does not carry it.
- The pyvibe range is `>=0.16.0,<0.17`.
- CI on the PR (Node 18): `npm test` 79/79, `scripts/smoke-pack.sh` OK.
- **Tree check:**
  - `HEAD` = that commit;
  - status empty;
  - `vendor/` sha256 as above.
- **Install:**
  - `rm -rf node_modules && npm ci`; java-vibe-guard `3.1.0` was installed, and the lockfile
    integrity is the one above;
  - no tracked file changed.
- **`vibe-guard --version`** with the pyvibe below: `vibe-guard 0.4.0 (java-vibe-guard 3.1.0; pyvibe 0.16.0)`.

## pyvibe for the runs (dedicated venv)

`~/vibe-guard-evaluation-work/tc4/pyvibe-venv`, Python 3.12.3:

    python-vibe-guard @ file://<build>/dist/python_vibe_guard-0.16.0-py3-none-any.whl --hash=sha256:92bb8f7ead3ea8458cc8717be673d106689de6e9167011821d2cdc11b0bb8db6
    pip install --no-deps --require-hashes -r <that file>

`--no-deps` is safe here: the only dependency, `tomli`, applies to Python < 3.11 only.
`pyvibe --version` → `pyvibe 0.16.0`. It is passed to the wrapper as `VIBE_GUARD_PYVIBE`.

## Verification against `FROZEN.json`

`scripts/run.mjs` `verifyTools` was run without any search or scan, with:
- `VGS` = the wrapper checkout;
- `PYVIBE` = the venv's `pyvibe`;
- `PYVIBE_PRO` and `JVG_PRO` = the engine checkouts;
- `WHEEL` = the wheel above;
- `TGZ` = `vendor/java-vibe-guard-3.1.0.tgz`.

It reported **no problem**:
- the three tags are annotated and resolve to the frozen commits;
- the wrapper is at its commit with no change;
- the wheel and the tgz match by name, sha256 and integrity, and so do the lockfile and the
  installed version;
- the `--version` line matches.

Negative control: with the tgz passed as the wheel and the PATH's pyvibe 0.15.0, it reported the wrong
wheel name, the wrong sha256 and the wrong `--version` line.
