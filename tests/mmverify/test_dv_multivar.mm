$( Test for multi-variable $d declarations.
   $d p y z $. should generate ALL pairs: (p,y), (p,z), AND (y,z)
   This is the compact form - equivalent to:
     $d p y $.
     $d p z $.
     $d y z $.
$)

$c wff three $.
$v ph ps ch p y z $.

vph $f wff ph $.
vps $f wff ps $.
vch $f wff ch $.
vp $f wff p $.
vy $f wff y $.
vz $f wff z $.

${
  $d ph ps $.
  $d ph ch $.
  $d ps ch $.
  ax-3way $a wff three ph ps ch $.
$}

$( Multi-variable $d: should declare ALL pairs disjoint $)
$d p y z $.

$( This should PASS: p, y, z are all mutually disjoint via the single $d p y z $. $)
test_multivar_good $p wff three p y z $=
  vp vy vz ax-3way
$.
