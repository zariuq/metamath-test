$( Unit Test 43: Path canonicalization - same file via different paths $)
$( Category: OPTIONAL - Both behaviors are spec-compliant $)
$( $)
$( Spec §4.1.2: "may assume that file names with different strings refer to $)
$( different files for the purpose of ignoring later references" $)
$( $)
$( Valid behaviors: $)
$( 1. String-based dedup: REJECT (duplicate labels from second include) $)
$( 2. Path canonicalization: PASS (second include ignored as same file) $)
$( $)
$( This test documents path canonicalization as a policy/extension, not required $)

$c wff |- $.

$( First include - direct relative path $)
$[ ./helpers/test43_include_canonical_shared.mm $]

$( Second include - convoluted path to same file $)
$( ./subdir/../test43_include_canonical_shared.mm resolves to same file $)
$[ ./subdir/../helpers/test43_include_canonical_shared.mm $]

$( Use declarations - should work (file included once) $)
th1 $p |- var-canon $= fcanon ax-canon $.
