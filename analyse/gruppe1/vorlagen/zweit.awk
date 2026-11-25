# Zweitprogramm zu reich.py und diff.py (eigene Zerlegung der Listenzeilen).
# Aufruf: awk -v modus=reich|diff -f zweit.awk py_zyklen_X.txt x.txt
NR==FNR { s[$1]=1; next }
($1 in s) {
  line=$0; sub(/^[0-9]+ C [0-9]+ lead 0 \| /,"",line)
  gsub(/<[0-9]+>/," ",line); gsub(/\|/," ",line)
  n=split(line,e," ")
  if (modus=="reich") {
    x=e[1]+4*e[2]+7; m=0
    for(i=(n>50?n-49:1);i<=n;i++) if(e[i]+0>m) m=e[i]+0
    printf "%s %d %d %d %d\n",$1,x,n,int(x/2)-n,m
  } else {
    mx=-1e9; mn=1e9; c=0
    for(i=1;i<n;i++){ d=e[i]-e[i+1]; if(d>mx)mx=d; if(d<mn)mn=d; if(d!=0)c++ }
    print $1,mx,mn,c
  }
}
