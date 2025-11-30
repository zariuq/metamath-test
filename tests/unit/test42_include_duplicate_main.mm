$( Unit Test 42: Duplicate include - same file twice $)
$( Should reject: False - second include should be ignored $)
$( Spec: First inclusion is processed, subsequent inclusions ignored $)

$c wff |- $.

$( First include - processes the file $)
$[ ./helpers/test42_helper.mm $]

$( Second include - should be ignored (file already seen) $)
$[ ./helpers/test42_helper.mm $]

$( Use declarations from first include $)
th1 $p |- var-dup $= fdup ax-dup $.
