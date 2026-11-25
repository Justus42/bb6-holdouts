# Thread "396, Teil 2": Rueckwaerts-Analyse "Wie kann 111 am Blockanfang entstehen?" (Gesetz von 396)
#   V(0x)=1x, V(100x)=V(110x)=000 V(x), V(1010x)=1010 V(V(x)), V(1011x)=0001x, V(111x)=Halt
# Teil A (vollstaendig): fuer jedes Wort der Laenge <= 8 am Blockanfang p und jede Besuchszahl n = 1..12:
#   haelt ein Besuch genau AM Block p (nicht weiter rechts), und wie sah das Wort bei der ersten Ankunft aus?
# Teil B (Stichprobe, Besuch fuer Besuch in echter Reihenfolge): 3000 Zufallswoerter, je bis 25 Runden:
#   B1: bei der ersten Ankunft an einem Blockanfang p sind alle Zellen >= p in dieser Runde unberuehrt;
#   B2: jedes "11" im Wort am Rundenende stand schon im Startwort (beide Zellen unberuehrt) oder seine linke Zelle
#       wurde in dieser Runde durch einen Halt-Schritt 0->1 gesetzt und die rechte ist unberuehrt;
#   B3: Halt und 1011-Ereignis kommen nur in Runden vor, deren Startwort "10 s" ein "11" enthaelt.
# Negativkontrolle: FEHLER=1 aendert die 1011-Regel zu 0111x; B2 muss dann Verstoesse melden.
import itertools, os, random, sys
sys.setrecursionlimit(100000)
FEHLER = os.environ.get('FEHLER') == '1'
class Halt(Exception):
    def __init__(self, pos): self.pos = pos

def runde(w, protokoll):
    """ein Besuch ab Zelle 0 (in echter Reihenfolge); protokolliert beruehrte Zellen und Erstankuenfte"""
    beruehrt = set(); erste = {}; k = []
    def setz(i, v): beruehrt.add(i); w[i] = v
    def besuch(i):
        while len(w) < i + 4: w.append(0)
        if i not in erste: erste[i] = (tuple(w[i:i+4]), any(j >= i for j in beruehrt))
        a, b, c, d = w[i:i+4]
        if a == 0: setz(i, 1); return
        if b == 1 and c == 1: raise Halt(i)
        if c == 0: setz(i, 0); setz(i+1, 0); setz(i+2, 0); besuch(i+3); return
        if d == 0: besuch(i+4); besuch(i+4); return
        k.append(i)
        if FEHLER: setz(i, 0); setz(i+1, 1); setz(i+2, 1)
        else: setz(i, 0); setz(i+1, 0); setz(i+2, 0)
    besuch(0)
    return beruehrt, erste, k

# ---- Teil A: Halt am Block p, abhaengig vom Wort bei erster Ankunft und n
def block_halt(wort, n):
    """n Besuche nacheinander ab Zelle 0 auf wort+0^inf; Rueckgabe: Halt am Block 0? (Halts weiter rechts zaehlen nicht)"""
    w = list(wort) + [0] * 40
    def besuch(i, oben):
        a, b, c, d = w[i:i+4]
        if a == 0: w[i] = 1; return
        if b == 1 and c == 1: raise Halt(i)
        if c == 0: w[i] = w[i+1] = w[i+2] = 0; besuch_rest(i+3); return
        if d == 0: besuch_rest(i+4); besuch_rest(i+4); return
        w[i] = w[i+1] = w[i+2] = 0
    def besuch_rest(i):    # weiter rechts: Halts dort ignorieren (gehoeren zu anderen Bloecken), Wirkung nur auf Zellen >= i
        try:
            if i < len(w) - 8: besuch(i, False)
        except Halt: pass
    for _ in range(n):
        try: besuch(0, True)
        except Halt as h:
            return h.pos == 0
    return False
muster = {}
for L in range(0, 9):
    for wort in itertools.product((0, 1), repeat=L):
        for n in range(1, 13):
            if block_halt(wort, n):
                key = ''.join(map(str, wort[:3])).ljust(3, '0')
                muster.setdefault(key, set()).add(n)
print('Teil A: Woerter am Blockanfang (erste 3 Zellen), bei denen ein Besuch am Block selbst haelt, und die Besuchszahlen n:')
for key in sorted(muster): print('  ', key, '-> n in', (min(muster[key]), max(muster[key])), 'Anzahl verschiedener n:', len(muster[key]))

# ---- Teil B
v1 = v2 = v3 = 0; runden = 0; n11 = 0; kr = 0; hr = 0
for seed in range(3000):
    random.seed(seed)
    s = [1] + [random.choice([0, 0, 0, 1]) for _ in range(random.randint(3, 30))]
    for r in range(25):
        w = [1, 0] + s; w0 = list(w)
        hat11 = any(w0[i] and w0[i+1] for i in range(len(w0) - 1))
        try:
            beruehrt, erste, k = runde(w, True)
        except Halt:
            hr += 1
            if not hat11: v3 += 1
            break
        if k:
            kr += 1
            if not hat11: v3 += 1
        v1 += sum(1 for (_, x) in erste.values() if x)
        while w and w[-1] == 0: w.pop()
        g = lambda j: w0[j] if j < len(w0) else 0
        for i in range(len(w) - 1):
            if w[i] and w[i+1]:
                n11 += 1
                ok = (i not in beruehrt and i+1 not in beruehrt) or (i in beruehrt and g(i) == 0 and i+1 not in beruehrt)
                if not ok: v2 += 1
        s = w; runden += 1
print(f'Teil B{" (FEHLER=1)" if FEHLER else ""}: {runden} Runden, {n11} Vorkommen von 11 am Rundenende, {kr} Runden mit 1011, {hr} Halts')
print(f'  B1 Verstoesse (Zelle >= p schon beruehrt bei Erstankunft): {v1}')
print(f'  B2 Verstoesse (Herkunft eines 11): {v2}')
print(f'  B3 Verstoesse (1011 oder Halt ohne 11 im Startwort): {v3}')
