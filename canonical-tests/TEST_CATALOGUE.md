# Complete Test Catalogue with Spec Citations

**Total:** 50 tests
**Last Updated:** 2025-10-07

---

## Lexical & Syntax (8 tests)

| Test | Description | Spec | Category | Expected |
|------|-------------|------|----------|----------|
| 01 | Non-printable ASCII | §4.1.1 | CORE | REJECT |
| 02 | Unclosed comment | §4.1.2 | CORE | REJECT |
| 03 | Unmatched block close | §4.1.3 | CORE | REJECT |
| 04 | Missing $. terminator | §4.1.3 | CORE | REJECT |
| 05 | Empty label | §4.1.3 | CORE | REJECT |
| 06 | Invalid token | §4.1.3 | CORE | REJECT |
| 07 | Valid minimal database | §4.1.3 | CORE | ACCEPT |
| 31 | Nested comments | §4.1.2 | CORE | REJECT |

---

## Scoping (6 tests)

| Test | Description | Spec | Category | Expected |
|------|-------------|------|----------|----------|
| 08 | Variable out of scope | §4.2.8 | CORE | REJECT |
| 35 | $f scope after block | §4.2.8 | CORE | REJECT |
| 45 | Variable redeclaration (sequential) | §4.2.8 | CORE | ACCEPT |
| 46 | Include in inner blocks | §4.1.2, §4.4.4 | **POLICY** | ACCEPT (permissive) |
| 47 | $c in inner scope | §4.2.8 | CORE | REJECT |
| 48 | Variable conflict via include | §4.2.8 | CORE | REJECT |

---

## Validation (8 tests)

| Test | Description | Spec | Category | Expected |
|------|-------------|------|----------|----------|
| 09 | Missing $d constraint | §4.2.4 | CORE | REJECT |
| 10 | Duplicate label | §4.2.1 | CORE | REJECT |
| 11 | Undefined variable | §4.2.3 | CORE | REJECT |
| 12 | Undefined constant | §4.2.3 | CORE | REJECT |
| 13 | Missing $f for variable | §4.2.5 | CORE | REJECT |
| 14 | Conflicting $d constraints | §4.2.4 | CORE | REJECT |
| 15 | Multiple $f for variable | §4.2.5 | CORE | REJECT |
| 16 | Conflicting typecodes (nested) | §4.2.5, §4.2.8 | CORE | REJECT |

---

## Include Handling (13 tests)

### CORE Tests (Strict - §4.1.2)

| Test | Description | Spec | Category | Expected |
|------|-------------|------|----------|----------|
| 17 | Include scope violation | §4.2.8 | CORE | REJECT |
| 28 | Self-include | §4.1.2 | CORE | ACCEPT (ignored) |
| 39 | Basic include | §4.1.2 | CORE | ACCEPT |
| 40 | Include inside ${ ... $} | §4.1.2 | CORE | REJECT |
| 41 | Multiple includes | §4.1.2 | CORE | ACCEPT |
| 42 | Duplicate include | §4.1.2 | CORE | ACCEPT (2nd ignored) |
| 43 | Path canonicalization | §4.1.2 | CORE | ACCEPT |
| 44 | Cycle detection | §4.1.2 | CORE | ACCEPT (cycle ignored) |
| 47 | $c in inner scope via include | §4.2.8 | CORE | REJECT |
| 48 | Variable conflict via include | §4.2.8 | CORE | REJECT |

### POLICY Tests (Permissive)

| Test | Description | Spec | Category | Expected |
|------|-------------|------|----------|----------|
| 46 | Include in inner blocks | §4.1.2 | CORE | REJECT |
| 49 | Token splice in axiom | §4.4.4 (interpretation) | **POLICY** | ACCEPT? (optional) |
| 50 | Token splice in proof | §4.4.4 (interpretation) | **POLICY** | ACCEPT? (optional) |

---

## Proof Verification (15 tests)

| Test | Description | Spec | Category | Expected |
|------|-------------|------|----------|----------|
| 18 | Invalid proof step | §4.3 | CORE | REJECT |
| 19 | Type mismatch in proof | §4.2.5 | CORE | REJECT |
| 20 | Hypothesis not satisfied | §4.2.5 | CORE | REJECT |
| 21 | Proof incomplete | §4.3 | CORE | REJECT |
| 22 | Proof with extra steps | §4.3 | CORE | REJECT |
| 23 | Valid simple proof | §4.3 | CORE | ACCEPT |
| 24 | $e hypothesis usage | §4.2.5 | CORE | ACCEPT |
| 25 | $d constraint check | §4.2.4 | CORE | ACCEPT |
| 26 | Variable substitution | §4.3 | CORE | ACCEPT |
| 27 | Complex proof | §4.3 | CORE | ACCEPT |
| 29 | Proof with undefined label | §4.3 | CORE | REJECT |
| 32 | Circular proof dependency | §4.3 | CORE | REJECT |
| 33 | Compressed proof format | Appendix B | CORE | ACCEPT |
| 34 | Proof with wrong conclusion | §4.3 | CORE | REJECT |
| 37 | RPN interleaving | §4.2.7 | CORE | ACCEPT |

---

## Compressed Proofs (4 tests)

| Test | Description | Spec | Category | Expected |
|------|-------------|------|----------|----------|
| 30 | Invalid compressed format | Appendix B | CORE | REJECT |
| 33 | Valid compressed proof | Appendix B | CORE | ACCEPT |
| 36 | Compressed with bad label | Appendix B | CORE | REJECT |
| 38 | Valid compressed (complex) | Appendix B | CORE | ACCEPT |

---

## Critical Tests (Must Pass)

### Scoping Enforcement
- **Test 47:** $c in inner scope (CRITICAL - catches missing scope check)
- **Test 48:** Variable conflict (CRITICAL - catches scoping bug)

### Include Handling
- **Test 42:** Duplicate include (found mm-lean4 state threading bug)
- **Test 28:** Self-include (spec compliance check)

### Typecode Rules
- **Test 16:** Nested typecode shadowing (strict vs permissive)

---

## Interpretation Notes

### Include Statements (tests 28, 39–44, 46)

- **Outermost only.** Spec §4.1.2 processes `$[ ... $]` before parsing; an include inside an open `${ ... $}` violates the spec. Both `test40` and `test46` therefore expect **REJECT** in strict mode. Some legacy verifiers accept these patterns; that is treated as non-compliant behaviour.
- **Self-include.** `test28` remains **ACCEPT**—the second inclusion is ignored because the file is already on the include stack, matching the spec’s “simply be ignored” wording.

### Optional Extensions (tests 49–50)

Token splicing inside statements is outside the core spec. We keep these as optional **POLICY** tests for experiments; strict runs may skip them.

---

## Running the Suite

### All CORE tests (binding spec)
```bash
./run_tests.sh --strict
# Expected: 48 CORE tests pass
```

### Add optional POLICY tests
```bash
./run_tests.sh --permissive
# Expected: All 50 tests pass
```

---

**Spec References:**
- §4.1.1: Character set (printable ASCII)
- §4.1.2: Preprocessing (comments, includes)
- §4.1.3: Basic syntax
- §4.2.x: Statement types
- §4.3: Proof verification
- Appendix B: Compressed proofs
- Appendix E: Grammar (authoritative)

**Last Updated:** 2025-10-07
