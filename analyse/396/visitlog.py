# Wo liest E eine 1? Fuer jedes Praefix: E1-Lesungen auf Oberebene (Zellen des Blocks) zaehlen
from tm import *
import itertools
for name in ['88','312','449','396']:
    T=parse(M[name]); out={}
    for pre,wid in [((0,),1),((1,0,0),3),((1,1,0),3),((1,0,1,0),4),((1,0,1,1),4),((1,1,1),3)]:
        s=set()
        for n in range(0,9):
            for b in itertools.product((0,1),repeat=n):
                lg=[]; visit(T,list(pre)+list(b),log=lg,maxsteps=10**5)
                top=sum(1 for q,c,p in lg if q=='E' and c==1 and p<wid)
                s.add(top)
        out[''.join(map(str,pre))]=sorted(s)
    print(name,out)
