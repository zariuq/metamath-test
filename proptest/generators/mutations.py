"""
Mutation generators for testing verification gaps.

These generators take valid Metamath databases and apply specific
mutations that should cause verification to fail.

Based on adversarial tests and the 19+ known verification gaps.
"""

from hypothesis import strategies as st
import re
from typing import Tuple


class MutationType:
    """Enumeration of mutation types mapped to verification gaps"""

    # Gap #1: ASCII + whitespace checking
    NON_ASCII = "non_ascii"

    # Gap #2: Keyword separation by whitespace
    NO_WHITESPACE_KEYWORDS = "no_whitespace_keywords"

    # Gap #3: Comment nesting
    NESTED_COMMENTS = "nested_comments"

    # Gap #4: Balanced ${$} blocks
    UNBALANCED_BLOCKS = "unbalanced_blocks"

    # Gap #5: $ character in math symbols
    DOLLAR_IN_SYMBOL = "dollar_in_symbol"

    # Gap #6: Dangling $ at EOF
    DANGLING_DOLLAR = "dangling_dollar"

    # Gap #9: Redeclaration of active constants
    REDECLARE_CONSTANT = "redeclare_constant"

    # Gap #10: Redeclaration of active variables
    REDECLARE_VARIABLE = "redeclare_variable"

    # Gap #11: Variable scope deactivation
    USE_DEACTIVATED_VAR = "use_deactivated_var"

    # Gap #12: $d distinct active variables
    D_CONSTANT = "d_constant"  # Adversarial: $d with constant
    D_DUPLICATE = "d_duplicate"  # Adversarial: $d x x (duplicate vars)

    # Gap #13: Label uniqueness
    DUPLICATE_LABEL = "duplicate_label"

    # Gap #14: Single $f per variable per scope
    DUPLICATE_F = "duplicate_f"

    # Gap #19: Unknown ? steps
    UNKNOWN_STEP = "unknown_step"

    # Additional: Variable/constant redeclaration after scope
    VAR_TO_CONSTANT = "var_to_constant"  # Adversarial: $v x in block, then $c x


