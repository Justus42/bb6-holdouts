# Prueft das Besuchsgesetz (PR #59) fuer jede Maschine auf allen Woertern bis Laenge L, beide Werte der Zelle x
from tm import *
import itertools,sys
def V(T,w,x):
    r=visit(T,list(w),x=x,maxsteps=10**6)
    if r[0]=='ret':
        o=list(r[1]); 
        while o and o[-1]==0: o.pop()
        return tuple(o)
    return r[0]
def norm(t):
    t=list(t)
    while t and t[-1]==0: t.pop()
    return tuple(t)
L=int(sys.argv[1]) if len(sys.argv)>1 else 11
for name in ['88','312','449','396','396.2']:
    T=parse(M[name]); bad={}; cnt={}
    for x in (0,1):
      for n in range(L+1):
        for b in itertools.product((0,1),repeat=n):
            b=tuple(b)
            def chk(rule,lhs,rhs):
                cnt[rule]=cnt.get(rule,0)+1
                if lhs!=rhs: bad.setdefault(rule,[]).append(b)
            if b[:1]==(0,) or b==(): chk('0',V(T,b,x),norm((1,)+b[1:]))
            if b[:3]==(1,0,0) or b[:3]==(1,1,0):
                v=V(T,b[3:],x); chk(''.join(map(str,b[:3])), V(T,b,x), v if isinstance(v,str) else norm((0,0,0)+v))
            if b[:4]==(1,0,1,0):
                v=V(T,b[4:],x); vv=v if isinstance(v,str) else V(T,v,x)
                chk('1010',V(T,b,x), vv if isinstance(vv,str) else norm((1,0,1,0)+vv))
            if b[:4]==(1,0,1,1):
                chk('1011=halt',V(T,b,x),'halt'); chk('1011=0001x',V(T,b,x),norm((0,0,0,1)+b[4:]))
            if b[:3]==(1,1,1): chk('111=halt',V(T,b,x),'halt')
    print(name, {k:('OK' if k not in bad else f'FALSCH {len(bad[k])}/{c}') for k,c in sorted(cnt.items())})
