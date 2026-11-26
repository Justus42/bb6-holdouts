# Project status (26 Nov 2026, early; check against busy-beaver-explorer; corrected 26 Nov midday after the external review; M5 updated 26 Nov after PR 31)

Per group: what is **proved** (Rocq, with file and Actions run), what is only **observed** (with the bound
checked and the number of programs), and what is **open**. Every number points to the report it comes from
(tags below). Where reports disagree or were corrected later, the later one counts; corrections are listed at
the end. German version: `STATUS.md` (authoritative if the two differ).

**Overall:** We have decided no machine. Our Rocq results are reformulations: for Group 1 (sweep
acceleration) with one rule on top of it (rule F), and for 396 the reduction to a word system (PR 21).
Everything else is observation up to a bound.

**External (26 Nov):** busycoq merged PRs #59 and #55 into BB6. So **88, 312, 449 (halt)** and **471 (does not
halt)** are decided upstream. 123 and 223 halt according to busy-beaver-explorer (Lean and Coq; busycoq PRs
#72/#73 open). On 396, busy-beaver-explorer had everything we found, and more, by 24 Nov; **our 396 result is an
independent confirmation, not a new finding** [AB].

**External review (26 Nov, 11:45, own code):** confirms Group 1 (367 = start D, 378 = start C mirrored), the M5
mapping of all four, the visit law for 396 (20,000 random words, 30 rounds direct), the 396 run to round 260,000
(events 161,210/211 and 194,646/647), 403 tables, 509 holdouts without a BB6 entry and without an open PR.

Reports (all in `analyse/`, German, merged with the PR in brackets):
[G1] `gruppe1.md` (PR 2) · [G1-2] `gruppe1_teil2.md` (PR 3) · [G1-3] `gruppe1_teil3.md` (PR 6) ·
[S1] `gruppe1_stufe1.md` (PR 7) · [S2a] `gruppe1_stufe2a.md` (PR 8) · [ZY] `gruppe1_zyklus.md` (PR 9) ·
[LE] `gruppe1_linkes_ende.md` (PR 10) · [VL] `gruppe1_vorlagen.md` (PR 11) · [P26] `gruppe1_pr26.md` (PR 11) ·
[GR] `gruppe1_groesse.md` (PR 16) · [VB] `gruppe1_verboten.md` (PR 17) · [INV] `invarianten.md` (PR 15) ·
[M1] `318_518.md` (PR 4) · [M2] `318_518_teil2.md` (PR 5) · [396] `396.md` (PR 13) ·
[VK] `verwandtschaft.md` (PR 12, corrected in PR 13; English summary `verwandtschaft_en.md`) ·
[DA] `stand/datenabgleich.md` (PR 18) · [FB] `besuchsgesetz.md` (PR 23) · [RF] `396_rueckfuehrung.md` (PR 21) ·
[T2] `396_teil2.md` (PR 24) · [AB] `abgleich_bbe.md` (check against busy-beaver-explorer) ·
[M3] `318_518_teil3.md` (PR 31, halting patterns up to 8·10^14).

## Data (check of 25 Nov 2026) [DA]

- `holdouts.json` re-downloaded from denniskoshta.com (`data/holdouts_2026-11-25.json`): **byte-identical** to
  the 10 Nov snapshot. The site has not regenerated the file since.
- busycoq read directly: branch BB6 still at `33209bc7` (3 Nov), so **nothing merged** since. 58 new PR refs
  (62 to 119, 9 to 25 Nov) contain strings of 63 holdouts. **None concerns 396, 88, 312, 449, Group 1 or the
  M5 group** (two programs agree line by line, plus a normal-form check; negative controls fire). Whether
  those PRs are open or closed was not checked.
- cryptids (commit `f01ee56`, 25 Nov): nothing on 396, 88, 449, Group 1, M5. 312 has a formal reduction there
  (not a decision). Holdout 587 has a proved acceleration in the same situation as 396 (`1011` does not halt,
  only `111` does); read only.

## Check against busycoq and busy-beaver-explorer (26 Nov 2026) [AB]

- **busycoq** (via git, read only): branch BB6 is now at `9c078ca` (26 Nov), 25 PRs merged, among them #59
  (88, 312, 449 halt) and #55 (among others, 471 does not halt). Our pin has been `9c078ca` since 26 Nov (PR 27,
  Justus' OK; before: `33209bc7`). No file in BB6 (new since the old pin) or in PR refs 1–120 mentions 396, 110,
  587, Group 1 or M5.
- **Open busycoq PRs** (26 Nov, midday): `git ls-remote` shows `refs/pull/N/merge` only for open PRs without a
  conflict, so this is a lower bound: **53 open** (3 to 120). Compared with BB6, none adds a line naming 114, 367,
  378, 318, 518, 322, 274, 396, 110 or 587 (searched with `---` and `HHH`; control: 581 found in PR 76). One
  program of ours; agrees with the external review's count.
- **bbe invariant transfer** (26 Nov, `holdouts/recent-proofs/followup/invariant-transfer.md`, commit
  `0e077e33`, read only, not rebuilt): three screens over 509 open holdouts against 236,071 proved tables,
  **nothing decided, nothing transfers**. For our ten machines, according to bbe's data files (searched for our
  strings): no proved sibling with the same table, no transitions that go quiet; every neighbour differing in
  1–2 transitions parts without re-joining (396: 63 pairs, 587: 10, 378: 7, 367: 6, 114: 4, 110: 3,
  318/518/322/274: 1 each).
