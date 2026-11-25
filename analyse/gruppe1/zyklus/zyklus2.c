/* Zweites, unabhaengig geschriebenes Programm zur Zyklusregel von Tabelle 114.
   Eigener Simulator (Feld-Band), eigene Token-Zerlegung, eigener Phasen-Automat, eigene Zyklusfunktion.
   Aufruf: zyklus2 <Start A|C|D> <Schritte>
   Negativkontrollen ueber ZYK_FEHLER=n1 (N1 schreibt k+3), =fress (x=a+4b+1), =j (J schreibt e3+1).
   Ausgabe: Zyklusanfaenge (Schrittzahlen), Phasen je Regel, Zyklen ok/nicht anwendbar/falsch, Paritaeten. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { int s; long n; } Tok;          /* s: 0, 1 oder 2 (=kein Trenner, nur ganz links) */
typedef struct { Tok *v; int len, cap; } TL;
static const char *FEHLER = "";

static void tl_init(TL *t){ t->cap=64; t->len=0; t->v=malloc(sizeof(Tok)*t->cap); }
static void tl_push(TL *t, int s, long n){ if(t->len==t->cap){ t->cap*=2; t->v=realloc(t->v,sizeof(Tok)*t->cap);} t->v[t->len].s=s; t->v[t->len].n=n; t->len++; }
static void tl_copy(TL *d, const TL *s){ d->len=0; for(int i=0;i<s->len;i++) tl_push(d,s->v[i].s,s->v[i].n); }
static int tl_eq(const TL *a, const TL *b){ if(a->len!=b->len) return 0; for(int i=0;i<a->len;i++) if(a->v[i].s!=b->v[i].s||a->v[i].n!=b->v[i].n) return 0; return 1; }

/* Band [lo,hi) -> Token: Trenner-Bits vor einem Block W^n (W=011); jedes Trenner-Bit ausser dem letzten wird (bit,0). */
static void zerlege(const unsigned char *b, long lo, long hi, TL *t){
    t->len=0; int pend[4096]; int np=0; long i=lo;
    while(i<hi){
        if(i+2<hi && b[i]==0 && b[i+1]==1 && b[i+2]==1){
            long n=0; while(i+2<hi && b[i]==0 && b[i+1]==1 && b[i+2]==1){ n++; i+=3; }
            if(np==0) tl_push(t,2,n);
            else { for(int k=0;k<np-1;k++) tl_push(t,pend[k],0); tl_push(t,pend[np-1],n); }
            np=0;
        } else { if(np<4096) pend[np++]=b[i]; i++; }
    }
}
static int unreg(Tok x){ return x.s==0 || x.n%2==0; }   /* Trenner 0 oder gerade Laenge */

