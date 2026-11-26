# Lokale Aufzaehlung (Programm 1): Was folgt auf einen Y-Tod (Strom stirbt auf einer 0 direkt vor einer 1)?
# Eingabe der Runde r+1: Token-Folge t1..tm (0=000, 1=100, L=1010) einer frueheren Runde, danach Rest R (Zellen).
# Runde r+1 tritt mit Versatz v in {1,2} in t1 ein (PR #59: Bloecke beginnen bei Versatz 1 oder 2), mit n Besuchen.
# Gesucht: Faelle, in denen der Strom in diesem Fenster mit einem Y-Tod stirbt. Danach Runde r+2 auf dem neuen
# Fenster: Eintritt mit Versatz 1 oder 2 in das erste neu geschriebene Token, n' Besuche. Kommt dabei ein Z vor
# (Ankunft auf 0, danach 11)?  Gezaehlt wird alles; Z-Faelle werden mit Beispiel ausgegeben.
import itertools, sys
TOK = {'0': [0,0,0], '1': [1,0,0], 'L': [1,0,1,0]}
def lauf(w, p, n):
    """n Besuche ab Zelle p (zaehlend wie runde_b); gibt (Ereignisse, Todesstelle, Art, Ausgabebloecke) zurueck"""
    ev = []; bloecke = []
    while n:
        while len(w) < p + 5: w.append(0)
        a, b, c, d = w[p:p+4]
        if a == 0:
            if b and c: ev.append(('Z', p, n))
            w[p] = 1; n -= 1
            if n == 0: return ev, p, ('Y' if b else '0'), bloecke
            continue
        if b and c: ev.append(('HALT', p, n)); return ev, p, 'H', bloecke
        if c == 0:
            u = n & 1; w[p], w[p+1], w[p+2] = (0 if u else 1), 0, 0; bloecke.append((p, 3)); n = (n + 1) // 2; p += 3; continue
        if d == 0: bloecke.append((p, 4)); n *= 2; p += 4; continue
        ev.append(('K', p, n)); w[p], w[p+1], w[p+2] = 0, 0, 0; n -= 1
        if n == 0: return ev, p, 'K', bloecke
    return ev, None, None, bloecke
M = int(sys.argv[1]) if len(sys.argv) > 1 else 5; NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 40
RESTE = [[0]*8, [1,0,0,0,0,0,0,0], [1,0,1,0,0,0,0,0], [1,1,0,0,0,0,0,0], [0,1,0,0,0,0,0,0]]
yfaelle = zfaelle = 0; beispiele = []; art_ende = {}
for m in range(1, M + 1):
    for toks in itertools.product('01L', repeat=m):
        basis = [x for t in toks for x in TOK[t]]
        for rest in RESTE:
            for v in (1, 2):
                if toks[0] == 'L' and v == 1: continue          # KX kommt nicht vor (PR #59)
                for n in range(1, NMAX + 1):
                    w = basis + rest
                    ev, tod, art, bl = lauf(w, v, n)
                    if art != 'Y': continue
                    if any(e[0] in ('Z','HALT','K') for e in ev): continue
                    yfaelle += 1
                    # Runde r+2: Eintritt in den ersten neu geschriebenen Block mit Versatz 1 oder 2
                    if not bl: continue
                    p0 = bl[0][0]
                    for v2 in (1, 2):
                        if bl[0][1] == 4 and v2 == 1: continue
                        for n2 in range(1, NMAX + 1):
                            w2 = list(w); ev2, tod2, art2, _ = lauf(w2, p0 + v2, n2)
                            erreicht = tod2 is not None and tod2 >= tod - 1
                            kz = [e[0] for e in ev2 if e[0] in ('Z','K','HALT')]
                            schl = (kz[0] if kz else 'nichts') + ('' if erreicht else '(nicht erreicht)')
                            art_ende[schl] = art_ende.get(schl, 0) + 1
                            if 'Z' in kz:
                                zfaelle += 1
                                if len(beispiele) < 12: beispiele.append((toks, rest[:4], v, n, v2, n2, ''.join(map(str, w[:tod+3]))))
print(f"m<={M} n<={NMAX}: Y-Tode {yfaelle}, Folgerunde mit Z {zfaelle}")
for k, x in sorted(art_ende.items(), key=lambda q: -q[1]): print(' ', k, x)
for b in beispiele: print('  Beispiel Z:', b)
