import sys
from trace import T
from blk import blocks, fmt
def snaps(start,N):
    W=200000; t=bytearray(2*W); p=W; q=start; lo=hi=W; n=0
    while n<N:
        s=t[p]
        if q==2 and s==0 and t[p+1]==0:
            # check reserve form 0 (100)^r 1 up to hi
            j=p+2; r=0
            while j+2<=hi and t[j]==1 and t[j+1]==0 and t[j+2]==0: r+=1; j+=3
            if j==hi and t[j]==1:
                yield n, r, bytes(t[lo:p]).decode('latin1').translate({0:'0',1:'1'}) if False else ''.join('01'[c] for c in t[lo:p])
        if (q,s) not in T: return
        w,d,nq=T[(q,s)]
        t[p]=w; p+=d; q=nq; n+=1
        if p<lo: lo=p
        if p>hi: hi=p
if __name__=='__main__':
    for n,r,b in snaps(ord(sys.argv[1])-65,int(float(sys.argv[2]))):
        it,tl=blocks(b)
        print(n,r,fmt(it,tl))
