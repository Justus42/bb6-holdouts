# Programm A (rekursiv, Besuch fuer Besuch): prueft fuer alle Woerter bis Laenge N (rechts davon Nullen)
#   L1: bei jeder Ankunft eines Besuchs an Zelle p ist die Zelle p-1 eine 0 (p=0: links ist Band-0)
#   C2: jedes Paar 11, das waehrend eines Besuchs entsteht, entsteht durch ein Ende 0->1 an i mit Zelle i+1 = 1
#   C1: hat w kein 111 und enthaelt V(w) ein 111 oder trifft der Besuch 111, dann gab es ein Ende 0->1 an i
#       mit Zellen i+1, i+2 = 1 1 (Ende auf 0 direkt vor 11)
# Regeln von 396: V(0x)=1x, V(100x)=V(110x)=000V(x), V(1010x)=1010V(V(x)), V(1011x)=0001x, V(111x)=Treffer.
# FEHLER=1: Regel V(100x)=001V(x) (Negativkontrolle: L1/C2 muessen anschlagen).
import itertools, os, sys
sys.setrecursionlimit(10000)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
FEHLER = os.environ.get('FEHLER') == '1'
class Treffer(Exception): pass
def besuch(w, p, ev):
    while len(w) < p + 5: w.append(0)
    links = w[p-1] if p > 0 else 0
    if links != 0: ev['L1'] += 1
    a, b, c, d = w[p:p+4]
    if a == 0:
        if p > 0 and w[p-1] == 1: ev['C2'] += 1
        ev['vor11'] += (b == 1 and c == 1); w[p] = 1; return
    if b == 1 and c == 1: raise Treffer
    if c == 0:
        if FEHLER and b == 0: w[p], w[p+1], w[p+2] = 0, 0, 1
        else: w[p], w[p+1], w[p+2] = 0, 0, 0
        besuch(w, p + 3, ev); return
    if d == 0: besuch(w, p + 4, ev); besuch(w, p + 4, ev); return
    w[p], w[p+1], w[p+2] = 0, 0, 0          # 1011 -> 0001
def hat111(w): return any(w[i] and w[i+1] and w[i+2] for i in range(len(w) - 2))
zahl = dict(woerter=0, ohne111=0, neu111=0, neu111_vor11=0, C1_verstoss=0, L1=0, C2=0, treffer=0)
for n in range(0, N + 1):
    for bits in itertools.product((0, 1), repeat=n):
        if n and bits[-1] == 0: continue          # kanonisch: kein Schluss-0 (rechts stehen ohnehin Nullen)
        zahl['woerter'] += 1
        w = list(bits); ev = dict(L1=0, C2=0, vor11=0); t = False
        try: besuch(w, 0, ev)
        except Treffer: t = True
        zahl['L1'] += ev['L1']; zahl['C2'] += ev['C2']; zahl['treffer'] += t
        if not hat111(list(bits) + [0, 0]):
            zahl['ohne111'] += 1
            if t or hat111(w):
                zahl['neu111'] += 1
                if ev['vor11']: zahl['neu111_vor11'] += 1
                else: zahl['C1_verstoss'] += 1
print(('FEHLER=1 ' if FEHLER else '') + f'N={N}', ' '.join(f'{k}={v}' for k, v in zahl.items()))
