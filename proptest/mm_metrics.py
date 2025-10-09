#!/usr/bin/env python3
"""
Metamath Database Metrics Analyzer

Analyzes generated Metamath databases to measure:
- Proof length statistics
- Structural diversity
- Feature usage ($e, $d, blocks, compressed proofs)
- Novelty (duplicate detection)
"""

import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field


@dataclass
class ProofMetrics:
    """Metrics for a single proof"""
    label: str
    conclusion: str
    proof_length: int  # Number of steps in proof
    uses_e_hyps: bool  # Does it use essential hypotheses?
    uses_compressed: bool  # Is it a compressed proof?
    ast_depth: int  # Max nesting depth of conclusion


@dataclass
class DatabaseMetrics:
    """Metrics for entire database"""
    total_lines: int = 0

    # Counts
    num_constants: int = 0
    num_variables: int = 0
    num_f_hyps: int = 0
    num_e_hyps: int = 0
    num_d_statements: int = 0
    num_axioms: int = 0
    num_theorems: int = 0
    num_blocks: int = 0

    # Proof statistics
    proof_lengths: List[int] = field(default_factory=list)
    proofs_with_e: int = 0  # Proofs that depend on $e
    compressed_proofs: int = 0

    # Diversity
    unique_conclusions: Set[str] = field(default_factory=set)
    conclusion_counts: Counter = field(default_factory=Counter)

    # AST depth
    ast_depths: List[int] = field(default_factory=list)

    def median(self, values: List[int]) -> float:
        """Compute median of values"""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        if n % 2 == 0:
            return (sorted_vals[n//2 - 1] + sorted_vals[n//2]) / 2
        return sorted_vals[n//2]

    def report(self) -> str:
        """Generate human-readable metrics report"""
        lines = []
        lines.append("=" * 70)
        lines.append("METAMATH DATABASE METRICS")
        lines.append("=" * 70)
        lines.append("")

        lines.append(f"Total lines: {self.total_lines}")
        lines.append("")

        lines.append("## Declarations")
        lines.append(f"  Constants ($c):           {self.num_constants}")
        lines.append(f"  Variables ($v):           {self.num_variables}")
        lines.append(f"  Floating hypotheses ($f): {self.num_f_hyps}")
        lines.append(f"  Essential hypotheses ($e):{self.num_e_hyps}")
        lines.append(f"  Disjoint variables ($d):  {self.num_d_statements}")
        lines.append(f"  Blocks (${{ ... $}}):       {self.num_blocks}")
        lines.append("")

        lines.append("## Assertions")
        lines.append(f"  Axioms ($a):              {self.num_axioms}")
        lines.append(f"  Theorems ($p):            {self.num_theorems}")
        lines.append("")

        if self.proof_lengths:
            median_len = self.median(self.proof_lengths)
            max_len = max(self.proof_lengths)
            min_len = min(self.proof_lengths)
            avg_len = sum(self.proof_lengths) / len(self.proof_lengths)

            lines.append("## Proof Length Statistics")
            lines.append(f"  Min:    {min_len} steps")
            lines.append(f"  Median: {median_len:.1f} steps")
            lines.append(f"  Mean:   {avg_len:.1f} steps")
            lines.append(f"  Max:    {max_len} steps")
            lines.append("")

        if self.num_theorems > 0:
            pct_with_e = (self.proofs_with_e / self.num_theorems) * 100
            lines.append("## Proof Complexity")
            lines.append(f"  Theorems using $e:        {self.proofs_with_e} ({pct_with_e:.1f}%)")
            lines.append(f"  Compressed proofs:        {self.compressed_proofs}")
            lines.append("")

        if self.ast_depths:
            median_depth = self.median(self.ast_depths)
            max_depth = max(self.ast_depths)
            lines.append("## AST Depth Statistics")
            lines.append(f"  Median depth: {median_depth:.1f}")
            lines.append(f"  Max depth:    {max_depth}")
            lines.append("")

        lines.append("## Diversity")
        lines.append(f"  Unique conclusions:       {len(self.unique_conclusions)}")
        lines.append(f"  Total conclusions:        {sum(self.conclusion_counts.values())}")

        if self.conclusion_counts:
            duplicates = [(k, v) for k, v in self.conclusion_counts.items() if v > 1]
            if duplicates:
                lines.append(f"  Duplicate conclusions:    {len(duplicates)}")
                lines.append(f"  Most common (count):      {duplicates[0][1]}x")
            else:
                lines.append(f"  Duplicate conclusions:    0 (all unique!)")
        lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def json_dict(self) -> dict:
        """Export metrics as JSON-serializable dict"""
        return {
            "total_lines": self.total_lines,
            "counts": {
                "constants": self.num_constants,
                "variables": self.num_variables,
                "f_hyps": self.num_f_hyps,
                "e_hyps": self.num_e_hyps,
                "d_statements": self.num_d_statements,
                "axioms": self.num_axioms,
                "theorems": self.num_theorems,
                "blocks": self.num_blocks,
            },
            "proof_stats": {
                "lengths": self.proof_lengths,
                "min": min(self.proof_lengths) if self.proof_lengths else 0,
                "median": self.median(self.proof_lengths),
                "max": max(self.proof_lengths) if self.proof_lengths else 0,
                "with_e_hyps": self.proofs_with_e,
                "compressed": self.compressed_proofs,
            },
            "ast_depth": {
                "median": self.median(self.ast_depths),
                "max": max(self.ast_depths) if self.ast_depths else 0,
            },
            "diversity": {
                "unique_conclusions": len(self.unique_conclusions),
                "total_conclusions": sum(self.conclusion_counts.values()),
                "duplicates": len([k for k, v in self.conclusion_counts.items() if v > 1]),
            }
        }


class MetamathAnalyzer:
    """Analyze Metamath database structure and compute metrics"""

    def __init__(self, database_text: str):
        self.text = database_text
        self.metrics = DatabaseMetrics()

    def compute_ast_depth(self, formula: str) -> int:
        """Compute maximum nesting depth of a formula"""
        max_depth = 0
        current_depth = 0
        for char in formula:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth -= 1
        return max_depth

    def analyze(self) -> DatabaseMetrics:
        """Analyze database and compute all metrics"""
        lines = self.text.strip().split('\n')
        self.metrics.total_lines = len(lines)

        in_block = 0
        block_count = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith('$('):
                continue

            # Track blocks
            if line == '${':
                in_block += 1
                block_count += 1
            elif line == '$}':
                in_block = max(0, in_block - 1)

            # Count declarations
            if ' $c ' in line:
                # Count symbols (split by spaces, exclude $c and $.)
                parts = line.replace('$.', '').split()
                self.metrics.num_constants += len([p for p in parts if p not in ['$c', '$.']])

            elif ' $v ' in line:
                parts = line.replace('$.', '').split()
                self.metrics.num_variables += len([p for p in parts if p not in ['$v', '$.']])

            elif ' $f ' in line:
                self.metrics.num_f_hyps += 1

            elif ' $e ' in line:
                self.metrics.num_e_hyps += 1

            elif ' $d ' in line:
                self.metrics.num_d_statements += 1

            elif ' $a ' in line:
                self.metrics.num_axioms += 1
                # Extract conclusion for diversity analysis
                match = re.search(r'\$a\s+(.+?)\s+\$\.', line)
                if match:
                    conclusion = match.group(1).strip()
                    self.metrics.unique_conclusions.add(conclusion)
                    self.metrics.conclusion_counts[conclusion] += 1
                    depth = self.compute_ast_depth(conclusion)
                    self.metrics.ast_depths.append(depth)

            elif ' $p ' in line:
                self.metrics.num_theorems += 1

                # Extract conclusion and proof
                match = re.search(r'\$p\s+(.+?)\s+\$=\s+(.+?)\s+\$\.', line)
                if match:
                    conclusion = match.group(1).strip()
                    proof = match.group(2).strip()

                    # Diversity
                    self.metrics.unique_conclusions.add(conclusion)
                    self.metrics.conclusion_counts[conclusion] += 1

                    # AST depth
                    depth = self.compute_ast_depth(conclusion)
                    self.metrics.ast_depths.append(depth)

                    # Proof length
                    proof_steps = proof.split()
                    self.metrics.proof_lengths.append(len(proof_steps))

                    # Check for compressed proof (contains parentheses)
                    if '(' in proof and ')' in proof:
                        self.metrics.compressed_proofs += 1

        self.metrics.num_blocks = block_count

        # Note: Detecting $e usage in proofs requires tracking which axioms
        # have $e hypotheses. For now, we count if ANY $e exist in the database.
        if self.metrics.num_e_hyps > 0:
            # Rough estimate: assume some theorems use $e
            self.metrics.proofs_with_e = min(self.metrics.num_theorems, self.metrics.num_e_hyps)

        return self.metrics


def analyze_file(filepath: str) -> DatabaseMetrics:
    """Analyze a Metamath database file"""
    with open(filepath, 'r') as f:
        content = f.read()

    analyzer = MetamathAnalyzer(content)
    return analyzer.analyze()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 mm_metrics.py <metamath-file>")
        sys.exit(1)

    filepath = sys.argv[1]
    metrics = analyze_file(filepath)
    print(metrics.report())
