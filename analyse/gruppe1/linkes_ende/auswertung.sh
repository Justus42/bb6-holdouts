#!/bin/bash
# Auswertung der Artefakte eines linkes_ende-Laufs (laeuft in Actions, weil die Artefakt-Ablage aus der
# Cloud-Sitzung nicht erreichbar ist). Aufruf: bash auswertung.sh <Artefakt-Verzeichnis>
# Erwartet <dir>/beschleuniger-{A,C,D}/ und <dir>/direkt-{A,C,D}/ wie im Workflow linkes_ende.
set -u
D=$1
H=$(cd "$(dirname "$0")" && pwd)
echo "### Logs"
for s in A C D; do
  for f in b_e16_log_$s.txt b_weit_log_$s.txt; do
    echo "--- $s $f"; tail -n 4 "$D/beschleuniger-$s/$f" 2>/dev/null || echo "(fehlt)"
  done
  echo "--- $s d_log"; cat "$D/direkt-$s/d_log_$s.txt" 2>/dev/null || echo "(fehlt)"
done
echo "### Rueckfall-Dateien (weitester Lauf je Start)"
F=()
for s in A C D; do
  w=$D/beschleuniger-$s/b_weit_${s}_rueckfall.txt
  e=$D/beschleuniger-$s/b_e16_${s}_rueckfall.txt
  if [ -s "$w" ] && [ "$(tail -n1 "$w" | awk '{print $1}')" -gt "$(tail -n1 "$e" | awk '{print $1}')" ]; then f=$w; else f=$e; fi
  F+=("$f")
  echo "$s: $(basename "$f")  Zeilen $(wc -l < "$f")  letzte n $(tail -n1 "$f" | awk '{print $1}')"
  # Konsistenz: gleiche Saetze wie der lokale Lauf bis 1e15 und wie der 1e16-Lauf bis 1e16?
  if cmp -s <(awk '$1 < 1e15' "$f") <(zcat "$H/ergebnisse/lokal_1e15_${s}_rueckfall.txt.gz"); then
    echo "$s: bis 1e15 gleich mit lokalem Lauf"; else echo "$s: bis 1e15 VERSCHIEDEN vom lokalen Lauf"; fi
  if cmp -s <(awk '$1 < 1e16' "$f") <(awk '$1 < 1e16' "$e"); then
    echo "$s: bis 1e16 gleich mit 1e16-Lauf"; else echo "$s: bis 1e16 VERSCHIEDEN vom 1e16-Lauf"; fi
  # Uebergangsprotokoll: Arten zaehlen
  u=${f%_rueckfall.txt}_uebergang.txt
  echo "$s Uebergaenge: $(awk '{print $2}' "$u" | sort | uniq -c | tr '\n' ' ')"
done
echo "### formen.py"
python3 "$H/formen.py" "${F[@]}"
echo "### formen2.awk (alle Starts zusammen)"
sed 's/ #.*//' "${F[@]}" | sort -s -n -k1,1 | awk -f "$H/formen2.awk"
for s in 0 1 2; do
  echo "### formen2.awk ${F[$s]##*/}"
  sed 's/ #.*//' "${F[$s]}" | awk -f "$H/formen2.awk"
done
echo "### Negativkontrollen (Gesamtzeile muss sich aendern)"
for x in kern fenster; do
  echo "formen.py FORMEN_FEHLER=$x: $(FORMEN_FEHLER=$x python3 "$H/formen.py" "${F[@]}" | grep 'alle Starts')"
  echo "formen2.awk FEHLER=$x: $(sed 's/ #.*//' "${F[@]}" | sort -s -n -k1,1 | awk -v FEHLER=$x -f "$H/formen2.awk" | head -n1)"
done
echo "### abdeck.py (VS-Familie gegen alle Faelle)"
python3 "$H/abdeck.py" "${F[@]}"
echo "### Uebergangs-Faelle ab 1e15"
for f in "${F[@]}"; do awk -v fn="${f##*/}" '$1 >= 1e15 && ($3 ~ /^Ueb/) {print fn": "$0}' "$f" | head -n 40; done
