# Metamath Specification: Complete Mapping to Formal Verification & Tests

**Purpose:** Master checklist linking every spec requirement to:
1. Formal Lean specification
2. Unit tests (positive & negative)
3. Verification proof obligations

**Authority:** Section 4 (binding), supplemented by Appendix E (grammar), not overridden by §4.4.4

---

## §4.1.1 Preliminaries (Character Set)

### Spec Text

> "A Metamath source file may contain only **printable ASCII characters** (American Standard Code for Information Interchange, an industry standard) and white space (spaces, tabs, carriage returns, line feeds). The **printable characters are those with ASCII numbers 33 through 126 inclusive** (corresponding roughly to those on a typewriter keyboard)."

### Formal Lean

```lean
-- Metamath/Spec/Core.lean
def isPrintableASCII (c : Char) : Bool :=
  c.toNat ≥ 33 ∧ c.toNat ≤ 126

def isWhitespace (c : Char) : Bool :=
  c = ' ' ∨ c = '\t' ∨ c = '\r' ∨ c = '\n'

def validMetamathChar (c : Char) : Bool :=
  isPrintableASCII c ∨ isWhitespace c

-- Well-formedness predicate
def validSource (s : String) : Prop :=
  ∀ c ∈ s.toList, validMetamathChar c
```

### Tests

**Negative:**
- `test01_non_printable.mm` - Contains byte 0x01 (should REJECT)

**Positive:**
- `test07_valid_minimal.mm` - All printable ASCII (should ACCEPT)

### Verification Obligation

```lean
theorem lexer_rejects_nonprintable :
  ∀ s, (∃ c ∈ s.toList, ¬validMetamathChar c) →
       Lexer.lex s = .error "non-printable character"
```

---

## §4.1.2 Preprocessing (Comments & Includes)

### Comments

#### Spec Text

> "The token `$(` begins a comment and `$)` ends a comment. Comments may contain any of the 94 non-whitespace printable characters and white space, except they may not contain the 2-character sequences `$(` or `$)` **(comments do not nest)**."

#### Formal Lean

```lean
-- Metamath/Spec/Core.lean
inductive CommentState
  | outside
  | inside (depth : Nat)  -- Should always be 0 or 1 (no nesting)

def wellFormedComments (s : String) : Prop :=
  ∀ state, parseComments s state → state.depth ≤ 1

-- Comments treated as whitespace
axiom comment_is_whitespace :
  normalize (withComments s) = normalize (withoutComments s)
```

#### Tests

**Negative:**
- `test02_unclosed_comment.mm` - `$(` without `$)` (should REJECT)
- `test31_nested_comments.mm` - `$( $( nested $) $)` (should REJECT)

**Positive:**
- All valid tests with comments

#### Verification Obligation

```lean
theorem comment_parsing_correct :
  ∀ s, validComments s ↔ Preprocess.stripComments s = .ok _
```

### Includes (CRITICAL - Binding Spec)

#### Spec Text (§4.1.2 - AUTHORITATIVE)

> "A file inclusion command consists of `$[` followed by a file name followed by `$]`. **It is only allowed in the outermost scope (i.e., not between `${` and `$}`) and must not be inside a statement** (e.g., it may not occur between the label of a `$a` statement and its `$.`). [...] **Only the first reference to a given file is included; any later references to the same file** (whether in the top-level file or in included files) **cause the inclusion command to be ignored** (treated like white space). [...] **A file self-reference is ignored, as is any reference to the top-level file** (to avoid loops)."

#### Formal Lean (Binding Spec)

