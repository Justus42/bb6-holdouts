/* m5sim.c - Simulator fuer die Analyse 318/518 (Hauptprogramm, C).
 *
 * Aufrufe:
 *   m5sim paare  <tm> <start> <N>     Zaehlt alle Paare aufeinanderfolgender Uebergaenge
 *                                     (Zustand,Symbol) -> (Zustand,Symbol) in N Schritten.
 *   m5sim gleich <N> [stoer]          318, 518 und M5 im Gleichschritt ab Leerband (Start A):
 *                                     prueft je Schritt Schreiben, Bewegung und Zustandsbild.
 *                                     "stoer" = Negativkontrolle (518 mit E0=1RA statt 0RA).
 *   m5sim links  <tm> <start> <N>     Gibt jeden Links-Rekord aus (Schritt, Zustand, Breite).
 *   m5sim zyklen <tm> <start> <N> <K> Gibt Schritt, Zustand und Band (linkes Ende bis vor den Kopf)
 *                                     an jedem Rechts-Rekord aus, dem ein Ausflug von mindestens
 *                                     K Schritten vorausging (= Beginn eines Zyklus).
 * Band: Array fester Groesse, Start in der Mitte. Halteuebergang "---" beendet den Lauf.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W (1<<22)
static unsigned char tape[W];


typedef struct { int n; int wr[8][2], mv[8][2], nx[8][2], h[8][2]; } M;

static void lese(const char *s, M *m) {
  size_t L = strlen(s);
  int n = (int)((L + 1) / 7), i, b;
  if ((size_t)(7 * n - 1) != L) { fprintf(stderr, "Format?\n"); exit(2); }
  m->n = n;
  for (i = 0; i < n; i++)
    for (b = 0; b < 2; b++) {
      const char *p = s + 7 * i + 3 * b;
      if (p[0] == '-') { m->h[i][b] = 1; m->wr[i][b] = 1; m->mv[i][b] = 1; m->nx[i][b] = 0; continue; }
      m->h[i][b] = 0;
      m->wr[i][b] = p[0] - '0';
      m->mv[i][b] = (p[1] == 'R') ? 1 : -1;
      m->nx[i][b] = p[2] - 'A';
    }
}

static const char *S318 = "1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC";
static const char *S518 = "1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---";
static const char *SM5  = "1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC";

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "Aufruf siehe Kopf\n"); return 2; }
  if (!strcmp(argv[1], "gleich")) {
    long long N = atoll(argv[2]), i;
    M a, b, c; lese(S318, &a); lese(S518, &b); lese(SM5, &c);
    /* Negativkontrolle: "stoer" aendert bei 518 den Uebergang E0 (0RA -> 1RA). */
    if (argc > 3 && !strcmp(argv[3], "stoer")) b.wr[4][0] = 1;
    /* Zustandsbild 318 -> M5 und 518 -> M5 (aus der Tabelle bestimmt, hier nur geprueft) */
    int f318[6] = {0, 1, 2, 3, 0, 4}, f518[6] = {0, 1, 2, 3, 4, 4};
    long p = W / 2; int sa = 0, sb = 0, sc = 0;
    memset(tape, 0, W);
    for (i = 0; i < N; i++) {
      int s = tape[p];
      if (a.h[sa][s] || b.h[sb][s]) {
        printf("Haltefeld erreicht in Schritt %lld: 318 %c%d, 518 %c%d\n", i + 1, 'A' + sa, s, 'A' + sb, s);
        return 0;
      }
      if (a.wr[sa][s] != c.wr[sc][s] || b.wr[sb][s] != c.wr[sc][s] ||
          a.mv[sa][s] != c.mv[sc][s] || b.mv[sb][s] != c.mv[sc][s] ||
          f318[a.nx[sa][s]] != c.nx[sc][s] || f518[b.nx[sb][s]] != c.nx[sc][s]) {
        printf("ABWEICHUNG in Schritt %lld\n", i + 1); return 1;
      }
      tape[p] = c.wr[sc][s]; p += c.mv[sc][s];
      sa = a.nx[sa][s]; sb = b.nx[sb][s]; sc = c.nx[sc][s];
      if (p <= 0 || p >= W - 1) { printf("Band zu klein\n"); return 3; }
    }
    printf("gleich %lld Schritte, kein Haltefeld\n", N);
    return 0;
  }
  if (argc < 5) { fprintf(stderr, "Aufruf siehe Kopf\n"); return 2; }
  M m; lese(argv[2], &m);
  int st = argv[3][0] - 'A';
  long long N = atoll(argv[4]), i;
  long p = W / 2, lo = p, hi = p;
  memset(tape, 0, W);
  if (!strcmp(argv[1], "paare")) {
    static long long cnt[16][16];
    int prev = -1;
    for (i = 0; i < N; i++) {
      int s = tape[p], cur = 2 * st + s;
      if (prev >= 0) cnt[prev][cur]++;
      if (m.h[st][s]) { printf("HALT in Schritt %lld (%c%d)\n", i + 1, 'A' + st, s); break; }
      tape[p] = m.wr[st][s]; p += m.mv[st][s]; st = m.nx[st][s]; prev = cur;
      if (p <= 0 || p >= W - 1) { printf("Band zu klein\n"); return 3; }
    }
    printf("Schritte %lld\n", i);
    for (int x = 0; x < 2 * m.n; x++)
      for (int y = 0; y < 2 * m.n; y++)
        if (cnt[x][y]) printf("%c%d %c%d %lld\n", 'A' + x / 2, x % 2, 'A' + y / 2, y % 2, cnt[x][y]);
    return 0;
  }
  if (!strcmp(argv[1], "links") || !strcmp(argv[1], "zyklen")) {
    int zyk = !strcmp(argv[1], "zyklen");
    long long K = zyk ? atoll(argv[5]) : 0, last = 0;
    for (i = 0; i < N; i++) {
      int s = tape[p];
      if (m.h[st][s]) { printf("HALT in Schritt %lld\n", i + 1); return 0; }
      tape[p] = m.wr[st][s]; p += m.mv[st][s]; st = m.nx[st][s];
      if (p <= 0 || p >= W - 1) { printf("Band zu klein\n"); return 3; }
      if (p < lo) { lo = p; if (!zyk) printf("%lld %c %ld\n", i + 1, 'A' + st, hi - lo + 1); }
      if (p > hi) {
        hi = p;
        if (zyk && i + 1 - last >= K) {
          printf("%lld %c ", i + 1, 'A' + st);
          for (long q = lo; q < hi; q++) putchar('0' + tape[q]);
          putchar('\n');
        }
        last = i + 1;
      }
    }
    return 0;
  }
  fprintf(stderr, "unbekannter Modus\n");
  return 2;
}
