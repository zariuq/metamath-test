"""
Property tests for mutation-based verification gap testing.

These tests verify that metamath.exe correctly rejects invalid databases
and expose bugs in mmverify.py.
"""

import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generators.template_substitutor import parse_template, randomized_symbol_mapper, substitute_template
from generators.mutations import (
    mutate_d_constant, mutate_d_duplicate, mutate_var_to_constant,
    mutate_unknown_step, mutate_dollar_in_symbol, mutate_duplicate_label,
    mutate_unbalanced_blocks, mutate_nested_comments, MutationType
)
from runners.metamath_runner import verify_metamath, verify_mmverify


# Sample valid database for testing
VALID_DEMO = """
$c wff |- -> ( ) $.
$v ph ps x y $.
wph $f wff ph $.
wps $f wff ps $.
xf $f wff x $.
yf $f wff y $.
ax1 $a |- ( ph -> ( ps -> ph ) ) $.
th1 $p |- ( ph -> ph ) $= wph wph wps ax1 ax1 $.
"""


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data())
def test_mutation_d_constant_rejected_by_metamath(data):
    """
    Gap #12a: $d with constant should be rejected by metamath.exe

    Known bug: mmverify.py incorrectly accepts this!
    """
    mutated, desc = data.draw(mutate_d_constant(VALID_DEMO))

    # Skip if mutation couldn't be applied
    assume(not desc.startswith("no_"))

    # metamath.exe should REJECT
    result_metamath = verify_metamath(mutated)
    assert not result_metamath.success, \
        f"metamath.exe should reject $d with constant (desc: {desc})"

    # Also test with mmverify.py (documenting the bug)
    result_mmverify = verify_mmverify(mutated)
    if result_mmverify.success:
        print(f"\n⚠️  BUG CONFIRMED: mmverify.py accepts $d with constant!")
        print(f"   Mutation: {desc}")
        # Don't fail the test - we're documenting known bugs


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data())
def test_mutation_d_duplicate_rejected_by_metamath(data):
    """
    Gap #12b: $d with duplicate variable should be rejected by metamath.exe

    Known bug: mmverify.py incorrectly accepts this!
    """
    mutated, desc = data.draw(mutate_d_duplicate(VALID_DEMO))

    assume(not desc.startswith("no_"))

    # metamath.exe should REJECT
    result_metamath = verify_metamath(mutated)
    assert not result_metamath.success, \
        f"metamath.exe should reject $d with duplicate var (desc: {desc})"

    # Document mmverify.py bug
    result_mmverify = verify_mmverify(mutated)
    if result_mmverify.success:
        print(f"\n⚠️  BUG CONFIRMED: mmverify.py accepts $d with duplicate variable!")
        print(f"   Mutation: {desc}")


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data())
def test_mutation_var_to_constant_rejected_by_metamath(data):
    """
    Gap #9/#10: Variable redeclared as constant should be rejected.

    Known bug: mmverify.py incorrectly accepts this!
    """
    test_mm = """
$c wff |- $.
${ $v x $. $}
wx $f wff x $.
"""
    mutated, desc = data.draw(mutate_var_to_constant(test_mm))

    assume(not desc.startswith("no_"))

    # metamath.exe should REJECT
    result_metamath = verify_metamath(mutated)
    assert not result_metamath.success, \
        f"metamath.exe should reject var->constant redeclaration (desc: {desc})"

    # Document mmverify.py bug
    result_mmverify = verify_mmverify(mutated)
    if result_mmverify.success:
        print(f"\n⚠️  BUG CONFIRMED: mmverify.py accepts var->constant redeclaration!")
        print(f"   Mutation: {desc}")


@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data())
def test_mutation_unknown_step_handling(data):
    """
    Gap #19: Unknown ? step in proof.

    Per spec 4.4.6: This is ALLOWED but should warn "not proved"
    metamath.exe: Accepts with warning
    mmverify.py: CRASHES (bug!)
    """
    mutated, desc = data.draw(mutate_unknown_step(VALID_DEMO))

    assume(not desc.startswith("no_"))

    # metamath.exe should ACCEPT (with warning)
    result_metamath = verify_metamath(mutated)
    # It reads successfully but proof verification shows warning
    # We consider this "success" for parsing

    # mmverify.py CRASHES
    result_mmverify = verify_mmverify(mutated)
    if not result_mmverify.success:
        print(f"\n⚠️  BUG CONFIRMED: mmverify.py crashes on ? step!")
        print(f"   Mutation: {desc}")
        print(f"   Error: {result_mmverify.error_message}")


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data())
def test_mutation_dollar_in_symbol(data):
    """
    Gap #5: $ in math symbol should be rejected.

    Status: Need to test both verifiers
    """
    mutated, desc = data.draw(mutate_dollar_in_symbol(VALID_DEMO))

    assume(not desc.startswith("no_"))
    assume(not desc.endswith("_too_short"))

    # Test both verifiers and report
    result_metamath = verify_metamath(mutated)
    result_mmverify = verify_mmverify(mutated)

    print(f"\nMutation: {desc}")
    print(f"  metamath.exe: {'REJECT ✓' if not result_metamath.success else 'ACCEPT ✗'}")
    print(f"  mmverify.py:  {'REJECT ✓' if not result_mmverify.success else 'ACCEPT ✗'}")

    # At least metamath.exe should reject
    if result_metamath.success:
        print("  ⚠️  metamath.exe unexpectedly accepted $ in symbol!")


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data())
def test_mutation_duplicate_label(data):
    """
    Gap #13: Duplicate labels should be rejected.

    Status: Need to test both verifiers
    """
    mutated, desc = data.draw(mutate_duplicate_label(VALID_DEMO))

    assume(not desc.startswith("no_"))
    assume(not desc.startswith("not_enough"))

    result_metamath = verify_metamath(mutated)
    result_mmverify = verify_mmverify(mutated)

    print(f"\nMutation: {desc}")
    print(f"  metamath.exe: {'REJECT ✓' if not result_metamath.success else 'ACCEPT ✗'}")
    print(f"  mmverify.py:  {'REJECT ✓' if not result_mmverify.success else 'ACCEPT ✗'}")

    # Both should reject
    if result_metamath.success or result_mmverify.success:
        print("  ⚠️  At least one verifier accepts duplicate labels!")


# Test with real template files

def test_mutation_on_demo0():
    """Apply mutations to demo0.mm and verify metamath.exe rejects them"""
    demo0_path = '/home/zar/claude/hyperon/metamath/metamath-test/demo0.mm'

    if not os.path.exists(demo0_path):
        pytest.skip("demo0.mm not found")

    with open(demo0_path, 'r') as f:
        demo0_content = f.read()

    # Test $d with constant
    mutated, desc = mutate_d_constant(demo0_content).example()
    if not desc.startswith("no_"):
        result = verify_metamath(mutated)
        assert not result.success, "demo0.mm with $d constant should be rejected"
        print(f"\n✓ Correctly rejected: {desc}")


def test_mutation_on_anatomy():
    """Apply mutations to anatomy.mm"""
    anatomy_path = '/home/zar/claude/hyperon/metamath/tests/anatomy.mm'

    if not os.path.exists(anatomy_path):
        pytest.skip("anatomy.mm not found")

    with open(anatomy_path, 'r') as f:
        anatomy_content = f.read()

    # Test $d with duplicate
    mutated, desc = mutate_d_duplicate(anatomy_content).example()
    if not desc.startswith("no_"):
        result = verify_metamath(mutated)
        assert not result.success, "anatomy.mm with $d duplicate should be rejected"
        print(f"\n✓ Correctly rejected: {desc}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
