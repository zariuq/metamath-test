"""
EBNF Grammar Parser

Parses EBNF grammar specifications into an AST that can be compiled to
Hypothesis strategies or mutated to generate invalid examples.

Design Goal: Language-agnostic parser for EBNF grammars, easily adaptable
to new languages (MM0, MeTTa-IL, etc.)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Union, List, Optional as Opt, Set
import re


# ============================================================================
# AST Node Types
# ============================================================================

@dataclass
class CharRange:
    """Character range: [a-z] or [#x20-#x7E]"""
    start: Union[str, int]  # 'a' or 0x20
    end: Union[str, int]    # 'z' or 0x7E
    exclude: Opt[str] = None  # Characters to exclude

    def __repr__(self):
        if isinstance(self.start, int):
            s = f"[#x{self.start:02X}-#x{self.end:02X}]"
        else:
            s = f"[{self.start}-{self.end}]"
        if self.exclude:
            s += f" - '{self.exclude}'"
        return s


@dataclass
class CharSet:
    """Set of individual characters: [abc] or [#x09#x0A#x0D]"""
    chars: Set[Union[str, int]]

    def __repr__(self):
        char_strs = []
        for c in sorted(self.chars):
            if isinstance(c, int):
                char_strs.append(f"#x{c:02X}")
            else:
                char_strs.append(c)
        return f"[{''.join(char_strs)}]"


@dataclass
class Literal:
    """Literal string: 'foo' or "bar" """
    value: str

    def __repr__(self):
        return f"'{self.value}'"


@dataclass
class NonTerminal:
    """Reference to another rule: database, statement, etc."""
    name: str

    def __repr__(self):
        return f"<{self.name}>"


@dataclass
class Sequence:
    """Sequence of elements: A B C"""
    elements: List['GrammarExpr']

    def __repr__(self):
        return f"({' '.join(str(e) for e in self.elements)})"


@dataclass
class Choice:
    """Alternatives: A | B | C"""
    alternatives: List['GrammarExpr']

    def __repr__(self):
        return f"({'|'.join(str(a) for a in self.alternatives)})"


@dataclass
class Optional:
    """Optional element: A?"""
    element: 'GrammarExpr'

    def __repr__(self):
        return f"{self.element}?"


@dataclass
class ZeroOrMore:
    """Zero or more repetitions: A*"""
    element: 'GrammarExpr'

    def __repr__(self):
        return f"{self.element}*"


@dataclass
class OneOrMore:
    """One or more repetitions: A+"""
    element: 'GrammarExpr'

    def __repr__(self):
        return f"{self.element}+"


# Type alias for any grammar expression
GrammarExpr = Union[
    CharRange, CharSet, Literal, NonTerminal,
    Sequence, Choice, Optional, ZeroOrMore, OneOrMore
]


@dataclass
class Rule:
    """Grammar production rule: name ::= expression"""
    name: str
    expr: GrammarExpr
    comment: Opt[str] = None

    def __repr__(self):
        comment_str = f"  # {self.comment}" if self.comment else ""
        return f"{self.name} ::= {self.expr}{comment_str}"


@dataclass
class Grammar:
    """Complete EBNF grammar"""
    rules: List[Rule]
    comments: List[str]  # Top-level comments

    def get_rule(self, name: str) -> Opt[Rule]:
        """Find rule by name"""
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None

    def __repr__(self):
        lines = []
        if self.comments:
            lines.extend(f"# {c}" for c in self.comments)
            lines.append("")
        lines.extend(str(r) for r in self.rules)
        return "\n".join(lines)


# ============================================================================
# EBNF Parser
# ============================================================================

class EBNFParser:
    """
    Parse EBNF grammar into AST.

    Supports:
    - Character ranges: [a-z], [A-Z], [0-9], [#x20-#x7E]
    - Character sets: [abc], [#x09#x0A#x0D]
    - Exclusions: [a-z] - 'x'
    - Literals: 'foo', "bar"
    - Non-terminals: database, statement
    - Sequences: A B C
    - Choices: A | B | C
    - Repetition: A*, A+, A?
    - Rules: name ::= expression
    - Comments: # comment
    """

    def __init__(self):
        self.rules = []
        self.comments = []

    def parse(self, text: str) -> Grammar:
        """Parse EBNF grammar text into Grammar AST"""
        lines = text.split('\n')

        current_rule_lines = []

        for line in lines:
            # Strip inline comments (but not # inside [...])
            if '#' in line:
                # Find # that's not inside brackets
                comment_pos = self._find_comment_position(line)
                if comment_pos is not None:
                    code = line[:comment_pos].rstrip()
                    comment = line[comment_pos+1:].strip()
                    line = code
                    if not line and not current_rule_lines:
                        self.comments.append(comment)
                else:
                    line = line.rstrip()
            else:
                line = line.rstrip()

            if not line:
                continue

            # Check if this is a rule definition
            if '::=' in line:
                # Parse previous rule if exists
                if current_rule_lines:
                    self._parse_rule('\n'.join(current_rule_lines))
                    current_rule_lines = []
                current_rule_lines.append(line)
            elif current_rule_lines:
                # Continuation of multi-line rule
                current_rule_lines.append(line)

        # Parse last rule
        if current_rule_lines:
            self._parse_rule('\n'.join(current_rule_lines))

        return Grammar(rules=self.rules, comments=self.comments)

    def _find_comment_position(self, line: str) -> int:
        """Find position of # that starts a comment (not inside [...])"""
        in_brackets = False
        in_quotes = False
        quote_char = None

        for i, ch in enumerate(line):
            if ch in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = ch
                elif ch == quote_char:
                    in_quotes = False
                    quote_char = None
            elif not in_quotes:
                if ch == '[':
                    in_brackets = True
                elif ch == ']':
                    in_brackets = False
                elif ch == '#' and not in_brackets:
                    return i  # Found comment start
        return None  # No comment found

    def _parse_rule(self, text: str):
        """Parse a single rule: name ::= expression"""
        # Extract rule name and expression
        match = re.match(r'([A-Za-z0-9_-]+)\s*::=(.*)', text, re.DOTALL)
        if not match:
            return

        name = match.group(1)
        expr_text = match.group(2).strip()

        # Parse expression
        expr = self._parse_expr(expr_text)

        self.rules.append(Rule(name=name, expr=expr))

    def _parse_expr(self, text: str) -> GrammarExpr:
        """Parse a grammar expression"""
        text = text.strip()

        # Choice: A | B | C
        if '|' in text:
            # Split on | but not inside brackets or quotes
            alternatives = self._split_choices(text)
            if len(alternatives) > 1:
                return Choice([self._parse_expr(alt.strip()) for alt in alternatives])

        # Check for exclusion pattern: [...] - 'x' (must be single atom)
        exclusion_match = re.match(r'(\[[^\]]+\])\s*-\s*["\'](.)["\']', text)
        if exclusion_match:
            # Parse as single charset with exclusion
            return self._parse_charset(text)

        # Sequence: A B C
        parts = self._split_sequence(text)
        if len(parts) > 1:
            return Sequence([self._parse_term(p) for p in parts])

        # Single term
        return self._parse_term(text)

    def _parse_term(self, text: str) -> GrammarExpr:
        """Parse a single term (possibly with repetition)"""
        text = text.strip()

        # Check for repetition suffix
        if text.endswith('*'):
            return ZeroOrMore(self._parse_atom(text[:-1].strip()))
        elif text.endswith('+'):
            return OneOrMore(self._parse_atom(text[:-1].strip()))
        elif text.endswith('?'):
            return Optional(self._parse_atom(text[:-1].strip()))
        else:
            return self._parse_atom(text)

    def _parse_atom(self, text: str) -> GrammarExpr:
        """Parse an atomic expression"""
        text = text.strip()

        # Character range or set: [...]
        if text.startswith('[') and ']' in text:
            return self._parse_charset(text)

        # Literal: '...' or "..."
        if (text.startswith("'") and text.endswith("'")) or \
           (text.startswith('"') and text.endswith('"')):
            return Literal(text[1:-1])

        # Parenthesized expression
        if text.startswith('(') and text.endswith(')'):
            return self._parse_expr(text[1:-1])

        # Non-terminal
        return NonTerminal(text)

    def _parse_charset(self, text: str) -> Union[CharRange, CharSet]:
        """Parse character set or range: [a-z] or [abc] or [#x20-#x7E]"""
        # Extract content between brackets
        match = re.match(r'\[(.*?)\](.*)', text)
        if not match:
            return CharSet(set())

        content = match.group(1)
        suffix = match.group(2).strip()

        # Check for exclusion: - 'char'
        exclude = None
        if suffix.startswith('-'):
            exclude_match = re.match(r"-\s*['\"](.)['\"]", suffix)
            if exclude_match:
                exclude = exclude_match.group(1)

        # Hex range: #x20-#x7E
        hex_range = re.match(r'#x([0-9A-Fa-f]+)-#x([0-9A-Fa-f]+)', content)
        if hex_range:
            start = int(hex_range.group(1), 16)
            end = int(hex_range.group(2), 16)
            return CharRange(start=start, end=end, exclude=exclude)

        # ASCII range: a-z, A-Z, 0-9
        ascii_range = re.match(r'(.)-(.)', content)
        if ascii_range and len(ascii_range.group(1)) == 1 and len(ascii_range.group(2)) == 1:
            return CharRange(start=ascii_range.group(1), end=ascii_range.group(2), exclude=exclude)

        # Character set: [abc] or [#x09#x0A#x0D]
        chars = set()
        i = 0
        while i < len(content):
            if content[i:i+2] == '#x':
                # Hex character
                hex_match = re.match(r'#x([0-9A-Fa-f]+)', content[i:])
                if hex_match:
                    chars.add(int(hex_match.group(1), 16))
                    i += len(hex_match.group(0))
                else:
                    i += 1
            else:
                chars.add(content[i])
                i += 1

        return CharSet(chars)

    def _split_choices(self, text: str) -> List[str]:
        """Split on | but not inside brackets, quotes, or parentheses"""
        parts = []
        current = []
        depth = 0
        in_quotes = False
        quote_char = None
        in_brackets = False

        for i, ch in enumerate(text):
            if ch in ('"', "'") and (i == 0 or text[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = ch
                elif ch == quote_char:
                    in_quotes = False
                    quote_char = None
            elif not in_quotes:
                if ch == '[':
                    in_brackets = True
                elif ch == ']':
                    in_brackets = False
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                elif ch == '|' and depth == 0 and not in_brackets:
                    parts.append(''.join(current))
                    current = []
                    continue

            current.append(ch)

        parts.append(''.join(current))
        return parts

    def _split_sequence(self, text: str) -> List[str]:
        """Split on whitespace but not inside brackets, quotes, or parentheses"""
        parts = []
        current = []
        depth = 0
        in_quotes = False
        quote_char = None
        in_brackets = False

        for i, ch in enumerate(text):
            if ch in ('"', "'") and (i == 0 or text[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = ch
                elif ch == quote_char:
                    in_quotes = False
                    quote_char = None
            elif not in_quotes:
                if ch == '[':
                    in_brackets = True
                elif ch == ']':
                    in_brackets = False
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                elif ch in ' \t\n\r' and depth == 0 and not in_brackets:
                    if current:
                        parts.append(''.join(current))
                        current = []
                    continue

            current.append(ch)

        if current:
            parts.append(''.join(current))

        return parts


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example EBNF grammar
    example = """
    # Simple arithmetic grammar
    expr ::= term ( '+' term | '-' term )*
    term ::= factor ( '*' factor | '/' factor )*
    factor ::= number | '(' expr ')'
    number ::= [0-9]+
    """

    parser = EBNFParser()
    grammar = parser.parse(example)

    print("Parsed Grammar:")
    print("=" * 60)
    print(grammar)
    print()

    # Show individual rules
    print("Rules:")
    print("=" * 60)
    for rule in grammar.rules:
        print(f"{rule.name}:")
        print(f"  {rule.expr}")
        print()
