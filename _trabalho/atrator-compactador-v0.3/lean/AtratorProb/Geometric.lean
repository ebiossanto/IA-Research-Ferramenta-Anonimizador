import Mathlib.Probability.ProbabilityMassFunction.Monad
import Mathlib.Analysis.SpecialFunctions.Log.Basic

/-!
Fase 2 (roadmap item 5): probabilidade real com Mathlib.

Peso não normalizado do geométrico bilateral com razão r = p/q ∈ (0,1]: w(z) = r^|z|.
A razão de pesos entre dois valores vizinhos (|z − z'| ≤ Q) é limitada por (1/r)^Q = (q/p)^Q,
ou seja e^{ε0} com ε0 = Q·ln(q/p). Esta é a cota de sensibilidade do mecanismo.

@trace T-DP-GEO   razão de massas do mecanismo geométrico
@trace T-DP-EPS   eps0 = Q ln(q/p)  (cota da razão, em log)
-/

namespace AtratorProb

open Real

/-- Peso não normalizado do geométrico bilateral: `r ^ |z|`. -/
noncomputable def geoWeight (r : ℝ) (z : ℤ) : ℝ := r ^ z.natAbs

/-- `@trace T-DP-GEO` : vizinhos a distância ≤ Q têm razão de pesos ≤ (1/r)^Q. -/
theorem geoWeight_ratio_le (r : ℝ) (hr0 : 0 < r) (hr1 : r ≤ 1) (Q : ℕ) (z z' : ℤ)
    (h : (z - z').natAbs ≤ Q) :
    geoWeight r z ≤ (1 / r) ^ Q * geoWeight r z' := by
  unfold geoWeight
  have e : (z' - z).natAbs = (z - z').natAbs := by
    rw [← Int.natAbs_neg]
    congr 1
    ring
  have hn : z'.natAbs ≤ z.natAbs + Q := by
    have htri : (z + (z' - z)).natAbs ≤ z.natAbs + (z' - z).natAbs := Int.natAbs_add_le _ _
    have hz : z + (z' - z) = z' := by ring
    rw [hz] at htri
    omega
  have hanti : r ^ (z.natAbs + Q) ≤ r ^ z'.natAbs :=
    pow_le_pow_of_le_one hr0.le hr1 hn
  calc r ^ z.natAbs
      = (1 / r) ^ Q * r ^ (z.natAbs + Q) := by
        rw [pow_add, one_div, inv_pow]
        field_simp
    _ ≤ (1 / r) ^ Q * r ^ z'.natAbs :=
        mul_le_mul_of_nonneg_left hanti (by positivity)

/-- `@trace T-DP-EPS` : em log, a cota é Q·ln(1/r) = Q·ln(q/p) com r = p/q. -/
theorem log_ratio_bound (r : ℝ) (Q : ℕ) :
    Real.log ((1 / r) ^ Q) = Q * Real.log (1 / r) := by
  rw [Real.log_pow]

end AtratorProb
