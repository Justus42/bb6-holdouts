/* Programm B der Verwandtschaftskarte (C), unabhaengig von karte_a.py geschrieben.
 *
 * Andere Verfahren als A:
 *   T  paarweise: Zuordnung per Breitensuche ab (A_j -> X), dann ganze Tabelle vergleichen
 *      (A: kanonische Formen ueber alle Umbenennungen).
 *   Q  alle 203 Zerlegungen der 6 Zustaende durchprobieren; je Zustandspaar die feinste gueltige
 *      Zerlegung (A: Union-Find-Abschluss je Paar).
 *   K  Quotienten paarweise per Durchprobieren aller Umbenennungen vergleichen (A: kanonische Form).
 *   V/W Verschmelzen: rollender Hash ueber das Band + exakte Nachpruefung (A: exakte Bandkopien).
 *   G  Produktautomat, eigener Code; zusaetzlich Simulations-Vorsiebung (Zeilen S), die A nicht hat.
 *
 * Aufruf: karte_b <universum.tsv> [NSIM] [NSIEB] > ausgabe.tsv
 * Fehler-Schalter fuer Negativkontrollen: KARTE_B_FEHLER=spiegel|joker|produkt|hash
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXM 4000
#define NS 6

typedef struct { int ok; int w; int d; int t; } Tr; /* ok=0: Halt; d: +1 = R, -1 = L */
typedef struct { Tr tr[8][2]; int k; } Tab;

static char lab[MAXM][32];
static char str[MAXM][64];
static Tab tab[MAXM];
static int nm;
static const char *FE = "";
static long NSIM = 100000, NSIEB = 0;

static int parse(const char *s, Tab *t) {
  int q = 0, c = 0;
  t->k = NS;
  for (const char *p = s; *p; ) {
    if (*p == '_') { p++; q++; c = 0; continue; }
    Tr *x = &t->tr[q][c];
    if (p[2] == '-') { x->ok = 0; x->w = x->d = x->t = 0; }
    else { x->ok = 1; x->w = p[0] - '0'; x->d = (p[1] == 'R') ? 1 : -1; x->t = p[2] - 'A'; }
    p += 3; c++;
  }
  return q == NS - 1;
}

static int zaehlt(int i, int j) {
  char gi[32], gj[32];
  if (lab[i][0] != 'h' && lab[j][0] != 'h') return 0;
  for (int r = 0; r < 2; r++) {
    const char *L = r ? lab[j] : lab[i]; char *G = r ? gj : gi;
    if (L[0] == 'h' || L[0] == 'a') { int n = 0; const char *p = L + 1; while (*p && *p != '.') G[n++] = *p++; G[n] = 0; }
    else strcpy(G, L);
  }
  return strcmp(gi, gj) != 0;
}

/* ---------- T: j (Start A) == i ab X, Spiegelung m ---------- */
static int iso_start(const Tab *ti, const Tab *tj, int X, int m) {
  int psi[NS], inv[NS], que[NS], h = 0, e = 0;
  int mm = (m && strcmp(FE, "spiegel") != 0) ? -1 : 1;
  if (m && strcmp(FE, "spiegel") == 0) return 0;
  for (int q = 0; q < NS; q++) psi[q] = inv[q] = -1;
  psi[0] = X; inv[X] = 0; que[e++] = 0;
  while (h < e) {
    int q = que[h++];
    for (int s = 0; s < 2; s++) {
      const Tr *a = &tj->tr[q][s], *b = &ti->tr[psi[q]][s];
      if (a->ok != b->ok) return 0;
      if (!a->ok) continue;
      if (a->w != b->w || a->d * mm != b->d) return 0;
      if (psi[a->t] < 0) {
        if (inv[b->t] >= 0) return 0;
        psi[a->t] = b->t; inv[b->t] = a->t; que[e++] = a->t;
      } else if (psi[a->t] != b->t) return 0;
    }
  }
  if (e != NS) { fprintf(stderr, "WARNUNG: %s nicht ganz erreichbar\n", lab[0]); return 0; }
  return 1;
}