- **busy-beaver-explorer** (bbe, `github.com/fractal-geometry-explorer/busy-beaver-explorer`, head `662e215`):
  one folder per holdout with evidence levels. Lean theorems there use bbe's own definitions, not busycoq's;
  "native" means `native_decide`. Per group below under "External (bbe)".
- From now on (CLAUDE.md): before any work on a machine, check busycoq and bbe; the Discord rule is dropped.

## Group 1: 114, 367, 378 (one table, three starts)

### Proved (Rocq)

File `rocq/gruppe1_durchlauf.v` (515 lines, sha256 starts `79fdf709fca14c75`, unchanged since commit `44d8ed5`).

| Statement | Content | **pruefen** run (both images green, Print Assumptions `Closed under the global context`) |
|---|---|---|
| `gruppe1_114`, `gruppe1_367`, `gruppe1_378` | The machine halts from blank tape iff the sweep model (rules S1, S2, E) started in A / D / C reaches "halt". A reformulation, **not a decision** [S1] | run 45599575217 (commit `8722d86`) [S1]; again in run 45602646558 [S2a] |
| `regel_F`, `regel_F_oft` | eating round `x \| y → x+4 \| y−1` for odd x, y ≥ 1, in 25 model steps; m rounds at once [S2a] | run 45602646558 (commit `44d8ed5`) [S2a] |
| `erreicht_halt_erreicht` | such a jump does not change halting [S2a] | run 45602646558 [S2a] |

Shown by hand, **not** machine-checked: **Lemma K(C)**. If the run starts on a tape that is blank to the right
of the head, every halt is preceded by a moment where C steps from the left onto `0 1 1`. Necessary, not
sufficient [VB, section 1.2]. Confirmed externally by Justus.

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| No halt, every step checked | 10^12 steps, all three starts | 2 (`direkt.c` run 45614962053; `zaehl_direkt.c` run 45668615893) | [LE §2], [VB §4] |
| No K(C) (`C> 0 1 1`) | 10^9 locally, 10^10 in Actions (run 45668615893); up to 10^12 only `zaehl_direkt.c` | 2 up to 10^10, 1 up to 10^12 | [VB §2, §4] |
| No halt, **conditional** (phase automaton rules only empirical) | 10^24 (A, C) and 10^25 (D), 1,110 samples without finding | cycle accelerator; two Actions runs equal at every common power of ten (runs 45684698614, 45682765314); validated against `beschleuniger.py` up to 10^12 | [VB §5], PR 25 |
| Sweep model = direct simulation, byte for byte | 10^9 steps, 36,944 list lines | 2 (`sweepmodell.py`, `zweitpruefung.c`) | [G1-3 §2] |
| Check points (B/D reads 0, `11` to the right) 1.63 to 1.64 million per start, none with `111` | 10^9 | 2 (C, Rust) | [G1-2 §1] |
| Rule Z: `x = a + 4b + 7` at the end of every eating phase, 76/76, 77/77, 76/76 | 10^9 | lists from C, check in Python | [G1] |
| a even at all 232 cycle starts (so x odd, as rule F requires) | 10^9 | 2 (`zyklus.py`, `zyklus2.c`) | [ZY §5] |
| Cycle function predicts 68/76 (A), 67/76 (C), 66/77 (D) cycles exactly, **none wrong**; the rest "not applicable", always at the left end | 10^9 | 2 | [ZY] |
| Phase automaton (N1, N2, N2s, UA, LE, LG, VS) explains 99.995 % of phases | 10^17 (run 45614962053) | accelerator, equal to `direkt.c` at about 642,000 snapshots per start up to 10^12 | [LE §1, §2] |
| Left end: 2,877 unexplained cases in 13 core patterns; 13th pattern only at 8.2·10^16; "alt" share rising (0.7 % → 1.5 %) | 10^17 | 2 (`formen.py`, `formen2.awk`) | [LE §3, §4] |
| VS family as an 11-case rule: 1,656 of 1,656 observed cases right | 10^17 | rule against sweep model | [LE §4] |
| No conserved quantity; inside only m, S + r, x are conserved | 10^15 | 2 (`groesse.py`, `groesse2.c`), runs 45676439532, 45679952727 | [GR] |
| No CTL certificate (tape language with two automata) | all sizes up to 12×12 | SAT search, small sizes confirmed by enumeration | [INV] |
| The three starts do not merge | 10^9 | 1 | [G1 §1] |

