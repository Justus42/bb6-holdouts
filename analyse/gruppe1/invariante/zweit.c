/* Zweites, unabhaengig geschriebenes Programm (C, Bitebene): vollstaendige Aufzaehlung kleiner Phasen.

   Tabelle 114: 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC.
   Fuer jede Regel (N1 N2 N2s UA LE0 LE1 LG) werden ALLE Schnappschuesse mit
     Zonenlaenge 0..ZMAX, jedes Zonen-Token (1,n) mit n in {1,3,5,7},
     T0 = (1,n0), n0 in {2,4,6},
     Grenze/G/U nach der Regel mit Zahlen bis 6 bzw. 7, Trenner von G beliebig (0/1),
     r in {1,2}
   aufgebaut und Zelle fuer Zelle gerechnet, bis der Kopf zum ersten Mal Zelle p+3 betritt.
   Geprueft: kein Halt; C tritt nie von links auf x mit x+1 = x+2 = 1; Ende in Zustand C;
   der Kopf liest keine Zelle links des beschriebenen Bereichs (Praefix "P", hier mit Bits 1 0 1 1 belegt).
   Gezaehlt werden alle Rechtsschritte nach C nach den drei Zellen x, x+1, x+2.
   Aufruf: ./zweit <ZMAX>      Negativkontrollen: ./zweit <ZMAX> fehler  (Zonen-Token gerade statt ungerade
   und T0 ungerade: dann muss mindestens eine Pruefung anschlagen); ./zweit <N> kc (K(C)-Detektor auf
   Zufallsbaendern, siehe kc_kontrolle). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W 4096
static const char *TAB = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC";
static int tw[6][2], td[6][2], tq[6][2], th[6][2];
static unsigned char band[W];
static long long typen[8], inst, schritte_ges, verstoss_kc, verstoss_halt, verstoss_ende, verstoss_p;
static int fehlermodus;

static void tabelle(void) {
    for (int q = 0; q < 6; q++)
        for (int b = 0; b < 2; b++) {
            const char *e = TAB + 7 * q + 3 * b;
            if (e[0] == '-') { th[q][b] = 1; continue; }
            th[q][b] = 0; tw[q][b] = e[0] - '0'; td[q][b] = e[1] == 'R' ? 1 : -1; tq[q][b] = e[2] - 'A';
        }
}

/* Token-Folge links->rechts als (sep, n); sep = 2: kein Trennerbit. */
typedef struct { int sep, n; } Tok;

static void rechne(Tok *t, int nt, int praefix, int r) {
    memset(band, 0, sizeof band);
    int len = 0;
    for (int i = 0; i < nt; i++) len += (t[i].sep != 2) + 3 * t[i].n;
    int p0 = W / 2;
    int pos = p0 - len;
    int grenze_links = pos;   /* links davon: Praefix (oder leer) */
    if (praefix) {            /* P-Bereich: Bits 1 0 1 1 direkt links */
        band[pos - 4] = 1; band[pos - 3] = 0; band[pos - 2] = 1; band[pos - 1] = 1;
    }
    for (int i = 0; i < nt; i++) {
        if (t[i].sep != 2) band[pos++] = (unsigned char)t[i].sep;
        for (int k = 0; k < t[i].n; k++) { band[pos++] = 0; band[pos++] = 1; band[pos++] = 1; }
    }
    /* rechts: 0 0 (100)^r 1 */
    band[p0] = 0; band[p0 + 1] = 0;
    for (int k = 0; k < r; k++) { band[p0 + 2 + 3 * k] = 1; }
    band[p0 + 2 + 3 * r] = 1;
    int p = p0, q = 2;
    long long n = 0;
    inst++;
    for (;;) {
        if (praefix && p < grenze_links) { verstoss_p++; return; }
        if (p < 2 || p > W - 3) { verstoss_p++; return; }
        int b = band[p];
        if (th[q][b]) { verstoss_halt++; return; }
        band[p] = (unsigned char)tw[q][b];
        int d = td[q][b];
        p += d; q = tq[q][b]; n++;
        if (q == 2 && d == 1) {
            int x0 = band[p], x1 = band[p + 1], x2 = band[p + 2];
            typen[x0 * 4 + x1 * 2 + x2]++;
            if (x1 == 1 && x2 == 1) { verstoss_kc++; return; }
        }
        if (p == p0 + 3) { if (q != 2) verstoss_ende++; schritte_ges += n; return; }
        if (n > 10000000) { verstoss_ende++; return; }
    }
}

static Tok tk[64];

/* Zone rekursiv aufzaehlen; vorne (links) steht der Kern, hinten T0 */
static void zone(int regel, Tok *kern, int nk, int praefix, int m, int ztiefe) {
    static const int zw[4] = {1, 3, 5, 7};
    static const int zwf[4] = {2, 4, 6, 0};
    if (ztiefe == m) {
        for (int n0 = 2; n0 <= 6; n0 += 2)
            for (int r = 1; r <= 2; r++) {
                int nt = nk + m;
                tk[nt].sep = 1; tk[nt].n = fehlermodus ? n0 - 1 : n0;
                rechne(tk, nt + 1, praefix, r);
            }
        return;
    }
    for (int i = 0; i < 4; i++) {
        tk[nk + ztiefe].sep = 1;
        tk[nk + ztiefe].n = fehlermodus ? zwf[i] : zw[i];
        zone(regel, kern, nk, praefix, m, ztiefe + 1);
    }
    (void)regel; (void)kern;
}

