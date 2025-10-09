"""
Hypothesis Strategy Compiler

Compiles EBNF grammar AST into Hypothesis strategies for generating
valid examples. Supports mutation hooks for generating invalid examples.

Design Goal: Language-agnostic compiler that works with any EBNF grammar.
"""

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from typing import Dict, Optional, Callable, Any, Set
import string

from .ebnf_parser import (
    Grammar, Rule, GrammarExpr,
    CharRange, CharSet, Literal, NonTerminal,
    Sequence, Choice, Optional as OptionalExpr,
    ZeroOrMore, OneOrMore
)


# ============================================================================
# Mutation Hooks
# ============================================================================

class MutationHook:
    """
    Hook for injecting mutations into generated examples.

    Allows transforming valid examples into invalid ones for testing
    verifier error handling.
    """

    def __init__(self, name: str, mutate_fn: Callable[[str], str]):
        self.name = name
        self.mutate_fn = mutate_fn

    def apply(self, value: str) -> str:
        return self.mutate_fn(value)


# ============================================================================
# Strategy Compiler
# ============================================================================

class StrategyCompiler:
    """
    Compile EBNF grammar AST into Hypothesis strategies.

    Features:
    - Generates valid examples from grammar
    - Supports mutation hooks for invalid examples
    - Handles recursive grammars with max_depth limit
    - Customizable character sets and literals
    """

    def __init__(self, grammar: Grammar, max_depth: int = 5):
        self.grammar = grammar
        self.max_depth = max_depth
        self.strategies: Dict[str, SearchStrategy] = {}
        self.current_depth = 0
        self.mutation_hooks: Dict[str, MutationHook] = {}

        # Character generation helpers
        self.whitespace_strategy = st.sampled_from([' ', '\t', '\n'])
        self.comment_strategy = st.just('')  # Override if comments needed

    def add_mutation_hook(self, rule_name: str, hook: MutationHook):
        """Register a mutation hook for a specific rule"""
        self.mutation_hooks[rule_name] = hook

    def compile(self, start_rule: str) -> SearchStrategy:
        """Compile grammar starting from the given rule"""
        rule = self.grammar.get_rule(start_rule)
        if not rule:
            raise ValueError(f"Rule '{start_rule}' not found in grammar")

        return self._compile_expr(rule.expr, start_rule)

    def _compile_expr(self, expr: GrammarExpr, context: str = "") -> SearchStrategy:
        """Compile a grammar expression into a Hypothesis strategy"""

        # CharRange: [a-z] or [#x20-#x7E]
        if isinstance(expr, CharRange):
            return self._compile_charrange(expr)

        # CharSet: [abc] or [#x09#x0A]
        elif isinstance(expr, CharSet):
            return self._compile_charset(expr)

        # Literal: 'foo'
        elif isinstance(expr, Literal):
            return st.just(expr.value)

        # NonTerminal: reference to another rule
        elif isinstance(expr, NonTerminal):
            return self._compile_nonterminal(expr)

        # Sequence: A B C
        elif isinstance(expr, Sequence):
            return self._compile_sequence(expr)

        # Choice: A | B | C
        elif isinstance(expr, Choice):
            return self._compile_choice(expr)

        # Optional: A?
        elif isinstance(expr, OptionalExpr):
            return self._compile_optional(expr)

        # ZeroOrMore: A*
        elif isinstance(expr, ZeroOrMore):
            return self._compile_zero_or_more(expr)

        # OneOrMore: A+
        elif isinstance(expr, OneOrMore):
            return self._compile_one_or_more(expr)

        else:
            raise ValueError(f"Unknown expression type: {type(expr)}")

    def _compile_charrange(self, expr: CharRange) -> SearchStrategy:
        """Compile character range into strategy"""
        if isinstance(expr.start, int):
            # Hex range: #x20-#x7E
            chars = [chr(i) for i in range(expr.start, expr.end + 1)]
        else:
            # ASCII range: a-z
            chars = [chr(i) for i in range(ord(expr.start), ord(expr.end) + 1)]

        # Apply exclusion
        if expr.exclude:
            chars = [c for c in chars if c != expr.exclude]

        return st.sampled_from(chars)

    def _compile_charset(self, expr: CharSet) -> SearchStrategy:
        """Compile character set into strategy"""
        chars = []
        for c in expr.chars:
            if isinstance(c, int):
                chars.append(chr(c))
            else:
                chars.append(c)

        return st.sampled_from(chars)

    def _compile_nonterminal(self, expr: NonTerminal) -> SearchStrategy:
        """Compile non-terminal reference"""
        # Check recursion depth
        if self.current_depth >= self.max_depth:
            # Return minimal example to avoid infinite recursion
            return st.just("")

        # Find the rule
        rule = self.grammar.get_rule(expr.name)
        if not rule:
            raise ValueError(f"Rule '{expr.name}' not found")

        # Check for mutation hook
        if expr.name in self.mutation_hooks:
            hook = self.mutation_hooks[expr.name]
            # Generate valid example, then mutate it
            self.current_depth += 1
            base_strategy = self._compile_expr(rule.expr, expr.name)
            self.current_depth -= 1
            return base_strategy.map(hook.apply)

        # Normal compilation
        self.current_depth += 1
        strategy = self._compile_expr(rule.expr, expr.name)
        self.current_depth -= 1

        return strategy

    def _compile_sequence(self, expr: Sequence) -> SearchStrategy:
        """Compile sequence: A B C"""
        # Build list of strategies
        element_strategies = [self._compile_expr(e) for e in expr.elements]

        # Combine with st.tuples and concatenate
        @st.composite
        def sequence_strategy(draw):
            parts = []
            for elem_st in element_strategies:
                parts.append(draw(elem_st))
            return ''.join(str(p) for p in parts)

        return sequence_strategy()

    def _compile_choice(self, expr: Choice) -> SearchStrategy:
        """Compile choice: A | B | C"""
        alt_strategies = [self._compile_expr(alt) for alt in expr.alternatives]
        return st.one_of(*alt_strategies)

    def _compile_optional(self, expr: OptionalExpr) -> SearchStrategy:
        """Compile optional: A?"""
        elem_strategy = self._compile_expr(expr.element)
        return st.one_of(st.just(""), elem_strategy)

    def _compile_zero_or_more(self, expr: ZeroOrMore) -> SearchStrategy:
        """Compile zero or more: A*"""
        elem_strategy = self._compile_expr(expr.element)

        # Limit max size to avoid huge examples
        return st.lists(elem_strategy, max_size=10).map(''.join)

    def _compile_one_or_more(self, expr: OneOrMore) -> SearchStrategy:
        """Compile one or more: A+"""
        elem_strategy = self._compile_expr(expr.element)

        # At least 1, up to 10
        return st.lists(elem_strategy, min_size=1, max_size=10).map(''.join)


