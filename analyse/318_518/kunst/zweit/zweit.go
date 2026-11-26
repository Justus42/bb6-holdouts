// zweit.go - zweites, unabhaengig geschriebenes Programm zur Umbau-Messung (Auflage 5).
//
// Teilt mit dem Sammelprogramm (kunst.c + familie.py + m5schnell.py) keinen Code. Eigenes:
//   - Maschine: nicht M5 aus einer Tabelle, sondern die Holdouts 318 und 518 aus ihren Strings, im Gleichschritt
//     auf demselben Band (beide sind Hebungen von M5). Halt = Aufruf eines undefinierten Eintrags ("---") in 318
//     oder 518. Schreiben/Bewegen beider muss in jedem Schritt uebereinstimmen (sonst Abbruch).
//   - Band waechst nach beiden Seiten (kein festes Feld).
//   - Zerlegung: Bausteine als Zeichenketten, von rechts gierig der laengste passende Baustein, der an einer
//     Zellgrenze beginnt (links davon 0 oder Bandanfang); kein Lauflaengen-Muster.
//   - Klassen, W-Regel, Ende-Regel, Abschnitte direkt hier nachgerechnet.
//
// Aufrufe:
//
//	zweit lauf <eingaben.tsv> <ausgabe.tsv>         Familie (Spalten id teil rest items u e), je Lauf eine Zeile
//	zweit einzeln <zustand A-E> <band>               ein Band, Zyklusbeginne und Muster auf stdout
//	zweit zerlege <band|@datei>                     Rest und Zahl der Bausteine
//	zweit zyklen <zustand A-E> <band|@datei>         Zyklusbeginne mit vollem Band (Abgleich mit kunst umbau)
//
// MAXS=<n> setzt die Schrittgrenze (Standard 10^7; groesser nur fuer die Kontrollen an natuerlichen Umbauten).
// Negativkontrolle der Regelpruefung: Umgebungsvariablen REGEL_D2, REGEL_D3 setzen andere Versaetze.
package main

import (
	"bufio"
	"fmt"
	"os"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
)

const (
	m318        = "1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC"
	m518        = "1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---"
	maxSchritte = 10_000_000
	kMin        = 100
	maxZyklen   = 5
)

type eintrag struct {
	w, d, n int // schreiben, Richtung (+1/-1), naechster Zustand; n = -1: undefiniert
}

func lese(tm string) [][2]eintrag {
	teile := strings.Split(tm, "_")
	t := make([][2]eintrag, len(teile))
	for z, s := range teile {
		for b := 0; b < 2; b++ {
			c := s[3*b : 3*b+3]
			if c == "---" {
				t[z][b] = eintrag{0, 0, -1}
				continue
			}
			d := 1
			if c[1] == 'L' {
				d = -1
			}
			t[z][b] = eintrag{int(c[0] - '0'), d, int(c[2] - 'A')}
		}
	}
	return t
}

var T318, T518 = lese(m318), lese(m518)

