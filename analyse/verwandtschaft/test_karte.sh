#!/bin/bash
# Positiv- und Negativkontrollen der Verwandtschaftskarte. Aufruf aus diesem Ordner: bash test_karte.sh
# Beendet sich mit Fehler, sobald eine Erwartung nicht stimmt.
set -u
T=$(mktemp -d); fail=0
gcc -O2 -Wall -o "$T/karte_b" karte_b.c || exit 1
gcc -O2 -o "$T/divergenz" divergenz.c || exit 1
python3 -I testfaelle.py universum.tsv > "$T/u.tsv"
python3 -I karte_a.py "$T/u.tsv" > "$T/a.tsv"
"$T/karte_b" "$T/u.tsv" 100000 0 > "$T/b.tsv"

norm() { awk -F'\t' 'BEGIN{OFS="\t"} $1=="Q"{NF=5} $1=="K"{NF=5} {print}' "$1" | grep -v '^S' | LC_ALL=C sort; }
gleich() { cmp -s <(norm "$1") <(norm "$2"); }
hat()   { if grep -qP "$2" "$1"; then echo "ok   hat: $3"; else echo "FEHLT: $3"; fail=1; fi; }
hatnicht() { if grep -qP "$2" "$1"; then echo "FALSCH vorhanden: $3"; fail=1; else echo "ok   nicht: $3"; fi; }

echo "== A und B auf dem Test-Universum"
if gleich "$T/a.tsv" "$T/b.tsv"; then echo "ok   A = B"; else echo "FEHLER: A != B"; fail=1; fi
for f in "$T/a.tsv" "$T/b.tsv"; do
  echo "-- $(basename $f)"
  hat "$f" '^T\th114\th367\t0D$' "114/367 gleiche Tabelle, Start D"
  hat "$f" '^T\th114\th378\t1C$' "114/378 gleiche Tabelle gespiegelt, Start C"
  hat "$f" '^T\th22\th9001\t1E$' "kuenstlich h9001 = h22 ab E gespiegelt"
  hat "$f" '^V\th22\th9001\t1\t1$' "h9001 verschmilzt nach 1 Schritt"
  hat "$f" '^G\th318\th518\t0\t' "318/518 Gleichschritt"
  hat "$f" '^G\th88\th312\t0\t' "88/312 Gleichschritt"
  hat "$f" '^K\th274\th322\t' "M5: 274/322 gemeinsamer Kern"
  hat "$f" '^K\th318\th274\t' "M5: 318/274 gemeinsamer Kern"
  hat "$f" '^W\th274\th322\t25\t11$' "274/322 verschmelzen im Kern (25/11)"
  hatnicht "$f" 'h9002' "h9002 (367 mit geaendertem B0) ohne Verwandte"
  hatnicht "$f" '^G\t.*h9003' "h9003 (518 mit D0=1RA) ohne Gleichschritt"
  hatnicht "$f" '^K\t.*h9004' "h9004 (318 mit C1=1RE) ohne gemeinsamen Kern"
done

echo "== Fehler-Schalter muessen den Abgleich brechen"
for x in spiegel joker produkt; do
  KARTE_A_FEHLER=$x python3 -I karte_a.py "$T/u.tsv" > "$T/af.tsv"
  if gleich "$T/af.tsv" "$T/b.tsv"; then echo "FEHLER: A-Schalter $x bleibt unbemerkt"; fail=1; else echo "ok   A-Schalter $x schlaegt an"; fi
done
for x in spiegel joker produkt hash; do
  KARTE_B_FEHLER=$x "$T/karte_b" "$T/u.tsv" 100000 0 > "$T/bf.tsv"
  if gleich "$T/a.tsv" "$T/bf.tsv"; then echo "FEHLER: B-Schalter $x bleibt unbemerkt"; fail=1; else echo "ok   B-Schalter $x schlaegt an"; fi
done

echo "== divergenz"
m318=$(awk '$1=="h318"{print $2}' "$T/u.tsv"); m518=$(awk '$1=="h518"{print $2}' "$T/u.tsv"); m9003=$(awk '$1=="h9003"{print $2}' "$T/u.tsv")
"$T/divergenz" "$m318" "$m518" 1000000 | grep -q "^gleich bis 1000000" && echo "ok   318/518 gleich bis 1e6" || { echo "FEHLER divergenz 318/518"; fail=1; }
"$T/divergenz" "$m318" "$m9003" 1000000 | grep -q "^verschieden" && echo "ok   318/h9003 verschieden" || { echo "FEHLER divergenz 318/h9003"; fail=1; }

rm -rf "$T"
[ $fail = 0 ] && echo "ALLE KONTROLLEN BESTANDEN" || { echo "KONTROLLEN FEHLGESCHLAGEN"; exit 1; }
