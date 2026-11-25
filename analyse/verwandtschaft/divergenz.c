/* divergenz: laeuft zwei Maschinen ab Leerband nebeneinander und meldet den ersten Schritt, in dem
 * sie verschieden schreiben oder laufen (oder eine haelt). Zusaetzlich: welche Zustandspaare (p,q)
 * mit gelesenem Symbol tatsaechlich vorkamen.
 * Aufruf: divergenz <tm1> <tm2> <N> [spiegel 0/1] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { int ok, w, d, t; } Tr;
static void parse(const char *s, Tr T[6][2]) {
  int q = 0, c = 0;
  for (const char *p = s; *p;) { if (*p == '_') { p++; q++; c = 0; continue; }
    Tr *x = &T[q][c]; if (p[2] == '-') x->ok = 0; else { x->ok = 1; x->w = p[0]-'0'; x->d = p[1]=='R'?1:-1; x->t = p[2]-'A'; }
    p += 3; c++; }
}
int main(int argc, char **argv) {
  Tr a[6][2], b[6][2]; parse(argv[1], a); parse(argv[2], b);
  long N = atol(argv[3]); int m = argc > 4 ? atoi(argv[4]) : 0;
  long L = 400000000L; unsigned char *t = calloc(L, 1); long h = L / 2; int p = 0, q = 0;
  static long seen[6][6][2];
  long lo = h, hi = h;
  for (long s = 0; s < N; s++) {
    int sym = t[h]; seen[p][q][sym]++;
    Tr *x = &a[p][sym], *y = &b[q][sym];
    if (!x->ok || !y->ok) { printf("Halt bei Schritt %ld (1:%s 2:%s) Paar %c%c liest %d\n", s, x->ok?"weiter":"haelt", y->ok?"weiter":"haelt", 'A'+p,'A'+q,sym); goto ende; }
    if (x->w != y->w || x->d != (m ? -y->d : y->d)) { printf("verschieden bei Schritt %ld, Paar %c%c liest %d\n", s, 'A'+p, 'A'+q, sym); goto ende; }
    t[h] = x->w; h += x->d; p = x->t; q = y->t;
    if (h < lo) lo = h; if (h > hi) hi = h;
    if (h <= 0 || h >= L - 1) { printf("Band zu klein bei Schritt %ld\n", s); goto ende; }
  }
  printf("gleich bis %ld Schritte, Breite %ld\n", N, hi - lo + 1);
ende:
  printf("vorgekommene Paare:");
  for (int i = 0; i < 6; i++) for (int j = 0; j < 6; j++) for (int s = 0; s < 2; s++) if (seen[i][j][s]) printf(" %c%c/%d", 'A'+i, 'A'+j, s);
  printf("\n");
  return 0;
}
