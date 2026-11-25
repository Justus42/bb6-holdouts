(** Abgleich Stufe 2a: [next] aus rocq/gruppe1_durchlauf.v auswerten (kein Beweis).
    Gibt fuer jeden Start die ersten K Modellzustaende als Zahlenlisten aus:
    [q; seite; Laenge ls; ls...; rs...] mit q = 0..5 (A..F), seite 0 = Li, 1 = Re,
    Stueck: Bit S0 = 0, Bit S1 = 1, Block n = n+2 (Block n steht fuer n+1 Woerter).
    Stapel von oben (Kopf) nach unten. Am Ende steht 99, wenn [next] None lieferte. *)
From BusyCoq Require Import Individual62.
From BusyCoq Require Import gruppe1_durchlauf.
Require Import List. Import ListNotations.

Definition qn (q : Q) : nat := match q with A => 0 | B => 1 | C => 2 | D => 3 | E => 4 | F => 5 end.
Definition sn (x : stueck) : nat := match x with Bit S0 => 0 | Bit S1 => 1 | Block n => n + 2 end.
Definition kodiere (z : zustand) : list nat :=
  match z with
  | Z q si ls rs =>
      cons (qn q) (cons (match si with Li => O | Re => S O end)
        (cons (List.length ls) (List.app (List.map sn ls) (List.map sn rs))))
  end.

Fixpoint spur (k : nat) (z : zustand) : list (list nat) :=
  match k with
  | O => [kodiere z]
  | S k' => kodiere z :: match next z with Some z' => spur k' z' | None => [[99]] end
  end.

Set Printing Width 1000000.
Eval vm_compute in spur 10000 (start A).
Eval vm_compute in spur 10000 (start D).
Eval vm_compute in spur 10000 (start C).