/* ein Automatenschritt; Grenze = rechtestes unregelmaessiges Token in [0, len-2]. Rueckgabe Regel-Nr, <0 = nicht anwendbar */
enum { LG=0, N1, N2, N2s, UA, LE, VS, NREG };
static const char *RN[] = {"LG","N1","N2","N2s","UA","LE","VS"};
static int schritt(TL *t){
    int f=-1;
    for(int i=t->len-2;i>=0;i--) if(unreg(t->v[i])){ f=i; break; }
    if(f<0){ tl_push(t,0,0); memmove(t->v+1,t->v,sizeof(Tok)*(t->len-1)); t->v[0].s=1; t->v[0].n=1; return LG; }
    Tok g=t->v[f];
    if(g.s==0 && g.n%2==0){ t->v[f].s=1; t->v[f].n=g.n+(strcmp(FEHLER,"n1")?1:3); return N1; }
    int vorne10 = t->v[0].s==1 && t->v[0].n==0;
    if(f==0){
        if(!vorne10) return -1;  /* links? */
        memmove(t->v,t->v+1,sizeof(Tok)*(t->len-1)); t->len--; t->v[0].s=1; t->v[0].n+=2; return LE;
    }
    if(f==1 && vorne10 && g.s==0 && g.n%2==1){
        memmove(t->v,t->v+1,sizeof(Tok)*(t->len-1)); t->len--; t->v[0].s=1; t->v[0].n=g.n+2; return LE;
    }
    Tok h=t->v[f-1];
    if(h.n>=1 && ((g.s==0 && g.n%2==1) || (g.s==1 && g.n%2==0))){
        t->v[f-1].n--; t->v[f].s=0; t->v[f].n=g.n+2; return g.s==0?N2s:N2;
    }
    int h10 = h.s==1 && h.n==0;
    if(g.s==0 && g.n%2==1 && h10 && f>=2 && t->v[f-2].n>=1){
        t->v[f-2].n--; t->v[f-1].s=0; t->v[f-1].n=0; t->v[f].s=1; t->v[f].n=g.n+2; return UA;
    }
    if(g.s==1 && g.n%2==0 && g.n>=2 && h10 && f+1<t->len){
        long m=g.n/2+3; if(f-1-m<0) return -2;
        for(long i=f-1-m;i<f-1;i++) if(!(t->v[i].s==1 && t->v[i].n==1)) return -2;   /* VS-zuwenig */
        long p=t->v[f+1].n;
        TL u; tl_init(&u);
        for(long i=0;i<f-1-m;i++) tl_push(&u,t->v[i].s,t->v[i].n);
        tl_push(&u,1,0); tl_push(&u,0,2);
        for(long i=0;i<(g.n-2)/2;i++) tl_push(&u,1,3);
        tl_push(&u,1,2); tl_push(&u,0,p+4);
        for(int i=f+2;i<t->len;i++) tl_push(&u,t->v[i].s,t->v[i].n);
        free(t->v); *t=u; return VS;
    }
    return -3;  /* Sonder */
}
/* Randschritt: Schritt auf den ersten len-rechts+1 Token, Rest unveraendert */
static int randschritt(TL *t, int rechts){
    int k=t->len-rechts+1; TL kopf, rest; tl_init(&kopf); tl_init(&rest);
    for(int i=0;i<t->len;i++) tl_push(i<k?&kopf:&rest,t->v[i].s,t->v[i].n);
    int r=schritt(&kopf);
    if(r>=0){ t->len=0; for(int i=0;i<kopf.len;i++) tl_push(t,kopf.v[i].s,kopf.v[i].n); for(int i=0;i<rest.len;i++) tl_push(t,rest.v[i].s,rest.v[i].n); }
    free(kopf.v); free(rest.v); return r;
}
/* ganzer Zyklus; 0 = ok, sonst Fehlerstelle */
static int zyklus(TL *t){
    if(randschritt(t,2)<0) return 1;
    int L=t->len; if(L<4) return 2;
    Tok a=t->v[L-1], b=t->v[L-2], e3=t->v[L-3];
    if(a.s!=1 || e3.n<1) return 2;
    long x=a.n+4*b.n+(strcmp(FEHLER,"fress")?3:1);
    t->len=L-2; t->v[L-3].n=e3.n-1; tl_push(t,0,0); tl_push(t,1,x);   /* (s3,e3-1),(0,0),(1,x) */
    L=t->len; Tok e4=t->v[L-4]; long e3b=t->v[L-3].n;
    if(e4.n<1) return 3;
    t->len=L-2; t->v[L-4].n=e4.n-1; t->v[L-3].s=1; t->v[L-3].n=e3b+(strcmp(FEHLER,"j")?2:1);
    for(long i=0;i<x-1;i++) if(schritt(t)<0) return 4;
    if(randschritt(t,1)<0) return 5;
    return 0;
}

static const signed char TM[6][2][3] = {  /* 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC: schreibe, richtung, zustand */
 {{1,1,1},{-1,0,0}}, {{0,1,2},{0,-1,5}}, {{1,-1,3},{0,1,4}}, {{1,1,2},{0,-1,1}}, {{1,1,3},{1,1,0}}, {{1,-1,1},{0,-1,2}} };

