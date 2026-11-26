// zweitzaehlung.go - Programm 2 fuer "M5-Haltemuster bis 8e14" (Analyse 318/518, Teil 3).
//
// Eigenstaendig geschrieben, ohne Code aus blocksim.c. Gleiche Aufgabe: alle Paare aufeinanderfolgender
// Uebergaenge (Zustand,gelesen) -> (Zustand,gelesen) einer TM ab Leerband exakt zaehlen, bis zu
// Pruefpunkten. Unterschiede zu Programm 1: Go statt C, Bloecke zu 24 statt 8 Zellen, andere
// Fensterregel (abgelegt wird erst bei mehr als 40 Zellen jenseits des Kopfes), andere Formulierung der
// Sprungbedingung (Ereignisprotokoll statt Zaehler).
//
// Sprungbedingung: Bei jedem Holen eines Blocks X von Seite S wird ein Schnappschuss genommen
// (Fenster, Kopf, Zustand, letzter Uebergang, Schritt, Zaehler) und ein Protokoll der Bandzugriffe
// (Holen/Ablegen je Seite) begonnen. Beim naechsten Holen von Seite S wird gesprungen, wenn
//   - Fenster, Kopf, Zustand, letzter Uebergang gleich sind,
//   - das Protokoll seit dem Schnappschuss genau [S holt X, Gegenseite legt Y ab] lautet,
//   - oben auf S wieder X liegt (dann derselbe Lauf, denn auf S wurde nichts abgelegt und
//     benachbarte Laeufe haben verschiedene Bloecke).
//
// Dann haengt der Abschnitt nur von (Fenster, Kopf, Zustand, letzter Uebergang, X) ab und wiederholt
// sich exakt, solange X kommt; k Wiederholungen werden mit k*Dauer und k*Paarzuwachs verbucht.
//
// Aufruf: zweitzaehlung <tm> <start> <pruefpunkt>... [-nosprung] [-fehler]
// -fehler: Negativkontrolle, springt ohne den Fenstervergleich.
package main

import (
	"bufio"
	"fmt"
	"hash/crc32"
	"os"
	"strconv"
)

const blk = 24
const grenze = 40

type uebergang struct {
	schreib, nach int
	rechts, halt  bool
}

type lauf struct {
	bits  uint32
	menge int64
}

type seite struct{ laeufe []lauf }

func (s *seite) ablegen(b uint32, k int64) {
	n := len(s.laeufe)
	if n > 0 && s.laeufe[n-1].bits == b {
		s.laeufe[n-1].menge += k
		return
	}
	s.laeufe = append(s.laeufe, lauf{b, k})
}

func (s *seite) oben() (uint32, int64) {
	n := len(s.laeufe)
	if n == 0 {
		return 0, 0
	}
	return s.laeufe[n-1].bits, s.laeufe[n-1].menge
}

func (s *seite) holen() uint32 {
	n := len(s.laeufe)
	if n == 0 {
		return 0
	}
	b := s.laeufe[n-1].bits
	s.laeufe[n-1].menge--
	if s.laeufe[n-1].menge == 0 {
		s.laeufe = s.laeufe[:n-1]
	}
	return b
}

type ereignis struct {
	art  byte // 'h' holen, 'a' ablegen
	link bool
	bits uint32
}

type schnapp struct {
	da      bool
	fenster string
	kopf    int
	zustand int
	letzter int
	schritt int64
	zaehl   [16][16]int64
	block   uint32
}

type maschine struct {
	t          [8][2]uebergang
	fenster    []byte
	kopf       int
	zustand    int
	letzter    int
	schritt    int64
	zaehl      [16][16]int64
	links      seite // Index 0 = ganz aussen, letzter = direkt am Fenster
	rechts     seite
	protokoll  []ereignis
	snap       [2]schnapp // 0 = links, 1 = rechts
	ohneSprung bool
	fehler     bool // Negativkontrolle: Fenstervergleich weglassen
	spruenge   int64
	imSprung   int64
	gehalten   bool
}

