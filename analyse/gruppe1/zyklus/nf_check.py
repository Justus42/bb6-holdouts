import sys
from collections import Counter
from pairs import lese
from blk import bits
from canon import canon, show
def nf(t,tl):
    """Normalform am Zyklusanfang. Rueckgabe: Fehlergrund oder None."""
    if tl!='0': return 'rest'
    if not t or t[-1][0]!='1' or t[-1][1]%2: return 'rechts'
    irr=[i for i,(s,n) in enumerate(t[:-1]) if s=='0' or n%2==0]
    if not irr: return None
    i=irr[0]
    if t[i]!=('1',0): return 'marke:'+show(t[max(0,i-1):i+2])
    rest=irr[1:]
    if rest==[] : pass
    elif rest==[i+1] and t[i+1][0]=='0' and t[i+1][1]%2==0: pass
    else: return 'mehr:'+show(t[max(0,i-1):i+4])
    return None
fn=sys.argv[1]; L,steps,anf=lese(fn)
C=Counter(); ex=[]
for c in anf:
    t,tl=canon(bits(L[c])); r=nf(t,tl)
    C[r is None]+=1
    if r and len(ex)<8: ex.append((steps[c],r,show(t[:10])))
print(fn,dict(C)); [print(' ',e) for e in ex]
