$( Unit Test 47b: $c declaration directly in inner scope $)
$( Category: CORE - CRITICAL scoping test $)
$( Should reject: True - $c must be in outermost block $)
$( Spec Section 4.1.2 L1088: "All $c statements must be placed in the outermost block" $)

$c wff |- $.

${
  $( INVALID: $c declaration inside block - must be in outermost scope only $)
  $c inner-const $.

  $v x $.
  wx $f wff x $.
  ax-x $a |- x $.
$}