### Open

- Whether Group 1 halts: **open** [VB §8].
- An invariant excluding K(C) or halting: none found [ZY §5], [GR §5], [INV], [VB §8].
- Phase automaton rules are not proved; halting beyond 10^12 is excluded only conditionally [VB §4].
- Left end: 7 of 8 families without a rule, "alt" cases without a rule, saturation not shown [LE §4].
- Rule Z and the first/last eating round not in Rocq [S2a]. Why a is always even is not proved [S2a], [ZY].
- Missing: an equation that ties the numbers together (like `gval G + 6 + κ = Q` in `PR_SBC.v`) [P26 §3].
- Per Justus (25 Nov): Group 1 rests at this stage.

### External (bbe, as of 13 Nov) [AB]

- Lean kernel: halting configurations, 10^4 steps, recoding sweeps (114: 6 rules, 367: 8, 378: shift rules);
  native: 10^7 steps. Computed: 10^9 (all), 114 accelerated to 1.29·10^10.
- Conjectured: "every entry grows by 2 per cycle". bbe also sees the same table with three starts.
- **We are further** (Rocq acceleration, rule F, 10^12 gap-free, 10^24/10^25 conditional). No contradiction.

## M5 group: 318, 518, 322, 274

### Proved (Rocq)

Nothing.

Shown by **table comparison** (holds for every step count, two programs, not in Rocq) [M1 §1]:
- All four are the 5-state machine M5 `1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC` with one state split.
  Halting patterns: 318 and 322 `B> 1 1`, 518 and 274 `C> 1 1`.
- Start in M5: 318/518 from A, 322 from C, 274 from D (mirrored). Runs from C and D coincide from step 11 / 25.
- Exactly these four in the 608 list; none in `decided`.

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| No halting pattern (`B> 1 1`, `C> 1 1`) | 10^10 steps (runs from A and from C) | 2 (`m5sim.c`, `zweitpruefung.go`) | [M1 §3] |
| No halting pattern (`B> 1 1`, `C> 1 1`), every transition counted | **8·10^14** (runs from A, C, D) | up to 10^10 three (`blocksim.c`, `zweitzaehlung.go`, `m5sim paare`); up to 10^11 also the external reviewer's direct simulation (code not in the repo); 10^11 to 8·10^14 two programs, **one principle** (jumps only on an exactly repeated situation, theorem in [M3 §2]); controls 9/9, including a planted halting pattern | [M3] |
| 318, 518 and M5 in lockstep | 10^9 | 1 (`m5sim gleich`) | [M1 §1] |
| Counter rules 1 to 3 (binary counter of digits Z/D1/D2/D3, separators W) | 3·10^8 | cycle files from 2 programs byte-identical, rule check Python only | [M1 §2] |
| Run from A does not meet run from C | 3·10^8 (cycle starts) | 1 | [M1 §1] |
| Accelerated simulator agrees at all cycle starts (40,324 from A, 41,794 from C) | 10^10 | 2 (`m5schnell.py`, `m5sim hash`) | [M2 §1] |
| Only three large rebuilds: from A at 29,754,240, from C at 87,823 and 874,896,314 | 8·10^14 (local; beyond 10^10 only every 5,000th cycle re-checked) | 1 (+ samples) | [M2 §3] |
| 83 / 88 wall passages (pairs) per run, not rebuilds | 8·10^14 | 1 | [M2 §2] |

