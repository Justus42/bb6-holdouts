"""Justus' Frage: bleiben am Zyklusanfang alle Listenelemente gerade? Textebene (Liste wie Teil 1)."""
import sys
from collections import Counter
from pairs import lese
fn=sys.argv[1]; L,steps,anf=lese(fn)
C=Counter(); ex=[]
for c in anf:
    t=L[c].split(' lead ',1)[1].split()[1:]   # '|', k, sep, k, ...
    assert t[0]=='|'; t=t[1:]
    el=[int(x) for x in t[0::2]]; sp=t[1::2]   # el[0] = rechtes Ende (a)
    n=len(el)
    odd=[i for i,v in enumerate(el) if v%2]
    sonder=[i for i,s in enumerate(sp) if s!='|']
    C['a_gerade' if el[0]%2==0 else 'a_ungerade']+=1
    if not odd and not sonder: C['alles_gerade']+=1
    else:
        C['bruch']+=1
        # Stelle vom linken Ende (Index n-1 = linkes Ende) aus zaehlen
        ex.append((steps[c], 'ungerade@links-'+','.join(str(n-1-i) for i in odd), 'sonder@links-'+','.join(f'{n-1-i}:{sp[i]}' for i in sonder), 'n='+str(n),
                   'links:'+' '.join(reversed([str(v) for v in el[-6:]]))))
print(fn,len(anf),dict(C))
for e in ex: print(' ',*e)
