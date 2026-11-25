#!/usr/bin/env python3
"""Karte eines grossen Umbaus (Analyse 318/518, Teil 2).

Aufruf: umbau_karte.py <m5sim-Programm> <band_vor.txt> <band_nach.txt>
  (Dateien wie von "m5schnell.py --baender" geschrieben)
Gibt die Lage der alten Ziffern/W, die Lage der neuen Bausteine (nachdem so viele Zyklen
weitergerechnet wurden, bis sich das Band wieder fast vollstaendig zerlegen laesst), die
Zuordnung alte Ziffer -> naechstes neues W und die Ziffern je Segment zwischen neuen W aus.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m5schnell import zerlege, TOK, M5
prog = sys.argv.pop(1)
def pos(m):
    p=len(m.rest); out=[]
    for a,u in m.items:
        p+=8*u; out.append((a,p)); p+=len(TOK[a])
    return out, p+8*m.uende+m.ende
vor=open(sys.argv[1]).read().strip()
dt,z,nach=open(sys.argv[2]).read().split()
mv=zerlege(vor); ov,ev=pos(mv)
print('vorher: Rest',len(mv.rest),'Breite',len(vor)); print('   ',' '.join(f'{a}@{x}' for a,x in ov),'Ende',ev)
k=0; b=nach
while True:
    mn=zerlege(b)
    if mn and len(mn.rest)<200: break
    r=subprocess.run([prog,'weiter',M5,z,'10000000000','100'],input=b+'\n',capture_output=True,text=True).stdout.split()
    z,b=r[1],r[2]; k+=1
on,en=pos(mn)
print(f'nachher (+{k} Zyklen): Rest',len(mn.rest),'Breite',len(b)); print('   ',' '.join(f'{a}@{x}' for a,x in on),'Ende',en)
# Zuordnung alter Ziffern -> neue W
W=[x for a,x in on if a=='W']
print('alte Ziffer/W/Ende -> naechstes neues W (Versatz):')
for a,x in ov+[('Ende',ev)]:
    if not W: break
    w=min(W,key=lambda y:abs(y-x)); print(f'   {a}@{x} -> W@{w} ({w-x:+d})')
# Ziffern je Segment
segs=[]; last=None; cur=[]
for a,x in on:
    if a=='W':
        if last is not None: segs.append((last,x,cur))
        last=x; cur=[]
    else: cur.append((a,x))
print('Segmente zwischen neuen W: Laenge, Ziffern (Abstand vom linken W)')
for l,r,c in segs: print(f'   {l}-{r} L={r-l}: '+' '.join(f'{a}+{x-l}' for a,x in c))
print('   nach letztem W:',' '.join(f'{a}+{x-last}' for a,x in cur))
