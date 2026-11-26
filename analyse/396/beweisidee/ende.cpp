// Zweites, unabhaengig geschriebenes Programm (Thread "396, Teil 2", 25.11.2026).
// Rundenrechnung nach dem Besuchsgesetz von 396 (busycoq PR #59, mit der 396-Halteregel):
//   V(0x)=1x, V(100x)=V(110x)=000 V(x), V(1010x)=1010 V(V(x)), V(1011x)=0001x, V(111x)=Halt.
//   Runde: s <- V(10 s), Start s = 1.
// Anders als runde.c:
//   * der Zaehler ist eine exakte natuerliche Zahl beliebiger Groesse, gespeichert als Laufliste ihrer Binaerziffern
//     (Laeufe gleicher Bits, vom niedrigsten Bit an), keine Annahme "2^e - c mit kleinem c";
//   * Bloecke werden nach jedem einzelnen Halt-Schritt (0->1, 1011->0001) neu bestimmt, nicht als feste Abfolge.
// Ausgabe im gleichen Protokollformat wie runde.c mit PROTO=1 (K, Z, E, H, HALT, ENDE).
// Aufruf: runde_b <max_runden> [zeit_s] [startwort]     TEST=1: Selbsttest der Zahl gegen unsigned __int128.
// MODUS=587: 1011-Regel von 587 (V(1011x)=1000x) statt 0001x.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <deque>
#include <vector>
#include <string>
#include <chrono>

struct Zahl {                      // n = Summe der Laeufe; front = niedrigste Bits
  struct Lauf { bool bit; uint64_t len; };
  std::deque<Lauf> l;              // Invariante: keine leeren Laeufe, Nachbarn verschieden, oberster Lauf ist 1, leer = 0
  bool null() const { return l.empty(); }
  bool ungerade() const { return !l.empty() && l.front().bit; }
  void unten_dazu(bool b, uint64_t k) {          // k Bits b unten anfuegen (vorne)
    if (k == 0) return;
    if (!l.empty() && l.front().bit == b) l.front().len += k; else l.push_front({b, k});
  }
  void unten_weg(uint64_t k) {                   // k unterste Bits entfernen (k <= Laenge des untersten Laufs)
    l.front().len -= k; if (l.front().len == 0) l.pop_front();
  }
  void oben_bereinigen() { while (!l.empty() && !l.back().bit) l.pop_back(); }
  void halbieren_ab() { if (l.empty()) return; unten_weg(1); oben_bereinigen(); }      // floor(n/2)
  void verdoppeln() { if (l.empty()) return; unten_dazu(false, 1); }                    // 2n
  void plus1() {
    if (l.empty()) { l.push_front({true, 1}); return; }
    if (!l.front().bit) {                         // ...0 -> ...1
      unten_weg(1); unten_dazu(true, 1); return;
    }
    uint64_t k = l.front().len; l.pop_front();    // 0111..1 + 1 = 1000..0
    if (l.empty()) { l.push_front({true, 1}); unten_dazu(false, k); return; }
    // naechster Lauf ist aus Nullen
    unten_weg(1);
    unten_dazu(true, 1);
    unten_dazu(false, k);
  }
  void minus1() {                                 // n >= 1
    if (l.front().bit) { unten_weg(1); unten_dazu(false, 1); oben_bereinigen(); return; }
    uint64_t k = l.front().len; l.pop_front();    // 1000..0 - 1 = 0111..1
    unten_weg(1);                                 // naechster Lauf besteht aus Einsen
    unten_dazu(false, 1);
    unten_dazu(true, k);
    oben_bereinigen();
  }
  void halbieren_auf() { bool u = ungerade(); halbieren_ab(); if (u) plus1(); }         // ceil(n/2)
  // Wert, falls < 2^62, sonst -1
  long long klein() const {
    uint64_t bits = 0; for (auto &x : l) { bits += x.len; if (bits > 62) return -1; }
    long long v = 0; int sh = 0; for (auto &x : l) { if (x.bit) for (uint64_t i = 0; i < x.len; i++) v |= 1LL << (sh + i); sh += (int)x.len; }
    return v;
  }
};

