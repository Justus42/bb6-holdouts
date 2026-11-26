#!/bin/bash
# kontrollen.sh - Negativ- und Positivkontrollen fuer blocksim (Programm 1) und zweitzaehlung (Programm 2).
# Jede Kontrolle meldet OK, wenn sie sich wie erwartet verhaelt (Negativkontrollen: sie SCHLAGEN AN).
# Laufzeit lokal unter 1 Minute.
set -uo pipefail
source "$(dirname "$0")/gemeinsam.sh"
bauen
T=$(mktemp -d)
ok=0; nok=0
melde() { if [ "$1" = 0 ]; then echo "OK    $2"; ok=$((ok+1)); else echo "NICHT $2"; nok=$((nok+1)); fi; }

# K1: Variante V1 (M5 mit B1 = 1LC statt 1RA): C1 E1 kommt vor, fast alles davon in Spruengen.
V1=1RB0LD_0RC1LC_1RD1RE_1LA0LE_0RA0LC
# K2: V1 mit umbenannten Zustaenden (A,B,C,D,E -> C,E,B,D,A), Start C: dasselbe Muster heisst jetzt B1 A1.
V2=0RC0LB_1RD1RA_1RE0LD_1LC0LA_0RB1LB
for x in "K1 $V1 A C1_E1" "K2 $V2 C B1_A1"; do
  set -- $x; k=$1; tm=$2; st=$3; muster=${4/_/ }
  "$BIN/blocksim" $tm $st 1e8 -anteil > $T/p1; "$BIN/zweitzaehlung" $tm $st 1e8 > $T/p2; direkt $tm $st 100000000 > $T/d
  n=$(awk -v m="$muster" '$1" "$2==m && NF==3{print $3}' $T/d)
  j=$(grep "im Sprung $muster" $T/p1 | awk '{print $NF}')
  diff <(paare $T/p1 100000000) $T/d > /dev/null && diff <(paare $T/p2 100000000) $T/d > /dev/null && [ "${n:-0}" -gt 0 ] && [ "${j:-0}" -gt 0 ]
  melde $? "$k: $tm ab $st, 1e8 Schritte: $muster direkt ${n:-0}-mal; Programm 1 und 2 zaehlen alle Paare gleich wie direkt; davon in Spruengen verbucht (Programm 1): ${j:-0}"
done

# K3: Programm 1 mit absichtlichem Fehler (in Spruengen Paare nur (k-1)-mal) weicht von direkt ab.
"$BIN/blocksim" $M5 A 1e9 -fehler > $T/f1; direkt $M5 A 1000000000 > $T/dA
! diff <(paare $T/f1 1000000000) $T/dA > /dev/null
melde $? "K3: Programm 1 mit -fehler weicht bei 1e9 von direkt ab ($(diff <(paare $T/f1 1000000000) $T/dA | grep -c '^<') Paarzeilen verschieden)"

# K4: Programm 2 ohne Fenstervergleich beim Sprung weicht ab (Paare oder Band).
"$BIN/zweitzaehlung" $M5 A 1e9 -fehler > $T/f2; "$BIN/zweitzaehlung" $M5 A 1e9 > $T/r2
! diff <(paare $T/f2 1000000000) $T/dA > /dev/null || ! diff <(grep Band $T/f2) <(grep Band $T/r2) > /dev/null
melde $? "K4: Programm 2 mit -fehler weicht bei 1e9 ab ($(diff <(paare $T/f2 1000000000) $T/dA | grep -c '^<') Paarzeilen verschieden)"

# K5: Der Vergleich erkennt eine Abweichung um 1: Lauf ab C gegen Lauf ab D bei 1e9 (dort 1 Schritt Versatz).
"$BIN/blocksim" $M5 C 1e9 > $T/c; "$BIN/blocksim" $M5 D 1e9 > $T/dd
! diff <(paare $T/c 1000000000) <(paare $T/dd 1000000000) > /dev/null
melde $? "K5: Vergleich C gegen D bei 1e9 meldet Unterschied ($(diff <(paare $T/c 1000000000) <(paare $T/dd 1000000000) | grep '^[<>]' | tr '\n' ' '))"

# K6: Ohne Spruenge (-nosprung) gleiche Ausgabe wie mit Spruengen, beide Programme, 1e7.
"$BIN/blocksim" $M5 A 1e7 -nosprung | grep -v Spruenge > $T/a; "$BIN/blocksim" $M5 A 1e7 | grep -v Spruenge > $T/b
"$BIN/zweitzaehlung" $M5 A 1e7 -nosprung | grep -v Spruenge > $T/c2; "$BIN/zweitzaehlung" $M5 A 1e7 | grep -v Spruenge > $T/d2
cmp -s $T/a $T/b && cmp -s $T/b $T/c2 && cmp -s $T/c2 $T/d2
melde $? "K6: mit und ohne Spruenge, Programm 1 und 2, 1e7: Paare und Band gleich"

# K7: Haltende Maschine: BB(2)-Meister haelt mit dem 6. Schritt (Halteuebergang B1). Die Programme zaehlen
# die ausgefuehrten Uebergaenge davor, also "Schritt 5 HALT".
B2=1RB1LB_1LA---
"$BIN/blocksim" $B2 A 100 | grep -q "^Schritt 5 HALT" && "$BIN/zweitzaehlung" $B2 A 100 | grep -q "^Schritt 5 HALT"
melde $? "K7: BB(2)-Meister $B2: beide Programme melden HALT (5 Uebergaenge, dann Halteuebergang als 6. Schritt)"

echo "Kontrollen: $ok OK, $nok NICHT"
rm -rf $T
[ $nok = 0 ]
