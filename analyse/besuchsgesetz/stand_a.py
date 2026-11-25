#!/usr/bin/env python3
# Stand der Mitglieder in busycoq (BB6 und alle PR-Koepfe) und cryptids, Programm 1 (Thread "Familie
# Besuchsgesetz", 25.11.2026): erzeugt fuer jedes Mitglied alle Schreibweisen (tm und aliases aus
# holdouts.json, jede Umbenennung der Zustaende B..F, gespiegelt und nicht) und sucht sie woertlich.
# Aufruf: python3 -I stand_a.py <busycoq-bare-repo> <cryptids-Verzeichnis> <holdouts.json> n1,n2,...
import json, subprocess, sys, itertools, os
repo, cry, jp, ns = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4].split(',')]
d = json.load(open(jp))
H = {h['n']: h for h in d['holdouts']}
def var(tm):
    T = [[p[:3], p[3:]] for p in tm.split('_')]
    out = set()
    for perm in itertools.permutations(range(1, 6)):
        P = [0] + list(perm)
        for sp in (0, 1):
            neu = [None] * 6
            for i in range(6):
                z = []
                for t in T[i]:
                    if t[2] not in 'ABCDEF': z.append(t)
                    else: z.append(t[0] + (t[1] if not sp else ('L' if t[1] == 'R' else 'R')) + 'ABCDEF'[P[ord(t[2]) - 65]])
                neu[P[i]] = z
            out.add('_'.join(a + b for a, b in neu))
    return out
def git(*a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True).stdout
refs = ['BB6'] + sorted((l for l in git('for-each-ref', '--format=%(refname)', 'refs/pr').split()), key=lambda r: int(r.rsplit('/', 1)[1]))
wer = {}
for n in ns:
    h = H[n]
    for tm in [h['tm']] + [a['tm'] for a in h['aliases']]:
        for v in var(tm): wer[v] = n
f = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'stand_a_muster.txt')
open(f, 'w').write('\n'.join(sorted(wer)) + '\n')
# BB6: ganzer Baum. PR-Koepfe: nur Dateien, die sich gegenueber BB6 unterscheiden (git diff --name-only);
# unveraenderte Dateien haben dieselben Treffer wie BB6 und werden unten ohnehin abgezogen.
treffer = {}
def suche(ref, pfade=None):
    if pfade is not None and not pfade: return
    for l in git('grep', '-o', '-I', '-F', '-f', f, ref, *(['--'] + pfade if pfade else [])).splitlines():
        r, datei, m = l.split(':', 2)
        treffer.setdefault((wer[m], ref), set()).add(datei)
suche('BB6')
for ref in refs[1:]:
    suche(ref, git('diff', '--name-only', '--diff-filter=AM', 'BB6', ref).split())
cr = subprocess.run(['grep', '-roF', '-f', f, '--exclude-dir=.git', cry], capture_output=True, text=True).stdout
crt = {}
for l in cr.splitlines():
    datei, m = l.rsplit(':', 1)
    crt.setdefault(wer[m], set()).add(os.path.relpath(datei, cry))
for n in ns:
    pin = treffer.get((n, 'BB6'), set())
    t = (['BB6: ' + ','.join(sorted(pin))] if pin else [])
    for ref in refs[1:]:
        fs = treffer.get((n, ref), set()) - pin
        if fs: t.append('PR ' + ref.rsplit('/', 1)[1] + ': ' + ','.join(sorted(fs)))
    print(f"{n}\tbusycoq: {'; '.join(t) or 'nichts'}\tcryptids: {','.join(sorted(crt.get(n, []))) or 'nichts'}")
