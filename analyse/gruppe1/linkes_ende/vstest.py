"""Zufallstest der VS-Familie: vsfam.vs_familie gegen eine Phase im Durchlaufmodell.
Aufruf: python3 vstest.py <Anzahl> <Saat>"""
import sys,random
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import beschleuniger as bz
from vsfam import vs_familie
random.seed(int(sys.argv[2]))
CTX=[('1',7),('1',9),('1',9),('1',4)]
ok=bad=0; badex=[]
for _ in range(int(sys.argv[1])):
    f=random.choice(range(2,31,2)); m=f//2+3
    k=random.randint(0,m+3)
    zone=[('1',random.choice([1,1,1,3,5,7,9,11,13])) for _ in range(k)]
    p=random.choice([1,3,5,7,9,15,21])
    X=zone+[('1',0),('1',f),('1',p)]+CTX
    Y,yt,r2,dn,ln=bz.rueckfall(X,'',5)
    P=vs_familie(X)
    if P==Y and yt=='' and r2==4: ok+=1
    else:
        bad+=1
        if len(badex)<8: badex.append((f,k,[t[1] for t in zone],p,bz.zeile(Y,yt)[:120], P and bz.zeile(P,'')[:120]))
print('ok',ok,'falsch',bad)
for b in badex: print(b)
