/* kein11.c - M5, neuer Ansatz (26.11.2026), Punkt 3 und 5: Eigenschaft "nie 11 strikt rechts vom Kopf"
 * bei jedem Schritt pruefen (Hauptprogramm, schnell, inkrementell).
 *
 * Eigenschaft I (Seite R): keine Stelle i > Kopf mit Band[i] = Band[i+1] = 1.
 *              (Seite L): keine Stelle i mit i+1 < Kopf und Band[i] = Band[i+1] = 1  (fuer 274, gespiegelt).
 * Gefuehrt wird P = Anzahl solcher Paare. Begruendung der Fortschreibung (Seite R):
 *   Schreiben auf Zelle h beruehrt nur die Paare i = h-1 und i = h; beide haben i <= h, zaehlen also nicht.
 *   Kopf h -> h+1: Paar i = h+1 faellt heraus:  P -= b[h+1] & b[h+2].
 *   Kopf h -> h-1: Paar i = h kommt hinzu:      P += b[h]   & b[h+1].
 * Seite L spiegelbildlich. Nach jeder Stoerung wird P vollstaendig neu gezaehlt. Mit --voll wird P zusaetzlich
 * alle <voll> Schritte vollstaendig neu gezaehlt und mit dem fortgeschriebenen Wert verglichen.
 *
 * Aufruf:
 *   kein11 <TM> <Seite R|L> <N> [Optionen]
 *     --start Z          Startzustand (Vorgabe A)
 *     --band W K         Startband W (0/1-Zeichen), Kopf auf Index K von W (Vorgabe: leeres Band)
 *     --stoer S O V      nach S Schritten Zelle (Kopf+O) := V setzen, P neu zaehlen (mehrfach erlaubt, aufsteigend)
 *     --umgebung Z a     bei jedem Schritt, in dem Zustand Z das Bit a liest: 16 Zellen links vom Kopf,
 *                        Kopfzelle und 8 Zellen rechts zaehlen; Ausgabe der Haeufigkeiten am Ende (Zeilen "UMG")
 *     --voll M           alle M Schritte P vollstaendig nachzaehlen (Selbstkontrolle)
 *     --stop             beim ersten Bruch anhalten
 * Ausgabe: Zeilen "ERGEBNIS ..." (Schritte, Brueche, erster Bruch, Halt), "NACHBAR" (je Zustand/Bit: wie oft
 *          die Nachbarzelle auf der gepruefte Seite eine 1 war), "HASH" (FNV-1a ueber Zustand, Kopf relativ zu lo,
 *          besuchtes Band lo..hi) zum Vergleich mit dem zweiten Programm naiv.go.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define W (1L << 26)
static unsigned char b[W];
static int WR[8][2], MV[8][2], NX[8][2], DEF[8][2];
static int nS;
static long long umg[1 << 25];  /* Index: 16 Bits links | Kopfbit | 8 Bits rechts */

static void parse(const char *s) {
  int q = 0, i = 0;
  while (s[i]) {
    for (int a = 0; a < 2; a++) {
      const char *t = s + i + 3 * a;
      if (t[0] == '-' || t[2] == '-' || t[2] == 'H' || t[2] == 'Z') { DEF[q][a] = 0; continue; }
      DEF[q][a] = 1; WR[q][a] = t[0] - '0'; MV[q][a] = (t[1] == 'R') ? 1 : -1; NX[q][a] = t[2] - 'A';
    }
    q++; i += 6;
    if (s[i] == '_') i++;
  }
  nS = q;
}

static long lo, hi; /* besuchter Bereich [lo, hi] (einschliesslich), immer mit Rand 2 Nullen gelesen */

static long long zaehle(long p, char seite) {
  long long P = 0;
  for (long i = lo - 2; i <= hi + 1; i++) {
    if (!(b[i] & b[i + 1])) continue;
    if (seite == 'R' && i > p) P++;
    if (seite == 'L' && i + 1 < p) P++;
  }
  return P;
}

