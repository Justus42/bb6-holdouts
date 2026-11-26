/* blocksim.c - Programm 1 fuer "M5-Haltemuster bis 8e14" (Analyse 318/518, Teil 3).
 *
 * Zaehlt in einem Lauf einer beliebigen Turingmaschine (2 Symbole, bis 8 Zustaende) ab Leerband
 * JEDES Paar aufeinanderfolgender Uebergaenge (Zustand,gelesen) -> (Zustand,gelesen), exakt bis zu
 * vorgegebenen Schrittzahlen. Fuer M5 heisst das:
 *   "B1 A1" = M5 fuehrt B1 aus und liest danach in A eine 1   = 318 (und 322) haelt
 *   "C1 E1" = M5 fuehrt C1 aus und liest danach in E eine 1   = 518 (und 274) haelt
 *
 * Bandmodell: Fenster aus Einzelzellen um den Kopf; links und rechts davon Stapel aus Bloecken zu
 * BS = 8 Zellen, lauflaengenkodiert (Block, Anzahl). Zieht der Kopf aus dem Fenster, wird ein Block
 * vom Stapel geholt; liegen mehr als 2*BS Zellen jenseits des Kopfes im Fenster, wird ein Block
 * abgelegt. Die Ablage haengt nur vom Fenster ab.
 *
 * Sprung (Beschleunigung), und warum er nichts ueberspringen kann:
 *   Moment E = "Kopf will links einen Block X holen". Festgehalten: Fensterinhalt, Kopfstelle, Zustand,
 *   letzter Uebergang (fuer die Paarzaehlung), Schritt, alle Paarzaehler.
 *   Ist der naechste Moment E' wieder "links holen" mit
 *     - gleichem Fensterinhalt, Kopfstelle, Zustand, letztem Uebergang,
 *     - gleichem Block X aus DEMSELBEN Lauf (Anzahl genau um 1 kleiner, links nichts abgelegt),
 *     - rechts nichts geholt und genau ein Block Y rechts abgelegt,
 *   dann ist der Lauf von E nach E' eine Funktion von (Fenster, Zustand, letzter Uebergang, X) allein,
 *   denn nichts anderes wurde gelesen. Ab E' liegen genau dieselben Eingaben vor, also wiederholt er sich
 *   Schritt fuer Schritt, solange links X kommt: gleiche Dauer dt, gleiche Paarzaehlungen d[], gleicher
 *   abgelegter Block Y. k Wiederholungen werden deshalb in einem Zug verbucht:
 *   Schritt += k*dt, Paare += k*d[], X-Anzahl -= k, rechts k mal Y. Die Paare INNERHALB jeder
 *   Wiederholung sind in d[] enthalten (einschliesslich des Paares ueber die Grenze zur vorigen
 *   Wiederholung, weil der letzte Uebergang zum festgehaltenen Zustand gehoert). Ein Haltemuster
 *   innerhalb eines Sprungs waere also in d[] und damit in der Summe sichtbar.
 *   Spiegelbildlich fuer "rechts holen".
 *   k wird so gewaehlt, dass der naechste Pruefpunkt nicht ueberschritten wird; der Rest laeuft
 *   in Einzelschritten. Ein Halteuebergang innerhalb der Wiederholung haette E' verhindert.
 *
 * Aufruf: blocksim <tm> <start> <pruefpunkt1> [<pruefpunkt2> ...] [-nosprung] [-fehler] [-anteil] [-kipp S d k]
 *   Ausgabe je Pruefpunkt: Schritt, Paare (alle, die vorkommen), Zahl der Spruenge und der darin
 *   verbuchten Schritte, Band (Laenge ohne Randnullen, CRC-32 der 0/1-Zeichen, Kopf relativ zur
 *   ersten 1, Zustand).
 *   -nosprung: ohne Beschleunigung (zum Abgleich).  -fehler: Negativkontrolle, verbucht in einem
 *   Sprung die Paare nur (k-1)-mal.  -anteil: zusaetzlich je Paar, wie viele davon in Spruengen
 *   verbucht wurden ("im Sprung ...", nur zur Anzeige).
 *   -kipp S d k: Negativkontrolle K8, nach genau S Schritten die k Zellen Kopf+d, Kopf+d+8, ... umdrehen
 *   (kuenstlich eingebautes Haltemuster); S wird zugleich Pruefpunkt.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define BS 8
#define FMAX 256

typedef struct { int n; int wr[8][2], mv[8][2], nx[8][2], h[8][2]; } TM;

static void lese(const char *s, TM *m) {
  size_t L = strlen(s);
  int n = (int)((L + 1) / 7);
  if ((size_t)(7 * n - 1) != L || n > 8) { fprintf(stderr, "Format?\n"); exit(2); }
  m->n = n;
  for (int i = 0; i < n; i++)
    for (int b = 0; b < 2; b++) {
      const char *p = s + 7 * i + 3 * b;
      if (p[0] == '-') { m->h[i][b] = 1; m->wr[i][b] = 1; m->mv[i][b] = 1; m->nx[i][b] = 0; continue; }
      m->h[i][b] = 0;
      m->wr[i][b] = p[0] - '0';
      m->mv[i][b] = (p[1] == 'R') ? 1 : -1;
      m->nx[i][b] = p[2] - 'A';
    }
}

/* Lauf: Block (Bits, Zelle 0 = Bit 0 = links) und Anzahl */
typedef struct { uint32_t b; int64_t c; } Lauf;
typedef struct { Lauf *a; long n, cap; } Stapel;

