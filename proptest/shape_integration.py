#!/usr/bin/env python3
"""
Layer 2: Integration Bridge - GramFuzz Shapes → Semantic Validity

Takes syntactically valid shapes from GramFuzz and ensures they're
semantically valid by coordinating with MMEnv.

Architecture:
    Layer 1 (GramFuzz) → Layer 2 (This module) → Layer 3 (Constructive Generator)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from typing import List, Set, Dict, Optional
from generators.mm_env import MMEnv
from gramfuzz_shapes import MetamathShapeGrammar, compute_depth, shape_fingerprint


class ShapeValidator:
    """
    Validates and prepares GramFuzz-generated shapes for use in Metamath.

    Responsibilities:
    1. Extract variables from shape
    2. Ensure all variables are declared in MMEnv
    3. Ensure all variables have $f hypotheses
    4. Convert shape tokens to valid Metamath symbols
    """

    def __init__(self, env: MMEnv):
        self.env = env

    def extract_variables(self, shape_tokens: List[str]) -> Set[str]:
        """Extract all variable symbols from a shape"""
        # In our grammar, variables are: ph, ps, ch, th, ta, et, ze, si
        var_symbols = {'ph', 'ps', 'ch', 'th', 'ta', 'et', 'ze', 'si'}
        return {tok for tok in shape_tokens if tok in var_symbols}

    def ensure_variables_declared(self, variables: Set[str]):
        """
        Ensure all variables in the shape are declared and typed.

        For each variable:
        1. Declare with $v if not already declared
        2. Add $f hypothesis if not already present
        """
        for var in variables:
            if var not in self.env.active_vars:
                self.env.declare_var(var)

            # Check if this variable has a $f hypothesis
            if var not in self.env.var_types:
                label = self.env.fresh_label("wf")
                self.env.declare_f_hyp(label, "wff", var)

    def shape_to_metamath_symbols(self, shape_tokens: List[str]) -> List[str]:
        """
        Convert shape tokens to proper Metamath symbols.

        Handles:
        - Logical operators: ->, -., /\, \/
        - Parentheses: (, )
        - Variables: ph, ps, ch, etc.
        """
        # Shape tokens are already in Metamath format
        return shape_tokens

    def validate_and_prepare(self, shape_tokens: List[str]) -> List[str]:
        """
        Main entry point: validate a shape and prepare environment.

        Returns the Metamath symbol list ready to use in an axiom/theorem.
        """
        # Extract variables
        variables = self.extract_variables(shape_tokens)

        # Ensure they're all declared and typed
        self.ensure_variables_declared(variables)

        # Convert to Metamath symbols (in this case, identity)
        metamath_symbols = self.shape_to_metamath_symbols(shape_tokens)

        return metamath_symbols


class EnhancedConstructiveGenerator:
    """
    Enhanced generator that uses GramFuzz shapes.

    Combines:
    - GramFuzz for syntactic variety (Layer 1)
    - ShapeValidator for semantic preparation (Layer 2)
    - Constructive proof building (Layer 3)
    """

    def __init__(self, seed: Optional[int] = None):
        from generators.mm_constructive import MMConstructiveGenerator

        self.base_generator = MMConstructiveGenerator(seed=seed)
        self.shape_grammar = MetamathShapeGrammar(seed=seed)
        self.validator = ShapeValidator(self.base_generator.env)
        self.shape_fingerprints = set()

    def generate_complex_axiom(self, max_depth: int = 3) -> str:
        """
        Generate an axiom with a complex shape from GramFuzz.

        Process:
        1. Generate shape with GramFuzz (Layer 1)
        2. Validate and prepare with ShapeValidator (Layer 2)
        3. Create axiom with constructive generator (Layer 3)
        """
        # Layer 1: Generate shape
        self.shape_grammar.set_max_depth(max_depth)
        shape_tokens = self.shape_grammar.expand_expr()

        # Check novelty
        fp = shape_fingerprint(shape_tokens)
        if fp in self.shape_fingerprints and len(self.shape_fingerprints) > 2:
            # Try once more for novelty
            shape_tokens = self.shape_grammar.expand_expr()
            fp = shape_fingerprint(shape_tokens)

        self.shape_fingerprints.add(fp)

        # Layer 2: Validate and prepare
        metamath_symbols = self.validator.validate_and_prepare(shape_tokens)

        # Layer 3: Create axiom
        label = self.base_generator.env.fresh_label("ax")
        self.base_generator.emit(f"{label} $a |- {' '.join(metamath_symbols)} $.")
        self.base_generator.env.declare_assertion(
            label, is_axiom=True, typecode="|-", symbols=metamath_symbols
        )

        return label

    def generate_database_with_complex_shapes(
        self,
        target_lines: int = 100,
        complex_axiom_ratio: float = 0.3
    ) -> str:
        """
        Generate a database using complex shapes from GramFuzz.

        Args:
            target_lines: Target number of lines
            complex_axiom_ratio: Fraction of axioms that should use complex shapes
        """
        # Start with header and basic setup
        self.base_generator.generate_header()

        # Declare additional logical operators that GramFuzz might use
        env = self.base_generator.env
        for op in ['-.', '/\\', '\\/']:
            if op not in env.active_consts:
                self.base_generator.emit(f"$c {op} $.")
                env.declare_const(op)
        self.base_generator.emit("")

        self.base_generator.generate_variables(count=2)  # Start with minimal
        self.base_generator.generate_f_hypotheses()

        self.base_generator.emit_comment("Axioms (mix of simple and complex shapes)")
        axioms = []

        # Add some basic axioms
        axioms.append(self.base_generator.generate_axiom_simple("ax-id"))

        # Add complex axioms from GramFuzz
        num_complex = int(5 * complex_axiom_ratio)
        for depth in range(1, min(4, num_complex + 1)):
            axiom = self.generate_complex_axiom(max_depth=depth)
            axioms.append(axiom)

        self.base_generator.emit("")
        self.base_generator.emit_comment("Theorems (generated constructively)")

        # Generate theorems using both simple and complex axioms
        attempts = 0
        max_attempts = target_lines * 3

        while len(self.base_generator.output) < target_lines and attempts < max_attempts:
            attempts += 1
            choice = self.base_generator.rng.random()

            if choice < 0.7 and axioms:
                # Simple proof: apply an axiom
                axiom = self.base_generator.rng.choice(axioms)
                result = self.base_generator.generate_proof_by_axiom(axiom)

            else:
                # Add another complex axiom occasionally
                if len(self.base_generator.output) < target_lines - 10:
                    depth = self.base_generator.rng.randint(1, 3)
                    new_axiom = self.generate_complex_axiom(max_depth=depth)
                    axioms.append(new_axiom)

        return "".join(self.base_generator.output)


# =============================================================================
# Example Usage & Testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("LAYER 2: SHAPE INTEGRATION")
    print("=" * 70)
    print()

    # Test the validator
    from generators.mm_env import MMEnv

    env = MMEnv()
    env.declare_const("wff")
    env.declare_const("|-")
    env.declare_const("->")
    env.declare_const("(")
    env.declare_const(")")

    validator = ShapeValidator(env)

    print("## Testing Shape Validation:")
    print()

    # Test shape 1: Simple
    shape1 = ['(', 'ph', '->', 'ps', ')']
    print(f"Shape 1: {' '.join(shape1)}")
    symbols1 = validator.validate_and_prepare(shape1)
    print(f"  Variables extracted: {validator.extract_variables(shape1)}")
    print(f"  Metamath symbols: {' '.join(symbols1)}")
    print(f"  Variables now in env: {env.active_vars}")
    print()

    # Test shape 2: Complex
    shape2 = ['(', 'ph', '->', '(', 'ch', '->', '(', 'th', '->', 'ph', ')', ')', ')']
    print(f"Shape 2: {' '.join(shape2)}")
    symbols2 = validator.validate_and_prepare(shape2)
    print(f"  Variables extracted: {validator.extract_variables(shape2)}")
    print(f"  Metamath symbols: {' '.join(symbols2)}")
    print(f"  Variables now in env: {env.active_vars}")
    print()

    print("=" * 70)
    print("## Testing Enhanced Generator:")
    print("=" * 70)
    print()

    gen = EnhancedConstructiveGenerator(seed=42)
    db = gen.generate_database_with_complex_shapes(target_lines=80, complex_axiom_ratio=0.4)

    print(db)
    print()
    print(f"Generated {len(db.splitlines())} lines")
    print(f"Unique shape fingerprints: {len(gen.shape_fingerprints)}")
    print()

    # Analyze shapes
    print("Shape fingerprints used:")
    for i, fp in enumerate(sorted(gen.shape_fingerprints), 1):
        print(f"  {i}. {fp}")
