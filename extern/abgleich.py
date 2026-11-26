import json, sys, hashlib
d = json.load(open(sys.argv[1]))
raw = open(sys.argv[2], 'rb').read()
print('sha256 txt', hashlib.sha256(raw).hexdigest())
lines = [l.strip() for l in raw.decode().splitlines() if l.strip()]
print('Zeilen', len(lines), 'eindeutig', len(set(lines)))
import re
bad = [l for l in lines if not re.fullmatch(r'([01][LR][A-F]|---)(_?([01][LR][A-F]|---)){11}', l.replace('_','')) and not re.fullmatch(r'(([01][LR][A-F]|---){2}_){5}([01][LR][A-F]|---){2}', l)]
print('Formatfehler', len(bad), bad[:3])
js = {x['n']: x['tm'] for x in d['holdouts']}
same_order = sum(1 for i, l in enumerate(lines, 1) if js.get(i) == l)
print('gleiche Position (n == Zeile):', same_order)
print('nur in TXT:', len(set(lines) - set(js.values())), '| nur in JSON:', len(set(js.values()) - set(lines)))
# Kandidaten pruefen
import collections as C
dec = C.Counter((x['class'] or 'None') for x in d['decided'] if x.get('by') == 'proof')
cand = [x for x in d['holdouts'] if x['busycoq']['status']=='open' and not x['busycoq']['prs'] and (x['slugbird'] or {}).get('status')=='rules' and not x['tags'] and dec[x['class'] or 'None']>=5]
print('Kandidaten', len(cand), 'davon in TXT:', sum(1 for x in cand if x['tm'] in set(lines)))
solved = [x for x in d['holdouts'] if x['busycoq']['status']=='solved']
print('solved in JSON:', [(x['n'], x['tm'], x['busycoq']['solved_in']) for x in solved])
m284 = '1RB1LE_0RC0LC_1LD0RA_0LA0LF_0LC0LE_0LD---'
print('PR32-Maschine in TXT:', m284 in lines)
