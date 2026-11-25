/* Zweitprogramm (unabhaengig von den Python-Skripten): direkte Simulation
   ab Leerband, Start A.  Aufruf:
     zweitpruefung <maschine> <schritte>            -> Zusammenfassung
     zweitpruefung <maschine> <schritte> liste [start] -> statt dessen bei jedem
        Rechts-Rekord in Zustand C die Liste der Nullabstaende, von rechts gelesen
        (3er-Abstaende gezaehlt, | = Abstand 4, <g> = anderer Abstand);
        start = Startzustand (Standard A)
   Band: Array fester Groesse, Kopf startet in der Mitte. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int wr[8][2], mv[8][2], nx[8][2];
static int parse(const char *m) {
  int ns = 0; const char *p = m;
  while (*p) {
    for (int s = 0; s < 2; s++) {
      if (p[0] == '-') { wr[ns][s] = 1; mv[ns][s] = 1; nx[ns][s] = -1; }
      else { wr[ns][s] = p[0]-'0'; mv[ns][s] = p[1]=='R' ? 1 : -1; nx[ns][s] = p[2]-'A'; }
      p += 3;
    }
    ns++; if (*p == '_') p++;
  }
  return ns;
}
int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage\n"); return 2; }
  parse(argv[1]);
  long long N = atoll(argv[2]); int liste = argc > 3;
  long long size = N / 2 + 1000; if (size > 50000000LL) size = 50000000LL; /* Breite waechst etwa wie Wurzel der Schritte */
  unsigned char *t = calloc(size, 1);
  long long p = size / 2, lo = p, hi = p, nL = 0, nR = 0, n;
  int q = (argc > 4) ? argv[4][0] - 'A' : 0, halted = 0;
  for (n = 0; n < N; n++) {
    int s = t[p];
    if (nx[q][s] < 0) { halted = 1; break; }
    t[p] = wr[q][s]; p += mv[q][s]; q = nx[q][s];
    if (p < 0 || p >= size) { fprintf(stderr, "Band zu kurz\n"); return 3; }
    if (p < lo) { lo = p; nL++; }
    if (p > hi) {
      hi = p; nR++;
      if (liste && q == 2) {
        /* Nullpositionen von hi rueckwaerts lesen: Abstaende zwischen Nullen,
           von rechts nach links, wie gaps.py mit inv */
        long long prev = -1, first = -1; int k = 0;
        printf("%lld C %lld lead", n + 1, hi - lo + 1);
        /* lead = Abstand vom rechten Ende bis zur ersten Null */
        for (long long i = hi; i >= lo; i--) if (t[i] == 0) { first = i; break; }
        printf(" %lld |", hi - first);
        prev = first;
        for (long long i = first - 1; i >= lo; i--) {
          if (t[i] == 0) {
            long long g = prev - i;
            if (g == 3) k++;
            else { if (g == 4) printf(" %d |", k); else printf(" %d <%lld>", k, g); k = 0; }
            prev = i;
          }
        }
        printf(" %d\n", k);
      }
    }
  }
  if (!liste)
    printf("%s halted=%d steps=%lld width=%lld left_records=%lld right_records=%lld state=%c\n",
           argv[1], halted, n + halted, hi - lo + 1, nL, nR, 'A' + q);
  return 0;
}
