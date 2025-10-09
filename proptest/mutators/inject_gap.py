#!/usr/bin/env python3
"""
Gap Injection Module

Takes a valid Metamath database and injects exactly ONE violation
corresponding to a specific unit test.

Usage:
    mutated_db = inject_gap(valid_db, gap_id=27)
"""

import re
import random
from typing import Dict, Literal

Verdict = Literal["ACCEPT", "REJECT", "WARN"]

# Metadata for each gap: expected verdicts per verifier
GAP_METADATA: Dict[int, Dict[str, Verdict]] = {
    1: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    2: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    3: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    4: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    5: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    6: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    7: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    8: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    9: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    10: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    11: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    12: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    13: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    14: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    15: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    16: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    17: {"metamath.exe": "ACCEPT", "mmverify": "REJECT"},  # Updated: self-include should be ignored
    18: {"metamath.exe": "ACCEPT", "mmverify": "REJECT"},  # Updated: comments OK in statements
    19: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    20: {"metamath.exe": "WARN", "mmverify": "WARN"},
    21: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    22: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    23: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    24: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    25: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    26: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    27: {"metamath.exe": "REJECT", "mmverify": "REJECT"},  # DV constraint
    28: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    29: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    30: {"metamath.exe": "WARN", "mmverify": "WARN"},
    31: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    32: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    33: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    34: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    35: {"metamath.exe": "REJECT", "mmverify": "REJECT"},
    36: {"metamath.exe": "ACCEPT", "mmverify": "REJECT"},  # Whitespace should be ignored
}


def inject_gap(valid_db: str, gap_id: int, seed: int = None) -> str:
    """
    Inject a specific gap/violation into a valid Metamath database.

    Args:
        valid_db: A valid, well-formed Metamath database
        gap_id: Which gap to inject (1-36)
        seed: Random seed for deterministic mutations

    Returns:
        Modified database with exactly ONE violation

    Raises:
        ValueError: If gap_id is invalid or database can't be mutated
    """
    if gap_id not in GAP_METADATA:
        raise ValueError(f"Invalid gap_id: {gap_id}. Must be 1-36.")

    rng = random.Random(seed)

    # Dispatch to specific mutation function
    mutations = {
        1: inject_gap_1_nonprintable_ascii,
        2: inject_gap_2_missing_whitespace,
        3: inject_gap_3_nested_comments,
        4: inject_gap_4_unbalanced_blocks,
        5: inject_gap_5_dollar_in_symbol,
        6: inject_gap_6_dangling_dollar,
        7: inject_gap_7_redeclaration,
        8: inject_gap_8_scope_violation,
        9: inject_gap_9_invalid_dv,
        10: inject_gap_10_duplicate_labels,
        11: inject_gap_11_label_symbol_conflict,
        12: inject_gap_12_nonconstant_typecode,
        13: inject_gap_13_undeclared_variable,
        14: inject_gap_14_missing_f,
        15: inject_gap_15_multiple_f,
        16: inject_gap_16_conflicting_types,
        17: inject_gap_17_include_in_block,
        18: inject_gap_18_comment_in_statement,
        19: inject_gap_19_illegal_compressed_char,
        20: inject_gap_20_unknown_step,
        21: inject_gap_21_self_reference,
        22: inject_gap_22_type_mismatch,
        23: inject_gap_23_wrong_hypotheses,
        24: inject_gap_24_undefined_label,
        25: inject_gap_25_missing_space,
        26: inject_gap_26_wrong_conclusion,
        27: inject_gap_27_dv_violation,
        28: inject_gap_28_include_placement,
        29: inject_gap_29_compressed_header,
        30: inject_gap_30_compressed_unknown,
        31: inject_gap_31_whitespace_after_comment,
        32: inject_gap_32_forward_reference,
        33: inject_gap_33_stack_underflow,
        34: inject_gap_34_label_math_context,
        35: inject_gap_35_f_scope,
        36: inject_gap_36_compressed_whitespace,
    }

    mutation_fn = mutations.get(gap_id)
    if not mutation_fn:
        raise ValueError(f"Gap {gap_id} not implemented yet")

    return mutation_fn(valid_db, rng)


