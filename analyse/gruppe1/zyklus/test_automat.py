import sys
from collections import Counter
from snap import snaps
from canon import canon, show
from automat import step, frontier
start=ord(sys.argv[1])-65; N=int(float(sys.argv[2]))
prev=None; C=Counter(); bad=Counter(); ex={}
for n,r,b in snaps(start,N):
    t,tl=canon(b)
    if prev and prev[1]==r+1:
        pt=prev[2]
        u,why=step(pt)
        if u==t: C[why]+=1
        else:
            f=frontier(pt)
            lo_=max(0,(f if f is not None else 0)-4)
            key=(why, show(pt[lo_:lo_+8]), show(t[lo_:lo_+9]))
            bad[(why,)]+=1; ex.setdefault(key,[]).append(n)
    prev=(n,r,t)
print('erklaert:',dict(C),' nicht erklaert:',sum(bad.values()),dict(bad))
for k,v in sorted(ex.items(),key=lambda kv:-len(kv[1])): print(len(v),v[0],k)
