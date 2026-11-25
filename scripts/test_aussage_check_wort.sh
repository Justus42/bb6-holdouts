#!/bin/bash
# Negativkontrollen fuer die Wortsystem-Form von scripts/aussage_check (--wortsystem), Rueckfuehrung 396
# (Auflage 4, 25.11.2026). Jede Kontrolle veraendert rocq/rueckfuehrung_396.v oder die Aufrufargumente
# an genau einer Stelle; aussage_check muss FAIL melden (exit 1) und den genannten Grund ausgeben.
# Die unveraenderte Datei (und eine nur in Kommentaren veraenderte) muss OK ergeben.
set -u
cd "$(dirname "$0")/.."
F=rocq/rueckfuehrung_396.v
REF=scripts/referenz/wortsystem_396.v
M=1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---     # 396
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
fehler=0

lauf() {  # lauf <name> <erwarteter rc> <grep-Muster> <datei> <args...>
  local name=$1 want=$2 muster=$3 datei=$4; shift 4
  out=$(scripts/aussage_check "$datei" "$@" 2>&1); rc=$?
  if [ "$rc" = "$want" ] && grep -qE -- "$muster" <<<"$out"; then
    echo "OK    $name (rc=$rc)"
  else
    echo "FEHLT $name (rc=$rc, erwartet $want, Muster '$muster')"; grep -E 'FAIL|ERGEBNIS' <<<"$out" | head -5; fehler=1
  fi
}
mut() {  # mut <alt> <neu> -> Pfad der veraenderten Kopie (alt muss genau einmal vorkommen)
  local n; n=$(grep -cF -- "$1" "$F")
  [ "$n" = 1 ] || { echo "Mutation nicht eindeutig ($n): $1" >&2; exit 2; }
  local p="$T/m$RANDOM.v"; python3 -I -c 'import sys; s=open(sys.argv[1]).read(); open(sys.argv[4],"w").write(s.replace(sys.argv[2],sys.argv[3],1))' "$F" "$1" "$2" "$p"; echo "$p"
}

# Positivkontrollen
lauf "unveraendert" 0 "ERGEBNIS: OK" "$F" "$M" --wortsystem "$REF"
lauf "nur Kommentar im Modul W geaendert" 0 "ERGEBNIS: OK" \
  "$(mut "(** Startwort (vom leeren Band). *)" "(** Startwort. *)")" "$M" --wortsystem "$REF"
# 1. falscher String
lauf "falscher String in der Datei (F0 0LA -> 0LB)" 1 "weder ein erwarteter String" \
  "$(mut "0RD0RF_0LA---\")." "0RD0RF_0LB---\").")" "$M" --wortsystem "$REF"
ANDERE=$(sed -n 1p data/BB6_holdouts_608.txt)
lauf "falscher erwarteter String (Holdout Zeile 1)" 1 "kommt in der Datei nicht exakt vor" "$F" "$ANDERE" --wortsystem "$REF"
lauf "falscher erwarteter String (587)" 1 "kommt in der Datei nicht exakt vor" "$F" "1RB1LD_0RC0LF_1LD1RE_0LA0RB_0RD1RB_0LD---" --wortsystem "$REF"
# 2. nur eine Richtung
lauf "nur eine Richtung (->)" 1 "kein Haupttheorem" \
  "$(mut "halts tm c0 <-> W.trifft111 W.start." "halts tm c0 -> W.trifft111 W.start.")" "$M" --wortsystem "$REF"
lauf "nur Rueckrichtung (<-)" 1 "kein Haupttheorem" \
  "$(mut "halts tm c0 <-> W.trifft111 W.start." "halts tm c0 <- W.trifft111 W.start.")" "$M" --wortsystem "$REF"
# 3. anderes Startwort
lauf "anderes Startwort im Satz (Liste statt W.start)" 1 "kein Haupttheorem" \
  "$(mut "halts tm c0 <-> W.trifft111 W.start." "halts tm c0 <-> W.trifft111 [true; false].")" "$M" --wortsystem "$REF"
lauf "anderes Startwort im Modul W ([true; true])" 1 "weicht von der Referenz ab" \
  "$(mut "Definition start : list bool := [true]." "Definition start : list bool := [true; true].")" "$M" --wortsystem "$REF"
# 4. Regel 1011 -> 1000 (System von 587)
lauf "Regel 1011 -> 1000 (587)" 1 "weicht von der Referenz ab" \
  "$(mut "      Vis w (false :: false :: false :: true :: tl (tl (tl (tl w))))." \
         "      Vis w (true :: false :: false :: false :: tl (tl (tl (tl w)))).")" "$M" --wortsystem "$REF"
# 5. sonstige
lauf "ohne --wortsystem" 1 "nur mit --wortsystem" "$F" "$M"
lauf "anderes Praedikat (Hit statt trifft111)" 1 "nicht die Referenz-Aussage" \
  "$(mut "halts tm c0 <-> W.trifft111 W.start." "halts tm c0 <-> W.Hit W.start.")" "$M" --wortsystem "$REF"
lauf "Satz nicht auf oberster Ebene (in Modul X)" 1 "nicht auf oberster Ebene" \
  "$(mut "Theorem rueckfuehrung : halts tm c0 <-> W.trifft111 W.start." "Module X. Theorem rueckfuehrung : halts tm c0 <-> W.trifft111 W.start.")" "$M" --wortsystem "$REF"
lauf "Admitted statt Qed" 1 "Beweis endet nicht mit Qed" \
  "$(mut "Proof. split; [exact nichthalt_richtung|exact halt_richtung]. Qed." "Proof. split; [exact nichthalt_richtung|exact halt_richtung]. Admitted.")" "$M" --wortsystem "$REF"
lauf "Umdefinition vor Modul W (tl)" 1 "vor Modul W steht mehr" \
  "$(mut "Set Default Goal Selector \"!\"." "Set Default Goal Selector \"!\".
Definition tl (w : list bool) : list bool := w.")" "$M" --wortsystem "$REF"
[ $fehler = 0 ] && echo "ALLE KONTROLLEN WORTSYSTEM-FORM BESTANDEN" || { echo "KONTROLLEN FEHLGESCHLAGEN"; exit 1; }
