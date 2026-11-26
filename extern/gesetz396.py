# Unabhaengige Pruefung des Besuchsgesetzes fuer 396 gegen direkte TM-Simulation.
import itertools, random, sys
S='ABCDEF'
def parse(s):
    t={}
    for i,p in enumerate(s.split('_')):
        for b in range(2):
            x=p[3*b:3*b+3]; t[(S[i],b)]=None if x=='---' else (int(x[0]),x[1],x[2])
    return t
T396=parse('1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---')
T88 =parse('1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD1RB_0RC---')
class Halt(Exception): pass
def V(w, rule1011):          # w: Liste von Bits, rechts mit Nullen aufgefuellt gedacht
    g=lambda i: w[i] if i<len(w) else 0
    if g(0)==0: return [1]+w[1:]
    if g(1)==1 and g(2)==1: raise Halt()                       # 111
    if (g(1),g(2))==(0,0) or (g(1),g(2))==(1,0): return [0,0,0]+V(w[3:],rule1011)   # 100, 110
    if g(3)==0: return [1,0,1,0]+V(V(w[4:],rule1011),rule1011)  # 1010
    if rule1011=='halt': raise Halt()
    return [0,0,0,1]+w[4:]                                       # 1011 bei 396
def norm(w):
    w=list(w)
    while w and w[-1]==0: w.pop()
    return w
def visit_tm(t, w, left, maxs=10**6):
    # Band: ... left, 0 an Position 0, Strom ab Position 1; Kopf in C auf Position 1.
    tape={-(i+1):b for i,b in enumerate(left)}; tape[0]=0
    for i,b in enumerate(w): tape[1+i]=b
    pos=1; q='C'
    for n in range(maxs):
        v=t[(q,tape.get(pos,0))]
        if v is None: return 'HALT',None,n
        tape[pos]=v[0]; pos+=1 if v[1]=='R' else -1; q=v[2]
        if pos==-1 and q=='A':
            mx=max([k for k,b in tape.items() if b] + [0])
            return 'OK',(tape.get(0,0),[tape.get(i,0) for i in range(1,mx+1)],[tape.get(-(i+1),0) for i in range(len(left))]),n+1
        if pos<0: return 'RAUS',(q,pos),n
    return 'ZEIT',None,maxs
def check(t, rule, L, name):
    bad=0; n=0; halts=0
    random.seed(1)
    for k in range(0,L+1):
        for w in itertools.product((0,1),repeat=k):
            if k and w[-1]==0: continue          # kanonisch: kein Null-Ende (Auffuellung ist ohnehin 0)
            w=list(w); left=[random.randint(0,1) for _ in range(6)]
            try: exp=('OK',norm(V(w,rule)))
            except Halt: exp=('HALT',None)
            except RecursionError: exp=('REK',None)
            r=visit_tm(t,w,left); n+=1
            got=(r[0], norm(r[1][1]) if r[0]=='OK' else None)
            ok = got==exp and (r[0]!='OK' or (r[1][0]==0 and r[1][2]==left))
            if exp[0]=='HALT': halts+=1
            if not ok:
                bad+=1
                if bad<=5: print('  ABWEICHUNG',name,''.join(map(str,w)),'erwartet',exp[0],''.join(map(str,exp[1] or [])),'TM',r[0],''.join(map(str,got[1] or [])) if got[1] is not None else r[1])
    print(f'{name}: {n} Woerter bis Laenge {L}, davon {halts} mit erwartetem Halt, Abweichungen: {bad}')
L=int(sys.argv[1])
check(T396,'396',L,'396 mit Regel 1011->0001, Halt bei 111')
check(T396,'halt',L,'NEGATIVKONTROLLE 396 mit Halt bei 1011')
check(T88,'halt',L,'88 mit Halt bei 1011 (wie PR 59)')