func parse(s string) [8][2]uebergang {
	var t [8][2]uebergang
	for i := 0; 7*i < len(s); i++ {
		for b := 0; b < 2; b++ {
			p := s[7*i+3*b : 7*i+3*b+3]
			if p[0] == '-' {
				t[i][b] = uebergang{halt: true}
				continue
			}
			t[i][b] = uebergang{schreib: int(p[0] - '0'), rechts: p[1] == 'R', nach: int(p[2] - 'A')}
		}
	}
	return t
}

func zuBits(z []byte) uint32 {
	var b uint32
	for i := 0; i < blk; i++ {
		if z[i] == 1 {
			b |= 1 << uint(i)
		}
	}
	return b
}

func ausBits(b uint32) []byte {
	z := make([]byte, blk)
	for i := 0; i < blk; i++ {
		z[i] = byte((b >> uint(i)) & 1)
	}
	return z
}

// sprungVersuch wird unmittelbar vor dem Holen von Seite li (true = links) aufgerufen.
func (m *maschine) sprungVersuch(li bool, ziel int64) {
	idx := 0
	eigen, gegen := &m.links, &m.rechts
	if !li {
		idx = 1
		eigen, gegen = &m.rechts, &m.links
	}
	sn := &m.snap[idx]
	topBits, topMenge := eigen.oben()
	if !m.ohneSprung && sn.da && topMenge > 0 && topBits == sn.block &&
		(m.fehler || sn.fenster == string(m.fenster)) && sn.kopf == m.kopf && sn.zustand == m.zustand && sn.letzter == m.letzter &&
		len(m.protokoll) == 2 &&
		m.protokoll[0] == (ereignis{'h', li, sn.block}) &&
		m.protokoll[1].art == 'a' && m.protokoll[1].link != li {
		dauer := m.schritt - sn.schritt
		k := topMenge
		if r := (ziel - m.schritt) / dauer; r < k {
			k = r
		}
		if k > 0 {
			var neu [16][16]int64
			for a := 0; a < 16; a++ {
				for b := 0; b < 16; b++ {
					neu[a][b] = m.zaehl[a][b] + k*(m.zaehl[a][b]-sn.zaehl[a][b])
				}
			}
			m.zaehl = neu
			m.schritt += k * dauer
			eigen.laeufe[len(eigen.laeufe)-1].menge -= k
			if eigen.laeufe[len(eigen.laeufe)-1].menge == 0 {
				eigen.laeufe = eigen.laeufe[:len(eigen.laeufe)-1]
			}
			gegen.ablegen(m.protokoll[1].bits, k)
			m.spruenge++
			m.imSprung += k * dauer
		}
	}
	// neuer Schnappschuss fuer diese Seite; Protokoll neu beginnen
	*sn = schnapp{true, string(m.fenster), m.kopf, m.zustand, m.letzter, m.schritt, m.zaehl, 0}
	sn.block, _ = eigen.oben()
	m.protokoll = m.protokoll[:0]
	// der andere Schnappschuss bleibt nur gueltig, wenn sein Protokoll weiterlaeuft - das tut es nicht
	m.snap[1-idx].da = false
}

