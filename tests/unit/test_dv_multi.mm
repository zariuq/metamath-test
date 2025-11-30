$( Test for multi-variable $d declarations - INVALID PROOF (should be rejected) $)

$c wff |- $.
$v x y z $.

wx $f wff x $.
wy $f wff y $.
wz $f wff z $.

${
  $d x y z $.
  ax $a |- x $.

  ${
    th.1 $e |- y $.
    th $p |- z $= wy wz ax th.1 $.
  $}
$}
