# Verifier Comparison

This file summarizes how the main verifiers currently compare against the
authoritative expectations encoded in `run-testsuite-all`.

If this file and `run-testsuite-all` ever disagree, trust `run-testsuite-all`.

## Current Snapshot

Current full-suite snapshot from the latest recorded runs:

| Driver | Verifier | Result | Semantic differences | Harness failures | Log |
|--------|----------|--------|----------------------|------------------|-----|
| `test-mm-lean4` | `mm-lean4` (zar mode) | `180/180` | none | none | `results/test-mm-lean4_20260814_025408.log` |
| `test-metamath` | `metamath-exe` | `168/180` | `test15`, `test16`, `test28`, `test40`, `test44`, `test49`, `test50`, `test87`, `test89`, `test90`, `test91`, `test99` | none | `results/test-metamath_20260814_025438.log` |
| `test-metamath-knife` | `metamath-knife` | `171/180` | `test19`, `test20`, `test28`, `test30`, `test44`, `test67`, `test100` | `test01`, `test48` | `results/test-metamath-knife_20260814_025446.log` |

This comparison tracks the harness drivers above. Mode-level differences inside
`mm-lean4` are documented in that project's `ModeConfig`.

The previous independent tri-valued differential compared semantic verdicts
for `175/177` knife cases with zero mirror mismatches. It predates `test98`,
`test99`, and `test100`; the current full-driver run verifies that Knife
rejects the first two negative cases but accepts the explicit mandatory-header
duplicate in `test100`. `metamath-knife` terminated
abnormally on `test01` and `test48`; these are process failures, not semantic
rejections. `run-testsuite-all` preserves those outcomes as harness failures.

## What The Harness Means

- `run-testsuite-all` is the source of truth for expected verdicts.
- This file only explains the current differences between implementations.
- The expectations are spec-driven, with explicit policy choices recorded in
  `run-testsuite-all`.

## mm-lean4

`mm-lean4` in zar mode currently matches the full suite exactly: `180/180`.

In this harness, `test-mm-lean4` is the primary spec-facing comparison driver.

## metamath-exe

`metamath-exe` currently diverges on twelve tests:

In this harness, `test-metamath` is the public comparison driver for
`metamath-exe`.

- `test15_multiple_f_for_same_variable_bad.mm`
  - accepts a second `$f` for a variable while the first `$f` is still active
- `test16_conflicting_typecodes_bad.mm`
  - accepts the same simultaneous-activity violation across nested blocks
- `test40_include_scope_correct_outer.mm`
  - accepts `$[ ... $]` inside an inner block, while the harness rejects it
- `test49_token_splice_axiom.mm`
  - accepts token splicing across includes, while the harness rejects it
- `test50_token_splice_proof.mm`
  - same token-splicing issue as `test49`
- `test28_self_include.mm` and `test44_include_cycle_main.mm`
  - rejects a self-include / include cycle that section 4.1.2 says to ignore
    as a later reference
- `test87`, `test89`, `test90`, `test91` (include child completeness)
  - accepts an included file that ends mid-statement, mid-`$a`, mid-`$p`, or
    with an open block, while the harness rejects it
- `test99_compressed_repeated_save_alias_bad.mm`
  - accepts a repeated `Z` after a completed compressed-proof label use, while
    the strict Appendix B grammar permits exactly one immediate save marker

In short: `metamath-exe` is more permissive than the harness on selected
include-scope, child-boundary, token-boundary, and active-`$f` cases, and
stricter than the harness on self-includes and cycles. It rejects
`test98_compressed_save_interrupts_index_bad.mm` as expected, but accepts the
repeated-save alias isolated by `test99`.

## metamath-knife

`metamath-knife` currently diverges on seven semantic tests and encounters two
harness failures:

- `test20_unknown_step_qmark_(should_accept_with_warning).mm`
  - rejects `?` in an ordinary proof where the harness accepts it
- `test30_qmark_in_compressed_proof.mm`
  - rejects `?` in a compressed proof where the harness accepts it
- `test67_toplevel_essential.mm`
  - rejects a top-level `$e` where the harness accepts it
- `test19_illegal_characters_in_compressed_proof.mm`
  - accepts compressed-proof bytes outside `A`-`Z` and `?` that the harness
    rejects under the strict Appendix B reading
- `test28_self_include.mm` and `test44_include_cycle_main.mm`
  - rejects a self-include / include cycle that section 4.1.2 says to ignore
    as a later reference
- `test100_compressed_header_explicit_mandatory_hyp_bad.mm`
  - accepts an implicit mandatory hypothesis repeated in the explicit
    compressed-proof header, which Appendix B excludes from that header

In short: `metamath-knife` is stricter than the harness on incomplete proofs,
top-level `$e`, self-includes, and cycles, and more permissive on
compressed-proof bytes.

On `test01` and `test48`, `metamath-knife` aborts while rendering diagnostics.
The harness records these as process failures rather than semantic verdicts.
Knife rejects both compressed-proof phase violations (`test98` and `test99`)
as expected, but accepts the independent header-inventory violation in
`test100`.

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
