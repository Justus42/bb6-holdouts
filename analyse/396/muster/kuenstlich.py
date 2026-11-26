#!/usr/bin/env python3
"""Kuenstliche A-Zeilen fuer die Kontrollen der Periodensuche: Hexziffer g in Runde r ist (r >> g) & 1,
also hat das Fenster aus h Hexziffern (m = 4h Zellen) genau die Periode 2^h. STOER=1: eine Ziffer im
Schwanz verfaelscht (dann darf fuer grosse m keine Periode mehr gefunden werden)."""
import os
R = 1 << 12
for r in range(1, R + 1):
    w = ['1' if (r >> g) & 1 else '0' for g in range(10)]
    if os.environ.get('STOER') and r == R - 2: w[9] = 'f'
    print(f'A {r} ' + ''.join(w))
    print(f'Z {r} 0 {r // 2} 0 1')
print(f'ENDE {R} 0 junk 0')