@st.composite
def mutate_d_constant(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #12a: $d statement with constant instead of variable.

    metamath.exe: "Constant symbols are not allowed in a '$d' statement."
    mmverify.py: INCORRECTLY ACCEPTS (BUG!)

    Example: $d -> ph $. where '->' is a constant
    """
    # Find a $c statement to extract a constant
    c_match = re.search(r'\$c\s+(.*?)\s+\$\.', mm_content, re.DOTALL)
    if not c_match:
        return mm_content, "no_c_statement"

    constants = c_match.group(1).split()
    if not constants:
        return mm_content, "no_constants"

    # Find a $v statement to extract a variable
    v_match = re.search(r'\$v\s+(.*?)\s+\$\.', mm_content, re.DOTALL)
    if not v_match:
        return mm_content, "no_v_statement"

    variables = v_match.group(1).split()
    if not variables:
        return mm_content, "no_variables"

    # Pick a constant and variable
    const = draw(st.sampled_from(constants))
    var = draw(st.sampled_from(variables))

    # Insert bad $d statement after the $v statement
    mutation = f"\n$d {const} {var} $.  $( INVALID: '{const}' is a constant $)\n"
    mutated = mm_content.replace(
        v_match.group(0),
        v_match.group(0) + mutation
    )

    return mutated, f"d_constant_{const}_{var}"


@st.composite
def mutate_d_duplicate(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #12b: $d statement with duplicate variable.

    metamath.exe: "All variables in a '$d' statement must be unique."
    mmverify.py: INCORRECTLY ACCEPTS (BUG!)

    Example: $d x x $.
    """
    # Find a $v statement
    v_match = re.search(r'\$v\s+(.*?)\s+\$\.', mm_content, re.DOTALL)
    if not v_match:
        return mm_content, "no_v_statement"

    variables = v_match.group(1).split()
    if not variables:
        return mm_content, "no_variables"

    # Pick a variable
    var = draw(st.sampled_from(variables))

    # Insert bad $d statement
    mutation = f"\n$d {var} {var} $.  $( INVALID: duplicate variable in $d $)\n"
    mutated = mm_content.replace(
        v_match.group(0),
        v_match.group(0) + mutation
    )

    return mutated, f"d_duplicate_{var}"


@st.composite
def mutate_var_to_constant(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #9/#10: Variable redeclared as constant (or vice versa).

    metamath.exe: "A symbol may not be both a constant and a variable."
    mmverify.py: INCORRECTLY ACCEPTS (BUG!)

    Example:
        ${ $v x $. $}
        $c x $.
    """
    # Find a block with $v
    block_match = re.search(r'\$\{\s*\$v\s+(.*?)\s+\$\.\s*\$\}', mm_content, re.DOTALL)
    if not block_match:
        return mm_content, "no_scoped_v"

    variables = block_match.group(1).split()
    if not variables:
        return mm_content, "no_variables_in_block"

    # Pick a variable
    var = draw(st.sampled_from(variables))

    # Add $c declaration after the block
    mutation = f"\n$c {var} $.  $( INVALID: {var} was variable, now constant $)\n"
    mutated = mm_content.replace(
        block_match.group(0),
        block_match.group(0) + mutation
    )

    return mutated, f"var_to_constant_{var}"


@st.composite
def mutate_unknown_step(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #19: Unknown ? step in proof (allowed by spec 4.4.6).

    metamath.exe: ACCEPTS with warning "statement(s) were not proved"
    mmverify.py: INCORRECTLY CRASHES (BUG!)

    Example: th $p |- ph $= ? $.
    """
    # Find a $p statement
    p_match = re.search(r'(\w+)\s+\$p\s+(.*?)\s+\$=\s+(.*?)\s+\$\.', mm_content, re.DOTALL)
    if not p_match:
        return mm_content, "no_p_statement"

    label = p_match.group(1)
    assertion = p_match.group(2)
    proof = p_match.group(3)

    # Replace proof with ?
    mutation = f"{label} $p {assertion} $= ? $.  $( INCOMPLETE proof, spec 4.4.6 $)"
    mutated = mm_content.replace(p_match.group(0), mutation)

    return mutated, f"unknown_step_{label}"


@st.composite
def mutate_dollar_in_symbol(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #5: $ character in math symbol.

    metamath.exe: Should reject ($ not allowed in MATH-SYMBOL)
    Status: UNKNOWN - needs testing

    Example: $c t$erm $.
    """
    # Find a $c statement
    c_match = re.search(r'\$c\s+(.*?)\s+\$\.', mm_content, re.DOTALL)
    if not c_match:
        return mm_content, "no_c_statement"

    constants = c_match.group(1).split()
    if not constants:
        return mm_content, "no_constants"

    # Pick a constant and inject $
    const = draw(st.sampled_from(constants))
    if len(const) < 2:
        return mm_content, "constant_too_short"

    # Insert $ in the middle
    pos = len(const) // 2
    bad_const = const[:pos] + '$' + const[pos:]

    mutated = mm_content.replace(const, bad_const, 1)

    return mutated, f"dollar_in_symbol_{const}"


@st.composite
def mutate_duplicate_label(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #13: Duplicate labels.

    metamath.exe: Should reject
    Status: UNKNOWN - needs testing

    Example: ax1 $a ... $. ... ax1 $p ... $.
    """
    # Find all labels
    labels = re.findall(r'(\w+)\s+\$[feap]', mm_content)
    if len(labels) < 2:
        return mm_content, "not_enough_labels"

    # Pick a label to duplicate
    label = draw(st.sampled_from(labels))

    # Find the second occurrence of any label statement
    matches = list(re.finditer(r'(\w+)\s+\$[feap]', mm_content))
    if len(matches) < 2:
        return mm_content, "not_enough_statements"

    # Replace second label with first label
    second_match = matches[1]
    original = second_match.group(0)
    duplicated = label + original[len(second_match.group(1)):]

    mutated = mm_content.replace(original, duplicated, 1)

    return mutated, f"duplicate_label_{label}"


@st.composite
def mutate_unbalanced_blocks(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #4: Unbalanced ${$} blocks.

    metamath.exe: Should reject
    Status: UNKNOWN - needs testing

    Example: ${ $v x $. (missing closing $})
    """
    # Find a block
    block_match = re.search(r'\$\{.*?\$\}', mm_content, re.DOTALL)
    if not block_match:
        return mm_content, "no_blocks"

    choice = draw(st.sampled_from(['remove_open', 'remove_close', 'extra_open', 'extra_close']))

    if choice == 'remove_open':
        mutated = mm_content.replace('${', '', 1)
        desc = "missing_open_block"
    elif choice == 'remove_close':
        mutated = mm_content.replace('$}', '', 1)
        desc = "missing_close_block"
    elif choice == 'extra_open':
        mutated = mm_content.replace('${', '${ ${', 1)
        desc = "extra_open_block"
    else:  # extra_close
        mutated = mm_content + '\n$}\n'
        desc = "extra_close_block"

    return mutated, desc


@st.composite
def mutate_nested_comments(draw, mm_content: str) -> Tuple[str, str]:
    """
    Gap #3: Nested comments (not allowed per spec).

    metamath.exe: Should reject
    Status: UNKNOWN - needs testing

    Example: $( outer $( inner $) $)
    """
    # Find a comment
    comment_match = re.search(r'\$\(.*?\$\)', mm_content, re.DOTALL)
    if not comment_match:
        return mm_content, "no_comments"

    # Insert nested comment delimiters
    original = comment_match.group(0)
    content = original[2:-2]  # Strip $( and $)

    if len(content) < 10:
        return mm_content, "comment_too_short"

    # Insert $( or $) in the middle
    pos = len(content) // 2
    nested = content[:pos] + ' $( nested ' + content[pos:]
    mutated_comment = '$(' + nested + '$)'

    mutated = mm_content.replace(original, mutated_comment, 1)

    return mutated, "nested_comment"


# Mutation registry for easy lookup
MUTATION_GENERATORS = {
    MutationType.D_CONSTANT: mutate_d_constant,
    MutationType.D_DUPLICATE: mutate_d_duplicate,
    MutationType.VAR_TO_CONSTANT: mutate_var_to_constant,
    MutationType.UNKNOWN_STEP: mutate_unknown_step,
    MutationType.DOLLAR_IN_SYMBOL: mutate_dollar_in_symbol,
    MutationType.DUPLICATE_LABEL: mutate_duplicate_label,
    MutationType.UNBALANCED_BLOCKS: mutate_unbalanced_blocks,
    MutationType.NESTED_COMMENTS: mutate_nested_comments,
}


@st.composite
def apply_mutation(draw, mm_content: str, mutation_type: str = None) -> Tuple[str, str]:
    """
    Apply a mutation to a valid Metamath database.

    Args:
        mm_content: Valid Metamath database content
        mutation_type: Specific mutation to apply (or None for random)

    Returns:
        (mutated_content, mutation_description)
    """
    if mutation_type is None:
        # Pick random mutation
        mutation_type = draw(st.sampled_from(list(MUTATION_GENERATORS.keys())))

    generator = MUTATION_GENERATORS[mutation_type]
    return draw(generator(mm_content))


if __name__ == '__main__':
    # Test mutations
    test_mm = """
$c wff |- -> ( ) $.
$v ph ps x y $.
${ $v t $. $}
wph $f wff ph $.
wps $f wff ps $.
xf $f wff x $.
yf $f wff y $.
ax1 $a |- ( ph -> ( ps -> ph ) ) $.
th1 $p |- ( ph -> ph ) $= wph wph wps ax1 ax1 $.
"""

    print("Testing mutations on sample database:\n")
    print("=" * 80)

    for mut_type, generator in MUTATION_GENERATORS.items():
        print(f"\nMutation: {mut_type}")
        print("-" * 80)
        mutated, desc = generator(test_mm).example()
        if desc.startswith("no_") or desc.endswith("_too_short"):
            print(f"  Skipped: {desc}")
        else:
            print(f"  Description: {desc}")
            print(f"  Result (first 200 chars):\n{mutated[:200]}")
