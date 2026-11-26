/* Zweites Programm, unabhaengig von pr76_port.py: direkte Simulation von 133 mit seiner eigenen Tabelle
   (keine Umbenennung, keine Makros). Protokolliert jeden Zeitpunkt, an dem der Kopf in Zustand C steht und
   das Kopffeld sowie alles links davon 0 ist (das ist, gespiegelt und umbenannt, "Zustand A am rechten Ende"
   in 581-Koordinaten). Ausgabe je Ereignis: Schritt, Wortlaenge, FNV-1a-64 des Worts von der hoechsten 1
   abwaerts bis zum Feld rechts neben dem Kopf. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define N (1<<22)
static unsigned char t[N];
int main(int argc,char**argv){
  const char*M="1RB0LC_1LC0RE_1LD1LB_1LA1LD_1RF0RA_---1RE";
  long long maxs=atoll(argv[1]);
  int wr[6][2],mv[6][2],nx[6][2],hal[6][2];
  for(int q=0;q<6;q++)for(int r=0;r<2;r++){const char*g=M+7*q+3*r;
    if(g[0]=='-'){hal[q][r]=1;continue;} hal[q][r]=0; wr[q][r]=g[0]-'0'; mv[q][r]=g[1]=='R'?1:-1; nx[q][r]=g[2]-'A';}
  long p=N/2,lo1=N,hi1=-1; int q=0; long long s;
  /* lo1/hi1: kleinste/groesste Position, die je eine 1 trug (obere Schranke fuer Einsen) */
  for(s=0;s<maxs;s++){
    if(q==2){ int ok=1; long a=lo1<p?lo1:p; for(long i=a;i<=p;i++) if(t[i]){ok=0;break;}
      if(ok){ long top=hi1; while(top>p && !t[top]) top--; uint64_t h=1469598103934665603ULL; long len=0;
        for(long i=top;i>p;i--){h^=(unsigned char)('0'+t[i]);h*=1099511628211ULL;len++;}
        printf("%lld %ld %016llx\n",s,len,(unsigned long long)h);} }
    int r=t[p]; if(hal[q][r]){printf("HALT %lld\n",s);return 0;}
    t[p]=wr[q][r]; if(t[p]){if(p<lo1)lo1=p;if(p>hi1)hi1=p;}
    p+=mv[q][r]; q=nx[q][r];
    if(p<1||p>=N-1){fprintf(stderr,"Band zu kurz bei %lld\n",s);return 1;}
  }
  fprintf(stderr,"ende %lld\n",s); return 0;
}
