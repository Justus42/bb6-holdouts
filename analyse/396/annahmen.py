# Die zwoelf Annahmen von busycoq PR #59 (Section Gen) fuer 396 durch Ausfuehren pruefen (Thread "396, Teil 2").
# Endliche Pruefung: alle Woerter bis Laenge L hinter dem Praefix, beide Werte der Zelle x. Kein Beweis, nur Stichprobe
# ueber alle kurzen Woerter; in PR #59 werden die Annahmen mit der Taktik `law` symbolisch bewiesen.
# Aufruf: python3 annahmen.py <maschine> [L]   (maschine: 396, 88, ...; Negativkontrolle: 88 muss bei hv_111 / Ersatzregel
# und 396 bei hv_1011 scheitern)
import sys, itertools
from tm import parse, M, visit
name = sys.argv[1]; L = int(sys.argv[2]) if len(sys.argv) > 2 else 8
T = parse(M[name])
def strip(w):
    w = list(w)
    while w and w[-1] == 0: w.pop()
    return w
def V(w, x):
    r = visit(T, list(w), x, maxsteps=10**6)
    if r[0] == 'ret': return ('ret', strip(r[1]))
    return (r[0],)
def words(n):
    for k in range(n + 1):
        for t in itertools.product((0, 1), repeat=k): yield list(t)
B = lambda s: [int(c) for c in s]
res = {}
def check(name_, ok):
    res.setdefault(name_, [0, 0]); res[name_][0 if ok else 1] += 1
for r in words(L):
    for x in (0, 1):
        vr = V(r, x)
        # vis_0 .. vis_L
        check('vis_0', V(B('0') + r, x) == ('ret', strip(B('1') + r)))
        if vr[0] == 'ret':
            r1 = vr[1]
            check('vis_H', V(B('100') + r, x) == ('ret', strip(B('000') + r1)))
            check('vis_G', V(B('110') + r, x) == ('ret', strip(B('000') + r1)))
            vr1 = V(r1, x)
            if vr1[0] == 'ret':
                check('vis_L', V(B('1010') + r, x) == ('ret', strip(B('1010') + vr1[1])))
            elif vr1[0] == 'halt':
                check('hv_L2', V(B('1010') + r, x)[0] == 'halt')
        if vr[0] == 'halt':
            for p, k in (('100', 'hv_H'), ('110', 'hv_G'), ('1010', 'hv_L1')):
                check(k, V(B(p) + r, x)[0] == 'halt')
        check('hv_1011 (PR #59: Besuch auf 1011 haelt)', V(B('1011') + r, x)[0] == 'halt')
        check('Ersatz 396: V(1011x) = 0001x', V(B('1011') + r, x) == ('ret', strip(B('0001') + r)))
        check('Ersatz 396: hv_111 (Besuch auf 111 haelt)', V(B('111') + r, x)[0] == 'halt')
# Runde: LE s = 0^inf A> 1 0 s.  round_step: LE s ->+ LE V(10 s); round_halt: V(10 s) haelt -> TM haelt.
def tm_from_LE(s, maxsteps=10**6):
    tape = {0: 1, 1: 0}
    for i, b in enumerate(s): tape[2 + i] = b
    p = 0; q = 'A'; n = 0
    while n < maxsteps:
        if n > 0 and q == 'A' and tape.get(p, 0) == 1 and tape.get(p + 1, 0) == 0 and all(v == 0 for k, v in tape.items() if k < p):
            hi = max(k for k, v in tape.items() if v) if any(tape.values()) else p
            return ('LE', strip([tape.get(i, 0) for i in range(p + 2, hi + 1)]))
        b = tape.get(p, 0); t = T[(q, b)]
        if t is None: return ('halt',)
        tape[p] = t[0]; p += t[1]; q = t[2]; n += 1
    return ('limit',)
for s in words(L):
    v = V(B('10') + s, 0)
    e = tm_from_LE(s)
    if v[0] == 'ret': check('round_step', e == ('LE', v[1]))
    elif v[0] == 'halt': check('round_halt', e == ('halt',))
# blank_start: ab Leerband erreicht die Maschine LE(1)
tape = {}; p = 0; q = 'A'; ok = False
for n in range(1000):
    if n > 0 and q == 'A' and tape.get(p, 0) == 1 and tape.get(p + 1, 0) == 0 and all(v == 0 for k, v in tape.items() if k < p):
        hi = max(k for k, v in tape.items() if v); ok = strip([tape.get(i, 0) for i in range(p + 2, hi + 1)]) == [1]; break
    b = tape.get(p, 0); t = T[(q, b)]
    if t is None: break
    tape[p] = t[0]; p += t[1]; q = t[2]
check('blank_start', ok)
print(f"Maschine {name} ({M[name]}), Woerter bis Laenge {L}:")
for k, (g, f) in res.items():
    print(f"  {k:45s} gilt {g:6d}  verletzt {f:6d}  -> {'GILT' if f == 0 and g > 0 else ('KEIN FALL' if g + f == 0 else 'FALSCH')}")
