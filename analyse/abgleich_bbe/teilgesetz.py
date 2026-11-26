#!/usr/bin/env python3
# Thread "Abgleich mit busy-beaver-explorer" (26.11.2026): prueft 396, 471, 123, 223 gegen das Besuchsgesetz in
# unserer Lage (Kopf auf erster Wortzelle, links 0 und x), Eintritt C oder F, Rueckkehr A. 300 Zufallsreste bis Laenge 8.
# Aufruf aus dem Repo-Wurzelordner: python3 analyse/abgleich_bbe/teilgesetz.py
import sys, itertools, random
sys.path.insert(0, '/home/user/bb6-holdouts/analyse/besuchsgesetz')
from suche_a import lies, besuch
M = {396:'1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---', 471:'1RB0LB_0RC0LD_1LD1RE_0LA0RB_0RD1RF_1LA---',
     123:'1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA0RE_1RE---', 223:'1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA1RB_1RE---'}
def tr(w): return ''.join(map(str,w)) if isinstance(w,tuple) else w
def V(T,w,c,a,x=0): return besuch(T, tuple(int(ch) for ch in w), x, c, a)
random.seed(1)
rs = [''.join(random.choice('01') for _ in range(random.randint(0,8))) for _ in range(300)]
for n,s in M.items():
    T = lies(s, False)
    for c,a in [(2,0),(5,0)]:
        ok = {k:0 for k in ['0','100','110','1010','1011','111','1010VW']}; tot=0
        for r in rs:
          for x in (0,1):
            tot+=1
            v = lambda w: besuch(T, tuple(int(ch) for ch in w), x, c, a)
            vr = v(r)
            if v('0'+r) == tuple(int(ch) for ch in ('1'+r).rstrip('0')): ok['0']+=1
            if isinstance(vr,tuple):
                if v('100'+r)==tuple(int(ch) for ch in ('000'+tr(vr)).rstrip('0')): ok['100']+=1
                if v('110'+r)==tuple(int(ch) for ch in ('000'+tr(vr)).rstrip('0')): ok['110']+=1
                vvr = v(tr(vr))
                if isinstance(vvr,tuple) and v('1010'+r)==tuple(int(ch) for ch in ('1010'+tr(vvr)).rstrip('0')): ok['1010']+=1
            if v('1011'+r)==tuple(int(ch) for ch in ('0001'+r).rstrip('0')): ok['1011']+=1
            if v('111'+r)=='halt': ok['111']+=1
        print(n, 'c=%s a=%s'%('ABCDEF'[c],'ABCDEF'[a]), {k:'%d/%d'%(v_,tot) for k,v_ in ok.items() if k!='1010VW'})
    # extra: 471 110 rule
    if n==471:
        c,a=2,0
        cnt=sum(1 for r in rs for x in (0,1) if besuch(T,tuple(int(ch) for ch in '110'+r),x,c,a)==tuple(int(ch) for ch in ('001'+r).rstrip('0')))
        print('  471 V(110r)=001r:',cnt,'/',2*len(rs))
