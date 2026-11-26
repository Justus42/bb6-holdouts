# gemeinsam.sh - Hilfsfunktionen fuer lauf.sh und kontrollen.sh (wird per "source" geladen)
M5=1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC
HIER=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BIN=${BIN:-$HIER/bin}
bauen() {
  mkdir -p "$BIN"
  gcc -O2 -Wall -o "$BIN/blocksim" "$HIER/blocksim.c"
  (cd "$HIER" && go build -o "$BIN/zweitzaehlung" zweitzaehlung.go)
  gcc -O2 -o "$BIN/m5sim" "$HIER/../m5sim.c"
}
# paare <datei> <schritt>: Paarzeilen des Pruefpunkts <schritt> aus einer Ausgabe von blocksim/zweitzaehlung
paare() { awk -v s="$2" '$1=="Schritt"{an=($2==s)} an && NF==3 && $1 ~ /^[A-H][01]$/ {print $1, $2, $3}' "$1" | LC_ALL=C sort; }
# direkt <tm> <start> <N>: Paarzeilen aus m5sim paare (direkte Simulation, Zelle fuer Zelle)
direkt() { "$BIN/m5sim" paare "$1" "$2" "$3" | awk 'NF==3' | LC_ALL=C sort; }