// Zustand von M5 (A..E) -> Zustand in 318 bzw. 518 (Tabelle in analyse/318_518.md: 318 = A B C D A E, 518 = A B C D E E).
// Am Zyklusbeginn liest der Kopf eine 0, daher ist die Wahl der Kopie gleichgueltig; gewaehlt wird die Kopie,
// die nicht nur ueber den Halteuebergang erreicht wird.
var von5zu318 = map[byte]int{'A': 4, 'B': 1, 'C': 2, 'D': 3, 'E': 5}
var von5zu518 = map[byte]int{'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
var nach5von318 = []byte{'A', 'B', 'C', 'D', 'A', 'E'}

var BAUSTEIN = []struct{ name, s string }{
	{"D1", "10111111111010"}, {"D2", "10101111111010"}, {"D3", "11111111111010"},
	{"W", "1111111010"}, {"U", "11111010"}, {"Z", "111010"},
}
var REST = map[string]string{
	"RC1": "11111111101011111111111110101011111111111010101111111111111010",
	"RX":  "11111111101011111111111010111111101010111111111110",
}

func init() {
	sort.SliceStable(BAUSTEIN, func(i, j int) bool { return len(BAUSTEIN[i].s) > len(BAUSTEIN[j].s) })
}

func tok(n string) string {
	for _, b := range BAUSTEIN {
		if b.name == n {
			return b.s
		}
	}
	panic(n)
}

// ---------- Simulation ----------

type zyklus struct {
	schritt int
	zustand byte
	loRel   int
	band    string
}

type ergebnis struct {
	zyklen   []zyklus
	halt318  int
	halt518  int
	schritte int
	grenze   bool
}

func simuliere(eingabe string, start byte, maxS int) ergebnis {
	// Band als Slice mit Ursprung off: Zelle x (relativ zum ersten Eingabezeichen) liegt bei band[x+off].
	off := 1024
	band := make([]byte, off+len(eingabe)+1024)
	for i := 0; i < len(eingabe); i++ {
		band[off+i] = eingabe[i] - '0'
	}
	x := len(eingabe)
	links := 0      // linkester besuchter Ort (Eingabe zaehlt als besucht)
	rechts := x     // rechtester besuchter Ort
	seitRekord := 0 // Schritte seit dem letzten Rechts-Rekord
	q318, q518 := von5zu318[start], von5zu518[start]
	var e ergebnis
	for s := 1; s <= maxS; s++ {
		for x+off >= len(band) {
			band = append(band, make([]byte, len(band))...)
		}
		if x+off < 0 {
			panic("Band links")
		}
		b := band[x+off]
		a := T318[q318][b]
		c := T518[q518][b]
		if a.n < 0 {
			e.halt318++
			// weiter wie die Kopie (318-E = M5-A), damit der Lauf vergleichbar bleibt
			a = T318[4][b]
		}
		if c.n < 0 {
			e.halt518++
			c = T518[4][b] // 518-E = M5-E
		}
		if a.w != c.w || a.d != c.d || nach5von318[a.n] != "ABCDEE"[c.n] {
			panic(fmt.Sprintf("318 und 518 laufen auseinander bei Schritt %d", s))
		}
		band[x+off] = byte(a.w)
		x += a.d
		q318, q518 = a.n, c.n
		seitRekord++
		if x < links {
			links = x
		}
		if x > rechts {
			rechts = x
			if seitRekord >= kMin {
				var sb strings.Builder
				for y := links; y < x; y++ {
					sb.WriteByte('0' + band[y+off])
				}
				e.zyklen = append(e.zyklen, zyklus{s, nach5von318[q318], links, sb.String()})
				if len(e.zyklen) >= maxZyklen {
					e.schritte = s
					return e
				}
			}
			seitRekord = 0
		}
		if x+off <= 0 { // links erweitern
			neu := make([]byte, len(band)+4096)
			copy(neu[4096:], band)
			band = neu
			off += 4096
		}
	}
	e.schritte = maxS
	e.grenze = true
	return e
}

// ---------- Zerlegung ----------

type stueck struct {
	art string
	pos int // Anfang relativ zum Anfang des zerlegten Bandes
}

type zerlegung struct {
	ok     bool
	rest   string
	teile  []stueck // ohne U
	nU     []int    // U links vor jedem Teil
	uEnde  int
	ende   int
	endPos int // Anfang der Schluss-Einsen
}

func zerlegen(b string) zerlegung {
	var z zerlegung
	// Schluss-Einsen
	i := len(b)
	for i > 0 && b[i-1] == '1' {
		i--
	}
	z.ende = len(b) - i
	if z.ende != 0 && z.ende != 4 {
		return z
	}
	z.endPos = i
	type roh struct {
		art string
		pos int
	}
	var r []roh
	for i > 0 {
		gef := false
		for _, t := range BAUSTEIN {
			n := len(t.s)
			if i >= n && b[i-n:i] == t.s && (i-n == 0 || b[i-n-1] == '0') {
				r = append(r, roh{t.name, i - n})
				i -= n
				gef = true
				break
			}
		}
		if !gef {
			break
		}
	}
	z.rest = b[:i]
	z.ok = true
	// umdrehen
	for a, c := 0, len(r)-1; a < c; a, c = a+1, c-1 {
		r[a], r[c] = r[c], r[a]
	}
	u := 0
	for _, t := range r {
		if t.art == "U" {
			u++
			continue
		}
		z.teile = append(z.teile, stueck{t.art, t.pos})
		z.nU = append(z.nU, u)
		u = 0
	}
	z.uEnde = u
	return z
}

// ---------- Familie ----------

type eingabe struct {
	id, teil, rest string
	items          []stueck // art, Luecke (in pos missbraucht: Zahl der U davor)
	u, e           int
}

func baue(in eingabe) (string, []stueck, int) {
	var sb strings.Builder
	sb.WriteString(REST[in.rest])
	var lage []stueck
	for _, it := range in.items {
		sb.WriteString(strings.Repeat(tok("U"), it.pos))
		lage = append(lage, stueck{it.art, sb.Len()})
		sb.WriteString(tok(it.art))
	}
	sb.WriteString(strings.Repeat(tok("U"), in.u))
	endPos := sb.Len()
	sb.WriteString(strings.Repeat("1", in.e))
	return sb.String(), lage, endPos
}

var versatz = map[string]int{"D2": -3, "D3": 5}

func auswerten(in eingabe) string {
	b, alt, altEnde := baue(in)
	r := simuliere(b, 'A', maxSchritte)
	halt := r.halt318 + r.halt518
	klasse := ""
	j := -1
	var z zerlegung
	switch {
	case len(r.zyklen) == 0:
		klasse = "L"
	case r.zyklen[0].schritt <= 10*len(b):
		klasse = "K"
	default:
		for k, zy := range r.zyklen {
			zz := zerlegen(zy.band)
			if zz.ok && len(zz.rest) < 200 {
				j, z = k, zz
				break
			}
		}
		if j < 0 {
			klasse = "U-X"
		} else if z.rest == REST["RC1"] || z.rest == REST["RX"] {
			klasse = "U"
		} else {
			klasse = "U-R"
		}
	}
	feld := []string{in.id, in.teil, klasse, strconv.Itoa(halt), strconv.Itoa(r.schritte)}
	if j < 0 {
		return strings.Join(append(feld, "-", "-", "-", "-", "-", "-", "-"), "\t")
	}
	lo := r.zyklen[j].loRel
	// neue W und Ziffern in Eingabekoordinaten
	neuW := map[int]int{} // Lage -> Index in z.teile
	for k, t := range z.teile {
		if t.art == "W" {
			neuW[t.pos+lo] = k
		}
	}
	grenze := lo + len(z.rest)
	treffer := map[string][2]int{}
	gesehen, suffix := false, true
	for _, a := range alt {
		v, ist := versatz[a.art]
		if !ist {
			continue
		}
		_, f := neuW[a.pos+v]
		if a.pos+v >= grenze {
			t := treffer[a.art]
			t[1]++
			if f {
				t[0]++
			}
			treffer[a.art] = t
		}
		if f {
			gesehen = true
		} else if gesehen {
			suffix = false
		}
	}
	// Ende-Regel: letztes neues W minus altes Ende
	endeTxt := "None"
	maxW := -1 << 60
	for p := range neuW {
		if p > maxW {
			maxW = p
		}
	}
	if len(neuW) > 0 {
		endeTxt = strconv.Itoa(maxW - altEnde)
	}
	// Abschnitte zwischen Regel-W zweier benachbarter alter Ziffern
	var abschn []string
	for k := 0; k+1 < len(alt); k++ {
		v1, i1 := versatz[alt[k].art]
		v2, i2 := versatz[alt[k+1].art]
		if !i1 || !i2 {
			continue
		}
		k1, f1 := neuW[alt[k].pos+v1]
		k2, f2 := neuW[alt[k+1].pos+v2]
		if !f1 || !f2 {
			continue
		}
		nz, nw := 0, 0
		for _, t := range z.teile[k1+1 : k2] {
			if t.art == "W" {
				nw++
			} else {
				nz++
			}
		}
		abschn = append(abschn, fmt.Sprintf("%d:%d,%d", in.items[k+1].pos, nz, nw))
	}
	tr := func(a string) string { return fmt.Sprintf("%d/%d", treffer[a][0], treffer[a][1]) }
	ab := strings.Join(abschn, ";")
	if ab == "" {
		ab = "-"
	}
	return strings.Join(append(feld, strconv.Itoa(j), z.rest, tr("D2"), tr("D3"), strconv.FormatBool(suffix), endeTxt, ab), "\t")
}

func leseEingaben(pfad string) []eingabe {
	f, err := os.Open(pfad)
	if err != nil {
		panic(err)
	}
	defer f.Close()
	var out []eingabe
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		c := strings.Split(sc.Text(), "\t")
		in := eingabe{id: c[0], teil: c[1], rest: c[2]}
		for _, it := range strings.Fields(c[3]) {
			p := strings.Split(it, ":")
			g, _ := strconv.Atoi(p[1])
			in.items = append(in.items, stueck{p[0], g})
		}
		in.u, _ = strconv.Atoi(c[4])
		in.e, _ = strconv.Atoi(c[5])
		out = append(out, in)
	}
	return out
}

