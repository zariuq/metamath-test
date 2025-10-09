#!/usr/bin/env python3
"""Debug the parser to see why hex exclusion doesn't work"""

import sys, re
sys.path.insert(0, '.')
from framework.ebnf_parser import EBNFParser

# Monkey-patch to add debug output
original_parse_rule = EBNFParser._parse_rule
original_parse_expr = EBNFParser._parse_expr

def debug_parse_rule(self, text):
    print(f'_parse_rule called with: {text!r}')

    match = re.match(r'([A-Za-z0-9_-]+)\s*::=(.*)', text, re.DOTALL)
    if match:
        name = match.group(1)
        expr_text = match.group(2).strip()
        print(f'  Rule name: {name!r}')
        print(f'  Expression text: {expr_text!r}')

    return original_parse_rule(self, text)

def debug_parse_expr(self, text):
    text_stripped = text.strip()
    print(f'_parse_expr called with: {text_stripped!r}')

    # Check exclusion
    exclusion_match = re.match(r'(\[[^\]]+\])\s*-\s*["\'](.)["\']', text_stripped)
    print(f'  Exclusion regex matches: {exclusion_match is not None}')

    if '|' in text_stripped:
        print('  Has |, will check choices...')

    # Call original
    result = original_parse_expr(self, text)
    print(f'  Returned: {type(result).__name__}')
    return result

EBNFParser._parse_rule = debug_parse_rule
EBNFParser._parse_expr = debug_parse_expr

print("=" * 70)
print("Parsing: MATH ::= [#x21-#x7E] - '$'")
print("=" * 70)

parser = EBNFParser()
grammar = parser.parse("MATH ::= [#x21-#x7E] - '$'")

print(f'\nFinal result:')
print(f'  Type: {type(grammar.rules[0].expr).__name__}')
print(f'  Expr: {grammar.rules[0].expr}')
