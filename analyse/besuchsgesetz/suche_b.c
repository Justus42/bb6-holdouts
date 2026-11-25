/* Programm B (Thread "Familie Besuchsgesetz", 25.11.2026), unabhaengig von suche_a.py geschrieben.
   Anderes Verfahren:
   - Gesetz: B rechnet fuer jedes Wort w (bis Laenge L, x in {0,1}) die VORHERSAGE des Gesetzes rekursiv
     (P(0r)=1r, P(100r)=P(110r)=000P(r), P(1010r)=1010P(P(r)); nur die Bloecke 1011 und 111 werden simuliert)
     und vergleicht sie mit der direkten Simulation des ganzen Besuchs. (A prueft dagegen jede Regel einzeln.)
   - Rundenform: B simuliert die Maschine ab Leerband direkt (bis SCHRITTE Schritte), sammelt alle
     Konfigurationen "Zustand c, links daneben 0, links davon 0^inf u" und prueft ueber alle beobachteten
     Runden, dass das naechste Wort = p . V(altes Wort) ist (mind. 6 Runden). (A rechnet das Zwischenspiel
     symbolisch einmal durch.)
   Besuch: Zelle -2 = x, Zelle -1 = 0, Wort ab Zelle 0, Kopf auf 0 im Zustand c; Ende beim ersten Mal im
   Zustand a auf Zelle -2 (dann muss -1 = 0 und -2 = x sein, sonst "falsch_zurueck"); links von -2: "links".
   Aufruf: suche_b <holdouts.txt> [L]   FEHLER=1: falsche 1010-Regel (1010 P(r)); FEHLER=2: keine Spiegelung;
   FEHLER=3: Praefix p muss "11" sein (Rundenform darf dann nie gefunden werden) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 65536
#define MAXW 4096
static int Wr[6][2], Mv[6][2], Nx[6][2], Hl[6][2];
static int fehler = 0;
static long grenze = 200000;

enum { WORT = 0, HALT, LINKS, GRENZE, FALSCH, UNDEF };
static const char *sname[] = {"wort", "halt", "links", "grenze", "falsch_zurueck", "undef"};
typedef struct { int st; int n; char *w; } Erg;  /* w: '0'/'1', ohne End-Nullen */

static void kuerze(char *w, int *n) { while (*n > 0 && w[*n - 1] == '0') (*n)--; w[*n] = 0; }

static unsigned char band[N];
static Erg simul(const char *w, int wn, int x, int c, int a) {
  Erg e = {0, 0, NULL};
  memset(band, 0, N);
  int o = N / 4;
  band[o - 2] = x; band[o - 1] = 0;
  int hi = o - 1;
  for (int i = 0; i < wn; i++) { band[o + i] = w[i] - '0'; if (band[o + i]) hi = o + i; }
  int p = o, q = c;
  for (long s = 0; s < grenze; s++) {
    if (q == a && p == o - 2) {
      if (band[o - 1] != 0 || band[o - 2] != x) { e.st = FALSCH; return e; }
      int n = 0; for (int i = o; i <= hi; i++) if (band[i]) n = i - o + 1;
      e.w = malloc(n + 1); for (int i = 0; i < n; i++) e.w[i] = '0' + band[o + i]; e.w[n] = 0; e.n = n; e.st = WORT; return e;
    }
    if (p < o - 2) { e.st = LINKS; return e; }
    int b = band[p];
    if (Hl[q][b]) { e.st = HALT; return e; }
    band[p] = Wr[q][b]; if (Wr[q][b] && p > hi) hi = p;
    p += Mv[q][b]; q = Nx[q][b];
    if (p < 4 || p > N - 4) { e.st = GRENZE; return e; }
  }
  e.st = GRENZE; return e;
}

static int gc, ga, gx;
static Erg mache(const char *pre, Erg r) { /* pre . r */
  Erg e = {WORT, 0, NULL}; int k = strlen(pre);
  e.w = malloc(k + r.n + 1); memcpy(e.w, pre, k); memcpy(e.w + k, r.w, r.n); e.n = k + r.n; e.w[e.n] = 0; kuerze(e.w, &e.n);
  return e;
}
static Erg vorhersage(const char *w, int n) {
  Erg e = {WORT, 0, NULL};
  if (n == 0 || w[0] == '0') { e.w = malloc(n + 2); e.w[0] = '1'; memcpy(e.w + 1, w + (n ? 1 : 0), n ? n - 1 : 0); e.n = n ? n : 1; e.w[e.n] = 0; kuerze(e.w, &e.n); return e; }
  /* w[0] == '1' */
  char b1 = n > 1 ? w[1] : '0', b2 = n > 2 ? w[2] : '0', b3 = n > 3 ? w[3] : '0';
  if (b2 == '0' && (b1 == '0' || b1 == '1') && !(b1 == '0' && b2 == '1')) {
    /* 100 oder 110 */
    int r = n > 3 ? n - 3 : 0; Erg i = vorhersage(w + (n > 3 ? 3 : n), r);
    if (i.st != WORT) { free(i.w); i.w = NULL; return i; }
    Erg z = mache("000", i); free(i.w); return z;
  }
  if (b1 == '0' && b2 == '1' && b3 == '0') {
    int r = n > 4 ? n - 4 : 0; Erg i = vorhersage(w + (n > 4 ? 4 : n), r);
    if (i.st != WORT) return i;
    Erg j;
    if (fehler == 1) j = i; else { j = vorhersage(i.w, i.n); free(i.w); }
    if (j.st != WORT) return j;
    Erg z = mache("1010", j); free(j.w); return z;
  }
  /* 1011 oder 111: simulieren */
  Erg s = simul(w, n, gx, gc, ga);
  if (s.st == WORT || s.st == HALT) return s;
  s.st = UNDEF; return s;
}

