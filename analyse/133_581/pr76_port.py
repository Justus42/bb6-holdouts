#!/usr/bin/env python3
"""Getreue Python-Portierung des Runden-Simulators aus busycoq-PR 76
(verify/M_1RB1RD_1RC1RB_1LD0RA_1RA0LE_1LF0LC_HHH1LE.v, Kopf 594cece).

Nur Analyse: Das Programm beweist nichts. Es fuehrt dieselben Rechenschritte aus wie
`run` in der Coq-Datei (gstep, macL, macR, canonL, tryJump), damit man sieht, was der
Simulator mit einem anderen Start macht. Stapel: Python-Listen, naechstes Feld zuerst.

Aufruf: pr76_port.py START RUNDEN [--tm TABELLE] [--log K]
  START = Zustand auf leerem Band (A = 581 selbst, C = 133 in 581-Koordinaten)
"""
import sys

TM581 = "1RB1RD_1RC1RB_1LD0RA_1RA0LE_1LF0LC_---1LE"


def parse(s):
    t = {}
    for i, g in enumerate(s.split('_')):
        for r in (0, 1):
            x = g[3 * r:3 * r + 3]
            t[('ABCDEF'[i], r)] = None if x[0] == '-' else (int(x[0]), x[1], x[2])
    return t


def flip(t):
    return {k: (None if v is None else (v[0], 'L' if v[1] == 'R' else 'R', v[2])) for k, v in t.items()}


# Items: ('B', s) oder ('R', w, n) mit w als Tupel
def Bit(s):
    return ('B', s)


def Run(w, n):
    return ('R', tuple(w), n)


def isbit(x, s):
    return x[0] == 'B' and x[1] == s


W = (1, 1, 0)
X = (1, 0, 0)
W110 = (0, 1, 1)
W101 = (1, 0, 1)


def segRun(T, fuel, l, r, q):
    l = list(l)
    r = list(r)
    while True:
        if fuel == 0:
            return None
        fuel -= 1
        if not r:
            return (l, q)
        s = r[0]
        a = T[(q, s)]
        if a is None:
            return None
        s2, d, q2 = a
        if d == 'R':
            l = [s2] + l
            r = r[1:]
        else:
            if not l:
                return None
            y = l[0]
            l = l[1:]
            r = [y, s2] + r[1:]
        q = q2


def cross(T, q, w, cache):
    key = (q, w)
    if key in cache:
        return cache[key]
    res = segRun(T, 200, [], w, q)
    out = None
    if res is not None and res[1] == q:
        out = tuple(res[0])
    cache[key] = out
    return out


def pushRun(w, n, s):
    if s and s[0][0] == 'R' and s[0][1] == tuple(w):
        return [('R', tuple(w), n + s[0][2])] + s[1:]
    return [('R', tuple(w), n)] + s


def unpack(w, n, f):
    return [Bit(x) for x in w] + (f if n == 1 else [('R', w, n - 1)] + f)


def dbl(T, w, n, f, b, q, cache):
    if n == 1:
        return None
    h = n // 2
    v = cross(T, q, w + w, cache)
    if v is None:
        return None
    f2 = ([('R', w, 1)] + f) if n % 2 == 1 else f
    k = len(w)
    if v[:k] == v[k:]:
        b2 = pushRun(v[:k], 2 * h, b)
    else:
        b2 = pushRun(v, h, b)
    return ('Same', f2, b2, q)


def act(o, f2, b):
    if o is None:
        return ('Halt',)
    s2, d, q2 = o
    if d == 'R':
        return ('Same', f2, [Bit(s2)] + b, q2)
    return ('Turn', b, [Bit(s2)] + f2, q2)


def gstep(T, f, b, q, cache):
    if f and f[0][0] == 'R':
        _, w, n = f[0]
        f2 = f[1:]
        w2 = cross(T, q, w, cache)
        if w2 is not None:
            return ('Same', f2, pushRun(w2, n, b), q)
        r = dbl(T, w, n, f2, b, q, cache)
        if r is not None:
            return r
        return ('Same', unpack(w, n, f2), b, q)
    if not f:
        s, f2 = 0, []
    else:
        s, f2 = f[0][1], f[1:]
    return act(T[(q, s)], f2, b)


# ---- 581-spezifisch: kanonische Phase, Zone, Sprung, Makros ----

