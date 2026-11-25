#!/bin/bash
# Kontrollen Teil 2: runde.c (PROTO=1) gegen runde_b.cpp, zeilengleiche Protokolle. Bricht bei Abweichung ab.
set -euo pipefail
cd "$(dirname "$0")"
gcc -O2 -Wall -o runde runde.c
gcc -O2 -Wall -DSCHWELLE=3 -o runde_s3 runde.c
g++ -O2 -Wall -o runde_b runde_b.cpp
TEST=1 ./runde_b
filt() { grep -E '^(K |Z |E |H |ENDE )|^HALT 111 [0-9]+ [0-9]+$' || true; }
echo "== 1. Ab Leerband, 20000 Runden"
PROTO=1 ./runde 396 20000 2>/dev/null | filt > pa.txt
./runde_b 20000 > pb.txt
cmp pa.txt pb.txt && echo "gleich ($(wc -l < pa.txt) Zeilen)"
echo "== 2. 300 Zufalls-Startwoerter (mit 1011, 011, 111), je 40 Runden, Schwelle 64 und 3"
n=0; k=0; zz=0; h=0
for i in $(seq 1 300); do
  w=$(python3 -c "import random;random.seed(1000+$i);L=random.randint(4,40);print('1'+''.join(random.choice('0001') if random.random()<0.7 else random.choice('01') for _ in range(L)))")
  PROTO=1 ./runde 396 40 0 "$w" 2>/dev/null | filt > za.txt
  PROTO=1 ./runde_s3 396 40 0 "$w" 2>/dev/null | filt > z3.txt
  ./runde_b 40 0 "$w" > zb.txt
  cmp -s za.txt zb.txt && cmp -s z3.txt zb.txt || { echo "ABWEICHUNG bei Startwort $w"; diff za.txt zb.txt | head; exit 1; }
  n=$((n+1)); grep -q '^K ' zb.txt && k=$((k+1)); grep -q '^Z ' zb.txt && zz=$((zz+1)); grep -q '^HALT' zb.txt && h=$((h+1))
done
echo "gleich auf $n Woertern (mit K: $k, mit Z: $zz, mit Halt: $h)"
echo "== 3. Negativkontrollen (muessen abweichen)"
bad=0
for i in $(seq 1 60); do
  w=$(python3 -c "import random;random.seed(1000+$i);L=random.randint(4,40);print('1'+''.join(random.choice('0001') if random.random()<0.7 else random.choice('01') for _ in range(L)))")
  FEHLER=1 PROTO=1 ./runde 396 40 0 "$w" 2>/dev/null | filt > za.txt
  ./runde_b 40 0 "$w" > zb.txt
  cmp -s za.txt zb.txt || bad=$((bad+1))
done
echo "Schalter 1 (falsche 1011-Regel): $bad von 60 Woertern weichen ab"; [ "$bad" -gt 0 ] || { echo "FEHLER: nicht erkannt"; exit 1; }
FEHLER=2 PROTO=1 ./runde_s3 396 3000 2>/dev/null | filt > pa2.txt
./runde_b 3000 > pb2.txt
cmp -s pa2.txt pb2.txt && { echo "FEHLER: Schalter 2 nicht erkannt"; exit 1; }
echo "Schalter 2 (falsche Rundung, Schwelle 3): weicht ab"
echo "ALLE KONTROLLEN TEIL 2 BESTANDEN"
