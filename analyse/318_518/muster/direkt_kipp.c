/* direkt_kipp.c - direkte Simulation (Zelle fuer Zelle, ohne Spruenge) fuer die Negativkontrolle K8.
 * Laeuft eine TM ab Leerband; nach genau S Schritten werden die k Zellen Kopf+d, Kopf+d+8, ..., Kopf+d+8(k-1)
 * umgedreht (0<->1); dann weiter bis N Schritte. Ausgabe wie "m5sim paare": alle Paare aufeinanderfolgender Uebergaenge mit Anzahl, dazu je
 * Haltepaar B1->A1 und C1->E1 der Schritt des ersten Vorkommens nach dem Umdrehen.
 * Aufruf: direkt_kipp <tm> <start> <S> <d> <k> <N>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define W (1 << 26)
static unsigned char t[W];
int main(int argc, char **argv) {
  if (argc != 7) { fprintf(stderr, "Aufruf: direkt_kipp <tm> <start> <S> <d> <k> <N>\n"); return 2; }
  const char *s = argv[1]; int n = (int)((strlen(s) + 1) / 7), wr[8][2], mv[8][2], nx[8][2], h[8][2];
  for (int i = 0; i < n; i++) for (int b = 0; b < 2; b++) {
    const char *p = s + 7 * i + 3 * b; h[i][b] = p[0] == '-';
    if (h[i][b]) continue;
    wr[i][b] = p[0] - '0'; mv[i][b] = p[1] == 'R' ? 1 : -1; nx[i][b] = p[2] - 'A';
  }
  int st = argv[2][0] - 'A';
  long long S = (long long)strtod(argv[3], 0), d = atoll(argv[4]), k = atoll(argv[5]), N = (long long)strtod(argv[6], 0), i;
  static long long cnt[16][16]; long long erstB = -1, erstC = -1;
  long p = W / 2; int prev = -1;
  for (i = 0; i < N; i++) {
    if (i == S) for (long long j = 0; j < k; j++) t[p + d + 8 * j] ^= 1;
    int b = t[p], cur = 2 * st + b;
    if (h[st][b]) { printf("HALT nach %lld Schritten\n", i); break; }
    if (prev >= 0) {
      cnt[prev][cur]++;
      if (prev == 3 && cur == 1 && erstB < 0) erstB = i + 1;   /* B1 dann A1 */
      if (prev == 5 && cur == 9 && erstC < 0) erstC = i + 1;   /* C1 dann E1 */
    }
    t[p] = wr[st][b]; p += mv[st][b]; st = nx[st][b]; prev = cur;
    if (p <= 0 || p >= W - 1) { printf("Band zu klein\n"); return 3; }
  }
  printf("Schritte %lld\n", i);
  printf("erstes B1 A1 bei %lld, erstes C1 E1 bei %lld\n", erstB, erstC);
  for (int x = 0; x < 2 * n; x++) for (int y = 0; y < 2 * n; y++)
    if (cnt[x][y]) printf("%c%d %c%d %lld\n", 'A' + x / 2, x % 2, 'A' + y / 2, y % 2, cnt[x][y]);
  return 0;
}
