#!/usr/bin/env python3
"""Einteilung der direkt gerechneten Zyklen (Analyse 318/518, Teil 2).

Aufruf: direkt_klassen.py <umbau-Datei von "m5schnell.py --umbau">
Klassen: Anlauf (<5000 Schritte), quadratischer Ueberlauf (Dauer > 10 x Breite),
Rest waechst / schrumpft (Zerlegung verliert bzw. findet den linken Teil), Rest gleich, ohne Zerlegung.
Gibt die Anzahl je Klasse aus und prueft fuer "Rest waechst", ob die Wendeziffer ein Z mit
Luecke 0 vor einem W ist (Wanddurchgang, Schritt 1).
"""
import re,sys,collections
L=open(sys.argv[1]).read().split('\n'); c=collections.Counter(); ex={}
i=0
while i<len(L):
    m=re.match(r'(\d+) -> (\d+) Dauer (\d+) Breite (\d+)',L[i])
    if not m: i+=1; continue
    a,b,dt,w=map(int,m.groups()); v=L[i+1].split('vorher:')[1].strip(); n=L[i+2].split('nachher:')[1].strip(); i+=3
    rv=re.search(r'Rest\[(\d+):',v); rn=re.search(r'Rest\[(\d+):',n)
    if a<5000: k='Anlauf (<5000 Schritte)'
    elif dt>10*w: k='Ueberlauf quadratisch'
    elif not rn or not rv: k='Zwischenstand ohne Zerlegung'
    elif int(rn.group(1))>int(rv.group(1))+20: k='Rest waechst (Zerlegung verliert linken Teil)'
    elif int(rn.group(1))<int(rv.group(1))-20: k='Rest schrumpft (Zerlegung wieder vollstaendig)'
    else: k='sonst (Rest gleich)'
    c[k]+=1; ex.setdefault(k,[]).append((a,dt,w,v,n))
for k,x in c.items(): print(x,k)
ok=0; andere=[]
for a,dt,w,v,n in ex.get('Rest waechst (Zerlegung verliert linken Teil)',[]):
    items=[]; u=0
    for t in v.split('] ',1)[1].split():
        if t.startswith('U^'): u=int(t[2:])
        elif t.startswith('|'): pass
        else: items.append((t,u)); u=0
    dig=[k for k,(x,_) in enumerate(items) if x!='W']
    j=next((k for k in reversed(dig) if items[k][0] in ('Z','D1')),None)
    nx=items[j+1] if j is not None and j+1<len(items) else None
    if j is not None and items[j][0]=='Z' and nx and nx[0]=='W' and nx[1]==0: ok+=1
    else: andere.append((a,items[j] if j is not None else None,nx))
print('Rest waechst: Wendeziffer Z mit Luecke 0 vor W:',ok,' andere:',len(andere),andere[:5])
