$( test64_multiple_ehyp_order.mm - ACCEPT
   Tests spec 4.1.4 L182-184, L211-214:
   "The (possibly empty) set of mandatory hypotheses is the set of all
   active $f statements containing mandatory variables, together with
   all active $e statements."

   "causes them to match the topmost entries of the stack, in order of
   occurrence of the mandatory hypotheses"

   Key insight: mandatory hypotheses = $f (for mandatory vars) + $e (all active)
   in order of OCCURRENCE in the file.
$)

$c wff |- ( ) -> $.
$v p q $.
wp $f wff p $.
wq $f wff q $.

$( Build implication $)
wi $a wff ( p -> q ) $.

$( A theorem with two essential hypotheses.
   Mandatory hyps in occurrence order: wp, wq, e1, e2 $)
${
  e1 $e |- p $.
  e2 $e |- ( p -> q ) $.
  $( Modus ponens: from p and p->q, derive q $)
  mp $a |- q $.
$}

$( Use mp with concrete values.
   To apply mp where p:=( p -> p ), q:=( p -> p ):
   Push order: wp (for p), wp (for q), inst of e1, inst of e2

   We'll prove: from ( p -> p ) and ( ( p -> p ) -> ( p -> p ) ), get ( p -> p )
$)

${
  h1 $e |- ( p -> p ) $.
  h2 $e |- ( ( p -> p ) -> ( p -> p ) ) $.

  $( Stack for mp: wp wp wi, wp wp wi, h1, h2
     This substitutes p:=( p -> p ), q:=( p -> p ) $)
  result $p |- ( p -> p ) $=
    wp wp wi wp wp wi h1 h2 mp $.
$}
