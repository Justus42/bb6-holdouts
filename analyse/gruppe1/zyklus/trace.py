import sys
TM="1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
T={}
for qi,p in enumerate(TM.split('_')):
    for r in range(2):
        x=p[3*r:3*r+3]
        if x!='---': T[(qi,r)]=(int(x[0]),1 if x[1]=='R' else -1,ord(x[2])-65)
def comp(s):
    out=[];i=0
    while i<len(s):
        best=None
        for w in ('011','100'):
            k=0
            while s[i+3*k:i+3*k+3]==w: k+=1
            if k>=2 and (best is None or k>best[1]): best=(w,k)
        if best:
            out.append(f"{best[0]}^{best[1]}");i+=3*best[1]
        else:
            j=i
            out.append(s[i]);i+=1
    return ' '.join(out)
def run(start,n0,n1,mode='turn'):
    t={};p=0;q=start;n=0;lo=hi=0;last=1
    while n<n1:
        s=t.get(p,0)
        if (q,s) not in T: print('HALT',n);return
        w,d,nq=T[(q,s)]
        if n>=n0 and d!=last:
            band=''.join(str(t.get(i,0)) for i in range(lo,hi+1))
            k=p-lo
            print(n,'ABCDEF'[q],'R>L' if d<0 else 'L>R',p-lo, comp(band[:k])+' ['+band[k]+'] '+comp(band[k+1:]))
        last=d
        t[p]=w;p+=d;q=nq;n+=1
        lo=min(lo,p);hi=max(hi,p)
if __name__=='__main__':
    run(ord(sys.argv[1])-65,int(sys.argv[2]),int(sys.argv[3]))