static void regel_lauf(const char *name, int regel, int zmax) {
    memset(typen, 0, sizeof typen);
    inst = schritte_ges = verstoss_kc = verstoss_halt = verstoss_ende = verstoss_p = 0;
    for (int m = (regel == 6 ? 1 : 0); m <= zmax; m++) {
        /* Kern aufbauen; tk[0..nk-1] */
        if (regel == 0) {           /* N1: (0, k gerade) */
            for (int k = 0; k <= 6; k += 2) { tk[0].sep = 0; tk[0].n = k; zone(regel, tk, 1, 1, m, 0); }
        } else if (regel == 1 || regel == 2) {   /* N2: G, (1, k gerade); N2s: G, (0, k ungerade) */
            for (int gs = 0; gs <= 1; gs++)
                for (int g = 1; g <= 4; g++)
                    for (int k = (regel == 1 ? 0 : 1); k <= 7; k += 2) {
                        tk[0].sep = gs; tk[0].n = g;
                        tk[1].sep = regel == 1 ? 1 : 0; tk[1].n = k;
                        zone(regel, tk, 2, 1, m, 0);
                    }
        } else if (regel == 3) {    /* UA: G, (1,0), (0, k ungerade) */
            for (int gs = 0; gs <= 1; gs++)
                for (int g = 1; g <= 4; g++)
                    for (int k = 1; k <= 7; k += 2) {
                        tk[0].sep = gs; tk[0].n = g; tk[1].sep = 1; tk[1].n = 0; tk[2].sep = 0; tk[2].n = k;
                        zone(regel, tk, 3, 1, m, 0);
                    }
        } else if (regel == 4) {    /* LE0: ganz links (1,0) */
            tk[0].sep = 1; tk[0].n = 0; zone(regel, tk, 1, 0, m, 0);
        } else if (regel == 5) {    /* LE1: ganz links (1,0), (0, k ungerade) */
            for (int k = 1; k <= 7; k += 2) {
                tk[0].sep = 1; tk[0].n = 0; tk[1].sep = 0; tk[1].n = k; zone(regel, tk, 2, 0, m, 0);
            }
        } else {                    /* LG: nur regulaere Token */
            zone(regel, tk, 0, 0, m, 0);
        }
    }
    printf("%-4s Phasen %lld  Schritte %lld  Verstoesse: K(C)/111 %lld  Halt %lld  Ende-nicht-C %lld  "
           "Bereich %lld   C-Fenster:", name, inst, schritte_ges, verstoss_kc, verstoss_halt, verstoss_ende,
           verstoss_p);
    for (int i = 0; i < 8; i++)
        if (typen[i]) printf(" %d%d%d", i >> 2, (i >> 1) & 1, i & 1);
    printf("\n");
}

/* Negativkontrolle fuer den K(C)-Detektor: zufaellige Baender (1..14 Bits links, rechts leer), zufaelliger
   Startzustand, 300 Schritte. Nach dem Satz K(C) kommen dort K(C)-Ereignisse vor; der Detektor muss sie finden. */
static unsigned long long lcg = 12345;
static int zuf(int m) { lcg = lcg * 6364136223846793005ULL + 1442695040888963407ULL; return (int)((lcg >> 33) % m); }
static void kc_kontrolle(long long N) {
    long long treffer = 0, halte = 0;
    for (long long i = 0; i < N; i++) {
        memset(band, 0, 64);
        int nb = 1 + zuf(14), p = 32, q = zuf(6);
        for (int k = 0; k < nb; k++) band[p - nb + k] = (unsigned char)zuf(2);
        for (int n = 0; n < 300; n++) {
            if (p < 2 || p > 60) break;
            int b = band[p];
            if (th[q][b]) { halte++; break; }
            band[p] = (unsigned char)tw[q][b];
            int d = td[q][b];
            p += d; q = tq[q][b];
            if (q == 2 && d == 1 && band[p + 1] == 1 && band[p + 2] == 1) { treffer++; break; }
        }
    }
    printf("K(C)-Kontrolle: %lld Zufallsbaender, Detektor schlaegt an: %lld, Halte ohne vorherigen Treffer: %lld\n",
           N, treffer, halte);
    printf("Negativkontrolle %s\n", treffer > 0 && halte == 0 ? "SCHLAEGT AN" : "SCHLAEGT NICHT AN");
}

int main(int argc, char **argv) {
    int zmax = argc > 1 ? atoi(argv[1]) : 4;
    fehlermodus = argc > 2 && strcmp(argv[2], "fehler") == 0;
    tabelle();
    if (argc > 2 && strcmp(argv[2], "kc") == 0) { kc_kontrolle(zmax); return 0; }
    const char *namen[7] = {"N1", "N2", "N2s", "UA", "LE0", "LE1", "LG"};
    for (int r = 0; r < 7; r++) regel_lauf(namen[r], r, zmax);
    return 0;
}
