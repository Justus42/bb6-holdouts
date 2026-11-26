import sys, bisect
d=[l.split() for l in open(sys.argv[1])]
p=[l.split() for l in open(sys.argv[2])]
pos={}
for i,(s,L,h) in enumerate(d): pos.setdefault((L,h),[]).append(i)
last=-1; ok=0; bad=0; jumps=0
for r in p:
    lst=pos.get((r[1],r[2]),[]); k=bisect.bisect_left(lst,last)
    if k<len(lst): last=lst[k]; ok+=1; jumps+=(len(r)==4)
    else: bad+=1
print('Portierung:',len(p),'in Reihenfolge gefunden:',ok,'nach Sprung:',jumps,'fehlend:',bad)
sys.exit(1 if bad else 0)
