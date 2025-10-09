#!/usr/bin/env python3
"""
Metamath Proof Compression

Implements incremental compression following Metamath spec:
- Pass A: Normal → Compressed (no Z-tagging)
- Pass B: Greedy Z-tagging for step reuse

Base encoding:
- Integers 1-20: A-T (base-20)
- Integers 21-120: UA-UT, ..., YA-YT (base-5,20 using U,V,W,X,Y prefixes)
- Special: Z = save current result for later reuse
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ProofStatement:
    """A single $p statement"""
    label: str
    typecode: str
    expression: List[str]
    proof: List[str]  # Normal proof (list of labels)
    mandatory_f: List[str]  # Mandatory $f labels in RPN order
    mandatory_e: List[str]  # Mandatory $e labels


def encode_int(n: int) -> str:
    """
    Encode integer to compressed proof letters.

    1-20: A-T
    21-120: UA-UT, VA-VT, ..., YA-YT (5 groups of 20)
    121+: Not supported in simple implementation
    """
    if n < 1:
        raise ValueError(f"Cannot encode {n}: must be >= 1")

    if n <= 20:
        # A-T (1-20)
        return chr(ord('A') + n - 1)

    if n <= 120:
        # Two-letter encoding
        # 21-40: UA-UT, 41-60: VA-VT, etc.
        n -= 21  # Now 0-99
        group = n // 20  # 0-4
        offset = n % 20  # 0-19

        first = chr(ord('U') + group)  # U, V, W, X, Y
        second = chr(ord('A') + offset)  # A-T
        return first + second

    raise ValueError(f"Cannot encode {n}: too large (>120)")


def decode_int(s: str) -> Tuple[int, int]:
    """
    Decode compressed letters to integer.

    Returns: (value, chars_consumed)
    """
    if not s:
        raise ValueError("Empty string")

    first = s[0]

    # Check for two-letter encoding (U-Y prefix)
    if first in 'UVWXY':
        if len(s) < 2:
            raise ValueError(f"Incomplete two-letter encoding: {s}")

        second = s[1]
        if second not in 'ABCDEFGHIJKLMNOPQRST':
            raise ValueError(f"Invalid second letter: {second}")

        group = ord(first) - ord('U')  # 0-4
        offset = ord(second) - ord('A')  # 0-19
        value = 21 + group * 20 + offset
        return (value, 2)

    # Single letter A-T (1-20)
    if first in 'ABCDEFGHIJKLMNOPQRST':
        value = ord(first) - ord('A') + 1
        return (value, 1)

    # Z is special (save marker)
    if first == 'Z':
        return (-1, 1)  # Special marker

    raise ValueError(f"Invalid character: {first}")


def parse_proof_statement(db: str, label: str) -> Optional[ProofStatement]:
    """
    Extract a $p statement and its proof from database.

    Returns None if not found or has no proof.
    """
    # Find the statement
    pattern = rf'{re.escape(label)}\s+\$p\s+(.*?)\$=\s+(.*?)\$\.'
    match = re.search(pattern, db, re.DOTALL)

    if not match:
        return None

    # Parse typecode and expression
    statement_part = match.group(1).strip()
    proof_part = match.group(2).strip()

    # Split statement: first token is typecode, rest is expression
    tokens = statement_part.split()
    if not tokens:
        return None

    typecode = tokens[0]
    expression = tokens[1:]

    # Parse proof (for now, assume normal proof - not compressed)
    if '(' in proof_part:
        # Compressed proof - skip for now
        return None

    proof = proof_part.split()

    # For simplicity, we'll need to look up mandatory hypotheses
    # This is a simplified version - real implementation needs full parsing
    return ProofStatement(
        label=label,
        typecode=typecode,
        expression=expression,
        proof=proof,
        mandatory_f=[],  # Would need full parse
        mandatory_e=[]
    )


def to_compressed(db: str, statement_label: str = None) -> str:
    """
    Convert normal proofs to compressed format (Pass A - no Z).

    If statement_label is None, compresses all $p statements.

    Args:
        db: Complete Metamath database
        statement_label: Specific statement to compress (or None for all)

    Returns:
        Modified database with compressed proofs
    """
    # This is a simplified implementation
    # Full implementation requires complete parsing

    # For now, just mark as compressed format
    result = db

    # Find all $p statements with normal proofs
    pattern = r'(\w+)\s+\$p\s+(.*?)\$=\s+([^(][^$]*?)\$\.'

    def compress_match(match):
        label = match.group(1)
        statement = match.group(2).strip()
        proof = match.group(3).strip()

        # Skip if already compressed (has parentheses)
        if '(' in proof:
            return match.group(0)

        # Parse proof steps
        steps = proof.split()
        if not steps:
            return match.group(0)

        # For simple case: assume all steps are in label-list
        # (In reality, need to distinguish mandatory hyps)
        label_list = steps

        # Encode each step as integer
        encoded = []
        for i, step in enumerate(steps, 1):
            encoded.append(encode_int(i))

        # Format: $= ( label-list ) ENCODED $.
        compressed_proof = f"( {' '.join(label_list)} ) {''.join(encoded)}"

        return f"{label} $p {statement} $= {compressed_proof} $."

    result = re.sub(pattern, compress_match, result, flags=re.DOTALL)

    return result


def greedy_z(db: str, min_gain: int = 1) -> str:
    """
    Apply greedy Z-tagging to compressed proofs (Pass B).

    Simulates proof execution to find repeated subexpressions,
    then tags them with Z for reuse.

    Args:
        db: Database with compressed proofs (from Pass A)
        min_gain: Minimum character savings to add Z-tag

    Returns:
        Database with Z-tagged compressed proofs
    """
    # This is a placeholder - full implementation requires:
    # 1. Parse and simulate proof execution
    # 2. Track expression results at each step
    # 3. Identify repeats
    # 4. Calculate gain for Z-tagging
    # 5. Re-encode proof with Z tags

    # For now, return unchanged
    # Real implementation coming in next iteration
    return db


def compress_database(db: str, use_z: bool = False, min_gain: int = 1) -> str:
    """
    Compress all proofs in a database.

    Args:
        db: Input database
        use_z: Whether to apply Z-tagging (Pass B)
        min_gain: Minimum gain for Z-tags

    Returns:
        Compressed database
    """
    # Pass A: Basic compression
    result = to_compressed(db)

    # Pass B: Z-tagging (if requested)
    if use_z:
        result = greedy_z(result, min_gain)

    return result


if __name__ == "__main__":
    # Test encoding
    print("Testing integer encoding...")
    for n in [1, 10, 20, 21, 40, 60, 80, 100, 120]:
        encoded = encode_int(n)
        decoded, consumed = decode_int(encoded)
        print(f"{n:3d} → {encoded:3s} → {decoded:3d} (consumed {consumed})")

    # Test on simple database
    test_db = """$c wff |- $.
$v ph ps $.
wph $f wff ph $.
wps $f wff ps $.
ax1 $a |- ph $.
ax2 $a |- ps $.
th1 $p |- ph $= wph ax1 $.
"""

    print("\nOriginal:")
    print(test_db)

    print("\nCompressed:")
    compressed = to_compressed(test_db)
    print(compressed)
