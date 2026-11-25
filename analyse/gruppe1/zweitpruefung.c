/* Zweitprogramm (unabhaengig von den Python-Skripten): direkte Simulation
   ab Leerband, Start A.  Aufruf:
     zweitpruefung <maschine> <schritte> [- start]  -> Zusammenfassung
     zweitpruefung <maschine> <schritte> liste [start] -> statt dessen bei jedem
        Rechts-Rekord in Zustand C die Liste der Nullabstaende, von rechts gelesen
        (3er-Abstaende gezaehlt, | = Abstand 4, <g> = anderer Abstand);
        start = Startzustand (Standard A)
   Zusammenfassung zaehlt auch A-Besuche und Pruefpunkte (B oder D liest 0, rechts davon 11).
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
  long long N = atoll(argv[2]); int liste = argc > 3 && strcmp(argv[3], "liste") == 0;
  long long size = N / 2 + 1000; if (size > 50000000LL) size = 50000000LL; /* Breite waechst etwa wie Wurzel der Schritte */
  unsigned char *t = calloc(size, 1);
  long long p = size / 2, lo = p, hi = p, nL = 0, nR = 0, n;
  int q = (argc > 4) ? argv[4][0] - 'A' : 0, halted = 0;
  long long a_vis = 0, a_one = 0, tests = 0, test_bad = 0, t_turn = 0, t_ctx100 = 0;
  long long turn_pos = -1; int turn_c0 = 0, lastdir = 1; int turn_ctx[3] = {0, 0, 0};
  for (n = 0; n < N; n++) {
    int s = t[p];
    if (q == 0) { a_vis++; if (s == 1) a_one++; }
    if ((q == 1 || q == 3) && s == 0 && t[p + 1] == 1 && t[p + 2] == 1) {
      tests++; if (t[p + 3] == 1) test_bad++;
      /* letzte Wende rechts->links: bei p+1 durch C0? Band dahinter damals 1 0 0? */
      if (turn_c0 && turn_pos == p + 1) { t_turn++; if (turn_ctx[0] == 1 && turn_ctx[1] == 0 && turn_ctx[2] == 0) t_ctx100++; }
    }
    if (nx[q][s] >= 0) {
      int d = mv[q][s];
      if (lastdir == 1 && d == -1) { turn_pos = p; turn_c0 = (q == 2 && s == 0); turn_ctx[0] = t[p + 1]; turn_ctx[1] = t[p + 2]; turn_ctx[2] = t[p + 3]; }
      lastdir = d;
    }
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
    printf("%s halted=%d steps=%lld width=%lld left_records=%lld right_records=%lld state=%c "
           "A_besuche=%lld A_liest_1=%lld pruefpunkte=%lld pruefpunkt_mit_111=%lld nach_C0_Wende_bei_i+1=%lld davon_Kontext_100=%lld\n",
           argv[1], halted, n + halted, hi - lo + 1, nL, nR, 'A' + q, a_vis, a_one, tests, test_bad, t_turn, t_ctx100);
  return 0;
}
