"""Prueft fuer eine Kern-Familie: zerfallen die Ergebnisse einer Phase (Durchlaufmodell) in endlich
viele Gestalten, und ist jede Gestalt exakt linear in den Parametern?
Gruppe = (Zonenlaenge k, Zahlen im Kern, Klasse des ersten und letzten Zonen-Tokens: 1, 3 oder >=5).
Gestalt = Trennerfolge der Ausgabe ohne fuehrende (1,1). Je Gestalt: Kleinste-Quadrate-Anpassung von
(Zahl fuehrender (1,1), n jedes weiteren Tokens) an (Zonenwerte, p, 1); exakt = Rest < 1e-6.
Aufruf: python3 autofit.py <Familie> <Proben> <kmax>   Familien: siehe FAM.
Negativkontrolle: AUTOFIT_FEHLER=1 addiert (p*p)//7 auf das letzte Token; dann muss "nicht linear" > 0 sein."""
import sys, random
import numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import beschleuniger as bz
BEISPIEL=[]
CTX=[('1',7),('1',9),('1',9),('1',4)]
FAM={
 'VS':      (lambda R: [('1',0),('1',R.choice(range(2,25,2)))], 1),
 '.0 .o':   (lambda R: [('0',0),('0',R.choice(range(1,25,2)))], 1),
 '0 .0 e':  (lambda R: [('1',0),('0',0),('1',R.choice(range(2,25,2)))], 1),
 '0 .o .0 e':(lambda R: [('1',0),('0',R.choice(range(1,9,2))),('0',0),('1',R.choice(range(2,25,2)))], 1),
 '.o .o':   (lambda R: [('0',R.choice(range(1,9,2))),('0',R.choice(range(1,25,2)))], 1),
 '0 .0 .o': (lambda R: [('1',0),('0',0),('0',R.choice(range(1,25,2)))], 1),
 '0 0':     (lambda R: [('1',0),('1',0)], 1),
 'e':       (lambda R: [('1',R.choice(range(2,25,2)))], 0),
}
def probe(fam,R,kmax):
    kern_f,_=FAM[fam]
    k=R.randint(0,kmax)
    zone=[('1',R.choice([1,1,1,3,5,7,9,11,13,15])) for _ in range(k)]
    if fam=='e': zone=[]; k=0
    kern=kern_f(R); p=R.choice(range(1,26,2))
    X=zone+kern+[('1',p)]+CTX
    try: Y,yt,r2,dn,ln=bz.rueckfall(X,'',5)
    except bz.Halt: return None
    if yt!='' or Y[-len(CTX):]!=CTX or r2!=4: return ('sonder',k,None,None)
    out=Y[:-len(CTX)]
    a=0
    while a<len(out) and out[a]==('1',1): a+=1
    kl=lambda c: c if c<=3 else 5
    rand=(kl(zone[0][1]),kl(zone[-1][1])) if zone else ()
    gest=((k,tuple(t[1] for t in kern),rand),tuple(s for s,n in out[a:]))
    x=[t[1] for t in zone]+[p,1]
    y=[a]+[n for s,n in out[a:]]
    if os.environ.get('AUTOFIT_FEHLER'): y[-1]+=(p*p)//7
    return ('ok',k,gest,(x,y))
def lauf(fam,N,kmax,seed=1):
    R=random.Random(seed); G={}; sonder=0
    for _ in range(N):
        r=probe(fam,R,kmax)
        if r is None or r[0]=='sonder': sonder+=1; continue
        G.setdefault(r[2],[]).append(r[3])
    # lineare Anpassung je Gestalt
    exakt=0; nicht=0
    proK={}
    for g,rows in G.items():
        X=np.array([r[0] for r in rows],float); Y=np.array([r[1] for r in rows],float)
        if len(rows) < X.shape[1] + 3: continue      # zu wenige Proben fuer eine echte Pruefung
        c,_,_,_=np.linalg.lstsq(X,Y,rcond=None)
        if np.abs(X@c-Y).max()<1e-6: exakt+=1
        else: nicht+=1; BEISPIEL.append((g,rows[:3]))
        proK.setdefault(g[0],0); proK[g[0]]+=1
    return G,exakt,nicht,sonder,proK
if __name__=='__main__':
    fam=sys.argv[1]; N=int(sys.argv[2]); kmax=int(sys.argv[3])
    G,ex,ni,so,proK=lauf(fam,N,kmax)
    print(f"{fam}: Proben {N}, Gestalten {len(G)}, davon gepruefte: exakt linear {ex}, nicht linear {ni}; ohne Ergebnis {so}")
    for b in BEISPIEL[:2]: print("   Bsp", b)
    from collections import Counter
    h=Counter(proK.values())
    print('  Gruppen (k, Kernzahlen):',len(proK),' Gestalten je Gruppe -> Anzahl Gruppen:',dict(sorted(h.items())), ' max:',max(proK.values()))