/* ---------- Simulation, Konfigurationen ---------- */
typedef struct { uint64_t h; int q; long t; } Ent;
#define MP 2305843009213693951ULL  /* 2^61-1 */
static uint64_t mulm(uint64_t a, uint64_t b) {
  __uint128_t r = (__uint128_t)a * b;
  uint64_t lo = (uint64_t)(r & MP), hi = (uint64_t)(r >> 61);
  uint64_t x = lo + hi; if (x >= MP) x -= MP; return x;
}
static uint64_t powm(uint64_t a, uint64_t e) { uint64_t r = 1; while (e) { if (e & 1) r = mulm(r, a); a = mulm(a, a); e >>= 1; } return r; }
static const uint64_t RB = 1000003ULL;

/* Lauf von Tabelle t ab Zustand s0, Leerband; schreibt je Schritt (Zustand, Hash relativ zum Kopf).
 * Rueckgabe: Zahl der Konfigurationen (t = 0..n oder bis Halt). */
static uint64_t *pw, *ipw; static long pwn;
static long lauf(const Tab *t, int s0, long n, uint64_t *hs, int *qs) {
  long L = 2 * n + 3, h = n + 1; unsigned char *tp = calloc(L, 1);
  uint64_t H = 0; int q = s0; long c = 0;
  for (long st = 0; st <= n; st++) {
    uint64_t key = mulm(H, ipw[h]);
    if (strcmp(FE, "hash") == 0) key = H; /* Fehler: nicht relativ zum Kopf */
    hs[c] = key; qs[c] = q; c++;
    const Tr *x = &t->tr[q][tp[h]];
    if (!x->ok) break;
    if (tp[h] != x->w) { uint64_t d = pw[h]; if (x->w) H = (H + d) % MP; else H = (H + MP - d) % MP; tp[h] = x->w; }
    h += x->d; q = x->t;
  }
  free(tp); return c;
}

/* exakte Konfiguration zur Zeit T (getrimmtes Band als Zeichenkette mit Kopfmarke) */
static char *konf(const Tab *t, int s0, long T, long n) {
  long L = 2 * n + 3, h = n + 1; unsigned char *tp = calloc(L, 1); int q = s0;
  for (long st = 0; st < T; st++) { const Tr *x = &t->tr[q][tp[h]]; if (!x->ok) break; tp[h] = x->w; h += x->d; q = x->t; }
  long a = 0, b = L - 1; while (a < L && tp[a] == 0) a++; while (b >= 0 && tp[b] == 0) b--;
  char *out = malloc(L + 64); int o = sprintf(out, "%c:%ld:", 'A' + q, a > b ? 0L : h - a);
  for (long p = a; p <= b; p++) out[o++] = '0' + tp[p];
  out[o] = 0; free(tp); return out;
}

static int hcmp(const void *x, const void *y) {
  const Ent *a = x, *b = y;
  if (a->h != b->h) return a->h < b->h ? -1 : 1;
  if (a->q != b->q) return a->q - b->q;
  return a->t < b->t ? -1 : (a->t > b->t);
}

/* erster t2 (Lauf ab s2), dessen Konfiguration im Lauf ab s1 vorkommt; t1 = groesster passender Zeitpunkt */
static int verschmelzen(const Tab *t, int s1, int s2, long n, long *r1, long *r2) {
  uint64_t *h1 = malloc((n + 1) * 8), *h2 = malloc((n + 1) * 8); int *q1 = malloc((n + 1) * 4), *q2 = malloc((n + 1) * 4);
  long c1 = lauf(t, s1, n, h1, q1), c2 = lauf(t, s2, n, h2, q2);
  Ent *E = malloc(c1 * sizeof(Ent));
  for (long i = 0; i < c1; i++) { E[i].h = h1[i]; E[i].q = q1[i]; E[i].t = i; }
  qsort(E, c1, sizeof(Ent), hcmp);
  int found = 0;
  for (long j = 0; j < c2 && !found; j++) {
    long lo = 0, hi = c1;
    while (lo < hi) { long md = (lo + hi) / 2; if (E[md].h < h2[j] || (E[md].h == h2[j] && E[md].q < q2[j])) lo = md + 1; else hi = md; }
    long best = -1;
    for (long k = lo; k < c1 && E[k].h == h2[j] && E[k].q == q2[j]; k++) {
      char *x = konf(t, s1, E[k].t, n), *y = konf(t, s2, j, n);
      if (strcmp(x, y) == 0 && E[k].t > best) best = E[k].t;
      free(x); free(y);
    }
    if (best >= 0) { *r1 = best; *r2 = j; found = 1; }
  }
  free(h1); free(h2); free(q1); free(q2); free(E);
  return found;
}