static void st_push(Stapel *s, uint32_t b, int64_t c) {
  if (s->n > 0 && s->a[s->n - 1].b == b) { s->a[s->n - 1].c += c; return; }
  if (s->n == s->cap) { s->cap = s->cap ? 2 * s->cap : 64; s->a = realloc(s->a, s->cap * sizeof(Lauf)); }
  s->a[s->n].b = b; s->a[s->n].c = c; s->n++;
}
/* oberster Block; leerer Stapel = Nullblock */
static uint32_t st_pop(Stapel *s) {
  if (s->n == 0) return 0;
  uint32_t b = s->a[s->n - 1].b;
  if (--s->a[s->n - 1].c == 0) s->n--;
  return b;
}

static TM M;
static unsigned char F[FMAX];          /* Fenster */
static int flen, kopf, zst, vorher;     /* vorher = letzter Uebergang 2*Zustand+Symbol, -1 am Anfang */
static Stapel L, R;                     /* L: oberster = direkt links vom Fenster; R: direkt rechts */
static int64_t schritt;
static int64_t paar[16][16];
static int64_t sprungpaar[16][16];     /* davon in Spruengen verbucht (nur Anzeige, -anteil) */
static int anteil = 0;
static int64_t nspruenge, sprungschritte;
static int halt;
static long nLpush, nRpush, nLpull, nRpull; /* Zaehler fuer die Sprungbedingungen */
static uint32_t letzterLpush, letzterRpush;

static uint32_t block_aus(const unsigned char *z) {
  uint32_t b = 0;
  for (int i = 0; i < BS; i++) b |= (uint32_t)z[i] << i;
  return b;
}
static void block_ein(unsigned char *z, uint32_t b) {
  for (int i = 0; i < BS; i++) z[i] = (b >> i) & 1;
}

/* Festgehaltener Moment fuer einen Sprung */
typedef struct {
  int gueltig;
  unsigned char f[FMAX]; int flen, kopf, zst, vorher;
  uint32_t x; long laufidx; int64_t anzahl;
  int64_t schritt; int64_t paar[16][16];
  long pushGegen, pullGegen, pushGleich, pullGleich; /* Gegenseite: abgelegt/geholt; eigene Seite: abgelegt/geholt */
} Moment;
static Moment ML, MR;

static int sprung_aus = 0, fehler = 0;
static int64_t kippS = -1, kippD, kippK; static int gekippt = 0;

static int gleich(const Moment *m) {
  return m->gueltig && m->flen == flen && m->kopf == kopf && m->zst == zst && m->vorher == vorher &&
         memcmp(m->f, F, flen) == 0;
}
static void merke(Moment *m, Stapel *s, long pushGegen, long pullGegen, long pushGleich, long pullGleich) {
  m->gueltig = 1; memcpy(m->f, F, flen); m->flen = flen; m->kopf = kopf; m->zst = zst; m->vorher = vorher;
  m->x = s->n ? s->a[s->n - 1].b : 0; m->laufidx = s->n - 1; m->anzahl = s->n ? s->a[s->n - 1].c : -1;
  m->schritt = schritt; memcpy(m->paar, paar, sizeof paar);
  m->pushGegen = pushGegen; m->pullGegen = pullGegen; m->pushGleich = pushGleich; m->pullGleich = pullGleich;
}

