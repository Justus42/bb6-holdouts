import sys
from pairs import lese
def bits(line):
    p=line.split()
    width=int(p[2]); lead=int(p[4]); t=p[5:]
    assert t[0]=='|'; t=t[1:]
    hi=width-1
    z=[hi-lead]
    for i in range(0,len(t),2):
        k=int(t[i])
        for _ in range(k): z.append(z[-1]-3)
        if i+1<len(t):
            g=4 if t[i+1]=='|' else int(t[i+1][1:-1])
            z.append(z[-1]-g)
    b=['1']*width
    for x in z:
        assert x>=0,(x,line[:60])
        b[x]='0'
    return ''.join(b)
def blocks(b):
    """greedy from left: list of (sep_before, n); returns (items, trailing sep)"""
    items=[];sep='';i=0
    while i<len(b):
        if b[i:i+3]=='011':
            n=0
            while b[i:i+3]=='011': n+=1;i+=3
            items.append((sep,n));sep=''
        else:
            sep+=b[i];i+=1
    return items,sep
def fmt(items,tail):
    out=[]
    for s,n in items:
        out.append(('' if s=='1' else f'<{s}>')+str(n))
    return ' '.join(out)+(f' <{tail}>' if tail else '')
if __name__=='__main__':
    L,steps,anf=lese(sys.argv[1])
    for c in anf[int(sys.argv[2]):int(sys.argv[3])]:
        for j in (c-1,c):
            it,tl=blocks(bits(L[j]))
            print(steps[j], fmt(it,tl))
        print()
