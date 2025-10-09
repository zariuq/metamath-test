"""
Grammar-Based Property Testing Framework

A language-agnostic framework for generating valid and invalid examples
from EBNF grammars using Hypothesis.

Design Goals:
1. Easy to adapt to new languages (MM0, MeTTa-IL, etc.)
2. Support both valid generation and targeted mutations
3. Integrate seamlessly with Hypothesis property testing

Example usage:

    from framework import compile_grammar

    grammar = '''
    statement ::= label '$a' symbols+ '$.'
    label ::= [A-Za-z0-9]+
    symbols ::= [a-z]+
    '''

    # Generate valid examples
    stmt_gen = compile_grammar(grammar, 'statement')
    example = stmt_gen.example()  # e.g., "ax1 $a wff ph $."

    # Generate invalid examples with mutations
    mutations = {'label': lambda l: l + '$'}  # Add invalid char
    invalid_gen = compile_grammar_with_mutations(
        grammar, 'statement', mutations
    )
    bad_example = invalid_gen.example()  # e.g., "ax1$ $a wff ph $."
"""

from .ebnf_parser import (
    EBNFParser,
    Grammar, Rule, GrammarExpr,
    CharRange, CharSet, Literal, NonTerminal,
    Sequence, Choice, Optional, ZeroOrMore, OneOrMore
)

from .strategy_compiler import (
    StrategyCompiler,
    MutationHook,
    compile_grammar,
    compile_grammar_with_mutations
)

__all__ = [
    # Parser
    'EBNFParser',
    'Grammar', 'Rule', 'GrammarExpr',
    'CharRange', 'CharSet', 'Literal', 'NonTerminal',
    'Sequence', 'Choice', 'Optional', 'ZeroOrMore', 'OneOrMore',

    # Compiler
    'StrategyCompiler',
    'MutationHook',
    'compile_grammar',
    'compile_grammar_with_mutations',
]
