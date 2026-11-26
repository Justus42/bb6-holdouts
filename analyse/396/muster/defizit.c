/* Programm X (Thread "396 Wachstumsmuster", 26.11.2026): Rundenrechnung 396 in Defizitform.
   Gesetz (busycoq PR #59 / rueckfuehrung_396.v): V(0x)=1x, V(100x)=V(110x)=000V(x), V(1010x)=1010V(V(x)),
   V(1011x)=0001x, V(111x)=Halt. Runde: s <- V(10 s), Start s = 1.
   Zaehler n = 2^e - c (e = Stufe, c = Defizit, klein); n = 0 genau wenn c = 2^e.
     Blockanfang 0:   1 schreiben, c+1, Zelle neu lesen
     1010:            e+1, c*2
     1011:            000 schreiben (0001), c+1, Zelle neu lesen
     1?0 (Ziffer):    n ungerade -> 000, n gerade -> 100; weiter ceil(n/2) = 2^(e-1) - floor(c/2) (e>=1) bzw. 1 (e=0)
   Ausgabe je Runde (ZEILEN=1, ab Runde VON):
     Z r laenge k eM stopabstand
       k = Laenge des fuehrenden Laufs (1010)^k, eM = FNV ueber die letzten M Zellen (M Standard 256, Vielfaches von 4),
       stopabstand = Wortende minus Stoppzelle des Laufs
     J r stelle abstand: Lauf stoppt auf einer 0 direkt vor einer 1 (neues 11, "junk")
   WORT=r1,r2,...: Wort dieser Runden in Tokenform (L=1010, H=100, Z=000, X=Zelle ausserhalb), Lauflaengen.
   APRE=1 (mit ZEILEN): zusaetzlich "A r hex": die M Zellen nach dem L-Lauf, je 4 Zellen eine Hexziffer.
   ZEIT=s: nach s Sekunden (Wanduhr) nach der laufenden Runde aufhoeren (ENDE-Zeile mit der erreichten Runde).
   PRUEF=1: Pruefsummen alle 1000 Runden im Format von runde.c (H r laenge fnv64).
   FEHLER=1: falsche Ziffernregel (Negativkontrolle).
   Aufruf: defizit <max_runden> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
static uint8_t *b; static int64_t cap, st, en;
static inline uint8_t zl(int64_t i){ return i < en ? b[i] : 0; }
static inline void sz(int64_t i, uint8_t v){ if (i >= en){ if (!v) return; if (i >= cap){ fprintf(stderr,"cap\n"); exit(4);} memset(b+en,0,i-en); en = i+1; } b[i] = v; }
static int fehler = 0;
static int64_t stop_p; static int junk;
/* ein Lauf; 1 = Halt */
static int lauf(void){
  int64_t p = st, e = 0; uint64_t c = 0;
  for (;;){
    if (e < 63 && c == ((uint64_t)1 << e)) { stop_p = p; return 0; }
    uint8_t a0 = zl(p);
    if (!a0){ sz(p,1); c++; if (e < 63 && c == ((uint64_t)1 << e)) { stop_p = p; junk = zl(p+1); return 0; } continue; }
    uint8_t a1 = zl(p+1), a2 = zl(p+2);
    if (a1 && a2) { stop_p = p; return 1; }
    if (!a1 && a2){
      if (!zl(p+3)) { e++; if (c > ((uint64_t)1 << 61)) { fprintf(stderr,"Defizit zu gross\n"); exit(5);} c <<= 1; p += 4; continue; }
      sz(p,0); sz(p+2,0); c++; continue;            /* 1011 -> 0001 */
    }
    int ung = e ? (int)(c & 1) : (int)((1 - c) & 1);
    if (fehler == 1) ung = !ung;
    sz(p, ung ? 0 : 1); sz(p+1,0); sz(p+2,0);
    if (e){ e--; c >>= 1; } else c = 0;
    p += 3;
  }
}
static uint64_t fnv(int64_t a, int64_t z){ uint64_t h = 1469598103934665603ULL; for (int64_t i = a; i < z; i++){ h ^= zl(i); h *= 1099511628211ULL; } return h; }
static int64_t anf_lim = 0; /* ANF=n: nur die ersten n Laeufe ausgeben */
static void wort(int64_t r){
  printf("W %lld", (long long)r); char last = 0; int64_t cnt = 0; int64_t i = st; int64_t nl = 0;
  while (i < en && (!anf_lim || nl <= anf_lim)){
    char t;
    if (zl(i)==1 && zl(i+1)==0 && zl(i+2)==1 && zl(i+3)==0){ t='L'; i+=4; }
    else if (zl(i)==1 && zl(i+1)==0 && zl(i+2)==0){ t='H'; i+=3; }
    else if (zl(i)==0 && zl(i+1)==0 && zl(i+2)==0){ t='Z'; i+=3; }
    else { t = zl(i) ? 'X' : 'Y'; i+=1; }
    if (t == last) cnt++; else { if (last) { printf(" %c%lld", last, (long long)cnt); nl++; } last = t; cnt = 1; }
  }
  if (last) printf(" %c%lld", last, (long long)cnt);
  printf("\n");
}
int main(int argc, char **argv){
  int64_t R = atoll(argv[1]);
  int64_t von = getenv("VON") ? atoll(getenv("VON")) : 1; int zeilen = getenv("ZEILEN") != NULL;
  int pruef = getenv("PRUEF") != NULL; int apre = getenv("APRE") != NULL; int M = getenv("M") ? atoi(getenv("M")) : 256;
  if (getenv("ANF")) anf_lim = atoll(getenv("ANF"));
  if (getenv("FEHLER")) fehler = atoi(getenv("FEHLER"));
  int64_t *wr = NULL; int nw = 0;
  if (getenv("WORT")){ char *s = strdup(getenv("WORT")); wr = malloc(sizeof(int64_t)*4096); for (char *q = strtok(s,","); q && nw < 4096; q = strtok(NULL,",")) wr[nw++] = atoll(q); }
  int64_t left = 2*R + 64; cap = left + 8*R + 1024*1024; b = calloc(cap,1);
  st = left; en = st; sz(st,1);
  int64_t k = 0; int64_t nj = 0;
  double zeit = getenv("ZEIT") ? atof(getenv("ZEIT")) : 0; time_t t0 = time(NULL);
  int64_t dvon = getenv("DIFF") ? atoll(getenv("DIFF")) : -1; uint8_t *alt = dvon >= 0 ? calloc(cap,1) : NULL; int64_t aen = 0;
  for (int64_t r = 1; r <= R; r++){
    if (alt && r >= dvon){ memcpy(alt+st, b+st, en-st); aen = en; }
    st -= 2; b[st] = 1; b[st+1] = 0; junk = 0;
    if (lauf()){ printf("HALT %lld %lld\n",(long long)r,(long long)(stop_p-st)); return 1; }
    while (en > st && !b[en-1]) en--;
    if (alt && r >= dvon){ /* DIFF=r0: geaenderte Zellen (absolute Lage) als Abschnitte, Luecken < 64 zusammengefasst */
      int64_t lo = st+2, hi = en > aen ? en : aen; printf("D %lld st=%lld",(long long)r,(long long)st); int64_t s0 = -1, l1 = -1;
      for (int64_t i = lo; i < hi; i++){ uint8_t o = i < aen ? alt[i] : 0, n = i < en ? b[i] : 0;
        if (o != n){ if (s0 < 0) s0 = i; else if (i - l1 > 64){ printf(" %lld-%lld",(long long)s0,(long long)l1); s0 = i; } l1 = i; } }
      if (s0 >= 0) printf(" %lld-%lld",(long long)s0,(long long)l1);
      printf(" ende=%lld\n",(long long)en); }
    if (junk) { nj++; printf("J %lld %lld %lld\n",(long long)r,(long long)(stop_p-st),(long long)(en-stop_p)); }
    if (zeilen && r >= von){
      /* L-Lauf (1010)^k am Wortanfang: waechst nur; ab k-1 neu pruefen, alle 1000 Runden ganz */
      if (k > 0) k--;
      if (r % 1000 == 0) k = 0;
      while (zl(st+4*k)==1 && zl(st+4*k+1)==0 && zl(st+4*k+2)==1 && zl(st+4*k+3)==0 && st+4*k+3 < en) k++;
      int64_t a = st + 4*k;
      printf("Z %lld %lld %lld %016llx %lld\n",(long long)r,(long long)(en-st),(long long)k,
        (unsigned long long)fnv(en-M>st?en-M:st, en),(long long)(en-stop_p));
      if (apre){ /* M Zellen nach dem L-Lauf, je 4 Zellen eine Hexziffer (erste Zelle = Bit 8) */
        printf("A %lld ",(long long)r);
        for (int64_t i = a; i < a + M; i += 4) putchar("0123456789abcdef"[zl(i)*8 + zl(i+1)*4 + zl(i+2)*2 + zl(i+3)]);
        putchar('\n'); }
    }
    if (pruef && r % 1000 == 0) printf("H %lld %lld %016llx\n",(long long)r,(long long)(en-st),(unsigned long long)fnv(st,en));
    for (int j = 0; j < nw; j++) if (wr[j] == r) wort(r);
    if (zeit > 0 && difftime(time(NULL), t0) > zeit){ printf("ENDE %lld %lld junk %lld\n",(long long)r,(long long)(en-st),(long long)nj); return 0; }
  }
  printf("ENDE %lld %lld junk %lld\n",(long long)R,(long long)(en-st),(long long)nj);
  return 0;
}
