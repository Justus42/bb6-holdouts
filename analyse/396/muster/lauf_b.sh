#!/bin/bash
# Zweites Programm (runde_b_anf.cpp = runde_b.cpp aus Teil 2 plus Anfangsfenster) im Workflow lauf_muster.
# Aufruf: lauf_b.sh <sekunden>
set -u
cd "$(dirname "$0")"
S="$1"
mkdir -p aus_b
g++ -O2 -Wall -o runde_b_anf runde_b_anf.cpp
start=$(date +%s)
ANF=1 ./runde_b_anf 5000000 "$S" > aus_b/b.txt || echo "Exit-Code $?"
echo "Laufzeit B $(( $(date +%s) - start )) s"
grep -E '^(E|HALT|ENDE)' aus_b/b.txt
gzip -6 aus_b/b.txt
ls -la aus_b
