$( Test DVar scope: $d in current scope should satisfy axiom requirements $)

$c wff two $.
$v ph ps a b $.

vph $f wff ph $.
vps $f wff ps $.
va $f wff a $.
vb $f wff b $.

$( Axiom requires ph != ps $)
${
  $d ph ps $.
  ax-two $a wff two ph ps $.
$}

$( Theorem uses a, b - must declare $d a b $. $)
${
  $d a b $.
  test_scope_good $p wff two a b $=
    va vb ax-two
  $.
$}
