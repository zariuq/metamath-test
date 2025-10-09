"""
Metamath Environment Tracker

Tracks the state of a Metamath database during generation:
- Active constants and variables
- Active hypotheses ($f and $e)
- Disjoint variable constraints ($d)
- Block scoping

This enables CONSTRUCTIVE proof generation: we only generate what's
provable given the current environment.

Design principle: If we track state correctly, every proof we generate
will be valid by construction.
"""

from dataclasses import dataclass, field
from typing import Set, Dict, List, Tuple, Optional


@dataclass
class Hypothesis:
    """A hypothesis ($f or $e statement)"""
    label: str
    type: str  # '$f' or '$e'
    typecode: str  # First symbol (e.g., 'wff', '|-')
    symbols: List[str]  # All symbols in the statement


@dataclass
class Assertion:
    """An assertion ($a or $p statement)"""
    label: str
    type: str  # '$a' or '$p'
    typecode: str
    symbols: List[str]
    f_hyps: List[str]  # Labels of mandatory $f hypotheses
    e_hyps: List[str]  # Labels of mandatory $e hypotheses
    dv_constraints: Set[Tuple[str, str]]  # Disjoint variable pairs


@dataclass
class MMEnv:
    """
    Metamath environment tracker.

    Maintains the state of what's declared and active at any point
    in the database.
    """

    # All labels ever used (to prevent duplicates)
    all_labels: Set[str] = field(default_factory=set)

    # Currently active declarations
    active_consts: Set[str] = field(default_factory=set)
    active_vars: Set[str] = field(default_factory=set)

    # Active hypotheses (label -> Hypothesis)
    active_f_hyps: Dict[str, Hypothesis] = field(default_factory=dict)
    active_e_hyps: Dict[str, Hypothesis] = field(default_factory=dict)

    # Variable typing: var -> typecode (from active $f)
    var_types: Dict[str, str] = field(default_factory=dict)

    # $f declaration order tracking (CRITICAL for proof correctness!)
    # Maps var -> (sequence_number, label)
    f_decl_index: Dict[str, Tuple[int, str]] = field(default_factory=dict)
    _f_seq: int = 0

    # Disjoint variable constraints
    dv_pairs: Set[Tuple[str, str]] = field(default_factory=set)

    # All assertions (for proof generation)
    assertions: Dict[str, Assertion] = field(default_factory=dict)

    # Block stack for scoping
    # Each block records what was added: [("const", "->"), ("var", "ph"), ...]
    block_stack: List[List[Tuple[str, str]]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize with top-level block"""
        self.block_stack.append([])

    # ========================================================================
    # Label Management
    # ========================================================================

    def fresh_label(self, prefix: str = "L") -> str:
        """
        Generate a fresh label that hasn't been used.

        Note: Does NOT add the label to all_labels - that's done
        by the declare methods.
        """
        i = 1
        while f"{prefix}{i}" in self.all_labels:
            i += 1
        label = f"{prefix}{i}"
        return label

    def is_label_available(self, label: str) -> bool:
        """Check if a label is available for use"""
        return label not in self.all_labels

    # ========================================================================
    # Block Management
    # ========================================================================

    def push_block(self):
        """Enter a new block (${ statement)"""
        self.block_stack.append([])

    def pop_block(self):
        """Exit current block ($} statement)"""
        if len(self.block_stack) <= 1:
            raise ValueError("Cannot pop top-level block")

        # Remove all declarations added in this block
        for kind, name in reversed(self.block_stack[-1]):
            if kind == "const":
                self.active_consts.discard(name)
            elif kind == "var":
                self.active_vars.discard(name)
                self.var_types.pop(name, None)
                # Note: We keep f_decl_index entries even when vars go out of scope
                # This preserves global declaration order for any future re-declarations
            elif kind == "f_hyp":
                self.active_f_hyps.pop(name, None)
            elif kind == "e_hyp":
                self.active_e_hyps.pop(name, None)
            elif kind == "dv":
                self.dv_pairs.discard(name)

        self.block_stack.pop()

    # ========================================================================
    # Constant/Variable Declaration
    # ========================================================================

    def declare_const(self, symbol: str):
        """Declare a constant ($c statement)"""
        if symbol in self.active_vars:
            raise ValueError(f"Cannot declare {symbol!r} as constant: already a variable")
        if symbol in self.active_consts:
            return  # Already declared

        self.active_consts.add(symbol)
        self.block_stack[-1].append(("const", symbol))

    def declare_var(self, symbol: str):
        """Declare a variable ($v statement)"""
        if symbol in self.active_consts:
            raise ValueError(f"Cannot declare {symbol!r} as variable: already a constant")
        if symbol in self.active_vars:
            return  # Already declared

        self.active_vars.add(symbol)
        self.block_stack[-1].append(("var", symbol))

    # ========================================================================
    # Hypothesis Declaration
    # ========================================================================

    def declare_f_hyp(self, label: str, typecode: str, var: str):
        """Declare a floating hypothesis ($f statement)"""
        if label in self.all_labels:
            raise ValueError(f"Label {label!r} already used")
        if var not in self.active_vars:
            raise ValueError(f"Variable {var!r} not declared")
        if typecode not in self.active_consts:
            raise ValueError(f"Typecode {typecode!r} not declared as constant")

        # Check for existing $f for this variable
        if var in self.var_types:
            existing_type = self.var_types[var]
            if existing_type != typecode:
                raise ValueError(
                    f"Variable {var!r} already has type {existing_type!r}, "
                    f"cannot change to {typecode!r}"
                )

        hyp = Hypothesis(
            label=label,
            type='$f',
            typecode=typecode,
            symbols=[var]
        )

        self.all_labels.add(label)
        self.active_f_hyps[label] = hyp
        self.var_types[var] = typecode

        # Record $f declaration order (CRITICAL for proof correctness!)
        self.f_decl_index[var] = (self._f_seq, label)
        self._f_seq += 1

        self.block_stack[-1].append(("f_hyp", label))

    def declare_e_hyp(self, label: str, typecode: str, symbols: List[str]):
        """Declare an essential hypothesis ($e statement)"""
        if label in self.all_labels:
            raise ValueError(f"Label {label!r} already used")
        if typecode not in self.active_consts:
            raise ValueError(f"Typecode {typecode!r} not declared as constant")

        # Check all symbols are declared
        for sym in symbols:
            if sym not in self.active_consts and sym not in self.active_vars:
                raise ValueError(f"Symbol {sym!r} not declared")

        hyp = Hypothesis(
            label=label,
            type='$e',
            typecode=typecode,
            symbols=symbols
        )

        self.all_labels.add(label)
        self.active_e_hyps[label] = hyp
        self.block_stack[-1].append(("e_hyp", label))

    # ========================================================================
    # Disjoint Variable Constraints
    # ========================================================================

    def declare_dv(self, var1: str, var2: str):
        """Declare disjoint variable constraint ($d statement)"""
        if var1 not in self.active_vars:
            raise ValueError(f"Variable {var1!r} not declared")
        if var2 not in self.active_vars:
            raise ValueError(f"Variable {var2!r} not declared")
        if var1 == var2:
            raise ValueError(f"Cannot declare variable disjoint from itself: {var1!r}")

        # Store as sorted tuple for consistency
        pair = tuple(sorted((var1, var2)))
        self.dv_pairs.add(pair)
        self.block_stack[-1].append(("dv", pair))

    def are_disjoint(self, var1: str, var2: str) -> bool:
        """Check if two variables are required to be disjoint"""
        pair = tuple(sorted((var1, var2)))
        return pair in self.dv_pairs

    # ========================================================================
    # Assertion Declaration
    # ========================================================================

    def declare_assertion(self, label: str, is_axiom: bool, typecode: str,
                         symbols: List[str]) -> Assertion:
        """
        Declare an assertion ($a or $p statement).

        Captures the current mandatory hypotheses and DV constraints.
        """
        if label in self.all_labels:
            raise ValueError(f"Label {label!r} already used")
        if typecode not in self.active_consts:
            raise ValueError(f"Typecode {typecode!r} not declared as constant")

        # Check all symbols are declared
        for sym in symbols:
            if sym not in self.active_consts and sym not in self.active_vars:
                raise ValueError(f"Symbol {sym!r} not declared")

        # Collect variables used in the statement (unique set)
        vars_in_stmt = set()
        for s in symbols:
            if s in self.active_vars:
                vars_in_stmt.add(s)

        # CRITICAL: Order variables by their $f declaration order in the database
        # This is required by the Metamath spec for proof correctness!
        vars_ordered_by_f_decl = []
        for var in vars_in_stmt:
            if var not in self.f_decl_index:
                raise ValueError(f"No $f hypothesis for variable {var!r}")
            vars_ordered_by_f_decl.append(var)

        # Sort by database $f declaration order
        vars_ordered_by_f_decl.sort(key=lambda v: self.f_decl_index[v][0])

        # Find mandatory $f hypotheses (in database declaration order)
        mandatory_f = []
        for var in vars_ordered_by_f_decl:
            seq, f_label = self.f_decl_index[var]
            # Verify it's still active
            if f_label not in self.active_f_hyps:
                raise ValueError(f"$f hypothesis {f_label!r} for variable {var!r} is not active")
            mandatory_f.append(f_label)

        # All active $e hypotheses are mandatory
        mandatory_e = list(self.active_e_hyps.keys())

        # Collect relevant DV constraints (involving variables in statement)
        relevant_dv = set()
        for v1 in vars_ordered_by_f_decl:
            for v2 in vars_ordered_by_f_decl:
                if v1 < v2:  # Avoid duplicates
                    pair = (v1, v2)
                    if pair in self.dv_pairs:
                        relevant_dv.add(pair)

        assertion = Assertion(
            label=label,
            type='$a' if is_axiom else '$p',
            typecode=typecode,
            symbols=symbols,
            f_hyps=mandatory_f,
            e_hyps=mandatory_e,
            dv_constraints=relevant_dv
        )

        self.all_labels.add(label)
        self.assertions[label] = assertion

        return assertion

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_typed_vars(self, typecode: str) -> List[str]:
        """Get all active variables with given typecode"""
        return [var for var, tc in self.var_types.items() if tc == typecode]

    def get_assertions_by_type(self, typecode: str) -> List[Assertion]:
        """Get all assertions with given typecode"""
        return [a for a in self.assertions.values() if a.typecode == typecode]

    def can_substitute(self, assertion: Assertion) -> bool:
        """
        Check if an assertion can be used (all hypotheses available).

        For constructive proof generation.
        """
        # Check all mandatory $f hypotheses are active
        for f_label in assertion.f_hyps:
            if f_label not in self.active_f_hyps:
                return False

        # Check all mandatory $e hypotheses are active
        for e_label in assertion.e_hyps:
            if e_label not in self.active_e_hyps:
                return False

        return True

    def check_dv_constraints(
        self,
        assertion: Assertion,
        substitution: Dict[str, List[str]]
    ) -> bool:
        """
        Check if a substitution violates disjoint variable constraints.

        Args:
            assertion: The assertion being applied
            substitution: Map from metavariables to substituted expressions

        Returns:
            True if DV constraints are satisfied, False if violated
        """
        # For each DV pair in the assertion
        for var1, var2 in assertion.dv_constraints:
            # Get the substituted expressions
            expr1 = substitution.get(var1, [var1])
            expr2 = substitution.get(var2, [var2])

            # Extract variables from both expressions
            vars1 = {s for s in expr1 if s in self.active_vars}
            vars2 = {s for s in expr2 if s in self.active_vars}

            # Check for overlap
            overlap = vars1 & vars2
            if overlap:
                # DV constraint violated!
                return False

        return True

    def __repr__(self) -> str:
        return (
            f"MMEnv(\n"
            f"  consts={sorted(self.active_consts)},\n"
            f"  vars={sorted(self.active_vars)},\n"
            f"  f_hyps={list(self.active_f_hyps.keys())},\n"
            f"  e_hyps={list(self.active_e_hyps.keys())},\n"
            f"  assertions={list(self.assertions.keys())}\n"
            f")"
        )
