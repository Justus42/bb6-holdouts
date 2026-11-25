# Problem statement: BB(6) holdouts 274 / 318 / 322 / 518 (one 5-state machine "M5")

*Status 25 Nov 2026. Everything below is from simulation unless marked "proved". Nothing is decided.*

## Machines
- M5 = `1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC` (5 states, no halting transition).
- Each holdout is M5 with one state split into two copies, one of which halts (proved by table comparison):
  | holdout | table | M5 start | halts iff M5 ever shows |
  |---|---|---|---|
  | 318 | `1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC` | A | `B> 1 1` (B on a 1, next cell 1) |
  | 518 | `1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---` | A | `C> 1 1` |
  | 322 | `1RB1RF_1LC0LF_1RD0LB_0RA1RE_1RD---_0RC0LA` | C | `B> 1 1` |
  | 274 | `1RB0RE_1LC0RA_0LD1LB_1LA1LF_0LB0RD_0LB---` | D (mirrored) | `C> 1 1` (mirrored) |
- Runs from C and from D coincide after 11 / 25 steps. The run from A does not meet them (checked to 3·10^8).
  So there are two runs and two forbidden patterns.

## Observed behaviour
- At each cycle start the tape reads (from the right) as blocks: filler `U = 11111010`, four digit forms
  `Z = 111010`, `D1 = 10111111111010`, `D2 = 10101111111010`, `D3 = 11111111111010`, a wall
  `W = 1111111010`, plus a short irregular remainder at the left end.
- It is a counter: each cycle the rightmost digit advances one phase (Z→D1→D2→D3→Z); a digit advances iff
  its right neighbour goes D2→D3 or D3→Z (carry); W is skipped; tape grows by 4 cells per cycle; filler
  counts between digits roughly double from digit to digit. Exact cycle-duration formula known.
- An accelerated simulator (validated against direct simulation at every cycle start up to 10^10)
  ran both runs to ~8·10^14 steps. B> 11 and C> 11 were never seen (direct check up to 10^10 only).
- Irregular events: "wall passages" (a digit crosses a W in two cycles; rule observed) and very rare
  **big rebuilds** when a carry overflows the left end (cost ~0.1·width²): from A once (step 2.98·10^7),
  from C twice (8.8·10^4 and 8.75·10^8); none afterwards up to 8·10^14. After a rebuild new walls appear
  at the old digit positions (fixed offsets), but where the new digits sit and in which phase follows
  no formula found so far.

## What is open
1. A closed-form map "counter parameters before rebuild → after rebuild" (like the shift-overflow
   counter deciders SBCv6a2 / SOBLv3 in busycoq). With it the orbit could be computed or an invariant
   (e.g. mod 3) could exclude B> 11 / C> 11.
2. Whether the next rebuild from A (which carries the same left remainder that triggered C's rebuild at
   8.75·10^8) behaves the same.
3. Halting is not excluded beyond the directly simulated range.

Question to you: how would you model the left-end overflow so that rebuilds become a parameter map,
and which invariant would you test first to exclude `B> 1 1` and `C> 1 1`?
