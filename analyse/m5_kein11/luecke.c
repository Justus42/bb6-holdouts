/* luecke.c - M5, Zusatz der Pruefstelle (26.11. spaet): "stehende Luecke" und Vorstufen von "A liest 0 vor 0001".
 * Nur Beobachtung. Laeuft auf M5 selbst (5 Zustaende A..E), Start A (= 318/518) oder C (= 322), oder auf einem Band.
 *
 * Gemessen wird:
 *  1. Muster vor dem Uebergang (Zustand, gelesenes Bit, Zellen rechts/links):
 *       T   A>0 | 0001        (wuerde "11" erzeugen)
 *       VB  B>1 | 00001       VE  E>0 | 00001     (ein Schritt vor T)
 *       P1  A>0 | 100001      P2  0 D>1 | 0001     P3  C>1 | 000001   (zwei Schritte vor T)
 *       R5  rechts beginnt mit 00001, je (Zustand, Bit) gezaehlt, mit erstem/letztem Schritt
 *  2. Luecken: "1 0^k 1" mit k >= 4, beide Einsen strikt rechts vom Kopf (rechts davon steht noch eine 1, also nicht
 *     das leere Bandende). Eine solche Luecke kann nur entstehen, wenn der Kopf nach links geht (nur dann kommt eine
 *     Zelle in den Bereich strikt rechts dazu; rechts vom Kopf wird nie geschrieben). Bei jedem Linksschritt wird
 *     geprueft, ob die verlassene Zelle eine 1 ist, auf die >= 4 Nullen und dann eine 1 folgen.
 *     Eine Episode endet, wenn der Kopf auf die linke 1 der Luecke kommt (dann ist sie nicht mehr strikt rechts).
 *     Ausgabe je Episode: EP <Beginn> <Ende|-1> <Dauer> <k> <Ankunftszustand> <Uebergaenge davor> <32 Zellen links der 1>
 *  Selbstkontrolle --voll M: alle M Schritte alle Luecken strikt rechts vom Kopf durch vollen Suchlauf zaehlen und mit
 *  der Zahl offener Episoden vergleichen.
 *
 * Aufruf: luecke <TM> <N> [--start Z] [--band W K] [--stoer S O V]... [--voll M] [--r5liste]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W (1L << 26)
static unsigned char b[W];
static int WR[8][2], MV[8][2], NX[8][2], DEF[8][2], nS;
static long lo, hi;

static void parse(const char *s) {
  int q = 0, i = 0;
  while (s[i]) {
    for (int a = 0; a < 2; a++) {
      const char *t = s + i + 3 * a;
      if (t[0] == '-' || t[2] == '-' || t[2] == 'H' || t[2] == 'Z') { DEF[q][a] = 0; continue; }
      DEF[q][a] = 1; WR[q][a] = t[0] - '0'; MV[q][a] = (t[1] == 'R') ? 1 : -1; NX[q][a] = t[2] - 'A';
    }
    q++; i += 6; if (s[i] == '_') i++;
  }
  nS = q;
}

/* Laenge der Luecke, die bei Zelle i (=1) beginnt: k >= 4 Nullen und dann eine 1 vor hi; sonst 0 */
static long luecke_bei(long i) {
  if (!b[i]) return 0;
  long j = i + 1;
  while (j <= hi && !b[j]) j++;
  if (j > hi) return 0;              /* nur Nullen bis zum Bandende */
  long k = j - i - 1;
  return k >= 4 ? k : 0;
}

static long zaehle_voll(long p) {
  long n = 0;
  for (long i = p + 1; i <= hi; i++) if (luecke_bei(i)) n++;
  return n;
}