def cbit(s, out):
    if s == 1 and len(out) >= 3 and isbit(out[0], 1) and isbit(out[1], 0) and out[2][0] == 'R':
        w, m = out[2][1], out[2][2]
        if w == W:
            return [('R', W, m + 1)] + out[3:]
        return [Bit(s)] + out
    if s == 1 and len(out) >= 5 and isbit(out[0], 1) and isbit(out[1], 0) and isbit(out[2], 1) \
            and isbit(out[3], 1) and isbit(out[4], 0):
        return pushRun(W, 2, out[5:])
    return [Bit(s)] + out


def crun(n, out):
    while True:
        if len(out) >= 3 and isbit(out[0], 1) and isbit(out[1], 1) and isbit(out[2], 0):
            n += 1
            out = out[3:]
            continue
        if out and out[0][0] == 'R':
            if out[0][1] == W:
                return [('R', W, n + out[0][2])] + out[1:]
            return [('R', W, n)] + out
        return [('R', W, n)] + out


def crun0(n, out):
    return out if n == 0 else crun(n, out)


def emit(x, out):
    if x[0] == 'B':
        return cbit(x[1], out)
    _, w, n = x
    if w == W:
        return crun(n, out)
    if w == W110:
        return cbit(0, crun0(n - 1, cbit(1, cbit(1, out))))
    if w == W101:
        return cbit(1, cbit(0, crun0(n - 1, cbit(1, out))))
    return [x] + out


def canonL(s):
    out = []
    for x in reversed(s):
        out = emit(x, out)
    return out


def wrun(n, rest):
    return rest if n == 0 else [('R', W, n)] + rest


def nb(b):
    return 0 if b else 1


def b2n(b):
    return 1 if b else 0


def sub(a, b):  # Abschneidende Subtraktion wie in N
    return a - b if a > b else 0


def encLv(lv, rest):
    out = rest
    for (b, n) in reversed(lv):
        out = [Bit(1), Bit(nb(b))] + wrun(n, out)
    return out


def encZone(n0, lv, rest):
    return [Bit(0)] + wrun(n0, encLv(lv, rest))


def parseLv(s):
    lv = []
    i = 0
    while len(s) - i >= 3 and isbit(s[i], 1) and s[i + 1][0] == 'B' and s[i + 2][0] == 'R':
        w, n = s[i + 2][1], s[i + 2][2]
        if w == W and n >= 7:
            lv.append((s[i + 1][1] == 0, n))
            i += 3
        else:
            break
    return lv, s[i:]


def parseZone(s):
    if len(s) >= 2 and isbit(s[0], 0) and s[1][0] == 'R':
        if s[1][1] == W:
            return (s[1][2], parseLv(s[2:]))
    return None


def toNaux(b, n, lv):
    # rekursiv in Coq; hier iterativ
    res = []
    cur_b, cur_n = b, n
    for (b2, n2) in lv:
        res.append((b2, sub(cur_n + b2n(cur_b), b2n(b2))))
        cur_b, cur_n = b2, n2
    return res, cur_n + b2n(cur_b)


def toN(n0, lv):
    if not lv:
        return [], 0
    b1, n1 = lv[0]
    rest, top = toNaux(b1, n1, lv[1:])
    return [(b1, sub(n0, b2n(b1)))] + rest, top


def chooseAux(ps, pw, blow, lim):
    for (b, M) in ps:
        if M < 6:
            return 0
        l = sub(pw * (2 * (M - 6) + b2n(b) + 1), 1 + blow)
        lim = l if lim is None else min(lim, l)
        blow = blow + b2n(b) * pw
        pw = 2 * pw
    v0 = sub(pw, 1 + blow)
    return v0 if lim is None else min(v0, lim)


def chooseV(ps):
    if not ps:
        return 0
    return chooseAux(ps[1:], 2, b2n(ps[0][0]), None)