int main(int argc, char **argv) {
  if (argc < 4) { fprintf(stderr, "Aufruf siehe Kopf\n"); return 2; }
  parse(argv[1]);
  char seite = argv[2][0];
  long long N = atoll(argv[3]);
  int st = 0, umgZ = -1, umgA = -1, stop = 0;
  long long voll = 0;
  long long stS[64]; long stO[64]; int stV[64]; int nst = 0;
  long p = W / 2;
  lo = hi = p;
  for (int i = 4; i < argc; i++) {
    if (!strcmp(argv[i], "--start")) st = argv[++i][0] - 'A';
    else if (!strcmp(argv[i], "--band")) {
      const char *w = argv[++i]; long k = atol(argv[++i]);
      long n = strlen(w);
      for (long j = 0; j < n; j++) b[p - k + j] = w[j] - '0';
      lo = p - k; hi = p - k + n - 1;
      if (lo > p) lo = p; if (hi < p) hi = p;
    } else if (!strcmp(argv[i], "--stoer")) {
      stS[nst] = atoll(argv[++i]); stO[nst] = atol(argv[++i]); stV[nst] = atoi(argv[++i]); nst++;
    } else if (!strcmp(argv[i], "--umgebung")) { umgZ = argv[++i][0] - 'A'; umgA = atoi(argv[++i]); }
    else if (!strcmp(argv[i], "--voll")) voll = atoll(argv[++i]);
    else if (!strcmp(argv[i], "--stop")) stop = 1;
    else { fprintf(stderr, "unbekannt: %s\n", argv[i]); return 2; }
  }
  long long P = zaehle(p, seite);
  long long brueche = 0, erster = -1, maxP = P, nachbar[8][2] = {{0}}, lesen[8][2] = {{0}};
  long long umgn = 0, vollfehler = 0;
  int haelt = 0; long long i = 0; int ist = 0;
  if (P > 0) { brueche++; erster = 0; }
  for (i = 0; i < N; i++) {
    while (ist < nst && stS[ist] == i) {
      long z = p + stO[ist]; b[z] = stV[ist];
      if (z < lo) lo = z; if (z > hi) hi = z;
      P = zaehle(p, seite);
      if (P > 0 && erster < 0) erster = i;
      ist++;
    }
    int a = b[p];
    if (!DEF[st][a]) { haelt = 1; break; }
    lesen[st][a]++;
    if (seite == 'R') nachbar[st][a] += b[p + 1]; else nachbar[st][a] += b[p - 1];
    if (st == umgZ && a == umgA) {
      unsigned idx = 0;
      for (int j = 16; j >= 1; j--) idx = (idx << 1) | b[p - j];
      idx = (idx << 1) | a;
      for (int j = 1; j <= 8; j++) idx = (idx << 1) | b[p + j];
      umg[idx]++; umgn++;
    }
    b[p] = WR[st][a];
    int d = MV[st][a];
    if (seite == 'R') {
      if (d > 0) P -= b[p + 1] & b[p + 2]; else P += b[p] & b[p + 1];
    } else {
      if (d > 0) P += b[p - 1] & b[p]; else P -= b[p - 2] & b[p - 1];
    }
    p += d; st = NX[st][a];
    if (p < lo) lo = p; if (p > hi) hi = p;
    if (p < 16 || p > W - 16) { fprintf(stderr, "Band zu klein\n"); return 3; }
    if (P > 0) { brueche++; if (erster < 0) erster = i + 1; if (P > maxP) maxP = P; if (stop) { i++; break; } }
    if (voll && (i + 1) % voll == 0) { if (zaehle(p, seite) != P) vollfehler++; }
  }
  long long schritte = i;
  /* Hash */
  uint64_t h = 1469598103934665603ULL;
#define MIX(x) do { h ^= (uint64_t)(x); h *= 1099511628211ULL; } while (0)
  MIX(st); MIX((uint64_t)(p - lo));
  for (long j = lo; j <= hi; j++) MIX(b[j]);
  printf("ERGEBNIS TM=%s seite=%c schritte=%lld halt=%d brueche=%lld erster_bruch=%lld maxP=%lld vollfehler=%lld breite=%ld\n",
         argv[1], seite, schritte, haelt, brueche, erster, maxP, vollfehler, hi - lo + 1);
  printf("HASH %016llx zustand=%c kopf_rel=%ld\n", (unsigned long long)h, 'A' + st, p - lo);
  for (int q = 0; q < nS; q++)
    for (int a = 0; a < 2; a++)
      if (DEF[q][a])
        printf("NACHBAR %c%d gelesen=%lld nachbar_1=%lld\n", 'A' + q, a, lesen[q][a], nachbar[q][a]);
  if (umgZ >= 0) {
    printf("UMG_SUMME %c%d %lld\n", 'A' + umgZ, umgA, umgn);
    for (long idx = 0; idx < (1L << 25); idx++)
      if (umg[idx]) {
        char s[32]; int k = 0;
        for (int j = 24; j >= 9; j--) s[k++] = '0' + ((idx >> j) & 1);
        s[k++] = '['; s[k++] = '0' + ((idx >> 8) & 1); s[k++] = ']';
        for (int j = 7; j >= 0; j--) s[k++] = '0' + ((idx >> j) & 1);
        s[k] = 0;
        printf("UMG %s %lld\n", s, umg[idx]);
      }
  }
  return 0;
}
