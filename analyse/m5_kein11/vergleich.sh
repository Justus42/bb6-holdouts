#!/bin/bash
# Punkt 3, Zweitpruefung: kein11 (C, fortgeschrieben) gegen naiv (Go, voller Suchlauf je Schritt), gleiche Eingaben.
# Vergleicht ERGEBNIS-Kernwerte (schritte, halt, brueche, erster_bruch, breite) und HASH Zeile fuer Zeile.
K=${K:-/tmp/claude-0/kein11}; G=${G:-/tmp/claude-0/naiv}; N=${N:-2000000}
vgl() {  # Argumente wie kein11/naiv
  a=$($K "$@" | grep -E "^(ERGEBNIS|HASH)" | sed -E 's/TM=[^ ]* seite=. //; s/ maxP=[0-9]+ vollfehler=[0-9]+//')
  b=$($G "$@")
  if [ "$a" == "$b" ]; then echo "GLEICH $* | $(echo $a | tr '\n' ' ')"; else echo "ABWEICHUNG $*"; echo "  C : $a"; echo "  Go: $b"; fi
}
"$@"
