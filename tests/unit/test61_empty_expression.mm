$( test61_empty_expression.mm - ACCEPT
   Tests spec 4.1.3 L153-154, L167-169:
   "$e statement consists of ... zero or more active math symbols"
   "$a statement consists of ... zero or more active math symbols"

   Empty expressions (just typecode, no symbols) should be valid.
$)

$c wff |- $.

$( Axiom with empty expression after typecode $)
ax-empty $a wff $.

$( Essential hypothesis with empty expression $)
${
  $v p $.
  wp $f wff p $.

  $( Empty essential hypothesis $)
  he $e |- $.

  $( Proof that uses the empty e-hyp $)
  th1 $p wff p $= wp $.
$}
