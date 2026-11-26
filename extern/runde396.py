import sys, os
sys.setrecursionlimit(100000)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'gesetz396.py')).read().split("L=int(sys.argv[1])")[0])
def tm_rounds(t, maxsteps):
    tape={}; pos=0; q='A'; out=[]; lo=0; hi=0
    for n in range(maxsteps):
        if q=='A' and tape.get(pos,0)==1 and tape.get(pos+1,0)==0 and all(tape.get(i,0)==0 for i in range(lo,pos)):
            s=norm([tape.get(i,0) for i in range(pos+2,hi+1)])
            if not out or out[-1][1]!=s or True: out.append((n,s))
        v=t[(q,tape.get(pos,0))]
        if v is None: out.append((n,'HALT')); break
        tape[pos]=v[0]; pos+=1 if v[1]=='R' else -1; q=v[2]; lo=min(lo,pos); hi=max(hi,pos)
    return out
N=int(sys.argv[1])
obs=tm_rounds(T396,N)
s=[1]; pred=[s]
for k in range(len(obs)+2):
    try: s=norm(V([1,0]+s,'396')); pred.append(s)
    except Halt: pred.append('HALT'); break
ok=sum(1 for i,(n,o) in enumerate(obs) if i<len(pred) and o==pred[i])
print(f'396: {len(obs)} Rundenanfaenge in {N} TM-Schritten beobachtet; mit Wortsystem gleich: {ok}; erster bei Schritt {obs[0][0]}, letzter bei Schritt {obs[-1][0]}')
if ok!=len(obs):
    for i,(n,o) in enumerate(obs[:6]): print(i,n,''.join(map(str,o)),'|',''.join(map(str,pred[i])) if i<len(pred) else '-')
obs88=tm_rounds(T88,N)
same=sum(1 for a,b in zip(obs,obs88) if a[1]==b[1])
print(f'88: {len(obs88)} Rundenanfaenge; Wortgleich mit 396 in {same} davon')
