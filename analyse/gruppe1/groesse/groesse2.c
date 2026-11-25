/* Erhaltene Groesse fuer Gruppe 1: Programm 2 (C), getrennt von groesse.py geschrieben.
 *
 * Rechnet jede Automatenphase (N1, N2, N2s, UA, LE0, LE1, LG) selbst, mit eigener Regel-Umsetzung und
 * eigener Schrittformel, und berechnet an JEDEM Schnappschuss alle Kandidaten neu aus der ganzen Liste
 * (keine laufenden Summen). Ereignisse, die keine Automatenphase sind (VS, nicht anwendbar, Zyklus-
 * uebergang), liest es aus dem Protokoll von Programm 1 (<praefix>_proto.txt): Liste vorher wird mit der
 * eigenen Liste verglichen (muss gleich sein), Liste nachher und Schrittzahl werden uebernommen. Fuer VS
 * und Zyklusuebergaenge rechnet es die Liste nachher zusaetzlich selbst (VS-Regel, Zyklusfunktion mit
 * Randschritten, Fressen, J) und vergleicht. Kernmuster eigene Umsetzung.
 *
 * Ausgabe: je Klasse und Aenderungsvektor "Klasse | dS dm dz du dq dr dx dy dL | Anzahl" (unsortiert;
 * Vergleich nach LC_ALL=C sort). Kandidaten wie in groesse.py (siehe dort / Bericht).
 *
 * Aufruf: ./groesse2 <A|C|D> <Schritte> <proto> <ausgabe>
 * Negativkontrollen (Umgebung GROESSE2_FEHLER): "ua" (UA setzt (1,k+3) statt (1,k+2)) muss am naechsten
 * Protokollereignis als Listenabweichung scheitern; "kern" (Kernmuster ohne Trenner-Zeichen) muss andere
 * Klassen liefern; "l" (Bandlaenge ohne den Anteil 3r rechts vom Kopf) muss andere Vektoren liefern.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef long long ll;
#define CAP (1 << 22)
static const char *FEHLER = "";

/* ---------- Token-Listen: links nach rechts, Trenner '0' '1' oder '_' (kein Trenner) */
typedef struct { char *t; ll *n; int lo, hi; } Liste;   /* Elemente lo..hi-1 */

static void l_init(Liste *L) {
  L->t = malloc(CAP); L->n = malloc(sizeof(ll) * CAP); L->lo = L->hi = CAP / 2;
}
static int l_len(const Liste *L) { return L->hi - L->lo; }
#define T(L, i) ((L)->t[(L)->lo + (i)])
#define N(L, i) ((L)->n[(L)->lo + (i)])
static void l_copy(Liste *d, const Liste *s) {
  d->lo = CAP / 2; d->hi = d->lo + l_len(s);
  memcpy(d->t + d->lo, s->t + s->lo, l_len(s));
  memcpy(d->n + d->lo, s->n + s->lo, sizeof(ll) * l_len(s));
}
static void l_prepend(Liste *L, char t, ll n) { L->lo--; L->t[L->lo] = t; L->n[L->lo] = n; }
static void l_remove(Liste *L, int i) {   /* Element i entfernen (nur nahe am linken Ende benutzt) */
  for (int k = i; k > 0; k--) { T(L, k) = T(L, k - 1); N(L, k) = N(L, k - 1); }
  L->lo++;
}
static int l_eq(const Liste *a, const Liste *b) {
  if (l_len(a) != l_len(b)) return 0;
  for (int i = 0; i < l_len(a); i++) if (T(a, i) != T(b, i) || N(a, i) != N(b, i)) return 0;
  return 1;
}

/* Text "t:n t:n ... /rest" einlesen */
static char *l_parse(Liste *L, char *s, char *tail) {
  L->lo = L->hi = CAP / 2;
  while (*s == ' ') s++;
  while (*s && *s != '/') {
    char t = *s; s += 2;
    ll v = strtoll(s, &s, 10);
    L->t[L->hi] = t; L->n[L->hi] = v; L->hi++;
    while (*s == ' ') s++;
  }
  if (*s == '/') s++;
  int k = 0;
  while (*s == '0' || *s == '1') tail[k++] = *s++;
  tail[k] = 0;
  return s;
}

