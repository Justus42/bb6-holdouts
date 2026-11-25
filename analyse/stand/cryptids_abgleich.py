#!/usr/bin/env python3
"""Maschinen-Strings in einem cryptids-Checkout (alle Dateien) ueber die Normalform aus
karte_a.canon mit den 608 Holdouts (tm + aliases) abgleichen.
Aufruf: python3 -I cryptids_abgleich.py <cryptids-Verzeichnis> <holdouts.json>
Ausgabe: je Holdout n die Dateien, in denen er (kanonisch) vorkommt; am Ende die Zielmaschinen.
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'verwandtschaft'))
import karte_a as K
root, jpath = sys.argv[1], sys.argv[2]
d = json.load(open(jpath))
alle = {}
for h in d['holdouts']:
    for tm in [h['tm']] + [a['tm'] for a in h['aliases']]:
        alle.setdefault(K.canon(K.parse(tm))[0], set()).add(h['n'])
TR = r'(?:[01][LR][A-F]|---)'
PAT = re.compile(r'(?<![0-9A-Za-z_-])' + '_'.join([TR + TR] * 6) + r'(?![0-9A-Za-z_-])')
treffer = {}
for dp, dn, fn in os.walk(root):
    if '/.git' in dp:
        continue
    for f in fn:
        p = os.path.join(dp, f)
        try:
            txt = open(p, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for m in set(PAT.findall(txt)):
            for n in alle.get(K.canon(K.parse(m))[0], ()):
                treffer.setdefault(n, set()).add(os.path.relpath(p, root))
for n in sorted(treffer):
    print(n, ' '.join(sorted(treffer[n])))
print('holdouts_mit_treffer', len(treffer))
for z in [88, 312, 396, 449, 114, 367, 378, 318, 518, 322, 274]:
    print('ZIEL', z, ' '.join(sorted(treffer.get(z, []))) or '-')
