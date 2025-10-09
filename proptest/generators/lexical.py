"""
Lexical generators for Metamath property-based testing.

These generators create the basic building blocks of Metamath syntax:
- MATH-SYMBOL: Printable ASCII excluding '$'
- LABEL: Alphanumeric with '.', '-', '_'
- Whitespace and comments

Based on EBNF grammar from Metamath book Appendix E.
"""

from hypothesis import strategies as st


# MATH-SYMBOL ::= (_PRINTABLE-CHARACTER - '$')+
# _PRINTABLE-CHARACTER ::= [#x21-#x7e]
PRINTABLE_ASCII_NO_DOLLAR = (
    "!\"#%&'()*+,-./0123456789:;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
)

# For mutation testing - includes '$'
PRINTABLE_ASCII_WITH_DOLLAR = PRINTABLE_ASCII_NO_DOLLAR + "$"


@st.composite
def math_symbol(draw, min_length=1, max_length=20, allow_dollar=False):
    """
    Generate valid MATH-SYMBOL per Metamath spec.

    MATH-SYMBOL ::= (_PRINTABLE-CHARACTER - '$')+

    Args:
        min_length: Minimum symbol length (default 1)
        max_length: Maximum symbol length (default 20)
        allow_dollar: If True, allow '$' for mutation testing (default False)

    Returns:
        Valid math symbol string

    Examples:
        'term', 'wff', '|-', '0', '+', '(', 'ABC123'
    """
    charset = PRINTABLE_ASCII_WITH_DOLLAR if allow_dollar else PRINTABLE_ASCII_NO_DOLLAR
    length = draw(st.integers(min_value=min_length, max_value=max_length))
    return ''.join(draw(st.sampled_from(charset)) for _ in range(length))


# LABEL ::= ( _LETTER-OR-DIGIT | '.' | '-' | '_' )+
# _LETTER-OR-DIGIT ::= [A-Za-z0-9]
LABEL_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"


@st.composite
def label(draw, min_length=1, max_length=30):
    """
    Generate valid LABEL per Metamath spec.

    LABEL ::= ( _LETTER-OR-DIGIT | '.' | '-' | '_' )+

    Args:
        min_length: Minimum label length (default 1)
        max_length: Maximum label length (default 30)

    Returns:
        Valid label string

    Examples:
        'ax1', 'th_theorem', 'mp.1', 'a-b-c', 'tze', 'test_123'
    """
    length = draw(st.integers(min_value=min_length, max_value=max_length))
    return ''.join(draw(st.sampled_from(LABEL_CHARS)) for _ in range(length))


# _WHITECHAR ::= [#x20#x09#x0d#x0a#x0c]
# Space, Tab, CR, LF, Form Feed
WHITESPACE_CHARS = [' ', '\t', '\r', '\n', '\f']


@st.composite
def whitespace(draw, min_length=1, max_length=4):
    """
    Generate valid whitespace sequence.

    _WHITECHAR ::= [#x20#x09#x0d#x0a#x0c]

    Args:
        min_length: Minimum whitespace length (default 1)
        max_length: Maximum whitespace length (default 4)

    Returns:
        Whitespace string (space, tab, newline, etc.)

    Examples:
        ' ', '  ', '\n', '\t', '  \n'
    """
    length = draw(st.integers(min_value=min_length, max_value=max_length))
    return ''.join(draw(st.sampled_from(WHITESPACE_CHARS)) for _ in range(length))


@st.composite
def single_whitespace(draw):
    """Generate single whitespace character (most common case)."""
    return draw(st.sampled_from([' ', '\n', '\t']))


