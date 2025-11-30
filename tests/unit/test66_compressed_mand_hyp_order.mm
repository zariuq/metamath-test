$( Unit Test 66: Compressed proof - mandatory hypothesis ordering $)
$( Tests: Mandatory hyps are f-hyps (in order) + e-hyps (in order) $)
$( Should accept: True $)

$c wff |- $.
$v ph ps $.
wp $f wff ph $.
wq $f wff ps $.

${
  $( Axiom with 2 essential hyps $)
  min.1 $e |- ph $.
  min.2 $e |- ps $.
  ax-min $a |- ph $.
$}

${
  $( Proof using compressed format $)
  $( Mandatory hyps: wp(A), wq(B), th.1(C), th.2(D). Label list: E=ax-min $)
  th.1 $e |- ph $.
  th.2 $e |- ps $.
  th $p |- ph $= ( ax-min ) ABCDE $.
$}
