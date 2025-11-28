$( Minimal test for nested scope bug - inner $e should not leak to outer scope $)

$c term |- |= $.
$v R S T $.

tr $f term R $.
ts $f term S $.
tt $f term T $.

${
  outer.1 $e |- R |= S $.      $( outer scope essential hyp $)

  ${
    inner.1 $e |- S |= T $.    $( inner scope essential hyp - should NOT leak $)

    $( inner proof uses both outer.1 and inner.1: 2 ehyps $)
    inner-thm $a |- R |= T $.
  $}

  $( outer-thm should only see outer.1, NOT inner.1: 1 ehyp $)
  $( If inner.1 leaks, this will fail with "needs 2 ehyps but only 1 on stack" $)
  outer-thm $a |- R |= S $.
$}
