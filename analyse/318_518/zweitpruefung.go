// zweitpruefung.go - zweites, unabhaengig geschriebenes Programm fuer die Analyse 318/518.
//
// Andere Sprache (Go), anderes Bandmodell (zwei Stapel statt Array) und es rechnet,
// wo moeglich, mit den Original-Maschinen statt mit der 5-Zustands-Maschine.
//
//	go run zweitpruefung.go abbild                Sucht fuer 274, 318, 322, 518 alle Abbildungen der
//	                                              6 Zustaende auf die 5 Zustaende von M5 (mit/ohne Spiegelung)
//	                                              und leitet daraus das Haltemuster in M5 ab.
//	go run zweitpruefung.go besuche <tm> <N>      Laeuft <tm> ab Leerband (Start A) N Schritte und zaehlt,
//	                                              wie oft der Zustand mit dem Halteuebergang betreten wird
//	                                              und was er dort liest.
//	go run zweitpruefung.go treffen <N>           M5 ab C und ab D: sucht den ersten Schritt, ab dem beide Laeufe
//	                                              dieselbe Konfiguration haben (gleicher Zustand, gleiches Band
//	                                              relativ zum Kopf), mit Versatz bis 100 Schritte.
//	go run zweitpruefung.go links <tm> <start> <N>  Links-Rekorde (Schritt, Zustand, Breite).
//	go run zweitpruefung.go zyklen <tm> <start> <N> <K>  Band an jedem Zyklusbeginn (Rechts-Rekord nach mindestens
//	                                              K Schritten ohne Rekord), gleiches Format wie m5sim.c.
//	go run zweitpruefung.go negativ               Negativkontrollen dieses Programms.
package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

type uebergang struct {
	schreibe byte
	rechts   bool
	nach     int // -1 = Halt
}

type maschine [][2]uebergang

func lies(s string) maschine {
	teile := strings.Split(s, "_")
	m := make(maschine, len(teile))
	for i, t := range teile {
		if len(t) != 6 {
			panic("Format: " + s)
		}
		for b := 0; b < 2; b++ {
			u := t[3*b : 3*b+3]
			if u == "---" {
				m[i][b] = uebergang{1, true, -1}
				continue
			}
			m[i][b] = uebergang{u[0] - '0', u[1] == 'R', int(u[2] - 'A')}
		}
	}
	return m
}

const M5 = "1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC"

var holdouts = []struct {
	n  int
	tm string
}{
	{274, "1RB0RE_1LC0RA_0LD1LB_1LA1LF_0LB0RD_0LB---"},
	{318, "1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC"},
	{322, "1RB1RF_1LC0LF_1RD0LB_0RA1RE_1RD---_0RC0LA"},
	{518, "1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---"},
}

// abbildungen liefert alle f: Zustaende(m) -> Zustaende(z), so dass jeder definierte Uebergang
// von m (ggf. gespiegelt) zum Uebergang von z im Bildzustand passt.
func abbildungen(m, z maschine, spiegel bool) [][]int {
	var erg [][]int
	f := make([]int, len(m))
	var rek func(i int)
	rek = func(i int) {
		if i == len(m) {
			for q := range m {
				for b := 0; b < 2; b++ {
					u := m[q][b]
					if u.nach < 0 {
						continue
					}
					v := z[f[q]][b]
					r := u.rechts
					if spiegel {
						r = !r
					}
					if u.schreibe != v.schreibe || r != v.rechts || f[u.nach] != v.nach {
						return
					}
				}
			}
			erg = append(erg, append([]int(nil), f...))
			return
		}
		for k := range z {
			f[i] = k
			rek(i + 1)
		}
	}
	rek(0)
	return erg
}

func buchstabe(i int) string { return string(rune('A' + i)) }

