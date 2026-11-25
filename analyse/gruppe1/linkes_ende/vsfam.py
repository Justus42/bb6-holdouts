"""Regelvorschlag VS-Familie (Kern "0 e") fuer das linke Ende, abgeleitet aus kuenstlichen Phasen. Eingabe Token-Liste X (links nach rechts, ohne letztes Token beachtet),
Grenze (1,f) f gerade >= 2, links davon (1,0), links davon nur regulaere Token c_1..c_k (bis zum Bandende).
Rueckgabe neue Liste oder None.
Negativkontrolle: VSFAM_FEHLER=1 (Fall k >= 4, c1 = 1: c2+5 statt c2+4) muss in vstest.py und abdeck.py anschlagen."""
import os
FEHLER = os.environ.get("VSFAM_FEHLER", "")
def vs_familie(X):
    L=len(X)
    # Grenze: rechtestes unregelmaessiges Token ohne das letzte
    g=None
    for j in range(L-2,-1,-1):
        s,n=X[j]
        if s!='1' or n%2==0: g=j; break
    if g is None or g<1 or g+1>=L: return None
    s,f=X[g]
    if not (s=='1' and f%2==0 and f>=2 and X[g-1]==('1',0)): return None
    zone=X[:g-1]
    if any(t[0]!='1' or t[1]%2==0 for t in zone): return None
    k=len(zone); m=f//2+3
    sp,p=X[g+1]; rest=X[g+2:]
    c=[None]+[t[1] for t in zone]       # c[1..k]
    one=('1',1)
    if k>=m:
        z=c[k-m+1:]                      # die letzten m
        z=[None]+z
        neu=[('1',z[1]-1),('0',z[2]+1)]+[('1',z[j]+2) for j in range(3,m-1)]+[('1',z[m-1]+1),('0',p+3+z[m])]
        return X[:k-m]+neu+rest
    if k==0: return [one]*(f-1)+[('1',0),('0',p+4)]+rest
    if k==1: return [one]*(c[1]-1)+[('0',2),('0',f+1),(sp,p)]+rest
    if k==2:
        if c[1]==1: return [one]*(f-1)+[('1',0),('0',p+5+c[2])]+rest
        return [one]*(f-1+c[1]-3)+[('1',0),('0',p+7+c[2])]+rest
    gg=f+4-2*k
    if k==3:
        if gg==0 and c[1]>=3: return [one]*(c[1]-2)+[('0',c[2]+4),('0',p+3+c[3])]+rest
        return [one]*(gg+max(0,c[1]-3))+[('1',c[2]+(3 if c[1]==1 else 5)),('0',p+3+c[3])]+rest
    mitte=[('1',c[j]+2) for j in range(3,k-1)]+[('1',c[k-1]+1),('0',p+3+c[k])]
    if c[1]==1: return [one]*gg+[('1',c[2]+(5 if FEHLER else 4))]+mitte+rest
    if gg>0: return [one]*(gg+c[1]-3)+[('1',c[2]+6)]+mitte+rest
    return [one]*(c[1]-2)+[('0',c[2]+5)]+mitte+rest