/* Versuch eines Sprungs vor dem Holen von Seite s (links: s=&L).  ziel = naechster Pruefpunkt. */
static void versuche(int links, int64_t ziel) {
  Stapel *s = links ? &L : &R, *g = links ? &R : &L;
  Moment *m = links ? &ML : &MR;
  long pushGegen = links ? nRpush : nLpush, pullGegen = links ? nRpull : nLpull;
  long pushGleich = links ? nLpush : nRpush, pullGleich = links ? nLpull : nRpull;
  uint32_t letzterGegen = links ? letzterRpush : letzterLpush;
  if (!sprung_aus && s->n > 0 && gleich(m) && s->n - 1 == m->laufidx && s->a[s->n - 1].b == m->x &&
      s->a[s->n - 1].c == m->anzahl - 1 && pushGegen == m->pushGegen + 1 && pullGegen == m->pullGegen &&
      pushGleich == m->pushGleich && pullGleich == m->pullGleich + 1) {
    int64_t dt = schritt - m->schritt;
    int64_t k = s->a[s->n - 1].c;           /* so viele X liegen noch an */
    if (dt > 0 && (ziel - schritt) / dt < k) k = (ziel - schritt) / dt;
    if (k > 0) {
      int64_t kz = fehler ? k - 1 : k;
      for (int a = 0; a < 16; a++)
        for (int b = 0; b < 16; b++) {
          int64_t d = kz * (paar[a][b] - m->paar[a][b]);
          paar[a][b] += d; sprungpaar[a][b] += d;
        }
      schritt += k * dt;
      s->a[s->n - 1].c -= k;
      if (s->a[s->n - 1].c == 0) s->n--;
      st_push(g, letzterGegen, k);
      nspruenge++; sprungschritte += k * dt;
      m->gueltig = 0;
      return;                               /* Fenster unveraendert; der Aufrufer holt jetzt normal */
    }
  }
  merke(m, s, pushGegen, pullGegen, pushGleich, pullGleich);
}

static void einzelschritt(void) {
  int s = F[kopf];
  int cur = 2 * zst + s;
  if (M.h[zst][s]) { halt = 1; return; }
  if (vorher >= 0) paar[vorher][cur]++;
  F[kopf] = M.wr[zst][s];
  kopf += M.mv[zst][s];
  zst = M.nx[zst][s];
  vorher = cur;
  schritt++;
}

static void holen_links(void) {
  uint32_t b = st_pop(&L);
  memmove(F + BS, F, flen); block_ein(F, b); flen += BS; kopf += BS; nLpull++;
}
static void holen_rechts(void) {
  uint32_t b = st_pop(&R);
  block_ein(F + flen, b); flen += BS; nRpull++;
}
static void ablegen(void) {
  while (kopf >= 2 * BS) {                 /* links zu viel */
    uint32_t b = block_aus(F); st_push(&L, b, 1); letzterLpush = b; nLpush++;
    memmove(F, F + BS, flen - BS); flen -= BS; kopf -= BS;
  }
  while (flen - 1 - kopf >= 2 * BS) {      /* rechts zu viel */
    uint32_t b = block_aus(F + flen - BS); st_push(&R, b, 1); letzterRpush = b; nRpush++;
    flen -= BS;
  }
}

static uint32_t crctab[256];
static void crcinit(void) {
  for (uint32_t n = 0; n < 256; n++) {
    uint32_t c = n;
    for (int k = 0; k < 8; k++) c = (c & 1) ? 0xEDB88320U ^ (c >> 1) : c >> 1;
    crctab[n] = c;
  }
}

/* Band ausbreiten: L von unten, Fenster, R von oben. Liefert Feld, Laenge, Kopfstelle. */
static unsigned char *ausbreiten(int64_t *laenge, int64_t *kpos) {
  int64_t n = flen;
  for (long i = 0; i < L.n; i++) n += L.a[i].c * BS;
  for (long i = 0; i < R.n; i++) n += R.a[i].c * BS;
  unsigned char *t = malloc(n);
  int64_t p = 0;
  for (long i = 0; i < L.n; i++) for (int64_t c = 0; c < L.a[i].c; c++) { block_ein(t + p, L.a[i].b); p += BS; }
  memcpy(t + p, F, flen); *kpos = p + kopf; p += flen;
  for (long i = R.n - 1; i >= 0; i--) for (int64_t c = 0; c < R.a[i].c; c++) { block_ein(t + p, R.a[i].b); p += BS; }
  *laenge = n;
  return t;
}

