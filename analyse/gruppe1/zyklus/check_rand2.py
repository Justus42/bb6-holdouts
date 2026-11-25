import sys, bisect
from collections import Counter
from pairs import lese
from blk import bits
from canon import canon, show
from snap import snaps
from automat import rand2 as rand
fn=sys.argv[1]; start=ord(sys.argv[2])-65; N=float(sys.argv[3])
L,steps,anf=lese(fn)
S=list(snaps(start,N)); ns=[s[0] for s in S]
res=Counter()
for i,c in enumerate(anf[:-1]):
    if steps[anf[i+1]]>N: break
    T,tl=canon(bits(L[c])); E,te=canon(bits(L[anf[i+1]-1]))
    T2,why=rand(T,2)
    (s3,e3),(s2,b),(s1,a)=T2[-3:]
    x=a+4*b+3
    pred=T2[:-3]+[(s3,e3-1),('0',0),('1',x)]
    res['eat',why,pred==E]+=1
    if pred!=E and res['eat',why,False]<3: print('EAT',steps[c],why,show(T[:12]),'|',show(E[:12]))
    k2=bisect.bisect_left(ns,steps[anf[i+1]])-1
    Z,_=canon(S[k2][2]); Nn,tn=canon(bits(L[anf[i+1]]))
    Z2,why=rand(Z,1)
    ok=(Z2==Nn) and S[k2][1]==0
    res['ret',why,ok]+=1
    if not ok and res['ret',why,False]<3: print('RET',steps[c],why,show(Z[:12]),'|',show(Nn[:12]))
print(sorted(res.items()))
