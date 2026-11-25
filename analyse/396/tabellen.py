# Zaehlt verschiedene Tabellen unter den 608 Holdouts bis auf Umbenennung der Zustaende und Spiegelung (Start egal).
# Verfahren: kanonische Form = kleinste Zeichenkette ueber alle 720 Umbenennungen x 2 Spiegelungen.
import itertools, sys
def canon(s, mirror_allowed=True):
    parts=s.split('_'); n=len(parts)
    tr=[[parts[q][3*b:3*b+3] for b in (0,1)] for q in range(n)]
    best=None
    for mir in ((False,True) if mirror_allowed else (False,)):
        for perm in itertools.permutations(range(n)):   # perm[alt] = neu
            new=[None]*n
            for q in range(n):
                row=[]
                for b in (0,1):
                    t=tr[q][b]
                    if t[2] in '-HZ': row.append('---'); continue
                    d=t[1]
                    if mir: d={'L':'R','R':'L'}[d]
                    row.append(t[0]+d+'ABCDEF'[perm['ABCDEF'.index(t[2])]])
                new[perm[q]]=''.join(row)
            c='_'.join(new)
            if best is None or c<best: best=c
    return best
ms=[l.strip() for l in open(sys.argv[1]) if l.strip()]
mode=sys.argv[2] if len(sys.argv)>2 else 'normal'
if mode=='mutiere':   # Negativkontrolle: Maschine 367 (Tabelle wie 114) in einem Uebergang veraendern
    s=list(ms[366]); i=s.index('_')+1; s[i]='1' if s[i]=='0' else '0'; ms[366]=''.join(s)
if mode=='spiegel':   # Positivkontrolle: Maschine 1 gespiegelt anhaengen, darf keine neue Tabelle ergeben
    m=ms[0]; ms.append(''.join({'L':'R','R':'L'}.get(ch,ch) for ch in m))
if mode=='umbenennen':  # Positivkontrolle: Maschine 1 mit vertauschten Namen B<->C anhaengen
    m=ms[0]; p=m.split('_'); sw={'B':'C','C':'B'}
    p=[''.join(sw.get(ch,ch) for ch in x) for x in p]; p[1],p[2]=p[2],p[1]; ms.append('_'.join(p))
classes={}
for i,m in enumerate(ms,1): classes.setdefault(canon(m),[]).append(i)
sizes={}
for v in classes.values(): sizes[len(v)]=sizes.get(len(v),0)+1
print(mode, 'Maschinen',len(ms),'verschiedene Tabellen',len(classes),'Groessen',dict(sorted(sizes.items())))
if mode=='normal':
    nomir={}
    for i,m in enumerate(ms,1): nomir.setdefault(canon(m,False),[]).append(i)
    print('ohne Spiegelung:',len(nomir))
    with open('tabellen_klassen.txt','w') as f:
        for k,v in sorted(classes.items(), key=lambda kv: kv[1][0]):
            if len(v)>1: f.write(','.join(map(str,v))+'\n')
