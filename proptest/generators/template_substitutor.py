"""
Template substitution - reuse existing .mm test files with random symbols/labels.

This is the key insight: take valid test files like demo0.mm and just randomize
all the symbols and labels while preserving structure. This gives us:
1. Known-valid structure
2. Random lexical variation
3. Easy differential testing

Example:
    Original demo0.mm:
        $c term wff |- $.
        $v t r s $.
        ax1 $a |- ( t = r -> ( t = s -> r = s ) ) $.

    Randomized:
        $c xyz abc pqr $.
        $v foo bar baz $.
        lbl_123 $a pqr ( foo def bar uvw ( foo def baz uvw bar def baz ) ) $.
"""

import re
from typing import Dict, Set, Tuple
from hypothesis import strategies as st
from .lexical import math_symbol, label, constant_name, variable_name, typecode, single_whitespace


class SymbolMapper:
    """
    Maps original symbols/labels to random replacements.

    Maintains consistency: if 'term' maps to 'xyz', all occurrences
    of 'term' in the template become 'xyz'.
    """

    def __init__(self):
        self.constant_map: Dict[str, str] = {}
        self.variable_map: Dict[str, str] = {}
        self.label_map: Dict[str, str] = {}
        self.typecode_map: Dict[str, str] = {}

    def map_constant(self, original: str, replacement: str):
        """Map a constant symbol."""
        self.constant_map[original] = replacement

    def map_variable(self, original: str, replacement: str):
        """Map a variable symbol."""
        self.variable_map[original] = replacement

    def map_label(self, original: str, replacement: str):
        """Map a label."""
        self.label_map[original] = replacement

    def map_typecode(self, original: str, replacement: str):
        """Map a typecode."""
        self.typecode_map[original] = replacement

    def get_constant(self, original: str) -> str:
        """Get mapped constant (or original if not mapped)."""
        return self.constant_map.get(original, original)

    def get_variable(self, original: str) -> str:
        """Get mapped variable (or original if not mapped)."""
        return self.variable_map.get(original, original)

    def get_label(self, original: str) -> str:
        """Get mapped label (or original if not mapped)."""
        return self.label_map.get(original, original)

    def get_typecode(self, original: str) -> str:
        """Get mapped typecode (or original if not mapped)."""
        return self.typecode_map.get(original, original)


def parse_template(mm_content: str) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    """
    Extract constants, variables, labels, and typecodes from a .mm file.

    Returns:
        (constants, variables, labels, typecodes)

    Example:
        For demo0.mm:
        constants = {'0', '+', '=', '->', '(', ')', 'term', 'wff', '|-'}
        variables = {'t', 'r', 's', 'P', 'Q'}
        labels = {'tt', 'tr', 'ts', 'wp', 'wq', 'tze', 'tpl', 'weq', 'wim', 'a1', 'a2', 'min', 'maj', 'mp', 'th1'}
        typecodes = {'term', 'wff', '|-'}
    """
    constants = set()
    variables = set()
    labels = set()
    typecodes = set()

    # Extract $c statements
    for match in re.finditer(r'\$c\s+(.*?)\s+\$\.', mm_content, re.DOTALL):
        symbols = match.group(1).split()
        constants.update(symbols)
        # Typecodes are typically declared in first $c statement
        # Common patterns: term, wff, |-, class, setvar
        for sym in symbols:
            if sym in ['term', 'wff', '|-', 'class', 'setvar'] or len(sym) > 3:
                typecodes.add(sym)

    # Extract $v statements
    for match in re.finditer(r'\$v\s+(.*?)\s+\$\.', mm_content, re.DOTALL):
        symbols = match.group(1).split()
        variables.update(symbols)

    # Extract labels (before $f, $e, $a, $p)
    for match in re.finditer(r'(\S+)\s+\$[feap]\s+', mm_content):
        labels.add(match.group(1))

    return constants, variables, labels, typecodes


@st.composite
def randomized_symbol_mapper(draw, constants: Set[str], variables: Set[str],
                              labels: Set[str], typecodes: Set[str]) -> SymbolMapper:
    """
    Generate random mappings for all symbols in a template.

    Ensures no collisions between different symbol types.

    Args:
        constants: Set of constant symbols from template
        variables: Set of variable symbols from template
        labels: Set of labels from template
        typecodes: Set of typecodes from template

    Returns:
        SymbolMapper with consistent random mappings
    """
    mapper = SymbolMapper()
    used_symbols = set()
    used_labels = set()

    # Map typecodes first (they're also constants but need special handling)
    for tc in typecodes:
        # Keep common typecodes recognizable
        if tc in ['term', 'wff', '|-', 'class', 'setvar']:
            replacement = tc  # Keep as-is for readability
        else:
            replacement = draw(math_symbol(min_length=2, max_length=8))
            while replacement in used_symbols or replacement in typecodes:
                replacement = draw(math_symbol(min_length=2, max_length=8))

        mapper.map_typecode(tc, replacement)
        used_symbols.add(replacement)

    # Map constants (excluding typecodes already mapped)
    for const in constants - typecodes:
        replacement = draw(constant_name())
        while replacement in used_symbols:
            replacement = draw(constant_name())

        mapper.map_constant(const, replacement)
        used_symbols.add(replacement)

    # Map variables
    for var in variables:
        replacement = draw(variable_name())
        while replacement in used_symbols:
            replacement = draw(variable_name())

        mapper.map_variable(var, replacement)
        used_symbols.add(replacement)

    # Map labels
    for lbl in labels:
        replacement = draw(label())
        while replacement in used_labels:
            replacement = draw(label())

        mapper.map_label(lbl, replacement)
        used_labels.add(replacement)

    return mapper


