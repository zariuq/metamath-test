$( Test for DV pairwise expansion: $d x y z $. should create pairs (x,y), (x,z), (y,z) $)

$c wff |- $.
$v x y z $.

wx $f wff x $.
wy $f wff y $.
wz $f wff z $.

${
  $d x y z $.

  $( Axiom requiring x,y disjoint $)
  ax-xy.1 $e |- x $.
  ax-xy $a |- y $.
$}

${
  $d x y z $.

  $( Axiom requiring x,z disjoint $)
  ax-xz.1 $e |- x $.
  ax-xz $a |- z $.
$}

${
  $d x y z $.

  $( Axiom requiring y,z disjoint - THIS IS THE KEY TEST $)
  ax-yz.1 $e |- y $.
  ax-yz $a |- z $.
$}

$( Test theorem - uses all three DV pairs $)
${
  $d x y z $.
  th.1 $e |- x $.
  th $p |- z $= wx wz th.1 ax-xz $.
$}
