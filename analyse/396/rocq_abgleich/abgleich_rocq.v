(** Abgleich: WX.runden aus rocq/rueckfuehrung_396.v auswerten (kein Beweis). Erzeugt von abgleich.py. *)
From BusyCoq Require Import Individual62.
From BusyCoq Require Import R396.
From Coq Require Import Lists.List. Import ListNotations.
Definition bits (w : list bool) : list nat := map (fun x : bool => if x then S O else O) w.
Definition kodiere (e : WX.ergebnis) : list nat :=
  match e with WX.Wort s => bits s | WX.Treffer j => [7; j] | WX.Grenze => [9] end.
Definition spur (k : nat) (s : list bool) : list (list nat) :=
  map (fun i => kodiere (WX.runden 5000 i s)) (seq O (S k)).
Set Printing Width 1000000.
Eval vm_compute in spur 35 W.start.
Eval vm_compute in spur 15 [false; false; false; false; false; false; false; false; true; false; true; true; true; false; true; true].
Eval vm_compute in spur 15 [false; false; false; false; false; true; false; true; false; false; true; true; false; false; false].
Eval vm_compute in spur 15 [true; false; true; true; false; false; false; false; false].
Eval vm_compute in spur 15 [false; false; false; true; true; false].
Eval vm_compute in spur 15 [false; true; false; false; false; true; true].
Eval vm_compute in spur 15 [true; true; true; false; false; true; false].
Eval vm_compute in spur 15 [false; false; true; true; false; true; true; false; false].
Eval vm_compute in spur 15 [false; false; false; false; false; true; false; false; false; true; true; true; false].
Eval vm_compute in spur 15 [true; false; true; true; false; true; true; true; false; true; true; true; false].
Eval vm_compute in spur 15 [true; true; true; false].
Eval vm_compute in spur 15 [false; false; true; true; true; false; false; false; false].
Eval vm_compute in spur 15 [false; true; true; false; false; false; false; false; true; true; false; true; false; false; false].
Eval vm_compute in spur 15 [false; true; false; true; false; false; false; false; true; true; false; false; false; false; false; false].
Eval vm_compute in spur 15 [false; false; true; true; true; false; false; false; false; false; true; false; false].
Eval vm_compute in spur 15 [false; true; true; false; false; true; false; true; false; false; true; false; true; true; true].
Eval vm_compute in spur 15 [false; false; false; false; false; false; false; true; true; false; true; false; false; true; false].
Eval vm_compute in spur 15 [false; true; true; true; false; false; false; false; false].
Eval vm_compute in spur 15 [true; false; false; false; true; false; false; true; false; true; true; false; false; false].
Eval vm_compute in spur 15 [false; false; true; true; true; false; false; false; true; true; true; true; false; false; false; true].
Eval vm_compute in spur 15 [true; true; true; true; false; false; false].
Eval vm_compute in spur 15 [false; true; false; true; true; false; false; true; false].
Eval vm_compute in spur 15 [true; false; true; false; true; false; false; true; true; false; false; false; true].
Eval vm_compute in spur 15 [false; true; true; false; true; true; false; true; false; true; false; true; true].
Eval vm_compute in spur 15 [false; true; true; false; false; false; false; false; false; false].
Eval vm_compute in spur 15 [true; true; true; false; true].
Eval vm_compute in spur 15 [false; false; false; false; false; true; true; false; false; false; true].
Eval vm_compute in spur 15 [true; false; false; false; false; true; true; false; false; false; false; false].
Eval vm_compute in spur 15 [true; true; true; true; false; true].
Eval vm_compute in spur 15 [true; false; false; false; true; true; false; false; false; true; false; false].
Eval vm_compute in spur 15 [false; true; true; true; false; true; false; false; false; false].
Eval vm_compute in spur 15 [true; true; false; false; true; true].
Eval vm_compute in spur 15 [false; true; true].
Eval vm_compute in spur 15 [true; false; false; true; false; false; false; false; true; true; true; false].
Eval vm_compute in spur 15 [true; false; false; false; true; false; false; true; false; false; false; false; true; true; false; true].
Eval vm_compute in spur 15 [false; false; false; false; true; true].
Eval vm_compute in spur 15 [true; true; true; true].
Eval vm_compute in spur 15 [false; true; true; true; false; false; true; true; false; false; true; false; false; true; false].
Eval vm_compute in spur 15 [false; false; true; true; false; true; true; false; false; true; false; false; true; true; false; true].
Eval vm_compute in spur 15 [false; true; false; true; false; false; true; false; false; true; true; false; false; true; true].
Eval vm_compute in spur 15 [false; false; true; true; false; true; false; false; true; false; false; true; false; false; false; true].
