(** * Gruppe 1 (Holdouts 114, 367, 378): Durchlauf-Beschleunigung, Stufe 1

    Alle drei Maschinen sind dieselbe Tabelle (hier [tm], Tabelle von 114),
    umbenannt bzw. gespiegelt und in einem anderen Zustand gestartet.

    Das Durchlaufmodell ([zustand], [encode], [next]) ersetzt die Maschine durch
    ein Listensystem: das Band ist eine Liste aus Bits und Bloecken [011]^(n+1)
    (links vom Kopf) bzw. [100]^(n+1) (rechts vom Kopf). Ein Schritt von [next]
    ist genau eine von drei Regeln:
    - S1: C laeuft ueber einen Block [100]^(n+1) nach rechts,
    - S2: B oder D laeuft ueber einen Block [011]^(n+1) nach links
          (B und D wechseln sich je Block ab),
    - E : sonst ein einzelner TM-Schritt.
    [next z = None] genau dann, wenn die Maschine in [encode z] haelt.

    Hauptsaetze (je Original-String, vom leeren Band):
      halts (TM_from_str "...") c0 <-> erreicht_halt (start q)
    mit q = A (114), D (367), C (378).

    Dies entscheidet nichts ueber Halten; es ist eine bewiesene Umformulierung
    nach dem Vorbild von IsValidAcceleration in google-deepmind/cryptids. *)

From BusyCoq Require Import Individual62.
Require Import String Lia List PeanoNat.
Import ListNotations.
Set Default Goal Selector "!".

(** Die Tabelle von 114 (Referenz fuer das Modell). *)
Definition tm := Eval compute in (TM_from_str "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC").

(** ** Zustaende des Modells *)

(** [Bit s] ist eine einzelne Zelle; [Block n] steht fuer n+1 Woerter
    (links [011], rechts [100], jeweils in Bandrichtung). *)
Inductive stueck := Bit (s : Sym) | Block (n : nat).

(** Auf welcher Seite steht die Zelle unter dem Kopf: oberstes Stueck von
    [rs] (Kopf zeigt nach rechts, [l {{q}}> r]) oder von [ls] ([l <{{q}} r]). *)
Inductive seite := Li | Re.

Record zustand := Z { zq : Q; zs : seite; zls : list stueck; zrs : list stueck }.

(** Woerter vom Kopf aus gelesen (busycoq: [l <* xs] legt xs[0] neben den Kopf). *)
Definition wl : list Sym := [S1; S1; S0].   (* Band links: 0 1 1 *)
Definition wr : list Sym := [S1; S0; S0].   (* Band rechts: 1 0 0 *)

Fixpoint lenc (ls : list stueck) : side :=
  match ls with
  | [] => const S0
  | Bit s :: ls' => s >> lenc ls'
  | Block n :: ls' => wl^^(S n) *> lenc ls'
  end.

Fixpoint renc (rs : list stueck) : side :=
  match rs with
  | [] => const S0
  | Bit s :: rs' => s >> renc rs'
  | Block n :: rs' => wr^^(S n) *> renc rs'
  end.

Definition encode (z : zustand) : Q * tape :=
  match z with
  | Z q Re ls rs => lenc ls {{q}}> renc rs
  | Z q Li ls rs => lenc ls <{{q}} renc rs
  end.

(** Start: leeres Band, Zustand q. *)
Definition start (q : Q) : zustand := Z q Re [] [].

(** ** Hilfsfunktionen *)

(** Zelle am Kopf abnehmen (ein Block wird dafuer aufgeteilt). *)
Definition kopf_l (ls : list stueck) : Sym * list stueck :=
  match ls with
  | [] => (S0, [])
  | Bit s :: ls' => (s, ls')
  | Block O :: ls' => (S1, Bit S1 :: Bit S0 :: ls')
  | Block (S n) :: ls' => (S1, Bit S1 :: Bit S0 :: Block n :: ls')
  end.

Definition kopf_r (rs : list stueck) : Sym * list stueck :=
  match rs with
  | [] => (S0, [])
  | Bit s :: rs' => (s, rs')
  | Block O :: rs' => (S1, Bit S0 :: Bit S0 :: rs')
  | Block (S n) :: rs' => (S1, Bit S0 :: Bit S0 :: Block n :: rs')
  end.

