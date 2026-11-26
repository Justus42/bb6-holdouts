import os, re, sys, csv, itertools
root = sys.argv[1]
names = set()
for dp, dn, fn in os.walk(root):
    for f in fn + dn:
        for m in re.findall(r'[01HL-][A-Z0-9-]{2}(?:[A-Z0-9-]{3}){1}(?:_[A-Z0-9-]{6}){4,5}', f): pass
txt = []
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f); txt.append(f)
        try: txt.append(open(p, errors='ignore').read())
        except Exception: pass
blob = '\n'.join(txt).replace('HHH', '---')
found = set(re.findall(r'(?:[01][LR][A-F]|---){2}(?:_(?:[01][LR][A-F]|---){2}){5}', blob))
print('Maschinen-Strings im DeepMind-Repo (BB6-Format):', len(found))
offiziell = [l.strip() for l in open(sys.argv[2]) if l.strip()]
treffer = [ (i+1, s) for i, s in enumerate(offiziell) if s in found]
print('davon auf offizieller Liste:', len(treffer))
ziel = {'114','367','378','141','315','31','222','274','518','318','322'}
print('unsere Kandidaten im DeepMind-Repo:', [t for t in treffer if str(t[0]) in ziel])
print('M5 im Repo:', '1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC' in blob)
