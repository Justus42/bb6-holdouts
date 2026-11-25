/* Direkte TM-Simulation ab einer Rundengrenze mit Startwort s (Thread "396, Teil 2", 25.11.2026).
   Modus 396: Rundengrenze 0^inf A> 1 0 s   (wie busycoq PR #59, LE s).
   Modus 587: Rundengrenze 0^inf 1 0 C> 1 0 s   (cryptids 2.3, W(w) mit w = 10 s; die 1 links ist der Waechter).
   Gibt bei jeder Rundengrenze "R <k> <s>" aus (k = 0 ist der Start), bei Halt "HALT <runde>".
   Aufruf: direkt_start <tm> <396|587> <startwort> <max_runden> <max_schritte> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int main(int argc,char**argv){
  const char*s=argv[1]; int mod=atoi(argv[2]); const char*w0=argv[3]; int maxr=atoi(argv[4]); long long maxs=atoll(argv[5]);
  int W[6][2],Mv[6][2],N[6][2],H[6][2];
  for(int q=0;q<6;q++)for(int b=0;b<2;b++){const char*t=s+7*q+3*b; H[q][b]=(t[2]=='-'); if(!H[q][b]){W[q][b]=t[0]-'0';Mv[q][b]=t[1]=='R'?1:-1;N[q][b]=t[2]-'A';}}
  int64_t C=1<<24; uint8_t*tp=calloc(C,1); int64_t p=C/2; int q;
  if(mod==396){ q=0; tp[p]=1; tp[p+1]=0; } else { q=2; tp[p-2]=1; tp[p-1]=0; tp[p]=1; tp[p+1]=0; }
  for(size_t i=0;i<strlen(w0);i++) tp[p+2+i]=(uint8_t)(w0[i]-'0');
  int64_t lmin=C, rmax=-1; for(int64_t i=0;i<C;i++) if(tp[i]){ if(i<lmin) lmin=i; rmax=i; }
  long long st=0; int r=0;
  while(st<maxs){
    uint8_t b=tp[p];
    int grenze = mod==396 ? (q==0 && b==1 && p==lmin && tp[p+1]==0)
                          : (q==2 && p==lmin+2 && tp[lmin+1]==0 && b==1 && tp[p+1]==0);
    if(grenze){ printf("R %d ",r); for(int64_t i=p+2;i<=rmax;i++) putchar('0'+tp[i]); putchar('\n'); r++; if(r>maxr) return 0; }
    if(H[q][b]){ printf("HALT %d\n",r); return 0; }
    tp[p]=W[q][b];
    if(W[q][b]){ if(p<lmin)lmin=p; if(p>rmax)rmax=p; } else { if(p==lmin){ while(lmin<=rmax && !tp[lmin]) lmin++; if(lmin>rmax) lmin=C; } }
    if(p==rmax && !W[q][b]){ while(rmax>=0 && !tp[rmax]) rmax--; }
    p+=Mv[q][b]; q=N[q][b]; st++;
    if(p<2||p>C-3){ printf("RAND\n"); return 1; }
  }
  printf("SCHRITTE\n"); return 0;
}
