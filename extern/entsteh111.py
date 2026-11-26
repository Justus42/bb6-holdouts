# Wann erzeugt ein Besuch (Regeln von 396) ein neues 111 bzw. ein neues 11?
import itertools, collections
class Halt(Exception): pass
def V(w, pos, ev):   # gibt neues Wort zurueck; ev sammelt (Art, absolute Position)
    g=lambda i: w[i] if i<len(w) else 0
    if g(0)==0: ev.append(('T',pos)); return [1]+w[1:]
    if g(1)==1 and g(2)==1: raise Halt()
    if (g(1),g(2)) in ((0,0),(1,0)): return [0,0,0]+V(w[3:],pos+3,ev)
    if g(3)==0:
        y1=V(w[4:],pos+4,ev); return [1,0,1,0]+V(y1,pos+4,ev)
    ev.append(('E',pos)); return [0,0,0,1]+w[4:]
def has(w,p):
    s=''.join(map(str,w)); return p in s
cnt=collections.Counter(); bsp={}
for k in range(0,15):
    for w in itertools.product((0,1),repeat=k):
        w=list(w)
        if k and w[-1]==0: continue
        if has(w,'111'): continue
        ev=[]
        try: y=V(w,0,ev)
        except Halt: continue
        if has(y,'111'):
            # Ursache: letzter Endpunkt T an Position p; steht dort vorher 0 gefolgt von 11?
            T=[p for a,p in ev if a=='T']; E=[p for a,p in ev if a=='E']
            # pruefe fuer jedes T, ob im Wort zu diesem Zeitpunkt ...0[0]11 stand: einfacher Test am Ergebnis
            ys=''.join(map(str,y)); i=ys.find('111')
            art='T vor 11' if any(p==i for p in T) else ('T nach/zwischen' if any(i<p<=i+2 for p in T) else ('E' if E else 'sonst'))
            cnt[art]+=1; bsp.setdefault(art,(''.join(map(str,w)),ys))
print('Woerter ohne 111, deren Besuch ein 111 erzeugt, nach Ursache:', dict(cnt)); print(bsp)