### Open

- Whether M5 reaches `B> 1 1` / `C> 1 1`: **open**. It does not occur up to 8·10^14 [M3]; not checked by us beyond.
  **Not a new bound:** per `data/holdouts.json` (as of 10 Nov) slugbird (Holdout Guide, 3 Nov) simulated 274, 322 and 518
  to 1.0·10^17 and 318 to 1.0·10^20 steps (status "rules"), the RobinCodes sheet (9 Oct) all four to at least 10^15.
  Not re-checked, their programs unknown. What [M3] adds is only the published count of every transition by two programs.
- How a rebuild places the new digits (position and phase): no formula found, hence **no proof plan** [M2 §4].
- Next rebuild, if any, beyond 8·10^14; `m5sim` reaches about 10^15 [M2 §6].
- Templates in the pin would be `SBCv6a2.v` (compute the orbit) or `SOBLv3.v` (residue-class invariant); both
  need the missing rebuild map [M2 §5].
- Justus posted the M5 reduction in #bb6 (per project memory, 25 Nov).

### External (bbe, as of 8 Nov) [AB]

- Lean kernel: sweeps per machine; **318/518 in lockstep up to the first break** (`Twin.lean`).
  Computed: no halt up to 2·10^10 (318), 10^11 (322, 518), 10^9 (274).
- bbe knows the pairs 318~322, 274~518 (same table), 318~518 (same run), 322~274 (same tapes), but not the
  common 5-state machine M5. bbe does not follow the rebuilds to 8·10^14 as we do.
- No contradiction. Rebuild "from A at 29,754,240" vs bbe "step 29,787,121": the same rebuild; 29,754,240 is the
  start of the cycle, at 29,787,121 the head reaches the left end in state C (recomputed directly) [M3 §1a].
- `Twin.lean` (lockstep 318/518, pairs A-A, B-B, C-C, D-D, E-A, F-E, F-F) matches our M5 map [M3 §1a].
- At 10^9 our tapes from C and D match bbe (47,247 cells, 30,462 / 30,463 ones) [M3 §1a].
- bbe folders of the four machines unchanged since 13 Nov (274: 24 Nov), checked up to bbe head `47856cd8` (external reviewer).

## 396 with 110, 587 and 88, 312, 449 (visit-law family)

### Proved (Rocq)

By us: the **reduction** `halts tm c0 <-> W.trifft111 W.start` for 396 (`rocq/rueckfuehrung_396.v`, axiom-free,
pruefen run 45700149762 in both images, PR 21). A reformulation, **not a decision** [RF].

External: busycoq #59 (head `f23281d`) is merged into BB6 since 26 Nov (`1ff6eba`): **88, 312, 449 halt**
(round 161,211, block `1011`). Not built by us; bbe built it with Coq 8.20.1 [AB].

Shown by **table comparison** [VK, section F12]:
- After merging the halting state, the cores of 88, 312, 396, 449 agree **except for E1**; only 88 and 312
  share a core and run in lockstep.
- 396 halts only via F1; F is reached via B1 or E1 (`0RF`).

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| The visit law of PR #59 holds for 396 except the halting rule: `V(1011x) = 0001x` instead of halting; 396 halts only at `111` | all words up to length 12 after the block | 1 (`gesetz.py`, running the table) | [396 §3] |
| 88 and 396 equal round by round, not step by step | round 27 (about 1.57 million steps) simulated directly | 3 routes to the round model agree (`direkt.c` 27 rounds, `naiv.py` 34 rounds, `runde.c`) | [396 §4, §5] |
| 88 halts in round 161,211, as computed in PR #59 | – | 1 own (`runde.c`), run 45676623019 | [396 §4] |
| 396: no halt, only two 1011 events (rounds 161,211 and 194,647) | round 260,000 (word of 1,615,087 cells) | 1 for the long run (`runde.c`), run 45676623019 | [396 §4] |
| Visit-law family among all 608 (mirrored, all state pairs): exactly 88, 110, 312, 396, 449, 587; 110 = 396 except `V(111x)`, round-identical until the first visit hits 111. Consequence "if 396 never halts, 110 never halts": **tested, not proved** (law for 110 checked only as far as this row says). **Not covered** (other position or rule): 123, 223 (shifted by one cell, 123 with a second visit form; they halt), 471 (`V(110x) = 001x`; does not halt) | all words up to length 12; 27 rounds direct | 2 (`suche_a.py`, `suche_b.c`), identical; addendum 123/223/471 by sampling, 1 program | [FB], [AB §2] |
| 396: no halt, never `111`, never `011`; `11` at the end of a round only in 161,210 and 194,646, each followed by a 1011 event | round 748,162 (A), identical with B up to 573,850 | 2 (`runde.c`, `runde_b.cpp`), run 45688978145 | [T2] |

