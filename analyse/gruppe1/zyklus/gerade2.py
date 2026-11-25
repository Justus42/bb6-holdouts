import sys
from collections import Counter
from pairs import lese
for fn in sys.argv[1:]:
    L,steps,anf=lese(fn); C=Counter(); maxl=0; minr=10**9; minrel=9
    for c in anf:
        t=L[c].split(' lead ',1)[1].split()[2:]
        el=[int(x) for x in t[0::2]]; sp=t[1::2]; n=len(el)
        odd={i for i,v in enumerate(el) if v%2}; so={i:sp[i] for i in range(len(sp)) if sp[i]!='|'}
        if not odd and not so: C['alles gerade']+=1; continue
        typ=[]
        for i,s in so.items():
            if s=='<1>' and i in odd: typ.append('<1>+ungerade')
            else: typ.append(s+('+ungerade' if i in odd else ''))
        for i in odd:
            if i not in so: typ.append('ungerade ohne Trenner')
        C[' & '.join(sorted(typ))]+=1
        idx=list(odd)+list(so)
        maxl=max(maxl,max(n-1-i for i in idx)); minr=min(minr,min(idx)); minrel=min(minrel,min(idx)/n)
    print(fn,len(anf),dict(C),'max Abstand vom linken Ende',maxl,'min Abstand vom rechten Ende',minr,'min relativ %.2f'%minrel)
