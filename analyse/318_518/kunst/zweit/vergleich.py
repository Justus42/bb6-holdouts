#!/usr/bin/env python3
"""Vergleicht je Lauf (id) die Ausgabe des Sammelprogramms (lauf_alle.jsonl) mit zweit.go (zweit.tsv):
Klasse, Schritte, Haltemuster, und fuer U/U-R: Zyklus, neuer Rest, W-Regel-Treffer, Suffix, Ende-Versatz, Abschnitte.
Aufruf: vergleich.py lauf_alle.jsonl zweit.tsv"""
import collections, json, sys
REG = {'D2': -3, 'D3': 5}
P = {str(d['id']): d for d in map(json.loads, open(sys.argv[1]))}
G = {c[0]: c for c in (l.rstrip('\n').split('\t') for l in list(open(sys.argv[2]))[1:])}
abw = collections.Counter(); n = 0
assert set(P) == set(G), 'verschiedene Laeufe'
for i, d in P.items():
    c = G[i]
    if d['klasse'] != c[2]: abw['klasse'] += 1
    if d['ende'][0] != int(c[4]): abw['schritte'] += 1
    if (d['muster'].get('BA', [0])[0] + d['muster'].get('CE', [0])[0]) != int(c[3]): abw['halt'] += 1
    if d['klasse'] not in ('U', 'U-R'): continue
    n += 1
    Wset = {x for a, x in d['neu_lage'] if a == 'W'}; grenze = d['lo_rel'] + len(d['nach_rest'])
    hit = collections.Counter(); tot = collections.Counter(); seen = False; ok = True
    for a, x in d['alt_lage']:
        if a not in REG: continue
        f = (x + REG[a]) in Wset
        if x + REG[a] >= grenze: tot[a] += 1; hit[a] += f
        if f: seen = True
        elif seen: ok = False
    Wl = [x for a, x in d['neu_lage'] if a == 'W']
    end = str(max(Wl) - d['alt_endlage']) if Wl else 'None'
    neu = d['neu_lage']; pos = {x: k for k, (a, x) in enumerate(neu)}; alt = d['alt_lage']; seg = []
    for k in range(len(alt) - 1):
        (a1, x1), (a2, x2) = alt[k], alt[k + 1]
        if a1 not in REG or a2 not in REG: continue
        w1, w2 = x1 + REG[a1], x2 + REG[a2]
        if w1 in pos and w2 in pos and neu[pos[w1]][0] == 'W' and neu[pos[w2]][0] == 'W':
            inner = neu[pos[w1] + 1:pos[w2]]
            seg.append(f"{d['items'][k + 1][1]}:{sum(a != 'W' for a, _ in inner)},{sum(a == 'W' for a, _ in inner)}")
    mine = [str(d['nach_zyklus']), d['nach_rest'], f"{hit['D2']}/{tot['D2']}", f"{hit['D3']}/{tot['D3']}",
            str(ok).lower(), end, ';'.join(seg) or '-']
    for name, a, b in zip(['zyklus', 'rest', 'D2', 'D3', 'suffix', 'ende', 'abschn'], mine, c[5:]):
        if a != b: abw[name] += 1
print('Laeufe', len(P), ' davon U/U-R', n, ' Abweichungen je Feld:', dict(abw) or 'keine')
