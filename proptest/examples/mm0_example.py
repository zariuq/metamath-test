"""
MM0 (Metamath Zero) Grammar Example

Demonstrates how easy it is to adapt the EBNF framework to a new language.

MM0 is a proof assistant language with a simpler syntax than Metamath.
This example shows generating valid MM0 programs from an EBNF grammar.

Estimated adaptation time: 30 minutes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework import compile_grammar, compile_grammar_with_mutations
from hypothesis import given, settings, HealthCheck

# ============================================================================
# MM0 EBNF Grammar
# ============================================================================

MM0_GRAMMAR = """
# MM0 Grammar (simplified)
# Based on: https://github.com/digama0/mm0/blob/master/mm0.md

program ::= decl*

decl ::=
    | sort_decl
    | term_decl
    | axiom_decl
    | theorem_decl

# Sort declaration: sort foo;
sort_decl ::= 'sort' ident ';'

# Term declaration: term add (x y: nat): nat;
term_decl ::= 'term' ident '(' binders ')' ':' ident ';'

binders ::= binder*
binder ::= ident ':' ident

# Axiom: axiom ax_add (x y: nat): $ add x y $;
axiom_decl ::= 'axiom' ident '(' binders ')' ':' formula ';'

# Theorem (with proof): theorem th1: $ P -> P $ = 'axiom_id;
theorem_decl ::= 'theorem' ident ':' formula '=' proof ';'

# Formula (simplified): $ P -> Q $
formula ::= '$' term_expr* '$'

term_expr ::= ident

# Proof (simplified): axiom reference
proof ::= ident

# Identifier: alphanumeric + underscore
ident ::= [a-zA-Z_] [a-zA-Z0-9_]*
"""

# ============================================================================
# Example 1: Generate Valid MM0 Programs
# ============================================================================

def example_generate_mm0_programs():
    """Generate random valid MM0 programs"""
    print("=" * 70)
    print("Example 1: Generating Valid MM0 Programs")
    print("=" * 70)

    # Compile grammar
    prog_gen = compile_grammar(MM0_GRAMMAR, 'program', max_depth=3)

    # Generate examples
    print("\nGenerated MM0 programs:\n")
    for i in range(5):
        program = prog_gen.example()
        print(f"Program {i+1}:")
        print(program)
        print()


# ============================================================================
# Example 2: Generate Specific MM0 Constructs
# ============================================================================

def example_generate_mm0_constructs():
    """Generate specific MM0 declarations"""
    print("=" * 70)
    print("Example 2: Generating Specific MM0 Constructs")
    print("=" * 70)

    # Sort declarations
    print("\nSort declarations:")
    sort_gen = compile_grammar(MM0_GRAMMAR, 'sort_decl', max_depth=2)
    for _ in range(3):
        print(f"  {sort_gen.example()}")

    # Term declarations
    print("\nTerm declarations:")
    term_gen = compile_grammar(MM0_GRAMMAR, 'term_decl', max_depth=2)
    for _ in range(3):
        print(f"  {term_gen.example()}")

    # Axioms
    print("\nAxiom declarations:")
    axiom_gen = compile_grammar(MM0_GRAMMAR, 'axiom_decl', max_depth=2)
    for _ in range(3):
        print(f"  {axiom_gen.example()}")


# ============================================================================
# Example 3: Generate Invalid MM0 (for testing error handling)
# ============================================================================

def example_generate_invalid_mm0():
    """Generate invalid MM0 programs using mutations"""
    print("=" * 70)
    print("Example 3: Generating Invalid MM0 (Mutations)")
    print("=" * 70)

    print("\nMutation 1: Missing semicolon")
    mutations_no_semicolon = {
        'sort_decl': lambda s: s.replace(';', '')  # Remove semicolon
    }
    invalid_gen = compile_grammar_with_mutations(
        MM0_GRAMMAR, 'sort_decl', mutations_no_semicolon, max_depth=2
    )
    for _ in range(3):
        print(f"  {invalid_gen.example()}")

    print("\nMutation 2: Invalid identifier (starts with digit)")
    mutations_bad_ident = {
        'ident': lambda i: '9' + i  # Start with digit (invalid)
    }
    invalid_gen2 = compile_grammar_with_mutations(
        MM0_GRAMMAR, 'sort_decl', mutations_bad_ident, max_depth=2
    )
    for _ in range(3):
        print(f"  {invalid_gen2.example()}")

    print("\nMutation 3: Mismatched delimiters")
    mutations_delimiter = {
        'formula': lambda f: f.replace('$', '#')  # Wrong delimiter
    }
    invalid_gen3 = compile_grammar_with_mutations(
        MM0_GRAMMAR, 'axiom_decl', mutations_delimiter, max_depth=2
    )
    for _ in range(3):
        print(f"  {invalid_gen3.example()}")


# ============================================================================
# Example 4: Property-Based Testing
# ============================================================================

@given(compile_grammar(MM0_GRAMMAR, 'ident', max_depth=2))
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
def test_mm0_identifiers(ident):
    """Test that generated identifiers are valid"""
    # First char must be letter or underscore
    assert ident[0].isalpha() or ident[0] == '_'
    # Rest can include digits
    for c in ident[1:]:
        assert c.isalnum() or c == '_'


@given(compile_grammar(MM0_GRAMMAR, 'sort_decl', max_depth=2))
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=10)
def test_mm0_sort_declarations(decl):
    """Test that generated sort declarations are valid"""
    assert decl.startswith('sort')
    assert decl.endswith(';')


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("MM0 Grammar Framework Demonstration")
    print("Language: Metamath Zero (MM0)")
    print("Adaptation time: ~30 minutes")
    print("=" * 70 + "\n")

    # Run examples
    example_generate_mm0_programs()
    print()

    example_generate_mm0_constructs()
    print()

    example_generate_invalid_mm0()
    print()

    # Run property tests
    print("=" * 70)
    print("Running Property Tests")
    print("=" * 70)
    print("\nTesting identifier generation...")
    test_mm0_identifiers()
    print("✓ All identifier tests passed")

    print("\nTesting sort declaration generation...")
    test_mm0_sort_declarations()
    print("✓ All sort declaration tests passed")

    print("\n" + "=" * 70)
    print("Success! MM0 grammar adaptation complete.")
    print("=" * 70)
