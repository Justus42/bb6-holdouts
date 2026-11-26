import json, sys, collections as C
d = json.load(open(sys.argv[1]))
h = d['holdouts']; dec = d['decided']
cls_hold = C.defaultdict(C.Counter)
for x in h:
    c = x['class'] or 'None'
    cls_hold[c]['holdouts'] += 1
    cls_hold[c]['bc_' + x['busycoq']['status']] += 1
    cls_hold[c]['sb_' + str((x['slugbird'] or {}).get('status'))] += 1
cls_dec = C.Counter((x['class'] or 'None') for x in dec if x.get('by') == 'proof')
cls_dec_all = C.Counter((x['class'] or 'None') for x in dec)
print(C.Counter(x.get('by') for x in dec))
rows = []
for c, k in cls_hold.items():
    rows.append((c, k['holdouts'], k['bc_open'], k['bc_pr_open'], k['bc_solved'], cls_dec[c], k['sb_rules'], k['sb_pattern'], k['sb_lottery'], k['sb_cryptid']))
rows.sort(key=lambda r: -r[1])
print(f"{'class':38s} hold open pr solv decProof rules pattern lottery cryptid")
for r in rows:
    print(f"{r[0][:38]:38s} {r[1]:4d} {r[2]:4d} {r[3]:3d} {r[4]:3d} {r[5]:6d} {r[6]:5d} {r[7]:6d} {r[8]:6d} {r[9]:5d}")