(** Zelle ablegen; drei Bits [011] links bzw. [100] rechts werden zum Block. *)
Definition push_l (w : Sym) (ls : list stueck) : list stueck :=
  match w, ls with
  | S1, Bit S1 :: Bit S0 :: Block n :: ls' => Block (S n) :: ls'
  | S1, Bit S1 :: Bit S0 :: ls' => Block O :: ls'
  | _, _ => Bit w :: ls
  end.

Definition push_r (w : Sym) (rs : list stueck) : list stueck :=
  match w, rs with
  | S1, Bit S0 :: Bit S0 :: Block n :: rs' => Block (S n) :: rs'
  | S1, Bit S0 :: Bit S0 :: rs' => Block O :: rs'
  | _, _ => Bit w :: rs
  end.

(** Block ablegen, mit einem gleichen Block darunter verschmelzen. *)
Definition block_l (n : nat) (ls : list stueck) : list stueck :=
  match ls with
  | Block m :: ls' => Block (S (n + m)) :: ls'
  | _ => Block n :: ls
  end.

Definition block_r (n : nat) (rs : list stueck) : list stueck :=
  match rs with
  | Block m :: rs' => Block (S (n + m)) :: rs'
  | _ => Block n :: rs
  end.

Definition wechsel (q : Q) : Q :=
  match q with
  | B => D
  | D => B
  | _ => q
  end.

(** [wechseln k q]: k-mal B und D tauschen. *)
Fixpoint wechseln (k : nat) (q : Q) : Q :=
  match k with
  | O => q
  | S k => wechseln k (wechsel q)
  end.

(** Ein TM-Schritt auf der Zelle [s] am Kopf; [ls], [rs] ohne diese Zelle. *)
Definition einzel (q : Q) (s : Sym) (ls rs : list stueck) : option zustand :=
  match tm (q, s) with
  | None => None
  | Some (w, R, q') => Some (Z q' Re (push_l w ls) rs)
  | Some (w, L, q') => Some (Z q' Li ls (push_r w rs))
  end.

