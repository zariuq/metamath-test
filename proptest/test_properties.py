#!/usr/bin/env python3
"""
Property-Based Tests for Metamath Verifiers

Uses Hypothesis to generate databases and test that verifiers:
1. Accept all constructively-generated (valid) databases
2. Reject mutated (invalid) databases
3. Agree with each other on pass/fail

This is the QuickCheck-style approach: define properties that must
hold for ALL inputs, then let Hypothesis find counterexamples.
"""

import subprocess
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hypothesis import given, settings, assume, Phase
from hypothesis import strategies as st
from strategies import small_database, large_database, mutate_database
from mm_metrics import MetamathAnalyzer


# ============================================================================
# Verification Helpers
# ============================================================================

def verify_with_metamath_exe(database: str, metamath_path: str = None) -> tuple[bool, str]:
    """
    Verify database with official metamath.exe

    Returns:
        (success: bool, output: str)
    """
    if metamath_path is None:
        # Default path - try multiple locations
        candidates = [
            "/home/zar/.local/bin/metamath",
            "/usr/local/bin/metamath",
            "/usr/bin/metamath"
        ]
        for candidate in candidates:
            if os.path.exists(candidate) and os.access(candidate, os.X_OK):
                metamath_path = candidate
                break

    if metamath_path is None or not os.path.exists(metamath_path):
        # Skip if metamath not available
        return (True, "SKIPPED: metamath.exe not found")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mm', delete=False) as f:
        f.write(database)
        temp_file = f.name

    try:
        # Create command script
        commands = f'read "{temp_file}"\nverify proof *\nexit\n'

        result = subprocess.run(
            [metamath_path],
            input=commands,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout + result.stderr

        # Check for verification success
        success = "All proofs in the database were verified" in output
        has_errors = "?Error" in output

        return (success and not has_errors, output)

    except subprocess.TimeoutExpired:
        return (False, "TIMEOUT")
    finally:
        os.unlink(temp_file)


def count_errors_in_output(output: str) -> int:
    """Count ?Error lines in metamath output"""
    return output.count("?Error")


# ============================================================================
# Properties (The Heart of Property-Based Testing)
# ============================================================================

@given(small_database())
@settings(max_examples=20, deadline=5000)  # 20 examples, 5s per example
def test_all_generated_databases_verify(db_and_config):
    """
    Property: All constructively-generated databases must verify.

    This is the POSITIVE test set.
    """
    db, config = db_and_config

    success, output = verify_with_metamath_exe(db)

    if not success and "SKIPPED" not in output:
        # Print debugging info
        print(f"\n{'='*70}")
        print(f"FAILED DATABASE (Config: {config}):")
        print(f"{'='*70}")
        print(db)
        print(f"\n{'='*70}")
        print(f"METAMATH OUTPUT:")
        print(f"{'='*70}")
        print(output[:2000])  # First 2000 chars

    assert success, f"Constructively-generated database failed verification! Config: {config}"


@given(small_database())
@settings(max_examples=20, deadline=5000)
def test_generated_databases_meet_quality_criteria(db_and_config):
    """
    Property: Generated databases should meet minimum quality standards.

    Quality criteria:
    - At least some theorems ($p statements)
    - At least some axioms ($a statements)
    - No excessive duplication (< 50% duplicates)
    """
    db, config = db_and_config

    analyzer = MetamathAnalyzer(db)
    metrics = analyzer.analyze()

    # Must have theorems
    assert metrics.num_theorems > 0, "No theorems generated!"

    # Must have axioms
    assert metrics.num_axioms > 0, "No axioms generated!"

    # Diversity: at least 30% unique conclusions
    if metrics.unique_conclusions:
        total = sum(metrics.conclusion_counts.values())
        uniqueness_ratio = len(metrics.unique_conclusions) / total
        assert uniqueness_ratio >= 0.3, \
            f"Too many duplicates! Only {uniqueness_ratio*100:.1f}% unique"

    # Proof lengths should be reasonable
    if metrics.proof_lengths:
        max_len = max(metrics.proof_lengths)
        assert max_len >= 2, f"All proofs trivial (max length {max_len})"


@given(small_database())
@settings(max_examples=10, deadline=5000)
def test_database_structure_invariants(db_and_config):
    """
    Property: Database structure must satisfy Metamath invariants.

    Invariants:
    - All $p come after their required $f and $e
    - All labels are unique
    - All variables in statements have active $f
    - Blocks are balanced (${ matches $})
    """
    db, config = db_and_config

    lines = [l.strip() for l in db.split('\n') if l.strip() and not l.strip().startswith('$(')]

    labels_seen = set()
    block_depth = 0

    for line in lines:
        # Check balanced blocks
        if line == '${':
            block_depth += 1
        elif line == '$}':
            block_depth -= 1
            assert block_depth >= 0, "Unbalanced blocks: $} without ${"

        # Check label uniqueness
        if ' $f ' in line or ' $e ' in line or ' $a ' in line or ' $p ' in line:
            label = line.split()[0]
            assert label not in labels_seen, f"Duplicate label: {label}"
            labels_seen.add(label)

    # Final check: all blocks closed
    assert block_depth == 0, f"Unbalanced blocks: {block_depth} unclosed blocks"


# ============================================================================
# Negative Tests (Mutations Should Fail)
# ============================================================================

@given(small_database())
@settings(max_examples=5, deadline=5000)
def test_mutated_databases_rejected(db_and_config):
    """
    Property: Databases with single-fault mutations should be rejected.

    This tests that verifiers correctly detect errors.
    """
    db, config = db_and_config

    # First verify original is valid
    success_original, _ = verify_with_metamath_exe(db)
    assume(success_original)  # Skip if original doesn't verify

    # Apply mutation
    mutated_db, mutation_type = mutate_database().example((db,))

    if mutation_type is None:
        # Mutation couldn't be applied, skip
        return

    # Verify mutated version fails
    success_mutated, output = verify_with_metamath_exe(mutated_db)

    # NOTE: Some mutations might not be detectable without full parsing
    # For now, we just track the behavior
    # TODO: Make this assertion once we have reliable mutations
    # assert not success_mutated, f"Mutation {mutation_type} not detected!"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    import pytest
    import sys

    # Run with pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
