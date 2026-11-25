#!/bin/bash
# Vergleicht die Protokolle von A und B bis zur kleineren erreichten Runde (ENDE- und W-Zeilen ausgenommen).
set -euo pipefail
a=$1; b=$2
ra=$(awk '$1=="ENDE"||($1=="HALT"){print ($1=="ENDE")?$2:$3}' "$a" | tail -n 1)
rb=$(awk '$1=="ENDE"||($1=="HALT"){print ($1=="ENDE")?$2:$3}' "$b" | tail -n 1)
r=$(( ra < rb ? ra : rb ))
echo "A bis Runde $ra, B bis Runde $rb, Vergleich bis Runde $r"
sel() { grep -E '^(K |Z |E |H )|^HALT 111 [0-9]+ [0-9]+$' "$1" | awk -v r="$r" '{x=($1=="HALT")?$3:$2; if (x+0 <= r) print}'; }
sel "$a" > va.txt; sel "$b" > vb.txt
if cmp va.txt vb.txt; then echo "GLEICH: $(wc -l < va.txt) Zeilen (davon H: $(grep -c '^H ' va.txt), K: $(grep -c '^K ' va.txt || true), Z: $(grep -c '^Z ' va.txt || true), E: $(grep -c '^E ' va.txt || true))"
else echo "ABWEICHUNG"; diff va.txt vb.txt | head -n 20; exit 1; fi
