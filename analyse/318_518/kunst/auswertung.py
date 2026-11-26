#!/usr/bin/env python3
"""Auswertung der Umbau-Messung (Sammelprogramm-Seite). Aufruf: auswertung.py ergebnisse/lauf_alle.jsonl"""
import json, collections, sys
L = [json.loads(l) for l in open(sys.argv[1])]
REG = {'D2': -3, 'D3': 5}
print('Laeufe', len(L), ' Haltemuster in Laeufen:', sum(d['halt'] for d in L),
      ' Schritte max', max(d['ende'][0] for d in L), ' Summe', sum(d['ende'][0] for d in L))
print('Klassen je Teil:')
for t in ('voll', 'W', 'gross'):
    print('  ', t, dict(collections.Counter(d['klasse'] for d in L if d['teil'] == t)))
U = [d for d in L if d['klasse'] in ('U', 'U-R')]
# 1. W-Regel: Ziffern, deren Regel-W rechts vom neuen Rest laege
hit = collections.Counter(); tot = collections.Counter(); suffix = 0; ausn = []
for d in U:
    Wset = {x for a, x in d['neu_lage'] if a == 'W'}
    grenze = d['lo_rel'] + len(d['nach_rest'])
    seen = False; ok = True
    for i, (a, x) in enumerate(d['alt_lage']):
        if a not in REG: continue
        f = (x + REG[a]) in Wset
        if x + REG[a] >= grenze:
            tot[a] += 1; hit[a] += f
        if f: seen = True
        elif seen: ok = False
    suffix += ok
    if not ok: ausn.append(d['id'])
print('W-Regel (D2 -3, D3 +5), Ziffern rechts vom neuen Rest:', {a: f'{hit[a]}/{tot[a]}' for a in tot})
print('Suffix-Eigenschaft (Regel gilt fuer alle Ziffern rechts der ersten, fuer die sie gilt):', suffix, '/', len(U),
      ' Ausnahmen (id):', ausn[:20])
# 2. Ende-Regel: letztes neues W relativ zum alten Ende, je (e,u)
endc = collections.defaultdict(collections.Counter)
for d in U:
    Wl = [x for a, x in d['neu_lage'] if a == 'W']
    endc[(d['e'], d['u'])][(max(Wl) - d['alt_endlage']) if Wl else None] += 1
print('letztes neues W minus altes Ende, je (e,u):')
for k in sorted(endc): print('  ', k, endc[k].most_common(6))
# 3. neue Ziffern je Abschnitt zwischen zwei Regel-W, nach Luecke g
cnt = collections.defaultdict(collections.Counter)
for d in U:
    neu = d['neu_lage']; pos = {x: i for i, (a, x) in enumerate(neu)}; alt = d['alt_lage']
    for i in range(len(alt) - 1):
        (a1, x1), (a2, x2) = alt[i], alt[i + 1]
        if a1 not in REG or a2 not in REG: continue
        w1, w2 = x1 + REG[a1], x2 + REG[a2]
        if w1 in pos and w2 in pos and neu[pos[w1]][0] == 'W' and neu[pos[w2]][0] == 'W':
            inner = neu[pos[w1] + 1:pos[w2]]
            cnt[d['items'][i + 1][1]][(sum(1 for a, _ in inner if a != 'W'), sum(1 for a, _ in inner if a == 'W'))] += 1
print('Abschnitte: (Luecke g) -> {(neue Ziffern, neue W): Anzahl}')
for g in sorted(cnt)[:40]: print('  ', g, dict(cnt[g]))
# 4. Beispiele der Klassen, die die Familie verlassen
for k in ('K', 'U-X'):
    ex = [d for d in L if d['klasse'] == k]
    print(f'Klasse {k}: {len(ex)} Laeufe; nach Teil', dict(collections.Counter(d['teil'] for d in ex)),
          '; nach Rest', dict(collections.Counter(d['rest'] for d in ex)))
    for d in ex[:4]:
        print('   ', d['id'], d['teil'], d['rest'], d['items'], 'u', d['u'], 'e', d['e'], 'Zyklen', d['zyklen'][:3])
        print('      ->', d.get('nach_kurz', '')[:220])
