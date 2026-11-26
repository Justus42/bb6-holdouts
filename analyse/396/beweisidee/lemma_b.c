/* Programm B (zaehlend, wie runde_b: n Besuche gemeinsam pro Blockanfang), unabhaengig von lemma_a.py.
   Fuer alle Woerter bis Laenge N ohne Schluss-0: Ergebnis eines Besuchs, Treffer, Enden auf 0 vor 11,
   Ankuenfte mit 1 links davon (L1). Zaehlt wie lemma_a: ohne111, neu111 (Treffer oder 111 im Ergebnis),
   davon mit Ende vor 11, Verstoesse. FEHLER=1: Regel V(100x)=001V(x) (Negativkontrolle). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int w[4096], fehler;
static long L1, vor11;
static int z(int i) { return w[i]; }
static int besuche(int p, long n) {           /* 1 = Treffer */
  while (n > 0) {
    if (p > 0 && w[p-1]) L1++;
    int a = z(p), b = z(p+1), c = z(p+2), d = z(p+3);
    if (!a) { if (b && c) vor11++; w[p] = 1; n--; continue; }
    if (b && c) return 1;
    if (!c) {                                 /* 100/110: erster Besuch -> 000 und weiter, dann abwechselnd Ende (0->1) und weiter */
      long weiter = (n + 1) / 2, enden = n / 2;
      if (fehler && !b) { w[p] = 0; w[p+1] = 0; w[p+2] = 1; if (enden) { w[p] = 1; } /* falsche Regel */ }
      else { w[p] = (n % 2) ? 0 : 1; w[p+1] = 0; w[p+2] = 0; }
      (void)enden; n = weiter; p += 3; continue;
    }
    if (!d) { n *= 2; p += 4; continue; }     /* 1010 */
    w[p] = 0; w[p+1] = 0; w[p+2] = 0; n--;    /* 1011 -> 0001, ein Besuch endet */
  }
  return 0;
}
static int hat111(int len) { for (int i = 0; i + 2 < len; i++) if (w[i] && w[i+1] && w[i+2]) return 1; return 0; }
int main(int argc, char **argv) {
  int N = argc > 1 ? atoi(argv[1]) : 14; fehler = getenv("FEHLER") && atoi(getenv("FEHLER")) == 1;
  long woerter = 0, ohne = 0, neu = 0, neuv = 0, verst = 0, treffer = 0, nurerg = 0; long L1s = 0;
  for (int n = 0; n <= N; n++) for (long m = 0; m < (1L << n); m++) {
    if (n && !(m & 1)) continue;              /* letzte Zelle (Bit 0) = 1 */
    memset(w, 0, sizeof w);
    for (int i = 0; i < n; i++) w[i] = (m >> (n - 1 - i)) & 1;
    int o = !hat111(n + 2); woerter++;
    L1 = 0; vor11 = 0;
    int t = besuche(0, 1); treffer += t; L1s += L1;
    if (o) { ohne++; if (t || hat111(4000)) { neu++; if (!t) nurerg++; if (vor11) neuv++; else verst++; } }
  }
  printf("%sN=%d woerter=%ld ohne111=%ld neu111=%ld (davon Treffer %ld, nur Ergebnis %ld) neu111_vor11=%ld C1_verstoss=%ld L1=%ld treffer=%ld\n",
         fehler ? "FEHLER=1 " : "", N, woerter, ohne, neu, neu - nurerg, nurerg, neuv, verst, L1s, treffer);
  return 0;
}
