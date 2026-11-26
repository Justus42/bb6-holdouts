import sys, bisect
d=[l.split() for l in open(sys.argv[1])]
p=[l.split() for l in open(sys.argv[2])]
pos={}
for i,(s,L,h) in enumerate(d): pos.setdefault((L,h),[]).append(i)
schritte_ok=0; schritte_bad=0
last=-1; ok=0; bad=0; jumps=0
for r in p:
    lst=pos.get((r[1],r[2]),[]); k=bisect.bisect_left(lst,last)
    if k<len(lst):
        last=lst[k]; ok+=1; jumps+=(r[-1]=='J')
        if len(r)>=4 and r[3]!='J':
            if r[3]==d[last][0]: schritte_ok+=1
            else: schritte_bad+=1
    else: bad+=1
print('Portierung:',len(p),'in Reihenfolge gefunden:',ok,'nach Sprung:',jumps,'fehlend:',bad,
      '| Schrittzahl gleich:',schritte_ok,'verschieden:',schritte_bad)
sys.exit(1 if bad or schritte_bad else 0)