/* ---------- Kandidaten, aus der ganzen Liste */
typedef struct { ll v[9]; } Vek;   /* S m z u q r x y L */
static Vek kand(const Liste *L, const char *tail, ll r) {
  Vek k; memset(&k, 0, sizeof k);
  ll S = 0, sep = 0; int M = l_len(L);
  for (int i = 0; i < M; i++) {
    char t = T(L, i); ll n = N(L, i);
    S += n;
    if (t == '0') k.v[2]++;
    if (n & 1) k.v[3]++;
    if (!(t == '1' && (n & 1))) k.v[4]++;
    if (t != '_') sep++;
  }
  k.v[0] = S; k.v[1] = M; k.v[5] = r;
  k.v[6] = M >= 1 ? N(L, M - 1) : 0;
  k.v[7] = M >= 2 ? N(L, M - 2) : 0;
  k.v[8] = sep + 3 * S + (ll)strlen(tail) + (strcmp(FEHLER, "l") == 0 ? 0 : 3 * r) + 3;
  return k;
}

/* ---------- Zaehltabelle Klasse|Vektor -> Anzahl */
#define HT (1 << 18)
static char *hk[HT]; static ll hv[HT];
static void zaehle(const char *kl, Vek a, Vek b) {
  char key[512];
  int p = snprintf(key, sizeof key, "%s |", kl);
  for (int i = 0; i < 9; i++) p += snprintf(key + p, sizeof key - p, " %lld", b.v[i] - a.v[i]);
  unsigned h = 2166136261u;
  for (char *c = key; *c; c++) h = (h ^ (unsigned char)*c) * 16777619u;
  h &= HT - 1;
  while (hk[h] && strcmp(hk[h], key)) h = (h + 1) & (HT - 1);
  if (!hk[h]) hk[h] = strdup(key);
  hv[h]++;
}

/* ---------- Automat (eigene Umsetzung der Tabelle aus PR 9, Abschnitt 3) */
static int unregel_b(char t, ll n) { return !(t == '1' && (n & 1)); }   /* wie im Beschleuniger */

/* Eine Automatenphase. Rueckgabe Regelname oder NULL (nicht anwendbar / VS). *kosten = Schritte. */
static const char *phase(Liste *L, ll *kosten, int *ist_vs) {
  int M = l_len(L);
  *ist_vs = 0;
  if (M < 2) return NULL;
  int F = -1;
  for (int i = M - 2; i >= 0; i--) if (unregel_b(T(L, i), N(L, i))) { F = i; break; }
  ll Sr = 0;
  for (int i = F + 1; i < M; i++) Sr += N(L, i);
  ll mr = M - 1 - F;
  if (F < 0) {                       /* LG */
    *kosten = 12 * Sr - 2 * M + 11;
    l_prepend(L, '1', 1);
    return "LG";
  }
  char s = T(L, F); ll k = N(L, F);
  ll basis = 12 * Sr - 2 * mr + 12 * k;
  if (s == '0' && k % 2 == 0) { T(L, F) = '1'; N(L, F) = k + 1; *kosten = basis + 11; return "N1"; }
  if (F == 0) {
    if (s == '1' && k == 0) {        /* LE0: (1,0),(t,k1) -> (1,k1+2) */
      l_remove(L, 0); T(L, 0) = '1'; N(L, 0) += 2; *kosten = basis + 25; return "LE0";
    }
    return NULL;
  }
  if (F == 1 && T(L, 0) == '1' && N(L, 0) == 0 && s == '0' && (k & 1)) {   /* LE1 */
    l_remove(L, 0); T(L, 0) = '1'; N(L, 0) = k + 2; *kosten = basis + 17; return "LE1";
  }
  ll g = N(L, F - 1);
  if (g >= 1 && s == '0' && (k & 1)) { N(L, F - 1) = g - 1; T(L, F) = '0'; N(L, F) = k + 2; *kosten = basis + 15; return "N2s"; }
  if (g >= 1 && s == '1' && k % 2 == 0) { N(L, F - 1) = g - 1; T(L, F) = '0'; N(L, F) = k + 2; *kosten = basis + 21; return "N2"; }
  if (s == '0' && (k & 1) && T(L, F - 1) == '1' && N(L, F - 1) == 0 && F >= 2 && N(L, F - 2) >= 1) {
    N(L, F - 2)--; T(L, F - 1) = '0'; N(L, F - 1) = 0; T(L, F) = '1';
    N(L, F) = k + (strcmp(FEHLER, "ua") == 0 ? 3 : 2);
    *kosten = basis + 15; return "UA";
  }
  if (s == '1' && k % 2 == 0 && k >= 2 && T(L, F - 1) == '1' && N(L, F - 1) == 0) {
    ll m = k / 2 + 3;
    if (F - 1 - m >= 0) {
      int alle = 1;
      for (ll i = F - 2; i >= F - 1 - m; i--) if (!(T(L, i) == '1' && N(L, i) == 1)) { alle = 0; break; }
      if (alle) *ist_vs = 1;
    }
  }
  return NULL;
}