# =============================================================================
# Individual mutation functions
# =============================================================================

def inject_gap_1_nonprintable_ascii(db: str, rng: random.Random) -> str:
    """Replace a symbol with Unicode character"""
    # Find first $c statement and inject Unicode
    match = re.search(r'(\$c\s+)(\w+)', db)
    if match:
        return db[:match.start(2)] + "→" + db[match.end(2):]
    return db + "\n$c → $.\n"


def inject_gap_2_missing_whitespace(db: str, rng: random.Random) -> str:
    """Remove whitespace between tokens"""
    # Remove space after first $c
    match = re.search(r'\$c\s+', db)
    if match:
        return db[:match.end()-1] + db[match.end():]
    return db.replace("$c ", "$c", 1)


def inject_gap_3_nested_comments(db: str, rng: random.Random) -> str:
    """Insert nested comment delimiter"""
    # Find first comment and nest it
    match = re.search(r'\$\([^$]*\$\)', db)
    if match:
        mid = match.start() + len(match.group()) // 2
        return db[:mid] + " $( nested " + db[mid:]
    return db + "\n$( outer $( nested $) $)\n"


def inject_gap_4_unbalanced_blocks(db: str, rng: random.Random) -> str:
    """Remove a closing $}"""
    match = re.search(r'\$\}', db)
    if match:
        return db[:match.start()] + db[match.end():]
    # Or add extra ${
    return "${\n" + db


def inject_gap_5_dollar_in_symbol(db: str, rng: random.Random) -> str:
    """Add $ to a constant name"""
    match = re.search(r'(\$c\s+)(\w+)', db)
    if match:
        return db[:match.end(2)] + "$bad" + db[match.end(2):]
    return db + "\n$c a$b $.\n"


def inject_gap_6_dangling_dollar(db: str, rng: random.Random) -> str:
    """Add dangling $ at EOF"""
    return db.rstrip() + "\n$"


def inject_gap_7_redeclaration(db: str, rng: random.Random) -> str:
    """Redeclare a constant"""
    match = re.search(r'\$c\s+(\w+)', db)
    if match:
        const = match.group(1)
        return db + f"\n$c {const} $.\n"
    return db + "\n$c wff $.\n$c wff $.\n"


def inject_gap_8_scope_violation(db: str, rng: random.Random) -> str:
    """Use variable outside its scope"""
    # Find a variable declaration in a block
    match = re.search(r'\$\{[^}]*\$v\s+(\w+)[^}]*\$\}', db, re.DOTALL)
    if match:
        var = re.search(r'\$v\s+(\w+)', match.group()).group(1)
        return db + f"\nbad $a |- {var} $.\n"
    return db + "\n${ $v x $. $}\nbad $a |- x $.\n"


def inject_gap_9_invalid_dv(db: str, rng: random.Random) -> str:
    """Put constant in $d statement"""
    match = re.search(r'\$c\s+(\w+)', db)
    if match:
        const = match.group(1)
        return db + f"\n$d {const} {const} $.\n"
    return db + "\n$d wff |- $.\n"


def inject_gap_10_duplicate_labels(db: str, rng: random.Random) -> str:
    """Reuse a label"""
    match = re.search(r'(\w+)\s+\$[afep]', db)
    if match:
        label = match.group(1)
        return db + f"\n{label} $a |- ph $.\n"
    return db + "\ndup $a |- ph $.\ndup $a |- ph $.\n"


def inject_gap_11_label_symbol_conflict(db: str, rng: random.Random) -> str:
    """Use constant name as label"""
    match = re.search(r'\$c\s+(\w+)', db)
    if match:
        const = match.group(1)
        return db + f"\n{const} $a |- ph $.\n"
    return db + "\n$c wff $.\nwff $a |- ph $.\n"


