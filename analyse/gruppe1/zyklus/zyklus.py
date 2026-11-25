"""Zyklusfunktion f: Token-Liste am Zyklusanfang -> Token-Liste am naechsten Zyklusanfang.
Pruefung gegen die Zeilen von zweitpruefung.c liste (Zyklusanfaenge wie gruppe1.py)."""
import sys
from collections import Counter
from pairs import lese
from blk import bits
from canon import canon, show
from automat import step, rand2
def zyklus(T, log=None):
    T=list(T)
    T,why=rand2(T,2)                        # Randschritt waehrend des Fressens
    if T is None: return None,'rand_fressen:'+why
    (s3,e3),(s2,b),(s1,a)=T[-3:]
    x=a+4*b+3                               # Fressregel
    if s1!='1' or e3<1: return None,'fressen'
    E=T[:-3]+[(s3,e3-1),('0',0),('1',x)]
    (s4,e4),(s3_,e3_)=E[-4:-2]
    if e4<1: return None,'J'
    F=E[:-4]+[(s4,e4-1),('1',e3_+2)]       # Uebergang J
    for i in range(x-1):                    # x-1 Phasen des langen Laufs
        F,why=step(F)
        if F is None: return None,'phase:'+why
    F,why=rand2(F,1)                        # Randschritt auf dem Rueckweg
    if F is None: return None,'rand_rueck:'+why
    return F,'ok'
if __name__=='__main__':
    fn=sys.argv[1]; L,steps,anf=lese(fn)
    C=Counter(); ex=[]
    for i in range(len(anf)-1):
        T,tl=canon(bits(L[anf[i]])); N,tn=canon(bits(L[anf[i+1]]))
        U,why=zyklus(T)
        ok = U==N
        C[why if U is None else ('ok' if ok else 'falsch')]+=1
        if not ok and len(ex)<30: ex.append((steps[anf[i]],why))
    print(fn,len(anf)-1,'Zyklen:',dict(C))
    for e in ex: print(' ',e)
