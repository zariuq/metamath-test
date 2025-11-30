$( Minimal DV test suite for metamath-knife.
   Mirrors MeTTa tests 5, 6, and 8 from the DV suite. $)

$( -------------------- Basic setup -------------------- $)

$c wff ( ) = dvpair chain fwd $.

$v x y z w ph ps ch $.

$( Type declarations: everything is a wff just to satisfy Metamath. $)
vx   $f wff x $.
vy   $f wff y $.
vz   $f wff z $.
vw   $f wff w $.
vph  $f wff ph $.
vps  $f wff ps $.
vch  $f wff ch $.

$( =====================================================
   Test 5 (nested-good.metta - ACTUALLY SHOULD FAIL!)
   ax-dv(x=y, z=w) with {x,y} intersect {z,w} = empty
   SHOULD FAIL - no $d declarations for cross-pairs like (x,z)
   The axiom $d ph ps requires ALL vars in ph to be disjoint from ALL vars in ps
   ===================================================== $)

$d ph ps $.
ax-dv $a wff dvpair ph ps $.

dv5_nested_bad $p wff dvpair ( x = y ) ( z = w ) $=
  vx vy vz vw ax-dv
$.

$( =====================================================
   Test 6 (transitive.metta)
   Constraints: ph != ps AND ps != ch
   Instance: ax-chain(x=y, x=z, w)
   First two args share x -> SHOULD FAIL (DV violation)
   ===================================================== $)

$d ph ps $.
$d ps ch $.
ax-chain $a wff chain ph ps ch $.

dv6_transitive_bad $p wff chain ( x = y ) ( x = z ) w $=
  ax-chain
$.

$( =====================================================
   Test 8 (symmetric.metta)
   DV: ph != ps, but pair should be treated as unordered
   ax-forward(ph, ph) and ax-forward(ps, ps) both
   substitute same-var expressions into both slots
   both SHOULD FAIL
   ===================================================== $)

$d ph ps $.
ax-forward $a wff fwd ph ps $.

dv8_sym_bad1 $p wff fwd ph ph $=
  ax-forward
$.

dv8_sym_bad2 $p wff fwd ps ps $=
  ax-forward
$.
