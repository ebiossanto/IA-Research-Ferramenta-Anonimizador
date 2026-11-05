import AtratorCore.GeoRatio

/-!
# Distância e razão de massas para saídas inteiras

`dist x y = |x - y|` em naturais. Junta a desigualdade triangular com `geo_ratio`, obtendo a forma completa:
para `a, a' : Int` com `dist a a' ≤ Q` e qualquer saída `z : Int`,

    p^(dist z a + Q) · q^(dist z a') ≤ p^(dist z a') · q^(dist z a + Q).

`@trace T-DP-TRI` `@trace T-DP-GEO`

STATUS: escrito e revisado à mão; NÃO compilado no ambiente que gerou este pacote. Usa `omega` com `Int.natAbs`
(com alternativa manual via `Int.natAbs_add_le`).
-/

namespace Atrator

def dist (x y : Int) : Nat := (x - y).natAbs

/-- `@trace T-DP-TRI` -/
theorem dist_tri (x y z : Int) : dist x z ≤ dist x y + dist y z := by
  unfold dist
  first
    | omega
    | (have h : x - z = (x - y) + (y - z) := (by omega); rw [h]; exact Int.natAbs_add_le _ _)

/-- `@trace T-DP-GEO` `@trace T-DP-TRI` : razão de massas do mecanismo geométrico (forma em naturais). -/
theorem dp_ratio (p q Q : Nat) (hpq : p ≤ q) (a a' z : Int) (h : dist a a' ≤ Q) :
    p ^ (dist z a + Q) * q ^ (dist z a') ≤ p ^ (dist z a') * q ^ (dist z a + Q) := by
  apply geo_ratio p q Q (dist z a) (dist z a') hpq
  have ht := dist_tri z a a'
  omega

end Atrator
