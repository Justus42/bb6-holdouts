#!/usr/bin/env python3
"""Tabellenvergleich durch rohes Durchprobieren aller 720 Umbenennungen, je mit und ohne Spiegelung.
Gibt jede Abbildung aus, die 133 genau in die andere Tabelle ueberfuehrt (Haltefeld eingeschlossen)."""
import sys
from itertools import permutations
def parse(s):
    t={}
    for i,g in enumerate(s.split('_')):
        for r in (0,1):
            x=g[3*r:3*r+3]; t[(i,r)]=None if x[0]=='-' else (int(x[0]),x[1],'ABCDEF'.index(x[2]))
    return t
a=parse(sys.argv[1]); b=parse(sys.argv[2])
for P in permutations(range(6)):
    for mir in (False,True):
        ok=True
        for (q,r),v in a.items():
            w=b[(P[q],r)]
            if v is None or w is None:
                ok = ok and v is None and w is None
                continue
            d=v[1] if not mir else ('L' if v[1]=='R' else 'R')
            ok = ok and (v[0],d,P[v[2]])==w
        if ok: print('A..F ->', ''.join('ABCDEF'[P[i]] for i in range(6)), 'gespiegelt' if mir else 'ungespiegelt')
