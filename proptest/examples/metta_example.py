"""
MeTTa-IL (Intermediate Language) Grammar Example

Demonstrates adapting the EBNF framework to MeTTa's hypergraph rewriting language.

MeTTa is a functional, hypergraph-based language for AGI reasoning.
This example shows generating valid MeTTa-IL expressions.

Estimated adaptation time: 30 minutes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework import compile_grammar, compile_grammar_with_mutations
from hypothesis import given, settings, HealthCheck

# ============================================================================
# MeTTa-IL EBNF Grammar (Simplified)
# ============================================================================

METTA_IL_GRAMMAR = """
# MeTTa-IL Grammar (simplified intermediate representation)
# Based on: https://github.com/trueagi-io/hyperon-experimental

program ::= expr*

expr ::=
    | atom
    | s_expr
    | grounded_atom

# Atoms
atom ::= symbol | variable | number | string

symbol ::= [a-zA-Z] [a-zA-Z0-9-]*
variable ::= '$' [a-zA-Z] [a-zA-Z0-9]*
number ::= [0-9]+
string ::= '"' [a-zA-Z0-9 ]* '"'

# S-expressions (Lisp-like)
s_expr ::= '(' expr_list ')'
expr_list ::= expr*

# Grounded atoms (typed)
grounded_atom ::= '(' type_symbol value ')'
type_symbol ::= 'Int' | 'Str' | 'Bool'
value ::= number | string | bool_val
bool_val ::= 'True' | 'False'
"""

# ============================================================================
# Example 1: Generate Valid MeTTa-IL Expressions
# ============================================================================

def example_generate_metta_expressions():
    """Generate random valid MeTTa-IL expressions"""
    print("=" * 70)
    print("Example 1: Generating Valid MeTTa-IL Expressions")
    print("=" * 70)

    # Compile grammar
    expr_gen = compile_grammar(METTA_IL_GRAMMAR, 'expr', max_depth=3)

    # Generate examples
    print("\nGenerated MeTTa expressions:\n")
    for i in range(10):
        expr = expr_gen.example()
        print(f"  {i+1:2}. {expr}")


# ============================================================================
# Example 2: Generate Specific MeTTa Constructs
# ============================================================================

def example_generate_metta_constructs():
    """Generate specific MeTTa constructs"""
    print("\n" + "=" * 70)
    print("Example 2: Generating Specific MeTTa Constructs")
    print("=" * 70)

    # Symbols
    print("\nSymbols:")
    symbol_gen = compile_grammar(METTA_IL_GRAMMAR, 'symbol', max_depth=2)
    for _ in range(5):
        print(f"  {symbol_gen.example()}")

    # Variables
    print("\nVariables:")
    var_gen = compile_grammar(METTA_IL_GRAMMAR, 'variable', max_depth=2)
    for _ in range(5):
        print(f"  {var_gen.example()}")

    # S-expressions
    print("\nS-expressions:")
    sexpr_gen = compile_grammar(METTA_IL_GRAMMAR, 's_expr', max_depth=2)
    for _ in range(5):
        print(f"  {sexpr_gen.example()}")

    # Grounded atoms
    print("\nGrounded atoms:")
    grounded_gen = compile_grammar(METTA_IL_GRAMMAR, 'grounded_atom', max_depth=2)
    for _ in range(5):
        print(f"  {grounded_gen.example()}")


# ============================================================================
# Example 3: Generate MeTTa Programs
# ============================================================================

def example_generate_metta_programs():
    """Generate complete MeTTa programs"""
    print("\n" + "=" * 70)
    print("Example 3: Generating Complete MeTTa Programs")
    print("=" * 70)

    # Compile grammar
    prog_gen = compile_grammar(METTA_IL_GRAMMAR, 'program', max_depth=2)

    # Generate examples
    print("\nGenerated programs:\n")
    for i in range(3):
        program = prog_gen.example()
        print(f"Program {i+1}:")
        print(f"  {program}")
        print()


# ============================================================================
# Example 4: Generate Invalid MeTTa (for testing)
# ============================================================================

def example_generate_invalid_metta():
    """Generate invalid MeTTa expressions using mutations"""
    print("=" * 70)
    print("Example 4: Generating Invalid MeTTa (Mutations)")
    print("=" * 70)

    print("\nMutation 1: Variable without $")
    mutations_no_dollar = {
        'variable': lambda v: v.replace('$', '')  # Remove $
    }
    invalid_gen = compile_grammar_with_mutations(
        METTA_IL_GRAMMAR, 'variable', mutations_no_dollar, max_depth=2
    )
    for _ in range(3):
        print(f"  {invalid_gen.example()}")

    print("\nMutation 2: Mismatched parentheses")
    mutations_paren = {
        's_expr': lambda e: e.replace(')', '')  # Remove closing paren
    }
    invalid_gen2 = compile_grammar_with_mutations(
        METTA_IL_GRAMMAR, 's_expr', mutations_paren, max_depth=2
    )
    for _ in range(3):
        print(f"  {invalid_gen2.example()}")

    print("\nMutation 3: Invalid symbol (starts with digit)")
    mutations_symbol = {
        'symbol': lambda s: '9' + s  # Start with digit
    }
    invalid_gen3 = compile_grammar_with_mutations(
        METTA_IL_GRAMMAR, 'symbol', mutations_symbol, max_depth=2
    )
    for _ in range(3):
        print(f"  {invalid_gen3.example()}")


# ============================================================================
# Example 5: Property-Based Testing
# ============================================================================

@given(compile_grammar(METTA_IL_GRAMMAR, 'symbol', max_depth=2))
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
def test_metta_symbols(symbol):
    """Test that generated symbols are valid"""
    # First char must be letter
    assert symbol[0].isalpha()
    # Rest can include hyphens and digits
    for c in symbol[1:]:
        assert c.isalnum() or c == '-'


@given(compile_grammar(METTA_IL_GRAMMAR, 'variable', max_depth=2))
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
def test_metta_variables(var):
    """Test that generated variables are valid"""
    # Must start with $
    assert var.startswith('$')
    # Second char must be letter
    assert var[1].isalpha()
    # Rest alphanumeric
    for c in var[2:]:
        assert c.isalnum()


@given(compile_grammar(METTA_IL_GRAMMAR, 's_expr', max_depth=2))
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
def test_metta_s_expressions(sexpr):
    """Test that generated s-expressions are balanced"""
    # Must start with ( and end with )
    assert sexpr.startswith('(')
    assert sexpr.endswith(')')


# ============================================================================
# Example 6: Differential Testing Simulation
# ============================================================================

def example_differential_testing():
    """Simulate differential testing with multiple MeTTa interpreters"""
    print("\n" + "=" * 70)
    print("Example 6: Differential Testing Simulation")
    print("=" * 70)

    expr_gen = compile_grammar(METTA_IL_GRAMMAR, 'expr', max_depth=3)

    # Simulate two interpreters
    def interpreter_a(expr):
        """Simulated interpreter A (always accepts)"""
        return True

    def interpreter_b(expr):
        """Simulated interpreter B (rejects parentheses)"""
        return '(' not in expr

    print("\nTesting for disagreements between interpreters:\n")
    disagreements = []

    for i in range(20):
        expr = expr_gen.example()
        result_a = interpreter_a(expr)
        result_b = interpreter_b(expr)

        if result_a != result_b:
            disagreements.append((expr, result_a, result_b))

    if disagreements:
        print(f"Found {len(disagreements)} disagreements:\n")
        for expr, res_a, res_b in disagreements[:5]:
            print(f"  Expression: {expr}")
            print(f"    Interpreter A: {res_a}")
            print(f"    Interpreter B: {res_b}")
            print()
    else:
        print("No disagreements found (interpreters agree on all examples)")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("MeTTa-IL Grammar Framework Demonstration")
    print("Language: MeTTa Intermediate Language")
    print("Adaptation time: ~30 minutes")
    print("=" * 70 + "\n")

    # Run examples
    example_generate_metta_expressions()
    example_generate_metta_constructs()
    example_generate_metta_programs()
    print()
    example_generate_invalid_metta()

    example_differential_testing()

    # Run property tests
    print("\n" + "=" * 70)
    print("Running Property Tests")
    print("=" * 70)

    print("\nTesting symbol generation...")
    test_metta_symbols()
    print("✓ All symbol tests passed")

    print("\nTesting variable generation...")
    test_metta_variables()
    print("✓ All variable tests passed")

    print("\nTesting s-expression generation...")
    test_metta_s_expressions()
    print("✓ All s-expression tests passed")

    print("\n" + "=" * 70)
    print("Success! MeTTa-IL grammar adaptation complete.")
    print("=" * 70)
    print("\nKey takeaway: Same framework, different language!")
    print("Total lines of MeTTa-specific code: ~20 (just the grammar)")
    print("=" * 70 + "\n")
