/* Unveraendert aus ../linkes_ende/direkt.c uebernommen (Token-Zerlegung, Phasen-Automat aus PR 9). */
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