/* VS-Ergebnis (PR 9): (1,1)^(k/2+3),(1,0),(1,k),(t,p) -> (1,0),(0,2),(1,3)^((k-2)/2),(1,2),(0,p+4) */
static void vs_anwenden(const Liste *L, Liste *aus) {
  int M = l_len(L), F = -1;
  for (int i = M - 2; i >= 0; i--) if (unregel_b(T(L, i), N(L, i))) { F = i; break; }
  ll k = N(L, F), m = k / 2 + 3, p = N(L, F + 1);
  aus->lo = aus->hi = CAP / 2;
  for (int i = 0; i < F - 1 - m; i++) { aus->t[aus->hi] = T(L, i); aus->n[aus->hi++] = N(L, i); }
#define PUT(a, b) do { aus->t[aus->hi] = (a); aus->n[aus->hi++] = (b); } while (0)
  PUT('1', 0); PUT('0', 2);
  for (ll i = 0; i < (k - 2) / 2; i++) PUT('1', 3);
  PUT('1', 2); PUT('0', p + 4);
  for (int i = F + 2; i < M; i++) PUT(T(L, i), N(L, i));
}

/* Randschritt (PR 9 automat.step auf dem Praefix ohne die letzten `rechts`-1 Token; Grenze nur
 * unter den Token 0 .. M-rechts-1). Unregelmaessig hier: Trenner 0 oder n gerade. */
static const char *rand_schritt(Liste *L, int rechts) {
  int M = l_len(L), P = M - rechts + 1;   /* Praefix 0..P-1, Grenze in 0..P-2 */
  int F = -1;
  for (int i = P - 2; i >= 0; i--) if (T(L, i) == '0' || N(L, i) % 2 == 0) { F = i; break; }
  if (F < 0) { l_prepend(L, '1', 1); return "LG"; }
  char s = T(L, F); ll k = N(L, F);
  if (s == '0' && k % 2 == 0) { T(L, F) = '1'; N(L, F) = k + 1; return "N1"; }
  if (F == 0) {
    if (s == '1' && k == 0) { l_remove(L, 0); T(L, 0) = '1'; N(L, 0) += 2; return "LE"; }
    return NULL;
  }
  if (F == 1 && T(L, 0) == '1' && N(L, 0) == 0 && s == '0' && (k & 1)) {
    l_remove(L, 0); T(L, 0) = '1'; N(L, 0) = k + 2; return "LE";
  }
  ll g = N(L, F - 1);
  if (g >= 1 && s == '0' && (k & 1)) { N(L, F - 1)--; T(L, F) = '0'; N(L, F) = k + 2; return "N2s"; }
  if (g >= 1 && s == '1' && k % 2 == 0) { N(L, F - 1)--; T(L, F) = '0'; N(L, F) = k + 2; return "N2"; }
  if (s == '0' && (k & 1) && T(L, F - 1) == '1' && N(L, F - 1) == 0 && F >= 2 && N(L, F - 2) >= 1) {
    N(L, F - 2)--; T(L, F - 1) = '0'; N(L, F - 1) = 0; T(L, F) = '1'; N(L, F) = k + 2; return "UA";
  }
  if (s == '1' && k % 2 == 0 && k >= 2 && T(L, F - 1) == '1' && N(L, F - 1) == 0 && F - 1 - (k / 2 + 3) >= 0) {
    ll m = k / 2 + 3;   /* VS als Randschritt: Ergebnis wie vs_anwenden, Grenze hier F */
    for (ll i = F - 2; i >= F - 1 - m; i--) if (!(T(L, i) == '1' && N(L, i) == 1)) return NULL;
    static Liste neu; static int init = 0;
    if (!init) { l_init(&neu); init = 1; }
    int M = l_len(L);
    ll p = N(L, F + 1);
    neu.lo = neu.hi = CAP / 2;
    for (int i = 0; i < F - 1 - m; i++) { neu.t[neu.hi] = T(L, i); neu.n[neu.hi++] = N(L, i); }
    neu.t[neu.hi] = '1'; neu.n[neu.hi++] = 0;
    neu.t[neu.hi] = '0'; neu.n[neu.hi++] = 2;
    for (ll i = 0; i < (k - 2) / 2; i++) { neu.t[neu.hi] = '1'; neu.n[neu.hi++] = 3; }
    neu.t[neu.hi] = '1'; neu.n[neu.hi++] = 2;
    neu.t[neu.hi] = '0'; neu.n[neu.hi++] = p + 4;
    for (int i = F + 2; i < M; i++) { neu.t[neu.hi] = T(L, i); neu.n[neu.hi++] = N(L, i); }
    l_copy(L, &neu);
    return "VS";
  }
  return NULL;   /* Sonderfaelle im Randschritt: nicht erklaert */
}