### External (bbe, as of 26 Nov, head `8515a2a4`) [AB §2, §3]

- **Lean kernel** (for 396 and 110): visit law and round form (since 13 Nov); word computation = machine, both
  directions (`halts_of_run`, `not_halts_of_run`); `junk_offset1` (harmless), `junk_offset2_halts` (halt);
  deficit form of the count (2^e − c). **native:** 10^7 steps, first 2,000 rounds.
- **Computed:** 10^11 steps direct; **no `111` up to round 4,000,000** (commit `195c1340`, 26 Nov; `piperun.c`,
  word-identical with `wordrun.c`/`deficit.c` checked only to 20,000 and 200,000 rounds, so one program with
  partial cross-checks; the word is then 24,856,760 cells). 18 junk events, all harmless (after a doubler,
  even deficit 6). Same statement in the folder of 110. Read only, not recomputed by us; our own run ends at
  round 748,162 [T2].
- **Danger condition:** a halt needs a junk event met at offset 2; that needs an odd deficit entering the last
  `000` block.
- **No invariant of the word end alone:** with an arbitrary count the last 48 cells reach `111` in 2–3 rounds;
  one or two extra visits lead to `111` about every 3,500 rounds. For 587, SAT finds no certificate with up to
  7 states (nor for the law of 110).
- 587 additionally in Lean: `1011` and `111` only at the right end of the word; run to round 4,000,000.
- **Our numbers agree** (event rounds, word length per round). Only we have: the reduction in Rocq on busycoq's
  definitions and the second independent round program.

### Open

- Whether 396 halts, i.e. whether `111` ever appears: **open** [T2], [AB].
- "396 never halts ⇒ 110 never halts" is **tested, not proved** on our side: the visit law for 110 is checked
  only for words up to length 12 and 27 rounds direct, not in Rocq [FB]. bbe has it in Lean on its own
  definitions; not checked by us.
- 396, 110, 587 still have no busycoq PR (not among the 53 open ones either, 26 Nov); of the three only 587 has a cryptids file [DA], [AB].
- The halting proof of PR #59 does **not** transfer to 396 [396].
- Next candidate template: busycoq #55 (471, `1011 → 0001` as in 396, does not halt); whether its technique fits
  396 is not checked [AB §2]. The proof idea "no visit ends on a 0 right before 11" is on hold (Justus, 26 Nov);
  according to bbe a statement about the word end alone is not enough for it [AB §3].

## Relationship map (all 608 holdouts)

### Proved (Rocq)

Nothing. Shown by **table comparison**, two programs (`karte_a.py`, `karte_b.c`, same 1,619 lines) [VK §3, §4]:
- 376 of 608 holdouts in **141 families**, almost all "same table, different start" (298 holdout pairs).
- **403 distinct tables** up to renaming and mirroring (498 without mirroring) [VK, result].
- 69 holdouts with a 5-state core; lockstep shown for 17 pairs, 2 of them holdout pairs (318/518, 88/312).
- busycoq `Eqv*.v` and cryptids `Equivalences.lean`: no holdout–holdout pairs [VK §1].

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| 6 more pairs in lockstep (e.g. 69/543, 166/391, 190/394, 489/598), **unproven** | 10^9 | 1 (`divergenz.c`), sieve in `karte_b.c` up to 10^6 | [VK §3] |
| None of the 510 same-table pairings merges | 10^6 (B), 10^5 (A) | 2 | [VK §3] |
| 14 families now lie entirely in new busycoq PRs, e.g. F1 {244, 279, 339, 473, 489, 598}, F26 {38, 59, 124}; not F12, F20 (M5) or Group 1 | PR refs up to 119, as of 25 Nov | 2 | [DA] |

### Open