static int selbsttest() {          // Zahl gegen unsigned __int128 auf Zufallsfolgen
  srand(7); long fehler = 0;
  for (int t = 0; t < 20000; t++) {
    Zahl z; unsigned __int128 v = 0;
    for (int s = 0; s < 200; s++) {
      int op = rand() % 5;
      if (op == 0 && v < ((unsigned __int128)1 << 100)) { z.verdoppeln(); v *= 2; }
      else if (op == 1) { z.halbieren_ab(); v /= 2; }
      else if (op == 2) { z.halbieren_auf(); v = (v + 1) / 2; }
      else if (op == 3 && v < ((unsigned __int128)1 << 100)) { z.plus1(); v += 1; }
      else if (op == 4 && v > 0) { z.minus1(); v -= 1; }
      unsigned __int128 w = 0; int sh = 0;
      for (auto &x : z.l) { if (x.bit) for (uint64_t i = 0; i < x.len; i++) w |= (unsigned __int128)1 << (sh + i); sh += (int)x.len; }
      bool inv = z.l.empty() || z.l.back().bit;
      for (size_t i = 0; i < z.l.size(); i++) { if (z.l[i].len == 0) inv = false; if (i && z.l[i].bit == z.l[i-1].bit) inv = false; }
      if (w != v || !inv || z.null() != (v == 0) || z.ungerade() != (bool)(v & 1)) { fehler++; break; }
    }
  }
  printf("Selbsttest Zahl: %ld Fehler in 20000 Folgen\n", fehler);
  return fehler ? 1 : 0;
}

static std::vector<uint8_t> w;     // Zellen; Wort beginnt bei anf, rechts von w.size() nur Nullen
static size_t anf;
static long long runde;
static bool regel587 = false;
static size_t tod; static char art; static std::vector<size_t> stapel; static size_t maxtiefe; static std::vector<long long> tiefen(64); static std::vector<long long> abst(64); static size_t ezone, epos; static long long en; static bool ein; static long long ab = 1;     // MODUS=587: Regel V(1011x)=1000x (Vergleich mit cryptids 2.3)
static uint8_t z(size_t i) { return i < w.size() ? w[i] : 0; }
static void setze(size_t i, uint8_t b) { if (i >= w.size()) { if (!b) return; w.resize(i + 1, 0); } w[i] = b; }
static void zeige(const char *tag, size_t p, const Zahl &n) {
  long long k = n.klein();
  if (k >= 0) printf("%s %lld %zu %lld\n", tag, runde, p - anf, k); else printf("%s %lld %zu gross\n", tag, runde, p - anf);
}

// ein Besuchspaket mit n Besuchen ab Zelle p; true = Halt
static bool besuche(size_t p, Zahl n, size_t &haltstelle) {
  while (!n.null()) {
    if (!ein && p >= ezone) { ein = true; epos = p; en = n.klein(); }
    uint8_t a = z(p), b = z(p + 1), c = z(p + 2), d = z(p + 3);
    if (a == 0) {                                   // Block 0: ein Besuch endet hier
      if (b == 1 && c == 1) zeige("Z", p, n);
      setze(p, 1); n.minus1(); if (n.null()) { tod = p; art = b ? 'Y' : '0'; } continue;
    }
    if (b == 1 && c == 1) { haltstelle = p; return true; }          // 111
    if (b == 0 && c == 1) {
      if (d == 0) { n.verdoppeln(); p += 4; continue; }             // 1010: jeder Besuch schickt zwei weiter
      zeige("K", p, n);                                             // 1011 -> 0001 (396) bzw. 1000 (587), Besuch endet
      if (regel587) { setze(p + 2, 0); setze(p + 3, 0); n.minus1(); continue; }
      setze(p, 0); setze(p + 1, 0); setze(p + 2, 0); n.minus1(); if (n.null()) { tod = p; art = 'K'; } continue;
    }
    // 100 oder 110: m Besuche; der erste geht durch (-> 000), dann abwechselnd Ende (-> 100) und durch
    bool u = n.ungerade();
    setze(p, u ? 0 : 1); setze(p + 1, 0); setze(p + 2, 0);
    n.halbieren_auf(); p += 3;
  }
  return false;
}

