#!/usr/bin/env python3
"""
PROPER scoring:
1. CORE tests (1-45, 47-48): All verifiers tested
2. PERMISSIVE tests (46, 49, 50): ONLY --perm modes and goverify
"""

import re

# Expected outcomes
EXPECTED = {
    # CORE TESTS - all verifiers
    1: ('REJECT', 'Non-printable ASCII'),
    2: ('REJECT', 'Unclosed comment'),
    3: ('REJECT', 'Unmatched block close'),
    4: ('REJECT', 'Missing $. terminator'),
    5: ('REJECT', 'Empty label'),
    6: ('REJECT', 'Invalid token'),
    7: ('REJECT', 'Constant redeclaration'),
    8: ('REJECT', 'Variable out of scope'),
    9: ('REJECT', 'Missing $d constraint'),
    10: ('REJECT', 'Duplicate label'),
    11: ('REJECT', 'Undefined variable'),
    12: ('REJECT', 'Undefined constant'),
    13: ('REJECT', 'Missing $f for variable'),
    14: ('REJECT', 'Variable without $f hypothesis'),
    15: ('REJECT', 'Multiple $f for variable'),
    16: ('REJECT', 'Conflicting typecodes'),
    17: ('REJECT', 'Include scope violation'),
    18: ('REJECT', 'Invalid proof step'),
    19: ('REJECT', 'Type mismatch in proof'),
    20: ('ACCEPT', 'Unknown step with ? (warning ok)'),
    21: ('REJECT', 'Self-referential proof'),
    22: ('REJECT', 'Typecode mismatch in substitution'),
    23: ('REJECT', 'Using non-essential hypotheses'),
    24: ('REJECT', 'Undefined label in proof'),
    25: ('REJECT', 'Missing space before comment'),
    26: ('REJECT', 'Wrong conclusion in proof'),
    27: ('REJECT', 'Disjoint variable constraint violation'),
    28: ('ACCEPT', 'Self-include (ignored)'),
    29: ('REJECT', 'Compressed proof header mismatch'),
    30: ('ACCEPT', '? in compressed proof (allowed)'),
    31: ('REJECT', 'Nested comments'),
    32: ('REJECT', 'Forward reference in proof'),
    33: ('REJECT', 'Compressed proof stack underflow'),
    34: ('REJECT', 'Label token in math context'),
    35: ('REJECT', '$f scope after block'),
    36: ('REJECT', 'Whitespace in compressed proof'),
    37: ('ACCEPT', 'RPN interleaving'),
    38: ('ACCEPT', 'Valid compressed (complex)'),
    39: ('ACCEPT', 'Basic include'),
    40: ('ACCEPT', 'Scoped include'),
    41: ('ACCEPT', 'Multiple includes (main)'),
    42: ('ACCEPT', 'Duplicate include (2nd ignored)'),
    43: ('ACCEPT', 'Path canonicalization'),
    44: ('ACCEPT', 'Cycle detection (cycle ignored)'),
    45: ('ACCEPT', 'Variable redeclaration (sequential)'),
    47: ('REJECT', '$c in inner scope'),
    48: ('REJECT', 'Variable conflict via include'),
    
    # PERMISSIVE TESTS - only --perm and goverify
    46: ('ACCEPT', 'Include in inner blocks'),
    49: ('ACCEPT', 'Token splice in axiom'),
    50: ('ACCEPT', 'Token splice in proof'),
}

CORE_TESTS = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,47,48]
PERMISSIVE_TESTS = [46, 49, 50]

# Read results
with open('test_results_proper_20251008_102945.txt', 'r') as f:
    content = f.read()

verifiers = {
    'metamath.exe': {},
    'metamath-knife': {},
    'mm-lean4': {},
    'mm-lean4 --perm': {},
    'mmverify_pure': {},
    'mmverify_pure --perm': {},
    'goverify': {}
}

current_test = None
for line in content.split('\n'):
    test_match = re.match(r'Test: test(\d+)_.*\.mm', line)
    if test_match:
        current_test = int(test_match.group(1))
        continue
    
    for vname in verifiers.keys():
        if line.strip().startswith(vname + ':'):
            result = 'PASS' if 'PASS' in line else 'FAIL' if 'FAIL' in line else 'UNKNOWN'
            if current_test:
                verifiers[vname][current_test] = result

