"""
Proof compression module for Metamath.

Implements incremental compression (Pass A & B):
- Pass A: Convert normal proof to compressed format (no Z)
- Pass B: Add greedy Z-tagging for step reuse
"""

from .compress_proof import to_compressed, greedy_z, compress_database

__all__ = ['to_compressed', 'greedy_z', 'compress_database']