int main(int argc, char **argv){
    if(getenv("ZYK_FEHLER")) FEHLER=getenv("ZYK_FEHLER");
    int q=argv[1][0]-'A'; long N=(long)atof(argv[2]);
    long W=300000; unsigned char *b=calloc(2*W,1); long p=W, lo=W, hi=W;
    long regel[NREG]={0}, phase_nicht=0, phase_paare=0;
    long zyk_ok=0, zyk_falsch=0, zyk_na[6]={0}, anf=0, a_gerade=0, alles_reg=0;
    TL prev, cur, start, pred; tl_init(&prev); tl_init(&cur); tl_init(&start); tl_init(&pred);
    long prev_r=-1; int warte_anfang=0, hat_start=0;
    FILE *fa=fopen(argc>3?argv[3]:"/dev/null","w");
    for(long n=0;n<N;n++){
        int s=b[p];
        if(q==2 && s==0 && b[p+1]==0){
            long j=p+2, r=0;
            while(j+2<=hi && b[j]==1 && b[j+1]==0 && b[j+2]==0){ r++; j+=3; }
            if(j==hi && b[j]==1){
                zerlege(b,lo,p,&cur);
                if(prev_r==r+1){
                    phase_paare++; TL u; tl_init(&u); tl_copy(&u,&prev);
                    int k=schritt(&u);
                    if(k>=0 && tl_eq(&u,&cur)) regel[k]++; else phase_nicht++;
                    free(u.v);
                }
                tl_copy(&prev,&cur); prev_r=r;
                if(r==0) warte_anfang=1;
            }
        }
        if(q==0 && s==1){ printf("HALT bei %ld\n",n); return 0; }
        const signed char *e=TM[q][s];
        b[p]=e[0]; p+=e[1]; q=e[2];
        if(p<lo) lo=p;
        if(p>hi){ hi=p;
            if(q==2 && warte_anfang){   /* Zyklusanfang: erster C-Rechtsrekord nach der letzten Phase (r=0) */
                warte_anfang=0; anf++;
                zerlege(b,lo,hi,&cur);
                Tok a=cur.v[cur.len-1];
                if(a.n%2==0) a_gerade++;
                int reg=1; for(int i=0;i<cur.len-1;i++) if(cur.v[i].s==0 || cur.v[i].n%2==0) reg=0;
                for(int i=0;i<cur.len;i++) if(cur.v[i].s==0) reg=0;
                if(reg && a.n%2==0) alles_reg++;
                fprintf(fa,"%ld a_gerade=%d alles_gerade=%d",n+1,(int)(a.n%2==0),(int)(reg && a.n%2==0));
                if(hat_start){
                    int z=zyklus(&pred);   /* pred enthaelt den vorigen Anfang */
                    if(z) zyk_na[z]++; else if(tl_eq(&pred,&cur)) zyk_ok++; else zyk_falsch++;
                    fprintf(fa," vorheriger_zyklus=%s", z?"na":(tl_eq(&pred,&cur)?"ok":"falsch"));
                }
                tl_copy(&pred,&cur); hat_start=1; fprintf(fa,"\n");
            }
        }
    }
    printf("start=%c schritte=%ld phasenpaare=%ld", argv[1][0], N, phase_paare);
    for(int k=0;k<NREG;k++) printf(" %s=%ld",RN[k],regel[k]);
    printf(" nicht_erklaert=%ld\n", phase_nicht);
    printf("zyklusanfaenge=%ld a_gerade=%ld alles_regulaer=%ld zyklen_ok=%ld zyklen_falsch=%ld nicht_anwendbar: rand_fressen=%ld fressen=%ld J=%ld phase=%ld rand_rueck=%ld\n",
        anf,a_gerade,alles_reg,zyk_ok,zyk_falsch,zyk_na[1],zyk_na[2],zyk_na[3],zyk_na[4],zyk_na[5]);
    return 0;
}
