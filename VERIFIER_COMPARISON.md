# Verifier Comparison

This file summarizes how the main verifiers currently compare against the
authoritative expectations encoded in `run-testsuite-all`.

If this file and `run-testsuite-all` ever disagree, trust `run-testsuite-all`.

## Current Snapshot

Current full-suite snapshot from the latest recorded runs:

| Driver | Verifier | Score | Diverging tests | Log |
|--------|----------|-------|-----------------|-----|
| `test-mm-lean4` | `mm-lean4` (zar mode) | `150/150` | none | `results/test-mm-lean4_20260514_122911.log` |
| `test-metamath` | `metamath-exe` | `145/150` | `test15`, `test16`, `test40`, `test49`, `test50` | `results/test-metamath_20260514_163702.log` |
| `test-metamath-knife` | `metamath-knife` | `147/150` | `test20`, `test30`, `test67` | `results/test-metamath-knife_20260513_133506.log` |

This comparison tracks the harness drivers above. Mode-level differences inside
`mm-lean4` are documented in that project's `ModeConfig`.

## What The Harness Means

- `run-testsuite-all` is the source of truth for expected verdicts.
- This file only explains the current differences between implementations.
- The expectations are spec-driven, with explicit policy choices recorded in
  `run-testsuite-all`.

## mm-lean4

`mm-lean4` in zar mode currently matches the full suite exactly: `150/150`.

In this harness, `test-mm-lean4` is the primary spec-facing comparison driver.

## metamath-exe

`metamath-exe` currently diverges on five tests:

In this harness, `test-metamath` is the public comparison driver for
`metamath-exe`.

- `test15_multiple_f_for_same_variable_bad.mm`
  - accepts a case the harness rejects under the strict reading that `$f`
    type declarations are global
- `test16_conflicting_typecodes_bad.mm`
  - same global-`$f` issue as `test15`
- `test40_include_scope_correct_outer.mm`
  - accepts `$[ ... $]` inside an inner block, while the harness rejects it
- `test49_token_splice_axiom.mm`
  - accepts token splicing across includes, while the harness rejects it
- `test50_token_splice_proof.mm`
  - same token-splicing issue as `test49`

In short: `metamath-exe` is more permissive than the harness on selected
include-scope, token-boundary, and `$f`-globality cases.

## metamath-knife

`metamath-knife` currently diverges on three tests:

- `test20_unknown_step_qmark_(should_accept_with_warning).mm`
  - rejects `?` in an ordinary proof where the harness accepts it
- `test30_qmark_in_compressed_proof.mm`
  - rejects `?` in a compressed proof where the harness accepts it
- `test67_toplevel_essential.mm`
  - rejects a top-level `$e` where the harness accepts it

In short: `metamath-knife` is stricter than the harness on incomplete proofs
and top-level `$e`.

## Shared Agreement Points

Some important scope-policy tests are not current divergence points:

- `test42_include_duplicate_main.mm`
  - all three current drivers accept duplicate includes being ignored
- `test47_constant_inner_scope_direct.mm`
  - all three current drivers reject `$c` in an inner block

## Updating This File

When behavior changes:

1. Re-run the relevant drivers with `run-testsuite-all`.
2. Update the score table and divergence lists here.
3. If expected outcomes changed, update `run-testsuite-all` first.
