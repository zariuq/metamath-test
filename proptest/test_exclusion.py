#!/usr/bin/env python3
"""Test exclusion parsing in detail"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from framework import EBNFParser, CharRange

def test_exclusion_regex():
    """Test if the regex pattern matches exclusion syntax"""
    import re

    test_cases = [
        ("[a-z] - 'x'", True, 'x'),
        ('[a-z] - "x"', True, 'x'),
        ("[#x21-#x7E] - '$'", True, '$'),
        ("[0-9] - '0'", True, '0'),
        ("[a-z]", False, None),  # No exclusion
    ]

    pattern = r'(\[[^\]]+\])\s*-\s*["\'](.)["\']'

    print("=" * 70)
    print("Test 1: Regex Pattern Matching")
    print("=" * 70)

    for text, should_match, expected_char in test_cases:
        match = re.match(pattern, text)
        matched = match is not None

        if matched == should_match:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"

        print(f"{status}: {text!r}")
        if match:
            print(f"    Charset: {match.group(1)}")
            print(f"    Exclude: {match.group(2)!r}")
        print()


def test_parser_output():
    """Test what the parser actually returns"""

    test_cases = [
        ("SIMPLE ::= [a-z] - 'x'", CharRange, 'a', 'z', 'x'),
        ("MATH ::= [#x21-#x7E] - '$'", CharRange, 0x21, 0x7E, '$'),
        ("DIGIT ::= [0-9] - '0'", CharRange, '0', '9', '0'),
    ]

    print("=" * 70)
    print("Test 2: Parser Output")
    print("=" * 70)

    for grammar_text, expected_type, exp_start, exp_end, exp_exclude in test_cases:
        parser = EBNFParser()
        grammar = parser.parse(grammar_text)

        if not grammar.rules:
            print(f"✗ FAIL: {grammar_text}")
            print(f"    No rules parsed!")
            continue

        rule = grammar.rules[0]
        expr = rule.expr

        # Check type
        if type(expr).__name__ == expected_type.__name__:
            print(f"✓ Type OK: {grammar_text}")
            print(f"    Got: {type(expr).__name__}")

            # Check details
            if isinstance(expr, CharRange):
                start_match = expr.start == exp_start
                end_match = expr.end == exp_end
                exclude_match = expr.exclude == exp_exclude

                if start_match and end_match and exclude_match:
                    print(f"✓ Details OK:")
                    print(f"    Start: {expr.start} (expected {exp_start})")
                    print(f"    End: {expr.end} (expected {exp_end})")
                    print(f"    Exclude: {expr.exclude!r} (expected {exp_exclude!r})")
                else:
                    print(f"✗ Details WRONG:")
                    if not start_match:
                        print(f"    Start: {expr.start} (expected {exp_start})")
                    if not end_match:
                        print(f"    End: {expr.end} (expected {exp_end})")
                    if not exclude_match:
                        print(f"    Exclude: {expr.exclude!r} (expected {exp_exclude!r})")
        else:
            print(f"✗ Type WRONG: {grammar_text}")
            print(f"    Expected: {expected_type.__name__}")
            print(f"    Got: {type(expr).__name__}")
            print(f"    Expression: {expr}")

        print()


def test_strategy_generation():
    """Test if we can generate characters with exclusion"""
    from framework import compile_grammar

    print("=" * 70)
    print("Test 3: Strategy Generation (if parser works)")
    print("=" * 70)

    grammar = "LETTER ::= [a-z] - 'x'"

    try:
        strategy = compile_grammar(grammar, 'LETTER', max_depth=2)

        # Generate some examples
        examples = [strategy.example() for _ in range(20)]

        print(f"Generated {len(examples)} examples:")
        print(f"  {examples}")

        # Check if 'x' appears (it shouldn't!)
        if 'x' in examples:
            print(f"✗ FAIL: Found excluded character 'x'!")
        else:
            print(f"✓ PASS: No excluded character 'x' found")

        # Check if all are lowercase letters
        if all(len(e) == 1 and e.islower() for e in examples):
            print(f"✓ PASS: All examples are lowercase letters")
        else:
            print(f"✗ FAIL: Some examples are not lowercase letters")

    except Exception as e:
        print(f"✗ FAIL: Could not compile grammar")
        print(f"    Error: {e}")

    print()


if __name__ == "__main__":
    test_exclusion_regex()
    test_parser_output()
    test_strategy_generation()

    print("=" * 70)
    print("Testing Complete")
    print("=" * 70)
