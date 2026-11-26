# 396, Beweisidee: Zwischenstand (angehalten)

Angehalten am 26.11.2026 um 05:15 UTC auf Justus' Anweisung („Beweisidee zu 396: noch NICHT starten“). Davor
liefen etwa 15 Minuten Arbeit. Es gab keinen Actions-Lauf und kein Rocq.

## Bis dahin erledigt

- **Justus' Zählung nachgeprüft, mit zwei Programmen.**
  - Grundlage: alle Wörter bis Länge 14 ohne 111.
  - Ein neues 111 entsteht nur, wenn ein Besuch auf einer 0 direkt vor `11` endet: 864 Fälle, davon
    82 Treffer und 782, bei denen nur das Ergebnis 111 enthält. Die 782 stimmen mit Justus überein.
    Andere Ursachen: 0.
  - Ein neues `11` entsteht nur aus einem Ende auf einer 0 direkt vor einer 1. Verstöße: 0.
  - Bis Länge 18 (`lemma_b.c`): 10.212 neue 111, alle mit einem Ende vor `11`.
  - Programme: `lemma_a.py` (rekursiv) und `lemma_b.c` (Zählerform), unabhängig geschrieben.
  - Negativkontrolle `FEHLER=1` (Regel V(100x)=001V(x)): schlägt an, 78 Verstöße bei Länge 12.
- **Beweisskizze auf Papier, noch nicht ausgearbeitet und nicht in Rocq.**
  - Links von jedem Eintreffen eines Besuchs steht eine 0.
  - Nur V(0x) erzeugt neue Einsen.
  - Daraus folgen beide Aussagen.
- **Diagnose des Wortendes mit zwei unabhängigen Programmen.**
  - Programme: `ende.cpp`, abgeleitet aus `runde_b.cpp`, und `runde_diag.c`, abgeleitet aus `runde.c`.
  - Bis Runde 20.000 zeilengleich (`a20k.txt` = `b20k.txt`).
  - Befund: Am Ende des Wortes stapeln sich die Todesstellen früherer Runden. Dieser „Generationen-Stapel“
    wird tiefer: Tiefe 9 bei Runde 10.974.
  - Die Abstände zwischen den Todesstellen wachsen bis 44.
  - Leitern `1(01)^k` entstehen, wenn ein Besuch 2 Zellen vor der vorigen Todesstelle endet.
- **Lokale Aufzählung** (`lokal_y.py`): Ohne globale Nebenbedingungen folgt auf ein neues `11` oft ein
  gefährlicher Besuch (31.504 Fälle). Die Sicherheit muss also aus der Zählerstruktur kommen.

## Vorläufige Einschätzung (unbelegt)

Eine endliche Menge roher Endzustände reicht vermutlich nicht, weil Stapeltiefe und Abstände wachsen. Der
Langlauf bis Runde 748.162, der das prüfen sollte, ist nicht gestartet.

## Nicht begonnen

- Kandidat für eine abgeschlossene Zustandsmenge
- Langlauf
- Plan für 110
- Bericht
