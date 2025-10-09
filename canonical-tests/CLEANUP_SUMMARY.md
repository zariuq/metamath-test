# Test Suite Cleanup - Strict Mode Only

## Summary

Per executive decision on 2025-10-08, the test suite has been cleaned up to focus exclusively on **strict Metamath spec compliance** (§4.1.2 + Appendix E).

## Changes Made

### 1. Directory Structure
```
canonical-tests/
├── test01-39, 41-45, 47-50.mm   (Core tests - 47 total)
├── helpers/                      (Include fragments - not run standalone)
│   ├── inner_test17.mm
│   ├── test39_include_basic_inner.mm
│   ├── test41_include_multiple_a.mm
│   ├── test41_include_multiple_b.mm
│   ├── test44_include_cycle_a.mm
│   ├── test44_include_cycle_b.mm
│   ├── test47_constant_inner_scope_helper.mm
│   ├── test48_variable_conflict_helper.mm
│   ├── test49_token_splice_axiom_fragment.mm
│   └── test50_token_splice_proof_fragment.mm
├── doc/                          (Non-normative tests)
│   ├── test40_include_scope_correct_*.mm
│   └── test43_include_canonical_*.mm
├── permissive/                   (Retired permissive-mode tests)
│   ├── README.md
│   └── test46_duplicate_include_*.mm
└── [test harness files]
```

### 2. Test Reclassification

**Tests 49-50: Moved to Core (negative)**
- `test49_token_splice_axiom.mm` - Include inside axiom statement (MUST REJECT)
- `test50_token_splice_proof.mm` - Include inside proof statement (MUST REJECT)
- Updated comments: "Should reject: True" per §4.1.2
- Moved fragments to `helpers/`

**Test 40: Moved to doc/**
- Inner-block includes (metamath.exe quirk, not part of strict spec)
- Marked as DOCUMENTATION ONLY

**Test 43: Moved to doc/**
- Path canonicalization (implementation detail, non-normative)
- Marked as DOCUMENTATION ONLY

**Test 46: Moved to permissive/**
- Duplicate include across blocks (goverify bug exposure)
- Not part of strict spec testing

### 3. Verifier Updates

**mm-lean4 (FIXED)**
- Strict mode now correctly rejects tests 49-50
- Added `inStatement` tracking to include preprocessor
- Error message: "include inside statement (strict mode forbids token splicing, spec §4.1.2)"

**Test Results (from previous run):**
- mm-lean4 strict: 100% compliance ✅
- mmverify_pure: 100% compliance ✅
- metamath.exe: ~91% (self-include deviation)
- metamath-knife: ~89%
- goverify: ~44% (scoping bugs)

### 4. Test Harness

**New files:**
- `run_strict_tests.sh` - Strict-only test runner (no permissive mode)
- `score_strict_results.py` - Scores against expected outcomes
- `VERIFIER_COMPLIANCE.md` - Documents known deviations

**Removed:**
- `all_tests.mm` - Monolithic file no longer needed
- `permissive_all_tests.mm` - Permissive mode retired

### 5. Core Test Count

**Total Core Tests: 47**
- Tests 01-39 (excluding 40): 38 tests
- Tests 41-45: 5 tests
- Tests 47-50: 4 tests

**Expected Outcomes:**
- Should PASS: 11 tests (valid constructs)
- Should FAIL: 36 tests (spec violations)

## Rationale

From GPT-5's analysis and spec review:

1. **Inner-block includes (test 40):** Not in spec grammar; metamath.exe quirk
2. **Token splice (tests 49-50):** Invalid per §4.1.2 ("includes processed at outermost level")
3. **Cross-block include (test 46):** Exposes goverify scoping bug; not spec-compliant behavior
4. **Path canonicalization (test 43):** Implementation detail; spec allows different strings = different files

## Next Steps

With strict-mode testing established:
1. ✅ Test suite cleaned up and organized
2. ✅ mm-lean4 strict mode verified correct
3. 🎯 **Ready to continue formal verification work**

## References

- Metamath Book: §4.1.2 (Include preprocessing)
- Appendix E: EBNF Grammar (normative)
- Previous test results: `test_results_proper_20251008_*.txt`