static void lies(const char *s, int spiegel) {
  for (int q = 0; q < 6; q++) for (int b = 0; b < 2; b++) {
    const char *t = s + 7 * q + 3 * b;
    Hl[q][b] = (t[2] < 'A' || t[2] > 'F' || t[0] == '-');
    if (!Hl[q][b]) { Wr[q][b] = t[0] - '0'; Mv[q][b] = (t[1] == 'R') ? 1 : -1; if (spiegel) Mv[q][b] = -Mv[q][b]; Nx[q][b] = t[2] - 'A'; }
  }
}

static void wortaus(char *buf, long v, int n) { for (int i = 0; i < n; i++) buf[i] = ((v >> (n - 1 - i)) & 1) + '0'; buf[n] = 0; }

/* Gesetz pruefen; zaehlt Vergleiche */
static int gesetz(int L, long *verglichen) {
  char w[64];
  *verglichen = 0;
  for (int x = 0; x < 2; x++) for (int n = 0; n <= L; n++) for (long v = 0; v < (1L << n); v++) {
    wortaus(w, v, n);
    gx = x;
    Erg p = vorhersage(w, n);
    if (p.st == UNDEF) { free(p.w); continue; }
    Erg s = simul(w, n, x, gc, ga);
    int gleich = (p.st == s.st) && (p.st != WORT || (p.n == s.n && memcmp(p.w, s.w, p.n) == 0));
    free(p.w); free(s.w);
    if (!gleich) return 0;
    (*verglichen)++;
  }
  return 1;
}

/* Verhalten von V(block r), alle r bis Laenge L-|block|, x in {0,1}; Ausgabe wie Programm A */
static void sonder(const char *block, int L, char *aus) {
  char kat[64][48]; int zahl[64]; int nk = 0; int k = strlen(block);
  char w[64];
  for (int x = 0; x < 2; x++) for (int n = 0; n <= L - k; n++) for (long v = 0; v < (1L << n); v++) {
    char r[32]; wortaus(r, v, n);
    strcpy(w, block); strcat(w, r);
    Erg s = simul(w, k + n, x, gc, ga);
    char name[48];
    if (s.st == WORT) {
      char q[8]; for (int i = 0; i < k; i++) q[i] = i < s.n ? s.w[i] : '0'; q[k] = 0;
      /* Rest ab Stelle k gleich r (ohne End-Nullen)? */
      int rn = n; char rr[32]; strcpy(rr, r); kuerze(rr, &rn);
      int sn = s.n > k ? s.n - k : 0;
      if (sn == rn && memcmp(s.w + k, rr, rn) == 0) snprintf(name, sizeof name, "wort:%sx", q);
      else snprintf(name, sizeof name, "wort:sonst");
    } else snprintf(name, sizeof name, "%s", sname[s.st]);
    free(s.w);
    int j; for (j = 0; j < nk; j++) if (!strcmp(kat[j], name)) break;
    if (j == nk) { strcpy(kat[nk], name); zahl[nk] = 0; nk++; }
    zahl[j]++;
  }
  if (nk == 1) {
    if (!strncmp(kat[0], "wort:", 5)) sprintf(aus, "= %s", kat[0] + 5); else strcpy(aus, kat[0]);
    return;
  }
  /* sortieren nach Name */
  for (int i = 0; i < nk; i++) for (int j = i + 1; j < nk; j++) if (strcmp(kat[i], kat[j]) > 0) {
    char t[48]; strcpy(t, kat[i]); strcpy(kat[i], kat[j]); strcpy(kat[j], t); int z = zahl[i]; zahl[i] = zahl[j]; zahl[j] = z; }
  strcpy(aus, "uneinheitlich(");
  for (int i = 0; i < nk; i++) { char t[128]; snprintf(t, sizeof t, "%s%s:%d", i ? "," : "", kat[i], zahl[i]); strcat(aus, t); }
  strcat(aus, ")");
}

/* Rundenform empirisch: direkte Simulation ab Leerband. Kandidaten fuer u: die Linkskontexte der ersten
   6 Konfigurationen "Zustand c, links daneben 0" (u nicht leer). Fuer jeden Kandidaten wird erneut ab Leerband
   simuliert; ein Rundenbeginn ist eine solche Konfiguration mit Linkskontext genau 0^inf u, ausserhalb eines
   laufenden Rundenbesuchs (der Rundenbesuch an P endet beim ersten Mal im Zustand a auf P-2). */
