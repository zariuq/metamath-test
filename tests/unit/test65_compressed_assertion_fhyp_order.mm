$( Unit Test 65: Compressed proof with 3-variable axiom $)
$( Tests: Correctly using an axiom with 3 f-hyps in a compressed proof.
   ax-3var has mandatory hyps: wff ph, wff ps, wff ch, |- ph, |- ps
   We prove |- ps by calling ax-3var with substitution ch -> ps
   IMPORTANT: Everything wrapped in outer ${ $} to avoid top-level $e $)
$( Should accept: True $)

$c wff |- $.
$v ph ps ch $.

${
  wp $f wff ph $.
  wq $f wff ps $.
  wc $f wff ch $.

  $( Axiom: from |- ph and |- ps, conclude |- ch $)
  ax.1 $e |- ph $.
  ax.2 $e |- ps $.
  ax-3var $a |- ch $.

  $( Theorem: prove |- ps by using ax-3var with ch -> ps $)
  $( Mandatory hyps of th: wp(A), wq(B), ax.1(C), ax.2(D), th.1(E), th.2(F)
     Note: ax.1 and ax.2 are mandatory because they're used in the proof!
     Label list: (ax-3var) -> G = ax-3var
     Proof: A B B E F G = push wff ph, wff ps, wff ps, |- ph, |- ps, call ax-3var
     ax-3var with {ph->ph, ps->ps, ch->ps} yields |- ps $)
  th.1 $e |- ph $.
  th.2 $e |- ps $.
  th $p |- ps $= ( ax-3var ) ABBEFG $.
$}
