import sys,re
starts=set(l.split()[0] for l in open(sys.argv[2]))
for line in open(sys.argv[1]):
    f=line.split(' ',4)
    if f[0] not in starts: continue
    nums=[int(t) for t in re.findall(r'(?<![<\d])\d+(?![>\d])', f[4])]
    # f[4] beginnt mit "0 |" (lead), erstes Element danach ist a
    body=f[4].split('|',1)[1]
    el=[int(t) for t in re.findall(r'(?<![<\d])\d+(?!>)', body)]
    a,b=el[0],el[1]; x=a+4*b+7; L=len(el)
    print(f[0],x,L,x//2-L,max(el[-50:]))
