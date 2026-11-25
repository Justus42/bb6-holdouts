/* Durchlaufmodell einer Phase fuer Tabelle 114 (Gruppe 1), in C.
 *
 * Gleiche Rechnung wie rechne() in zyklus_beschl.py (dort in Python, Vorbild beschleuniger.rueckfall und
 * teil3/sweepmodell.py), Zeile fuer Zeile uebertragen:
 *   L = linker Stapel aus der Token-Liste (b = Einzelzelle, w = Wort 011 mal m), Kopf oben;
 *   R = [b1, w100^r, b0, b0]; Zustand C; Makroschritte: C laeuft ueber 100^m (schreibt 011^m),
 *   B/D laufen nach links ueber 011^m (schreiben 100^m, Paritaet tauscht B/D); sonst Einzelschritt.
 *   Ende der Phase: Zustand C (nicht im ersten Schritt) mit rechtem Muster z1 bzw. z2 (rechts_muster).
 *   K(C): Zustand C tritt von links auf eine Zelle mit 0 1 1 (auch beim letzten Eintritt eines 100-Blocks).
 * Ausgabe: kanonische Token-Liste (wie beschleuniger.canon: (?:011)+ gierig von links), Rest, r', Schritte,
 * K(C). Rueckgabe 0 = Phase zu Ende, 1 = Halt (Schritte bis zum Halt in *n_aus), 2 = mehr als grenze
 * Makroschritte (grenze 0 = unbegrenzt), <0 = Fehler (Platz).
 *
 * Bauen: cc -O2 -shared -fPIC -o rechne.so rechne.c
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { WB = 0, WW = 1 };          /* Eintrag: Einzelzelle / Wort */
enum { W011 = 0, W100 = 1 };
static const int WORT[2][3] = {{0, 1, 1}, {1, 0, 0}};

typedef struct { int8_t art, wort, bit; int64_t m; } E;
typedef struct { E *e; int64_t n, cap; } St;

static int st_push(St *s, E x) {
    if (s->n == s->cap) {
        int64_t c = s->cap ? 2 * s->cap : 1024;
        E *p = realloc(s->e, c * sizeof(E));
        if (!p) return -1;
        s->e = p; s->cap = c;
    }
    s->e[s->n++] = x;
    return 0;
}
static int push_b(St *s, int b) { E x = {WB, 0, (int8_t)b, 0}; return st_push(s, x); }

static int push_wort(St *s, int w, int64_t m) {
    if (s->n && s->e[s->n - 1].art == WW && s->e[s->n - 1].wort == w) { s->e[s->n - 1].m += m; return 0; }
    E x = {WW, (int8_t)w, 0, m};
    return st_push(s, x);
}

/* sweepmodell.pop_zelle */
static int pop_zelle(St *s, int links) {
    if (!s->n) return 0;
    E top = s->e[s->n - 1];
    if (top.art == WB) { s->n--; return top.bit; }
    s->n--;
    const int *w = WORT[(int)top.wort];
    if (top.m > 1) { E x = top; x.m = top.m - 1; st_push(s, x); }
    if (links) { push_b(s, w[0]); push_b(s, w[1]); return w[2]; }
    push_b(s, w[2]); push_b(s, w[1]); return w[0];
}

/* sweepmodell.push_zelle */
static int push_zelle(St *s, int b, int links) {
    if (push_b(s, b)) return -1;
    if (s->n >= 3 && s->e[s->n - 1].art == WB && s->e[s->n - 2].art == WB && s->e[s->n - 3].art == WB) {
        int a3 = s->e[s->n - 3].bit, a2 = s->e[s->n - 2].bit, a1 = s->e[s->n - 1].bit;
        if (links && a3 == 0 && a2 == 1 && a1 == 1) { s->n -= 3; return push_wort(s, W011, 1); }
        if (!links && a1 == 1 && a2 == 0 && a3 == 0) { s->n -= 3; return push_wort(s, W100, 1); }
    }
    return 0;
}

/* oben(): die k Zellen am Kopf, naechste zuerst; Blank 0 */
static void oben(const St *s, int links, int k, int *out) {
    int j = 0;
    for (int64_t i = s->n - 1; i >= 0 && j < k; i--) {
        E t = s->e[i];
        if (t.art == WB) { out[j++] = t.bit; continue; }
        const int *w = WORT[(int)t.wort];
        for (int64_t c = 0; c < t.m && j < k; c++)
            for (int u = 0; u < 3 && j < k; u++) out[j++] = links ? w[2 - u] : w[u];
    }
    while (j < k) out[j++] = 0;
}

