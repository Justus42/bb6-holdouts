; Weg 1, Positivkontrolle RGRv1 (busycoq-Pin verify/RGRv1.v) als Horn-Klauseln (SMT-LIB, Logik HORN).
; Zustand S0 n1 n2 n3 n4 = 0^inf 1^n1 0 1^n2 QR> (01)^n3 000 (10)^n4 0^inf
(set-logic HORN)
(declare-fun Inv (Int Int Int Int) Bool)
; init: c0 -->* S0 4 5 2 1
(assert (Inv 4 5 2 1))
; Inc: S0 n1 (2+n2) (2+n3) n4 -->+ S0 (1+n1) (1+n2) (1+n3) (1+n4)
(assert (forall ((a Int) (b Int) (c Int) (d Int))
  (=> (and (Inv a (+ b 2) (+ c 2) d) (>= a 0) (>= b 0) (>= c 0) (>= d 0))
      (Inv (+ a 1) (+ b 1) (+ c 1) (+ d 1)))))
; ROv: S0 n1 (1+n2) 1 n4 -->+ S0 (2+n1) (1+n2) (1+n4) 0
(assert (forall ((a Int) (b Int) (d Int))
  (=> (and (Inv a (+ b 1) 1 d) (>= a 0) (>= b 0) (>= d 0))
      (Inv (+ a 2) (+ b 1) (+ d 1) 0))))
; LOv: S0 (4+n1) 1 (2+n3) n4 -->+ S0 3 (1+n1) (2+n3) (1+n4)
(assert (forall ((a Int) (c Int) (d Int))
  (=> (and (Inv (+ a 4) 1 (+ c 2) d) (>= a 0) (>= c 0) (>= d 0))
      (Inv 3 (+ a 1) (+ c 2) (+ d 1)))))
; schlecht: keine Regel passt
(assert (forall ((a Int) (b Int) (c Int) (d Int))
  (=> (and (Inv a b c d) (>= a 0) (>= b 0) (>= c 0) (>= d 0)
           (not (or (and (>= b 2) (>= c 2)) (and (>= b 1) (= c 1)) (and (>= a 4) (= b 1) (>= c 2)))))
      false)))
(check-sat)
(get-model)
