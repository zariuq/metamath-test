$( Unit Test 40: Include inside block $)
$( Should reject: True - include must be at outermost level $)
$( Category: CORE - Strict include semantics $)
$( Spec Section 4.1.2: Include directives processed at outermost level only $)

$c wff |- $.
$v x $.
wx $f wff x $.
ax-x $a |- x $.

${
  $( Include inside block $)
  $[ ./helpers/test40_helper.mm $]

  $( Use included axiom INSIDE the block - this should work $)
  th1 $p |- y $= wy ax-inner $.
$}

$( Outside the block, only x is available $)
th2 $p |- x $= wx ax-x $.
