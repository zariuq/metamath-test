#!/bin/bash
#
# Strict-mode test runner for Metamath verifiers
# Tests CORE spec compliance only (no permissive mode)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Output file with timestamp
OUTPUT_FILE="test_results_strict_$(date +%Y%m%d_%H%M%S).txt"

# Redirect all output to file
exec > "$OUTPUT_FILE" 2>&1

echo "================================"
echo "STRICT MODE TEST SUITE"
echo "Testing Metamath Spec Compliance"
echo "$(date)"
echo "================================"
echo

# Verifier paths
METAMATH_EXE_WRAPPER="./mmverify_wrapper.sh"
METAMATH_KNIFE="metamath-knife"
MM_LEAN4_DIR="../../mm-lean4"
MM_LEAN4="~/.elan/bin/lake env lean --run Metamath.lean"
MMVERIFY_PURE="python3 ../../mmverify/mmverify_pure.py"
GOVERIFY="../../goverify/goverify"

# Core tests (excluding doc-only test 43)
CORE_TESTS=(
  "test01_non-printable_ascii_characters.mm"
  "test02_missing_whitespace_between_tokens.mm"
  "test03_nested_comment_delimiters.mm"
  "test04_unbalanced_block_delimiters.mm"
  "test05_dollar_sign_in_math_symbols.mm"
  "test06_dangling_dollar_sign_at_eof.mm"
  "test07_redeclaration_of_constant.mm"
  "test08_variable_used_outside_scope.mm"
  "test09_d_with_non-variables.mm"
  "test10_duplicate_labels.mm"
  "test11_label_conflicts_with_symbol.mm"
  "test12_non-constant_typecode.mm"
  "test13_f_with_undeclared_variable.mm"
  "test14_variable_without_f_hypothesis.mm"
  "test15_multiple_f_for_same_variable.mm"
  "test16_conflicting_typecodes.mm"
  "test17_include_scope_violation.mm"
  "test18_missing_whitespace_after_comment.mm"
  "test19_illegal_characters_in_compressed_proof.mm"
  "test20_unknown_step_qmark_(should_accept_with_warning).mm"
  "test21_self-referential_proof.mm"
  "test22_typecode_mismatch_in_substitution.mm"
  "test23_using_non-essential_hypotheses.mm"
  "test24_undefined_label_in_proof.mm"
  "test25_missing_space_before_comment.mm"
  "test26_wrong_conclusion_in_proof.mm"
  "test27_disjoint_variable_constraint_violation.mm"
  "test28_self_include.mm"
  "test29_compressed_proof_header_mismatch.mm"
  "test30_qmark_in_compressed_proof.mm"
  "test31_missing_whitespace_after_comment.mm"
  "test32_forward_reference_in_proof.mm"
  "test33_compressed_proof_stack_underflow.mm"
  "test34_label_token_in_math_context.mm"
  "test35_f_not_active_after_block_close.mm"
  "test36_whitespace_in_compressed_proof.mm"
  "test37_rpn_interleaving_mandatory_hyps.mm"
  "test38_whitespace_in_valid_compressed.mm"
  "test39_include_basic_outer.mm"
  "test40_include_scope_correct_outer.mm"
  "test41_include_multiple_main.mm"
  "test42_include_duplicate_main.mm"
  "test44_include_cycle_main.mm"
  "test45_variable_redeclaration.mm"
  "test46_duplicate_include_main.mm"
  "test47_constant_inner_scope_main.mm"
  "test48_variable_conflict_main.mm"
  "test49_token_splice_axiom.mm"
  "test50_token_splice_proof.mm"
)

# Function to run a verifier on a test
run_test() {
  local verifier=$1
  local test_file=$2
  local timeout=5

  case "$verifier" in
    "metamath.exe")
      timeout "$timeout" bash "$METAMATH_EXE_WRAPPER" "$test_file" >/dev/null 2>&1
      ;;
    "metamath-knife")
      timeout "$timeout" "$METAMATH_KNIFE" "$test_file" >/dev/null 2>&1
      ;;
    "mm-lean4")
      cd "$MM_LEAN4_DIR"
      timeout "$timeout" bash -c "$MM_LEAN4 \"$SCRIPT_DIR/$test_file\"" >/dev/null 2>&1
      cd "$SCRIPT_DIR"
      ;;
    "mmverify_pure")
      timeout "$timeout" $MMVERIFY_PURE "$test_file" >/dev/null 2>&1
      ;;
    "goverify")
      timeout "$timeout" "$GOVERIFY" -f "$test_file" >/dev/null 2>&1
      ;;
  esac

  return $?
}

# Run tests for each verifier
for verifier in "metamath.exe" "metamath-knife" "mm-lean4" "mmverify_pure" "goverify"; do
  echo "========================================="
  echo "Testing: $verifier"
  echo "========================================="
  echo

  pass_count=0
  fail_count=0

  for test in "${CORE_TESTS[@]}"; do
    if [ ! -f "$test" ]; then
      echo "  $test: SKIP (not found)"
      continue
    fi

    if run_test "$verifier" "$test"; then
      result="PASS"
      ((pass_count++))
    else
      result="FAIL"
      ((fail_count++))
    fi

    echo "  $test: $result"
  done

  total=$((pass_count + fail_count))
  echo
  echo "Summary: $pass_count/$total passed"
  echo
done

echo "================================"
echo "Test run completed: $(date)"
echo "Results saved to: $OUTPUT_FILE"
echo "================================"
