#!/usr/bin/env python3
"""Zusatz der Pruefstelle, Punkt 3 und b): stehende Luecken auf allen 27.108 Baendern der Familie F.

Je Band luecke.c (und, mit --zweit, zusaetzlich zweit/luecke.go; dann werden je Band alle EP-Zeilen und die
ERGEBNIS-Zaehler verglichen). Startkonfiguration wie kunst.c: M5, Zustand A, Kopf direkt rechts vom Band.
Ausgabe: Zusammenfassung, Verteilung der Dauern, Ankunftszustaende, linke Umgebungen bei Entstehung, und fuer b)
alle Episoden, die nicht genau 45 Schritte dauern, nach Bausteinen links geordnet.

Aufruf: python3 luecke_familie.py <schritte> [--zweit] [--nur N]
"""
import sys, os, subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, '..', '318_518', 'kunst'))
sys.path.insert(0, os.path.join(HIER, '..', '318_518'))
from familie import familie, band_aus, RESTE  # noqa: E402
from m5schnell import RUNS  # noqa: E402

C = '/tmp/claude-0/luecke'; GO = '/tmp/claude-0/luecke_go'
M5 = '1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC'

def lies(text):
    ep = []; erg = {}
    for l in text.splitlines():
        f = l.split()
        if not f: continue
        if f[0] == 'EP': ep.append(tuple(f[1:]))
        elif f[0] == 'ERGEBNIS':
            erg = dict(t.split('=') for t in f[1:] if t.split('=')[0] != 'vollfehler')
    return sorted(ep), erg

def lauf(arg):
    i, band, N, zweit = arg
    cmd = [M5, str(N), '--band', band + '0', str(len(band))]
    a = lies(subprocess.run([C] + cmd, capture_output=True, text=True).stdout)
    b = lies(subprocess.run([GO] + cmd, capture_output=True, text=True).stdout) if zweit else None
    return i, a, b

def bausteine(ctx):
    """Linke Umgebung (Zellen vor der linken 1 der Luecke, endet auf ...0101) in Bausteine zerlegen, von rechts.
    Die letzte Zelle (1, direkt links der Luecken-1) gehoert zu keinem Baustein und wird als '|1' gezeigt."""
    s = ctx[:-1]                      # endet auf ...010
    r = [len(x) for x in s.split('0')][:-1]   # Einserlaeufe, jeder von einer 0 beendet
    aus = []; i = len(r)
    while i > 0:
        for name, muster in RUNS:
            k = len(muster)
            if i >= k and tuple(r[i-k:i]) == muster:
                aus.append(name); i -= k; break
        else:
            break
    rest = '?' if i > 0 else ''
    return (rest + ' ' + ' '.join(reversed(aus))).strip() + ' |1'

def main():
    N = int(sys.argv[1]); zweit = '--zweit' in sys.argv
    fam = familie(('voll', 'W', 'gross'), list(RESTE))
    baender = [band_aus(RESTE[rn], items, u, e) for (_, rn, items, u, e) in fam]
    if '--nur' in sys.argv: baender = baender[:int(sys.argv[sys.argv.index('--nur') + 1])]
    eps = []; maxg = 0; mehr = 0; abw = 0; zus = Counter()
    with ThreadPoolExecutor(4) as ex:
        for i, (ep, erg), b in ex.map(lauf, [(i, x, N, zweit) for i, x in enumerate(baender)], chunksize=1):
            if zweit and (ep, erg) != b:
                abw += 1; print(f'ABWEICHUNG Band {i}:\n  C ={ep} {erg}\n  Go={b}', flush=True)
            eps += [(i,) + e for e in ep]
            maxg = max(maxg, int(erg['max_gleichzeitig'])); mehr += int(erg['mehrfach'])
            for k in ('T', 'VB', 'VE', 'P1', 'P2', 'P3'): zus[k] += int(erg[k])
            zus['halt'] += int(erg['halt'])
    print(f'{len(baender)} Baender, je {N} Schritte' + (f'; Zweitprogramm: {len(baender) - abw} gleich, {abw} abweichend' if zweit else ''))
    print(f'Muster: ' + ' '.join(f'{k}={v}' for k, v in zus.items()))
    print(f'Episoden: {len(eps)}; hoechstens gleichzeitig offen: {maxg}; Beginn bei schon offener Episode: {mehr}')
    # EP: band, beginn, ende, dauer, k, ankunft, uebergaenge, ctx32
    print('Laenge k:', dict(Counter(e[4] for e in eps)))
    print('Ankunftszustand auf der linken 1:', dict(Counter(e[5] for e in eps)))
    print('Uebergaenge vor der Entstehung:', dict(Counter(e[6] for e in eps)))
    dauer = Counter(int(e[3]) for e in eps if e[2] != '-1')
    offen = sum(1 for e in eps if e[2] == '-1')
    print(f'Dauer: min {min(dauer)}, max {max(dauer)}, genau 45: {dauer[45]}, andere: {sum(dauer.values()) - dauer[45]}, '
          f'bei Laufende noch offen: {offen}')
    print('Dauerverteilung:', dict(sorted(dauer.items())))
    for L in (4, 8, 16, 32):
        c = Counter(e[7][-L:] for e in eps)
        print(f'Linke Umgebung, letzte {L} Zellen: {len(c)} verschieden' + (f': {dict(c)}' if len(c) <= 8 else ''))
    print('\n== b) Episoden, die nicht genau 45 Schritte dauern, nach Bausteinen links (letzte Bausteine vor der Luecke)')
    andere = [e for e in eps if e[2] != '-1' and int(e[3]) != 45]
    g = Counter(); gd = {}
    for e in andere:
        bs = bausteine(e[7])
        g[bs] += 1; gd.setdefault(bs, Counter())[(int(e[3]), e[5])] += 1
    for bs, n in g.most_common():
        print(f'  {n:4d}  {bs:40s}  Dauer/Ankunft: ' + ', '.join(f'{d}{a}x{m}' for (d, a), m in sorted(gd[bs].items())))
    g45 = Counter(bausteine(e[7]) for e in eps if e[2] != '-1' and int(e[3]) == 45)
    print('\n== zum Vergleich: Episoden mit genau 45 Schritten, nach Bausteinen links')
    for bs, n in g45.most_common():
        print(f'  {n:5d}  {bs}')
    print('\n== b) alle Episoden ungleich 45 einzeln: Band, Beginn, Dauer, Ankunft, 32 Zellen links')
    for e in sorted(andere, key=lambda e: (int(e[3]), e[7])):
        print(f'  Band {e[0]:5d}  Beginn {e[1]:>8s}  Dauer {e[3]:>4s}  {e[5]}  {e[7]}  {bausteine(e[7])}')

if __name__ == '__main__':
    main()
