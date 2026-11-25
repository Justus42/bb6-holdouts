(** * Holdout 396: Rueckfuehrung auf ein Wortsystem

    Maschine: 1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---

    Hauptsatz (vom leeren Band):
      halts tm c0 <-> W.trifft111 W.start
    396 haelt genau dann, wenn im Wortsystem [W] ab dem Startwort [1] in einer
    Runde ein Besuch auf den Block 111 trifft. Das entscheidet nicht, ob 396 haelt;
    es ist eine bewiesene Umformulierung.

    Aufbau:
    - Modul [W]: das Wortsystem auf endlichen Woertern, ohne Bezug auf die
      Maschine (Besuch ergibt Wort, Besuch trifft 111, Runde k).
    - Modul [WX]: ausfuehrbare Fassung mit Schrittgrenze, als gleichwertig bewiesen.
    - Modul [WT]: jeder Besuch endet oder trifft 111 (Totalitaet).
    - Band-Teil: dreizehn Lemmata ueber die Maschine fuer beliebige Bandreste,
      dann der Hauptsatz.

    Herkunft des Geruests: busycoq PR #59 (alkrssve, offen, Commit f23281d,
    Datei verify/M_1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD1RF_0RCHHH.v), Beweis fuer
    88/312/449. Daraus uebernommen: die Definitionen [sym], [lw], [Zinf],
    [Zinf_unfold], die Bandformen von Besuch und Halt ([BandVis], [BandHalt],
    [LE], dort [Vis], [HV], [LE]), die Form von elf Annahmen (vis_0, vis_H,
    vis_G, vis_L, hv_H, hv_G, hv_L1, hv_L2, round_step, round_halt, blank_start)
    und die Taktiken [run_to], [run_to2], [run_halt], [run_halt1], [law].
    Neu: die Annahmen vis_K (1011 -> 0001) und hv_111 an Stelle von hv_1011,
    alle Annahmen als Lemmata fuer 396 statt als Hypothesen, das Wortsystem,
    die Totalitaet und beide Richtungen des Hauptsatzes. Der Rechenteil von
    PR #59 (check 161210) wird nicht benutzt. *)

From BusyCoq Require Import Individual62.
From Coq Require Import String Lists.List Lia Bool PeanoNat Wf_nat.
Import ListNotations.
Set Default Goal Selector "!".

(** ** Das Wortsystem (ohne Maschine) *)

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

(** ** Ausfuehrbare Fassung mit Schrittgrenze *)

Module WX.
Import W.

(** Ein Besuch in einem Schritt; [rec] macht die Teilbesuche weiter rechts. *)
Definition schritt (rec : list bool -> option (option (list bool))) (w : list bool)
  : option (option (list bool)) :=
  if negb (z w) then Some (Some (true :: tl w))
  else if z (tl w) && z (tl (tl w)) then Some None
  else if negb (z (tl (tl w))) then
    match rec (tl (tl (tl w))) with
    | Some (Some y) => Some (Some (false :: false :: false :: y))
    | e => e
    end
  else if negb (z (tl (tl (tl w)))) then
    match rec (tl (tl (tl (tl w)))) with
    | Some (Some y1) =>
        match rec y1 with
        | Some (Some y2) => Some (Some (true :: false :: true :: false :: y2))
        | e => e
        end
    | e => e
    end
  else Some (Some (false :: false :: false :: true :: tl (tl (tl (tl w))))).

(** [besuch f w]: [Some (Some y)] = Besuch endet mit y, [Some None] = trifft 111,
    [None] = Schrittgrenze f (Rekursionstiefe) erreicht. *)
Fixpoint besuch (f : nat) (w : list bool) : option (option (list bool)) :=
  match f with
  | O => None
  | S f => schritt (besuch f) w
  end.

Lemma besuch_S : forall f w, besuch (S f) w = schritt (besuch f) w.
Proof. reflexivity. Qed.

Inductive ergebnis := Wort (s : list bool) | Treffer (k : nat) | Grenze.

(** [runden f k w0]: k Runden ab w0, jeder Besuch mit Schrittgrenze f.
    [Treffer j]: der Besuch in Runde j+1 (auf 1 0 s_j) trifft 111. *)