/* ---------- Q: Zerlegungen ---------- */
static int nparts; static int parts[300][NS];
static void gen(int *a, int pos, int mx) {
  if (pos == NS) { memcpy(parts[nparts++], a, sizeof(int) * NS); return; }
  for (int v = 0; v <= mx + 1; v++) { a[pos] = v; gen(a, pos + 1, v > mx ? v : mx); }
}
static int nblocks(const int *p) { int m = 0; for (int i = 0; i < NS; i++) if (p[i] > m) m = p[i]; return m + 1; }
static int gueltig(const Tab *t, const int *p) {
  for (int a = 0; a < NS; a++) for (int b = a + 1; b < NS; b++) {
    if (p[a] != p[b]) continue;
    for (int s = 0; s < 2; s++) {
      const Tr *x = &t->tr[a][s], *y = &t->tr[b][s];
      if (!x->ok || !y->ok) {
        if (strcmp(FE, "joker") == 0 && x->ok != y->ok) return 0;
        continue;
      }
      if (x->w != y->w || x->d != y->d || p[x->t] != p[y->t]) return 0;
    }
  }
  return 1;
}
static void quot(const Tab *t, const int *p, Tab *qt) {
  qt->k = nblocks(p);
  for (int b = 0; b < qt->k; b++) for (int s = 0; s < 2; s++) qt->tr[b][s].ok = 0;
  for (int q = 0; q < NS; q++) for (int s = 0; s < 2; s++) {
    const Tr *x = &t->tr[q][s];
    if (x->ok) { qt->tr[p[q]][s] = *x; qt->tr[p[q]][s].t = p[x->t]; }
  }
}

typedef struct { int m; int idx; int part[NS]; Tab q; } QE;
static QE qe[20000]; static int nqe;

/* alle Isomorphismen qj -> qi (Spiegelung m); setzt hit[m][X] fuer X = Bild von 0 */
static int perm_iso(const Tab *qi, const Tab *qj, int hit[2][8]) {
  int k = qi->k, any = 0; if (qj->k != k) return 0;
  int p[8]; for (int i = 0; i < k; i++) p[i] = i;
  /* Heap-Algorithmus ueber alle Permutationen */
  int c[8] = {0};
  for (int iter = 0;;) {
    for (int m = 0; m < 2; m++) {
      if (m && strcmp(FE, "spiegel") == 0) continue;
      int ok = 1;
      for (int q = 0; q < k && ok; q++) for (int s = 0; s < 2 && ok; s++) {
        const Tr *a = &qj->tr[q][s], *b = &qi->tr[p[q]][s];
        if (a->ok != b->ok) ok = 0;
        else if (a->ok && (a->w != b->w || (m ? -a->d : a->d) != b->d || p[a->t] != b->t)) ok = 0;
      }
      if (ok) { hit[m][p[0]] = 1; any = 1; }
    }
    /* naechste Permutation */
    int i = 1; while (i < k && c[i] >= i) { c[i] = 0; i++; }
    if (i >= k) break;
    if (i % 2 == 0) { int tmp = p[0]; p[0] = p[i]; p[i] = tmp; } else { int tmp = p[c[i]]; p[c[i]] = p[i]; p[i] = tmp; }
    c[i]++; iter++;
  }
  return any;
}