int main(int argc, char **argv) {
  if (getenv("TEST")) return selbsttest();
  if (getenv("MODUS") && atoi(getenv("MODUS")) == 587) regel587 = true;
  long long maxr = atoll(argv[1]); double zeit = argc > 2 ? atof(argv[2]) : 0; const char *start = argc > 3 ? argv[3] : "1"; ab = argc > 4 ? atoll(argv[4]) : 1;
  size_t rand_links = 2 * (size_t)maxr + 8;
  w.assign(rand_links, 0); anf = rand_links;
  for (const char *q = start; *q; q++) setze(anf + (q - start), (uint8_t)(*q - '0'));
  auto t0 = std::chrono::steady_clock::now();
  for (runde = 1; runde <= maxr; runde++) {
    size_t altende = w.size(); std::string altrest; for (size_t i = altende >= 30 ? altende - 30 : 0; i < altende; i++) altrest += char('0' + w[i]);
    ezone = altende >= 30 ? altende - 30 : 0; ein = false;
    anf -= 2; w[anf] = 1; w[anf + 1] = 0;
    Zahl eins; eins.plus1();
    size_t hs = 0;
    bool halt = besuche(anf, eins, hs);
    while (w.size() > anf && w.back() == 0) w.pop_back();
    if (halt) { printf("HALT 111 %lld %zu\n", runde, hs - anf); return 0; }
    if (getenv("DIAG")) {
      while (!stapel.empty() && stapel.back() <= tod + (art == 'K' ? 2 : 0)) stapel.pop_back();
      long long dl = stapel.empty() ? 0 : (long long)(stapel.back() - tod); abst[dl < 63 ? dl : 63]++;
      if (stapel.size() && dl <= 1) printf("DELTA %lld %lld art %c\n", runde, dl, art);
      if (art != '0') { printf("TOD %lld %c pos %zu rest %zu kontext ", runde, art, tod - anf, w.size() - tod);
        for (long long i = (long long)tod - 24; i < (long long)tod + 8; i++) putchar(i >= (long long)anf ? '0' + z((size_t)i) : '.'); putchar('\n'); }
      stapel.push_back(tod); tiefen[stapel.size() < 63 ? stapel.size() : 63]++;
      if (stapel.size() > maxtiefe) { maxtiefe = stapel.size(); printf("T %lld %zu\n", runde, maxtiefe); }
      bool schluss = runde == maxr || (zeit > 0 && std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() > zeit);
      if (schluss) {
        printf("TIEFEN"); for (int i = 0; i < 64; i++) if (tiefen[i]) printf(" %d:%lld", i, tiefen[i]); printf("\n");
        printf("ABSTAND"); for (int i = 0; i < 64; i++) if (abst[i]) printf(" %d:%lld", i, abst[i]); printf("\n");
        printf("DIAGENDE %lld %zu\n", runde, w.size() - anf); fflush(stdout); return 0; }
    }
    if (getenv("ENDE") && runde >= ab) {
      std::string s; size_t von = tod >= anf + 6 ? tod - 6 : anf;
      for (size_t i = von; i < w.size() && s.size() < 60; i++) s += char('0' + w[i]);
      std::string neu; for (size_t i = ezone; i < w.size(); i++) neu += char('0' + w[i]);
      printf("R %lld L %zu d %zu Rest %zu %c %s\n", runde, w.size() - anf, tod - anf, w.size() - tod, art, s.c_str());
      if (getenv("ZONE")) printf("Z %lld ein %lld n %lld alt %s neu %s\n", runde, ein ? (long long)epos - (long long)ezone : -1, ein ? en : 0, altrest.c_str(), neu.c_str());
    }
    long long c11 = 0, c111 = 0, f11 = -1;
    for (size_t i = anf; i + 1 < w.size(); i++) if (w[i] && w[i + 1]) { c11++; if (f11 < 0) f11 = (long long)(i - anf); if (i + 2 < w.size() && w[i + 2]) c111++; }
    if (c11) printf("E %lld %lld %lld %lld\n", runde, c11, c111, f11);
    if (runde % 1000 == 0) {
      uint64_t h = 1469598103934665603ULL;
      for (size_t i = anf; i < w.size(); i++) { h ^= w[i]; h *= 1099511628211ULL; }
      printf("H %lld %zu %016llx\n", runde, w.size() - anf, (unsigned long long)h);
    }
    fflush(stdout);
    double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    if (zeit > 0 && s > zeit) { printf("ENDE %lld %zu\n", runde, w.size() - anf); return 0; }
  }
  printf("ENDE %lld %zu\n", maxr, w.size() - anf);
  return 0;
}
