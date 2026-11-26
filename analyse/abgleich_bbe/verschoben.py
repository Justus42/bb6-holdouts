#!/usr/bin/env python3
# Thread "Abgleich mit busy-beaver-explorer" (26.11.2026): prueft 123 und 223 in der um eine Zelle verschobenen Lage
# (Fuehrungszelle 0 vor dem Wort, Eintritt C = Form V bzw. F = Form W, Rueckkehr A). Ausgabe [richtig, geprueft] je Regel.
# Aufruf aus dem Repo-Wurzelordner: python3 analyse/abgleich_bbe/verschoben.py
import sys, random
sys.path.insert(0, '/home/user/bb6-holdouts/analyse/besuchsgesetz')
from suche_a import lies, besuch
random.seed(2)
rs = [''.join(random.choice('01') for _ in range(random.randint(0,8))) for _ in range(300)]
def t(w): return tuple(int(ch) for ch in w.rstrip('0'))
def s(v): return ''.join(map(str,v))
for n,m in [(123,'1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA0RE_1RE---'),(223,'1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA1RB_1RE---')]:
    T = lies(m, False)
    def VV(q, w, x):  # visit with lead 0 in state q (C=2,F=5): returns s' or status
        r = besuch(T, t('0'+w) if ('0'+w).rstrip('0') else (), x, q, 0)
        if not isinstance(r, tuple): return r
        o = s(r)
        if not o.startswith('0') and o!='': return 'lead!'
        return o[1:] if o else ''
    res = {}
    def chk(k, ok):
        a=res.setdefault(k,[0,0]); a[1]+=1; a[0]+= (1 if ok else 0)
    tot=0
    for r in rs:
      for x in (0,1):
        tot+=1
        for q,nm in [(2,'V'),(5,'W')]:
            v = lambda w: VV(q,w,x)
            chk(nm+':0', v('0'+r).rstrip('0') == ('1'+r).rstrip('0'))
            vr = VV(2, r, x)
            if isinstance(vr,str) and vr not in ('halt','links','grenze','falsch_zurueck','lead!'):
                chk(nm+':100', v('100'+r).rstrip('0') == ('000'+vr).rstrip('0'))
                chk(nm+':110', v('110'+r).rstrip('0') == ('000'+vr).rstrip('0'))
                wr = VV(5, r, x)
                if isinstance(wr,str) and wr not in ('halt','links','grenze','falsch_zurueck','lead!'):
                    vwr = VV(2, wr, x)
                    if isinstance(vwr,str) and vwr not in ('halt','links','grenze','falsch_zurueck','lead!'):
                        chk(nm+':1010(W,V)', v('1010'+r).rstrip('0') == ('1010'+vwr).rstrip('0'))
                vvr = VV(2, vr, x)
                if isinstance(vvr,str) and vvr not in ('halt','links','grenze','falsch_zurueck','lead!'):
                    chk(nm+':1010(V,V)', v('1010'+r).rstrip('0') == ('1010'+vvr).rstrip('0'))
            chk(nm+':1011halt', v('1011'+r)=='halt')
    print(n, tot, res)
