(* Referenz des Wortsystems fuer 396 (Thread "396, Teil 2", 25.11.2026).
   scripts/aussage_check --wortsystem prueft, dass die Beweisdatei ein Modul mit genau diesen Saetzen
   enthaelt (Kommentare und Leerraum zaehlen nicht) und dass der Hauptsatz die Form
     halts <tm> c0 <-> <PRAEDIKAT> <START>
   mit den unten genannten Namen hat.
   AUSSAGE: W.trifft111 W.start
   Regeln: V(0x) = 1x, V(100x) = V(110x) = 000 V(x), V(1010x) = 1010 V(V(x)), V(1011x) = 0001x,
   V(111x) trifft 111; Runde: s <- V(10 s); Startwort W.start = 1. *)

Module W.

(** Ein Wort ist eine endliche Liste von Zellen (true = 1); rechts davon stehen
    nur Nullen. [z w] ist die erste Zelle (0 hinter dem Ende), [tl w] der Rest. *)
Definition z (w : list bool) : bool := match w with [] => false | b :: _ => b end.

(** [Vis w y]: ein Besuch auf w endet, das Wort ist danach y. *)
Inductive Vis : list bool -> list bool -> Prop :=
  | V_0 : forall w,
      z w = false ->
      Vis w (true :: tl w)
  | V_100 : forall w y,
      z w = true -> z (tl w) = false -> z (tl (tl w)) = false ->
      Vis (tl (tl (tl w))) y ->
      Vis w (false :: false :: false :: y)
  | V_110 : forall w y,
      z w = true -> z (tl w) = true -> z (tl (tl w)) = false ->
      Vis (tl (tl (tl w))) y ->
      Vis w (false :: false :: false :: y)
  | V_1010 : forall w y1 y2,
      z w = true -> z (tl w) = false -> z (tl (tl w)) = true -> z (tl (tl (tl w))) = false ->
      Vis (tl (tl (tl (tl w)))) y1 -> Vis y1 y2 ->
      Vis w (true :: false :: true :: false :: y2)
  | V_1011 : forall w,
      z w = true -> z (tl w) = false -> z (tl (tl w)) = true -> z (tl (tl (tl w))) = true ->
      Vis w (false :: false :: false :: true :: tl (tl (tl (tl w)))).

(** [Hit w]: ein Besuch auf w trifft (hier oder weiter rechts) auf 111. *)
Inductive Hit : list bool -> Prop :=
  | H_111 : forall w,
      z w = true -> z (tl w) = true -> z (tl (tl w)) = true ->
      Hit w
  | H_100 : forall w,
      z w = true -> z (tl w) = false -> z (tl (tl w)) = false ->
      Hit (tl (tl (tl w))) ->
      Hit w
  | H_110 : forall w,
      z w = true -> z (tl w) = true -> z (tl (tl w)) = false ->
      Hit (tl (tl (tl w))) ->
      Hit w
  | H_1010a : forall w,
      z w = true -> z (tl w) = false -> z (tl (tl w)) = true -> z (tl (tl (tl w))) = false ->
      Hit (tl (tl (tl (tl w)))) ->
      Hit w
  | H_1010b : forall w y1,
      z w = true -> z (tl w) = false -> z (tl (tl w)) = true -> z (tl (tl (tl w))) = false ->
      Vis (tl (tl (tl (tl w)))) y1 -> Hit y1 ->
      Hit w.

(** [Runde w0 k s]: nach k Runden ab w0 ist das Wort s. Eine Runde setzt 1 0 vor
    das Wort und macht einen Besuch. *)
Inductive Runde (w0 : list bool) : nat -> list bool -> Prop :=
  | R_0 : Runde w0 O w0
  | R_S : forall k s s',
      Runde w0 k s -> Vis (true :: false :: s) s' ->
      Runde w0 (S k) s'.

(** In einer Runde trifft der Besuch auf 111. *)
Definition trifft111 (w0 : list bool) : Prop :=
  exists k s, Runde w0 k s /\ Hit (true :: false :: s).

(** Startwort (vom leeren Band). *)
Definition start : list bool := [true].

End W.