/* ---------- Kernmuster (eigene Umsetzung der Definition im Bericht "linkes Ende") */
static void kernmuster(const Liste *X, const char *xt, int ueb, char *aus) {
  int M = l_len(X), Z = ueb ? (M >= 5 ? M - 4 : M) : M - 1;
  int g = -1;
  for (int i = Z - 1; i >= 0; i--) if (T(X, i) != '1' || N(X, i) % 2 == 0) { g = i; break; }
  if (g < 0) { sprintf(aus, "keine Grenze%s%s%s", *xt ? "<" : "", xt, *xt ? ">" : ""); return; }
  int a = g;
  while (a - 1 >= 0 && (T(X, a - 1) != '1' || N(X, a - 1) % 2 == 0)) a--;
  int p = 0;
  for (int i = a; i <= g; i++) {
    if (i > a) aus[p++] = ' ';
    char t = T(X, i);
    if (strcmp(FEHLER, "kern") != 0) { if (t == '0') aus[p++] = '.'; else if (t == '_') aus[p++] = '_'; }
    ll n = N(X, i);
    aus[p++] = n == 0 ? '0' : ((n & 1) ? 'o' : 'e');
  }
  aus[p] = 0;
  if (*xt) { strcat(aus, "<"); strcat(aus, xt); strcat(aus, ">"); }
}

/* ---------- Anlauf: direkt vom leeren Band bis zum ersten Schnappschuss */
static const char *TM = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC";
static void canon(const char *b, int len, Liste *L, char *tail) {
  L->lo = L->hi = CAP / 2;
  int i = 0, letzt = 0;
  while (i + 3 <= len) {
    if (b[i] == '0' && b[i + 1] == '1' && b[i + 2] == '1') {
      int j = i; ll c = 0;
      while (j + 3 <= len && b[j] == '0' && b[j + 1] == '1' && b[j + 2] == '1') { j += 3; c++; }
      if (i == letzt) { L->t[L->hi] = '_'; L->n[L->hi++] = c; }
      else {
        for (int k = letzt; k < i - 1; k++) { L->t[L->hi] = b[k]; L->n[L->hi++] = 0; }
        L->t[L->hi] = b[i - 1]; L->n[L->hi++] = c;
      }
      letzt = i = j;
    } else i++;
  }
  int k = 0;
  for (int q = letzt; q < len; q++) tail[k++] = b[q];
  tail[k] = 0;
}
static ll anlauf(int start, Liste *L, char *tail, ll *r) {
  enum { W = 4096 };
  char band[W]; memset(band, 0, W);
  int p = W / 2, lo = p, hi = p, q = start; ll n = 0;
  for (;;) {
    if (q == 2 && band[p] == 0 && band[p + 1] == 0 && n > 0) {
      int j = p + 2; ll rr = 0;
      while (j + 2 <= hi && band[j] == 1 && band[j + 1] == 0 && band[j + 2] == 0) { rr++; j += 3; }
      if (j == hi && band[j] == 1) {
        char b[W]; int k = 0;
        for (int i = lo; i < p; i++) b[k++] = '0' + band[i];
        canon(b, k, L, tail);
        *r = rr;
        return n;
      }
    }
    const char *e = TM + 7 * q + 3 * band[p];
    band[p] = e[0] - '0';
    p += e[1] == 'R' ? 1 : -1;
    q = e[2] - 'A';
    n++;
    if (p < lo) lo = p;
    if (p > hi) hi = p;
  }
}