(** ** Die Schrittfunktion *)
Definition next (z : zustand) : option zustand :=
  match z with
  | Z C Re ls (Block n :: rs) => Some (Z C Re (block_l n ls) rs)                 (* S1 *)
  | Z B Li (Block n :: ls) rs => Some (Z (wechseln (S n) B) Li ls (block_r n rs)) (* S2 *)
  | Z D Li (Block n :: ls) rs => Some (Z (wechseln (S n) D) Li ls (block_r n rs)) (* S2 *)
  | Z q Re ls rs => let (s, rs') := kopf_r rs in einzel q s ls rs'               (* E *)
  | Z q Li ls rs => let (s, ls') := kopf_l ls in einzel q s ls' rs               (* E *)
  end.

(** Das Modell erreicht "Halt": wiederholtes Anwenden von [next] liefert [None]. *)
Inductive erreicht_halt : zustand -> Prop :=
  | eh_halt z : next z = None -> erreicht_halt z
  | eh_weiter z z' : next z = Some z' -> erreicht_halt z' -> erreicht_halt z.

(** ** Kodierung *)

Lemma const0_unfold : const S0 = S0 >> const S0.
Proof. apply const_unfold. Qed.

Lemma kopf_l_spec : forall ls,
  lenc ls = fst (kopf_l ls) >> lenc (snd (kopf_l ls)).
Proof.
  intros [| [s | [| n]] ls']; cbn; try reflexivity.
  apply const0_unfold.
Qed.

Lemma kopf_r_spec : forall rs,
  renc rs = fst (kopf_r rs) >> renc (snd (kopf_r rs)).
Proof.
  intros [| [s | [| n]] rs']; cbn; try reflexivity.
  apply const0_unfold.
Qed.

Lemma push_l_spec : forall w ls, lenc (push_l w ls) = w >> lenc ls.
Proof.
  intros [] ls; try reflexivity.
  destruct ls as [| [[] | ] [| [[] | ] [| [] ls'']]]; reflexivity.
Qed.

Lemma push_r_spec : forall w rs, renc (push_r w rs) = w >> renc rs.
Proof.
  intros [] rs; try reflexivity.
  destruct rs as [| [[] | ] [| [[] | ] [| [] rs'']]]; reflexivity.
Qed.

Lemma lpow_SS : forall {A} (xs : list A) n m,
  xs^^(S n) ++ xs^^(S m) = xs^^(S (S (n + m))).
Proof.
  intros A xs n m. rewrite <- lpow_add. f_equal. lia.
Qed.

Lemma block_l_spec : forall n ls, lenc (block_l n ls) = wl^^(S n) *> lenc ls.
Proof.
  intros n [| [s | m] ls']; try reflexivity.
  cbn [block_l lenc]. rewrite <- Str_app_assoc, lpow_SS. reflexivity.
Qed.

Lemma block_r_spec : forall n rs, renc (block_r n rs) = wr^^(S n) *> renc rs.
Proof.
  intros n [| [s | m] rs']; try reflexivity.
  cbn [block_r renc]. rewrite <- Str_app_assoc, lpow_SS. reflexivity.
Qed.

(** ** Durchlauf-Lemmata *)

Lemma s1_wort : forall l r,
  l {{C}}> wr *> r -[ tm ]->+ l <* wl {{C}}> r.
Proof. intros. unfold wr, wl. execute. Qed.

Lemma s1_alle : forall n l r,
  l {{C}}> wr^^n *> r -[ tm ]->* l <* wl^^n {{C}}> r.
Proof.
  induction n as [| n IH]; intros l r.
  - apply evstep_refl.
  - cbn [lpow]. rewrite !Str_app_assoc.
    eapply evstep_trans; [apply progress_evstep, s1_wort |].
    eapply evstep_trans; [apply IH |].
    rewrite <- Str_app_assoc, lpow_shift. apply evstep_refl.
Qed.

Lemma s1_lauf : forall n l r,
  l {{C}}> wr^^(S n) *> r -[ tm ]->+ l <* wl^^(S n) {{C}}> r.
Proof.
  intros n l r. cbn [lpow]. rewrite !Str_app_assoc.
  eapply progress_evstep_trans; [apply s1_wort |].
  eapply evstep_trans; [apply s1_alle |].
  rewrite <- Str_app_assoc, lpow_shift. apply evstep_refl.
Qed.

Lemma s2_wort_B : forall l r,
  l <* wl <{{B}} r -[ tm ]->+ l <{{D}} wr *> r.
Proof. intros. unfold wr, wl. execute. Qed.

Lemma s2_wort_D : forall l r,
  l <* wl <{{D}} r -[ tm ]->+ l <{{B}} wr *> r.
Proof. intros. unfold wr, wl. execute. Qed.

Lemma s2_wort : forall q l r, q = B \/ q = D ->
  l <* wl <{{q}} r -[ tm ]->+ l <{{wechsel q}} wr *> r.
Proof.
  intros q l r [-> | ->]; [apply s2_wort_B | apply s2_wort_D].
Qed.

Lemma wechsel_BD : forall q, q = B \/ q = D -> wechsel q = B \/ wechsel q = D.
Proof. intros q [-> | ->]; cbn; auto. Qed.

Lemma s2_alle : forall n q l r, q = B \/ q = D ->
  l <* wl^^n <{{q}} r -[ tm ]->* l <{{wechseln n q}} wr^^n *> r.
Proof.
  induction n as [| n IH]; intros q l r Hq.
  - apply evstep_refl.
  - cbn [lpow wechseln]. rewrite Str_app_assoc.
    eapply evstep_trans; [apply progress_evstep, s2_wort, Hq |].
    eapply evstep_trans; [apply IH, wechsel_BD, Hq |].
    rewrite <- Str_app_assoc, lpow_shift. apply evstep_refl.
Qed.

Lemma s2_lauf : forall n q l r, q = B \/ q = D ->
  l <* wl^^(S n) <{{q}} r -[ tm ]->+ l <{{wechseln (S n) q}} wr^^(S n) *> r.
Proof.
  intros n q l r Hq. cbn [lpow wechseln]. rewrite Str_app_assoc.
  eapply progress_evstep_trans; [apply s2_wort, Hq |].
  eapply evstep_trans; [apply s2_alle, wechsel_BD, Hq |].
  rewrite <- Str_app_assoc, lpow_shift. apply evstep_refl.
Qed.

(** ** Einzelschritt *)

Lemma einzel_re : forall q s ls rs z',
  einzel q s ls rs = Some z' ->
  q;; lenc ls {{s}} renc rs -[ tm ]->+ encode z'.
Proof.
  intros q s ls rs z' H. unfold einzel in H.
  destruct (tm (q, s)) as [[[w []] q'] |] eqn:Etm; try discriminate;
    injection H as <-; apply progress_base; cbn [encode].
  - rewrite push_r_spec. apply step_left. exact Etm.
  - rewrite push_l_spec. apply step_right. exact Etm.
Qed.

Lemma einzel_none : forall q s ls rs,
  einzel q s ls rs = None -> tm (q, s) = None.
Proof.
  intros q s ls rs H. unfold einzel in H.
  destruct (tm (q, s)) as [[[w []] q'] |]; congruence.
Qed.

Lemma encode_re : forall q ls rs,
  encode (Z q Re ls rs) =
  (q;; lenc ls {{fst (kopf_r rs)}} renc (snd (kopf_r rs))).
Proof.
  intros q ls rs. cbn [encode]. rewrite (kopf_r_spec rs). reflexivity.
Qed.

Lemma encode_li : forall q ls rs,
  encode (Z q Li ls rs) =
  (q;; lenc (snd (kopf_l ls)) {{fst (kopf_l ls)}} renc rs).
Proof.
  intros q ls rs. cbn [encode]. rewrite (kopf_l_spec ls). reflexivity.
Qed.

(** ** Korrektheit von [next] *)

Lemma next_re : forall q ls rs z',
  (let (s, rs') := kopf_r rs in einzel q s ls rs') = Some z' ->
  encode (Z q Re ls rs) -[ tm ]->+ encode z'.
Proof.
  intros q ls rs z' H. rewrite encode_re.
  destruct (kopf_r rs) as [s rs'] eqn:E. cbn [fst snd].
  apply einzel_re, H.
Qed.

Lemma next_li : forall q ls rs z',
  (let (s, ls') := kopf_l ls in einzel q s ls' rs) = Some z' ->
  encode (Z q Li ls rs) -[ tm ]->+ encode z'.
Proof.
  intros q ls rs z' H. rewrite encode_li.
  destruct (kopf_l ls) as [s ls'] eqn:E. cbn [fst snd].
  apply einzel_re, H.
Qed.

Lemma schritt_some : forall z z', next z = Some z' -> encode z -[ tm ]->+ encode z'.
Proof.
  intros [q [] ls rs] z' H.
  - (* Li *)
    destruct q; try (apply next_li; exact H);
    (destruct ls as [| [s | n] ls']; [apply next_li; exact H | apply next_li; exact H |]);
    cbn in H; injection H as <-; cbn [encode lenc];
    rewrite block_r_spec; apply s2_lauf; auto.
  - (* Re *)
    destruct q; try (apply next_re; exact H).
    destruct rs as [| [s | n] rs']; try (apply next_re; exact H).
    cbn in H; injection H as <-; cbn [encode renc].
    rewrite block_l_spec. apply s1_lauf.
Qed.

Lemma schritt_none : forall z, next z = None -> halted tm (encode z).
Proof.
  intros [q [] ls rs] H.
  - rewrite encode_li. cbn [halted].
    assert (H' : (let (s, ls') := kopf_l ls in einzel q s ls' rs) = None).
    { destruct q; try exact H; destruct ls as [| [s | n] ls']; try exact H; discriminate. }
    destruct (kopf_l ls) as [s ls']. cbn [fst snd]. apply (einzel_none _ _ _ _ H').
  - rewrite encode_re. cbn [halted].
    assert (H' : (let (s, rs') := kopf_r rs in einzel q s ls rs') = None).
    { destruct q; try exact H; destruct rs as [| [s | n] rs']; try exact H; discriminate. }
    destruct (kopf_r rs) as [s rs']. cbn [fst snd]. apply (einzel_none _ _ _ _ H').
Qed.

(** ** Allgemeiner Satz: Halten der Maschine = Halt des Modells *)

Theorem beschleunigung : forall z, halts tm (encode z) <-> erreicht_halt z.
Proof.
  intros z. split.
  - intros [k Hk]. revert z Hk.
    induction k as [k IH] using strong_induction. intros z Hk.
    destruct (next z) as [z' |] eqn:En.
    + apply (eh_weiter z z' En).
      apply schritt_some, progress_multistep in En. destruct En as [n Hn].
      assert (Hle : S n <= k) by (eapply within_halt; eassumption).
      apply (IH (k - S n)); [lia |].
      eapply preceeds_halt; eassumption.
    + apply eh_halt, En.
  - intros H. induction H as [z En | z z' En _ IH].
    + apply halted_halts, schritt_none, En.
    + apply schritt_some, progress_multistep in En. destruct En as [n Hn].
      eapply halts_multistep; eassumption.
Qed.

Lemma encode_start : forall q, encode (start q) = (q;; tape0).
Proof. reflexivity. Qed.

(** ** Die drei Starts *)

(** 367 ist die Tabelle von 114, umbenannt: A..F von 114 = E C B A D F von 367. *)
Definition tm367 := Eval compute in (TM_from_str "1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB").
Definition f367 (q : Q) : Q :=
  match q with A => E | B => C | C => B | D => A | E => D | F => F end.

Lemma perm367 : Perm tm tm367 f367.
Proof.
  split.
  - intros q s; destruct q, s; cbn; congruence.
  - intros q s s' d q' H; destruct q, s; cbn in H; try discriminate;
      inversion H; subst; reflexivity.
Qed.

(** 378 ist das Spiegelbild der Tabelle von 114, umbenannt:
    A..F von 114 = F D A B C E von 378. *)
Definition tm378 := Eval compute in (TM_from_str "1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---").
Definition f378 (q : Q) : Q :=
  match q with A => F | B => D | C => A | D => B | E => C | F => E end.

Lemma perm378 : Perm (flip tm) tm378 f378.
Proof.
  split.
  - intros q s H; destruct q, s; compute in H |- *; congruence.
  - intros q s s' d q' H; destruct q, s; compute in H; try discriminate;
      inversion H; subst; reflexivity.
Qed.

(** Doppeltes Spiegeln ohne funktionale Extensionalitaet: punktweise gleich. *)
Lemma perm_flipflip : Perm (flip (flip tm)) tm (fun q => q).
Proof.
  split.
  - intros q s H; destruct q, s; compute in H |- *; congruence.
  - intros q s s' d q' H; destruct q, s; compute in H; try discriminate;
      inversion H; subst; reflexivity.
Qed.

Lemma halts_flip_iff : forall q,
  halts tm (q;; tape0) <-> halts (flip tm) (q;; tape0).
Proof.
  intros q. split.
  - intros H. exact (flip_halts tm (q;; tape0) H).
  - intros H. apply (flip_halts (flip tm) (q;; tape0)) in H.
    exact (perm_halts _ _ _ q tape0 perm_flipflip H).
Qed.

(** ** Hauptsaetze *)

Theorem gruppe1_114 :
  halts (TM_from_str "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC") c0 <-> erreicht_halt (start A).
Proof.
  rewrite <- beschleunigung, encode_start. reflexivity.
Qed.

Theorem gruppe1_367 :
  halts (TM_from_str "1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB") c0 <-> erreicht_halt (start D).
Proof.
  rewrite <- beschleunigung, encode_start.
  change (TM_from_str "1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB") with tm367.
  change c0 with (f367 D;; tape0).
  split.
  - apply (perm_halts' _ _ _ D tape0 perm367).
  - apply (perm_halts _ _ _ D tape0 perm367).
Qed.

Theorem gruppe1_378 :
  halts (TM_from_str "1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---") c0 <-> erreicht_halt (start C).
Proof.
  rewrite <- beschleunigung, encode_start, halts_flip_iff.
  change (TM_from_str "1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---") with tm378.
  change c0 with (f378 C;; tape0).
  split.
  - apply (perm_halts' _ _ _ C tape0 perm378).
  - apply (perm_halts _ _ _ C tape0 perm378).
Qed.


(** * Stufe 2a: Regel F (Fressrunde)

    Listenform (Teil 1): an einem Rechts-Rekord in C steht ganz rechts das Element x, daneben y,
    getrennt durch [|]; eine Fressrunde macht daraus x+4 | y-1. Im Modell: oben auf dem linken
    Stapel liegt [011]^x, dann eine 1, dann [011]^(y+1), dann eine 1, darunter der Rest; rechts ist
    das Band leer. Bis 10^8 Schritte ist x bei allen Fressrunden ungerade (alle drei Starts);
    hier x = 2k+1, also [Block (k+k)], und y = b+1, also [Block (S b)]. *)

(** [erreicht z z']: wiederholtes Anwenden von [next] fuehrt von z nach z'. *)
Inductive erreicht : zustand -> zustand -> Prop :=
  | er_refl z : erreicht z z
  | er_schritt z z' z'' : next z = Some z' -> erreicht z' z'' -> erreicht z z''.

Lemma erreicht_trans : forall z1 z2 z3, erreicht z1 z2 -> erreicht z2 z3 -> erreicht z1 z3.
Proof.
  intros z1 z2 z3 H12 H23. induction H12 as [z | z z' z'' En _ IH]; [exact H23 |].
  eapply er_schritt; [exact En | apply IH, H23].
Qed.

(** Wer z' erreicht, erreicht "Halt" genau dann, wenn z' es tut. *)
Lemma erreicht_halt_erreicht : forall z z', erreicht z z' ->
  (erreicht_halt z <-> erreicht_halt z').
Proof.
  intros z z' H. induction H as [z | z z' z'' En _ IH]; [tauto |].
  rewrite <- IH. split.
  - intros Hh. inversion Hh as [? Hn | ? z2 Hn Hh']; subst; congruence.
  - intros Hh. eapply eh_weiter; eassumption.
Qed.

Lemma wechsel_wechsel : forall q, wechsel (wechsel q) = q.
Proof. intros []; reflexivity. Qed.

Lemma wechseln_SS : forall n q, wechseln (S (S n)) q = wechseln n q.
Proof. intros n q. cbn [wechseln]. rewrite wechsel_wechsel. reflexivity. Qed.

Lemma wechseln_gerade : forall k q, wechseln (k + k) q = q.
Proof.
  induction k as [| k IH]; intros q; [reflexivity |].
  replace (S k + S k) with (S (S (k + k))) by lia. rewrite wechseln_SS. apply IH.
Qed.

(** Ein Schritt von [next], symbolisch ausgerechnet. *)
Ltac schritt :=
  eapply er_schritt;
  [ cbn; repeat (rewrite ?Nat.add_0_r, ?Nat.add_succ_r, ?wechseln_SS, ?wechseln_gerade); reflexivity
  | ].

(** Regel F: eine Fressrunde, 25 Schritte von [next]. *)
Lemma regel_F : forall k b rest,
  erreicht (Z C Re (Block (k + k) :: Bit S1 :: Block (S b) :: Bit S1 :: rest) [])
           (Z C Re (Block (S (S (S (S (k + k))))) :: Bit S1 :: Block b :: Bit S1 :: rest) []).
Proof.
  intros k b rest. do 25 schritt. apply er_refl.
Qed.

(** Regel F, m-mal hintereinander: x | y wird zu x+4m | y-m. *)
Lemma regel_F_oft : forall m k b rest,
  erreicht (Z C Re (Block (k + k) :: Bit S1 :: Block (m + b) :: Bit S1 :: rest) [])
           (Z C Re (Block ((k + 2 * m) + (k + 2 * m)) :: Bit S1 :: Block b :: Bit S1 :: rest) []).
Proof.
  induction m as [| m IH]; intros k b rest.
  - replace (k + 2 * 0) with k by lia. apply er_refl.
  - eapply erreicht_trans; [apply regel_F |].
    replace (S (S (S (S (k + k))))) with (S (S k) + S (S k)) by lia.
    replace (k + 2 * S m) with (S (S k) + 2 * m) by lia.
    apply IH.
Qed.
