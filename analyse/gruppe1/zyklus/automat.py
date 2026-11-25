"""Phasen-Automat auf kanonischen Token (bit, n): Band = bit W^n bit W^n ..., W = 011.
Regeln (je Phase genau eine):
  N1  Grenze (0,k), k gerade            -> (1,k+1)
  N2  G=(s,g>=1), Grenze (1,k), k gerade -> (s,g-1), (0,k+2)
  N2s G=(s,g>=1), Grenze (0,k), k ungerade -> (s,g-1), (0,k+2)
  UA  G=(s,g>=1), (1,0), Grenze (0,k), k ungerade -> (s,g-1), (0,0), (1,k+2)     [alte Marke wird uebersprungen]
  LE  Grenze steht ganz links hinter (1,0): (1,0),(s,k) -> (1,k+2)              [linkes Ende erreicht]
  VS  (1,1)^(f/2+3), (1,0), Grenze (1,f), f gerade, (s,p) -> (1,0),(0,2),(1,3)^((f-2)/2),(1,2),(0,p+4)   [Verschmelzen an alter Marke]
  LG  keine Grenze mehr (alles ungerade mit Trenner 1) -> (1,1) links anfuegen   [Band waechst links]
Grenze = rechtestes Token ausser dem letzten mit Trenner 0 oder gerader Laenge.
"""
def frontier(t):
    for i in range(len(t)-2,-1,-1):
        s,n=t[i]
        if s=='0' or n%2==0: return i
    return None
def step(t):
    f=frontier(t)
    if f is None:
        return [('1',1)]+list(t), 'LG'
    s,k=t[f]
    if s=='0' and k%2==0:
        u=list(t); u[f]=('1',k+1); return u,'N1'
    if f==0:
        if t[0]==('1',0):
            u=list(t[1:]); s1,k1=u[0]; u[0]=('1',k1+2); return u,'LE'
        return None,'links?'
    sg,g=t[f-1]
    if f==1 and t[0]==('1',0) and s=='0' and k%2==1:
        u=list(t[1:]); u[0]=('1',k+2); return u,'LE'
    if g>=1 and ((s=='0' and k%2==1) or (s=='1' and k%2==0)):
        u=list(t); u[f-1]=(sg,g-1); u[f]=('0',k+2); return u,('N2s' if s=='0' else 'N2')
    if s=='0' and k%2==1 and t[f-1]==('1',0) and f>=2 and t[f-2][1]>=1:
        u=list(t); s2,g2=t[f-2]; u[f-2]=(s2,g2-1); u[f-1]=('0',0); u[f]=('1',k+2); return u,'UA'
    if s=='1' and k%2==0 and k>=2 and t[f-1]==('1',0) and f+1<len(t):
        m=k//2+3
        if f-1-m>=0 and all(x==('1',1) for x in t[f-1-m:f-1]):
            sp,p=t[f+1]
            new=[('1',0),('0',2)]+[('1',3)]*((k-2)//2)+[('1',2),('0',p+4)]
            return list(t[:f-1-m])+new+list(t[f+2:]),'VS'
        return None,'VS-zuwenig'
    return None,'Sonder'

def irregular(tok):
    s,n=tok
    return s=='0' or n%2==0
def rand(t, rechts=2):
    """Randschritt bei Fressphase und Rueckweg: Automatenschritt an der linken Marke.
    Marke = erste Gruppe unregelmaessiger Token (ohne die letzten `rechts` Token); Grenze = ihr rechtes Ende.
    Ohne Marke: (1,1) links anfuegen."""
    m=len(t)-rechts
    i=0
    while i<m and not irregular(t[i]): i+=1
    if i>=m:
        return [('1',1)]+list(t),'LG'
    j=i
    while j+1<m and irregular(t[j+1]): j+=1
    # Teil-Liste bis j+1 (plus ein Token rechts fuer VS) mit dem normalen Schritt behandeln
    head=list(t[:j+1])+[('1',1)]   # Platzhalter-Token rechts, damit step die Grenze bei j sieht
    u,why=step(head+[('1',2)]) if False else (None,None)
    # direkte Anwendung: die Grenze ist j
    return _step_at(t,j)
def _step_at(t,f):
    s,k=t[f]
    if s=='0' and k%2==0:
        u=list(t); u[f]=('1',k+1); return u,'N1'
    if f==0:
        if t[0]==('1',0):
            u=list(t[1:]); s1,k1=u[0]; u[0]=('1',k1+2); return u,'LE'
        return None,'links?'
    sg,g=t[f-1]
    if f==1 and t[0]==('1',0) and s=='0' and k%2==1:
        u=list(t[1:]); u[0]=('1',k+2); return u,'LE'
    if g>=1 and ((s=='0' and k%2==1) or (s=='1' and k%2==0)):
        u=list(t); u[f-1]=(sg,g-1); u[f]=('0',k+2); return u,('N2s' if s=='0' else 'N2')
    if s=='0' and k%2==1 and t[f-1]==('1',0) and f>=2 and t[f-2][1]>=1:
        u=list(t); s2,g2=t[f-2]; u[f-2]=(s2,g2-1); u[f-1]=('0',0); u[f]=('1',k+2); return u,'UA'
    return None,'Sonder-Rand'

def rand2(t, rechts):
    """Randschritt = gewoehnlicher Automatenschritt, Grenze aber ohne die letzten `rechts` Token."""
    k=len(t)-rechts+1
    u,why=step(list(t[:k]))
    if u is None: return None,why
    return u+list(t[k:]),why
