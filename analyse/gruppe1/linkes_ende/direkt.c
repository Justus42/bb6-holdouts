/* Zweites, unabhaengiges Programm zum Beschleuniger (beschleuniger.py): direkte Simulation von
   Tabelle 114 Zelle fuer Zelle, ohne Durchlaufmodell und ohne Kostenformel.

   An jedem Phasen-Schnappschuss (Zustand C liest 0, rechts davon 0 (100)^r 1 bis zum rechten Ende,
   wie snap.py / zyklus2.c) wird das Band links vom Kopf in Token (t, n) zerlegt (eigene Zerlegung).
   Ausgabe 1 (Datei <schnapp>): je Schnappschuss "n r crc", crc32 der Token-Zeile
     "t:n t:n ... /rest"  (t = 0, 1 oder _ fuer "kein Trenner", rest = Bits nach dem letzten 011-Lauf);
     crc nur wenn n < crc_bis oder r == 0, sonst "-".
   Ausgabe 2 (Datei <formen>, nur wenn angegeben): jede Phase, die der Phasen-Automat aus PR 9 nicht
     erklaert, und jeder Zyklusuebergang (Schnappschuss mit r = 0 bis zum naechsten), den die
     Zyklusfunktion aus PR 9 (Randschritt Rueckweg, Randschritt Fressen, Fressen, J) nicht erklaert:
     "n r art | vorher | nachher | r'=..." im selben Format wie beschleuniger.py.
     Der Automat ist aus zyklus2.c (PR 9, unabhaengig von automat.py geschrieben) uebernommen.
   Halt: jeder Schritt wird simuliert; liest A eine 1, wird "HALT" gemeldet.
   Aufruf: direkt <A|C|D> <schritte> <crc_bis> <schnapp-datei> [<formen-datei>]
   Negativkontrolle: DIREKT_FEHLER=vs (VS schreibt p+6 statt p+4) muss Formen-Abgleich stoeren. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---------- crc32 (wie zlib) ---------- */
static unsigned int crctab[256];
static void crc_init(void){ for(unsigned i=0;i<256;i++){ unsigned c=i; for(int k=0;k<8;k++) c = (c&1)? 0xEDB88320u^(c>>1) : c>>1; crctab[i]=c; } }
static unsigned crc_add(unsigned c, const char *s, long len){ for(long i=0;i<len;i++) c = crctab[(c^(unsigned char)s[i])&0xff]^(c>>8); return c; }

/* ---------- Token-Listen ---------- */
typedef struct { int s; long n; } Tok;          /* s: 0, 1, 2 (= kein Trenner) */
typedef struct { Tok *v; long len, cap; char *rest; long nrest, caprest; } TL;
static void tl_init(TL *t){ t->cap=1024; t->len=0; t->v=malloc(sizeof(Tok)*t->cap); t->caprest=1024; t->nrest=0; t->rest=malloc(t->caprest); }
static void tl_push(TL *t, int s, long n){ if(t->len==t->cap){ t->cap*=2; t->v=realloc(t->v,sizeof(Tok)*t->cap);} t->v[t->len].s=s; t->v[t->len].n=n; t->len++; }
static void rest_push(TL *t, char c){ if(t->nrest==t->caprest){ t->caprest*=2; t->rest=realloc(t->rest,t->caprest);} t->rest[t->nrest++]=c; }
static void tl_copy(TL *d, const TL *s){ d->len=0; for(long i=0;i<s->len;i++) tl_push(d,s->v[i].s,s->v[i].n); d->nrest=0; for(long i=0;i<s->nrest;i++) rest_push(d,s->rest[i]); }
static int tl_eq(const TL *a, const TL *b){ if(a->len!=b->len || a->nrest!=b->nrest) return 0; for(long i=0;i<a->len;i++) if(a->v[i].s!=b->v[i].s||a->v[i].n!=b->v[i].n) return 0; return memcmp(a->rest,b->rest,a->nrest)==0; }

/* Zerlegung von b[lo..p-1]: von links; an jeder Stelle mit 0,1,1 beginnt ein Lauf aus 011-Bloecken,
   alle anderen Bits sammeln sich als Trenner. */
