# Maschinen und Besuchs-Simulator (Thread 396, 25.11.2026). visit(): Kopf in C auf Zelle 0, Zelle -2 = x, Zelle -1 = 0;
# Ende, wenn der Kopf in A auf Zelle -2 steht (Besuchsgesetz aus busycoq PR #59, Definition Vis).
import sys, itertools
def parse(s):
    T={}
    for i,part in enumerate(s.split('_')):
        q='ABCDEF'[i]
        for b in (0,1):
            t=part[3*b:3*b+3]
            T[(q,b)]=None if t[2] in '-HZ' else (int(t[0]), 1 if t[1]=='R' else -1, t[2])
    return T
M={
 '88':'1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD1RB_0RC---',
 '312':'1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD1RF_0RC---',
 '449':'1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD0LC_0RC---',
 '396':'1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---',
 '396.2':'1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD1RB_0LA---',
}
def visit(T, w, x=0, maxsteps=10**6, log=None):
    """head in C at cell 0, tape: cell -2 = x, cell -1 = 0, w at 0.., zeros after.
    returns ('ret', newtape-from-0) when head at -2 in state A, or ('halt',...), ('left',..), ('limit',)"""
    tape={-2:x,-1:0}
    for i,b in enumerate(w): tape[i]=b
    p=0;q='C';n=0
    while n<maxsteps:
        if p==-2 and q=='A':
            assert tape[-1]==0 and tape[-2]==x
            hi=max(tape); out=[tape.get(i,0) for i in range(0,hi+1)]
            return ('ret',out,n)
        if p<-2: return ('left',p,q,n)
        b=tape.get(p,0)
        t=T[(q,b)]
        if log is not None: log.append((q,b,p))
        if t is None: return ('halt',p,q,n)
        tape[p]=t[0]; p+=t[1]; q=t[2]; n+=1
    return ('limit',)