@st.composite
def comment(draw, min_length=0, max_length=100, allow_nesting=False):
    """
    Generate valid Metamath comment.

    Comment ::= '$(' _WHITECHAR+ content _WHITECHAR+ '$)' _WHITECHAR

    Important: Comments do NOT nest in Metamath spec.

    Args:
        min_length: Minimum content length (default 0)
        max_length: Maximum content length (default 100)
        allow_nesting: If True, allow nested $( $) for mutation testing

    Returns:
        Valid comment string including delimiters and trailing whitespace

    Examples:
        '$( test $) '
        '$( This is a comment $)\\n'
        '$(  $) '  # Empty comment (valid)
    """
    # Generate comment content
    # Use safe character set to avoid accidentally creating $( or $)
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:!?-_+=*/[]{}()<>@#%&|~"

    content_length = draw(st.integers(min_value=min_length, max_value=max_length))
    content = ''.join(draw(st.sampled_from(safe_chars)) for _ in range(content_length))

    # For mutation testing, allow nested delimiters
    if allow_nesting and content_length > 5:
        # Inject nested $( or $)
        insert_pos = draw(st.integers(min_value=1, max_value=len(content)-1))
        nested = draw(st.sampled_from(['$(', '$)']))
        content = content[:insert_pos] + nested + content[insert_pos:]

    # Comments must have whitespace before and after content
    ws_before = draw(single_whitespace())
    ws_after = draw(single_whitespace())
    ws_trailing = draw(single_whitespace())

    return f"$({ws_before}{content}{ws_after}$){ws_trailing}"


# Common typecode constants
COMMON_TYPECODES = ['term', 'wff', '|-', 'class', 'setvar']


@st.composite
def typecode(draw):
    """
    Generate common typecode (used in $f statements).

    Typecodes are math symbols, but we prefer common ones.

    Returns:
        Common typecode string

    Examples:
        'term', 'wff', '|-', 'class', 'setvar'
    """
    return draw(st.sampled_from(COMMON_TYPECODES))


# Common variable and constant names for readable output
COMMON_VARIABLES = ['x', 'y', 'z', 't', 'r', 's', 'u', 'v', 'w', 'ph', 'ps', 'ch', 'th', 'ta', 'P', 'Q', 'R', 'S', 'A', 'B', 'C']
COMMON_CONSTANTS = ['0', '1', '2', '+', '-', '*', '/', '=', '<', '>', '(', ')', '[', ']', '{', '}']


@st.composite
def variable_name(draw):
    """Generate readable variable name (prefer common ones)."""
    # 80% common, 20% random
    if draw(st.integers(min_value=0, max_value=99)) < 80:
        return draw(st.sampled_from(COMMON_VARIABLES))
    else:
        return draw(math_symbol(min_length=1, max_length=5))


@st.composite
def constant_name(draw):
    """Generate readable constant name (prefer common ones)."""
    # 70% common, 30% random
    if draw(st.integers(min_value=0, max_value=99)) < 70:
        return draw(st.sampled_from(COMMON_CONSTANTS))
    else:
        return draw(math_symbol(min_length=1, max_length=8))


# Mutation generators for gap testing

@st.composite
def non_ascii_text(draw, min_length=1, max_length=20):
    """
    Generate text with non-ASCII characters for Gap #1 testing.

    Should be rejected by compliant verifiers.
    """
    # Include some problematic characters
    bad_chars = '\x00\x01\x7f\x80\xff\u0394\u03B1'  # null, control, high ASCII, Greek
    length = draw(st.integers(min_value=min_length, max_value=max_length))
    return ''.join(draw(st.sampled_from(bad_chars)) for _ in range(length))


@st.composite
def label_with_bad_chars(draw):
    """
    Generate label with invalid characters for mutation testing.

    Should be rejected by compliant verifiers.
    """
    bad_chars = '$(){}[]!@#%^&*+=<>?/'
    base = draw(label())
    insert_pos = draw(st.integers(min_value=0, max_value=len(base)))
    bad_char = draw(st.sampled_from(bad_chars))
    return base[:insert_pos] + bad_char + base[insert_pos:]


if __name__ == '__main__':
    # Test generators
    from hypothesis import find

    print("Sample math_symbols:")
    for _ in range(5):
        print(f"  {find(math_symbol(), lambda x: True)}")

    print("\nSample labels:")
    for _ in range(5):
        print(f"  {find(label(), lambda x: True)}")

    print("\nSample comments:")
    for _ in range(3):
        print(f"  {repr(find(comment(), lambda x: True))}")

    print("\nSample variable names:")
    for _ in range(5):
        print(f"  {find(variable_name(), lambda x: True)}")

    print("\nSample constant names:")
    for _ in range(5):
        print(f"  {find(constant_name(), lambda x: True)}")
