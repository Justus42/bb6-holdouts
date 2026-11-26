#!/bin/bash
# Programm X (defizit.c) im Workflow lauf_muster. Aufruf: lauf_x.sh <runden> <sekunden>
set -u
cd "$(dirname "$0")"
R="$1"; S="$2"
mkdir -p aus_x
gcc -O2 -Wall -o defizit defizit.c
W="1000,2000,194646,194647,200000,300000,400000,500000,600000,700000,748162,757565,757566,800000,906775,906776,1000000,1042306,1042307,1100000,1200000,1300000,1400000,1500000"
start=$(date +%s)
ZEILEN=1 APRE=1 PRUEF=1 M=320 ZEIT="$S" WORT="$W" ./defizit "$R" > aus_x/x.txt || echo "Exit-Code $?"
echo "Laufzeit X $(( $(date +%s) - start )) s"
grep -E '^(J|HALT|ENDE)' aus_x/x.txt
echo "== Auswertung A (auswertung.py)"
python3 auswertung.py aus_x/x.txt 194647
echo "== Zweite Auswertung (zweit.c) auf denselben Daten"
gcc -O2 -Wall -o zweit zweit.c && ./zweit aus_x/x.txt
echo "== Tokenbild der Stichrunden"
python3 tokenbild.py aus_x/x.txt
grep -E '^W ' aus_x/x.txt > aus_x/woerter.txt; grep -vE '^W ' aus_x/x.txt | gzip -6 > aus_x/x_ohne_w.txt.gz; rm aus_x/x.txt
gzip -6 aus_x/woerter.txt
ls -la aus_x
