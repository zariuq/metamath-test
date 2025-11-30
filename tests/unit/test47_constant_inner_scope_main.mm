$( Unit Test 47: Include directive inside block $)
$( Category: CORE - CRITICAL scoping test $)
$( Should reject: True - include must be in outermost scope $)
$( Spec Section 4.1.2 L105-106: "$[ $] only allowed in outermost scope" $)

$c wff |- $.

${
  $( INVALID: Include inside block - must be in outermost scope only $)
  $[ ./helpers/test47_helper.mm $]

  $( Try to use included declarations $)
  th1 $p |- inner-var $= finner ax-inner $.
$}