static void zerlege(const unsigned char *b, long lo, long p, TL *t){
    t->len=0; t->nrest=0;
    long i=lo;
    while(i<p){
        if(i+2<p && b[i]==0 && b[i+1]==1 && b[i+2]==1){
            long n=0;
            while(i+2<p && b[i]==0 && b[i+1]==1 && b[i+2]==1){ n++; i+=3; }
            if(t->nrest==0) tl_push(t,2,n);
            else { for(long k=0;k<t->nrest-1;k++) tl_push(t,t->rest[k]-'0',0); tl_push(t,t->rest[t->nrest-1]-'0',n); }
            t->nrest=0;
        } else { rest_push(t,(char)('0'+b[i])); i++; }
    }
}
static char *zeile_buf=NULL; static long zeile_cap=0;
static long zeile(const TL *t){   /* Text in zeile_buf, Rueckgabe Laenge */
    long need = t->len*24 + t->nrest + 8;
    if(need>zeile_cap){ zeile_cap=need*2; zeile_buf=realloc(zeile_buf,zeile_cap); }
    long k=0;
    for(long i=0;i<t->len;i++){
        if(i) zeile_buf[k++]=' ';
        zeile_buf[k++] = t->v[i].s==2 ? '_' : (char)('0'+t->v[i].s);
        k += sprintf(zeile_buf+k, ":%ld", t->v[i].n);
    }
    zeile_buf[k++]=' '; zeile_buf[k++]='/';
    memcpy(zeile_buf+k,t->rest,t->nrest); k+=t->nrest; zeile_buf[k]=0;
    return k;
}

/* ---------- Phasen-Automat (aus zyklus2.c, PR 9) ---------- */
static const char *FEHLER="";
static int unreg(Tok x){ return x.s==0 || x.n%2==0; }
enum { LG=0, N1, N2, N2s, UA, LE, VS, NREG };
static const char *RN[] = {"LG","N1","N2","N2s","UA","LE","VS"};
static int schritt(TL *t){
    long f=-1;
    for(long i=t->len-2;i>=0;i--) if(unreg(t->v[i])){ f=i; break; }
    if(f<0){ tl_push(t,0,0); memmove(t->v+1,t->v,sizeof(Tok)*(t->len-1)); t->v[0].s=1; t->v[0].n=1; return LG; }
    Tok g=t->v[f];
    if(g.s==0 && g.n%2==0){ t->v[f].s=1; t->v[f].n=g.n+1; return N1; }
    int vorne10 = t->v[0].s==1 && t->v[0].n==0;
    if(f==0){
        if(!vorne10) return -1;
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
        for(long i=f-1-m;i<f-1;i++) if(!(t->v[i].s==1 && t->v[i].n==1)) return -2;
        long p=t->v[f+1].n;
        TL u; tl_init(&u);
        for(long i=0;i<f-1-m;i++) tl_push(&u,t->v[i].s,t->v[i].n);
        tl_push(&u,1,0); tl_push(&u,0,2);
        for(long i=0;i<(g.n-2)/2;i++) tl_push(&u,1,3);
        tl_push(&u,1,2); tl_push(&u,0,p+(strcmp(FEHLER,"vs")?4:6));
        for(long i=f+2;i<t->len;i++) tl_push(&u,t->v[i].s,t->v[i].n);
        free(t->v); free(t->rest); *t=u; return VS;
    }
    return -3;
}
static const char *grund(int k){ return k==-1?"links?":k==-2?"VS-zuwenig":"Sonder"; }
static int randschritt(TL *t, int rechts){
    long k=t->len-rechts+1; TL kopf; tl_init(&kopf);
    for(long i=0;i<k && i<t->len;i++) tl_push(&kopf,t->v[i].s,t->v[i].n);
    int r=schritt(&kopf);
    if(r>=0){ TL u; tl_init(&u); for(long i=0;i<kopf.len;i++) tl_push(&u,kopf.v[i].s,kopf.v[i].n);
        for(long i=k;i<t->len;i++) tl_push(&u,t->v[i].s,t->v[i].n);
        free(t->v); free(t->rest); *t=u; }
    free(kopf.v); free(kopf.rest); return r;
}
/* Zyklusuebergang ab Schnappschuss r=0; Rueckgabe NULL = ok, sonst Grund */
static char ugrund[64];
static const char *uebergang(TL *t){
    int k=randschritt(t,1); if(k<0){ sprintf(ugrund,"rand_rueck:%s",grund(k)); return ugrund; }
    k=randschritt(t,2);     if(k<0){ sprintf(ugrund,"rand_fressen:%s",grund(k)); return ugrund; }
    long L=t->len; if(L<4) return "kurz";
    Tok a=t->v[L-1], b=t->v[L-2], e3=t->v[L-3];
    if(a.s!=1 || e3.n<1) return "fressen";
    long x=a.n+4*b.n+3;
    t->len=L-2; t->v[L-3].n=e3.n-1; tl_push(t,0,0); tl_push(t,1,x);
    L=t->len; Tok e4=t->v[L-4]; long e3b=t->v[L-3].n;
    if(e4.n<1) return "J";
    t->len=L-2; t->v[L-4].n=e4.n-1; t->v[L-3].s=1; t->v[L-3].n=e3b+2;
    return NULL;
}

