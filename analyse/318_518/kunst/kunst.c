/* kunst.c - M5-Umbau an kuenstlichen Baendern messen (Idee 1 der Lueckenkarte, 26.11.2026).
 *
 * Maschine fest: M5 = 1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC (Zustaende A..E).
 * Haltemuster (wie Teil 3): Uebergang B1, direkt danach liest A eine 1  (= Halt von 318/322);
 *                           Uebergang C1, direkt danach liest E eine 1  (= Halt von 518/274).
 *
 * Aufrufe:
 *   kunst bis <start A..E> <N>
 *       Leerband, Start im Zustand <start>, genau N Schritte. Ausgabe:
 *       "STAND <N> <Zustand> <Kopf-lo> <hi-lo> <Band lo..hi-1>"  (lo/hi = besuchte Grenzen, hi exklusiv)
 *       und je Haltemuster "MUSTER BA|CE <Anzahl> <erster Schritt>".
 *   kunst umbau <zustand> <maxschritte> <K> <maxzyklen>
 *       Liest ein Band (0/1) von stdin; Kopf rechts daneben auf leerer Zelle, Zustand <zustand>.
 *       Gibt jeden Zyklusbeginn aus (Rechts-Rekord nach mindestens K Schritten ohne Rechts-Rekord,
 *       wie m5sim zyklen):  "Z <Schritt> <Zustand> <lo_rel> <Band lo..hi-1>"
 *       lo_rel = linkester besuchter Ort relativ zum ersten Zeichen der Eingabe (<= 0).
 *       Hoert nach <maxzyklen> Zyklusbeginnen oder <maxschritte> Schritten auf.
 *       Am Ende: "MUSTER BA <n> <erster>", "MUSTER CE <n> <erster>", "ENDE <Schritte> ZYKLEN|LIMIT".
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W (1<<24)
static unsigned char tape[W];
static char buf[W];
/* M5: [Zustand][Symbol] -> schreiben, Richtung (+1 rechts), neuer Zustand */
static const int WR[5][2] = {{1,0},{0,1},{1,1},{1,0},{0,0}};
static const int MV[5][2] = {{1,-1},{1,1},{1,1},{-1,-1},{1,-1}};
static const int NX[5][2] = {{1,3},{2,0},{3,4},{0,4},{0,2}};

static long long nBA = 0, nCE = 0, fBA = -1, fCE = -1;

int main(int argc, char **argv) {
  if (argc < 4) { fprintf(stderr, "Aufruf siehe Kopf\n"); return 2; }
  long p = W / 2, lo, hi;
  int st;
  memset(tape, 0, W);
  if (!strcmp(argv[1], "bis")) {
    st = argv[2][0] - 'A';
    long long N = atoll(argv[3]);
    lo = hi = p;  /* hi = rechteste besuchte Zelle + 1 */
    hi = p + 1;
    int prev = -1; /* vorheriger (Zustand,Symbol) als 2*z+s */
    for (long long i = 0; i < N; i++) {
      int s = tape[p];
      if (prev == 2*1+1 && st == 0 && s == 1) { nBA++; if (fBA < 0) fBA = i + 1; }
      if (prev == 2*2+1 && st == 4 && s == 1) { nCE++; if (fCE < 0) fCE = i + 1; }
      prev = 2*st + s;
      tape[p] = WR[st][s]; p += MV[st][s]; st = NX[st][s];
      if (p <= 0 || p >= W - 1) { printf("BAND_ZU_KLEIN\n"); return 3; }
      if (p < lo) lo = p;
      if (p + 1 > hi) hi = p + 1;
    }
    /* Band lo..hi-1 ohne die Kopfzelle, falls der Kopf rechts aussen auf leerer Zelle steht */
    long h = (p == hi - 1 && tape[p] == 0) ? p : hi;
    printf("STAND %lld %c %ld %ld ", N, 'A' + st, p - lo, h - lo);
    for (long q = lo; q < h; q++) putchar('0' + tape[q]);
    putchar('\n');
    printf("MUSTER BA %lld %lld\nMUSTER CE %lld %lld\n", nBA, fBA, nCE, fCE);
    return 0;
  }
  if (!strcmp(argv[1], "umbau")) {
    if (argc < 6) { fprintf(stderr, "Aufruf siehe Kopf\n"); return 2; }
    st = argv[2][0] - 'A';
    long long N = atoll(argv[3]), K = atoll(argv[4]), MZ = atoll(argv[5]), nz = 0, last = 0, i;
    if (!fgets(buf, sizeof buf, stdin)) return 2;
    long L = (long)strcspn(buf, "\r\n");
    long base = W / 4;
    for (long q = 0; q < L; q++) tape[base + q] = buf[q] - '0';
    lo = base; p = base + L; hi = p;   /* hi = rechteste besuchte Zelle */
    int prev = -1;
    for (i = 0; i < N; i++) {
      int s = tape[p];
      if (prev == 2*1+1 && st == 0 && s == 1) { nBA++; if (fBA < 0) fBA = i + 1; }
      if (prev == 2*2+1 && st == 4 && s == 1) { nCE++; if (fCE < 0) fCE = i + 1; }
      prev = 2*st + s;
      tape[p] = WR[st][s]; p += MV[st][s]; st = NX[st][s];
      if (p <= 0 || p >= W - 1) { printf("BAND_ZU_KLEIN\n"); return 3; }
      if (p < lo) lo = p;
      if (p > hi) {
        hi = p;
        if (i + 1 - last >= K) {
          printf("Z %lld %c %ld ", i + 1, 'A' + st, lo - base);
          for (long q = lo; q < hi; q++) putchar('0' + tape[q]);
          putchar('\n');
          if (++nz >= MZ) { i++; break; }
        }
        last = i + 1;
      }
    }
    printf("MUSTER BA %lld %lld\nMUSTER CE %lld %lld\n", nBA, fBA, nCE, fCE);
    printf("ENDE %lld %s\n", i, nz >= MZ ? "ZYKLEN" : "LIMIT");
    return 0;
  }
  fprintf(stderr, "unbekannter Modus\n");
  return 2;
}
