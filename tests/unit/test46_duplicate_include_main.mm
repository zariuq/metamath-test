$( Unit Test 46: Duplicate include in different inner blocks $)
$( Should reject: True - includes must be at outermost level $)
$( Category: CORE - Strict include semantics $)
$( Spec Section 4.1.2: Include directives processed at outermost level only $)

$c wff |- $.

${
  $( First include: processes the file $)
  $[ ./helpers/test46_helper.mm $]

  $( Use the included content $)
  th1 $p |- y $= wy ax-y $.
$}

${
  $( Second include: should be ignored as whitespace $)
  $[ ./helpers/test46_helper.mm $]

  $( This would fail if file processed twice (y redeclared) $)
  $( But since second include ignored, ax-y and wy are still available globally $)
  th2 $p |- y $= wy ax-y $.
$}
