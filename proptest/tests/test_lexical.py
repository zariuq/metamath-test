"""
Property tests for lexical generators.

Tests that generated lexical elements conform to Metamath spec.
"""

import pytest
import re
from hypothesis import given, settings, assume
from hypothesis import strategies as st

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generators.lexical import (
    math_symbol, label, whitespace, comment,
    PRINTABLE_ASCII_NO_DOLLAR, LABEL_CHARS
)


# Test MATH-SYMBOL generation

@given(symbol=math_symbol())
def test_math_symbol_no_dollar(symbol):
    """Property: math_symbol() should never contain '$'"""
    assert '$' not in symbol, f"Math symbol contains $: {symbol}"


@given(symbol=math_symbol())
def test_math_symbol_printable_ascii(symbol):
    """Property: math_symbol() should only contain printable ASCII [#x21-#x7e] - '$'"""
    for char in symbol:
        assert char in PRINTABLE_ASCII_NO_DOLLAR, \
            f"Invalid char {repr(char)} in symbol {symbol}"


@given(symbol=math_symbol())
def test_math_symbol_non_empty(symbol):
    """Property: math_symbol() should be non-empty"""
    assert len(symbol) >= 1


@given(symbol=math_symbol(min_length=5, max_length=10))
def test_math_symbol_respects_bounds(symbol):
    """Property: math_symbol() should respect length bounds"""
    assert 5 <= len(symbol) <= 10


@given(symbol=math_symbol(allow_dollar=True))
def test_math_symbol_with_dollar_mutation(symbol):
    """Property: math_symbol(allow_dollar=True) can contain '$' for mutation testing"""
    # Just verify it doesn't crash
    assert len(symbol) >= 1


# Test LABEL generation

@given(lbl=label())
def test_label_valid_chars(lbl):
    """Property: label() should only contain [A-Za-z0-9._-]"""
    for char in lbl:
        assert char in LABEL_CHARS, \
            f"Invalid char {repr(char)} in label {lbl}"


@given(lbl=label())
def test_label_non_empty(lbl):
    """Property: label() should be non-empty"""
    assert len(lbl) >= 1


@given(lbl=label(min_length=10, max_length=15))
def test_label_respects_bounds(lbl):
    """Property: label() should respect length bounds"""
    assert 10 <= len(lbl) <= 15


# Test whitespace generation

@given(ws=whitespace())
def test_whitespace_valid_chars(ws):
    """Property: whitespace() should only contain [ \t\r\n\f]"""
    valid_chars = {' ', '\t', '\r', '\n', '\f'}
    for char in ws:
        assert char in valid_chars, \
            f"Invalid whitespace char {repr(char)}"


@given(ws=whitespace())
def test_whitespace_non_empty(ws):
    """Property: whitespace() should be non-empty"""
    assert len(ws) >= 1


# Test comment generation

@given(cmt=comment())
def test_comment_has_delimiters(cmt):
    """Property: comment() should start with '$(' and contain '$)'"""
    assert cmt.startswith('$('), f"Comment doesn't start with '$(' : {repr(cmt)}"
    assert '$)' in cmt, f"Comment doesn't contain '$)' : {repr(cmt)}"


@given(cmt=comment())
def test_comment_has_trailing_whitespace(cmt):
    """Property: comment() should end with whitespace"""
    # Comment format: '$(' ws content ws '$)' ws
    # So it should end with whitespace after '$)'
    assert cmt.endswith((' ', '\t', '\n', '\r', '\f')), \
        f"Comment doesn't end with whitespace: {repr(cmt)}"


@given(cmt=comment(allow_nesting=False))
def test_comment_no_nested_delimiters(cmt):
    """Property: comment(allow_nesting=False) should not have nested $( or $)"""
    # Extract content between first $( and last $)
    start = cmt.index('$(') + 2
    end = cmt.rindex('$)')
    content = cmt[start:end]

    # Content should not contain $( or $) (they don't nest)
    assert '$(' not in content, f"Nested '$(' in comment: {repr(cmt)}"
    assert '$)' not in content, f"Nested '$)' in comment: {repr(cmt)}"


@given(cmt=comment(allow_nesting=True))
def test_comment_mutation_allows_nesting(cmt):
    """Property: comment(allow_nesting=True) may have nested delimiters"""
    # Just verify it doesn't crash
    assert cmt.startswith('$(')


# Uniqueness tests

@given(symbols=st.lists(math_symbol(), min_size=10, max_size=20, unique=True))
def test_math_symbols_can_be_unique(symbols):
    """Property: Should be able to generate many unique math symbols"""
    # Using unique=True ensures all are different
    unique_count = len(set(symbols))
    assert unique_count == len(symbols), \
        f"Not all unique: {unique_count}/{len(symbols)} unique"


@given(labels=st.lists(label(), min_size=10, max_size=20, unique=True))
def test_labels_can_be_unique(labels):
    """Property: Should be able to generate many unique labels"""
    # Using unique=True ensures all are different
    unique_count = len(set(labels))
    assert unique_count == len(labels), \
        f"Not all unique: {unique_count}/{len(labels)} unique"


# Test that generated symbols are usable in Metamath syntax

@given(sym=math_symbol())
def test_math_symbol_usable_in_c_statement(sym):
    """Property: Generated math symbols should be usable in $c statements"""
    stmt = f"$c {sym} $."
    # Should not contain problematic patterns
    assert '$$' not in stmt
    assert stmt.count('$.') == 1


@given(lbl=label(), tc=math_symbol(), var=math_symbol())
def test_label_usable_in_f_statement(lbl, tc, var):
    """Property: Generated labels should be usable in $f statements"""
    stmt = f"{lbl} $f {tc} {var} $."
    # Should be well-formed
    assert stmt.startswith(lbl)
    assert '$f' in stmt
    assert stmt.endswith('$.')


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
