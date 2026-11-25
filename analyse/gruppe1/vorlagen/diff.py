import sys,re
starts=set(l.split()[0] for l in open(sys.argv[2]))
for line in open(sys.argv[1]):
    f=line.split(' ',4)
    if f[0] not in starts: continue
    body=f[4].split('|',1)[1]
    el=[int(t) for t in re.findall(r'(?<![<\d])\d+(?!>)', body)]
    d=[el[i]-el[i+1] for i in range(len(el)-1)]
    print(f[0],max(d),min(d),sum(1 for v in d if v!=0))
