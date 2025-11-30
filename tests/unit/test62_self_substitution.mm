$( test62_self_substitution.mm - ACCEPT
   Tests spec 4.1.4 L204-205:
   "It is acceptable for a variable to be mapped to an expression
   containing it."

   This tests that p can be substituted with an expression containing p.
$)

$c wff |- ( ) -> $.
$v p q $.
wp $f wff p $.
wq $f wff q $.

$( Build implication: wff ( p -> q ) $)
wi $a wff ( p -> q ) $.

$( Axiom: |- ( p -> p )
   Mandatory hypothesis: just wp (only var p is used) $)
ax-id $a |- ( p -> p ) $.

$( Prove ( ( p -> p ) -> ( p -> p ) )
   We apply ax-id with p := ( p -> p )
   This means p maps to an expression containing p itself!

   ax-id needs: wp
   We need to push wff ( p -> p ) to substitute for p.
   Building wff ( p -> p ): wp wp wi (gives wff ( p -> p ))
   Then apply ax-id.
$)
th-self $p |- ( ( p -> p ) -> ( p -> p ) ) $=
  wp wp wi ax-id $.
