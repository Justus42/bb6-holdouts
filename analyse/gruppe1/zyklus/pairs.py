import sys,re
def lese(fn):
    L=[l.rstrip('\n') for l in open(fn)]
    steps=[int(l.split()[0]) for l in L]
    anf=[i for i in range(2,len(steps)) if steps[i]-steps[i-1]>8*(steps[i-1]-steps[i-2]) and steps[i]-steps[i-1]>5000]
    return L,steps,anf
def tok(l):
    b=l.split(' lead ',1)[1]
    lead,rest=b.split(' ',1)
    t=rest.split()
    # t: '|', k, sep, k, sep, ..., k
    return int(lead),t
if __name__=='__main__':
    L,steps,anf=lese(sys.argv[1])
    for c in anf[int(sys.argv[2]):int(sys.argv[3])]:
        l1,t1=tok(L[c-1]); l2,t2=tok(L[c])
        print(steps[c-1],'lead',l1,' '.join(t1))
        print(steps[c],'lead',l2,' '.join(t2))
        print()