/* beschleuniger.rechts_muster; Zustaende z1=0 z2=1 B0=2 B1=3 B2=4. Rueckgabe r oder -1 */
static int64_t rechts_muster(const St *R, int st) {
    int64_t r = 0;
    for (int64_t i = R->n - 1; i >= 0; i--) {
        E t = R->e[i];
        if (t.art == WW && t.wort == W100 && st == 2) { r += t.m; continue; }
        int z[6], nz;
        if (t.art == WB) { z[0] = t.bit; nz = 1; }
        else {
            const int *w = WORT[(int)t.wort];
            int64_t k = t.m < 2 ? t.m : 2;
            nz = 0;
            for (int64_t c = 0; c < k; c++) for (int u = 0; u < 3; u++) z[nz++] = w[u];
        }
        for (int a = 0; a < nz; a++) {
            int v = z[a];
            if (st == 0) { if (v != 0) return -1; st = 1; }
            else if (st == 1) { if (v != 0) return -1; st = 2; }
            else if (st == 2) { if (v != 1) return -1; st = 3; }
            else if (st == 3) { if (v != 0) return -1; st = 4; }
            else { if (v != 0) return -1; r++; st = 2; }
        }
    }
    return st == 3 ? r : -1;
}

/* Tabelle 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC: [q][c] = schreiben, Richtung, neu; A1 fehlt */
static const int T_W[6][2] = {{1, -1}, {0, 0}, {1, 0}, {1, 0}, {1, 1}, {1, 0}};
static const int T_D[6][2] = {{1, 0}, {1, -1}, {-1, 1}, {1, -1}, {1, 1}, {-1, -1}};
static const int T_Q[6][2] = {{1, -1}, {2, 5}, {3, 4}, {2, 1}, {3, 0}, {1, 2}};

/* Ausgabe-Puffer fuer Token */
typedef struct { int8_t *sep; int64_t *val; int64_t n, cap; } Tok;
static int tok_add(Tok *t, int sep, int64_t v) {
    if (t->n >= t->cap) return -1;
    t->sep[t->n] = (int8_t)sep; t->val[t->n] = v; t->n++;
    return 0;
}

/* canon(bits_aus_l(L)[:len-ab]) ohne die Bits auszuschreiben. sep: 0/1 Zelle, 2 = "" */
static int canon_l(const St *L, int64_t ab, Tok *t, int8_t *rest, int64_t *nrest, int64_t restcap) {
    /* Bitstrom: Eintraege von unten nach oben; die letzten ab Bits fallen weg */
    int64_t gesamt = 0;
    for (int64_t i = 0; i < L->n; i++) gesamt += L->e[i].art == WB ? 1 : 3 * L->e[i].m;
    int64_t ende = gesamt - ab;
    /* offene Trennbits (seit dem Ende des letzten Laufs) */
    int64_t ncap = 64, np = 0;
    int8_t *pend = malloc(ncap);
    if (!pend) return -1;
    int64_t lauf = 0;           /* Laenge des laufenden 011-Laufs (in Woertern), 0 = keiner */
    int fenster[3]; int nf = 0; /* noch nicht entschiedene Bits (hoechstens 2 nach vorn) */
    int64_t pos = 0;
    int64_t i = 0, kopie = 0; int u = 0;   /* Cursor: Eintrag i, Kopie kopie, Bit u im Wort */
#define SCHLUSS_LAUF() do { if (lauf) { \
        if (np == 0) { if (tok_add(t, 2, lauf)) goto fehler; } \
        else { for (int64_t a = 0; a + 1 < np; a++) if (tok_add(t, pend[a], 0)) goto fehler; \
               if (tok_add(t, pend[np - 1], lauf)) goto fehler; } \
        np = 0; lauf = 0; } } while (0)
#define PEND(b) do { if (np == ncap) { ncap *= 2; int8_t *q2 = realloc(pend, ncap); if (!q2) goto fehler; pend = q2; } \
        pend[np++] = (int8_t)(b); } while (0)
    /* gieriges (?:011)+ von links: Fenster mit 3 Bits */
    for (;;) {
        /* Schnellweg: Fenster leer, Cursor am Anfang einer Wortkopie 011, ganze Kopien passen vor das Ende */
        if (nf == 0 && i < L->n && L->e[i].art == WW && L->e[i].wort == W011 && u == 0) {
            int64_t uebrig = L->e[i].m - kopie;
            int64_t passt = (ende - pos) / 3;
            int64_t k = uebrig < passt ? uebrig : passt;
            if (k > 0) {
                lauf += k; pos += 3 * k; kopie += k;
                if (kopie == L->e[i].m) { i++; kopie = 0; }
                continue;
            }
        }
        /* Fenster auf 3 Bits fuellen */
        while (nf < 3 && pos + nf < ende) {
            /* Bit am Cursor holen und Cursor weiterschieben */
            int b;
            E e = L->e[i];
            if (e.art == WB) { b = e.bit; i++; }
            else { b = WORT[(int)e.wort][u]; u++; if (u == 3) { u = 0; kopie++; if (kopie == e.m) { i++; kopie = 0; } } }
            fenster[nf++] = b;
        }
        if (nf == 3 && fenster[0] == 0 && fenster[1] == 1 && fenster[2] == 1) {
            lauf++; pos += 3; nf = 0;
            continue;
        }
        if (nf == 0) break;
        /* kein 011 am Fensteranfang: laufenden Lauf schliessen, erstes Bit wird Trennbit */
        SCHLUSS_LAUF();
        PEND(fenster[0]);
        fenster[0] = fenster[1]; fenster[1] = fenster[2]; nf--;
        pos++;
    }
    SCHLUSS_LAUF();
    if (np > restcap) goto fehler;
    memcpy(rest, pend, np);
    *nrest = np;
    free(pend);
    return 0;
