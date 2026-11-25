#!/usr/bin/env python3
"""Ergaenzung zu pr_abgleich.py: alle Maschinen-Strings der neuen/geaenderten PRs ueber die
Normalform aus karte_a.canon (Umbenennung + Spiegelung) mit den Zielmaschinen vergleichen.
Aufruf: python3 -I kanon_abgleich.py <bare-repo> <holdouts.json>
"""
import json, re, subprocess, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'verwandtschaft'))
import karte_a as K

repo, jpath = sys.argv[1], sys.argv[2]
d = json.load(open(jpath))
snap = {p['number']: p['head_sha'] for p in d['busycoq']['pr_snapshot']}
ZIEL = [88, 312, 396, 449, 114, 367, 378, 318, 518, 322, 274]
ziel = {}
for h in d['holdouts']:
    if h['n'] in ZIEL:
        for tm in [h['tm']] + [a['tm'] for a in h['aliases']]:
            ziel.setdefault(K.canon(K.parse(tm))[0], set()).add(h['n'])
alle = {}
for h in d['holdouts']:
    for tm in [h['tm']] + [a['tm'] for a in h['aliases']]:
        alle.setdefault(K.canon(K.parse(tm))[0], set()).add(h['n'])

def git(*a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, check=True).stdout
TR = r'(?:[01][LR][A-F]|---)'
PAT = re.compile(r'(?<![0-9A-Za-z_-])' + '_'.join([TR + TR] * 6) + r'(?![0-9A-Za-z_-])')
n_str = 0; n_hold = 0; fremd = []
for line in git('for-each-ref', '--format=%(objectname) %(refname)', 'refs/pr').splitlines():
    sha, ref = line.split(); n = int(ref.rsplit('/', 1)[1])
    if snap.get(n) == sha:
        continue
    base = git('merge-base', 'refs/heads/BB6', sha).strip()
    for l2 in git('diff', '--name-status', '--no-renames', base, sha).splitlines():
        st, f = l2.split('\t', 1)
        if st == 'D':
            continue
        for m in set(PAT.findall(git('show', f'{sha}:{f}'))):
            n_str += 1
            c = K.canon(K.parse(m))[0]
            if c in ziel:
                print(f'TREFFER PR {n} {f} {m} -> {sorted(ziel[c])}')
            if c in alle:
                n_hold += 1
            else:
                fremd.append((n, m))
print(f'strings={n_str} davon_holdout_kanonisch={n_hold} ohne_holdout={len(fremd)}')
for n, m in fremd:
    print('  ohne Holdout-Bezug: PR', n, m)
