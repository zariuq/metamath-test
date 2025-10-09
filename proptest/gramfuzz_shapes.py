#!/usr/bin/env python3
"""
GramFuzz Integration for Metamath Shape Generation

Layer 1: Use GramFuzz to generate varied syntactic shapes for formulas.
These shapes are then validated and used by our constructive generator.

The key insight: GramFuzz handles SYNTAX variety, our generator handles SEMANTIC validity.
"""

from typing import List, Optional
import random


# We'll implement a simple recursive grammar expander since gramfuzz's API
# is a bit complex. This gives us more control and is clearer.

class MetamathShapeGrammar:
    """
    Grammar for generating Metamath formula shapes.

    Productions:
        EXPR     ::= VAR | '(' EXPR '->' EXPR ')' | '(' '-.' EXPR ')' | '(' EXPR '/\\' EXPR ')'
        VAR      ::= 'ph' | 'ps' | 'ch' | 'th' | 'ta' | 'et'
        CONST    ::= '0' | '1' | '+' | '*'

    Generates shapes like:
        - Simple: ph
        - Nested: ( ph -> ( ps -> ph ) )
        - Deep: ( ph -> ( ps -> ( ch -> ( th -> ps ) ) ) )
        - Balanced: ( ( ph -> ps ) -> ( ps -> ph ) )
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.var_pool = ['ph', 'ps', 'ch', 'th', 'ta', 'et', 'ze', 'si']
        self.depth = 0
        self.max_depth = 4

    def set_max_depth(self, depth: int):
        """Control complexity by limiting nesting"""
        self.max_depth = depth

    def expand_expr(self, depth: int = 0) -> List[str]:
        """
        Expand EXPR production.

        Returns list of tokens representing the formula.
        """
        self.depth = depth

        # Base case: use variable if too deep
        if depth >= self.max_depth:
            return [self.rng.choice(self.var_pool)]

        # Choose production with weights
        choice = self.rng.random()

        if choice < 0.3:
            # VAR (30% - prefer variables at lower depths)
            return [self.rng.choice(self.var_pool)]

        elif choice < 0.8:
            # ( EXPR -> EXPR ) - Implication (50%)
            left = self.expand_expr(depth + 1)
            right = self.expand_expr(depth + 1)
            return ['('] + left + ['->'] + right + [')']

        elif choice < 0.9:
            # ( -. EXPR ) - Negation (10%)
            sub = self.expand_expr(depth + 1)
            return ['(', '-.'] + sub + [')']

        else:
            # ( EXPR /\ EXPR ) - Conjunction (10%)
            left = self.expand_expr(depth + 1)
            right = self.expand_expr(depth + 1)
            return ['('] + left + ['/\\'] + right + [')']

    def expand_balanced_expr(self, depth: int = 0) -> List[str]:
        """
        Generate more balanced trees (left and right similar depth).
        Good for testing balanced vs skewed structures.
        """
        if depth >= self.max_depth:
            return [self.rng.choice(self.var_pool)]

        if self.rng.random() < 0.4:
            return [self.rng.choice(self.var_pool)]

        # Always implication, balanced depths
        left = self.expand_balanced_expr(depth + 1)
        right = self.expand_balanced_expr(depth + 1)
        return ['('] + left + ['->'] + right + [')']

    def expand_skewed_expr(self, depth: int = 0, skew_right: bool = True) -> List[str]:
        """
        Generate skewed trees (one side deeper than other).
        Like: ( ph -> ( ps -> ( ch -> th ) ) ) - right-skewed
        Or: ( ( ( ph -> ps ) -> ch ) -> th ) - left-skewed
        """
        if depth >= self.max_depth:
            return [self.rng.choice(self.var_pool)]

        if self.rng.random() < 0.3:
            return [self.rng.choice(self.var_pool)]

        if skew_right:
            # Right side deeper
            left = [self.rng.choice(self.var_pool)]
            right = self.expand_skewed_expr(depth + 1, skew_right=True)
        else:
            # Left side deeper
            left = self.expand_skewed_expr(depth + 1, skew_right=False)
            right = [self.rng.choice(self.var_pool)]

        return ['('] + left + ['->'] + right + [')']

    def expand_chain(self, length: int = 3) -> List[str]:
        """
        Generate implication chains: ( ph -> ( ps -> ( ch -> th ) ) )
        Good for testing associativity and chaining.
        """
        if length <= 1:
            return [self.var_pool[0]]

        vars_used = self.var_pool[:min(length, len(self.var_pool))]

        # Build from right to left
        result = [vars_used[-1]]
        for var in reversed(vars_used[:-1]):
            result = ['(', var, '->'] + result + [')']

        return result

    def generate_varied_shapes(self, count: int = 10) -> List[List[str]]:
        """
        Generate a diverse set of formula shapes.

        Returns list of token lists, each representing a different shape.
        """
        shapes = []

        # Mix of strategies for diversity
        for i in range(count):
            strategy = i % 5

            if strategy == 0:
                # Regular random
                shapes.append(self.expand_expr(0))
            elif strategy == 1:
                # Balanced
                shapes.append(self.expand_balanced_expr(0))
            elif strategy == 2:
                # Right-skewed
                shapes.append(self.expand_skewed_expr(0, skew_right=True))
            elif strategy == 3:
                # Left-skewed
                shapes.append(self.expand_skewed_expr(0, skew_right=False))
            else:
                # Chain
                chain_len = self.rng.randint(2, 5)
                shapes.append(self.expand_chain(chain_len))

        return shapes


# =============================================================================
# Metrics for Shape Complexity
# =============================================================================

def compute_depth(tokens: List[str]) -> int:
    """Compute max parenthesis depth"""
    depth = max_depth = 0
    for tok in tokens:
        if tok == '(':
            depth += 1
            max_depth = max(max_depth, depth)
        elif tok == ')':
            depth -= 1
    return max_depth


def compute_size(tokens: List[str]) -> int:
    """Compute total token count"""
    return len(tokens)


def is_balanced(tokens: List[str]) -> bool:
    """
    Check if tree is roughly balanced.
    A tree is balanced if left and right subtrees of root have similar depth.
    """
    # Find root operator (first -> at depth 1)
    depth = 0
    root_idx = None

    for i, tok in enumerate(tokens):
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
        elif tok == '->' and depth == 1:
            root_idx = i
            break

    if root_idx is None:
        return True  # No implication, trivially balanced

    # Get left and right parts
    left_tokens = tokens[1:root_idx]
    right_tokens = tokens[root_idx+1:-1]

    left_depth = compute_depth(left_tokens)
    right_depth = compute_depth(right_tokens)

    # Balanced if depths differ by at most 1
    return abs(left_depth - right_depth) <= 1


def shape_fingerprint(tokens: List[str]) -> str:
    """
    Create a canonical fingerprint for a shape (ignoring variable names).

    Example: ( ph -> ( ps -> ph ) ) and ( x -> ( y -> x ) ) have same fingerprint.
    """
    # Replace all variables with 'V'
    canonical = []
    for tok in tokens:
        if tok in ['(', ')', '->', '-.', '/\\', '\\/']:
            canonical.append(tok)
        else:
            canonical.append('V')
    return ' '.join(canonical)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    grammar = MetamathShapeGrammar(seed=42)

    print("=" * 70)
    print("GRAMFUZZ SHAPE GENERATION - Layer 1")
    print("=" * 70)
    print()

    # Test different strategies
    print("## Random Shapes (varied depth):")
    grammar.set_max_depth(3)
    for i in range(5):
        shape = grammar.expand_expr()
        print(f"  {i+1}. {' '.join(shape)}")
        print(f"     Depth: {compute_depth(shape)}, Size: {compute_size(shape)}, Balanced: {is_balanced(shape)}")
    print()

    print("## Balanced Shapes:")
    for i in range(3):
        shape = grammar.expand_balanced_expr()
        print(f"  {i+1}. {' '.join(shape)}")
        print(f"     Depth: {compute_depth(shape)}, Balanced: {is_balanced(shape)}")
    print()

    print("## Right-Skewed Chains:")
    for i in range(3):
        shape = grammar.expand_skewed_expr(skew_right=True)
        print(f"  {i+1}. {' '.join(shape)}")
        print(f"     Depth: {compute_depth(shape)}, Balanced: {is_balanced(shape)}")
    print()

    print("## Implication Chains:")
    for length in [2, 3, 4]:
        shape = grammar.expand_chain(length)
        print(f"  Length {length}: {' '.join(shape)}")
    print()

    print("## Diverse Set (mixed strategies):")
    shapes = grammar.generate_varied_shapes(count=10)
    fingerprints = set()
    for i, shape in enumerate(shapes):
        fp = shape_fingerprint(shape)
        fingerprints.add(fp)
        print(f"  {i+1}. {' '.join(shape)}")
        print(f"     Fingerprint: {fp}")

    print(f"\n  Unique shapes: {len(fingerprints)}/10")
    print()

    print("=" * 70)
    print("Layer 1 complete! These shapes can now feed into Layer 2 (MMEnv)")
    print("=" * 70)
