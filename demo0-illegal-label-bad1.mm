$( demo0.mm  1-Jan-04 $)

$(
                      PUBLIC DOMAIN DEDICATION

This file is placed in the public domain per the Creative Commons Public
Domain Dedication. ht\tp://creativecommons.org/licenses/publicdomain/

Norman Megill - email: nm at alum.mit.edu

$)


$( This file is the introductory formal system example described
   in Chapter 2 of the Meamath book. $)

$( Declare the constant symbols we will use $)
    $c 0 + = -> ( ) term wff |- $.
$( Declare the metavariables we will use $)
    $v t r s P Q $.
$( Specify properties of the metavariables $)
    t\t $f term t $.
    tr $f term r $.
    ts $f term s $.
    wp $f wff P $.
    wq $f wff Q $.
$( Define "term" (part 1) $)
    (tze $a term 0 $.
$( Define "term" (part 2) $)
    t)pl $a term ( t + r ) $.
$( Define "wff" (part 1) $)
    w"eq $a wff t = r $.
$( Define "wff" (part 2) $)
    w%i\m $a wff ( P -> Q ) $.
$( State axiom a1 $)
    a1 $a |- ( t = r -> ( t = s -> r = s ) ) $.
$( State axiom 'a2` $)
    'a2` $a |- ( t + 0 ) = t $.
    ${
       min $e |- P $.
       maj $e |- ( P -> Q ) $.
$( Define the modus ponens inference rule $)
       mp  $a |- Q $.
    $}
$( Prove a theorem $)
    th1 $p |- t = t $=
  $( Here is its proof: $)
       t\t (tze t)pl t\t w"eq t\t t\t w"eq t\t 'a2` t\t (tze t)pl
       t\t w"eq t\t (tze t)pl t\t w"eq t\t t\t w"eq w%i\m t\t 'a2`
       t\t (tze t)pl t\t t\t a1 mp mp
     $.

