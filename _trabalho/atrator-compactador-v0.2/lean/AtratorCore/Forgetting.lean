/-!
# Evicção: o estado retido só depende das W janelas mais recentes

`agg a` é o agregado (com ruído) da janela de idade `a` (idade 0 = a mais recente).
`retained W agg` = soma dos agregados de idade `0 .. W-1` (o anel).

Se dois históricos coincidem nas janelas de idade `< W`, o estado retido é IGUAL — logo nenhum registro
de uma janela com idade `≥ W` influencia o estado (vazamento residual exatamente zero).

`@trace T-F-EVICT`

STATUS: escrito e revisado à mão; NÃO compilado no ambiente que gerou este pacote.
-/

namespace Atrator

def retained : Nat → (Nat → Int) → Int
  | 0, _ => 0
  | W + 1, agg => retained W agg + agg W

/-- `@trace T-F-EVICT` -/
theorem retained_congr : ∀ (W : Nat) (agg agg' : Nat → Int),
    (∀ a, a < W → agg a = agg' a) → retained W agg = retained W agg'
  | 0, _, _, _ => rfl
  | W + 1, agg, agg', h => by
    have ih := retained_congr W agg agg' (fun a ha => h a (Nat.lt_succ_of_lt ha))
    have hw := h W (Nat.lt_succ_self W)
    simp only [retained]
    rw [ih, hw]

end Atrator
