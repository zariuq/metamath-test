$( Minimized test case for syl2anc - tests complex essential hypothesis handling $)
$( Based on hol.mm by Mario Carneiro $)
$( This proof SHOULD verify correctly $)

$c term |- |= ( ) , $.
$v R S T A B $.

tr $f term R $.
ts $f term S $.
tt $f term T $.
ta $f term A $.
tb $f term B $.

$( Syntax: context pair $)
kct $a term ( A , B ) $.

$( Axioms with essential hypotheses $)
${
  ax-syl.1 $e |- R |= S $.
  ax-syl.2 $e |- S |= T $.
  ax-syl $a |- R |= T $.
$}

${
  ax-jca.1 $e |- R |= S $.
  ax-jca.2 $e |- R |= T $.
  ax-jca $a |- R |= ( S , T ) $.
$}

$( Derived theorems $)
${
  syl.1 $e |- R |= S $.
  syl.2 $e |- S |= T $.
  syl $p |- R |= T $=
    tr ts tt syl.1 syl.2 ax-syl $.
$}

${
  jca.1 $e |- R |= S $.
  jca.2 $e |- R |= T $.
  jca $p |- R |= ( S , T ) $=
    tr ts tt jca.1 jca.2 ax-jca $.
$}

${
  syl2anc.1 $e |- R |= S $.
  syl2anc.2 $e |- R |= T $.
  syl2anc.3 $e |- ( S , T ) |= A $.
  syl2anc $p |- R |= A $=
    tr ts tt kct ta tr ts tt syl2anc.1 syl2anc.2 jca syl2anc.3 syl $.
$}
