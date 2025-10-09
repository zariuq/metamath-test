# Permissive Mode Tests

These tests require `--permissive` mode to pass. They test optional interpretations of the Metamath specification.

## Spec Interpretation

**Strict Mode (Default):** Section 4.1.2 and 4.2.8 are binding
- Includes only at outermost scope
- $c only at outermost scope
- Variable scoping strictly enforced

**Permissive Mode (Optional):** Section 4.4.4 interpretation
- Allows includes in inner blocks (treated as token splices)
- Allows $c in inner blocks (if semantically valid)
- More lenient token splice behavior

## Tests

### Test 46: Duplicate Include in Different Scopes
**File:** `test46_duplicate_include_main.mm`
**Category:** POLICY
**Expected:**
- Strict mode: REJECT (includes not allowed in blocks)
- Permissive mode: ACCEPT (duplicate include ignored)

**Description:** Tests that includes in separate `${ }` blocks work correctly, with second include ignored per spec Section 4.1.2 "first reference processed."

### Test 49: Token Splice in Axiom
**File:** `test49_token_splice_axiom_main.mm`
**Category:** POLICY
**Expected:**
- Strict mode: REJECT
- Permissive mode: ACCEPT (optional)

**Description:** Tests include as token splice within axiom statement. Per spec Section 4.4.4, includes can appear "anywhere" as token splices. This is technically valid but discouraged.

### Test 50: Token Splice in Proof
**File:** `test50_token_splice_proof_main.mm`
**Category:** POLICY
**Expected:**
- Strict mode: REJECT
- Permissive mode: ACCEPT (optional)

**Description:** Tests include as token splice within proof statement. Demonstrates proof steps can be in separate file via token splice.

## Usage

```bash
# Test with mm-lean4
/path/to/mm-lean4 --permissive test46_duplicate_include_main.mm

# Test with mmverify_pure
python3 /path/to/mmverify_pure.py --permissive test46_duplicate_include_main.mm

# Test with goverify (implicitly permissive)
/path/to/mmverify test46_duplicate_include_main.mm
```

## Notes

- **goverify** is implicitly permissive (no flag needed)
- **metamath.exe** uses strict interpretation
- **metamath-knife** uses strict interpretation
- Test 46 may still fail in some verifiers due to frame/scoping issues with inner-block includes
