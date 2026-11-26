#!/usr/bin/env python3
"""Punkt 3, Negativkontrolle mit gestoertem Band: zufaellige Einzelstoerungen, beide Programme muessen dasselbe melden.

Je Versuch: Maschine (318 oder 322, Leerband), nach S Schritten wird die Zelle Kopf+O auf V gesetzt, danach
laufen beide Programme bis S + 100.000 Schritte. Verglichen werden Schritte, Halt, Zahl der Brueche, erster Bruch,
Breite und HASH. Eingeteilt wird nach erstem Bruch: sofort (= Schritt S, die Stoerung selbst ist schon "11"),
spaeter (die Maschine erzeugt "11" selbst, Pruefung der Fortschreibung) oder nie.

Aufruf: python3 stoer_zufall.py <anzahl> [keim]
"""
import sys, random, subprocess
from concurrent.futures import ThreadPoolExecutor

K = '/tmp/claude-0/kein11'; G = '/tmp/claude-0/naiv'
TM = {'318': '1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC', '322': '1RB1RF_1LC0LF_1RD0LB_0RA1RE_1RD---_0RC0LA'}

def kern(text):
    z = {}
    for l in text.splitlines():
        if l.startswith('ERGEBNIS') or l.startswith('HASH'):
            for t in l.split()[1:]:
                if '=' in t:
                    k, v = t.split('=', 1)
                    if k in ('schritte', 'halt', 'brueche', 'erster_bruch', 'breite', 'zustand', 'kopf_rel'): z[k] = v
                else:
                    z['hash'] = t
    return z

def versuch(arg):
    name, S, O, V = arg
    N = S + 100000
    cmd = [TM[name], 'R', str(N), '--stoer', str(S), str(O), str(V)]
    a = kern(subprocess.run([K] + cmd, capture_output=True, text=True).stdout)
    b = kern(subprocess.run([G] + cmd, capture_output=True, text=True).stdout)
    return arg, a, b

def main():
    n = int(sys.argv[1]); keim = int(sys.argv[2]) if len(sys.argv) > 2 else 20261126
    r = random.Random(keim)
    args = [(r.choice(['318', '322']), r.randint(10000, 200000), r.randint(-150, 150), r.randint(0, 1)) for _ in range(n)]
    gleich = 0; art = {'sofort': 0, 'spaeter': 0, 'nie': 0}; halt = 0
    with ThreadPoolExecutor(4) as ex:
        for (name, S, O, V), a, b in ex.map(versuch, args):
            ok = (a == b)
            gleich += ok
            e = int(a['erster_bruch'])
            k = 'nie' if e < 0 else ('sofort' if e == S else 'spaeter')
            art[k] += 1; halt += int(a['halt'])
            print(f"{'GLEICH' if ok else 'ABWEICHUNG'} {name} S={S} O={O} V={V} erster_bruch={e} ({k}) "
                  f"brueche={a['brueche']} halt={a['halt']} schritte={a['schritte']} hash={a['hash']}"
                  + ('' if ok else f'\n   C={a}\n   Go={b}'), flush=True)
    print(f'ZUSAMMEN {n} Versuche (Keim {keim}): {gleich} gleich; erster Bruch sofort {art["sofort"]}, '
          f'spaeter {art["spaeter"]}, nie {art["nie"]}; Halt in {halt} Versuchen')

if __name__ == '__main__':
    main()