func abbild() {
	z := lies(M5)
	for _, h := range holdouts {
		m := lies(h.tm)
		gefunden := 0
		for _, sp := range []bool{false, true} {
			for _, f := range abbildungen(m, z, sp) {
				gefunden++
				bild := ""
				for _, k := range f {
					bild += buchstabe(k)
				}
				// Halteuebergang und die Uebergaenge, die in den Haltezustand fuehren
				for q := range m {
					for b := 0; b < 2; b++ {
						if m[q][b].nach >= 0 {
							continue
						}
						var vor []string
						for p := range m {
							for c := 0; c < 2; c++ {
								if m[p][c].nach == q {
									vor = append(vor, fmt.Sprintf("%s%d (in M5: %s%d)", buchstabe(p), c, buchstabe(f[p]), c))
								}
							}
						}
						fmt.Printf("%d %s gespiegelt=%v Bild=%s Start in M5=%s Halt bei %s%d (M5-Zustand %s); in den Haltezustand fuehren: %s\n",
							h.n, h.tm, sp, bild, buchstabe(f[0]), buchstabe(q), b, buchstabe(f[q]), strings.Join(vor, ", "))
					}
				}
			}
		}
		if gefunden == 0 {
			fmt.Printf("%d %s: KEINE Abbildung auf M5\n", h.n, h.tm)
		}
	}
}

// Band als zwei Stapel: links (oben = Zelle links vom Kopf), rechts (oben = Zelle unter dem Kopf).
type band struct {
	links, rechts []byte
}

func (b *band) lese() byte {
	if len(b.rechts) == 0 {
		return 0
	}
	return b.rechts[len(b.rechts)-1]
}
func (b *band) schreibeUndGehe(s byte, rechts bool) {
	if len(b.rechts) == 0 {
		b.rechts = append(b.rechts, 0)
	}
	b.rechts[len(b.rechts)-1] = s
	if rechts {
		x := b.rechts[len(b.rechts)-1]
		b.rechts = b.rechts[:len(b.rechts)-1]
		b.links = append(b.links, x)
	} else {
		var x byte
		if len(b.links) > 0 {
			x = b.links[len(b.links)-1]
			b.links = b.links[:len(b.links)-1]
		}
		b.rechts = append(b.rechts, x)
	}
}

func besuche(tm string, n int64) (halt int64, zaehl map[string]int64) {
	m := lies(tm)
	hz := map[int]bool{}
	for q := range m {
		for b := 0; b < 2; b++ {
			if m[q][b].nach < 0 {
				hz[q] = true
			}
		}
	}
	zaehl = map[string]int64{}
	var bd band
	q := 0
	for i := int64(0); i < n; i++ {
		s := bd.lese()
		if hz[q] && i > 0 {
			zaehl[fmt.Sprintf("%s liest %d", buchstabe(q), s)]++
		}
		u := m[q][s]
		if u.nach < 0 {
			return i + 1, zaehl
		}
		bd.schreibeUndGehe(u.schreibe, u.rechts)
		q = u.nach
	}
	return -1, zaehl
}

// konfiguration: Zustand + Band ohne Rand-Nullen, Kopf markiert.
func konfig(q int, b *band) string {
	var sb strings.Builder
	l := b.links
	i := 0
	for i < len(l) && l[i] == 0 {
		i++
	}
	for ; i < len(l); i++ {
		sb.WriteByte('0' + l[i])
	}
	sb.WriteString("[" + buchstabe(q) + "]")
	r := b.rechts
	j := 0
	for j < len(r) && r[j] == 0 {
		j++
	}
	for k := len(r) - 1; k >= j; k-- {
		sb.WriteByte('0' + r[k])
	}
	return sb.String()
}

func treffen(n int, s1, s2 int) (int, int, bool) {
	z := lies(M5)
	lauf := func(start int, n int) []string {
		var bd band
		q := start
		out := make([]string, 0, n+1)
		out = append(out, konfig(q, &bd))
		for i := 0; i < n; i++ {
			u := z[q][bd.lese()]
			bd.schreibeUndGehe(u.schreibe, u.rechts)
			q = u.nach
			out = append(out, konfig(q, &bd))
		}
		return out
	}
	c := lauf(s1, n+100)
	d := lauf(s2, n+100)
	for t := 0; t <= n; t++ {
		for v := -100; v <= 100; v++ {
			if t+v >= 0 && t+v < len(d) && c[t] == d[t+v] {
				return t, t + v, true
			}
		}
	}
	return 0, 0, false
}

func links(tm string, start int, n int64) {
	m := lies(tm)
	var bd band
	q := start
	pos, lo, hi := int64(0), int64(0), int64(0)
	for i := int64(0); i < n; i++ {
		u := m[q][bd.lese()]
		if u.nach < 0 {
			fmt.Println("HALT", i+1)
			return
		}
		bd.schreibeUndGehe(u.schreibe, u.rechts)
		q = u.nach
		if u.rechts {
			pos++
		} else {
			pos--
		}
		if pos > hi {
			hi = pos
		}
		if pos < lo {
			lo = pos
			fmt.Println(i+1, buchstabe(q), hi-lo+1)
		}
	}
}

