# Metamath Test Suite - Verification Summary

**Date:** 2025-11-30  
**Spec:** SPEC_SECTION_4.txt  
**Verifiers Tested:** metamath-knife, mmexe

## Disputed Tests Analysis

| Test    | File Comment      | Spec Verdict | Spec Citation | knife  | mmexe  | Notes |
|---------|-------------------|--------------|---------------|--------|--------|-------|
| test39  | reject: **False** | **ACCEPT**   | L105-106      | ACCEPT | ACCEPT | ✅ All agree |
| test40  | reject: **True**  | **REJECT**   | L105-106      | REJECT | ACCEPT | ⚠️ mmexe lenient |
| test41  | reject: **False** | **ACCEPT**   | Outermost OK  | ACCEPT | ACCEPT | ✅ All agree |
| test42  | reject: **False** | **ACCEPT**   | L111-113      | ACCEPT | ACCEPT | ✅ All agree |
| test47  | reject: **True**  | **REJECT**   | L105-106      | REJECT | ACCEPT | ⚠️ mmexe lenient |
| test47b | reject: **True**  | **REJECT**   | L1088         | REJECT | REJECT | ✅ All agree |

## Spec Citations (verified against SPEC_SECTION_4.txt)

### L105-106: Include Scope Restriction
```
A file inclusion command consists of $[ followed by a file name
followed by $]. It is only allowed in the outermost scope (i.e., not between ${
and $}) and must not be inside a statement
```

**Tests:** test40, test47 (both have includes inside `${ ... }` blocks)  
**Verdict:** REJECT  
**Compliance:** knife ✅ | mmexe ⚠️ lenient

### L111-113: Duplicate Includes Ignored
```
Only the first reference to a given file is included; any later references to the same
file (whether in the top-level file or in included files) cause the inclusion
command to be ignored (treated like white space).
```

**Tests:** test42 (duplicate include of same file)  
**Verdict:** ACCEPT (second include silently ignored)  
**Compliance:** knife ✅ | mmexe ✅

### L1088: $c in Outermost Block Only
```
All $c statements must be placed in the outermost block.
```

**Tests:** test47b (has `$c inner-const $.` inside `${ ... }` block)  
**Verdict:** REJECT  
**Compliance:** knife ✅ | mmexe ✅

## Reference Verifier Behavior

### metamath-knife (Spec-Compliant)
- ✅ Correctly rejects includes-in-blocks (test40, test47)
- ✅ Correctly accepts duplicate includes (test42)
- ✅ Correctly rejects $c in inner scope (test47b)

### mmexe (Lenient on Include Scope)
- ⚠️ Accepts includes-in-blocks (test40, test47) - **diverges from spec**
- ✅ Correctly accepts duplicate includes (test42)
- ✅ Correctly rejects $c in inner scope (test47b)

**mmexe Design Choice:** The official verifier is lenient on include scope restrictions (L105-106), accepting includes in blocks. This is a known divergence from the written spec but may represent the "living spec" based on reference implementation behavior.

## Corrected Reference Expectations

The `reference/reference.txt` file has been updated to reflect THE SPEC, not any particular verifier:

```
ACCEPT unit/test39_include_basic_outer.mm        # Valid include at outermost scope
REJECT unit/test40_include_scope_correct_outer.mm # L105-106: $[ $] only allowed in outermost scope
ACCEPT unit/test41_include_multiple_main.mm      # Multiple valid includes at outermost scope
ACCEPT unit/test42_include_duplicate_main.mm     # L110-112: duplicate includes are ignored (like whitespace)
REJECT unit/test47_constant_inner_scope_main.mm  # L105-106: $[ $] only allowed in outermost scope
REJECT unit/test47b_constant_inner_scope_direct.mm # L1088: $c must be in outermost block
```

## Test Quality Improvements

**test47 Refactoring:**
- **Before:** Violated TWO rules (include-in-block AND $c-in-inner-scope)
- **After:** Only violates include-in-block rule
- **New test47b:** Clean test for $c-in-inner-scope rule only

This follows the "one error per test" principle for better diagnostics.

## Recommendations for pverify

When testing pverify against this suite:

1. **Expected Spec Compliance:**
   - ACCEPT: test39, test41, test42
   - REJECT: test40, test47, test47b

2. **Known Divergences to Document:**
   - If pverify follows mmexe behavior on includes-in-blocks (test40, test47), document as "lenient like mmexe"
   - If pverify follows knife behavior, document as "spec-compliant"

3. **Current pverify Bugs to Fix:**
   - test42: Should ACCEPT (duplicate includes ignored per L111-113)
   - test47b: Should REJECT ($c in inner scope per L1088)
