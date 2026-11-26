#!/bin/bash
# Nachtrag 2, Negativkontrolle: Lauf ab C, bei der Entstehung der ersten stehenden Luecke (Schritt 89.985, Kopf eine
# Zelle links der Luecken-1) wird Zelle 5 links der Luecken-1 (Kopf-4) auf 0 gesetzt. Beide Programme muessen die
# Ankunft in einem anderen Zustand als C melden. Programme in /tmp/claude-0 (gcc -O2 luecke.c; go build zweit/luecke.go).
M5=1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC
for P in /tmp/claude-0/luecke /tmp/claude-0/luecke_go; do
  echo "== $P ohne Stoerung";  $P $M5 200000 --start C | grep -E "^EP|ERGEBNIS"
  echo "== $P mit Stoerung";   $P $M5 200000 --start C --stoer 89985 -4 0 | grep -E "^EP|ERGEBNIS"
done
