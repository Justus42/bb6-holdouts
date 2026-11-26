#!/bin/bash
# lauf.sh - Hauptlauf: M5 ab A (318, 518), ab C (322), ab D (274) bis 8e14 mit Programm 1 und 2,
# Vergleich beider, Abgleich mit der direkten Simulation (m5sim paare) bei 1e9 und 1e10.
# Ausgabe nach ergebnisse/. Laufzeit lokal etwa 5 Minuten (4 Kerne).
set -euo pipefail
source "$(dirname "$0")/gemeinsam.sh"
bauen
E=$HIER/ergebnisse; mkdir -p "$E"
PP="1e9 1e10 1e11 1e12 1e13 1e14 2e14 4e14 8e14"
for s in A C D; do
  ( t0=$(date +%s); "$BIN/blocksim" $M5 $s $PP -anteil > "$E/p1_$s.txt"; echo "$s Programm 1: $(( $(date +%s) - t0 )) s" > "$E/zeit_p1_$s.txt" ) &
  ( t0=$(date +%s); "$BIN/zweitzaehlung" $M5 $s $PP > "$E/p2_$s.txt"; echo "$s Programm 2: $(( $(date +%s) - t0 )) s" > "$E/zeit_p2_$s.txt" ) &
done
wait
for s in A C D; do
  for N in 1000000000 10000000000; do
    direkt $M5 $s $N > "$E/direkt_${s}_$N.txt" &
  done
done
wait
{
  echo "# Vergleich (lauf.sh), $(date -u +%Y-%m-%dT%H:%MZ), Kopf $(git -C "$HIER" rev-parse --short HEAD 2>/dev/null || echo ?)"
  cat "$E"/zeit_*.txt; rm -f "$E"/zeit_*.txt
  fehler=0
  for s in A C D; do
    # Programm 1 gegen 2: alle Zeilen ausser Sprungstatistik (Paare und Band an jedem Pruefpunkt)
    if diff <(grep -v -e Spruenge -e "im Sprung" "$E/p1_$s.txt") <(grep -v Spruenge "$E/p2_$s.txt") > /dev/null; then
      echo "$s: Programm 1 und 2 zeilengleich an allen Pruefpunkten ($(grep -c '^Schritt' "$E/p1_$s.txt") Pruefpunkte, $(grep -v -c -e Spruenge -e 'im Sprung' "$E/p1_$s.txt") Zeilen)"
    else echo "$s: Programm 1 und 2 VERSCHIEDEN"; fehler=1; fi
    for N in 1000000000 10000000000; do
      if diff <(paare "$E/p1_$s.txt" $N) "$E/direkt_${s}_$N.txt" > /dev/null && [ -s "$E/direkt_${s}_$N.txt" ]; then
        echo "$s: bei $N alle $(wc -l < "$E/direkt_${s}_$N.txt") Paarzahlen gleich der direkten Simulation"
      else echo "$s: bei $N ABWEICHUNG zur direkten Simulation"; fehler=1; fi
    done
    for p in "B1 A1" "C1 E1"; do
      n=$(grep -c "^  $p " "$E/p1_$s.txt" || true); m=$(grep -c "^  $p " "$E/p2_$s.txt" || true)
      echo "$s: Zeilen mit Haltepaar $p: Programm 1 $n, Programm 2 $m"
    done
    awk -v s=$s '$1=="Schritt"{x=$2} $1=="B1"&&$2=="A0"{b=$3} $1=="C1"&&$2=="E0"{c=$3} $1=="Spruenge"{print s": bis " x ": B1 A0 " b ", C1 E0 " c ", Spruenge " $2 " " $3 " " $4}' "$E/p1_$s.txt" | tail -1
  done
  [ $fehler = 0 ] && echo "ERGEBNIS: alles gleich" || echo "ERGEBNIS: FEHLER"
} | tee "$E/vergleich.txt"
