#!/usr/bin/env python3
"""Programm 1: neue/geaenderte busycoq-PRs gegen die 608 Holdouts abgleichen.

Aufruf: python3 -I pr_abgleich.py <bare-repo> <holdouts.json>
Das bare Repo muss refs/heads/BB6 und refs/pr/<n> (= refs/pull/<n>/head) enthalten.
Gesucht wird in allen Dateien, die ein PR gegenueber dem Merge-Base mit BB6 hinzufuegt oder
aendert, nach Maschinen-Strings (6 Zustaende, Format wie busycoq). Treffer werden ueber
tm und aliases (equivalent) einem Holdout n zugeordnet.
"""
import json, re, subprocess, sys

repo, jpath = sys.argv[1], sys.argv[2]
d = json.load(open(jpath))
snap = {p['number']: p['head_sha'] for p in d['busycoq']['pr_snapshot']}
idx = {}
for h in d['holdouts']:
    idx[h['tm']] = (h['n'], 'tm')
    for a in h['aliases']:
        idx.setdefault(a['tm'], (h['n'], a['relation']))

def git(*a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, check=True).stdout

TR = r'(?:[01][LR][A-F]|---)'
PAT = re.compile(r'(?<![0-9A-Za-z_-])' + '_'.join([TR + TR] * 6) + r'(?![0-9A-Za-z_-])')

refs = {}
for line in git('for-each-ref', '--format=%(objectname) %(refname)', 'refs/pr').splitlines():
    sha, ref = line.split()
    refs[int(ref.rsplit('/', 1)[1])] = sha

for n in sorted(refs):
    sha = refs[n]
    if snap.get(n) == sha:
        continue  # unveraendert seit Schnappschuss
    art = 'neu' if n not in snap else 'geaendert'
    base = git('merge-base', 'refs/heads/BB6', sha).strip()
    files = []
    for line in git('diff', '--name-status', '--no-renames', base, sha).splitlines():
        st, f = line.split('\t', 1)
        if st != 'D':
            files.append(f)
    treffer = {}
    alle = set()
    for f in files:
        txt = git('show', f'{sha}:{f}')
        for m in PAT.findall(txt):
            alle.add(m)
            if m in idx:
                treffer.setdefault(idx[m][0], set()).add(f)
    msg = git('log', '-1', '--format=%ad|%an|%s', '--date=short', sha).strip()
    hn = ' '.join(str(k) for k in sorted(treffer)) or '-'
    print(f'PR {n}\t{art}\t{sha[:8]}\t{msg}\tdateien={len(files)}\tstrings={len(alle)}\tholdouts={hn}')