def inject_gap_12_nonconstant_typecode(db: str, rng: random.Random) -> str:
    """Use variable as typecode"""
    match = re.search(r'\$v\s+(\w+)', db)
    if match:
        var = match.group(1)
        return db + f"\nbad $f {var} x $.\n"
    return db + "\n$v x $.\nbad $f x y $.\n"


def inject_gap_13_undeclared_variable(db: str, rng: random.Random) -> str:
    """Use undeclared variable in $f"""
    return db + "\nbad $f wff undeclared $.\n"


def inject_gap_14_missing_f(db: str, rng: random.Random) -> str:
    """Use variable without $f"""
    match = re.search(r'\$v\s+(\w+)', db)
    if match:
        var = match.group(1)
        # Find if there's already an $f for this var, skip if so
        if not re.search(rf'\$f\s+\w+\s+{var}\s+\$\.', db):
            return db + f"\nbad $a |- {var} $.\n"
    return db + "\n$v x $.\nbad $a |- x $.\n"


def inject_gap_15_multiple_f(db: str, rng: random.Random) -> str:
    """Declare multiple $f for same variable"""
    match = re.search(r'\$v\s+(\w+)', db)
    if match:
        var = match.group(1)
        return db + f"\nf1 $f wff {var} $.\nf2 $f class {var} $.\n"
    return db + "\n$v x $.\nf1 $f wff x $.\nf2 $f class x $.\n"


def inject_gap_16_conflicting_types(db: str, rng: random.Random) -> str:
    """Give variable conflicting types in nested scopes"""
    match = re.search(r'\$v\s+(\w+)', db)
    if match:
        var = match.group(1)
        return db + f"\n${{ f1 $f wff {var} $. ${{ f2 $f class {var} $. $}} $}}\n"
    return db + "\n$v x $.\n${ f1 $f wff x $. ${ f2 $f class x $. $} $}\n"


def inject_gap_17_include_in_block(db: str, rng: random.Random) -> str:
    """Put include inside block"""
    return "${\n$[ /tmp/test.mm $]\n$}\n" + db


def inject_gap_18_comment_in_statement(db: str, rng: random.Random) -> str:
    """Put comment between statement tokens"""
    match = re.search(r'(\w+\s+\$a\s+)(\|-)', db)
    if match:
        return db[:match.end(1)] + "$( comment $) " + db[match.end(1):]
    return db + "\nbad $a $( comment $) |- ph $.\n"


def inject_gap_19_illegal_compressed_char(db: str, rng: random.Random) -> str:
    """Put digit in compressed proof"""
    # Find compressed proof
    match = re.search(r'(\$=\s*\([^)]*\)\s*)([A-Z]+)', db)
    if match:
        return db[:match.end(2)-1] + "0" + db[match.end(2):]
    # Or add one
    return db + "\nth $p |- ph $= ( ax ) A0B $.\n"


def inject_gap_20_unknown_step(db: str, rng: random.Random) -> str:
    """Add ? to proof"""
    match = re.search(r'\$p[^$]*\$=', db)
    if match:
        end = db.find('$.', match.end())
        if end > 0:
            return db[:end] + " ? " + db[end:]
    return db + "\nth $p |- ph $= ? $.\n"


def inject_gap_21_self_reference(db: str, rng: random.Random) -> str:
    """Make proof reference itself"""
    match = re.search(r'(\w+)\s+\$p([^$]*)\$=', db)
    if match:
        label = match.group(1)
        end = db.find('$.', match.end())
        if end > 0:
            return db[:end] + f" {label} " + db[end:]
    return db + "\nevil $p |- ph $= evil $.\n"


def inject_gap_22_type_mismatch(db: str, rng: random.Random) -> str:
    """Create type mismatch in proof"""
    # This requires finding axioms with different types
    return db + "\n$v x y $.\nf1 $f wff x $.\nf2 $f class y $.\nax $a |- x $.\nbad $p |- y $= f2 ax $.\n"