Fixpoint runden (f k : nat) (w0 : list bool) : ergebnis :=
  match k with
  | O => Wort w0
  | S k' =>
    match runden f k' w0 with
    | Wort s =>
        match besuch f (true :: false :: s) with
        | Some (Some s') => Wort s'
        | Some None => Treffer k'
        | None => Grenze
        end
    | e => e
    end
  end.

Lemma besuch_sound : forall f w,
  (forall y, besuch f w = Some (Some y) -> Vis w y) /\
  (besuch f w = Some None -> Hit w).
Proof.
  induction f as [|f IH]; intros w; [split; intros; discriminate|].
  rewrite besuch_S. unfold schritt.
  destruct (z w) eqn:Ea; cbv beta iota delta [negb].
  2:{ split; [intros y H|intros H; discriminate]. inversion H; subst. apply V_0. exact Ea. }
  destruct (z (tl w)) eqn:Eb, (z (tl (tl w))) eqn:Ec; cbv beta iota delta [andb negb].
  - split; [intros y H; discriminate|]. intros _. apply H_111; assumption.
  - destruct (IH (tl (tl (tl w)))) as [IH1 IH2].
    destruct (besuch f (tl (tl (tl w)))) as [[y|]|] eqn:E.
    + split; [|intros H; discriminate]. intros y0 H. inversion H; subst.
      apply V_110; auto.
    + split; [intros y0 H; discriminate|]. intros _. apply H_110; auto.
    + split; [intros y0 H|intros H]; discriminate.
  - destruct (z (tl (tl (tl w)))) eqn:Ed; cbv beta iota delta [negb].
    + split; [|intros H; discriminate]. intros y H. inversion H; subst.
      apply V_1011; assumption.
    + destruct (IH (tl (tl (tl (tl w))))) as [IH1 IH2].
      destruct (besuch f (tl (tl (tl (tl w))))) as [[y1|]|] eqn:E1.
      * destruct (IH y1) as [IH3 IH4].
        destruct (besuch f y1) as [[y2|]|] eqn:E2.
        -- split; [|intros H; discriminate]. intros y H. inversion H; subst.
           eapply V_1010; eauto.
        -- split; [intros y H; discriminate|]. intros _. eapply H_1010b; eauto.
        -- split; [intros y H|intros H]; discriminate.
      * split; [intros y H; discriminate|]. intros _. apply H_1010a; auto.
      * split; [intros y H|intros H]; discriminate.
  - destruct (IH (tl (tl (tl w)))) as [IH1 IH2].
    destruct (besuch f (tl (tl (tl w)))) as [[y|]|] eqn:E.
    + split; [|intros H; discriminate]. intros y0 H. inversion H; subst.
      apply V_100; auto.
    + split; [intros y0 H; discriminate|]. intros _. apply H_100; auto.
    + split; [intros y0 H|intros H]; discriminate.
Qed.

Lemma besuch_mono1 : forall f w e, besuch f w = Some e -> besuch (S f) w = Some e.
Proof.
  induction f as [|f IH]; intros w e H; [discriminate|].
  rewrite besuch_S in H. rewrite besuch_S. unfold schritt in H |- *.
  destruct (negb (z w)); [exact H|].
  destruct (z (tl w) && z (tl (tl w))); [exact H|].
  destruct (negb (z (tl (tl w)))).
  - destruct (besuch f (tl (tl (tl w)))) as [e1|] eqn:E1; [|discriminate].
    rewrite (IH _ _ E1). exact H.
  - destruct (negb (z (tl (tl (tl w))))); [|exact H].
    destruct (besuch f (tl (tl (tl (tl w))))) as [e1|] eqn:E1; [|discriminate].
    rewrite (IH _ _ E1).
    destruct e1 as [y1|]; [|exact H].
    destruct (besuch f y1) as [e2|] eqn:E2; [|discriminate].
    rewrite (IH _ _ E2). exact H.
Qed.

Lemma besuch_mono : forall f g w e, f <= g -> besuch f w = Some e -> besuch g w = Some e.
Proof.
  intros f g w e Hle. induction Hle; intros H; [exact H|]. apply besuch_mono1. auto.
Qed.

Ltac schritt_auf E := rewrite besuch_S; unfold schritt; rewrite E; cbv beta iota delta [andb negb].

Lemma besuch_vis : forall w y, Vis w y -> exists f, besuch f w = Some (Some y).
Proof.
  induction 1 as [w Ea|w y Ea Eb Ec _ [f IH]|w y Ea Eb Ec _ [f IH]
                 |w y1 y2 Ea Eb Ec Ed _ [f1 IH1] _ [f2 IH2]|w Ea Eb Ec Ed].
  - exists (S O). rewrite besuch_S. unfold schritt. rewrite Ea. reflexivity.
  - exists (S f). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec.
    cbv beta iota delta [andb negb]. rewrite IH. reflexivity.
  - exists (S f). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec.
    cbv beta iota delta [andb negb]. rewrite IH. reflexivity.
  - exists (S (f1 + f2)). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec, Ed.
    cbv beta iota delta [andb negb].
    rewrite (besuch_mono f1 (f1 + f2) _ _ ltac:(lia) IH1).
    rewrite (besuch_mono f2 (f1 + f2) _ _ ltac:(lia) IH2). reflexivity.
  - exists (S O). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec, Ed. reflexivity.
Qed.

Lemma besuch_hit : forall w, Hit w -> exists f, besuch f w = Some None.
Proof.
  induction 1 as [w Ea Eb Ec|w Ea Eb Ec _ [f IH]|w Ea Eb Ec _ [f IH]
                 |w Ea Eb Ec Ed _ [f IH]|w y1 Ea Eb Ec Ed Hv _ [f2 IH2]].
  - exists (S O). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec. reflexivity.
  - exists (S f). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec.
    cbv beta iota delta [andb negb]. rewrite IH. reflexivity.
  - exists (S f). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec.
    cbv beta iota delta [andb negb]. rewrite IH. reflexivity.
  - exists (S f). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec, Ed.
    cbv beta iota delta [andb negb]. rewrite IH. reflexivity.
  - destruct (besuch_vis _ _ Hv) as [f1 IH1].
    exists (S (f1 + f2)). rewrite besuch_S. unfold schritt. rewrite Ea, Eb, Ec, Ed.
    cbv beta iota delta [andb negb].
    rewrite (besuch_mono f1 (f1 + f2) _ _ ltac:(lia) IH1).
    rewrite (besuch_mono f2 (f1 + f2) _ _ ltac:(lia) IH2). reflexivity.
Qed.

Lemma runden_mono1 : forall f k w0, runden f k w0 <> Grenze ->
  runden (S f) k w0 = runden f k w0.
Proof.
  intros f k w0. induction k as [|k IH]; intros H; [reflexivity|].
  cbn [runden] in H |- *.
  destruct (runden f k w0) as [s|j|] eqn:E.
  - rewrite (IH ltac:(discriminate)). cbv beta iota.
    destruct (besuch f (true :: false :: s)) as [r|] eqn:B; [|contradiction].
    rewrite (besuch_mono1 _ _ _ B). reflexivity.
  - rewrite (IH ltac:(discriminate)). reflexivity.
  - contradiction.
Qed.

Lemma runden_mono : forall f g k w0, f <= g -> runden f k w0 <> Grenze ->
  runden g k w0 = runden f k w0.
Proof.
  intros f g k w0 Hle H. induction Hle as [|g Hle IH]; [reflexivity|].
  rewrite runden_mono1; [exact IH|]. rewrite IH. exact H.
Qed.

(** Gleichwertigkeit: was die ausfuehrbare Fassung liefert, gilt im Wortsystem ... *)
Theorem runden_korrekt : forall f k w0,
  (forall s, runden f k w0 = Wort s -> Runde w0 k s) /\
  (forall j, runden f k w0 = Treffer j -> exists s, Runde w0 j s /\ Hit (true :: false :: s)).
Proof.
  intros f k w0. induction k as [|k [IH1 IH2]].
  - split; intros x H; cbn in H; [inversion H; subst; constructor|discriminate].
  - cbn [runden]. destruct (runden f k w0) as [s|j|] eqn:E; cbv beta iota.
    + destruct (besuch_sound f (true :: false :: s)) as [B1 B2].
      destruct (besuch f (true :: false :: s)) as [[s'|]|] eqn:B.
      * split; intros x H; [|discriminate]. inversion H; subst.
        eapply R_S; [apply IH1; reflexivity|apply B1; reflexivity].
      * split; intros x H; [discriminate|]. inversion H; subst.
        exists s. split; [apply IH1; reflexivity|apply B2; reflexivity].
      * split; intros x H; discriminate.
    + split; intros x H; [discriminate|]. apply IH2. exact H.
    + split; intros x H; discriminate.
Qed.

(** ... und mit genuegend grosser Schrittgrenze liefert sie alles, was im
    Wortsystem gilt. *)
Theorem runden_vollstaendig : forall w0 k s, Runde w0 k s ->
  exists f, runden f k w0 = Wort s.
Proof.
  intros w0 k s R. induction R as [|k s s' R [f IH] Hv].
  - exists O. reflexivity.
  - destruct (besuch_vis _ _ Hv) as [g B].
    exists (f + g). cbn [runden].
    rewrite (runden_mono f (f + g) k w0 ltac:(lia) ltac:(rewrite IH; discriminate)), IH.
    cbv beta iota.
    rewrite (besuch_mono g (f + g) _ _ ltac:(lia) B). reflexivity.
Qed.

Theorem trifft111_iff_runden : forall w0,
  trifft111 w0 <-> exists f k j, runden f k w0 = Treffer j.
Proof.
  intros w0. split.
  - intros [k [s [R H]]].
    destruct (runden_vollstaendig _ _ _ R) as [f E].
    destruct (besuch_hit _ H) as [g B].
    exists (f + g), (S k), k. cbn [runden].
    rewrite (runden_mono f (f + g) k w0 ltac:(lia) ltac:(rewrite E; discriminate)), E.
    cbv beta iota.
    rewrite (besuch_mono g (f + g) _ _ ltac:(lia) B). reflexivity.
  - intros [f [k [j E]]]. destruct (runden_korrekt f k w0) as [_ K].
    destruct (K j E) as [s [R H]]. exists j, s. auto.
Qed.

End WX.

(** ** Jeder Besuch endet oder trifft 111 *)

Module WT.
Import W.

(** n Besuche nacheinander *)
Inductive VS : nat -> list bool -> list bool -> Prop :=
  | VS_0 : forall w, VS O w w
  | VS_S : forall n w w1 w2, Vis w w1 -> VS n w1 w2 -> VS (S n) w w2.

(** [Tot n w]: von n Besuchen nacheinander trifft einer 111, oder alle enden. *)
Definition Tot (n : nat) (w : list bool) : Prop :=
  (exists k wk, k < n /\ VS k w wk /\ Hit wk) \/ (exists w', VS n w w').

Lemma Tot_0 : forall w, Tot O w.
Proof. intros w. right. exists w. constructor. Qed.

Lemma Tot_hit : forall n w, Hit w -> Tot (S n) w.
Proof. intros n w H. left. exists O, w. repeat split; [lia|constructor|exact H]. Qed.

Lemma Tot_vis : forall n w w1, Vis w w1 -> Tot n w1 -> Tot (S n) w.
Proof.
  intros n w w1 H [[k [wk [Hk [HV HH]]]]|[w' HV]].
  - left. exists (S k), wk. repeat split; [lia|econstructor; eauto|exact HH].
  - right. exists w'. econstructor; eauto.
Qed.

Lemma Tot_inv : forall n w, Tot (S n) w -> Hit w \/ exists w1, Vis w w1 /\ Tot n w1.
Proof.
  intros n w [[k [wk [Hk [HV HH]]]]|[w' HV]].
  - destruct k as [|k].
    + inversion HV; subst. left. exact HH.
    + inversion HV as [|k' w0 w1 w2 Hv Hr]; subst. right. exists w1. split; [exact Hv|].
      left. exists k, wk. repeat split; [lia|exact Hr|exact HH].
  - inversion HV as [|k' w0 w1 w2 Hv Hr]; subst. right. exists w1. split; [exact Hv|].
    right. exists w'. exact Hr.
Qed.

Lemma tot_000 : forall m y, Tot m y ->
  Tot (2 * m) (false :: false :: false :: y) /\ Tot (S (2 * m)) (false :: false :: false :: y).
Proof.
  induction m as [|m IH]; intros y H.
  - split; [apply Tot_0|].
    eapply Tot_vis; [apply V_0; reflexivity|apply Tot_0].
  - replace (2 * S m) with (S (S (2 * m))) by lia.
    destruct (Tot_inv _ _ H) as [Hh|[y1 [Hv Ht]]].
    + assert (Hit (true :: false :: false :: y)) by (apply H_100; [reflexivity..|exact Hh]).
      split; (eapply Tot_vis; [apply V_0; reflexivity|apply Tot_hit; exact H0]).
    + destruct (IH y1 Ht) as [T1 T2].
      assert (Vis (true :: false :: false :: y) (false :: false :: false :: y1))
        by (apply V_100; [reflexivity..|exact Hv]).
      split; (eapply Tot_vis; [apply V_0; reflexivity|eapply Tot_vis; [exact H0|]]); assumption.
Qed.

Lemma tot_1b0 : forall w m,
  z w = true -> z (tl (tl w)) = false -> Tot (S m) (tl (tl (tl w))) ->
  Tot (S (2 * m)) w /\ Tot (S (S (2 * m))) w.
Proof.
  intros w m Ea Ec H.
  destruct (Tot_inv _ _ H) as [Hh|[x1 [Hv Ht]]].
  - assert (Hit w) by (destruct (z (tl w)) eqn:Eb; [apply H_110|apply H_100]; auto).
    split; apply Tot_hit; exact H0.
  - destruct (tot_000 m x1 Ht) as [T1 T2].
    assert (Vis w (false :: false :: false :: x1))
      by (destruct (z (tl w)) eqn:Eb; [apply V_110|apply V_100]; auto).
    split; eapply Tot_vis; eauto.
Qed.

Lemma tot_1010 : forall n w,
  z w = true -> z (tl w) = false -> z (tl (tl w)) = true -> z (tl (tl (tl w))) = false ->
  Tot (2 * n) (tl (tl (tl (tl w)))) -> Tot n w.
Proof.
  induction n as [|n IH]; intros w Ea Eb Ec Ed H; [apply Tot_0|].
  replace (2 * S n) with (S (S (2 * n))) in H by lia.
  destruct (Tot_inv _ _ H) as [Hh|[x1 [Hv1 Ht1]]].
  - apply Tot_hit. apply H_1010a; auto.
  - destruct (Tot_inv _ _ Ht1) as [Hh|[x2 [Hv2 Ht2]]].
    + apply Tot_hit. eapply H_1010b; eauto.
    + eapply Tot_vis; [eapply V_1010; eauto|].
      apply IH; [reflexivity..|exact Ht2].
Qed.

Lemma gerade_oder_ungerade : forall n, exists m, n = 2 * m \/ n = S (2 * m).
Proof.
  intros n. destruct (Nat.Even_or_Odd n) as [[m Hm]|[m Hm]]; exists m; lia.
Qed.

Lemma tot_nil : forall n, Tot n [].
Proof.
  intros n. induction n as [n IH] using lt_wf_ind.
  destruct n as [|n]; [apply Tot_0|].
  eapply Tot_vis; [apply V_0; reflexivity|]. cbn [tl].
  destruct n as [|n]; [apply Tot_0|].
  destruct (gerade_oder_ungerade n) as [m [Hm|Hm]]; subst n.
  - destruct (tot_1b0 [true] m eq_refl eq_refl (IH (S m) ltac:(lia))) as [T1 _]. exact T1.
  - destruct (tot_1b0 [true] m eq_refl eq_refl (IH (S m) ltac:(lia))) as [_ T2]. exact T2.
Qed.

Lemma len_tl : forall (w : list bool), length (tl w) <= length w.
Proof. intros [|b w]; cbn; lia. Qed.

Lemma tot_alle : forall len n w, length w = len -> Tot n w.
Proof.
  intros len. induction len as [len IHl] using lt_wf_ind.
  intros n. induction n as [n IHn] using lt_wf_ind.
  intros w Hlen.
  destruct n as [|n]; [apply Tot_0|].
  destruct w as [|a w']; [apply tot_nil|].
  assert (L1 : length (tl w') < len) by (pose proof (len_tl w'); cbn in Hlen; lia).
  assert (L2 : length (tl (tl w')) < len) by (pose proof (len_tl (tl w')); lia).
  assert (L3 : length (tl (tl (tl w'))) < len) by (pose proof (len_tl (tl (tl w'))); lia).
  destruct a.
  - destruct (z w') eqn:Eb, (z (tl w')) eqn:Ec.
    + apply Tot_hit. apply H_111; [reflexivity|exact Eb|exact Ec].
    + destruct (gerade_oder_ungerade n) as [m [Hm|Hm]]; subst n.
      * destruct (tot_1b0 (true :: w') m eq_refl Ec (IHl _ L2 (S m) (tl (tl w')) eq_refl)) as [T1 _].
        exact T1.
      * destruct (tot_1b0 (true :: w') m eq_refl Ec (IHl _ L2 (S m) (tl (tl w')) eq_refl)) as [_ T2].
        exact T2.
    + destruct (z (tl (tl w'))) eqn:Ed.
      * destruct w' as [|b [|c [|d rest]]]; cbn in Eb, Ec, Ed; try discriminate.
        subst b c d.
        eapply Tot_vis; [apply V_1011; reflexivity|]. cbn [tl].
        apply (IHn n ltac:(lia)). cbn in Hlen |- *. lia.
      * apply (tot_1010 (S n) (true :: w') eq_refl Eb Ec Ed).
        exact (IHl _ L3 _ (tl (tl (tl w'))) eq_refl).
    + destruct (gerade_oder_ungerade n) as [m [Hm|Hm]]; subst n.
      * destruct (tot_1b0 (true :: w') m eq_refl Ec (IHl _ L2 (S m) (tl (tl w')) eq_refl)) as [T1 _].
        exact T1.
      * destruct (tot_1b0 (true :: w') m eq_refl Ec (IHl _ L2 (S m) (tl (tl w')) eq_refl)) as [_ T2].
        exact T2.
  - eapply Tot_vis; [apply V_0; reflexivity|]. cbn [tl].
    apply (IHn n ltac:(lia)). cbn in Hlen |- *. lia.
Qed.

(** Jeder Besuch endet oder trifft 111. *)
Theorem besuch_endet_oder_trifft111 : forall w, Hit w \/ exists y, Vis w y.
Proof.
  intros w. destruct (Tot_inv O w (tot_alle (length w) (S O) w eq_refl)) as [H|[y [H _]]].
  - left. exact H.
  - right. exists y. exact H.
Qed.

End WT.

(** ** Die Maschine *)

Definition tm := Eval compute in (TM_from_str "1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---").

(** Zellen (aus PR #59) *)
Definition sym (b : bool) : Sym := if b then S1 else S0.
Fixpoint lw (w : list bool) (r : side) : side :=
  match w with [] => r | b :: w => sym b >> lw w r end.
Definition Zinf : side := const S0.
Lemma Zinf_unfold : Zinf = S0 >> Zinf.
Proof. apply const_unfold. Qed.

(** Besuch und Halt auf dem Band (aus PR #59: [Vis], [HV], [LE]): der Kopf betritt s
    von links im Zustand C (links daneben eine 0) und kommt im Zustand A eine
    Zelle links von dieser 0 zurueck; s ist dann s'. *)
Definition BandVis (s s' : side) : Prop :=
  forall x l, S0 >> x >> l {{C}}> s -[ tm ]->+ l {{A}}> x >> S0 >> s'.
Definition BandHalt (s : side) : Prop :=
  forall x l, halts tm (S0 >> x >> l {{C}}> s).
Definition LE (s : side) : Q * tape := const S0 {{A}}> S1 >> S0 >> s.

(** Taktiken (aus PR #59) *)
Ltac run_to H := repeat (first [solve [finish] | eapply evstep_trans; [apply progress_evstep; apply H|] | step]).
Ltac run_to2 H1 H2 :=
  repeat (first [solve [finish] | eapply evstep_trans; [apply progress_evstep; apply H1|]
                | eapply evstep_trans; [apply progress_evstep; apply H2|] | step]).
Ltac run_halt := repeat (first [apply evstep_refl | eapply evstep_step; [prove_step|simpl_tape]]).
Ltac run_halt1 H := repeat (first [apply evstep_refl | eapply evstep_trans; [apply progress_evstep; apply H|]
                                  | eapply evstep_step; [prove_step|simpl_tape]]).
Ltac law :=
  first
  [ solve [intros r x l; execute]
  | solve [let H := fresh "H" in intros r r' H x l; eapply progress_intro; [prove_step|simpl_tape]; run_to H]
  | solve [let H1 := fresh "H" in let H2 := fresh "H" in
           intros r r1 r2 H1 H2 x l; eapply progress_intro; [prove_step|simpl_tape]; run_to2 H1 H2]
  | solve [intros r x l; solve_halt]
  | solve [let H := fresh "H" in intros r H x l; eapply halts_evstep; [apply H|]; run_halt]
  | solve [let H1 := fresh "H" in let H2 := fresh "H" in
           intros r r1 H1 H2 x l; eapply halts_evstep; [apply H2|]; run_halt1 H1]
  | solve [let H := fresh "H" in intros s s' H; unfold LE; eapply progress_intro; [prove_step|simpl_tape];
           repeat (first [apply progress_evstep; apply H | step])]
  | solve [let H := fresh "H" in intros s H; unfold LE; eapply halts_evstep; [apply H|]; run_halt]
  | solve [unfold c0, LE, tape0; eapply progress_intro; [prove_step|simpl_tape]; repeat (first [solve [finish] | step])]
  ].

(** Die dreizehn Annahmen, fuer beliebige Bandreste bewiesen. Elf in der Form
    von PR #59, dazu vis_K und hv_111 an Stelle von hv_1011. *)
Lemma vis_0 : forall r, BandVis (S0 >> r) (S1 >> r).
Proof. law. Qed.
Lemma vis_H : forall r r', BandVis r r' -> BandVis (S1 >> S0 >> S0 >> r) (S0 >> S0 >> S0 >> r').
Proof. law. Qed.
Lemma vis_G : forall r r', BandVis r r' -> BandVis (S1 >> S1 >> S0 >> r) (S0 >> S0 >> S0 >> r').
Proof. law. Qed.
Lemma vis_L : forall r r1 r2, BandVis r r1 -> BandVis r1 r2 ->
  BandVis (S1 >> S0 >> S1 >> S0 >> r) (S1 >> S0 >> S1 >> S0 >> r2).
Proof. law. Qed.
Lemma vis_K : forall r, BandVis (S1 >> S0 >> S1 >> S1 >> r) (S0 >> S0 >> S0 >> S1 >> r).
Proof. law. Qed.
Lemma hv_111 : forall r, BandHalt (S1 >> S1 >> S1 >> r).
Proof. law. Qed.
Lemma hv_H : forall r, BandHalt r -> BandHalt (S1 >> S0 >> S0 >> r).
Proof. law. Qed.
Lemma hv_G : forall r, BandHalt r -> BandHalt (S1 >> S1 >> S0 >> r).
Proof. law. Qed.
Lemma hv_L1 : forall r, BandHalt r -> BandHalt (S1 >> S0 >> S1 >> S0 >> r).
Proof. law. Qed.
Lemma hv_L2 : forall r r1, BandVis r r1 -> BandHalt r1 -> BandHalt (S1 >> S0 >> S1 >> S0 >> r).
Proof. law. Qed.
Lemma round_step : forall s s', BandVis (S1 >> S0 >> s) s' -> LE s -[ tm ]->+ LE s'.
Proof. law. Qed.
Lemma round_halt : forall s, BandHalt (S1 >> S0 >> s) -> halts tm (LE s).
Proof. law. Qed.
Lemma blank_start : c0 -[ tm ]->+ LE (S1 >> const S0).
Proof. law. Qed.

(** ** Vom Wort zum Band *)

Lemma lw_z : forall w, lw w Zinf = sym (W.z w) >> lw (tl w) Zinf.
Proof. intros [|b w]; [exact Zinf_unfold|reflexivity]. Qed.

Ltac zerlege w :=
  rewrite (lw_z w), (lw_z (tl w)), (lw_z (tl (tl w))), (lw_z (tl (tl (tl w)))).

Lemma band_vis : forall w y, W.Vis w y -> BandVis (lw w Zinf) (lw y Zinf).
Proof.
  induction 1 as [w Ea|w y Ea Eb Ec _ IH|w y Ea Eb Ec _ IH
                 |w y1 y2 Ea Eb Ec Ed _ IH1 _ IH2|w Ea Eb Ec Ed].
  - rewrite (lw_z w), Ea. apply vis_0.
  - rewrite (lw_z w), (lw_z (tl w)), (lw_z (tl (tl w))), Ea, Eb, Ec. apply vis_H. exact IH.
  - rewrite (lw_z w), (lw_z (tl w)), (lw_z (tl (tl w))), Ea, Eb, Ec. apply vis_G. exact IH.
  - zerlege w. rewrite Ea, Eb, Ec, Ed. eapply vis_L; eauto.
  - zerlege w. rewrite Ea, Eb, Ec, Ed. apply vis_K.
Qed.

Lemma band_hit : forall w, W.Hit w -> BandHalt (lw w Zinf).
Proof.
  induction 1 as [w Ea Eb Ec|w Ea Eb Ec _ IH|w Ea Eb Ec _ IH
                 |w Ea Eb Ec Ed _ IH|w y1 Ea Eb Ec Ed Hv _ IH].
  - rewrite (lw_z w), (lw_z (tl w)), (lw_z (tl (tl w))), Ea, Eb, Ec. apply hv_111.
  - rewrite (lw_z w), (lw_z (tl w)), (lw_z (tl (tl w))), Ea, Eb, Ec. apply hv_H. exact IH.
  - rewrite (lw_z w), (lw_z (tl w)), (lw_z (tl (tl w))), Ea, Eb, Ec. apply hv_G. exact IH.
  - zerlege w. rewrite Ea, Eb, Ec, Ed. apply hv_L1. exact IH.
  - zerlege w. rewrite Ea, Eb, Ec, Ed. eapply hv_L2; [apply band_vis; exact Hv|exact IH].
Qed.

Lemma runde_band : forall k s, W.Runde W.start k s -> c0 -[ tm ]->* LE (lw s Zinf).
Proof.
  induction 1 as [|k s s' _ IH Hv].
  - apply progress_evstep. exact blank_start.
  - eapply evstep_trans; [exact IH|]. apply progress_evstep. apply round_step.
    exact (band_vis _ _ Hv).
Qed.

(** ** Hauptsatz *)

Lemma halt_richtung : W.trifft111 W.start -> halts tm c0.
Proof.
  intros [k [s [R H]]].
  eapply halts_evstep; [|exact (runde_band k s R)].
  apply round_halt. exact (band_hit _ H).
Qed.

Lemma nichthalt_richtung : halts tm c0 -> W.trifft111 W.start.
Proof.
  intros Hh.
  assert (Hs : halts tm (LE (lw W.start Zinf))).
  { apply (proj1 (halts_evstep_iff tm _ _ (runde_band O W.start (W.R_0 W.start)))). exact Hh. }
  destruct Hs as [n Hn].
  assert (Gen : forall n k s, W.Runde W.start k s -> halts_in tm (LE (lw s Zinf)) n ->
                W.trifft111 W.start).
  { clear. intros n. induction n as [n IH] using lt_wf_ind. intros k s R Hn.
    destruct (WT.besuch_endet_oder_trifft111 (true :: false :: s)) as [Hit|[s' Hv]].
    - exists k, s. auto.
    - pose proof (round_step _ _ (band_vis _ _ Hv)) as P.
      destruct (progress_multistep _ _ _ P) as [m M].
      destruct (Nat.leb_spec (S m) n) as [Le|Gt].
      + apply (IH (n - S m) ltac:(lia) (S k) s' (W.R_S W.start k s s' R Hv)).
        eapply preceeds_halt; eauto.
      + exfalso. eapply exceeds_halt; [exact Hn| |exact M]. lia. }
  exact (Gen n O W.start (W.R_0 W.start) Hn).
Qed.

Theorem rueckfuehrung : halts tm c0 <-> W.trifft111 W.start.
Proof. split; [exact nichthalt_richtung|exact halt_richtung]. Qed.