def addV(V, ps):
    out = []
    for (b, M) in ps:
        c = V + b2n(b)
        out.append((c % 2 == 1, sub(M + b2n(b), (c + 1) // 2)))
        V = c // 2
    return out


def ovf(V, ps):
    for (b, _) in ps:
        V = (V + b2n(b)) // 2
    return V


def bump(d, ps):
    if not ps:
        return []
    return [(ps[0][0], ps[0][1] + d)] + ps[1:]


def after(V, ps):
    return addV(V, bump(2 * V, ps))


def physP(ps, top):
    out = []
    for i, (b, M) in enumerate(ps):
        if i == len(ps) - 1:
            out.append((b, sub(top, b2n(b))))
        else:
            b2, M2 = ps[i + 1]
            out.append((b, sub(M2 + b2n(b2), b2n(b))))
    return out


def n0of(ps):
    return 0 if not ps else ps[0][1] + b2n(ps[0][0])


def goodN(ps, top):
    if not ps:
        return False
    return all(M >= 2 for (_, M) in ps[1:]) and top >= 2


STAT = {'jumps': 0, 'jumpV': 0}


def tryJump(b):
    cb = canonL(b)
    pz = parseZone(cb)
    if pz is None:
        return None
    n0, (lv, rest) = pz
    ps, top = toN(n0, lv)
    V = chooseV(ps)
    ps2 = after(V, ps)
    if V >= 8 and ovf(V, ps) == 0 and goodN(ps2, top) and n0of(ps) == n0 \
            and physP(ps, top) == lv and encZone(n0, lv, rest) == cb:
        STAT['jumps'] += 1
        STAT['jumpV'] += V
        return encZone(n0of(ps2), physP(ps2, top), rest)
    return None


def xrun(m, b):
    return b if m == 0 else [('R', X, m)] + b


def macL(f, b):
    if len(f) >= 4 and isbit(f[0], 1) and isbit(f[1], 0) and f[2][0] == 'R' and isbit(f[3], 1):
        w, k = f[2][1], f[2][2]
        if w == W:
            return ([Bit(1)] + f[4:], xrun(k - 1, [Bit(1), Bit(0), Bit(1), Bit(1), Bit(0)] + b))
    return None


def macR(f, b):
    if len(f) >= 6 and f[0][0] == 'R':
        w, m = f[0][1], f[0][2]
        if isbit(f[1], 1) and isbit(f[2], 0) and isbit(f[3], 1) and isbit(f[4], 1) and isbit(f[5], 0):
            if w == X:
                return (f[6:], [Bit(1), Bit(1), ('R', W, m + 1)] + b)
        return None
    if len(f) >= 5 and isbit(f[0], 1) and isbit(f[1], 0) and isbit(f[2], 1) and isbit(f[3], 1) \
            and isbit(f[4], 0):
        return (f[5:], [Bit(1), Bit(1), ('R', W, 1)] + b)
    return None


def atVisit(c):
    d, f, b, q = c
    if d and not f and q == 'A':
        bj = tryJump(b)
        if bj is not None:
            return (True, [], bj, 'A')
        return (True, [], canonL(b), 'A')
    return c


def macros(c):
    d, f, b, q = c
    if not d and q == 'D':
        r = macL(f, b)
        return None if r is None else (False, r[0], r[1], 'D')
    if d and q == 'C':
        r = macR(f, b)
        return None if r is None else (True, r[0], r[1], 'C')
    return None


def make_round(tmstr):
    T = {True: parse(tmstr), False: flip(parse(tmstr))}
    caches = {True: {}, False: {}}

    def round_(c):
        c1 = atVisit(c)
        m = macros(c1)
        if m is not None:
            return m
        d, f, b, q = c1
        g = gstep(T[d], f, b, q, caches[d])
        if g[0] == 'Halt':
            return None
        if g[0] == 'Same':
            return (d, g[1], g[2], g[3])
        return (not d, g[1], g[2], g[3])
    return round_


def show(c, lim=12):
    d, f, b, q = c

    def it(x):
        return str(x[1]) if x[0] == 'B' else '(%s)^%d' % (''.join(map(str, x[1])), x[2])
    return 'dir=%s q=%s front=[%s] back=[%s]' % (d, q, ' '.join(it(x) for x in f[:lim]),
                                                    ' '.join(it(x) for x in b[:lim]))


def main():
    start = sys.argv[1]
    rounds = int(sys.argv[2])
    tmstr = TM581
    logk = 0
    a = sys.argv[3:]
    if '--tm' in a:
        tmstr = a[a.index('--tm') + 1]
    if '--log' in a:
        logk = int(a[a.index('--log') + 1])
    rnd = make_round(tmstr)
    c = (True, [], [], start)
    for i in range(1, rounds + 1):
        c2 = rnd(c)
        if c2 is None:
            print('HALT in Runde', i, '| Spruenge', STAT['jumps'], '| Sprung-Besuche', STAT['jumpV'])
            print('letzte Konfiguration:', show(c))
            return
        c = c2
        if logk and i % logk == 0:
            mx = max([x[2] for x in c[1] + c[2] if x[0] == 'R'] + [0])
            print('Runde', i, 'Items', len(c[1]) + len(c[2]), 'Spruenge', STAT['jumps'],
                  'groesste Wiederholung 2^%d' % mx.bit_length(), flush=True)
    print('KEIN HALT nach', rounds, 'Runden | Spruenge', STAT['jumps'], '| Sprung-Besuche', STAT['jumpV'])
    print('Konfiguration:', show(c))


if __name__ == '__main__':
    main()