func main() {
	if v := os.Getenv("REGEL_D2"); v != "" {
		versatz["D2"], _ = strconv.Atoi(v)
	}
	if v := os.Getenv("REGEL_D3"); v != "" {
		versatz["D3"], _ = strconv.Atoi(v)
	}
	grenzeS := maxSchritte
	if v := os.Getenv("MAXS"); v != "" { // nur fuer die Kontrollen an natuerlichen Umbauten (Freigabe Justus 26.11.)
		grenzeS, _ = strconv.Atoi(v)
	}
	switch os.Args[1] {
	case "einzeln":
		r := simuliere(os.Args[3], os.Args[2][0], grenzeS)
		for _, z := range r.zyklen {
			zz := zerlegen(z.band)
			fmt.Println(z.schritt, string(z.zustand), z.loRel, len(z.band), len(zz.rest), zz.ok)
		}
		fmt.Println("HALT318", r.halt318, "HALT518", r.halt518, "SCHRITTE", r.schritte, "GRENZE", r.grenze)
	case "zyklen": // Zyklusbeginne mit vollem Band (fuer den Abgleich mit kunst umbau)
		arg := os.Args[3]
		if strings.HasPrefix(arg, "@") { // Band aus Datei
			d, err := os.ReadFile(arg[1:])
			if err != nil {
				panic(err)
			}
			arg = strings.TrimSpace(string(d))
		}
		r := simuliere(arg, os.Args[2][0], grenzeS)
		for _, z := range r.zyklen {
			fmt.Println("Z", z.schritt, string(z.zustand), z.loRel, z.band)
		}
		fmt.Println("HALT318", r.halt318, "HALT518", r.halt518, "SCHRITTE", r.schritte)
	case "zerlege": // Rest und Bausteine eines Bandes (Datei mit @)
		arg := os.Args[2]
		if strings.HasPrefix(arg, "@") {
			d, _ := os.ReadFile(arg[1:])
			arg = strings.TrimSpace(string(d))
		}
		z := zerlegen(arg)
		fmt.Println("OK", z.ok, "REST", z.rest, "TEILE", len(z.teile), "UENDE", z.uEnde, "ENDE", z.ende)
	case "lauf":
		ein := leseEingaben(os.Args[2])
		out := make([]string, len(ein))
		var wg sync.WaitGroup
		ch := make(chan int)
		for w := 0; w < runtime.NumCPU(); w++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for i := range ch {
					out[i] = auswerten(ein[i])
				}
			}()
		}
		for i := range ein {
			ch <- i
		}
		close(ch)
		wg.Wait()
		f, _ := os.Create(os.Args[3])
		defer f.Close()
		fmt.Fprintln(f, "id\tteil\tklasse\thalt\tschritte\tzyklus\tneuer_rest\tD2\tD3\tsuffix\tende\tabschnitte")
		for _, l := range out {
			fmt.Fprintln(f, l)
		}
	default:
		fmt.Fprintln(os.Stderr, "Aufruf siehe Kopf")
		os.Exit(2)
	}
}
