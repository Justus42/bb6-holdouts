import itertools, sys
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'gesetz396.py')).read().split("L=int(sys.argv[1])")[0])
class Skip(Exception): pass
def Vb(w):
    g=lambda i: w[i] if i<len(w) else 0
    if g(0)==0: return [1]+w[1:]
    if g(1)==1 and g(2)==1: raise Skip()
    if (g(1),g(2)) in ((0,0),(1,0)): return [0,0,0]+Vb(w[3:])
    if g(3)==0: return [1,0,1,0]+Vb(Vb(w[4:]))
    raise Skip()
def visit_gen(t, w, c, a, maxs=200000):
    tape={-2:1,-1:0}
    for i,b in enumerate(w): tape[i]=b
    pos=0; q=c
    for n in range(maxs):
        v=t[(q,tape.get(pos,0))]
        if v is None: return None
        tape[pos]=v[0]; pos+=1 if v[1]=='R' else -1; q=v[2]
        if pos==-2:
            if q!=a or tape[-1]!=0 or tape[-2]!=1: return None
            mx=max([k for k,b in tape.items() if b and k>=0]+[-1]); return [tape.get(i,0) for i in range(mx+1)]
    return None
def mirror(t): return {k:(None if v is None else (v[0],'L' if v[1]=='R' else 'R',v[2])) for k,v in t.items()}
M={'123':'1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA0RE_1RE---','223':'1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA1RB_1RE---','471':'1RB0LB_0RC0LD_1LD1RE_0LA0RB_0RD1RF_1LA---','396':'1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---','110':'1RB0LB_0RC0LD_1LD1RE_0LA0RF_1RB0RD_0RB---'}
words=[list(w) for k in range(0,11) for w in itertools.product((0,1),repeat=k) if not (k and w[-1]==0)]
for n,s in M.items():
    t0=parse(s); best=None
    for mir in (0,1):
        t=mirror(t0) if mir else t0
        for c in S:
            for a in S:
                ok=tot=0
                for w in words:
                    try: e=norm(Vb(w))
                    except Skip: continue
                    tot+=1; r=visit_gen(t,w,c,a)
                    if r is not None and norm(r)==e: ok+=1
                if best is None or ok>best[0]: best=(ok,tot,c,a,mir)
    print(n, 'bestes Paar: Eintritt',best[2],'Rueckkehr',best[3],'gespiegelt' if best[4] else 'ungespiegelt', f'{best[0]}/{best[1]} Woerter gesetzestreu')
