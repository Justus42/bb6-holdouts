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
echo "== 4. Modus 587 (1011 -> 1000): runde.c gegen runde_b, 300 Zufallswoerter"
n=0; k=0; h=0; t=0
for i in $(seq 1 300); do
  w=$(python3 -c "import random;random.seed(1000+$i);L=random.randint(4,40);print('1'+''.join(random.choice('0001') if random.random()<0.7 else random.choice('01') for _ in range(L)))")
  PROTO=1 ./runde 587 40 0 "$w" 2>/dev/null | filt > za.txt
  MODUS=587 ./runde_b 40 0 "$w" > zb.txt
  ./runde_b 40 0 "$w" > z3.txt
  cmp -s za.txt zb.txt || { echo "ABWEICHUNG 587 bei Startwort $w"; diff za.txt zb.txt | head; exit 1; }
  cmp -s zb.txt z3.txt || t=$((t+1))
  n=$((n+1)); grep -q '^K ' zb.txt && k=$((k+1)); grep -q '^HALT' zb.txt && h=$((h+1))
done
echo "gleich auf $n Woertern (mit K: $k, mit Halt: $h); 587 und 396 verschieden auf $t Woertern"; [ "$t" -gt 0 ] || { echo "FEHLER: Modus 587 wirkungslos"; exit 1; }
echo "== 5. Direkte TM-Simulation (396 und 587) gegen Rundenmodell ab Zufallswoertern"
gcc -O2 -Wall -o direkt_start direkt_start.c
bash tm_zufall.sh 150 10 | tee tz.txt; grep -q 'Abweichungen: 0$' tz.txt || exit 1
FEHLER=1 bash tm_zufall.sh 60 10 | tail -1 | tee tz.txt; grep -q 'Abweichungen: 0$' tz.txt && { echo "FEHLER: Schalter 1 nicht erkannt"; exit 1; }
TAUSCH=1 bash tm_zufall.sh 60 10 | tail -1 | tee tz.txt; grep -q 'Abweichungen: 0$' tz.txt && { echo "FEHLER: Tausch nicht erkannt"; exit 1; }
echo "== 6. 396 und 587 ab Leerband (direkt), Runden 1-27 gleich"
./direkt_start 1RB1LD_0RC0LF_1LD1RE_0LA0RB_0RD1RB_0LD--- 587 1 27 3000000000 | awk '$2>0' > d_587.txt
./direkt_start 1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA--- 396 1 27 3000000000 | awk '$2>0' > d_396s.txt
cmp d_587.txt d_396s.txt && echo "gleich ($(wc -l < d_587.txt) Runden)"
echo "== 7. Zwoelf Annahmen aus PR #59 fuer 396 (Woerter bis Laenge 12), Gegenprobe 88 und veraenderte Tabelle"
python3 annahmen.py 396 12 | tee aus_annahmen_396.txt
[ "$(grep -c 'FALSCH' aus_annahmen_396.txt)" = 1 ] && grep -q 'hv_1011.*FALSCH' aus_annahmen_396.txt || { echo "FEHLER: 396 Annahmen"; exit 1; }
python3 annahmen.py 88 12 > aus_annahmen_88.txt
[ "$(grep -c 'Ersatz 396.*FALSCH' aus_annahmen_88.txt)" = 2 ] && grep -q 'hv_1011.*GILT' aus_annahmen_88.txt || { echo "FEHLER: Gegenprobe 88"; exit 1; }
python3 -c "import sys, tm; tm.M['neg']='1RB1LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---'; sys.argv=['annahmen.py','neg','8']; exec(open('annahmen.py').read())" | grep -q 'round_step.*FALSCH' || { echo "FEHLER: veraenderte Tabelle (A1=1LB) nicht erkannt"; exit 1; }
echo "Gegenprobe 88 und veraenderte Tabelle schlagen an"
echo "ALLE KONTROLLEN TEIL 2 BESTANDEN"
