/-!
# Agregação por âncora: apagamento estrutural da identidade e sensibilidade

`aggAnchor j rs` = soma das magnitudes `q` dos registros da âncora `j`. O agregado NUNCA lê `id`
(a identidade/payload) — logo trocar a identidade de qualquer registro não muda o agregado (0 bits).
Adicionar um registro altera exatamente UMA coordenada, em no máximo `Q` (sensibilidade L1 ≤ Q).

`@trace T-F-ANON` `@trace T-DP-SENS`

STATUS: escrito e revisado à mão; NÃO compilado no ambiente que gerou este pacote.
-/

namespace Atrator

structure Rec where
  anchor : Nat
  q : Nat
  id : Nat

def aggAnchor (j : Nat) : List Rec → Nat
  | [] => 0
  | r :: rs => (if r.anchor = j then r.q else 0) + aggAnchor j rs

/-- `@trace T-F-ANON` : reescrever a identidade de todos os registros não altera o agregado. -/
theorem agg_ignores_id (j : Nat) (f : Rec → Nat) :
    ∀ rs : List Rec, aggAnchor j (rs.map (fun r => { r with id := f r })) = aggAnchor j rs
  | [] => rfl
  | r :: rs => by
    have ih := agg_ignores_id j f rs
    simp [aggAnchor, ih]

/-- `@trace T-DP-SENS` : na âncora do registro, o agregado soma `q`. -/
theorem agg_cons_same (r : Rec) (rs : List Rec) :
    aggAnchor r.anchor (r :: rs) = r.q + aggAnchor r.anchor rs := by
  simp [aggAnchor]

/-- `@trace T-DP-SENS` : nas demais âncoras, o agregado não muda. -/
theorem agg_cons_other (j : Nat) (r : Rec) (rs : List Rec) (h : r.anchor ≠ j) :
    aggAnchor j (r :: rs) = aggAnchor j rs := by
  simp [aggAnchor, h]

/-- `@trace T-DP-SENS` : em qualquer âncora, adicionar um registro de magnitude `≤ Q` soma no máximo `Q`. -/
theorem agg_cons_le (j Q : Nat) (r : Rec) (rs : List Rec) (h : r.q ≤ Q) :
    aggAnchor j (r :: rs) ≤ aggAnchor j rs + Q := by
  show (if r.anchor = j then r.q else 0) + aggAnchor j rs ≤ aggAnchor j rs + Q
  by_cases hj : r.anchor = j
  · rw [if_pos hj]
    omega
  · rw [if_neg hj]
    omega

end Atrator
