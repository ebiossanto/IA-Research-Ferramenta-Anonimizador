/-!
# Razão de massas do mecanismo geométrico (núcleo combinatório do ε-DP)

A massa (não normalizada) do ruído geométrico bilateral com `α = p/q` na saída `z`, sendo `a` o valor
verdadeiro, é `α^{|z-a|}`; a constante de normalização `(q-p)/(q+p)` não depende de `a` e se cancela na razão.
Para valores `a, a'` com `|a - a'| ≤ Q` e distâncias `m = |z-a|`, `n = |z-a'|` (então `n ≤ m + Q`):

    (p/q)^m ≤ (q/p)^Q · (p/q)^n      ⇔      p^(m+Q) · q^n ≤ p^n · q^(m+Q)      (forma em naturais)

isto é, `P[M(a)=z] ≤ e^ε P[M(a')=z]` com `ε = Q·ln(q/p)`.

`@trace T-DP-GEO`

STATUS: escrito e revisado à mão; NÃO compilado no ambiente que gerou este pacote.
-/

namespace Atrator

/-- `@trace T-DP-GEO` -/
theorem geo_ratio (p q Q m n : Nat) (hpq : p ≤ q) (h : n ≤ m + Q) :
    p ^ (m + Q) * q ^ n ≤ p ^ n * q ^ (m + Q) := by
  obtain ⟨t, ht⟩ : ∃ t, m + Q = n + t := ⟨m + Q - n, by omega⟩
  rw [ht, Nat.pow_add, Nat.pow_add]
  have h1 : p ^ t ≤ q ^ t := Nat.pow_le_pow_left hpq t
  calc p ^ n * p ^ t * q ^ n = p ^ n * q ^ n * p ^ t := by
        first
          | exact Nat.mul_right_comm _ _ _
          | ac_rfl
    _ ≤ p ^ n * q ^ n * q ^ t := Nat.mul_le_mul (Nat.le_refl _) h1
    _ = p ^ n * (q ^ n * q ^ t) := Nat.mul_assoc _ _ _

end Atrator
