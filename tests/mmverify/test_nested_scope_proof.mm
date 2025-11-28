$( Minimal test for nested scope bug with proofs $)

$c term |- |= $.
$v R S T $.

tr $f term R $.
ts $f term S $.
tt $f term T $.

$( Base axiom - syllogism $)
${
  ax-syl.1 $e |- R |= S $.
  ax-syl.2 $e |- S |= T $.
  ax-syl $a |- R |= T $.
$}

$( Test nested scopes $)
${
  outer.1 $e |- R |= S $.

  ${
    inner.1 $e |- S |= T $.
    $( inner-thm uses ax-syl with outer.1 and inner.1 $)
    inner-thm $p |- R |= T $= tr ts tt outer.1 inner.1 ax-syl $.
  $}

  $( outer-thm should only see outer.1: prove R |= S trivially $)
  $( This is an identity - just return the hypothesis $)
  outer-id $a |- R |= S $.
$}

$( After all scopes close, prove something with fresh hypotheses $)
${
  final.1 $e |- R |= S $.
  final.2 $e |- S |= T $.
  $( Should work: 2 ehyps expected, 2 on stack $)
  final-thm $p |- R |= T $= tr ts tt final.1 final.2 ax-syl $.
$}
