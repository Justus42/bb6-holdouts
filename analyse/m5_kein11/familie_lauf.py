#!/usr/bin/env python3
"""Punkt 3 auf den kuenstlichen Baendern: alle 27.108 Baender der Familie F (analyse/318_518/kunst/BANDFAMILIE.md,
erzeugt mit familie.py, fester Keim) mit kein11 auf M5 pruefen: bei jedem Schritt "nie 11 strikt rechts vom Kopf",
dazu wie oft M5-D eine 0 liest und rechts daneben eine 1 steht.

Startkonfiguration wie in kunst.c: Zustand A, Kopf direkt rechts vom Band auf einer leeren Zelle.
Zweitpruefung: eine Stichprobe (fester Keim) zusaetzlich mit naiv.go, Vergleich aller Kernwerte und des HASH.

Aufruf: python3 familie_lauf.py <schritte> <stichprobe> <stichprobe_schritte>
"""
import sys, os, random, subprocess
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '318_518', 'kunst'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '318_518'))
from familie import familie, band_aus, RESTE  # noqa: E402

K = '/tmp/claude-0/kein11'; G = '/tmp/claude-0/naiv'
M5 = '1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC'

def kern(text, mit_nachbar=True):
    z = {}
    for l in text.splitlines():
        f = l.split()
        if not f: continue
        if f[0] in ('ERGEBNIS', 'HASH'):
            for t in f[1:]:
                if '=' in t:
                    k, v = t.split('=', 1)
                    if k in ('schritte', 'halt', 'brueche', 'erster_bruch', 'breite', 'zustand', 'kopf_rel'): z[k] = v
                else: z['hash'] = t
        elif f[0] == 'NACHBAR' and f[1] == 'D0' and mit_nachbar:
            z['D0_nachbar1'] = int(f[3].split('=')[1]); z['D0'] = int(f[2].split('=')[1])
    return z

def lauf(arg):
    i, band, N = arg
    cmd = [M5, 'R', str(N), '--band', band + '0', str(len(band))]
    return i, kern(subprocess.run([K] + cmd, capture_output=True, text=True).stdout)

def zweit(arg):
    i, band, N = arg
    cmd = [M5, 'R', str(N), '--band', band + '0', str(len(band))]
    a = kern(subprocess.run([K] + cmd, capture_output=True, text=True).stdout, False)
    b = kern(subprocess.run([G] + cmd, capture_output=True, text=True).stdout, False)
    return i, a, b

def main():
    N, n2, N2 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    fam = familie(('voll', 'W', 'gross'), list(RESTE))
    baender = [band_aus(RESTE[rn], items, u, e) for (_, rn, items, u, e) in fam]
    print(f'{len(baender)} Baender, je {N} Schritte', flush=True)
    brueche = 0; d0 = 0; d0n = 0; schritte = 0
    with ThreadPoolExecutor(4) as ex:
        for i, z in ex.map(lauf, [(i, b, N) for i, b in enumerate(baender)], chunksize=1):
            schritte += int(z['schritte']); d0 += z['D0']; d0n += z['D0_nachbar1']
            if int(z['brueche']) > 0 or z['D0_nachbar1'] > 0 or z['halt'] != '0':
                brueche += 1
                print(f'BRUCH Band {i}: {z}', flush=True)
    print(f'ZUSAMMEN {len(baender)} Baender, {schritte} Schritte: Baender mit Bruch {brueche}; '
          f'M5-D liest 0: {d0} Mal, davon rechts daneben 1: {d0n}', flush=True)
    r = random.Random(20261126)
    probe = r.sample(range(len(baender)), n2)
    gleich = 0
    with ThreadPoolExecutor(4) as ex:
        for i, a, b in ex.map(zweit, [(i, baender[i], N2) for i in probe]):
            gleich += (a == b)
            if a != b: print(f'ABWEICHUNG Band {i}: C={a} Go={b}', flush=True)
    print(f'ZWEITPRUEFUNG {n2} Baender (Keim 20261126), je {N2} Schritte: {gleich} gleich (C gegen Go)', flush=True)

if __name__ == '__main__':
    main()