// zyklen: an jedem Rechts-Rekord, dem mindestens k Schritte ohne Rekord vorausgingen,
// Schritt, Zustand und Band links vom Kopf (alles Besuchte) ausgeben.
func zyklen(tm string, start int, n, k int64) {
	m := lies(tm)
	var bd band
	q := start
	pos, hi, letzter := int64(0), int64(0), int64(0)
	w := bufio.NewWriterSize(os.Stdout, 1<<20)
	defer w.Flush()
	for i := int64(0); i < n; i++ {
		u := m[q][bd.lese()]
		if u.nach < 0 {
			fmt.Fprintln(w, "HALT", i+1)
			return
		}
		bd.schreibeUndGehe(u.schreibe, u.rechts)
		q = u.nach
		if u.rechts {
			pos++
		} else {
			pos--
		}
		if pos > hi {
			hi = pos
			if i+1-letzter >= k {
				fmt.Fprintf(w, "%d %s ", i+1, buchstabe(q))
				for _, c := range bd.links {
					w.WriteByte('0' + c)
				}
				w.WriteByte('\n')
			}
			letzter = i + 1
		}
	}
}

func negativ() {
	ok := true
	// 1. Abbildung: 518 mit geaendertem Uebergang E0 (0RA -> 1RA) darf sich nicht auf M5 abbilden lassen.
	z := lies(M5)
	m := lies("1RB0LD_0RC1RA_1RD1RF_1LA0LE_1RA0LC_0RA---")
	n := len(abbildungen(m, z, false)) + len(abbildungen(m, z, true))
	fmt.Println("Negativ 1 (518 mit E0=1RA): Abbildungen gefunden:", n, "(erwartet 0)")
	ok = ok && n == 0
	// 2. Haltefund: 2-Zustands-Fleissiger-Biber haelt nach 6 Schritten.
	h, _ := besuche("1RB1LB_1LA---", 100)
	fmt.Println("Negativ 2 (BB(2)-Meister): Halt in Schritt", h, "(erwartet 6)")
	ok = ok && h == 6
	// 3. Haltefund bei 318 mit absichtlich geaendertem F0 (0RE -> 0RA, fuehrt also in die Halte-Kopie A):
	//    muss halten, und der Zaehler muss "A liest 1" melden.
	h, zz := besuche("1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RA0LC", 1000000)
	fmt.Println("Negativ 3 (318 mit F0=0RA): Halt in Schritt", h, "A liest 1:", zz["A liest 1"], "(erwartet Halt, 1)")
	ok = ok && h > 0 && zz["A liest 1"] == 1
	// 4. Treffen: die Laeufe ab A und ab C duerfen sich in 400 Schritten nicht treffen.
	_, _, g := treffen(400, 0, 2)
	fmt.Println("Negativ 4 (Treffen A gegen C, 400 Schritte): gefunden", g, "(erwartet false)")
	ok = ok && !g
	if ok {
		fmt.Println("Negativkontrollen: alle schlagen an")
	} else {
		fmt.Println("Negativkontrollen: FEHLER")
		os.Exit(1)
	}
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Aufruf siehe Kopf der Datei")
		os.Exit(2)
	}
	switch os.Args[1] {
	case "abbild":
		abbild()
	case "besuche":
		n, _ := strconv.ParseInt(os.Args[3], 10, 64)
		h, z := besuche(os.Args[2], n)
		fmt.Println("Halt:", h, "(-1 = kein Halt)")
		for k, v := range z {
			fmt.Println(k, v)
		}
	case "treffen":
		n, _ := strconv.Atoi(os.Args[2])
		t, u, g := treffen(n, 2, 3)
		fmt.Println("C-Lauf Schritt", t, "= D-Lauf Schritt", u, "gefunden:", g)
	case "links":
		n, _ := strconv.ParseInt(os.Args[4], 10, 64)
		links(os.Args[2], int(os.Args[3][0]-'A'), n)
	case "zyklen":
		n, _ := strconv.ParseInt(os.Args[4], 10, 64)
		k, _ := strconv.ParseInt(os.Args[5], 10, 64)
		zyklen(os.Args[2], int(os.Args[3][0]-'A'), n, k)
	case "negativ":
		negativ()
	default:
		fmt.Println("unbekannter Modus")
		os.Exit(2)
	}
}
