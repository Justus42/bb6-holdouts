"""Wendet vsfam.vs_familie auf alle beobachteten Rueckfaelle an (je Kern: richtig / falsch).
Aufruf: python3 abdeck.py <rueckfall-Dateien>"""
import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formen import saetze, kern
from vsfam import vs_familie
from collections import Counter
C=Counter(); T=Counter()
for fn in sys.argv[1:]:
    for n,art,X,xt,Y,yt in saetze(fn):
        k=kern(art,X,xt,Y,yt)
        T[k]+=1
        if art.startswith('na') and xt=='':
            P=vs_familie(X)
            if P is not None:
                C[(k,'ok' if (P==Y and yt=='') else 'FALSCH')]+=1
for k,v in T.most_common(): print('%5d %-28s  VS-Familie: ok %d falsch %d'%(v,k,C[(k,'ok')],C[(k,'FALSCH')]))
