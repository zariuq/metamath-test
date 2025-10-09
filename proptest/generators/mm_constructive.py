"""
Constructive Metamath Database Generator

Generates valid Metamath databases by CONSTRUCTION, not by proof search.

Key insight: Instead of trying to prove a theorem, we:
1. Start with axioms and hypotheses
2. Apply valid proof steps (substitution)
3. Whatever we build IS the theorem!

This guarantees every proof verifies because it's built correctly from the start.

Example:
  Have: ax1 $a |- ( ph -> ( ps -> ph ) )
  Have: wph $f wff ph
  Have: wps $f wff ps

  Apply ax1 → Stack contains: |- ( ph -> ( ps -> ph ) )
  Stop and declare: "I just proved this!"

  th1 $p |- ( ph -> ( ps -> ph ) ) $= wph wps ax1 $.

  This WILL verify!
"""

import random
from typing import List, Tuple, Set, Optional, Dict
from .mm_env import MMEnv, Assertion, Hypothesis


class MMSubstitution:
    """Handle Metamath substitutions"""

    @staticmethod
    def apply_substitution(symbols: List[str], subst: Dict[str, List[str]]) -> List[str]:
        """
        Apply a substitution to a list of symbols.

        Args:
            symbols: Original symbol list
            subst: Mapping from variables to replacement symbol lists

        Returns:
            Symbols with substitution applied
        """
        result = []
        for sym in symbols:
            if sym in subst:
                result.extend(subst[sym])
            else:
                result.append(sym)
        return result

    @staticmethod
    def find_variables(symbols: List[str], env: MMEnv) -> Set[str]:
        """Find all variables in a symbol list"""
        return {s for s in symbols if s in env.active_vars}

    @staticmethod
    def generate_random_substitution(
        vars_needed: Set[str],
        env: MMEnv,
        max_depth: int = 2
    ) -> Dict[str, List[str]]:
        """
        Generate a random valid substitution for variables.

        Args:
            vars_needed: Variables that need substitution
            env: Current environment
            max_depth: Max depth of generated expressions

        Returns:
            Substitution mapping
        """
        subst = {}

        for var in vars_needed:
            # Get typecode for this variable
            if var not in env.var_types:
                continue

            typecode = env.var_types[var]

            # For now, substitute with a simple variable or constant
            # Could be enhanced to generate complex expressions
            if random.random() < 0.7:
                # Substitute with another variable of same type
                same_type_vars = env.get_typed_vars(typecode)
                if same_type_vars:
                    subst[var] = [random.choice(same_type_vars)]
                else:
                    subst[var] = [var]  # Identity substitution
            else:
                # Substitute with constant (if any exist for this type)
                # For now, just use identity
                subst[var] = [var]

        return subst