def inject_gap_23_wrong_hypotheses(db: str, rng: random.Random) -> str:
    """Use hypothesis from wrong scope"""
    return db + "\n${ hyp $e |- ph $. th $p |- ph $= hyp $. $}\nevil $p |- ph $= hyp $.\n"


def inject_gap_24_undefined_label(db: str, rng: random.Random) -> str:
    """Reference non-existent label"""
    return db + "\nbad $p |- ph $= nosuchlabel $.\n"


def inject_gap_25_missing_space(db: str, rng: random.Random) -> str:
    """Remove space before comment"""
    match = re.search(r'\s+\$\(', db)
    if match:
        return db[:match.start()] + "$(" + db[match.end():]
    return db + "\n$c wff$.$(comment$)\n"


def inject_gap_26_wrong_conclusion(db: str, rng: random.Random) -> str:
    """Proof produces wrong result"""
    return db + "\n$v x y $.\nf1 $f wff x $.\nf2 $f wff y $.\nax $a |- x $.\nbad $p |- y $= f1 ax $.\n"


def inject_gap_27_dv_violation(db: str, rng: random.Random) -> str:
    """Violate DV constraint"""
    return db + "\n$v x y $.\nf1 $f wff x $.\nf2 $f wff y $.\n$d x y $.\nax $a |- x $.\nbad $p |- y $= f2 ax $.\n"


def inject_gap_28_include_placement(db: str, rng: random.Random) -> str:
    """Include inside block"""
    return inject_gap_17_include_in_block(db, rng)


def inject_gap_29_compressed_header(db: str, rng: random.Random) -> str:
    """Mismatch compressed proof header"""
    return db + "\nax1 $a |- ph $.\nax2 $a |- ph $.\nbad $p |- ph $= ( ax1 ) B $.\n"


def inject_gap_30_compressed_unknown(db: str, rng: random.Random) -> str:
    """? in compressed proof"""
    return db + "\nth $p |- ph $= ( ax ) ? $.\n"


def inject_gap_31_whitespace_after_comment(db: str, rng: random.Random) -> str:
    """No space after $)"""
    return "$( comment $)$c wff $.\n" + db


def inject_gap_32_forward_reference(db: str, rng: random.Random) -> str:
    """Reference later label"""
    return db + "\nearly $p |- ph $= later $.\nlater $a |- ph $.\n"


def inject_gap_33_stack_underflow(db: str, rng: random.Random) -> str:
    """Compressed proof pops too many"""
    return db + "\nth $p |- ph $= ( ax ) C $.\n"


def inject_gap_34_label_math_context(db: str, rng: random.Random) -> str:
    """Use label where math expected"""
    return db + "\nbad $a label x $.\n"


def inject_gap_35_f_scope(db: str, rng: random.Random) -> str:
    """Use $f after block close"""
    return db + "\n${ $v x $. wf $f wff x $. $}\nbad $a |- x $.\n"


def inject_gap_36_compressed_whitespace(db: str, rng: random.Random) -> str:
    """Add whitespace in compressed proof"""
    match = re.search(r'(\$=\s*\([^)]*\)\s*)([A-Z]+)', db)
    if match:
        letters = match.group(2)
        # Insert newline/tab in middle
        mid = len(letters) // 2
        return db[:match.start(2) + mid] + "\n\t" + db[match.start(2) + mid:]
    return db + "\nth $p |- ph $= ( ax ) A\n\tB $.\n"


if __name__ == "__main__":
    # Test basic injection
    simple_db = """$c wff |- $.
$v ph $.
wf $f wff ph $.
ax $a |- ph $.
"""

    print("Testing gap injection...")
    for gap_id in [1, 7, 10, 20, 27]:
        try:
            mutated = inject_gap(simple_db, gap_id)
            verdict = GAP_METADATA[gap_id]["metamath.exe"]
            print(f"Gap {gap_id}: {verdict} - OK")
        except Exception as e:
            print(f"Gap {gap_id}: ERROR - {e}")
