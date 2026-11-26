import csv, sys, itertools
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r['Klasse'] in ('Monotone list', 'Shift-overflow structural counter')]
print(len(rows), [(r['Klasse'][:4], r['n']) for r in rows])
S = 'ABCDEF'
def parse(s):
    t = {}
    for i, part in enumerate(s.split('_')):
        for b in range(2):
            x = part[3*b:3*b+3]
            t[(S[i], b)] = None if x == '---' else (int(x[0]), x[1], x[2])
    return t
def transform(t, perm, mirror):  # perm: alte->neue Zustandsnamen
    u = {}
    for (q, b), v in t.items():
        if v is None: u[(perm[q], b)] = None
        else:
            w, d, n = v
            if mirror: d = 'L' if d == 'R' else 'R'
            u[(perm[q], b)] = (w, d, perm[n])
    return u
M = {r['n']: parse(r['Maschinen-String']) for r in rows}
found = []
for a, b in itertools.combinations(M, 2):
    for perm_t in itertools.permutations(S):
        perm = dict(zip(S, perm_t))
        for mirror in (False, True):
            if transform(M[a], perm, mirror) == M[b]:
                found.append((a, b, 'Spiegel' if mirror else 'gleich', 'Start von %s entspricht Zustand %s in %s' % (a, perm['A'], b)))
for f in found: print(f)
# 318 / 518
def sim(t, steps):
    tape = {}; pos = 0; q = 'A'; used = set()
    for i in range(steps):
        b = tape.get(pos, 0); used.add((q, b)); v = t[(q, b)]
        if v is None: return ('HALT', i + 1, used)
        w, d, n = v; tape[pos] = w; pos += 1 if d == 'R' else -1; q = n
    return ('läuft', steps, used)
allrows = {r['n']: r['Maschinen-String'] for r in csv.DictReader(open(sys.argv[1]))}
for n in ('318', '518'):
    print(n, allrows.get(n))
if '318' in allrows and '518' in allrows:
    A, B = parse(allrows['318']), parse(allrows['518'])
    diff = [k for k in A if A[k] != B[k]]
    print('Unterschiedliche Felder:', [(k, A[k], B[k]) for k in diff])
    for n, t in (('318', A), ('518', B)):
        st, k, used = sim(t, 3_000_000)
        print(n, st, k, 'benutzte Felder mit Unterschied:', [d for d in diff if d in used])