def substitute_template(mm_content: str, mapper: SymbolMapper) -> str:
    """
    Apply symbol mappings to template content.

    This is tricky because we need to:
    1. Preserve keywords ($c, $v, $f, etc.)
    2. Preserve comments
    3. Replace symbols in the right context

    Strategy: Process line by line, identify statement types, apply mappings.
    """
    lines = mm_content.split('\n')
    result_lines = []

    for line in lines:
        # Skip comments (preserve as-is for now)
        if '$(' in line:
            result_lines.append(line)
            continue

        # Process $c statements
        if '$c' in line and '$.' in line:
            match = re.match(r'(\s*\$c\s+)(.*?)(\s+\$\..*)', line, re.DOTALL)
            if match:
                prefix, symbols_str, suffix = match.groups()
                symbols = symbols_str.split()
                new_symbols = [mapper.get_constant(s) if s not in mapper.typecode_map
                              else mapper.get_typecode(s)
                              for s in symbols]
                result_lines.append(f"{prefix}{' '.join(new_symbols)}{suffix}")
                continue

        # Process $v statements
        if '$v' in line and '$.' in line:
            match = re.match(r'(\s*\$v\s+)(.*?)(\s+\$\..*)', line, re.DOTALL)
            if match:
                prefix, symbols_str, suffix = match.groups()
                symbols = symbols_str.split()
                new_symbols = [mapper.get_variable(s) for s in symbols]
                result_lines.append(f"{prefix}{' '.join(new_symbols)}{suffix}")
                continue

        # Process $d statements
        if '$d' in line and '$.' in line:
            match = re.match(r'(\s*\$d\s+)(.*?)(\s+\$\..*)', line, re.DOTALL)
            if match:
                prefix, symbols_str, suffix = match.groups()
                symbols = symbols_str.split()
                new_symbols = [mapper.get_variable(s) for s in symbols]
                result_lines.append(f"{prefix}{' '.join(new_symbols)}{suffix}")
                continue

        # Process labeled statements ($f, $e, $a, $p)
        match = re.match(r'(\s*)(\S+)(\s+\$[feap]\s+)(.*)', line, re.DOTALL)
        if match:
            indent, lbl, keyword, rest = match.groups()
            new_label = mapper.get_label(lbl)

            # For $f: label $f typecode variable $.
            if '$f' in keyword:
                parts = rest.split()
                if len(parts) >= 2:
                    tc = mapper.get_typecode(parts[0])
                    var = mapper.get_variable(parts[1])
                    result_lines.append(f"{indent}{new_label}{keyword}{tc} {var} {' '.join(parts[2:])}")
                    continue

            # For $e, $a, $p: replace all symbols in math expression
            # Need to handle both constants and variables
            parts = rest.split()
            new_parts = []
            for part in parts:
                if part in ['$.', '$=', '${', '$}', '$(', '$)', '$[', '$]']:
                    new_parts.append(part)
                elif part in mapper.typecode_map:
                    new_parts.append(mapper.get_typecode(part))
                elif part in mapper.variable_map:
                    new_parts.append(mapper.get_variable(part))
                elif part in mapper.constant_map:
                    new_parts.append(mapper.get_constant(part))
                elif part in mapper.label_map:  # Proof steps reference labels
                    new_parts.append(mapper.get_label(part))
                else:
                    new_parts.append(part)  # Unknown - keep as-is

            result_lines.append(f"{indent}{new_label}{keyword}{' '.join(new_parts)}")
            continue

        # Default: keep line as-is
        result_lines.append(line)

    return '\n'.join(result_lines)


@st.composite
def randomized_template(draw, template_path: str) -> str:
    """
    Generate randomized version of a template .mm file.

    This is the main entry point for template-based generation.

    Args:
        template_path: Path to template .mm file (e.g., demo0.mm)

    Returns:
        Randomized .mm content with same structure, different symbols

    Example:
        >>> template = randomized_template('../demo0.mm')
        >>> # Generates valid Metamath with random symbols
    """
    # Read template
    with open(template_path, 'r') as f:
        template_content = f.read()

    # Parse to extract symbols
    constants, variables, labels, typecodes = parse_template(template_content)

    # Generate random mappings
    mapper = draw(randomized_symbol_mapper(constants, variables, labels, typecodes))

    # Apply substitutions
    return substitute_template(template_content, mapper)


if __name__ == '__main__':
    # Test template parsing
    test_mm = """
    $( Test file $)
    $c term wff |- 0 + = $.
    $v t r s $.

    tt $f term t $.
    tr $f term r $.

    ax1 $a |- ( t = r -> r = t ) $.
    """

    constants, variables, labels, typecodes = parse_template(test_mm)
    print(f"Constants: {constants}")
    print(f"Variables: {variables}")
    print(f"Labels: {labels}")
    print(f"Typecodes: {typecodes}")
