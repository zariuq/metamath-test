"""
Tests for EBNF-based grammar framework.

Tests both the framework itself and its application to Metamath.
Demonstrates language-agnostic design and mutation capabilities.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import sys
import os

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework import (
    EBNFParser, compile_grammar, compile_grammar_with_mutations,
    MutationHook
)


# ============================================================================
# Framework Tests (Language-Agnostic)
# ============================================================================

class TestEBNFParser:
    """Test EBNF parser on simple grammars"""

    def test_parse_simple_rule(self):
        """Test parsing a simple rule"""
        grammar_text = "number ::= [0-9]+"
        parser = EBNFParser()
        grammar = parser.parse(grammar_text)

        assert len(grammar.rules) == 1
        assert grammar.rules[0].name == "number"

    def test_parse_choice(self):
        """Test parsing choice (|)"""
        grammar_text = "bool ::= 'true' | 'false'"
        parser = EBNFParser()
        grammar = parser.parse(grammar_text)

        assert len(grammar.rules) == 1
        rule = grammar.rules[0]
        assert rule.name == "bool"

    def test_parse_sequence(self):
        """Test parsing sequence"""
        grammar_text = "stmt ::= 'if' '(' expr ')'"
        parser = EBNFParser()
        grammar = parser.parse(grammar_text)

        assert len(grammar.rules) == 1

    def test_parse_charrange(self):
        """Test parsing character ranges"""
        test_cases = [
            "[a-z]",
            "[A-Z]",
            "[0-9]",
            "[#x20-#x7E]",
        ]

        for case in test_cases:
            grammar_text = f"test ::= {case}"
            parser = EBNFParser()
            grammar = parser.parse(grammar_text)
            assert len(grammar.rules) == 1

    def test_parse_repetition(self):
        """Test parsing repetition operators"""
        test_cases = [
            ("zero_or_more ::= [a-z]*", "zero_or_more"),
            ("one_or_more ::= [a-z]+", "one_or_more"),
            ("optional ::= [a-z]?", "optional"),
        ]

        for grammar_text, name in test_cases:
            parser = EBNFParser()  # Fresh parser for each case
            grammar = parser.parse(grammar_text)
            assert len(grammar.rules) == 1
            assert grammar.rules[0].name == name


class TestStrategyCompiler:
    """Test Hypothesis strategy compilation"""

    def test_compile_literal(self):
        """Test compiling literal strings"""
        grammar_text = "hello ::= 'world'"
        strategy = compile_grammar(grammar_text, 'hello')

        # Should always generate "world"
        for _ in range(10):
            assert strategy.example() == "world"

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_compile_charrange(self, data):
        """Test compiling character ranges"""
        grammar_text = "digit ::= [0-9]"
        strategy = compile_grammar(grammar_text, 'digit')

        example = data.draw(strategy)
        assert len(example) == 1
        assert example in '0123456789'

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_compile_one_or_more(self, data):
        """Test compiling A+"""
        grammar_text = "digits ::= [0-9]+"
        strategy = compile_grammar(grammar_text, 'digits')

        example = data.draw(strategy)
        assert len(example) >= 1
        assert all(c in '0123456789' for c in example)

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_compile_choice(self, data):
        """Test compiling A | B"""
        grammar_text = "bool ::= 'true' | 'false'"
        strategy = compile_grammar(grammar_text, 'bool')

        example = data.draw(strategy)
        assert example in ('true', 'false')

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_compile_sequence(self, data):
        """Test compiling A B C"""
        grammar_text = "stmt ::= 'if' '(' [0-9]+ ')'"
        strategy = compile_grammar(grammar_text, 'stmt')

        example = data.draw(strategy)
        assert example.startswith('if(')
        assert example.endswith(')')


# ============================================================================
# Metamath-Specific Tests
# ============================================================================

class TestMetamathGrammar:
    """Test framework with Metamath grammar"""

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_generate_math_symbol(self, data):
        """Test generating MATH-SYMBOL"""
        grammar_text = "MATH-SYMBOL ::= [#x21-#x7E] - '$'"
        strategy = compile_grammar(grammar_text, 'MATH-SYMBOL')

        example = data.draw(strategy)
        assert len(example) == 1
        assert ord(example) >= 0x21 and ord(example) <= 0x7E
        assert example != '$'

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_generate_label(self, data):
        """Test generating LABEL"""
        grammar_text = "LABEL ::= [A-Za-z0-9] [A-Za-z0-9._-]*"
        strategy = compile_grammar(grammar_text, 'LABEL')

        example = data.draw(strategy)
        assert len(example) >= 1
        # First char must be alphanumeric
        assert example[0].isalnum()
        # Rest can include ._-
        for c in example[1:]:
            assert c.isalnum() or c in '._-'

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_generate_constant_stmt(self, data):
        """Test generating constant statement"""
        grammar_text = """
        constant-stmt ::= '$c' MATH-SYMBOL+ '$.'
        MATH-SYMBOL ::= [a-z]
        """
        strategy = compile_grammar(grammar_text, 'constant-stmt', max_depth=3)

        example = data.draw(strategy)
        assert example.startswith('$c')
        assert example.endswith('$.')

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_generate_floating_stmt(self, data):
        """Test generating floating hypothesis"""
        grammar_text = """
        floating-stmt ::= LABEL '$f' MATH-SYMBOL MATH-SYMBOL '$.'
        LABEL ::= [A-Za-z]+
        MATH-SYMBOL ::= [a-z]
        """
        strategy = compile_grammar(grammar_text, 'floating-stmt', max_depth=3)

        example = data.draw(strategy)
        assert '$f' in example
        assert example.endswith('$.')


# ============================================================================
# Mutation Tests
# ============================================================================

class TestMutations:
    """Test mutation hooks for generating invalid examples"""

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_mutate_label_with_dollar(self, data):
        """Test mutation: add $ to label (invalid)"""
        grammar_text = "LABEL ::= [A-Za-z0-9]+"

        # Mutation: append $ (invalid character)
        mutations = {
            'LABEL': lambda label: label + '$'
        }

        strategy = compile_grammar_with_mutations(
            grammar_text, 'LABEL', mutations
        )

        example = data.draw(strategy)
        # Should end with $ (invalid)
        assert example.endswith('$')

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
    def test_mutate_constant_stmt_duplicate(self, data):
        """Test mutation: duplicate symbol in $c statement"""
        grammar_text = """
        constant-stmt ::= '$c' symbol '$.'
        symbol ::= [a-z]+
        """

        # Mutation: duplicate the symbol
        mutations = {
            'symbol': lambda s: f"{s} {s}"  # Duplicate
        }

        strategy = compile_grammar_with_mutations(
            grammar_text, 'constant-stmt', mutations, max_depth=3
        )

        example = data.draw(strategy)
        # Should have duplicated symbol
        parts = example.replace('$c', '').replace('$.', '').strip().split()
        assert len(parts) == 2
        assert parts[0] == parts[1]


# ============================================================================
# Language Adaptability Tests
# ============================================================================

class TestLanguageAdaptability:
    """Demonstrate framework works with different language grammars"""

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=5)
    def test_simple_arithmetic(self, data):
        """Test with simple arithmetic grammar (not Metamath)"""
        grammar_text = """
        expr ::= term
        term ::= number
        number ::= [0-9]+
        """

        strategy = compile_grammar(grammar_text, 'expr', max_depth=3)
        example = data.draw(strategy)

        assert all(c.isdigit() for c in example)

    @given(st.data())
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=5)
    def test_simple_lisp(self, data):
        """Test with simple Lisp-like grammar"""
        grammar_text = """
        expr ::= atom | list
        atom ::= [a-z]+
        list ::= '(' expr ')'
        """

        strategy = compile_grammar(grammar_text, 'expr', max_depth=2)
        example = data.draw(strategy)

        # Should be either lowercase letters or parenthesized expr
        assert len(example) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """End-to-end tests combining multiple features"""

    def test_parse_compile_generate(self):
        """Test full pipeline: parse → compile → generate"""
        grammar_text = """
        # Simple statement grammar
        stmt ::= LABEL '$a' symbols '$.'
        LABEL ::= [A-Za-z]+
        symbols ::= [a-z]+
        """

        # Parse
        from framework import EBNFParser
        parser = EBNFParser()
        grammar = parser.parse(grammar_text)

        assert len(grammar.rules) == 3

        # Compile
        strategy = compile_grammar(grammar_text, 'stmt', max_depth=3)

        # Generate
        examples = [strategy.example() for _ in range(10)]

        # Validate
        for example in examples:
            assert '$a' in example
            assert example.endswith('$.')

    def test_mutation_pipeline(self):
        """Test mutation pipeline: parse → compile with hooks → generate invalid"""
        grammar_text = """
        label ::= [A-Za-z]+
        """

        # Add mutation: insert space (invalid for label)
        mutations = {
            'label': lambda l: l[:len(l)//2] + ' ' + l[len(l)//2:]
        }

        strategy = compile_grammar_with_mutations(
            grammar_text, 'label', mutations
        )

        examples = [strategy.example() for _ in range(10)]

        # All should have space (invalid)
        for example in examples:
            assert ' ' in example


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