#define MAXEP 4096
static long ep_pos[MAXEP], ep_k[MAXEP]; static long long ep_beginn[MAXEP]; static char ep_ctx[MAXEP][40], ep_ueb[MAXEP][8];
static int nep = 0;

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "Aufruf siehe Kopf\n"); return 2; }
  parse(argv[1]);
  long long N = atoll(argv[2]);
  int st = 0, r5liste = 0; long long voll = 0;
  long long stS[64]; long stO[64]; int stV[64]; int nst = 0;
  long p = W / 2; lo = hi = p;
  for (int i = 3; i < argc; i++) {
    if (!strcmp(argv[i], "--start")) st = argv[++i][0] - 'A';
    else if (!strcmp(argv[i], "--band")) {
      const char *w = argv[++i]; long k = atol(argv[++i]); long n = strlen(w);
      for (long j = 0; j < n; j++) b[p - k + j] = w[j] - '0';
      lo = p - k; hi = p - k + n - 1; if (lo > p) lo = p; if (hi < p) hi = p;
    } else if (!strcmp(argv[i], "--stoer")) { stS[nst] = atoll(argv[++i]); stO[nst] = atol(argv[++i]); stV[nst] = atoi(argv[++i]); nst++; }
    else if (!strcmp(argv[i], "--voll")) voll = atoll(argv[++i]);
    else if (!strcmp(argv[i], "--r5liste")) r5liste = 1;
    else { fprintf(stderr, "unbekannt: %s\n", argv[i]); return 2; }
  }
  long long cT = 0, cVB = 0, cVE = 0, cP1 = 0, cP2 = 0, cP3 = 0;
  long long r5[8][2] = {{0}}, r5erst[8][2], r5letzt[8][2];
  for (int q = 0; q < 8; q++) for (int a = 0; a < 2; a++) { r5erst[q][a] = -1; r5letzt[q][a] = -1; }
  long long epzahl = 0, maxoffen = 0, vollfehler = 0, ep_mehr = 0;
  int ist = 0, haelt = 0; long long i;
  int vorher[2] = {-1, -1}; /* die zwei letzten Uebergaenge als 2*z+bit */
  nep = 0;
  for (i = 0; i < N; i++) {
    while (ist < nst && stS[ist] == i) {
      long z = p + stO[ist]; b[z] = stV[ist];
      if (z < lo) lo = z; if (z > hi) hi = z;
      ist++;
    }
    int a = b[p];
    if (!DEF[st][a]) { haelt = 1; break; }
    /* 1. Muster vor dem Uebergang. Rechts: b[p+1..p+6] als Zeichenfolge */
    unsigned r = 0; for (int j = 1; j <= 6; j++) r = (r << 1) | b[p + j];   /* Bit 5 = p+1 ... Bit 0 = p+6 */
    if ((r >> 1) == 0x01 /* 00001 */) {
      r5[st][a]++; if (r5erst[st][a] < 0) r5erst[st][a] = i; r5letzt[st][a] = i;
      if (r5liste) printf("R5 %lld %c%d\n", i, 'A' + st, a);
      if (st == 1 && a == 1) cVB++;
      if (st == 4 && a == 0) cVE++;
    }
    if (st == 0 && a == 0 && (r >> 2) == 0x1 /* 0001 */) cT++;
    if (st == 0 && a == 0 && r == 0x21 /* 100001 */) cP1++;
    if (st == 3 && a == 1 && b[p - 1] == 0 && (r >> 2) == 0x1) cP2++;
    if (st == 2 && a == 1 && r == 0x01 /* 000001 */) cP3++;
    /* Uebergang */
    int nb = WR[st][a], d = MV[st][a], ns = NX[st][a];
    b[p] = nb;
    long alt = p;
    p += d;
    if (p < lo) lo = p; if (p > hi) hi = p;
    if (p < 64 || p > W - 64) { fprintf(stderr, "Band zu klein\n"); return 3; }
    vorher[0] = vorher[1]; vorher[1] = 2 * st + a;
    st = ns;
    if (d < 0) {
      long k = luecke_bei(alt);
      if (k) {
        if (nep >= MAXEP) { fprintf(stderr, "zu viele offene Episoden\n"); return 4; }
        ep_pos[nep] = alt; ep_k[nep] = k; ep_beginn[nep] = i + 1;
        for (int j = 0; j < 32; j++) ep_ctx[nep][j] = '0' + b[alt - 32 + j];
        ep_ctx[nep][32] = 0;
        snprintf(ep_ueb[nep], 8, "%c%d%c%d", vorher[0] >= 0 ? 'A' + vorher[0] / 2 : '-', vorher[0] >= 0 ? vorher[0] % 2 : 0,
                 'A' + vorher[1] / 2, vorher[1] % 2);
        nep++; epzahl++;
        if (nep > maxoffen) maxoffen = nep;
        if (nep > 1) ep_mehr++;
      }
    } else {
      for (int e = 0; e < nep; e++)
        if (ep_pos[e] == p) {
          printf("EP %lld %lld %lld %ld %c %s %s\n", ep_beginn[e], i + 1, i + 1 - ep_beginn[e], ep_k[e], 'A' + st, ep_ueb[e], ep_ctx[e]);
          ep_pos[e] = ep_pos[nep - 1]; ep_k[e] = ep_k[nep - 1]; ep_beginn[e] = ep_beginn[nep - 1];
          memcpy(ep_ctx[e], ep_ctx[nep - 1], 40); memcpy(ep_ueb[e], ep_ueb[nep - 1], 8);
          nep--; e--;
        }
    }
    if (voll && (i + 1) % voll == 0 && zaehle_voll(p) != nep) vollfehler++;
  }
  for (int e = 0; e < nep; e++)
    printf("EP %lld -1 %lld %ld - %s %s\n", ep_beginn[e], i - ep_beginn[e], ep_k[e], ep_ueb[e], ep_ctx[e]);
  printf("ERGEBNIS schritte=%lld halt=%d T=%lld VB=%lld VE=%lld P1=%lld P2=%lld P3=%lld episoden=%lld max_gleichzeitig=%lld "
         "mehrfach=%lld vollfehler=%lld\n", i, haelt, cT, cVB, cVE, cP1, cP2, cP3, epzahl, maxoffen, ep_mehr, vollfehler);
  for (int q = 0; q < nS; q++) for (int a = 0; a < 2; a++)
    if (r5[q][a]) printf("R5SUMME %c%d %lld erster=%lld letzter=%lld\n", 'A' + q, a, r5[q][a], r5erst[q][a], r5letzt[q][a]);
  return 0;
}