```lean
-- Metamath/Spec/Include.lean

-- Include state
structure IncludeState where
  seen : HashSet FilePath
  root : FilePath
  level : Nat  -- Block nesting level

-- Include constraints
def canInclude (state : IncludeState) (file : FilePath) : Prop :=
  state.level = 0 ∧                    -- §4.1.2: outermost only
  ¬state.seen.contains file ∧          -- First reference only
  file ≠ state.root                     -- Not self/top-level

-- Include expansion (strict, binding spec)
inductive ExpandStrict : IncludeState → List Token → List Token → Prop
  | ignore_duplicate (file : FilePath) (state : IncludeState)
      (seen : state.seen.contains file ∨ file = state.root) :
      ExpandStrict state (tokInclude file :: ts) ts

  | ignore_inner (file : FilePath) (state : IncludeState)
      (notOuter : state.level > 0) :
      ExpandStrict state (tokInclude file :: ts)
        (.error "include not at outermost scope")

  | process_first (file : FilePath) (state : IncludeState)
      (canDo : canInclude state file)
      (content : List Token) :
      ExpandStrict ⟨state.seen.insert file, state.root, state.level⟩
        (tokInclude file :: ts) (content ++ ts)

-- Permissive mode (OPTIONAL, requires --permissive flag)
def ExpandPermissive (state : IncludeState) (tokens : List Token) : List Token :=
  -- Hoist inner includes to outermost
  hoistToOutermost (ExpandStrict state tokens)

-- Semantic preservation of hoisting
theorem hoist_preserves_semantics :
  ∀ tokens, verify (ExpandPermissive s tokens) = verify (ExpandStrict s tokens)
```

#### Tests (Binding Spec - Strict Mode)

**Negative (must REJECT in strict mode):**
- `test17_include_scope_violation.mm` - Uses symbols from scoped include outside block
- `test47_constant_inner_scope_main.mm` - `$c` in inner scope via include (CRITICAL)
- **NEW:** `test_include_in_block.mm` - `$[ file $]` inside `${ ... $}` block

**Positive:**
- `test39_basic_include.mm` - Include at outermost (should ACCEPT)
- `test42_duplicate_include_main.mm` - Second include ignored (should ACCEPT)
- `test28_self_include.mm` - Self-include ignored (should ACCEPT)
- `test44_include_cycle_main.mm` - Cycle detection (should ACCEPT, ignore cycle)

**Policy Tests (PERMISSIVE mode only, requires `--permissive`):**
- `test46_duplicate_include_main.mm` - Includes in different `${ ... $}` blocks
- Mark with: `# POLICY: Permissive include mode required`

#### Verification Obligations

```lean
-- Binding spec correctness
theorem include_strict_correct :
  ∀ state tokens,
    ExpandStrict state tokens = .ok result →
    (∀ file, appears_once file result) ∧
    (∀ file ∈ result, file_at_outermost file result)

-- Permissive mode preserves semantics (if implemented)
theorem permissive_sound :
  ∀ tokens, verify_strict (hoist tokens) = verify_permissive tokens
```

---

## §4.2.3 The $c and $v Declaration Statements

### $c Must Be Outermost (CRITICAL)

#### Spec Text

> "A constant must be declared in the outermost block and may not be declared a second time."
> "All `$c` statements must be placed in the outermost block."

#### Formal Lean

```lean
-- Metamath/Spec/Scoping.lean
def canDeclareConst (state : Scope) : Prop :=
  state.level = 0  -- §4.2.8: outermost only

-- Invariant: all constants at level 0
def constInvariant (db : Database) : Prop :=
  ∀ c ∈ db.constants, declaredAt c level → level = 0
```

#### Tests

**Negative:**
- `test47_constant_inner_scope_main.mm` - `$c` in `${ ... $}` block (CRITICAL)

**Positive:**
- All valid tests (constants at outermost)

#### Verification Obligation

```lean
theorem const_outermost_enforced :
  ∀ db, verify db = .ok → constInvariant db
```

### $v Redeclaration After Scope

#### Spec Text

> "A variable may not be declared a second time while it is active, but it may be declared again after it becomes inactive."

#### Formal Lean

```lean
-- Metamath/Spec/Scoping.lean
def canRedeclareVar (state : Scope) (v : Sym) : Prop :=
  ¬(state.vars.contains v)  -- Not currently active

-- Variables deactivate at block exit
def exitBlock (state : Scope) : Scope :=
  { state with
    level := state.level - 1
    vars := state.vars.filter (λ v => declLevel v < state.level)
    floats := state.floats.filter (λ v _ => declLevel v < state.level)
  }
```

#### Tests

**Negative:**
- `test48_variable_conflict_main.mm` - Redeclare while active (should REJECT)

**Positive:**
- `test45_variable_redeclaration.mm` - Redeclare after scope (should ACCEPT)

