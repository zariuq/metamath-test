$( test60_empty_block.mm - ACCEPT
   Tests EBNF: block ::= '${' stmt* '$}'
   Zero statements in a block is valid.

   Empty blocks between valid proofs should be accepted.
$)

$c wff |- $.
$v p q $.
wp $f wff p $.
wq $f wff q $.

$( First proof $)
th1 $a wff p $.

$( Empty block - should be valid $)
${ $}

$( Another proof after empty block $)
th2 $a wff q $.

$( Nested empty blocks $)
${
  ${ $}
  ${ $}
$}

$( Final proof $)
th3 $p wff p $= wp $.
