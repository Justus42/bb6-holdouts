#!/bin/bash
# Alle kurzen Kontrollen fuer analyse/396 (lokal ca. 1 min). Bricht bei der ersten Abweichung ab.
set -euo pipefail
cd "$(dirname "$0")"
H=../../data/BB6_holdouts_608.txt
echo "== 1. Besuchsgesetz (PR #59) auf allen Woertern bis Laenge 12, beide Werte von x"
python3 gesetz.py 12 | tee aus_gesetz.txt
# Erwartung: 88/312/449: 0,100,110,1010 OK und 1011=halt OK; 396: 0,100,110,1010 OK, 1011=0001x OK, 111=halt OK
grep '^396 ' aus_gesetz.txt | grep -q "'1011=0001x': 'OK'" && grep '^396 ' aus_gesetz.txt | grep -q "'1011=halt': 'FALSCH" \
  && grep '^88 ' aus_gesetz.txt | grep -q "'1011=halt': 'OK'" && grep '^88 ' aus_gesetz.txt | grep -q "'1011=0001x': 'FALSCH" \
  || { echo "FEHLER Besuchsgesetz"; exit 1; }
echo "== 2. E1-Lesungen auf oberster Ebene je Blockart"
python3 visitlog.py
echo "== 3. Rundenmodell: direkte TM-Simulation = naiv (Besuch fuer Besuch) = runde.c"
gcc -O2 -Wall -o direkt direkt.c
gcc -O2 -Wall -o runde runde.c
gcc -O2 -Wall -DSCHWELLE=3 -o runde_s3 runde.c
for m in 88 396; do
  T=$(python3 -c "import tm;print(tm.M['$m'])")
  ./direkt "$T" 20000000000 27 | awk '$1=="R" && $2>=1{print "R",$2,$3}' | sed 's/0*$//' > d_$m.txt
  python3 naiv.py $m 34 | sed 's/0*$//' > n_$m.txt
  ./runde $m 34 34 2>/dev/null | grep '^R' | sed 's/0*$//' > r_$m.txt
  ./runde_s3 $m 34 34 2>/dev/null | grep '^R' | sed 's/0*$//' > r3_$m.txt
  cmp n_$m.txt r_$m.txt && cmp n_$m.txt r3_$m.txt && diff <(head -27 n_$m.txt) d_$m.txt >/dev/null \
    || { echo "FEHLER Rundenmodell $m"; exit 1; }
  echo "$m: direkt (27 Runden) = naiv (34) = runde (34, Schwelle 64 und 3)"
done
echo "== 4. Zufalls-Startwoerter mit 1011 und 111"
./zufall.sh 150 12 2>/dev/null | tail -n1 | tee aus_zufall.txt
grep -q 'Abweichungen 0,' aus_zufall.txt || { echo "FEHLER Zufall"; exit 1; }
cp runde runde_ok; cp runde_s3 runde
./zufall.sh 150 12 2>/dev/null | tail -n1 | grep -q 'Abweichungen 0,' || { echo "FEHLER Zufall Schwelle 3"; exit 1; }
echo "Schwelle 3: Abweichungen 0"
echo "== 5. Negativkontrollen (muessen anschlagen)"
FEHLER=1 ./zufall.sh 150 12 2>/dev/null | tail -n1 | tee aus_f1.txt
grep -q 'Abweichungen 0,' aus_f1.txt && { echo "FEHLER: Schalter 1 nicht erkannt"; exit 1; }
for m in 88 396; do
  FEHLER=2 ./runde_s3 $m 34 34 2>/dev/null | grep '^R' | sed 's/0*$//' | cmp -s - n_$m.txt && { echo "FEHLER: Schalter 2 nicht erkannt ($m)"; exit 1; }
  echo "Schalter 2 ($m): erkannt"
done
cp runde_ok runde
echo "== 6. Verschiedene Tabellen unter den 608 Holdouts"
for m in normal mutiere spiegel umbenennen; do python3 tabellen.py $H $m; done | tee aus_tabellen.txt
grep -q '^normal Maschinen 608 verschiedene Tabellen 403' aus_tabellen.txt && grep -q '^mutiere .* 404' aus_tabellen.txt \
  && grep -q '^spiegel .* 403' aus_tabellen.txt && grep -q '^umbenennen .* 403' aus_tabellen.txt || { echo "FEHLER Tabellen"; exit 1; }
python3 tabellen_csv.py
echo "ALLE KONTROLLEN BESTANDEN"