class MMConstructiveGenerator:
    """
    Generate valid Metamath databases constructively.

    Strategy:
    1. Declare basic constants and variables
    2. Add typing hypotheses ($f)
    3. Add axioms ($a)
    4. Constructively build proofs by applying axioms
    """

    def __init__(self, seed: Optional[int] = None):
        self.env = MMEnv()
        self.output = []
        self.rng = random.Random(seed)

        # Novelty tracking - prevent duplicate conclusions
        self.conclusion_counts = {}  # conclusion_str -> count
        self.boring_budget = 5  # Max times we allow same conclusion

    # ========================================================================
    # Symbol Generation
    # ========================================================================

    def gen_const(self, prefix: str = "c") -> str:
        """Generate a fresh constant symbol"""
        i = 1
        while True:
            sym = f"{prefix}{i}" if len(prefix) > 0 else str(i)
            if sym not in self.env.active_consts and sym not in self.env.active_vars:
                return sym
            i += 1

    def gen_var(self, prefix: str = "v") -> str:
        """Generate a fresh variable symbol"""
        i = len([v for v in self.env.active_vars if v.startswith(prefix)]) + 1
        while True:
            sym = f"{prefix}{i}"
            if sym not in self.env.active_vars and sym not in self.env.active_consts:
                return sym
            i += 1

    # ========================================================================
    # Output Methods
    # ========================================================================

    def emit(self, line: str):
        """Add a line to output"""
        self.output.append(line + "\n")

    def emit_comment(self, text: str):
        """Add a comment"""
        self.emit(f"$( {text} $)")

    def is_novel_enough(self, conclusion: List[str]) -> bool:
        """Check if a conclusion is novel enough to include"""
        conclusion_str = " ".join(conclusion)
        count = self.conclusion_counts.get(conclusion_str, 0)
        return count < self.boring_budget

    def record_conclusion(self, conclusion: List[str]):
        """Record that we used this conclusion"""
        conclusion_str = " ".join(conclusion)
        self.conclusion_counts[conclusion_str] = self.conclusion_counts.get(conclusion_str, 0) + 1

    # ========================================================================
    # Database Generation
    # ========================================================================

    def generate_header(self):
        """Generate standard Metamath header"""
        self.emit_comment("Generated Metamath database with constructive proofs")
        self.emit_comment("Every proof verifies by construction!")
        self.emit("")

        # Declare basic typecodes
        self.emit("$c wff |- $.")
        self.env.declare_const("wff")
        self.env.declare_const("|-")

        # Declare basic logical constants
        for const in ["->", "(", ")"]:
            self.emit(f"$c {const} $.")
            self.env.declare_const(const)

        self.emit("")

    def generate_variables(self, count: int = 3):
        """Generate and declare variables"""
        self.emit_comment(f"Declare {count} variables")

        for _ in range(count):
            var = self.gen_var("ph")
            self.emit(f"$v {var} $.")
            self.env.declare_var(var)

        self.emit("")

    def generate_f_hypotheses(self):
        """Generate $f hypotheses for all active variables"""
        self.emit_comment("Type all variables as wff")

        for var in sorted(self.env.active_vars):
            if var not in self.env.var_types:
                label = self.env.fresh_label("wf")
                self.emit(f"{label} $f wff {var} $.")
                self.env.declare_f_hyp(label, "wff", var)

        self.emit("")

    def generate_axiom_simple(self, name: Optional[str] = None) -> str:
        """
        Generate a simple axiom using active variables.

        Example: |- ( ph1 -> ph1 )
        """
        label = name or self.env.fresh_label("ax")

        # Get typed variables
        wff_vars = self.env.get_typed_vars("wff")
        if not wff_vars:
            raise ValueError("No wff variables available")

        # Simple self-implication - include parens in symbols!
        var = self.rng.choice(wff_vars)
        symbols = ["(", var, "->", var, ")"]

        self.emit(f"{label} $a |- {' '.join(symbols)} $.")
        self.env.declare_assertion(label, is_axiom=True, typecode="|-", symbols=symbols)

        return label

    def generate_axiom_implication(self, name: Optional[str] = None) -> str:
        """
        Generate implication axiom.

        Example: |- ( ph -> ( ps -> ph ) )
        """
        label = name or self.env.fresh_label("ax")

        wff_vars = self.env.get_typed_vars("wff")
        if len(wff_vars) < 2:
            # Fall back to simple axiom
            return self.generate_axiom_simple(label)

        var1, var2 = self.rng.sample(wff_vars, 2)
        symbols = ["(", var1, "->", "(", var2, "->", var1, ")", ")"]

        self.emit(f"{label} $a |- {' '.join(symbols)} $.")
        self.env.declare_assertion(label, is_axiom=True, typecode="|-", symbols=symbols)

        return label

    def generate_axiom_modus_ponens(self, name: Optional[str] = None) -> str:
        """
        Generate modus ponens axiom with essential hypotheses IN A BLOCK.

        Example:
          ${
            min $e |- ph $.
            maj $e |- ( ph -> ps ) $.
            ax-mp $a |- ps $.
          $}

        This creates an axiom that requires $e hypotheses!
        The block ensures the $e hypotheses don't leak to later axioms.
        """
        label = name or self.env.fresh_label("ax")

        wff_vars = self.env.get_typed_vars("wff")
        if len(wff_vars) < 2:
            # Need at least 2 variables
            return self.generate_axiom_simple(label)

        var1, var2 = self.rng.sample(wff_vars, 2)

        # Open a block to scope the $e hypotheses
        self.emit("${")
        self.env.push_block()

        # Create $e hypotheses
        min_label = self.env.fresh_label("min")
        maj_label = self.env.fresh_label("maj")

        self.emit(f"  {min_label} $e |- {var1} $.")
        self.env.declare_e_hyp(min_label, "|-", [var1])

        self.emit(f"  {maj_label} $e |- ( {var1} -> {var2} ) $.")
        self.env.declare_e_hyp(maj_label, "|-", ["(", var1, "->", var2, ")"])

        # Create axiom that uses these $e
        self.emit(f"  {label} $a |- {var2} $.")
        self.env.declare_assertion(label, is_axiom=True, typecode="|-", symbols=[var2])

        # Close the block - this removes min/maj from active $e
        self.emit("$}")
        self.env.pop_block()

        return label

    def generate_proof_by_axiom(self, axiom_label: str) -> Optional[str]:
        """
        Generate a $p statement that just applies an axiom.

        This is constructive: we apply the axiom, whatever it produces
        becomes our theorem!

        Returns theorem label, or None if conclusion is too boring (duplicate).
        """
        axiom = self.env.assertions.get(axiom_label)
        if not axiom:
            raise ValueError(f"Axiom {axiom_label!r} not found")

        # The conclusion is exactly what the axiom produces
        conclusion = axiom.symbols

        # Check novelty
        if not self.is_novel_enough(conclusion):
            return None  # Too boring, skip it

        label = self.env.fresh_label("th")

        # The proof is: mandatory $f hyps (in database declaration order) + axiom
        # mm_env.py now ensures f_hyps are ordered correctly by $f declaration sequence
        proof_steps = axiom.f_hyps + [axiom_label]

        # Format conclusion exactly as axiom has it
        self.emit(
            f"{label} $p {axiom.typecode} {' '.join(conclusion)} $= "
            f"{' '.join(proof_steps)} $."
        )

        self.env.declare_assertion(
            label, is_axiom=False, typecode=axiom.typecode, symbols=conclusion
        )

        # Record this conclusion
        self.record_conclusion(conclusion)

        return label

    def generate_proof_with_mp(self, mp_label: str) -> Optional[str]:
        """
        Generate a multi-step proof using modus ponens.

        This creates a proof that:
        1. Proves the minor premise using an available axiom
        2. Proves the major premise using an available axiom
        3. Applies modus ponens

        Returns the label of the generated theorem, or None if MP not available.
        """
        mp = self.env.assertions.get(mp_label)
        if not mp or len(mp.e_hyps) != 2:
            return None  # Not a valid MP axiom

        # MP needs two $e hypotheses
        # Find what they are
        min_hyp_label = mp.e_hyps[0]
        maj_hyp_label = mp.e_hyps[1]

        min_hyp = self.env.active_e_hyps.get(min_hyp_label)
        maj_hyp = self.env.active_e_hyps.get(maj_hyp_label)

        if not min_hyp or not maj_hyp:
            return None

        # Find axioms that can prove these hypotheses
        # For simplicity, look for exact matches in existing assertions
        min_proof = None
        maj_proof = None

        for ax_label, ax in self.env.assertions.items():
            if ax.symbols == min_hyp.symbols and not ax.e_hyps:
                min_proof = ax_label
            if ax.symbols == maj_hyp.symbols and not ax.e_hyps:
                maj_proof = ax_label

        if not min_proof or not maj_proof:
            return None  # Can't prove prerequisites

        # Build the proof
        label = self.env.fresh_label("th")

        # Proof steps:
        # 1. All $f for variables in min premise
        # 2. Axiom that proves min premise
        # 3. All $f for variables in maj premise
        # 4. Axiom that proves maj premise
        # 5. MP axiom

        min_ax = self.env.assertions[min_proof]
        maj_ax = self.env.assertions[maj_proof]

        proof_steps = []
        # f_hyps are already in correct database declaration order from mm_env.py
        proof_steps.extend(min_ax.f_hyps)
        proof_steps.append(min_proof)
        proof_steps.extend(maj_ax.f_hyps)
        proof_steps.append(maj_proof)
        proof_steps.append(mp_label)

        # Conclusion is what MP produces
        conclusion = mp.symbols

        self.emit(
            f"{label} $p {mp.typecode} {' '.join(conclusion)} $= "
            f"{' '.join(proof_steps)} $."
        )

        self.env.declare_assertion(
            label, is_axiom=False, typecode=mp.typecode, symbols=conclusion
        )

        return label

    def generate_proof_with_substitution(
        self,
        axiom_label: str,
        subst: Optional[Dict[str, List[str]]] = None
    ) -> Optional[str]:
        """
        Generate a $p statement by applying an axiom with substitution.

        Args:
            axiom_label: Axiom to apply
            subst: Substitution to use (or generate random if None)

        Returns:
            Label of generated theorem, or None if substitution invalid
        """
        axiom = self.env.assertions.get(axiom_label)
        if not axiom:
            return None

        # Find variables in axiom
        vars_in_axiom = MMSubstitution.find_variables(axiom.symbols, self.env)

        # Generate substitution if not provided
        if subst is None:
            subst = MMSubstitution.generate_random_substitution(
                vars_in_axiom, self.env
            )

        # Apply substitution to conclusion
        conclusion = MMSubstitution.apply_substitution(axiom.symbols, subst)

        # Build proof: substituted $f hyps + axiom
        proof_steps = []

        # For each mandatory $f hypothesis, apply substitution
        for f_label in axiom.f_hyps:
            f_hyp = self.env.active_f_hyps.get(f_label)
            if not f_hyp:
                return None  # Hypothesis not active

            var = f_hyp.symbols[0]
            if var in subst:
                # Need $f for substituted variable
                subst_vars = subst[var]
                if len(subst_vars) == 1 and subst_vars[0] in self.env.var_types:
                    # Find $f for this variable
                    for lbl, hyp in self.env.active_f_hyps.items():
                        if hyp.symbols[0] == subst_vars[0]:
                            proof_steps.append(lbl)
                            break
                else:
                    # Complex substitution - skip for now
                    return None
            else:
                proof_steps.append(f_label)

        proof_steps.append(axiom_label)

        label = self.env.fresh_label("th")

        self.emit(
            f"{label} $p {axiom.typecode} {' '.join(conclusion)} $= "
            f"{' '.join(proof_steps)} $."
        )

        self.env.declare_assertion(
            label, is_axiom=False, typecode=axiom.typecode, symbols=conclusion
        )

        return label

    # ========================================================================
    # Main Generation
    # ========================================================================

    def generate_database(self, target_lines: int = 100) -> str:
        """
        Generate a complete, valid Metamath database.

        Args:
            target_lines: Approximate number of output lines

        Returns:
            Complete Metamath database as string
        """
        self.generate_header()
        self.generate_variables(count=3)
        self.generate_f_hypotheses()

        self.emit_comment("Axioms")
        axioms = []
        mp_axiom = None

        # Start with basic axioms
        axioms.append(self.generate_axiom_simple("ax-id"))
        axioms.append(self.generate_axiom_implication("ax-1"))

        # Add modus ponens with $e hypotheses
        mp_axiom = self.generate_axiom_modus_ponens("ax-mp")
        axioms.append(mp_axiom)

        self.emit("")

        self.emit_comment("Theorems (generated constructively)")

        # Generate theorems until we hit target
        attempts = 0
        max_attempts = target_lines * 3  # Prevent infinite loops

        while len(self.output) < target_lines and attempts < max_attempts:
            attempts += 1
            choice = self.rng.random()

            if choice < 0.3 and mp_axiom:
                # Try to generate a multi-step proof using MP
                result = self.generate_proof_with_mp(mp_axiom)
                if not result:
                    # Fall back to simple proof
                    if axioms:
                        axiom = self.rng.choice([a for a in axioms if a != mp_axiom])
                        self.generate_proof_by_axiom(axiom)

            elif choice < 0.6 and axioms:
                # Simple proof: just apply an axiom
                # Skip mp_axiom since it requires $e hypotheses
                non_mp_axioms = [a for a in axioms if a != mp_axiom]
                if non_mp_axioms:
                    axiom = self.rng.choice(non_mp_axioms)
                    self.generate_proof_by_axiom(axiom)  # May return None if too boring

            else:
                # Add another variable and axiom to increase diversity
                if len(self.output) < target_lines - 10:
                    var = self.gen_var("ps")
                    self.emit(f"$v {var} $.")
                    self.env.declare_var(var)

                    label = self.env.fresh_label("wf")
                    self.emit(f"{label} $f wff {var} $.")
                    self.env.declare_f_hyp(label, "wff", var)

                    # Sometimes create simple axiom, sometimes implication
                    if self.rng.random() < 0.5:
                        new_axiom = self.generate_axiom_simple()
                    else:
                        new_axiom = self.generate_axiom_implication()
                    axioms.append(new_axiom)

        return "".join(self.output)


# ============================================================================
# Convenience Function
# ============================================================================

def generate_valid_metamath(lines: int = 100, seed: Optional[int] = None) -> str:
    """
    Generate a valid Metamath database with constructive proofs.

    Args:
        lines: Approximate number of lines to generate
        seed: Random seed for reproducibility

    Returns:
        Complete Metamath database as string

    Example:
        db = generate_valid_metamath(lines=100, seed=42)
        # This database will pass metamath.exe verification!
    """
    gen = MMConstructiveGenerator(seed=seed)
    return gen.generate_database(target_lines=lines)


if __name__ == "__main__":
    # Test generation
    print("Generating 50-line Metamath database...")
    db = generate_valid_metamath(lines=50, seed=42)
    print(db)
    print(f"\nGenerated {len(db.splitlines())} lines")
