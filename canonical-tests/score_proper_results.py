#!/usr/bin/env python3
"""Score the PROPER results with correct metamath.exe wrapper"""

import re

# Expected outcomes
EXPECTED = {
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
    20: ('ACCEPT', 'Unknown step with ? (accepted with warning)'),
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
    46: ('ACCEPT_PERM', 'Include in inner blocks (permissive)'),
    47: ('REJECT', '$c in inner scope'),
    48: ('REJECT', 'Variable conflict via include'),
    49: ('ACCEPT_PERM', 'Token splice in axiom'),
    50: ('ACCEPT_PERM', 'Token splice in proof'),
}

# Read results
with open('test_results_proper_20251008_102945.txt', 'r') as f:
    content = f.read()

# Parse results
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

# Score each verifier
print("="*100)
print("FINAL COMPREHENSIVE RESULTS - PROPERLY SCORED WITH CORRECT METAMATH.EXE WRAPPER")
print("="*100)
print()

results_table = []

for vname in ['metamath.exe', 'metamath-knife', 'mm-lean4', 'mm-lean4 --perm', 'mmverify_pure', 'mmverify_pure --perm', 'goverify']:
    results = verifiers[vname]
    
    correct_accept = 0
    correct_reject = 0
    incorrect_accept = 0
    incorrect_reject = 0
    not_tested = 0
    
    errors = []
    
    for test_num, (expected, desc) in EXPECTED.items():
        if test_num not in results:
            not_tested += 1
            continue
            
        actual = results[test_num]
        
        # For permissive-only tests
        if expected == 'ACCEPT_PERM':
            if '--perm' not in vname and vname != 'goverify':
                # Strict mode should reject
                if actual == 'FAIL':
                    correct_reject += 1
                else:
                    incorrect_accept += 1
                    errors.append(f"Test {test_num}: {desc} - incorrectly accepted in strict mode")
                continue
            else:
                # Permissive mode should accept
                expected = 'ACCEPT'
        
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
                errors.append(f"Test {test_num}: {desc} - should REJECT but ACCEPTED")
    
    total_correct = correct_accept + correct_reject
    total_incorrect = incorrect_accept + incorrect_reject
    total_tested = total_correct + total_incorrect
    
    accuracy = (total_correct / total_tested * 100) if total_tested > 0 else 0
    
    results_table.append({
        'name': vname,
        'correct': total_correct,
        'correct_accept': correct_accept,
        'correct_reject': correct_reject,
        'incorrect': total_incorrect,
        'incorrect_accept': incorrect_accept,
        'incorrect_reject': incorrect_reject,
        'accuracy': accuracy,
        'errors': errors
    })

# Sort by accuracy
results_table.sort(key=lambda x: x['accuracy'], reverse=True)

# Print table
print(f"{'Rank':<5} {'Verifier':<25} {'Accuracy':>10} {'Correct':>8} {'Incorrect':>10}")
print("-" * 100)

for i, r in enumerate(results_table, 1):
    print(f"{i:<5} {r['name']:<25} {r['accuracy']:>9.1f}% {r['correct']:>8} {r['incorrect']:>10}")

print()
print("="*100)
print("DETAILED BREAKDOWN")
print("="*100)

for r in results_table:
    print()
    print(f"{r['name']:}")
    print(f"  Correct: {r['correct']} ({r['correct_accept']} accept, {r['correct_reject']} reject)")
    print(f"  Incorrect: {r['incorrect']} ({r['incorrect_accept']} wrong accept, {r['incorrect_reject']} wrong reject)")
    print(f"  Accuracy: {r['accuracy']:.1f}%")
    
    if r['errors']:
        print(f"  Errors ({len(r['errors'])}):")
        for err in r['errors'][:5]:  # Show first 5 errors
            print(f"    • {err}")
        if len(r['errors']) > 5:
            print(f"    ... and {len(r['errors']) - 5} more")

