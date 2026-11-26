#!/bin/bash
# Vergleich X gegen B (Workflow lauf_muster). Aufruf: vergleich.sh <ordner_x> <ordner_b>
set -u
X="$1/x_ohne_w.txt.gz"; B="$2/b.txt.gz"
cd "$(dirname "$0")"; X="../../../$X"; B="../../../$B"
ls -la "$X" "$B" || exit 1
rx=$(zcat "$X" | awk '$1=="ENDE"{print $2}'); rb=$(zcat "$B" | awk '$1=="ENDE"{print $2}')
n=$(( rx < rb ? rx : rb )); echo "X bis Runde $rx, B bis Runde $rb, Vergleich bis $n"
zcat "$X" | awk -v n="$n" '($1=="A"||$1=="H") && $2<=n' > vx.txt
zcat "$B" | awk -v n="$n" '($1=="A"||$1=="H") && $2<=n' > vb.txt
echo "A- und H-Zeilen: X $(wc -l < vx.txt), B $(wc -l < vb.txt)"
if cmp -s vx.txt vb.txt; then echo "A+H GLEICH"; else echo "A+H VERSCHIEDEN"; cmp vx.txt vb.txt | head -3; fi
echo "Junk in X (J): $(zcat "$X" | awk -v n="$n" '$1=="J" && $2<=n{printf "%s ", $2}')"
echo "11 im Wort in B (E, Runde): $(zcat "$B" | awk -v n="$n" '$1=="E" && $2<=n{printf "%s ", $2}')"
echo "E-Zeilen B im Detail:"; zcat "$B" | awk -v n="$n" '$1=="E" && $2<=n'
echo "== Zweite Auswertung (zweit.c) auf den Daten von B"
gcc -O2 -Wall -o zweit zweit.c && zcat "$B" | awk -v n="$n" '$1=="A" && $2<=n' > ab.txt && ./zweit ab.txt
