#!/bin/bash
# Langer Lauf der PR-76-Portierung ab dem Start von 133 (581er Tabelle, Zustand C auf leerem Band).
# Aufruf: lauf_133.sh RUNDEN   (Ausgabe in aus/lauf133.txt)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p aus
RUNDEN="${1:-268435456}"
python3 --version | tee aus/lauf133.txt
echo "Runden: $RUNDEN, Start C, Kopf $(git rev-parse HEAD 2>/dev/null || echo ?)" | tee -a aus/lauf133.txt
python3 pr76_port.py C "$RUNDEN" --log 8388608 | tee -a aus/lauf133.txt
