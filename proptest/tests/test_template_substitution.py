"""
Property tests for template substitution.

These tests verify that we can:
1. Parse existing .mm files
2. Generate random symbol mappings
3. Substitute symbols while preserving structure
4. Produce valid Metamath databases
"""

import pytest
from hypothesis import given, settings, assume, example, HealthCheck
from hypothesis import strategies as st

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generators.template_substitutor import (
    parse_template, randomized_symbol_mapper, substitute_template, randomized_template
)
from runners.metamath_runner import verify_metamath, verify_mmverify


# Test template parsing

def test_parse_demo0():
    """Parse demo0.mm and verify we extract the right symbols"""
    demo0_path = '/home/zar/claude/hyperon/metamath/metamath-test/demo0.mm'

    with open(demo0_path, 'r') as f:
        content = f.read()

    constants, variables, labels, typecodes = parse_template(content)

    # Check we found expected elements
    assert 'term' in constants
    assert 'wff' in constants
    assert '|-' in constants
    assert '0' in constants
    assert '+' in constants
    assert '=' in constants

    assert 't' in variables
    assert 'r' in variables
    assert 's' in variables

    assert 'tt' in labels
    assert 'tze' in labels
    assert 'th1' in labels
    assert 'mp' in labels

    assert 'term' in typecodes
    assert 'wff' in typecodes
    assert '|-' in typecodes


# Test symbol mapper

@settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.large_base_example])
@given(mapper=randomized_symbol_mapper(
    constants={'term', 'wff', '0', '+'},
    variables={'t', 'r'},
    labels={'ax1', 'ax2'},
    typecodes={'term', 'wff'}
))
def test_symbol_mapper_no_collisions(mapper):
    """Property: Mapped symbols should not collide"""
    all_mapped = []

    # Get all mapped constants (excluding typecodes)
    for const in {'0', '+'}:
        all_mapped.append(mapper.get_constant(const))

    # Get all mapped variables
    for var in {'t', 'r'}:
        all_mapped.append(mapper.get_variable(var))

    # Check no duplicates
    assert len(all_mapped) == len(set(all_mapped)), \
        f"Symbol collision detected: {all_mapped}"


@settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.large_base_example])
@given(mapper=randomized_symbol_mapper(
    constants={'term', 'wff', '0'},
    variables={'x', 'y'},
    labels={'lbl1', 'lbl2', 'lbl3'},
    typecodes={'term', 'wff'}
))
def test_label_mapper_no_collisions(mapper):
    """Property: Mapped labels should not collide"""
    labels = ['lbl1', 'lbl2', 'lbl3']
    mapped = [mapper.get_label(lbl) for lbl in labels]

    assert len(mapped) == len(set(mapped)), \
        f"Label collision detected: {mapped}"


# Test simple substitution

@given(mapper=randomized_symbol_mapper(
    constants={'term', '0'},
    variables={'t'},
    labels={'ax1'},
    typecodes={'term'}
))
def test_substitute_simple_template(mapper):
    """Property: Substitution should preserve statement structure"""
    template = "$c term 0 $.\n$v t $.\nax1 $a term 0 $."

    result = substitute_template(template, mapper)

    # Should still have same statement count
    assert result.count('$c') == 1
    assert result.count('$v') == 1
    assert result.count('$a') == 1
    assert result.count('$.') == 3


# Integration test: Generate and verify random demo0 variants

@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large, HealthCheck.large_base_example])
@given(st.data())
def test_randomized_demo0_verifies(data):
    """
    Property: Randomized versions of demo0.mm should pass metamath.exe

    This is the KEY test - can we generate valid random databases?
    """
    demo0_path = '/home/zar/claude/hyperon/metamath/metamath-test/demo0.mm'

    with open(demo0_path, 'r') as f:
        template_content = f.read()

    # Parse template
    constants, variables, labels, typecodes = parse_template(template_content)

    # Generate random mapper
    mapper = data.draw(randomized_symbol_mapper(constants, variables, labels, typecodes))

    # Substitute
    randomized = substitute_template(template_content, mapper)

    # Verify with metamath.exe
    result = verify_metamath(randomized)

    if not result.success:
        # Print for debugging
        print("FAILED randomized database:")
        print(randomized[:500])
        print("\nError:", result.error_message)

    assert result.success, f"Randomized demo0 failed verification: {result.error_message}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