/* Negativkontrolle K8: k Zellen Kopf+d, Kopf+d+8, ... umdrehen; Band danach neu in Bloecke fassen. */
static void kippe(int64_t d, int64_t k) {
  int64_t n, kpos;
  unsigned char *t = ausbreiten(&n, &kpos);
  for (int64_t j = 0; j < k; j++) {
    int64_t q = kpos + d + 8 * j;
    if (q < 0 || q >= n) { fprintf(stderr, "kippe: Zelle ausserhalb des Bandes\n"); exit(2); }
    t[q] ^= 1;
  }
  int64_t l0 = kpos - kopf, r0 = l0 + flen;
  L.n = 0; R.n = 0;
  for (int64_t q = 0; q < l0; q += BS) st_push(&L, block_aus(t + q), 1);
  memcpy(F, t + l0, flen);
  for (int64_t q = n - BS; q >= r0; q -= BS) st_push(&R, block_aus(t + q), 1);
  ML.gueltig = MR.gueltig = 0;
  free(t);
}

static void bericht(void) {
  int64_t n, kpos;
  unsigned char *t = ausbreiten(&n, &kpos);
  int64_t a = 0, e = n - 1, eins = 0;
  while (a < n && !t[a]) a++;
  while (e >= a && !t[e]) e--;
  uint32_t c = 0xFFFFFFFFU;
  for (int64_t q = a; q <= e; q++) { c = crctab[(c ^ ('0' + t[q])) & 0xFF] ^ (c >> 8); eins += t[q]; }
  c ^= 0xFFFFFFFFU;
  printf("Schritt %lld%s\n", (long long)schritt, halt ? " HALT" : "");
  for (int x = 0; x < 16; x++)
    for (int y = 0; y < 16; y++)
      if (paar[x][y]) printf("  %c%d %c%d %lld\n", 'A' + x / 2, x % 2, 'A' + y / 2, y % 2, (long long)paar[x][y]);
  printf("  Spruenge %lld, darin %lld Schritte\n", (long long)nspruenge, (long long)sprungschritte);
  if (anteil)
    for (int x = 0; x < 16; x++)
      for (int y = 0; y < 16; y++)
        if (sprungpaar[x][y]) printf("  im Sprung %c%d %c%d %lld\n", 'A' + x / 2, x % 2, 'A' + y / 2, y % 2, (long long)sprungpaar[x][y]);
  printf("  Band %lld Zellen, %lld Einsen, CRC %u, Kopf %lld, Zustand %c\n", (long long)(e - a + 1), (long long)eins, c,
         (long long)(kpos - a), 'A' + zst);
  fflush(stdout);
  free(t);
}

int main(int argc, char **argv) {
  if (argc < 4) { fprintf(stderr, "Aufruf: blocksim <tm> <start> <pruefpunkt>... [-nosprung] [-fehler]\n"); return 2; }
  lese(argv[1], &M);
  crcinit();
  zst = argv[2][0] - 'A';
  int64_t ziele[64]; int nz = 0;
  for (int i = 3; i < argc; i++) {
    if (!strcmp(argv[i], "-nosprung")) sprung_aus = 1;
    else if (!strcmp(argv[i], "-fehler")) fehler = 1;
    else if (!strcmp(argv[i], "-anteil")) anteil = 1;
    else if (!strcmp(argv[i], "-kipp") && i + 3 < argc) {
      kippS = (int64_t)strtod(argv[i + 1], NULL); kippD = atoll(argv[i + 2]); kippK = atoll(argv[i + 3]); i += 3;
      ziele[nz++] = kippS;
    }
    else ziele[nz++] = (int64_t)strtod(argv[i], NULL);
  }
  for (int i = 1; i < nz; i++)                 /* Pruefpunkte aufsteigend */
    for (int j = i; j > 0 && ziele[j] < ziele[j - 1]; j--) { int64_t x = ziele[j]; ziele[j] = ziele[j - 1]; ziele[j - 1] = x; }
  flen = 2 * BS + 1; memset(F, 0, sizeof F); kopf = BS; vorher = -1;
  for (int z = 0; z < nz && !halt; z++) {
    int64_t ziel = ziele[z];
    while (schritt < ziel && !halt) {
      einzelschritt();
      if (halt) break;
      if (kopf < 0) {
        if (schritt < ziel) versuche(1, ziel);
        holen_links();
      } else if (kopf >= flen) {
        if (schritt < ziel) versuche(0, ziel);
        holen_rechts();
      }
      ablegen();
    }
    bericht();
    if (kippS >= 0 && schritt == kippS && !gekippt) { kippe(kippD, kippK); gekippt = 1; }
  }
  return 0;
}
