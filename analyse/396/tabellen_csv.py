# Abgleich: Klassen "gleiche Tabelle" aus data/verwandtschaft.csv (Programme A/B aus PR 12) gegen tabellen.py
import csv, sys
rows=list(csv.reader(l for l in open('../../data/verwandtschaft.csv') if not l.startswith('#')))[1:]
par=list(range(609))
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for r in rows:
    if r[2]=='tabelle' and r[0].isdigit() and r[1].isdigit(): par[f(int(r[0]))]=f(int(r[1]))
cl={}
for i in range(1,609): cl.setdefault(f(i),[]).append(i)
mine=sorted(tuple(map(int,l.split(','))) for l in open('tabellen_klassen.txt'))
theirs=sorted(tuple(v) for v in cl.values() if len(v)>1)
print('CSV: Klassen', len(cl), '; Mehrfachklassen gleich wie tabellen.py:', mine==theirs)
sys.exit(0 if (len(cl)==403 and mine==theirs) else 1)
