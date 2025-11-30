$( Minimal test for compressed proof $)

$c term |- |= $.
$v R S T $.

tR $f term R $.
tS $f term S $.
tT $f term T $.

${
  syl.1 $e |- R |= S $.
  syl.2 $e |- S |= T $.
  ax-syl $a |- R |= T $.
$}

${
  th.1 $e |- R |= S $.
  th.2 $e |- S |= T $.
  $( Uncompressed proof - should work $)
  th $p |- R |= T $= tR tS tT th.1 th.2 ax-syl $.
$}
