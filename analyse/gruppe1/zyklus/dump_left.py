import sys
from snap import snaps
from canon import canon, show
from automat import step
start=ord(sys.argv[1])-65; N=int(float(sys.argv[2]))
prev=None
for n,r,b in snaps(start,N):
    t,tl=canon(b)
    if prev and prev[1]==r+1:
        pt=prev[2]; u,why=step(pt)
        if u!=t:
            # gemeinsames Ende suchen
            k=0
            while k<min(len(pt),len(t)) and pt[-1-k]==t[-1-k]: k+=1
            print(n,why,'|',show(pt[:len(pt)-k]),'->',show(t[:len(t)-k]),'| next',show(pt[len(pt)-k:len(pt)-k+1]))
    prev=(n,r,t)
