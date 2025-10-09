"""
Mutation module for injecting specific violations into valid Metamath databases.

Each gap/test has a corresponding mutation function that takes a valid database
and injects exactly ONE violation.
"""

from .inject_gap import inject_gap, GAP_METADATA

__all__ = ['inject_gap', 'GAP_METADATA']