func (m *maschine) lauf(ziel int64) {
	for m.schritt < ziel && !m.gehalten {
		sym := m.fenster[m.kopf]
		u := m.t[m.zustand][sym]
		if u.halt {
			m.gehalten = true
			return
		}
		jetzt := 2*m.zustand + int(sym)
		if m.letzter >= 0 {
			m.zaehl[m.letzter][jetzt]++
		}
		m.letzter = jetzt
		m.fenster[m.kopf] = byte(u.schreib)
		if u.rechts {
			m.kopf++
		} else {
			m.kopf--
		}
		m.zustand = u.nach
		m.schritt++
		if m.kopf < 0 {
			if m.schritt < ziel {
				m.sprungVersuch(true, ziel)
			}
			b := m.links.holen()
			m.protokoll = append(m.protokoll, ereignis{'h', true, b})
			m.fenster = append(ausBits(b), m.fenster...)
			m.kopf += blk
		} else if m.kopf >= len(m.fenster) {
			if m.schritt < ziel {
				m.sprungVersuch(false, ziel)
			}
			b := m.rechts.holen()
			m.protokoll = append(m.protokoll, ereignis{'h', false, b})
			m.fenster = append(m.fenster, ausBits(b)...)
		}
		for m.kopf > grenze {
			b := zuBits(m.fenster[:blk])
			m.links.ablegen(b, 1)
			m.protokoll = append(m.protokoll, ereignis{'a', true, b})
			m.fenster = append([]byte(nil), m.fenster[blk:]...)
			m.kopf -= blk
		}
		for len(m.fenster)-1-m.kopf > grenze {
			n := len(m.fenster)
			b := zuBits(m.fenster[n-blk:])
			m.rechts.ablegen(b, 1)
			m.protokoll = append(m.protokoll, ereignis{'a', false, b})
			m.fenster = m.fenster[:n-blk]
		}
		if len(m.protokoll) > 8 {
			m.protokoll = m.protokoll[:8] // laenger als 2 heisst ohnehin: kein Sprung
		}
	}
}

func (m *maschine) ausgabe(w *bufio.Writer) {
	var band []byte
	for _, l := range m.links.laeufe {
		z := ausBits(l.bits)
		for c := int64(0); c < l.menge; c++ {
			band = append(band, z...)
		}
	}
	kpos := len(band) + m.kopf
	band = append(band, m.fenster...)
	for i := len(m.rechts.laeufe) - 1; i >= 0; i-- {
		l := m.rechts.laeufe[i]
		z := ausBits(l.bits)
		for c := int64(0); c < l.menge; c++ {
			band = append(band, z...)
		}
	}
	a, e := 0, len(band)-1
	for a < len(band) && band[a] == 0 {
		a++
	}
	for e >= a && band[e] == 0 {
		e--
	}
	txt := make([]byte, 0, e-a+1)
	for _, c := range band[a : e+1] {
		txt = append(txt, '0'+c)
	}
	h := ""
	if m.gehalten {
		h = " HALT"
	}
	fmt.Fprintf(w, "Schritt %d%s\n", m.schritt, h)
	for x := 0; x < 16; x++ {
		for y := 0; y < 16; y++ {
			if m.zaehl[x][y] != 0 {
				fmt.Fprintf(w, "  %c%d %c%d %d\n", 'A'+x/2, x%2, 'A'+y/2, y%2, m.zaehl[x][y])
			}
		}
	}
	fmt.Fprintf(w, "  Spruenge %d, darin %d Schritte\n", m.spruenge, m.imSprung)
	fmt.Fprintf(w, "  Band %d Zellen, CRC %d, Kopf %d, Zustand %c\n", e-a+1, crc32.ChecksumIEEE(txt), kpos-a, 'A'+m.zustand)
	w.Flush()
}

func main() {
	if len(os.Args) < 4 {
		fmt.Fprintln(os.Stderr, "Aufruf: zweitzaehlung <tm> <start> <pruefpunkt>... [-nosprung]")
		os.Exit(2)
	}
	m := &maschine{t: parse(os.Args[1]), zustand: int(os.Args[2][0] - 'A'), letzter: -1}
	m.fenster = make([]byte, 2*blk+1)
	m.kopf = blk
	var ziele []int64
	for _, a := range os.Args[3:] {
		if a == "-nosprung" {
			m.ohneSprung = true
			continue
		}
		if a == "-fehler" {
			m.fehler = true
			continue
		}
		f, err := strconv.ParseFloat(a, 64)
		if err != nil {
			fmt.Fprintln(os.Stderr, "Pruefpunkt?", a)
			os.Exit(2)
		}
		ziele = append(ziele, int64(f))
	}
	w := bufio.NewWriter(os.Stdout)
	for _, z := range ziele {
		m.lauf(z)
		m.ausgabe(w)
		if m.gehalten {
			break
		}
	}
}
