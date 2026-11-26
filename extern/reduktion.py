# Rueckfuehrung auf kleinere Maschinen: Zwei Zustaende zusammenlegen, die sich nur dort unterscheiden,
# wo einer von beiden haelt. Aufruf: python3 reduktion.py <BB6_holdouts_608.txt> <n> [<n> ...]
# Ausgabe je Maschine: moegliche Paare und eine Normalform der 5-Zustands-Maschine (bis auf Umbenennung/Spiegelung).
import sys, itertools, hashlib
S='ABCDEF'
def parse(s):
    t={}
    for i,p in enumerate(s.split('_')):
        for b in range(2):
            x=p[3*b:3*b+3]; t[(S[i],b)]=None if x=='---' else (x[0],x[1],x[2])
    return t
def quotienten(t):
    for p,q in itertools.combinations(S,2):
        f=lambda s: p if s==q else s
        u={}; ok=True
        for s in S:
            if s==q: continue
            for b in (0,1):
                x=t[(s,b)]; y=t[(q,b)] if s==p else None
                xs=None if x is None else (x[0],x[1],f(x[2])); ys=None if y is None else (y[0],y[1],f(y[2]))
                if s==p and xs and ys and xs!=ys: ok=False
                u[(s,b)]=xs or ys
        if ok and all(v is not None for v in u.values()): yield p,q,u
def normalform(u):
    st=sorted(set(k[0] for k in u)); best=None
    ziel='ABCDEF'[:len(st)]
    for perm in itertools.permutations(ziel):
        m=dict(zip(st,perm))
        for mir in (0,1):
            key=tuple(sorted(((m[s],b),(x[0],('L' if x[1]=='R' else 'R') if mir else x[1],m[x[2]])) for (s,b),x in u.items()))
            if best is None or key<best: best=key
    names=ziel; return '_'.join(''.join(''.join(dict(best)[(s,b)]) for b in (0,1)) for s in names)
if __name__=='__main__':
    zeilen=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    for n in map(int,sys.argv[2:]):
        tm=zeilen[n-1]; qs=list(quotienten(parse(tm)))
        print(n, tm, '->', [(p+q, normalform(u)) for p,q,u in qs] or 'keine Rueckfuehrung')
