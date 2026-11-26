#!/usr/bin/env python3
# Programm 2 zum Stand (Thread "Familie Besuchsgesetz", 25.11.2026), getrennt von stand_a.py geschrieben:
# liest ALLE Maschinen-Strings (Regex) aus jedem Baum (busycoq BB6, jeder PR-Kopf, cryptids), bringt jeden
# in eine Normalform (Start A fest; Zustaende in Reihenfolge des ersten Auftretens bei Breitensuche ab A,
# beide Spiegelungen, kleinere Zeichenkette) und vergleicht mit den Normalformen der Mitglieder (tm + aliases).
# Aufruf: python3 -I stand_b.py <busycoq-bare-repo> <cryptids-Verzeichnis> <holdouts.json> n1,n2,...
import json, re, subprocess, sys, os
repo, cry, jp, ns = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4].split(',')]
TR = r'(?:[01][LR][A-F]|---)'
PAT = re.compile(r'(?<![0-9A-Za-z_-])' + '_'.join([TR + TR] * 6) + r'(?![0-9A-Za-z_-])')
def nf(tm):
    T = [[p[:3], p[3:]] for p in tm.split('_')]
    best = None
    for sp in (False, True):
        # Breitensuche ab A, Uebergaenge in Reihenfolge (0, 1)
        name = {0: 0}; folge = [0]; i = 0
        while i < len(folge):
            q = folge[i]; i += 1
            for t in T[q]:
                if t[2] in 'ABCDEF':
                    z = ord(t[2]) - 65
                    if z not in name: name[z] = len(name); folge.append(z)
        for z in range(6):
            if z not in name: name[z] = len(name); folge.append(z)
        zeilen = []
        for q in folge:
            zz = ''
            for t in T[q]:
                if t[2] not in 'ABCDEF': zz += '---'
                else: zz += t[0] + (('L' if t[1] == 'R' else 'R') if sp else t[1]) + 'ABCDEF'[name[ord(t[2]) - 65]]
            zeilen.append(zz)
        s = '_'.join(zeilen)
        if best is None or s < best: best = s
    return best
d = json.load(open(jp)); H = {h['n']: h for h in d['holdouts']}
ziel = {}
for n in ns:
    for tm in [H[n]['tm']] + [a['tm'] for a in H[n]['aliases']]: ziel[nf(tm)] = n
def strings_git(ref):
    out = subprocess.run(['git', '-C', repo, 'grep', '-o', '-E', '-I', '[01LRA-F_-]{41}', ref], capture_output=True, text=True).stdout
    res = {}
    for l in out.splitlines():
        _, f, s = l.split(':', 2)
        for m in PAT.findall(s): res.setdefault(m, set()).add(f)
    return res
def treffer(res):
    t = {}
    for s, fs in res.items():
        n = ziel.get(nf(s))
        if n is not None: t.setdefault(n, set()).update(fs)
    return t
pin = treffer(strings_git('BB6'))
prs = {}
for l in subprocess.run(['git', '-C', repo, 'for-each-ref', '--format=%(refname)', 'refs/pr'], capture_output=True, text=True).stdout.split():
    k = int(l.rsplit('/', 1)[1]); t = treffer(strings_git(l))
    for n, fs in t.items():
        fs = fs - pin.get(n, set())
        if fs: prs.setdefault(n, []).append((k, fs))
cr = {}
for dp, dn, fn in os.walk(cry):
    if '.git' in dp.split(os.sep): continue
    for f in fn:
        p = os.path.join(dp, f)
        try: txt = open(p, errors='ignore').read()
        except Exception: continue
        for m in PAT.findall(txt):
            n = ziel.get(nf(m))
            if n is not None: cr.setdefault(n, set()).add(os.path.relpath(p, cry))
for n in ns:
    b = (['BB6: ' + ','.join(sorted(pin[n]))] if n in pin else []) + [f'PR {k}: ' + ','.join(sorted(fs)) for k, fs in sorted(prs.get(n, []))]
    print(f"{n}\tbusycoq: {'; '.join(b) or 'nichts'}\tcryptids: {','.join(sorted(cr.get(n, []))) or 'nichts'}")
