#!/usr/bin/env python3
"""Zaehlt aus der Ausgabe von zweit.go (nur diese Datei, kein Zugriff auf die Daten des Sammelprogramms)."""
import collections, sys
Z = [l.rstrip('\n').split('\t') for l in open(sys.argv[1])][1:]
print('Laeufe', len(Z), ' Haltemuster (318 oder 518 erreicht ---):', sum(int(c[3]) for c in Z),
      ' Schritte max', max(int(c[4]) for c in Z), ' Summe', sum(int(c[4]) for c in Z))
for t in ('voll', 'W', 'gross'):
    print('  ', t, dict(collections.Counter(c[2] for c in Z if c[1] == t)))
U = [c for c in Z if c[2] in ('U', 'U-R')]
h = collections.Counter()
for c in U:
    for k, a in ((7, 'D2'), (8, 'D3')):
        x, y = map(int, c[k].split('/')); h[a + 't'] += x; h[a + 'n'] += y
print('W-Regel: D2', f"{h['D2t']}/{h['D2n']}", ' D3', f"{h['D3t']}/{h['D3n']}",
      ' Suffix', sum(c[9] == 'true' for c in U), '/', len(U))
# Ende-Regel braucht u und e: aus der Eingabedatei
E = {c[0]: (int(c[5]), int(c[4])) for c in (l.rstrip('\n').split('\t') for l in open(sys.argv[2]))}
end = collections.defaultdict(collections.Counter)
for c in U:
    end[E[c[0]]][c[10]] += 1
print('letztes neues W minus altes Ende, je (e,u):')
for k in sorted(end): print('  ', k, end[k].most_common(4))
seg = collections.Counter()
for c in U:
    if c[11] != '-':
        for s in c[11].split(';'): seg[s.split(':')[1]] += 1
print('Abschnitte (neue Ziffern, neue W):', dict(seg))