/* ---------- Protokoll */
static char *zeile_buf; static size_t zeile_cap;
typedef struct { ll n, r, dn, r2; char art[64]; Liste vor, nach; char vt[64], nt[64]; int ende; } Ereignis;
static int lies_ereignis(FILE *f, Ereignis *e) {
  if (getline(&zeile_buf, &zeile_cap, f) < 0) return 0;
  if (strncmp(zeile_buf, "ENDE", 4) == 0) { e->ende = 1; e->n = strtoll(zeile_buf + 5, NULL, 10); return 1; }
  e->ende = 0;
  char *s = zeile_buf;
  e->n = strtoll(s, &s, 10); e->r = strtoll(s, &s, 10);
  while (*s == ' ') s++;
  int k = 0; while (*s != ' ') e->art[k++] = *s++; e->art[k] = 0;
  e->dn = strtoll(s, &s, 10); e->r2 = strtoll(s, &s, 10);
  s = strchr(s, '|') + 1;
  s = l_parse(&e->vor, s, e->vt);
  s = strchr(s, '|') + 1;
  l_parse(&e->nach, s, e->nt);
  return 1;
}

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "Aufruf: groesse2 <A|C|D> <Schritte> <proto> <aus>\n"); return 2; }
  if (getenv("GROESSE2_FEHLER")) FEHLER = getenv("GROESSE2_FEHLER");
  int start = argv[1][0] - 'A';
  ll NMAX = (ll)atof(argv[2]);
  FILE *pf = fopen(argv[3], "r");
  Liste L, H1, H2, H3; l_init(&L); l_init(&H1); l_init(&H2); l_init(&H3);
  Ereignis e; l_init(&e.vor); l_init(&e.nach);
  char tail[64]; ll r;
  ll n = anlauf(start, &L, tail, &r);
  /* START-Zeile pruefen */
  if (getline(&zeile_buf, &zeile_cap, pf) < 0) return 3;
  { char *s = zeile_buf + 6; ll n0 = strtoll(s, &s, 10), r0 = strtoll(s, &s, 10);
    char t0[64]; s = strchr(s, '|') + 1; l_parse(&H1, s, t0);
    if (n0 != n || r0 != r || !l_eq(&H1, &L) || strcmp(t0, tail)) { printf("FEHLER: Anlauf verschieden\n"); return 1; } }
  long fehler = 0, ereignisse = 0, auto_ph = 0, vs_eig = 0, ueb_eig = 0;
  int hat = lies_ereignis(pf, &e);
  char kl[512];
  while (n < NMAX) {
    Vek a = kand(&L, tail, r);
    if (hat && !e.ende && n == e.n) {
      ereignisse++;
      if (e.r != r || !l_eq(&e.vor, &L) || strcmp(e.vt, tail)) {
        printf("FEHLER: Liste vor Ereignis bei n=%lld verschieden\n", n); fehler++; break;
      }
      /* Programm 2 darf hier keine Automatenregel anwenden koennen */
      if (r >= 1 && tail[0] == 0) {
        l_copy(&H1, &L); ll ko; int vs;
        const char *w = phase(&H1, &ko, &vs);
        if (w) { printf("FEHLER: n=%lld Protokoll-Ereignis %s, Programm 2 findet Regel %s\n", n, e.art, w); fehler++; }
        if (vs != (strcmp(e.art, "VS") == 0)) { printf("FEHLER: n=%lld VS-Erkennung verschieden (%s)\n", n, e.art); fehler++; }
      }
      Vek b = kand(&e.nach, e.nt, e.r2);
      if (strcmp(e.art, "VS") == 0) {
        vs_anwenden(&L, &H1);
        if (!l_eq(&H1, &e.nach) || e.r2 != r - 1) { printf("FEHLER: n=%lld VS-Ergebnis verschieden\n", n); fehler++; }
        vs_eig++;
        zaehle("VS", a, b);
      } else if (r == 0) {
        /* Zyklusfunktion selbst */
        int ok = 0; const char *w1 = NULL, *w2 = NULL; Vek k1, k2, k3;
        if (tail[0] == 0) {
          l_copy(&H1, &L); w1 = rand_schritt(&H1, 1);
          if (w1) { l_copy(&H2, &H1); w2 = rand_schritt(&H2, 2); }
          if (w1 && w2 && l_len(&H2) >= 4) {
            int M = l_len(&H2);
            ll e3 = N(&H2, M - 3), bb = N(&H2, M - 2), aa = N(&H2, M - 1);
            if (T(&H2, M - 1) == '1' && e3 >= 1) {
              l_copy(&H3, &H2);
              N(&H3, M - 3) = e3 - 1; T(&H3, M - 2) = '0'; N(&H3, M - 2) = 0; N(&H3, M - 1) = aa + 4 * bb + 3;
              ll e4 = N(&H3, M - 4);
              if (e4 >= 1) {
                k1 = kand(&H1, "", 0); k2 = kand(&H2, "", 0); k3 = kand(&H3, "", 0);
                /* J */
                l_copy(&H1, &H3);   /* H1 wird zum Ergebnis */
                ll e3n = N(&H1, M - 3);
                N(&H1, M - 4) = e4 - 1;
                H1.hi -= 2;
                T(&H1, M - 3) = '1'; N(&H1, M - 3) = e3n + 2;
                ok = l_eq(&H1, &e.nach) && e.nt[0] == 0;
              }
            }
          }
        }
        if ((strcmp(e.art, "Ueb-ok") == 0) != ok) { printf("FEHLER: n=%lld Uebergang %s, Programm 2 ok=%d\n", n, e.art, ok); fehler++; }
        if (ok) {
          ueb_eig++;
          zaehle("Ueb gesamt", a, b);
          snprintf(kl, sizeof kl, "UebRueck:%s", w1); zaehle(kl, a, k1);
          snprintf(kl, sizeof kl, "UebFress:%s", w2); zaehle(kl, k1, k2);
          zaehle("Fressen", k2, k3);
          zaehle("J", k3, b);
        } else {
          char km[256]; kernmuster(&L, tail, 1, km);
          snprintf(kl, sizeof kl, "KernUeb:%s", km); zaehle(kl, a, b);
        }
      } else {
        char km[256]; kernmuster(&L, tail, 0, km);
        snprintf(kl, sizeof kl, "Kern:%s", km); zaehle(kl, a, b);
      }
      l_copy(&L, &e.nach); strcpy(tail, e.nt);
      n += e.dn; r = e.r2;
      hat = lies_ereignis(pf, &e);
      continue;
    }
    if (hat && !e.ende && n > e.n) { printf("FEHLER: Ereignis bei n=%lld uebersprungen (n=%lld)\n", e.n, n); fehler++; break; }
    if (r < 1 || tail[0]) { printf("FEHLER: n=%lld r=%lld ohne Protokoll-Ereignis\n", n, r); fehler++; break; }
    ll ko; int vs;
    const char *w = phase(&L, &ko, &vs);
    if (!w) { printf("FEHLER: n=%lld keine Regel, aber kein Ereignis im Protokoll\n", n); fehler++; break; }
    auto_ph++;
    Vek b = kand(&L, tail, r - 1);
    zaehle(w, a, b);
    n += ko; r -= 1;
  }
  if (hat && e.ende && e.n != n) { printf("FEHLER: Ende bei n=%lld, Protokoll %lld\n", n, e.n); fehler++; }
  FILE *af = fopen(argv[4], "w");
  for (int i = 0; i < HT; i++) if (hk[i]) fprintf(af, "%s | %lld\n", hk[i], hv[i]);
  fclose(af);
  printf("start=%c schritte=%lld automatenphasen=%ld ereignisse=%ld vs_selbst=%ld uebergaenge_selbst=%ld fehler=%ld\n",
         'A' + start, n, auto_ph, ereignisse, vs_eig, ueb_eig, fehler);
  return fehler ? 1 : 0;
}
