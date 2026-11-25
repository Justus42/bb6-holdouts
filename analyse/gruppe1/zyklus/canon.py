def canon(b):
    """band bits -> list of (bit, n): b = bit0 W^n0 bit1 W^n1 ... ; first element may have bit '' if band starts with W"""
    out=[];i=0;cur=None
    # leading: if starts with 011, sep ''
    toks=[]; sep=''
    while i<len(b):
        if b[i:i+3]=='011':
            n=0
            while b[i:i+3]=='011': n+=1;i+=3
            toks.append((sep,n)); sep=''
        else: sep+=b[i]; i+=1
    res=[]
    for s,n in toks:
        if s=='': res.append(('',n)); continue
        for c in s[:-1]: res.append((c,0))
        res.append((s[-1],n))
    tail=sep
    return res, tail
def render(t,tail=''):
    return ''.join(s+'011'*n for s,n in t)+tail
def show(t):
    return ' '.join(('' if s=='1' else ('.' if s=='0' else s))+str(n) for s,n in t)
