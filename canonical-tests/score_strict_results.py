#!/usr/bin/env python3
"""
Score test results against expected outcomes for strict Metamath spec compliance.
"""

import sys
import re

# Expected outcomes for Core tests (True = should pass, False = should fail)
EXPECTED = {
    # Tests 01-19: Basic syntax errors (should REJECT)
    "test01_non-printable_ascii_characters.mm": False,
    "test02_missing_whitespace_between_tokens.mm": False,
    "test03_nested_comment_delimiters.mm": False,
    "test04_unbalanced_block_delimiters.mm": False,
    "test05_dollar_sign_in_math_symbols.mm": False,
    "test06_dangling_dollar_sign_at_eof.mm": False,
    "test07_redeclaration_of_constant.mm": False,
    "test08_variable_used_outside_scope.mm": False,
    "test09_d_with_non-variables.mm": False,
    "test10_duplicate_labels.mm": False,
    "test11_label_conflicts_with_symbol.mm": False,
    "test12_non-constant_typecode.mm": False,
    "test13_f_with_undeclared_variable.mm": False,
    "test14_variable_without_f_hypothesis.mm": False,
    "test15_multiple_f_for_same_variable.mm": False,
    "test16_conflicting_typecodes.mm": False,
    "test17_include_scope_violation.mm": False,
    "test18_missing_whitespace_after_comment.mm": False,
    "test19_illegal_characters_in_compressed_proof.mm": False,

    # Test 20: Unknown step ? (should ACCEPT with warning)
    "test20_unknown_step_qmark_(should_accept_with_warning).mm": True,

    # Tests 21-27: Semantic errors (should REJECT)
    "test21_self-referential_proof.mm": False,
    "test22_typecode_mismatch_in_substitution.mm": False,
    "test23_using_non-essential_hypotheses.mm": False,
    "test24_undefined_label_in_proof.mm": False,
    "test25_missing_space_before_comment.mm": False,
    "test26_wrong_conclusion_in_proof.mm": False,
    "test27_disjoint_variable_constraint_violation.mm": False,

    # Test 28: Self-include (should ACCEPT - spec says ignore)
    "test28_self_include.mm": True,

    # Tests 29-36: Proof errors and edge cases
    "test29_compressed_proof_header_mismatch.mm": False,
    "test30_qmark_in_compressed_proof.mm": True,
    "test31_missing_whitespace_after_comment.mm": False,
    "test32_forward_reference_in_proof.mm": False,
    "test33_compressed_proof_stack_underflow.mm": False,
    "test34_label_token_in_math_context.mm": False,
    "test35_f_not_active_after_block_close.mm": False,
    "test36_whitespace_in_compressed_proof.mm": False,

    # Tests 37-38: Valid edge cases (should ACCEPT)
    "test37_rpn_interleaving_mandatory_hyps.mm": True,
    "test38_whitespace_in_valid_compressed.mm": True,

    # Tests 39-48: Include semantics
    "test39_include_basic_outer.mm": True,   # Basic include (ACCEPT)
    "test40_include_scope_correct_outer.mm": False, # Include in inner block (REJECT)
    "test41_include_multiple_main.mm": True, # Multiple includes (ACCEPT)
    "test42_include_duplicate_main.mm": True, # Duplicate include ignored (ACCEPT)
    "test44_include_cycle_main.mm": True,    # Cycle detection (ACCEPT)
    "test45_variable_redeclaration.mm": True, # Redeclaration across scopes (ACCEPT)
    "test46_duplicate_include_main.mm": False, # Includes in inner blocks (REJECT)
    "test47_constant_inner_scope_main.mm": False, # $c in inner scope (REJECT)
    "test48_variable_conflict_main.mm": False,    # Variable redeclaration conflict (REJECT)

    # Tests 49-50: Token splice (strict mode REJECTS these)
    "test49_token_splice_axiom.mm": False,  # Include in statement (REJECT)
    "test50_token_splice_proof.mm": False,  # Include in proof (REJECT)
}

def parse_results(filename):
    """Parse test results file and extract pass/fail counts per verifier."""
    results = {}
    current_verifier = None

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()

            # Match verifier header
            if line.startswith("Testing:"):
                current_verifier = line.split("Testing:")[1].strip()
                results[current_verifier] = {"tests": {}, "total": 0, "correct": 0}
                continue

            # Match test result
            if current_verifier and ".mm:" in line:
                match = re.match(r'\s*(test\S+\.mm):\s*(PASS|FAIL)', line)
                if match:
                    test_file = match.group(1)
                    passed = (match.group(2) == "PASS")

                    if test_file in EXPECTED:
                        expected_pass = EXPECTED[test_file]
                        correct = (passed == expected_pass)

                        results[current_verifier]["tests"][test_file] = {
                            "passed": passed,
                            "expected": expected_pass,
                            "correct": correct
                        }
                        results[current_verifier]["total"] += 1
                        if correct:
                            results[current_verifier]["correct"] += 1

    return results

def print_summary(results):
    """Print summary of results."""
    print("\n" + "="*60)
    print("STRICT MODE TEST RESULTS - SPEC COMPLIANCE")
    print("="*60)
    print()

    # Sort verifiers by score
    sorted_verifiers = sorted(results.items(),
                             key=lambda x: x[1]["correct"] / max(1, x[1]["total"]),
                             reverse=True)

    for verifier, data in sorted_verifiers:
        total = data["total"]
        correct = data["correct"]
        percentage = (correct / total * 100) if total > 0 else 0

        print(f"{verifier:20s} {correct:3d}/{total:3d} ({percentage:5.1f}%)")

    print()
    print("="*60)

    # Show failures for each verifier
    for verifier, data in sorted_verifiers:
        failures = [test for test, info in data["tests"].items() if not info["correct"]]
        if failures:
            print(f"\n{verifier} - Failures ({len(failures)}):")
            for test in sorted(failures):
                info = data["tests"][test]
                if info["passed"] and not info["expected"]:
                    error_type = "FALSE POSITIVE (accepted invalid)"
                else:
                    error_type = "FALSE NEGATIVE (rejected valid)"
                print(f"  - {test}: {error_type}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 score_strict_results.py <results_file>")
        sys.exit(1)

    results_file = sys.argv[1]
    results = parse_results(results_file)
    print_summary(results)
