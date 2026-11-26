#!/usr/bin/env python3
"""Zusatz der Pruefstelle, b): die Episoden der Familie F, die nicht genau 45 Schritte dauern, nach linker Umgebung.
Liest die Einzelzeilen aus ergebnisse/luecke_familie_F.txt (32 Zellen links der linken Luecken-1).

Darstellung: Einserlaeufe von der Luecke nach links gelesen (jeder Lauf durch eine 0 vom naechsten getrennt).
Die Zelle direkt links der Luecken-1 ist immer 1 (Lauf 1), davor immer '0 1 0'. Der erste GERADE Lauf (von rechts)
und alles rechts davon heisst 'nah'; links davon wird mit den Bausteinen U, Z, W, D1, D2, D3 (m5schnell.RUNS,
alle Laeufe ungerade) von rechts zerlegt, soweit es geht ('…' = Rest nicht zerlegbar).
Aufruf: python3 luecke_b.py ergebnisse/luecke_familie_F.txt
"""
import sys, os
from collections import defaultdict, Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '318_518'))
from m5schnell import RUNS

def zerlege_links(ctx):
    r = [len(x) for x in ctx.split('0')]
    j = len(r) - 1
    while j >= 0 and r[j] % 2 == 1: j -= 1
    nah, weiter = r[j:], r[:j]
    aus = []; i = len(weiter)
    while i > 0:
        for name, m in RUNS:
            k = len(m)
            if i >= k and tuple(weiter[i-k:i]) == m: aus.append(name); i -= k; break
        else: break
    return ('…' if i > 0 else '') + ' '.join(reversed(aus)), ','.join(map(str, reversed(nah)))

rows = []
for l in open(sys.argv[1]):
    if l.startswith('  Band '):
        f = l.split(); rows.append((int(f[1]), int(f[3]), int(f[5]), f[6], f[7]))
print(f'{len(rows)} Episoden ungleich 45 Schritte')
print('\nNach den 16 Zellen links (Einserlaeufe von der Luecke nach links):')
g = defaultdict(Counter)
for b, beg, d, a, ctx in rows: g[ctx[-16:]][d] += 1
for k, v in sorted(g.items(), key=lambda x: -sum(x[1].values())):
    laeufe = ','.join(str(len(x)) for x in reversed(k.split('0')))
    print(f'  {k}  Laeufe {laeufe:18s} {sum(v.values()):3d}  Dauern {dict(sorted(v.items()))}')
for L in (16, 24, 32):
    h = defaultdict(set)
    for b, beg, d, a, ctx in rows: h[ctx[-L:]].add(d)
    print(f'Letzte {L} Zellen: {len(h)} verschiedene, davon {sum(1 for s in h.values() if len(s) == 1)} mit nur einer Dauer')
print('\nNach erstem geraden Lauf (nah, von der Luecke nach links) und Bausteinen davor:')
g = defaultdict(Counter)
for b, beg, d, a, ctx in rows:
    t, n = zerlege_links(ctx); g[(n, t)][d] += 1
for (n, t), v in sorted(g.items(), key=lambda x: (x[0][0], -sum(x[1].values()))):
    print(f'  nah {n:10s} davor {t:14s} {sum(v.values()):3d}  Dauern {dict(sorted(v.items()))}')
