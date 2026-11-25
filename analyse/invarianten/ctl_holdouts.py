#!/usr/bin/env python3
"""Weg 2 ueber alle Maschinen der Holdout-Liste: kleinste CTL-Zertifikate bis MAX x MAX (Start A).
Aufruf: python3 ctl_holdouts.py ../../data/BB6_holdouts_608.txt MAX > ergebnisse/holdouts.txt
Jeder Fund wird gespeichert und sofort mit ctl_pruefer (unabhaengig) geprueft."""
import sys, json, time
from ctl_sat import suche
import ctl_pruefer
liste = [z.strip() for z in open(sys.argv[1]) if z.strip()]
MAX = int(sys.argv[2])
funde = 0
for i, tm in enumerate(liste, 1):
    t = time.time(); fund = None
    for s in range(2, 2 * MAX + 1):
        for nL in range(1, MAX + 1):
            nR = s - nL
            if not 1 <= nR <= MAX: continue
            z, _ = suche(tm, nL, nR, 0)
            if z: fund = z; break
        if fund: break
    if fund:
        funde += 1
        fehler = ctl_pruefer.pruefe(fund); lauf = ctl_pruefer.lauf(fund, 100000)
        json.dump(fund, open(f'zertifikate/holdout_{i}.json', 'w'))
        print(f'{i} {tm} FUND {fund["nL"]}x{fund["nR"]} pruefer={"OK" if not fehler and lauf is None else "FEHLER"}', flush=True)
    else:
        print(f'{i} {tm} kein Zertifikat bis {MAX}x{MAX} ({time.time()-t:.1f}s)', flush=True)
print(f'Maschinen: {len(liste)}, Funde: {funde}')
