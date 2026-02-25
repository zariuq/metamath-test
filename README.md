# metamath-test

Metamath verifier conformance suite for parser + proof-checking behavior.

This repository is focused on verifier correctness, not theorem/library freshness.

## Quick Start

Full suite (authoritative), using the current recommended driver:

```bash
./run-testsuite-all ./test-pverify-op-space
```

Common variants:

```bash
# Fast iteration: skips >=1000-line files and grouped big-unifier negatives
./run-testsuite-all ./test-pverify-op-space --small-only

# Skip only the 30+ minute large corpora
./run-testsuite-all ./test-pverify-op-space --skip-large

# Run against official metamath executable wrapper
./run-testsuite-all ./mmexe.sh

# Run against metamath-knife
./run-testsuite-all ./test-metamath-knife
```

## What Is Authoritative

`run-testsuite-all` is the authoritative executable specification of expected outcomes.

- It contains the PASS/FAIL verdict for every active test.
- It is the source of truth for `tests/core`, `tests/unit`, and `tests/mmverify`.
- If this README and the script ever differ, trust `run-testsuite-all`.

Current active assertion count in `run-testsuite-all`:

- `core`: 40
- `unit`: 80
- `mmverify`: 31
- `total`: 151

Typical `--small-only` run reports `141/141` with `10` skips.

## Test Layout

Active suite is under `tests/`:

- `tests/core/`
  - `small/`: targeted baseline and regression files
  - `medium/`: `hol.mm`, `iset.mm`, `nf.mm`, `ql.mm`
  - `large/`: `set.mm`, `set.2010-08-29.mm`, `set-dist-bad1.mm`
- `tests/unit/`
  - focused spec-edge and parser/proof invariants
- `tests/unit/helpers/`
  - include fragments used by unit include/scope tests (not run directly)
- `tests/mmverify/`
  - compatibility/regression corpus derived from mmverify-style cases

Legacy/archival content exists at repo root (e.g. `unit-tests/`, top-level `*.mm`) for history/backward compatibility. The active conformance harness runs `tests/...`.

## Driver Contract

A driver is any executable taking one `.mm` path and returning:

- exit `0` = accept
- nonzero exit = reject

Examples:

- `test-pverify-op`
- `test-pverify-op-space`
- `test-pverify-op-stream`
- `test-metamath-knife`
- `mmexe.sh`
- `test-mmverify-pl`

All bundled driver scripts apply a 6GB virtual-memory limit (`ulimit -v 6291456`).

## Reference Policy and Choices

Expected outcomes are spec-driven from `SPEC_SECTION_4.txt`, with explicit policy choices where implementations diverge.

Reference tools used for cross-checking:

- official Metamath executable via `mmexe.sh`
- `metamath-knife` via `test-metamath-knife`
- comparison helper: `run_reference_verifiers.sh`

Important explicit choices currently encoded in `run-testsuite-all`:

- Accept incomplete proof marker `?` in normal/compressed proofs (`test20`, `test30`).
- Enforce outermost-only include usage for specific scope tests (`test40`, `test47`).
- Treat duplicate includes as ignored where appropriate (`test42`).
- Accept top-level `$e` (`test67`), with note that `metamath-knife` rejects this case.
- Keep `test59_f_type_global_conflict.mm` as ACCEPT (documented spec-divergence case; all checked implementations currently accept).

When adding/changing policy, update:

1. `run-testsuite-all` verdict lines and reason comments — **this is the only required change**
2. `reference/reference.txt` — supplementary prose summary
3. `SPEC_DIVERGENCES.md` — if behavior diverges from strict spec reading or major implementations

## Adding Tests

1. Add test file under the appropriate active subtree in `tests/`.
2. Add helper include fragments under `tests/unit/helpers/` if needed.
3. Add a `pass` or `fail` line in `run-testsuite-all` with reason/spec citation.
4. Run at least:

```bash
./run-testsuite-all ./test-pverify-op-space --small-only
./run-testsuite-all ./mmexe.sh --small-only
```

## Related Verified Lean Project

Lean-verified Metamath checker project (active branch):

- https://github.com/zariuq/mm-lean4/tree/verified-mm-4.27
