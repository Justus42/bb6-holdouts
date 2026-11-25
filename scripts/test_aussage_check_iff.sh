#!/bin/bash
# Negativkontrollen fuer die Genau-dann-wenn-Form von scripts/aussage_check (Auflage 3, 25.11.2026).
# Jede Kontrolle veraendert rocq/gruppe1_durchlauf.v oder die Aufrufargumente an genau einer
# Stelle; aussage_check muss dann FAIL melden (exit 1) und den genannten Grund ausgeben.
# Die unveraenderte Datei muss OK ergeben. Aufruf aus dem Repo-Wurzelverzeichnis.
set -u
cd "$(dirname "$0")/.."
F=rocq/gruppe1_durchlauf.v
R=1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC     # 114 (Referenz)
M367=1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB
M378=1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---
M="$R,$M367,$M378"
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

# Positivkontrolle
lauf "unveraendert" 0 "ERGEBNIS: OK" "$F" "$M" --modell "$R"
# 1. falscher String
P=$(python3 -I - "$F" "$T/s1.v" <<'PY'
import sys
s=open(sys.argv[1]).read()
alt='Theorem gruppe1_114 :\n  halts (TM_from_str "1RB---_0RC0LF_'
assert s.count(alt)==1
open(sys.argv[2],'w').write(s.replace(alt,'Theorem gruppe1_114 :\n  halts (TM_from_str "1RB---_0RC0LE_'))
print(sys.argv[2])
PY
)
lauf "falscher String im Satz (114, B1 0LF->0LE)" 1 "weder ein erwarteter String" "$P" "$M" --modell "$R"
# (Nur 367 und 378 zu erwarten waere kein Fehler: 114 ist Spiegel-Zwilling von 378, solche
# Zwillinge mit eigenem Satz laesst aussage_check seit jeher zu.)
ANDERE=$(sed -n 1p data/BB6_holdouts_608.txt)   # Holdout Zeile 1, keine Verwandte von 114
lauf "falscher erwarteter String (Holdout Zeile 1 statt 114)" 1 "kommt in der Datei nicht exakt vor" "$F" "$ANDERE,$M367,$M378" --modell "$R"
# 2. nur eine Richtung
lauf "nur eine Richtung (-> statt <->, 114)" 1 "kein Haupttheorem" \
  "$(mut "c0 <-> erreicht_halt (start A)" "c0 -> erreicht_halt (start A)")" "$M" --modell "$R"
lauf "nur Rueckrichtung (<- statt <->, 367)" 1 "kein Haupttheorem" \
  "$(mut "c0 <-> erreicht_halt (start D)" "c0 <- erreicht_halt (start D)")" "$M" --modell "$R"
# 3. anderer Start des Modells
lauf "anderer Start (114: B statt A)" 1 "Modell-Start B passt nicht" \
  "$(mut "erreicht_halt (start A)." "erreicht_halt (start B).")" "$M" --modell "$R"
lauf "anderer Start (367: A statt D)" 1 "Modell-Start A passt nicht" \
  "$(mut "erreicht_halt (start D)." "erreicht_halt (start A).")" "$M" --modell "$R"
lauf "anderer Start (378: A statt C)" 1 "Modell-Start A passt nicht" \
  "$(mut "erreicht_halt (start C)." "erreicht_halt (start A).")" "$M" --modell "$R"
lauf "falsche Referenz (--modell 367)" 1 "Modell-Start .* passt nicht" "$F" "$M" --modell "$M367"
# weitere
lauf "Genau-dann-wenn ohne --modell" 1 "nur mit --modell" "$F" "$M"
lauf "Modell-Start ist keine Definition der Datei" 1 "keine oberste Definition" \
  "$(mut "erreicht_halt (start C)." "erreicht_halt (startx C).")" "$M" --modell "$R"
lauf "verschiedene Modelle" 1 "verschiedene Modelle" \
  "$(mut "erreicht_halt (start C)." "next (start C).")" "$M" --modell "$R"
exit $fehler