def score_verifier(vname, test_list):
    """Score a verifier on specific tests"""
    results = verifiers[vname]
    correct_accept = 0
    correct_reject = 0
    incorrect_accept = 0
    incorrect_reject = 0
    errors = []
    
    for test_num in test_list:
        if test_num not in EXPECTED:
            continue
        if test_num not in results:
            continue
            
        expected, desc = EXPECTED[test_num]
        actual = results[test_num]
        
        if expected == 'ACCEPT':
            if actual == 'PASS':
                correct_accept += 1
            else:
                incorrect_reject += 1
                errors.append(f"Test {test_num}: {desc} - should ACCEPT but REJECTED")
        elif expected == 'REJECT':
            if actual == 'FAIL':
                correct_reject += 1
            else:
                incorrect_accept += 1
                errors.append(f"Test {test_num}: {desc} - should REJECT but ACCEPTED ⚠️")
    
    total_correct = correct_accept + correct_reject
    total_incorrect = incorrect_accept + incorrect_reject
    total = total_correct + total_incorrect
    accuracy = (total_correct / total * 100) if total > 0 else 0
    
    return {
        'correct': total_correct,
        'correct_accept': correct_accept,
        'correct_reject': correct_reject,
        'incorrect': total_incorrect,
        'incorrect_accept': incorrect_accept,
        'incorrect_reject': incorrect_reject,
        'accuracy': accuracy,
        'total': total,
        'errors': errors
    }

print("="*100)
print("FINAL COMPREHENSIVE TEST RESULTS - PROPERLY ORGANIZED")
print("="*100)
print()

print("="*100)
print("PART 1: CORE TESTS (47 tests - binding spec)")
print("="*100)
print()

core_verifiers = ['metamath.exe', 'metamath-knife', 'mm-lean4', 'mm-lean4 --perm', 'mmverify_pure', 'mmverify_pure --perm', 'goverify']
core_results = []

for vname in core_verifiers:
    result = score_verifier(vname, CORE_TESTS)
    result['name'] = vname
    core_results.append(result)

core_results.sort(key=lambda x: x['accuracy'], reverse=True)

print(f"{'Rank':<5} {'Verifier':<25} {'Accuracy':>10} {'Correct':>10} {'Errors':>8}")
print("-" * 100)

for i, r in enumerate(core_results, 1):
    marker = "🏆" if i == 1 else "✅" if r['accuracy'] >= 90 else "⚠️" if r['accuracy'] >= 70 else "❌"
    print(f"{i:<5} {r['name']:<25} {r['accuracy']:>9.1f}% {r['correct']:>2}/{r['total']:<5} {marker} {len(r['errors'])}")

print()
print("="*100)
print("PART 2: PERMISSIVE TESTS (3 tests - optional extensions)")
print("="*100)
print()
print("Only --permissive modes and goverify are tested")
print()

perm_verifiers = ['mm-lean4 --perm', 'mmverify_pure --perm', 'goverify']
perm_results = []

for vname in perm_verifiers:
    result = score_verifier(vname, PERMISSIVE_TESTS)
    result['name'] = vname
    perm_results.append(result)

perm_results.sort(key=lambda x: x['accuracy'], reverse=True)

print(f"{'Rank':<5} {'Verifier':<25} {'Accuracy':>10} {'Correct':>10} {'Notes':>8}")
print("-" * 100)

for i, r in enumerate(perm_results, 1):
    marker = "🏆" if i == 1 else "✅" if r['accuracy'] >= 90 else "⚠️"
    print(f"{i:<5} {r['name']:<25} {r['accuracy']:>9.1f}% {r['correct']:>2}/{r['total']:<5} {marker}")

print()
print("="*100)
print("DETAILED ERROR ANALYSIS")
print("="*100)
print()

# Show errors for top performers
print("CORE TESTS - Error Details for All Verifiers:")
print()

for r in core_results:
    print(f"{r['name']} ({r['accuracy']:.1f}% on CORE):")
    print(f"  Correct: {r['correct_accept']} accept + {r['correct_reject']} reject = {r['correct']}/{r['total']}")
    
    if r['incorrect_accept'] > 0:
        print(f"  ⚠️  FALSE POSITIVES: {r['incorrect_accept']} (accepts invalid code - DANGEROUS!)")
    if r['incorrect_reject'] > 0:
        print(f"  ⚠️  FALSE NEGATIVES: {r['incorrect_reject']} (rejects valid code)")
    
    if r['errors']:
        print(f"  Errors ({len(r['errors'])}):")
        for err in r['errors'][:10]:
            print(f"    • {err}")
        if len(r['errors']) > 10:
            print(f"    ... and {len(r['errors']) - 10} more")
    print()

print()
print("PERMISSIVE TESTS - Error Details:")
print()

for r in perm_results:
    print(f"{r['name']} ({r['accuracy']:.1f}% on PERMISSIVE):")
    print(f"  Correct: {r['correct']}/{r['total']}")
    
    if r['errors']:
        for err in r['errors']:
            print(f"    • {err}")
    print()

