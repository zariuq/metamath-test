# metamath-test

Metamath verifier conformance suite for parser + proof-checking behavior.

This repository is focused on verifier correctness, not theorem/library freshness.

## Quick Start

Full suite (authoritative), using a built `mm-lean4` binary through the local wrapper:

```bash
MM_LEAN4=/path/to/mm-lean4/.lake/build/bin/mm-lean4 ./run-testsuite-all ./test-mm-lean4
```

Common variants:

```bash
# Fast iteration: skips >=1000-line files and grouped big-unifier negatives
MM_LEAN4=/path/to/mm-lean4/.lake/build/bin/mm-lean4 ./run-testsuite-all ./test-mm-lean4 --small-only

# Skip only the 30+ minute large corpora
MM_LEAN4=/path/to/mm-lean4/.lake/build/bin/mm-lean4 ./run-testsuite-all ./test-mm-lean4 --skip-large

# Run against the official metamath executable
MMEXE=/path/to/metamath ./run-testsuite-all ./test-metamath

# Run against metamath-knife
METAMATH_KNIFE=/path/to/metamath-knife ./run-testsuite-all ./test-metamath-knife
```

## What Is Authoritative

`run-testsuite-all` is the authoritative executable specification of expected outcomes.

- It contains the PASS/FAIL verdict for every active test.
- It is the source of truth for `tests/core`, `tests/unit`, and `tests/mmverify`.
- If this README and the script ever differ, trust `run-testsuite-all`.

Current active assertion count in `run-testsuite-all`:

- `core`: 40
- `unit`: 106
- `mmverify`: 31
- `total`: 177

A `--small-only` run reports `167/167` with `10` skips for a conforming verifier.

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
- exit `1` = semantic rejection
- exit `2` or higher = harness/process failure

Core local comparison drivers:

- `test-mm-lean4`
- `test-metamath`
- `test-metamath-knife`

Other historical/local drivers also exist in the repo.

## Reference Policy and Choices

Expected outcomes are spec-driven from the
[Metamath book](https://us.metamath.org/downloads/metamath.pdf),
especially Chapter 4 and Appendix B, with explicit policy choices where
implementations diverge.

Suggested comparison verifiers:

- `mm-lean4` via `test-mm-lean4`
- official Metamath executable via `test-metamath`
- `metamath-knife` via `test-metamath-knife`

Important explicit choices currently encoded in `run-testsuite-all`:

- Accept incomplete proof marker `?` in normal/compressed proofs (`test20`, `test30`).
- Enforce outermost-only include usage (`test40`) and outermost-only `$c` declaration (`test47`).
- Treat duplicate includes as ignored where appropriate (`test42`).
- Accept top-level `$e` (`test67`), with note that `metamath-knife` rejects this case.
- Keep `test59_f_type_global_conflict.mm` as ACCEPT (documented spec-divergence case; all checked implementations currently accept).

See `VERIFIER_COMPARISON.md` for the current implementation-difference snapshot
for `mm-lean4`, `metamath-exe`, and `metamath-knife`.

When adding or changing policy, update:

1. `run-testsuite-all` verdict lines and reason comments.
2. `reference/reference.txt` to keep the spec-oriented summary synchronized.
3. `VERIFIER_COMPARISON.md` if implementation differences changed.

## Adding Tests

1. Add the test file under the appropriate active subtree.
2. Add helper include fragments under `tests/unit/helpers/` if needed.
3. Add a `pass` or `fail` line in `run-testsuite-all` with a reason/spec citation.
4. Run at least:

```bash
MM_LEAN4=/path/to/mm-lean4/.lake/build/bin/mm-lean4 ./run-testsuite-all ./test-mm-lean4 --small-only
MMEXE=/path/to/metamath ./run-testsuite-all ./test-metamath --small-only
```

## Related Verified Lean Project

Lean-verified Metamath checker project:

- https://github.com/zariuq/mm-lean4/tree/verified-mm-latest
- versioned branches also available: `verified-mm-4.29`, `verified-mm-4.28`
