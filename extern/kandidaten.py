import json, sys, collections as C
d = json.load(open(sys.argv[1]))
dec = C.Counter((x['class'] or 'None') for x in d['decided'] if x.get('by') == 'proof')
rows = []
for x in d['holdouts']:
    sb = (x['slugbird'] or {})
    if x['busycoq']['status'] != 'open' or x['busycoq']['prs']: continue
    if sb.get('status') != 'rules': continue
    if x['tags']: continue
    c = x['class'] or 'None'
    if dec[c] < 5: continue
    ds = [m['date'] for m in x['discord']]
    recent = sum(1 for m in ds if m >= '2026-10-15')
    rows.append((recent, len(ds), max(ds) if ds else '-', c, x['n'], x['tm'], sb.get('simulated'), len(x['wiki_pages']), [n['kind'] for n in x['notes']]))
rows.sort()
print(len(rows), 'Kandidaten (open, keine PR, slugbird=rules, ohne Tags, Klasse >=5 Beweise)')
print(C.Counter(r[3] for r in rows))
print('ohne Discord-Erwaehnung seit 15.10.:', sum(1 for r in rows if r[0]==0), '| ganz ohne Erwaehnung:', sum(1 for r in rows if r[1]==0))
for r in rows[:25]:
    print(r)