# ============================================================================
# Convenience Functions
# ============================================================================

def compile_grammar(grammar_text: str, start_rule: str,
                   max_depth: int = 5) -> SearchStrategy:
    """
    Compile EBNF grammar text into Hypothesis strategy.

    Args:
        grammar_text: EBNF grammar as string
        start_rule: Name of rule to start generation from
        max_depth: Maximum recursion depth for nested rules

    Returns:
        Hypothesis strategy that generates examples of the language
    """
    from .ebnf_parser import EBNFParser

    parser = EBNFParser()
    grammar = parser.parse(grammar_text)
    compiler = StrategyCompiler(grammar, max_depth=max_depth)

    return compiler.compile(start_rule)


def compile_grammar_with_mutations(
    grammar_text: str,
    start_rule: str,
    mutations: Dict[str, Callable[[str], str]],
    max_depth: int = 5
) -> SearchStrategy:
    """
    Compile grammar with mutation hooks for generating invalid examples.

    Args:
        grammar_text: EBNF grammar as string
        start_rule: Name of rule to start generation from
        mutations: Dict mapping rule names to mutation functions
        max_depth: Maximum recursion depth

    Returns:
        Hypothesis strategy that generates mutated (invalid) examples
    """
    from .ebnf_parser import EBNFParser

    parser = EBNFParser()
    grammar = parser.parse(grammar_text)
    compiler = StrategyCompiler(grammar, max_depth=max_depth)

    # Add mutation hooks
    for rule_name, mutate_fn in mutations.items():
        hook = MutationHook(name=rule_name, mutate_fn=mutate_fn)
        compiler.add_mutation_hook(rule_name, hook)

    return compiler.compile(start_rule)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    from hypothesis import given

    # Simple arithmetic grammar
    grammar = """
    expr ::= term ( '+' term )*
    term ::= number
    number ::= [0-9]+
    """

    # Compile to strategy
    expr_strategy = compile_grammar(grammar, 'expr', max_depth=3)

    # Test generation
    @given(expr_strategy)
    def test_expr_generation(expr):
        print(f"Generated: {expr}")
        assert isinstance(expr, str)
        assert len(expr) > 0

    # Generate a few examples
    print("Valid expressions:")
    for _ in range(5):
        example = expr_strategy.example()
        print(f"  {example}")

    print("\nMutated expressions (invalid):")

    # Add mutation: insert operator without operand
    mutations = {
        'term': lambda t: t + '+'  # Invalid: ends with operator
    }

    mutated_strategy = compile_grammar_with_mutations(
        grammar, 'expr', mutations, max_depth=3
    )

    for _ in range(5):
        example = mutated_strategy.example()
        print(f"  {example}")