- F1: why d833 halts and what distinguishes the starts; FAR starts (d581, d1250, d653, d934) [VK §3, §6].
- Whether cryptids accelerations transfer to other starts of the same table [VK §6].

## Corrections (later wins)

| earlier | later | source |
|---|---|---|
| F12 = "the same 5-state machine", "second M5-like family" | cores agree only except E1; only 88 and 312 share a core | [VK], corrected in PR 13 |
| lockstep of 88/312 with equivalents of 396 / 449: direction swapped | 88/312 with 396.2/.3/.5/.7; 396 with 449.1/.2 | [VK], [396 §6] |
| "likely" that the PR #59 law also decides 396 | does not transfer; 396 does not halt at `1011` | [396] |
| number of distinct tables not stated | 403 (498 without mirroring) | [VK], addendum PR 13 |
| left end: "verdict (a) with reservation", "alt share not rising" (draft up to 10^15) | verdict open; alt share rises to 1.5 % | [LE §7] |
| "no template in the pin for a regular + counter invariant" | `verify/PR_SBC.v` (busycoq PR #26) is such a template | [VL §4], [P26] |
| Lemma K(C) without hypothesis | holds only for runs with blank tape right of the start (Justus' counterexample) | [VB §7] |
| halting condition part 2 (B/D reads 0 before `111`) vs part 3 (C before `111`) | equivalent, checked | [G1-3 §3, addendum] |
| 11 check points at the left end unexplained (27/39 steps after a left record) | explained: C meets separator `<1>`, 14 or 26 cells from the end | [G1-2] → [G1-3 §2] |
| "x/2 ≥ list length" in 24 of 76 cycles (start A) | 19 of 77 with a different cut; what matters is the spread −64 to +27 | [G1] → [VL §3] |
| M5: left record from C at 29,550,874 read as a rebuild | not a large rebuild; real rebuilds from C only at 87,823 and 874,896,314 | [M1] → [M2 §2, §3] |
| M5: "no further rebuild up to 10^11" | none up to 8·10^14 | [M1] → [M2] |
| M5: halting pattern "not checked beyond 10^10" | checked up to 8·10^14, no occurrence | [M2 §4] → [M3] |
| M5: 8·10^14 read as the furthest bound | not a new bound: slugbird 10^17 (274, 322, 518) / 10^20 (318), sheet ≥ 10^15 (`holdouts.json`) | [M3] → external review 26 Nov |
| M5: 29,754,240 vs bbe 29,787,121 "not reconciled" | the same rebuild, two moments | [AB] → [M3 §1a] |
| cycle runs without int64 guard (runs 45675033053, 45682765314) | do not use beyond 10^24; guard since commit `509fb21` | [VB §5, §6] |
| busycoq BB6 "still at `33209bc7`", PR #59 "open, not merged" | since 26 Nov at `9c078ca`, #59 and #55 merged; 88, 312, 449, 471 decided upstream | [DA] → [AB §1] |
| 110 "new" in the visit-law family | known to bbe since 13 Nov, with a Lean proof of the law | [FB] → [AB §2] |
| family "exactly 6", "no further search needed" | holds only for the literal position; 123, 223 (shifted) and 471 (other `110` rule) are relatives, all three decided | [FB] → [AB §2] |
| 396 result (part 2) as our own finding | independent confirmation of bbe (as of 24 Nov), not new | [T2] → [AB] |
| "Our pin stays `33209bc7`" (check section) | pin is `9c078ca` since 26 Nov (PR 27) | external review 26 Nov |
| bbe 396/110: no `111` up to round 3,000,000, 14 junk events | up to round 4,000,000, 18, all harmless (bbe `195c1340`) | [AB] → external review 26 Nov |
| "If 396 never halts, 110 never halts" without a label | tested, not proved (law for 110 only tested) | [FB] → external review 26 Nov |
| whether busycoq PRs are open "not visible via git" | visible via `refs/pull/N/merge` (open ones without conflict only, lower bound); 53 on 26 Nov | [DA] → external review 26 Nov |

## Not included here

- The thread "Invariant against K(C)" (PR 19) only indirectly (phase automaton rules still empirical).
- The state of cryptids after 25 Nov (`f01ee56`) and Lean proofs outside busycoq.
- Results of the running thread "396 growth pattern" (not yet checked, so not included).
- Content from Discord. Instead of "ask in Discord first", the rule now is: check busycoq and bbe via git (CLAUDE.md).
