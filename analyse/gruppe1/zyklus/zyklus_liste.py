"""Pro Zyklusanfang eine Zeile im Format von c/zyklus2.c, aber aus den Zeilen von zweitpruefung.c (Textliste)
und der Python-Zyklusfunktion. Negativkontrolle: ZYK_FEHLER=fress|n1|j."""
import sys, os
import automat, zyklus as Z
from pairs import lese
from blk import bits
from canon import canon
F=os.environ.get('ZYK_FEHLER','')
if F=='n1':
    alt=automat.step
    def kaputt(t):
        u,w=alt(t)
        if w=='N1':
            f=automat.frontier(t); u=list(u); u[f]=('1',u[f][1]+2)
        return u,w
    Z.step=kaputt; automat.step=kaputt
fn=sys.argv[1]; L,steps,anf=lese(fn)
def text(c):
    t=L[c].split(' lead ',1)[1].split()[2:]; return [int(x) for x in t[0::2]],t[1::2]
for i,c in enumerate(anf):
    el,sp=text(c)
    ag=el[0]%2==0; alle=ag and all(v%2==0 for v in el) and all(s=='|' for s in sp)
    line=f"{steps[c]} a_gerade={int(ag)} alles_gerade={int(alle)}"
    if i>0:
        T,_=canon(bits(L[anf[i-1]])); N,_=canon(bits(L[c]))
        if F=='fress': T=T[:-1]+[(T[-1][0],T[-1][1]-2)]
        if F=='j': T=T[:-3]+[(T[-3][0],T[-3][1]-1)]+T[-2:]
        U,why=Z.zyklus(T)
        line+=" vorheriger_zyklus="+("na" if U is None else ("ok" if U==N else "falsch"))
    print(line)
