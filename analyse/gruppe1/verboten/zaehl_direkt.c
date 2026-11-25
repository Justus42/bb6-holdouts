/* Programm 1 (direkte Simulation, Zelle fuer Zelle) fuer "Halt als verbotenes Muster", Tabelle 114.

   Gezaehlt wird jeder Schritt, der den Kopf nach RECHTS bewegt: Zustand X nach dem Schritt und die drei
   Zellen z, z+1, z+2 ab der neuen Kopfposition z. Notwendiges Muster fuer Halt ist X = C mit 0 1 1
   (Begruendung im Bericht); X = C mit 1 1 1 ist der Halt selbst (C1 -> E1 -> A1).

   Ausgabe: "gesamt X zzz anzahl" fuer die Schritte 0 .. N-1. Danach laeuft das Programm bis zum
   naechsten Phasen-Schnappschuss (wie direkt.c) und gibt dieselbe Zaehlung je Phasenart aus:
   "phase <art> X zzz anzahl"; art = anlauf (vor dem ersten Schnappschuss), ueb (r = 0), vs, na
   (Automat nicht anwendbar oder Rest), sonst die Automatenregel (LG N1 N2 N2s UA LE). Die Arten ueb,
   vs, na sind genau die Phasen, die beschleuniger.py mit dem Durchlaufmodell nachrechnet ("rueckfall").
   Aufruf: zaehl_direkt <A|C|D> <schritte>
   Negativkontrolle: ZAEHL_FEHLER=zustand zaehlt den Zustand VOR dem Schritt statt danach. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "teile_direkt.h"

static const signed char TM[6][2][3] = {  /* 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC */
 {{1,1,1},{-1,0,0}}, {{0,1,2},{0,-1,5}}, {{1,-1,3},{0,1,4}}, {{1,1,2},{0,-1,1}}, {{1,1,3},{1,1,0}}, {{1,-1,1},{0,-1,2}} };

enum { B_ANL=0, B_UEB, B_VS, B_NA, B_LG, B_N1, B_N2, B_N2s, B_UA, B_LE, NB };
static const char *BN[NB] = {"anlauf","ueb","vs","na","LG","N1","N2","N2s","UA","LE"};

static long cnt[NB][6][8], cur[6][8], ges[6][8], phasen[NB];

int main(int argc, char **argv){
    if(argc<3){ fprintf(stderr,"Aufruf: zaehl_direkt <A|C|D> <schritte>\n"); return 2; }
    int fehler = getenv("ZAEHL_FEHLER") && !strcmp(getenv("ZAEHL_FEHLER"),"zustand");
    int q=argv[1][0]-'A'; long N=(long)atof(argv[2]);
    long W=1L<<26; unsigned char *b=calloc(2*W,1); long p=W, lo=W, hi=W;
    TL prev, u; tl_init(&prev); tl_init(&u);
    int bucket=B_ANL; int ges_fertig=0; long halt=-1;
    for(long n=0;;n++){
        if(n==N){ memcpy(ges,cur,sizeof ges); for(int k=0;k<NB;k++) for(int x=0;x<6;x++) for(int z=0;z<8;z++) ges[x][z]+=cnt[k][x][z]; ges_fertig=1; }
        int s=b[p];
        if(q==2 && s==0 && b[p+1]==0){
            long j=p+2, r=0;
            while(j+2<=hi && b[j]==1 && b[j+1]==0 && b[j+2]==0){ r++; j+=3; }
            if(j==hi && b[j]==1){
                /* Phase zu Ende: Zaehler der laufenden Phase ihrer Art zuschlagen */
                for(int x=0;x<6;x++) for(int z=0;z<8;z++){ cnt[bucket][x][z]+=cur[x][z]; cur[x][z]=0; }
                phasen[bucket]++;
                if(ges_fertig) break;
                zerlege(b,lo,p,&prev);
                if(r==0) bucket=B_UEB;
                else if(prev.nrest>0 || prev.len<2) bucket=B_NA;
                else { tl_copy(&u,&prev); int k=schritt(&u);
                    bucket = k<0 ? B_NA : k==VS ? B_VS : k==LG ? B_LG : k==N1 ? B_N1 : k==N2 ? B_N2 : k==N2s ? B_N2s : k==UA ? B_UA : B_LE; }
            }
        }
        if(q==0 && s==1){ halt=n; break; }
        const signed char *e=TM[q][s];
        int qvor=q;
        b[p]=e[0]; p+=e[1]; q=e[2];
        if(e[1]==1) cur[fehler?qvor:q][b[p]*4+b[p+1]*2+b[p+2]]++;
        if(p<lo){ lo=p; if(lo<2){ fprintf(stderr,"Band zu kurz\n"); return 3; } }
        if(p>hi){ hi=p; if(hi>2*W-4){ fprintf(stderr,"Band zu kurz\n"); return 3; } }
    }
    if(halt>=0) printf("HALT bei Schritt %ld\n",halt);
    for(int x=0;x<6;x++) for(int z=0;z<8;z++) if(ges[x][z]) printf("gesamt %c %d%d%d %ld\n","ABCDEF"[x],z>>2,(z>>1)&1,z&1,ges[x][z]);
    for(int k=0;k<NB;k++){
        printf("phasen %s %ld\n",BN[k],phasen[k]);
        for(int x=0;x<6;x++) for(int z=0;z<8;z++) if(cnt[k][x][z]) printf("phase %s %c %d%d%d %ld\n",BN[k],"ABCDEF"[x],z>>2,(z>>1)&1,z&1,cnt[k][x][z]);
    }
    return 0;
}
