# Haltemuster fuer Tabelle 114 (Gruppe 1): Vorgaenger des Halts und Gegenbeispiel zur lokalen Fassung des Muster-Satzes.
S='ABCDEF'; s='1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC'; t={}
for i,p in enumerate(s.split('_')):
    for b in range(2):
        x=p[3*b:3*b+3]; t[(S[i],b)]=None if x=='---' else (int(x[0]),x[1],x[2])
for q in 'AEC': print('nach',q,'fuehren:',[(k,v) for k,v in t.items() if v and v[2]==q])
def run(q,tape,pos,maxs=200):
    tape=dict(enumerate(tape)); gesehen=[]
    for i in range(maxs):
        b=tape.get(pos,0)
        if q=='C' and b==0 and tape.get(pos+1,0)==1 and tape.get(pos+2,0)==1: gesehen.append(i)
        v=t[(q,b)]
        if v is None: return 'HALT nach %d Schritten; C>011 gesehen bei %s'%(i,gesehen)
        tape[pos]=v[0]; pos+=1 if v[1]=='R' else -1; q=v[2]
    return 'kein Halt in %d Schritten'%maxs
print('C vor 1 1 0 0 1 1 1 (rechts schon 111):', run('C',[1,1,0,0,1,1,1],0))
print('C vor 0 1 1, links 0             :', run('C',[0,0,1,1],1))