fehler:
    free(pend);
    return -1;
#undef SCHLUSS_LAUF
#undef PEND
}

int rechne(int64_t ntok, const int8_t *sep, const int64_t *val, int64_t ntail, const int8_t *tail, int64_t r,
           int8_t *sep_aus, int64_t *val_aus, int64_t cap_aus, int64_t *ntok_aus,
           int8_t *tail_aus, int64_t cap_tail, int64_t *ntail_aus,
           int64_t *r_aus, int64_t *n_aus, int64_t *kc_aus, int64_t grenze) {
    St L = {0}, R = {0};
    int ret = -1;
    for (int64_t j = 0; j < ntok; j++) {
        if (sep[j] != 2 && push_b(&L, sep[j])) goto ende;
        if (val[j]) { E x = {WW, W011, 0, val[j]}; if (st_push(&L, x)) goto ende; }  /* l_aus_token: append */
    }
    for (int64_t j = 0; j < ntail; j++) if (push_b(&L, tail[j])) goto ende;
    /* Python: R = [("b",1), ("w","100",r), ("b",0), ("b",0)], Kopf = R[-1] */
    if (push_b(&R, 1)) goto ende;
    if (r) { E x = {WW, W100, 0, r}; if (st_push(&R, x)) goto ende; }
    if (push_b(&R, 0) || push_b(&R, 0)) goto ende;
    int q = 2, rechts = 1, erster = 1;
    int64_t n = 0, kc = 0;
    int o[3];
    int64_t makro = 0;
    for (;;) {
        if (grenze && ++makro > grenze) { ret = 2; goto ende; }   /* Makroschritt-Grenze (nur Tests) */
        if (n > ((int64_t)1 << 61)) { ret = -3; goto ende; }      /* Schrittzahl zu gross fuer int64 */
        if (!erster && q == 2) {
            int64_t rr = -1; int ab = -1;
            if (rechts) { oben(&R, 0, 2, o); if (o[0] == 0 && o[1] == 0) { rr = rechts_muster(&R, 0); ab = 0; } }
            else { oben(&L, 1, 1, o); if (o[0] == 0) { rr = rechts_muster(&R, 1); ab = 1; } }
            if (rr >= 0) {
                Tok t = {sep_aus, val_aus, 0, cap_aus};
                if (canon_l(&L, ab, &t, tail_aus, ntail_aus, cap_tail)) goto ende;
                *ntok_aus = t.n; *r_aus = rr; *n_aus = n; *kc_aus = kc;
                ret = 0;
                goto ende;
            }
        }
        erster = 0;
        if (rechts && q == 2 && R.n && R.e[R.n - 1].art == WW && R.e[R.n - 1].wort == W100) {
            int64_t m = R.e[--R.n].m;
            oben(&R, 0, 3, o);
            if (o[0] == 0 && o[1] == 1 && o[2] == 1) kc++;
            if (push_wort(&L, W011, m)) goto ende;
            n += 3 * m;
            continue;
        }
        if (!rechts && (q == 1 || q == 3) && L.n && L.e[L.n - 1].art == WW && L.e[L.n - 1].wort == W011) {
            int64_t m = L.e[--L.n].m;
            if (push_wort(&R, W100, m)) goto ende;
            n += 3 * m;
            if (m % 2) q = q == 1 ? 3 : 1;
            continue;
        }
        int links = !rechts;
        int c = pop_zelle(links ? &L : &R, links);
        if (T_D[q][c] == 0) { *n_aus = n; ret = 1; goto ende; }   /* A liest 1: Halt */
        int w = T_W[q][c], d = T_D[q][c], nq = T_Q[q][c];
        n++;
        if (d == 1) {
            if (push_zelle(&L, w, 1)) goto ende;
            rechts = 1;
            if (nq == 2) { oben(&R, 0, 3, o); if (o[0] == 0 && o[1] == 1 && o[2] == 1) kc++; }
        } else {
            if (push_zelle(&R, w, 0)) goto ende;
            rechts = 0;
        }
        q = nq;
    }
ende:
    free(L.e); free(R.e);
    return ret;
}
