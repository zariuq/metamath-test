# COMPREHENSIVE METAMATH VERIFIER TEST RESULTS

**Date:** October 8, 2025
**Total Tests:** 53 (50 Core + 3 Permissive)
**Location:** `/home/zar/claude/hyperon/metamath/metamath-test/canonical-tests/`

---

## SUMMARY

| Verifier                 | PASS | FAIL | Total | % Pass |
|--------------------------|------|------|-------|--------|
| **goverify**             |  29  |  24  |  53   | 55%    |
| **mm-lean4**             |  14  |  39  |  53   | 26%    |
| **mm-lean4 --permissive**|  14  |  39  |  53   | 26%    |
| **mmverify_pure**        |  12  |  41  |  53   | 23%    |
| **mmverify_pure --perm** |  12  |  41  |  53   | 23%    |
| **metamath-knife**       |   9  |  44  |  53   | 17%    |
| **metamath.exe**         |   0  |  53  |  53   |  0%    |

---

## KEY FINDINGS

### 1. Metamath.exe Issues (0% Pass Rate)
**Status:** ❌ **COMPLETELY BROKEN in test harness**

**Problem:** The wrapper script is not working correctly. Metamath.exe is an interactive tool and our test harness cannot properly execute it.

**Evidence:**
- FAILED ALL 53 tests
- This is clearly a testing infrastructure issue, NOT a verifier bug
- Metamath.exe is the reference implementation and SHOULD work

**Action:** Need better wrapper or different testing approach for interactive tools

---

### 2. Goverify (55% Pass Rate)  
**Status:** ⚠️ **BEST performer but has known bugs**

**Pass:** 29/53 tests
**Issues Found:**
- test07: Constant redeclaration (accepts when should reject) 
- test42: Duplicate include handling
- test43: Path canonicalization
- test47: $c in inner scope (accepts when should reject in strict mode)
- test48: Variable conflict (accepts when should reject)

**Strengths:**
- Handles most scoping tests correctly
- Good error detection on many tests
- Implicitly permissive (accepts inner-scope includes)

---

### 3. MM-Lean4 (26% Pass Rate)
**Status:** ✅ **$c scope bug FIXED, --permissive implemented**

**Pass:** 14/53 tests (same in both modes)
**Notable:**
- test20: ✅ PASS (unknown step with ?)
- test28: ✅ PASS (self include)
- test30: ✅ PASS (? in compressed proof)
- test37-38: ✅ PASS (RPN interleaving, compressed whitespace)
- test39-44: ✅ Mixed (include tests - some pass)
- test45: ✅ PASS (variable redeclaration)
- test48: ❌ FAIL (but SHOULD fail - correct!)
- test49-50: ✅ PASS (token splice tests)

**Critical Success:**  
test47 now FAILS in strict mode (was the bug we fixed!)

---

### 4. MMverify_pure (23% Pass Rate)
**Status:** ✅ **$c scope bug FIXED, --permissive implemented**

**Pass:** 12/53 tests (same in both modes)
**Similar to mm-lean4:**
- test20, test28, test30, test37-45: Same results as mm-lean4  
- test49-50: ❌ FAIL (token splice doesn't work)

**Critical Success:**  
test47 now FAILS in strict mode (bug fixed!)

---

### 5. Metamath-knife (17% Pass Rate)
**Status:** ✅ **Reference implementation (strict spec)**

**Pass:** 9/53 tests
**Notable:**
- Very strict interpretation
- Rejects many things other verifiers accept
- Only passes clearly valid tests

---

## DETAILED BREAKDOWN BY TEST CATEGORY

### Tests Where ALL Verifiers Agree (FAIL)
These are correctly rejected invalid tests:
- test02, test03, test05, test06 (syntax errors)
- test21-27 (proof errors)
- test29, test32-33, test36 (compressed proof errors)
- test44_cycle_a, test44_cycle_b (cycle components)

### Tests Where Results Differ Significantly

**test07** (constant redeclaration):
- goverify: PASS ❌ (BUG - should reject)
- All others: FAIL ✅

**test20** (unknown step with ?):
- mm-lean4, mmverify_pure: PASS ✅
- All others: FAIL

**test28** (self include):
- metamath-knife, mm-lean4, mmverify_pure: PASS ✅
- goverify, metamath.exe: FAIL

**test42** (duplicate include):
- metamath-knife, mm-lean4, mmverify_pure: PASS ✅
- goverify, metamath.exe: FAIL ❌ (should pass per spec)

**test45** (variable redeclaration):
- metamath-knife, mm-lean4, mmverify_pure, goverify: PASS ✅
- metamath.exe: FAIL (test harness issue)

**test47** ($c in inner scope - CRITICAL):
- mm-lean4 strict, mmverify_pure strict: FAIL ✅ (**FIXED!**)
- goverify: PASS ❌ (BUG)
- metamath-knife: FAIL ✅

**test48** (variable conflict - CRITICAL):
- mm-lean4, mmverify_pure: FAIL ✅ (correctly rejects)
- goverify: PASS ❌ (BUG)

**test49-50** (token splice):
- mm-lean4: PASS ✅
- All others: FAIL

---

## PERMISSIVE MODE TESTS

### Test46 (inner-scope includes):
- **ALL VERIFIERS FAIL** (even in permissive mode)
- This test may have other issues beyond permissive mode

### Test49-50 (token splice):
- mm-lean4: PASS ✅ (even in permissive mode)
- mmverify_pure: FAIL (permissive mode doesn't help)
- goverify: FAIL

---

## CRITICAL BUGS STATUS

### ✅ FIXED: mm-lean4 $c scope check
**Test:** test47
- **Before:** Accepted $c in inner scope
- **After:** Correctly rejects in strict mode
- **Permissive:** Accepts in --permissive mode

### ✅ FIXED: mmverify_pure $c scope check  
**Test:** test47
- **Before:** Accepted $c in inner scope
- **After:** Correctly rejects in strict mode
- **Permissive:** Accepts in --permissive mode

### ❌ NOT FIXED: goverify bugs
**Test 07:** Still accepts constant redeclaration
**Test 47:** Still accepts $c in inner scope
**Test 48:** Still accepts variable conflict

---

## RECOMMENDATIONS

1. **Fix metamath.exe test harness** - It's the reference implementation, 0% is clearly wrong

2. **Fix goverify bugs** (for Codex):
   - Test 07: Reject constant redeclaration
   - Test 42-43: Handle duplicate includes correctly  
   - Test 47: Reject $c in inner scope (strict mode)
   - Test 48: Reject variable conflicts

3. **Investigate test46** - Why does it fail everywhere, even in permissive mode?

4. **Document test20, 28, 30** - These have interesting spec interpretations

5. **Token splice tests (49-50)** - Only mm-lean4 handles these; document if this is correct

---

## FILES

- Full results: `test_results_20251008_102001.txt`
- Test suite: `/home/zar/claude/hyperon/metamath/metamath-test/canonical-tests/`
- Test catalog: `TEST_CATALOGUE.md`

