/* Runden-Simulation (Thread 396, 25.11.2026) nach dem Besuchsgesetz aus busycoq PR #59, auf Zellebene, Zaehler n = 2^e - c.
   Gesetz: V(0x)=1x, V(100x)=000V(x), V(110x)=000V(x), V(1010x)=1010V(V(x)),
           V(1011x)= HALT (Modus 88) bzw. 0001x (Modus 396), V(111x)=HALT.
   Runde: s <- V(10 s), Start s = 1.
   Aufruf: runde <modus 88|396> <max_runden> [ausgabe_bis_runde] [startwort]  (FEHLER=1: falsche 1011-Regel, FEHLER=2: falsche Rundung im 2^e-c-Zweig) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef __int128 i128;
#ifndef SCHWELLE
#define SCHWELLE 64   /* ab 2^SCHWELLE wird n als 2^e - c gefuehrt; zum Testen kleiner waehlen (-DSCHWELLE=3) */
#endif
static int fehler = 0; /* Fehler-Schalter fuer die Negativkontrolle */
typedef struct { int64_t e; i128 c; } cnt;   /* n = 2^e - c */
static const i128 LIM = ((i128)1) << 120;
static void chk(i128 c){ if (c > LIM || c < -LIM) { fprintf(stderr,"UEBERLAUF c\n"); exit(3);} }
static int iszero(cnt n){ if (n.e >= 120) return 0; return n.c == (((i128)1) << n.e); }
static int odd(cnt n){ return n.e >= 1 ? (int)(n.c & 1) : (int)((1 - n.c) & 1); }
static cnt dec(cnt n){ n.c += 1; return n; }
static i128 fl2(i128 c){ return c >> 1; }            /* floor(c/2), arithm. Shift */
static cnt ceilh(cnt n){ if (n.e >= 1){ n.e--; n.c = fehler == 2 ? -((-n.c) >> 1) : fl2(n.c);} else { i128 v = 1 - n.c; v = (v+1)/2; n.c = 1 - v; } return n; }
static cnt dbl(cnt n){ n.e++; n.c *= 2; chk(n.c); return n; }
/* kleine exakte Zahl normalisieren: wenn e klein, als e=0 darstellen */
static cnt norm(cnt n){
  if (n.e > 0 && n.e < SCHWELLE){ i128 v = (((i128)1) << n.e) - n.c; n.e = 0; n.c = 1 - v; }
  if (n.e == 0){ i128 v = 1 - n.c; if (v >= (((i128)1) << SCHWELLE)){ int b = 0; while ((((i128)1) << b) < v) b++; n.e = b; n.c = (((i128)1) << b) - v; } }
  return n; }

static uint8_t *buf; static int64_t cap, st, en; /* Wort = buf[st..en) , rechts davon Nullen */
static int modus;
static int64_t ev1011 = 0, ev_round = 0, round_no = 0; static int64_t first1011 = -1;
static uint8_t cell(int64_t i){ return i < en ? buf[i] : 0; }
static void setc(int64_t i, uint8_t v){ if (i >= cap) { fprintf(stderr,"cap\n"); exit(4);} if (i >= en){ if(!v) return; memset(buf+en,0,i-en); en=i+1; } buf[i]=v; }
/* ein Besuch-Paket: n Besuche ab Position p. Rueckgabe 1 = Halt */
static int besuche(int64_t p, cnt n){
  for (;;){
    n = norm(n);
    if (iszero(n)) return 0;
    if (p >= en){ /* nur noch Nullen: n Besuche auf 0^inf; trotzdem zellweise weiter */ }
    uint8_t a = cell(p);
    if (a == 0){ setc(p,1); n = dec(n); n = norm(n); if (iszero(n)) return 0; }
    uint8_t b = cell(p+1), c = cell(p+2), d = cell(p+3);
    if (b == 1 && c == 1) return 1;                         /* 111: Halt */
    if (b == 0 && c == 1 && d == 0){ n = dbl(n); /* 2n */ p += 4; continue; }
    if (b == 0 && c == 1 && d == 1){                        /* 1011 */
      ev1011++; ev_round++; if (first1011 < 0) first1011 = round_no;
      if (ev1011 <= 200) { cnt m = n; printf("EREIGNIS 1011 Runde %lld Position %lld (von links) Besuche n = 2^%lld - %lld%s\n",
        (long long)round_no, (long long)(p - st), (long long)m.e, (long long)m.c, (m.c > (i128)INT64_MAX || m.c < (i128)INT64_MIN) ? " (c gekuerzt)" : ""); }
      if (modus == 88) return 2;
      setc(p,0); setc(p+1,0); setc(p+2,fehler == 1 ? 1 : 0); /* 0001 (Fehler-Schalter 1: 0011) */
      n = dec(n); n = norm(n); if (iszero(n)) return 0;
      setc(p,1); n = dec(n); n = norm(n); if (iszero(n)) return 0; /* 1001 -> Block 100, Rest beginnt bei p+3 */
      b = 0; c = 0;
    }
    /* Block 100 oder 110 im Zustand "geht durch", m = n Besuche, Breite 3 */
    {
      int par = odd(n);
      cnt pass = ceilh(n);
      /* Endzustand: m ungerade -> 000, m gerade (>=2) -> 100 */
      if (par){ setc(p,0); setc(p+1,0); setc(p+2,0); }
      else { setc(p,1); setc(p+1,0); setc(p+2,0); }
      n = pass; p += 3;
    }
  }
}
int main(int argc, char **argv){
  modus = atoi(argv[1]); int64_t maxr = atoll(argv[2]); int64_t outr = argc > 3 ? atoll(argv[3]) : 0;
  int64_t left = 2*maxr + 16; cap = left + 64*1024*1024; buf = calloc(cap,1);
  const char *w0 = (argc > 4) ? argv[4] : "1";   /* Startwort (Standard: s0 = 1, wie ab Leerband) */
  if (getenv("FEHLER")) fehler = atoi(getenv("FEHLER"));
  st = left; en = st; for (const char *q = w0; *q; q++) setc(st + (q - w0), (uint8_t)(*q - '0'));
  for (round_no = 1; round_no <= maxr; round_no++){
    st -= 2; buf[st] = 1; buf[st+1] = 0;  /* 10 s */
    cnt one = {0, 0};                     /* n = 1 */
    ev_round = 0;
    int r = besuche(st, one);
    while (en > st && buf[en-1] == 0) en--;
    if (r == 1){ printf("HALT 111 in Runde %lld, Wortlaenge %lld\n",(long long)round_no,(long long)(en-st)); return 0; }
    if (r == 2){ printf("HALT 1011 in Runde %lld, Wortlaenge %lld\n",(long long)round_no,(long long)(en-st)); return 0; }
    if (round_no <= outr){ printf("R %lld ", (long long)round_no); for (int64_t i = st; i < en; i++) putchar('0'+buf[i]); putchar('\n'); }
    if (first1011 >= 0 && (round_no < first1011 + 100 || ev_round)) printf("NACH Runde %lld Laenge %lld 1011-Ereignisse in der Runde %lld\n",(long long)round_no,(long long)(en-st),(long long)ev_round);
    if (round_no % 10000 == 0) { fprintf(stderr,"Runde %lld Laenge %lld 1011-Ereignisse %lld (erstes in Runde %lld)\n",(long long)round_no,(long long)(en-st),(long long)ev1011,(long long)first1011); }
  }
  printf("KEIN HALT bis Runde %lld, Wortlaenge %lld, 1011-Ereignisse %lld, erstes in Runde %lld\n",(long long)maxr,(long long)(en-st),(long long)ev1011,(long long)first1011);
}