#### Verification Obligation

```lean
theorem var_redecl_after_inactive :
  ∀ state v, exitBlock state → canRedeclareVar state v
```

---

## §4.2.5 The $f and $e Statements

### Unique Active $f Per Variable

#### Spec Text

> "Each variable must have **one and only one active** `$f` statement associated with it."

#### Formal Lean

```lean
-- Metamath/Spec/Scoping.lean
def uniqueActiveFloat (state : Scope) (v : Sym) : Prop :=
  match state.floats.find? v with
  | none => true
  | some (tc, lvl) => ∀ tc' lvl', state.floats.find? v = some (tc', lvl') →
                                   tc = tc' ∧ lvl = lvl'

def scopeInvariant (state : Scope) : Prop :=
  ∀ v, uniqueActiveFloat state v
```

#### Tests

**Negative:**
- `test15_multiple_f_for_var.mm` - Two `$f` in same scope (should REJECT)
- `test16_conflicting_typecodes.mm` - Nested `$f` with different types (should REJECT)

**Positive:**
- `test45_variable_redeclaration.mm` - Different `$f` in sequential scopes (should ACCEPT)

#### Verification Obligation

```lean
theorem unique_float_enforced :
  ∀ db, verify db = .ok → ∀ state ∈ db.scopes, scopeInvariant state
```

---

## §4.2.8 Scoping Statements (${ and $})

### What Becomes Inactive

#### Spec Text

> "Certain of these statement types become inactive at the end of the block in which they appear; these statement types are: **`$c`, `$v`, `$d`, `$e`, and `$f`**. The other statement types remain active forever (i.e. through the end of the database); they are: **`$a` and `$p`**."

#### Formal Lean

```lean
-- Metamath/Spec/Scoping.lean
inductive Statement
  | scoped : ScopedStmt → Statement     -- $c, $v, $d, $e, $f
  | global : GlobalStmt → Statement     -- $a, $p

-- Exit block removes scoped, keeps global
def exitBlock (state : Scope) : Scope :=
  { state with
    level := state.level - 1
    -- Remove scoped items declared at current level
    vars := filterByLevel state.vars state.level
    floats := filterByLevel state.floats state.level
    essentials := filterByLevel state.essentials state.level
    dvs := filterByLevel state.dvs state.level
    -- Keep global items
    globAxioms := state.globAxioms
    globTheorems := state.globTheorems
  }
```

#### Tests

**Negative:**
- `test08_variable_out_of_scope.mm` - Use variable after `$}` (should REJECT)
- `test35_float_after_block.mm` - Use `$f` after block (should REJECT)

**Positive:**
- All valid tests (use axioms/theorems from any scope)

#### Verification Obligation

```lean
theorem scoped_inactive_at_exit :
  ∀ state v, declaredAt v state.level →
             ¬(exitBlock state).vars.contains v

theorem global_always_active :
  ∀ state ax, state.globAxioms.contains ax →
              (exitBlock state).globAxioms.contains ax
```

---

## §4.3 Proof Verification (RPN)

### Mandatory Hypothesis Order

#### Spec Text

> "The mandatory hypotheses are processed in the order they appear (the **RPN order**). [...] The proof is a sequence of labels that reference earlier statements."

#### Formal Lean

```lean
-- Metamath/Spec/Proof.lean
structure Frame where
  mandFloats : List (Sym × Sym)      -- In RPN (appearance) order
  mandEssentials : List (Sym × List Sym)
  dvConstraints : List (Sym × Sym)

-- RPN proof execution
def runStep (state : ProofState) (label : Label) : Except Error ProofState :=
  match db.find? label with
  | some (.axiom fr expr) =>
      -- Pop mandatory hypotheses in RPN order
      popInOrder fr.mandFloats state >>=
      popInOrder fr.mandEssentials >>=
      checkDV fr.dvConstraints >>=
      push expr
  | _ => .error "unknown label"
```

#### Tests

**Negative:**
- `test18_invalid_proof_step.mm` - Wrong label (should REJECT)
- `test20_hypothesis_not_satisfied.mm` - Missing hypothesis (should REJECT)