static const signed char TM[6][2][3] = {  /* 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC */
 {{1,1,1},{-1,0,0}}, {{0,1,2},{0,-1,5}}, {{1,-1,3},{0,1,4}}, {{1,1,2},{0,-1,1}}, {{1,1,3},{1,1,0}}, {{1,-1,1},{0,-1,2}} };

int main(int argc, char **argv){
    if(argc<5){ fprintf(stderr,"Aufruf: direkt <A|C|D> <schritte> <crc_bis> <schnapp> [<formen>]\n"); return 2; }
    if(getenv("DIREKT_FEHLER")) FEHLER=getenv("DIREKT_FEHLER");
    crc_init();
    int q=argv[1][0]-'A'; long N=(long)atof(argv[2]); long crc_bis=(long)atof(argv[3]);
    FILE *fs=fopen(argv[4],"w"); FILE *ff = argc>5 ? fopen(argv[5],"w") : NULL;
    long W=1L<<25; unsigned char *b=calloc(2*W,1); long p=W, lo=W, hi=W;
    TL prev, cur, u; tl_init(&prev); tl_init(&cur); tl_init(&u);
    long prev_r=-1, prev_n=0, schnapp=0, a_liest_1=0, rekorde_phase=0, rekorde_ueb=0;
    long n;
    for(n=0;n<N;n++){
        int s=b[p];
        if(q==2 && s==0 && b[p+1]==0){
            long j=p+2, r=0;
            while(j+2<=hi && b[j]==1 && b[j+1]==0 && b[j+2]==0){ r++; j+=3; }
            if(j==hi && b[j]==1){
                schnapp++;
                int brauche = (n<crc_bis || r==0 || ff!=NULL);
                if(brauche) zerlege(b,lo,p,&cur);
                if(n<crc_bis || r==0){ long k=zeile(&cur); fprintf(fs,"%ld %ld %u\n",n,r,crc_add(0xFFFFFFFFu,zeile_buf,k)^0xFFFFFFFFu); }
                else fprintf(fs,"%ld %ld -\n",n,r);
                if(ff && prev_r>=0){
                    tl_copy(&u,&prev);
                    const char *art=NULL; char artbuf[80];
                    if(prev_r>=1){
                        if(prev.nrest>0 || prev.len<2) art="na:rest";
                        else {
                            int k=schritt(&u);
                            if(k<0){ sprintf(artbuf,"na:%s",grund(k)); art=artbuf; }
                            else if(!(tl_eq(&u,&cur) && r==prev_r-1)){ sprintf(artbuf,"%s-falsch",RN[k]); art=artbuf; }
                        }
                        if(art) rekorde_phase++;
                    } else {
                        if(prev.nrest>0) art="Ueb-na:rest";
                        else {
                            const char *g=uebergang(&u);
                            if(g){ sprintf(artbuf,"Ueb-na:%s",g); art=artbuf; }
                            else if(!(tl_eq(&u,&cur) && cur.nrest==0)) art="Ueb-falsch";
                        }
                        if(art) rekorde_ueb++;
                    }
                    if(art){
                        fprintf(ff,"%ld %ld %s | ",prev_n,prev_r,art);
                        zeile(&prev); fputs(zeile_buf,ff); fputs(" | ",ff);
                        zeile(&cur); fputs(zeile_buf,ff); fprintf(ff," | r'=%ld\n",r);
                    }
                }
                if(ff) tl_copy(&prev,&cur);
                prev_r=r; prev_n=n;
            }
        }
        if(q==0 && s==1){ a_liest_1++; printf("HALT bei Schritt %ld\n",n); break; }
        const signed char *e=TM[q][s];
        b[p]=e[0]; p+=e[1]; q=e[2];
        if(p<lo){ lo=p; if(lo<2){ fprintf(stderr,"Band zu kurz\n"); return 3; } }
        if(p>hi){ hi=p; if(hi>2*W-4){ fprintf(stderr,"Band zu kurz\n"); return 3; } }
    }
    fclose(fs); if(ff) fclose(ff);
    printf("start=%c schritte=%ld breite=%ld schnappschuesse=%ld A_liest_1=%ld rekorde_phase=%ld rekorde_uebergang=%ld\n",
           argv[1][0], n, hi-lo+1, schnapp, a_liest_1, rekorde_phase, rekorde_ueb);
    return 0;
}