/* ---------- G: Produktautomat ---------- */
static int gleich(const Tab *a, const Tab *b, int m, int seen[NS][NS]) {
  int st[64][2], sp = 0; memset(seen, 0, sizeof(int) * NS * NS);
  seen[0][0] = 1; st[sp][0] = 0; st[sp][1] = 0; sp++;
  while (sp) {
    sp--; int p = st[sp][0], q = st[sp][1];
    for (int s = 0; s < 2; s++) {
      const Tr *x = &a->tr[p][s], *y = &b->tr[q][s];
      if (!x->ok || !y->ok) continue;
      int dy = m ? -y->d : y->d;
      if (strcmp(FE, "produkt") == 0) dy = x->d;
      if (x->w != y->w || x->d != dy) return 0;
      if (!seen[x->t][y->t]) { seen[x->t][y->t] = 1; st[sp][0] = x->t; st[sp][1] = y->t; sp++; }
    }
  }
  return 1;
}

int main(int argc, char **argv) {
  if (getenv("KARTE_B_FEHLER")) FE = getenv("KARTE_B_FEHLER");
  if (argc > 2) NSIM = atol(argv[2]);
  if (argc > 3) NSIEB = atol(argv[3]);
  FILE *f = fopen(argv[1], "r"); char line[256];
  while (fgets(line, sizeof line, f)) {
    if (sscanf(line, "%31s %63s", lab[nm], str[nm]) != 2) continue;
    if (!parse(str[nm], &tab[nm])) { fprintf(stderr, "Formatfehler %s\n", line); return 1; }
    nm++;
  }
  fclose(f);
  pwn = 2 * NSIM + 10; pw = malloc(pwn * 8); ipw = malloc(pwn * 8);
  uint64_t inv = powm(RB, MP - 2); pw[0] = ipw[0] = 1;
  for (long i = 1; i < pwn; i++) { pw[i] = mulm(pw[i - 1], RB); ipw[i] = mulm(ipw[i - 1], inv); }

  /* T + V */
  for (int i = 0; i < nm; i++) for (int j = i + 1; j < nm; j++) {
    if (!zaehlt(i, j)) continue;
    char w[128] = ""; int first = -1;
    for (int m = 0; m < 2; m++) for (int X = 0; X < NS; X++)
      if (iso_start(&tab[i], &tab[j], X, m)) {
        char b[8]; sprintf(b, "%s%d%c", w[0] ? "," : "", m, 'A' + X); strcat(w, b);
        if (first < 0) first = X;
      }
    if (first < 0) continue;
    printf("T\t%s\t%s\t%s\n", lab[i], lab[j], w);
    long r1, r2;
    if (verschmelzen(&tab[i], 0, first, NSIM, &r1, &r2)) printf("V\t%s\t%s\t%ld\t%ld\n", lab[i], lab[j], r1, r2);
    else printf("V\t%s\t%s\t-\n", lab[i], lab[j]);
  }

  /* Q */
  int a[NS]; gen(a, 0, -1);
  if (nparts != 203) { fprintf(stderr, "Zerlegungen: %d\n", nparts); return 1; }
  for (int i = 0; i < nm; i++) {
    int got[300] = {0};
    for (int P = 0; P < NS; P++) for (int Q = P + 1; Q < NS; Q++) {
      int best = -1, bk = 0, tie = 0;
      for (int z = 0; z < nparts; z++) {
        if (parts[z][P] != parts[z][Q] || !gueltig(&tab[i], parts[z])) continue;
        int k = nblocks(parts[z]);
        if (k > bk) { bk = k; best = z; tie = 0; } else if (k == bk) tie = 1;
      }
      if (best < 0) continue;
      if (tie) { fprintf(stderr, "FEHLER: feinste Zerlegung nicht eindeutig (%s)\n", lab[i]); return 1; }
      if (got[best]) continue;
      got[best] = 1;
      int *p = parts[best]; int k = nblocks(p); char bl[32]; int o = 0;
      for (int b = 0; b < k; b++) { if (b) bl[o++] = '|'; for (int q = 0; q < NS; q++) if (p[q] == b) bl[o++] = 'A' + q; }
      bl[o] = 0;
      int joker = 0;
      for (int q = 0; q < NS; q++) for (int s = 0; s < 2; s++) if (!tab[i].tr[q][s].ok) {
        for (int r = 0; r < NS; r++) if (r != q && p[r] == p[q]) joker = 1;
      }
      printf("Q\t%s\t%s\t%d\t%d\n", lab[i], bl, k, joker);
      QE *e = &qe[nqe++]; e->idx = i; memcpy(e->part, p, sizeof(int) * NS); quot(&tab[i], p, &e->q);
    }
  }
  /* K + W */
  for (int x = 0; x < nqe; x++) for (int y = x + 1; y < nqe; y++) {
    int i = qe[x].idx, j = qe[y].idx;
    if (!zaehlt(i, j)) continue;
    int hit[2][8] = {{0}};
    if (!perm_iso(&qe[x].q, &qe[y].q, hit)) continue;
    char w[128] = ""; int first = -1;
    for (int m = 0; m < 2; m++) for (int X = 0; X < qe[x].q.k; X++) if (hit[m][X]) {
      char b[8]; sprintf(b, "%s%d%c", w[0] ? "," : "", m, 'A' + X); strcat(w, b); if (first < 0) first = X; }
    printf("K\t%s\t%s\t%c\t%s\n", lab[i], lab[j], 'A' + qe[x].part[0], w);
    long r1, r2;
    if (verschmelzen(&qe[x].q, qe[x].part[0], first, NSIM, &r1, &r2)) printf("W\t%s\t%s\t%ld\t%ld\n", lab[i], lab[j], r1, r2);
    else printf("W\t%s\t%s\t-\n", lab[i], lab[j]);
  }

  /* G */
  for (int i = 0; i < nm; i++) for (int j = i + 1; j < nm; j++) {
    if (!zaehlt(i, j) || strcmp(str[i], str[j]) == 0) continue;
    for (int m = 0; m < 2; m++) {
      int seen[NS][NS];
      if (!gleich(&tab[i], &tab[j], m, seen)) continue;
      printf("G\t%s\t%s\t%d\t", lab[i], lab[j], m); int fst = 1;
      for (int p = 0; p < NS; p++) for (int q = 0; q < NS; q++) if (seen[p][q]) { printf(fst ? "%c%c" : " %c%c", 'A' + p, 'A' + q); fst = 0; }
      printf("\n");
    }
  }

  /* S: Simulations-Vorsiebung fuer Gleichschritt (nur B): gleiche Folge (Schreiben, Richtung) ueber NSIEB Schritte */
  if (NSIEB > 0) {
    uint64_t *fp = malloc(nm * 8 * 2); long *len = malloc(nm * sizeof(long));
    for (int i = 0; i < nm; i++) {
      long L = 2 * NSIEB + 3, h = NSIEB + 1; unsigned char *tp = calloc(L, 1); int q = 0; uint64_t F = 1469598103934665603ULL, G = F; long st;
      for (st = 0; st < NSIEB; st++) {
        const Tr *x = &tab[i].tr[q][tp[h]]; if (!x->ok) break;
        F = (F ^ (uint64_t)(x->w * 4 + (x->d + 1))) * 1099511628211ULL;
        G = (G ^ (uint64_t)(x->w * 4 + (-x->d + 1))) * 1099511628211ULL;
        tp[h] = x->w; h += x->d; q = x->t;
      }
      fp[2 * i] = F; fp[2 * i + 1] = G; len[i] = st; free(tp);
    }
    for (int i = 0; i < nm; i++) for (int j = i + 1; j < nm; j++) {
      if (!zaehlt(i, j) || strcmp(str[i], str[j]) == 0) continue;
      for (int m = 0; m < 2; m++)
        if (len[i] == NSIEB && len[j] == NSIEB && fp[2 * i] == fp[2 * j + m]) printf("S\t%s\t%s\t%d\n", lab[i], lab[j], m);
    }
  }
  return 0;
}