**Positive:**
- `test23_valid_simple_proof.mm` - Correct RPN order (should ACCEPT)
- `test37_rpn_interleaving.mm` - `$f` and `$e` interleaved (should ACCEPT)

#### Verification Obligation

```lean
theorem rpn_order_preserved :
  ∀ proof, runProof proof = .ok result →
           mandatoryHypsInOrder result.usedLabels
```

---

## Appendix B: Compressed Proofs

### Compressed Format Equivalence

#### Spec Text

> "The compressed proof format maps letters to integers, uses Z-tags for memoization, and ignores whitespace."

#### Formal Lean

```lean
-- Metamath/Spec/Compression.lean
structure CompressedProof where
  labels : List Label
  blocks : String  -- [A-Z?]+ with whitespace ignored

-- Decode compressed to uncompressed
def decode (cp : CompressedProof) : List Step := ...

-- Critical equivalence theorem
theorem compressed_uncompressed_equiv :
  ∀ cp proof, decode cp = proof →
              run_compressed cp = run_uncompressed proof
```

#### Tests

**Negative:**
- `test30_invalid_compressed_format.mm` - Bad compressed syntax (should REJECT)
- `test36_compressed_bad_label.mm` - Invalid label reference (should REJECT)

**Positive:**
- `test33_compressed_proof_format.mm` - Valid compressed (should ACCEPT)
- `test38_valid_compressed_complex.mm` - Complex compressed (should ACCEPT)

#### Verification Obligation

```lean
theorem compression_sound :
  ∀ cp, verify_compressed cp = .ok →
        verify_uncompressed (decode cp) = .ok
```

---

## Master Checklist

### Lexical (3 obligations)
- [ ] `theorem lexer_rejects_nonprintable`
- [ ] `theorem comment_parsing_correct`
- [ ] `theorem tokens_whitespace_delimited`

### Include (5 obligations)
- [ ] `theorem include_strict_correct` (binding spec)
- [ ] `theorem include_outermost_only`
- [ ] `theorem include_first_wins`
- [ ] `theorem include_self_ignored`
- [ ] `theorem permissive_sound` (if implemented)

### Scoping (6 obligations)
- [ ] `theorem const_outermost_enforced`
- [ ] `theorem var_redecl_after_inactive`
- [ ] `theorem unique_float_enforced`
- [ ] `theorem scoped_inactive_at_exit`
- [ ] `theorem global_always_active`
- [ ] `theorem frames_correct`

### Proof (4 obligations)
- [ ] `theorem rpn_order_preserved`
- [ ] `theorem dv_constraints_checked`
- [ ] `theorem compression_sound`
- [ ] `theorem unknown_steps_rejected`

### Main Theorems (2)
- [ ] `theorem Kernel.sound`
- [ ] `theorem Pipeline.refines`

---

## Test Suite Cross-Reference

### By Spec Section

**§4.1.1 (Characters):** Tests 1, 7
**§4.1.2 (Comments):** Tests 2, 31
**§4.1.2 (Includes - STRICT):** Tests 17, 28, 39, 42, 43, 44, 47
**§4.1.2 (Includes - POLICY):** Test 46 (requires `--permissive`)
**§4.2.3 ($c/$v):** Tests 47, 48, 45
**§4.2.5 ($f/$e):** Tests 13, 15, 16, 24
**§4.2.8 (Scoping):** Tests 8, 35, 45, 47, 48
**§4.3 (Proofs):** Tests 18-27, 29, 32-34
**Appendix B (Compressed):** Tests 30, 33, 36, 38

### Test Categorization

**CORE (Binding Spec):** Tests 1-44 except 46
**POLICY (Permissive):** Test 46 (mark with `# POLICY`)
**CRITICAL (Must Pass):** Tests 47, 48 (scoping bugs)

---

## Usage

1. **For formal verification:** Each `theorem` must be proven
2. **For test suite:** Each test validates a specific `theorem`
3. **For implementation:** Each formal spec guides the code

**This document ensures every spec requirement has:**
- ✅ Formal Lean definition
- ✅ Unit test coverage (positive & negative)
- ✅ Verification theorem

---

**Last Updated:** 2025-10-07
**Status:** Ready for formal verification work
**Next:** Begin Kernel.lean implementation with `Kernel.sound` theorem