#define MAXK 4000
static unsigned char vb[1 << 22];
typedef struct { int P; char u[8]; char *w; int wn; } Kfg;
static Kfg kf[MAXK];
static int linkskontext(int lo, int p, char *u) {
  int i = lo; while (i <= p - 2 && vb[i] == 0) i++;
  int un = p - 1 - i; if (un < 1 || un > 6) return 0;
  for (int j = 0; j < un; j++) u[j] = '0' + vb[i + j]; u[un] = 0; return 1;
}
static int sammle(const char *ziel, long schritte, char kand[][8], int *nkand) {
  int M = 1 << 22; memset(vb, 0, M);
  int o = M / 2, p = o, q = 0, lo = o, hi = o, nk = 0, drin = 0, Pd = 0;
  for (long s = 0; s < schritte && nk < MAXK; s++) {
    if (drin && p == Pd - 2 && q == ga) drin = 0;
    if (!drin && q == gc && vb[p - 1] == 0) {
      char u[8];
      if (linkskontext(lo, p, u)) {
        if (!ziel) { if (*nkand < 6) strcpy(kand[(*nkand)++], u); else return 0; }
        else if (!strcmp(u, ziel)) {
          Kfg *k = &kf[nk++]; k->P = p; strcpy(k->u, u);
          int e = p - 1; for (int j = p; j <= hi; j++) if (vb[j]) e = j;
          k->wn = e - p + 1; k->w = malloc(k->wn + 1); for (int j = 0; j < k->wn; j++) k->w[j] = '0' + vb[p + j]; k->w[k->wn] = 0;
          drin = 1; Pd = p;
        }
      }
    }
    int b = vb[p];
    if (Hl[q][b]) break;
    vb[p] = Wr[q][b]; p += Mv[q][b]; q = Nx[q][b];
    if (p < lo) lo = p;
    if (p > hi) hi = p;
    if (p < 8 || p > M - 8) break;
  }
  return nk;
}
static int runden(char *aus, long schritte) {
  char kand[6][8]; int nkand = 0, ok = 0;
  sammle(NULL, schritte, kand, &nkand);
  for (int c = 0; c < nkand && !ok; c++) {
    int doppelt = 0; for (int j = 0; j < c; j++) if (!strcmp(kand[j], kand[c])) doppelt = 1;
    if (doppelt) continue;
    int m = sammle(kand[c], schritte, NULL, NULL);
    int x = kand[c][strlen(kand[c]) - 1] - '0';
    char pre[8] = ""; int plen = -1, gut = m >= 7, paare = 0;
    for (int t = 0; t + 1 < m && gut; t++) {
      Kfg *A = &kf[t], *B = &kf[t + 1];
      Erg y = simul(A->w, A->wn, x, gc, ga);
      if (y.st == GRENZE) { free(y.w); break; }   /* Besuch zu lang fuer die Grenze: Datenende */
      if (y.st != WORT) { gut = 0; free(y.w); break; }
      int found = 0;
      for (int L = 0; L <= 4 && !found; L++) {
        if (plen >= 0 && L != plen) continue;
        char cand[8]; for (int j = 0; j < L; j++) cand[j] = j < B->wn ? B->w[j] : '0'; cand[L] = 0;
        if (fehler == 3 && strcmp(cand, "11")) continue;
        if (plen >= 0 && strcmp(cand, pre)) continue;
        Erg z = mache(cand, y);
        if (z.n == B->wn && !memcmp(z.w, B->w, z.n)) { found = 1; if (plen < 0) { plen = L; strcpy(pre, cand); } }
        free(z.w);
      }
      free(y.w);
      if (!found) gut = 0; else paare++;
    }
    if (gut && paare >= 6) {
      ok = 1;
      sprintf(aus, "u=%s p=%s w0=%s", kand[c], plen ? pre : "-", kf[0].wn ? kf[0].w : "-");
      fprintf(stderr, "  %s: %d Runden geprueft\n", aus, paare);
    }
    for (int i = 0; i < m; i++) free(kf[i].w);
  }
  if (!ok) strcpy(aus, "keine");
  return ok;
}

int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "r"); int L = argc > 2 ? atoi(argv[2]) : 12;
  if (getenv("FEHLER")) fehler = atoi(getenv("FEHLER"));
  char s[128]; int n = 0;
  while (fgets(s, sizeof s, f)) {
    if (strlen(s) < 41) continue; s[41] = 0; n++;
    for (int sp = 0; sp < (fehler == 2 ? 1 : 2); sp++) {
      lies(s, sp);
      for (gc = 0; gc < 6; gc++) for (ga = 0; ga < 6; ga++) {
        long vg;
        if (!gesetz(L, &vg)) continue;
        char k[512], h[512], r[128];
        sonder("1011", L, k); sonder("111", L, h);
        runden(r, 1000000);
        printf("%d\t%s\t%s\t%c\t%c\t%ld\t1011:%s\t111:%s\t%s\n", n, s, sp ? "gespiegelt" : "normal", 'A' + gc, 'A' + ga, vg, k, h, r);
        fflush(stdout);
      }
    }
  }
  return 0;
}
