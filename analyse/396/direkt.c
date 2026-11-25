/* Direkte TM-Simulation ab Leerband. Gibt bei jeder Konfiguration LE s (Zustand A auf einer 1, links alles 0,
   rechts daneben 0) das Wort s aus (nach "1 0"). Zaehlt E1-Lesungen. Aufruf: direkt <tm-string> <max_schritte> <max_runden> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
int main(int argc,char**argv){
  const char*s=argv[1]; long long maxs=atoll(argv[2]); int maxr=atoi(argv[3]);
  int W[6][2],Mv[6][2],N[6][2],H[6][2];
  for(int q=0;q<6;q++)for(int b=0;b<2;b++){const char*t=s+7*q+3*b; H[q][b]=(t[2]=='-'); if(!H[q][b]){W[q][b]=t[0]-'0';Mv[q][b]=t[1]=='R'?1:-1;N[q][b]=t[2]-'A';}}
  int64_t C=1<<26; uint8_t*tp=calloc(C,1); int64_t p=C/2, lmin=C, rmax=-1; int q=0; long long st=0, e1=0; int r=0;
  while(st<maxs){
    uint8_t b=tp[p];
    if(q==0 && b==1 && p<=lmin && tp[p+1]==0){
      r++; printf("R %d ",r-1); int64_t hi=rmax; for(int64_t i=p+2;i<=hi;i++) putchar('0'+tp[i]); printf("  schritt=%lld e1=%lld\n",st,e1);
      if(r>maxr) break;
    }
    if(H[q][b]){ printf("HALT schritt %lld zustand %c\n",st,'A'+q); return 0; }
    if(q==4&&b==1) e1++;
    tp[p]=W[q][b];
    if(W[q][b]){ if(p<lmin)lmin=p; if(p>rmax)rmax=p; } else { if(p==lmin){ while(lmin<=rmax && !tp[lmin]) lmin++; if(lmin>rmax) lmin=C; } }
    if(p==rmax && !W[q][b]){ while(rmax>=0 && !tp[rmax]) rmax--; }
    p+=Mv[q][b]; q=N[q][b]; st++;
    if(p<2||p>C-3){printf("Rand\n");return 1;}
  }
  printf("ENDE schritte %lld e1 %lld\n",st,e1); return 0;
}
