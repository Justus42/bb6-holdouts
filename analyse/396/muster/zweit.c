/* Zweite Auswertung (Thread "396 Wachstumsmuster", 26.11.2026), unabhaengig von auswertung.py geschrieben.
   Liest "A <runde> <hex>"-Zeilen (z. B. aus runde_b_anf.cpp mit ANF=1) und bestimmt fuer m = 8, 16, ..., 4*Hexlaenge
   die kleinste Periode der Folge der m-Zellen-Fenster auf der zweiten Haelfte der Runden, mit der Rand-Funktion
   (Knuth-Morris-Pratt): Periode = L - pi(L). Gemeldet nur, wenn sie <= L/2 ist (mindestens zwei volle Wiederholungen).
   Dazu die erste Runde, ab der die Folge mit dieser Periode periodisch ist.
   Aufruf: zweit <datei>   (Kontrollen an kuenstlichen Folgen: kontrollen.sh) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static char **wort; static long *rnd; static long n = 0, cap = 0; static int hl = 0;
static long *pi;
static int gleich(long a, long b, int h){ return memcmp(wort[a], wort[b], h) == 0; }
/* kleinste Periode der Folge wort[s..s+L) bezogen auf die ersten h Zeichen, 0 wenn keine <= L/2 */
static long periode(long s, long L, int h){
  pi[0] = 0;
  for (long i = 1; i < L; i++){
    long k = pi[i-1];
    while (k > 0 && !gleich(s+i, s+k, h)) k = pi[k-1];
    if (gleich(s+i, s+k, h)) k++;
    pi[i] = k;
  }
  long p = L - pi[L-1];
  return p <= L/2 ? p : 0;
}
static void auswerten(void){
  long s = 0; while (s < n && rnd[s] <= rnd[n-1] / 2) s++;
  long L = n - s;
  printf("zweit: Runden %ld..%ld, Haelfte ab %ld (%ld Runden)\n", rnd[0], rnd[n-1], rnd[s], L);
  pi = malloc(sizeof(long) * (size_t)L);
  for (int m = 8; m <= 4*hl; m += 8){
    int h = m / 4; long p = periode(s, L, h);
    if (!p){ printf("  m=%3d: keine Periode <= %ld\n", m, L/2); continue; }
    long i = n - 1 - p; while (i >= 0 && gleich(i, i+p, h)) i--;
    printf("  m=%3d: Periode %ld, periodisch ab Runde %ld\n", m, p, rnd[i+1]);
  }
}
static void neu(long r, const char *hx){
  if (n == cap){ cap = cap ? 2*cap : 1024; wort = realloc(wort, sizeof(char*)*(size_t)cap); rnd = realloc(rnd, sizeof(long)*(size_t)cap); }
  hl = (int)strlen(hx); wort[n] = strdup(hx); rnd[n] = r; n++;
}
int main(int argc, char **argv){
  FILE *f = fopen(argv[1], "r"); if (!f){ perror(argv[1]); return 1; }
  char *zeile = NULL; size_t zl = 0;
  while (getline(&zeile, &zl, f) > 0){
    if (zeile[0] != 'A' || zeile[1] != ' ') continue;
    long r; char hx[1024]; if (sscanf(zeile + 2, "%ld %1000s", &r, hx) == 2) neu(r, hx);
  }
  if (n < 4){ printf("zu wenige A-Zeilen\n"); return 1; }
  auswerten(); return 0;
}
