# Metamath Canonical Test Suite

**Version:** 3.0 (Strict Mode Only)
**Date:** 2025-10-08
**Core Tests:** 49
**Optional Tests:** 1
**Spec Authority:** Metamath Book + Appendix E (normative grammar)

---

## Quick Start

```bash
# Run all core tests
./run_strict_tests.sh

# Score results
python3 score_strict_results.py test_results_strict_YYYYMMDD_HHMMSS.txt
```

## Test Suite Structure

### Core Tests (49 tests)
Located in main directory: `test01-42.mm`, `test44-50.mm`

**All core tests have definitive expected outcomes per Metamath Book + Appendix E.**

- **Positive tests (11)**: Valid constructs that must PASS
- **Negative tests (38)**: Spec violations that must REJECT

### Optional Tests (1 test)
Located in `optional_tests/` directory

- **test43**: Path canonicalization - **both PASS and REJECT are spec-compliant**

### Helper Files
Located in `helpers/` directory (not run standalone)

- Include fragments, inner files, shared files for multi-file tests

---

## Core Spec Requirements

### Include Semantics (§4.1.2)

✅ **Outermost level only** - includes processed before parsing, not inside blocks
✅ **Not inside statements** - no token splicing mid-axiom or mid-proof
✅ **Self-include ignored** - including same file is no-op
✅ **Duplicates ignored** - second reference to same file ignored
✅ **Cycle detection** - include stack prevents infinite loops
⚠️ **Path deduplication** - string-based is sufficient (canonicalization is optional)

### Scoping Rules (§4.2.8)

✅ **Constants outermost** - all `$c` must be at outermost block
✅ **Variables scoped** - active in current and nested blocks only
✅ **No redeclaration** - while variable is active
✅ **Redeclaration allowed** - after variable becomes inactive

---

## Test Classification

### Must PASS (11 tests)

Valid constructs per spec:

- test20: Unknown step ? (warning OK)
- test28: Self-include (spec says ignore)
- test30: ? in compressed proof
- test37: RPN interleaving mandatory hyps
- test38: Whitespace in valid compressed
- test39: Basic include (outermost)
- test41: Multiple includes (outermost)
- test42: Duplicate include (second ignored)
- test44: Include cycle detection
- test45: Variable redeclaration across scopes

### Must REJECT (38 tests)

**Syntax Errors (18):** 01-19 (except 20), 25, 31
**Semantic Errors (11):** 21-24, 26-27, 29, 32-36
**Include Violations (9):** 17, 40, 46-50

---

## Key Clarifications

### Inner-Block Includes (Tests 40, 46)
❌ **OUT OF SPEC** - Must REJECT

Spec §4.1.2: includes processed "at the outermost level" before parsing. Inner-block includes violate this. metamath.exe accepts test40 as a quirk, but this is not spec-compliant.

### Token Splice (Tests 49, 50)
❌ **OUT OF SPEC** - Must REJECT

Spec §4.1.2: includes processed before parsing, not spliced mid-statement. Attempting to splice `$[ $]` inside `$a` or `$p` statements is invalid.

### Path Canonicalization (Test 43)
✅ **BOTH VALID** - Optional

Spec §4.1.2: "may assume that file names with different strings refer to different files"

- **String-based dedup** (no canonicalization): spec-compliant → REJECT (duplicate labels)
- **Path canonicalization**: policy/extension → PASS (second include ignored)

Both behaviors are correct! Test 43 is in `optional_tests/` for this reason.

---

## Verifier Compliance

| Verifier | Core Compliance | Status |
|----------|----------------|--------|
| **mm-lean4** | 100% (49/49) | ✅ Fully compliant |
| **mmverify_pure** | 100% (49/49) | ✅ Fully compliant |
| **metamath.exe** | ~91% | ⚠️ Some deviations |
| **metamath-knife** | ~89% | ⚠️ Some deviations |
| **goverify** | ~44% | ❌ Major issues |

See `VERIFIER_COMPLIANCE.md` for detailed analysis.

---

## Files

- `run_strict_tests.sh` - Test runner (all 49 core tests)
- `score_strict_results.py` - Scoring script with expected outcomes
- `VERIFIER_COMPLIANCE.md` - Detailed compliance analysis
- `README.md` - This file
- `test01-50.mm` - Individual test files (except test43)
- `helpers/` - Helper files for multi-file tests
- `optional_tests/` - Optional tests (test43)

---

## History

- **2025-10-08 v3.0**: Cleanup for strict-spec only
  - Retired permissive mode
  - Clarified test43 as optional (both behaviors valid per spec)
  - Confirmed tests 40, 46, 49, 50 as negative (out of spec)
  - Final count: **49 core tests, 1 optional test**

- **2025-10-07 v2.0**: Refactored for CORE vs POLICY distinction

---

## References

- [Metamath Book](http://us.metamath.org/downloads/metamath.pdf) - Primary specification
- [Appendix E](http://us.metamath.org/downloads/appendix-e.txt) - EBNF grammar (normative)
- [mm-lean4 verification](../../mm-lean4/) - Formally verified implementation
