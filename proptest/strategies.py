"""
Hypothesis Strategies for Metamath Database Generation

This module defines Hypothesis strategies for property-based testing
of Metamath verifiers using constructive generation.

The key insight: We use Hypothesis to control the randomness in our
constructive generator, giving us:
- Proper distribution control (not just uniform random)
- Automatic shrinking when tests fail
- Reproducible failures via seeds
- Coverage over a wide range of inputs
"""

from hypothesis import strategies as st
from typing import Optional
from generators.mm_constructive import MMConstructiveGenerator


# ============================================================================
# Configuration Strategies
# ============================================================================

@st.composite
def gen_config(draw):
    """
    Strategy for generating database configuration parameters.

    Returns a dict with generation knobs:
    - lines: Target number of lines (50-200)
    - initial_vars: Number of initial variables (2-5)
    - p_use_mp: Probability of using modus ponens (0.1-0.5)
    - p_new_axiom: Probability of creating new axiom (0.2-0.5)
    - boring_budget: Max times to repeat same conclusion (1-3)
    - max_depth: Target AST nesting depth (1-4)
    """
    return {
        'lines': draw(st.integers(min_value=50, max_value=200)),
        'initial_vars': draw(st.integers(min_value=2, max_value=5)),
        'p_use_mp': draw(st.floats(min_value=0.1, max_value=0.5)),
        'p_new_axiom': draw(st.floats(min_value=0.2, max_value=0.5)),
        'boring_budget': draw(st.integers(min_value=1, max_value=3)),
        'max_depth': draw(st.integers(min_value=1, max_value=4)),
    }


# ============================================================================
# Database Generation Strategy
# ============================================================================

@st.composite
def metamath_database(draw, target_lines: Optional[int] = None):
    """
    Strategy for generating complete Metamath databases.

    This wraps our constructive generator, but uses Hypothesis
    to control the randomness instead of Python's random module.

    Args:
        target_lines: Optional fixed line count. If None, Hypothesis chooses.

    Returns:
        Tuple of (database_str, config_dict)
    """
    # Draw configuration from Hypothesis
    config = draw(gen_config())

    if target_lines is not None:
        config['lines'] = target_lines

    # Create generator with fixed seed (Hypothesis controls the seed)
    # We use Hypothesis's random_module() to seed our generator
    seed = draw(st.integers(min_value=0, max_value=2**31 - 1))

    gen = MMConstructiveGenerator(seed=seed)
    gen.boring_budget = config['boring_budget']

    # Generate database with Hypothesis-controlled parameters
    # For now, we use the existing generate_database method
    # TODO: Refactor to use config parameters for p_use_mp, etc.
    db = gen.generate_database(target_lines=config['lines'])

    return (db, config)


@st.composite
def small_database(draw):
    """Strategy for generating small (50-100 line) databases"""
    lines = draw(st.integers(min_value=50, max_value=100))
    return draw(metamath_database(target_lines=lines))


@st.composite
def large_database(draw):
    """Strategy for generating larger (100-200 line) databases"""
    lines = draw(st.integers(min_value=100, max_value=200))
    return draw(metamath_database(target_lines=lines))


# ============================================================================
# Advanced Strategies (for future use)
# ============================================================================

@st.composite
def axiom_template(draw):
    """
    Strategy for generating axiom templates.

    Returns patterns like:
    - "ph -> ph" (identity)
    - "ph -> (ps -> ph)" (weakening)
    - "(ph -> (ps -> ch)) -> ((ph -> ps) -> (ph -> ch))" (distribution)
    """
    pattern_type = draw(st.sampled_from([
        'identity',
        'weakening',
        'distribution',
        'contrapositive',
    ]))

    if pattern_type == 'identity':
        var = draw(st.sampled_from(['ph', 'ps', 'ch']))
        return f"{var} -> {var}"
    elif pattern_type == 'weakening':
        var1 = draw(st.sampled_from(['ph', 'ps', 'ch']))
        var2 = draw(st.sampled_from(['ph', 'ps', 'ch', 'th']))
        return f"{var1} -> ({var2} -> {var1})"
    # TODO: Add more complex patterns
    else:
        return "ph -> ph"


@st.composite
def nested_formula(draw, max_depth=3):
    """
    Strategy for generating nested formulas with controlled depth.

    This will be used to generate varied term shapes.
    """
    depth = draw(st.integers(min_value=1, max_value=max_depth))

    if depth == 1:
        # Base case: just a variable
        return draw(st.sampled_from(['ph', 'ps', 'ch', 'th']))

    # Recursive case: implication
    left = draw(nested_formula(max_depth=depth-1))
    right = draw(nested_formula(max_depth=depth-1))
    return f"( {left} -> {right} )"


# ============================================================================
# Mutation Strategies (for negative testing)
# ============================================================================

@st.composite
def mutate_database(draw, database: str):
    """
    Strategy for applying single-fault mutations to a valid database.

    This is used for negative testing: verify that verifiers
    correctly reject invalid databases.

    Mutations:
    - duplicate_label: Reuse a label
    - wrong_typecode: Mismatch typecode in substitution
    - unbalanced_block: Add ${ without $}
    - missing_hypothesis: Remove a $f or $e
    - self_reference: Use label in its own proof
    """
    mutation_type = draw(st.sampled_from([
        'duplicate_label',
        'wrong_typecode',
        'unbalanced_block',
        'missing_hypothesis',
        'self_reference',
    ]))

    lines = database.split('\n')

    if mutation_type == 'duplicate_label':
        # Find first theorem label and duplicate it
        for i, line in enumerate(lines):
            if ' $p ' in line:
                # Extract label
                label = line.split()[0]
                # Find another $p and replace its label
                for j in range(i+1, len(lines)):
                    if ' $p ' in lines[j]:
                        parts = lines[j].split()
                        parts[0] = label  # Duplicate!
                        lines[j] = ' '.join(parts)
                        return '\n'.join(lines), mutation_type
                break

    elif mutation_type == 'unbalanced_block':
        # Add ${ without matching $}
        for i, line in enumerate(lines):
            if ' $a ' in line or ' $p ' in line:
                lines.insert(i, '${')
                return '\n'.join(lines), mutation_type

    elif mutation_type == 'missing_hypothesis':
        # Remove a $f statement
        for i, line in enumerate(lines):
            if ' $f ' in line:
                lines[i] = ''  # Delete it
                return '\n'.join(lines), mutation_type

    # If mutation couldn't be applied, return original
    return database, None


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    from hypothesis import given, settings, Phase

    @given(small_database())
    @settings(max_examples=5, phases=[Phase.generate])
    def test_generate_small_db(db_and_config):
        db, config = db_and_config
        print(f"Generated database with {config['lines']} target lines")
        print(f"Actual lines: {len(db.splitlines())}")
        print(f"Config: {config}")
        print()

    print("=== Testing Hypothesis Integration ===\n")
    test_generate_small_db()
