import AtratorProb.Normalized

/-!
Fase 2 (roadmap item 5): erro absoluto esperado do mecanismo geométrico.

E_μ|Z − μ| = 2r/(1 − r²) = 1/sinh(ln(1/r)),  com r = p/q  e  ln(1/r) = ε0/Q.
Logo o erro esperado por coordenada é 1/sinh(ε0/Q) ≈ Q/ε0 para ε0 pequeno (medido em docs/03).

@trace T-DP-UTIL  erro esperado = 1/sinh(eps0/Q)
-/

namespace AtratorProb

open Real

/-- `Σ_{z∈ℤ} |z| r^|z| = 2r/(1−r)²` em ℝ, para `0 ≤ r < 1`. -/
theorem hasSum_abs_geoWeight (r : ℝ) (hr0 : 0 ≤ r) (hr1 : r < 1) :
    HasSum (fun z : ℤ => |(z : ℝ)| * geoWeight r z) (2 * r / (1 - r) ^ 2) := by
  have hnorm : ‖r‖ < 1 := by rw [Real.norm_of_nonneg hr0]; exact hr1
  have hS := hasSum_coe_mul_geometric_of_norm_lt_one hnorm
  have h1 : HasSum (fun n : ℕ => |((n : ℤ) : ℝ)| * geoWeight r (n : ℤ)) (r / (1 - r) ^ 2) := by
    have e : (fun n : ℕ => |((n : ℤ) : ℝ)| * geoWeight r (n : ℤ)) = fun n : ℕ => (n : ℝ) * r ^ n := by
      funext n
      simp [geoWeight, abs_of_nonneg]
    rw [e]
    exact hS
  have h2 : HasSum (fun n : ℕ => |(((-((n : ℤ) + 1)) : ℤ) : ℝ)| * geoWeight r (-((n : ℤ) + 1)))
      (r / (1 - r) ^ 2) := by
    have hg := (hasSum_nat_add_iff' 1).mpr hS
    have e : (fun n : ℕ => |(((-((n : ℤ) + 1)) : ℤ) : ℝ)| * geoWeight r (-((n : ℤ) + 1)))
        = fun n : ℕ => (((n + 1 : ℕ)) : ℝ) * r ^ (n + 1) := by
      funext n
      have hn : (-((n : ℤ) + 1)).natAbs = n + 1 := by omega
      have hc : |(((-((n : ℤ) + 1)) : ℤ) : ℝ)| = ((n + 1 : ℕ) : ℝ) := by
        push_cast
        rw [abs_neg, abs_of_nonneg (by positivity)]
      rw [hc]
      simp only [geoWeight, hn]
    rw [e]
    simpa using hg
  have h := HasSum.of_nat_of_neg_add_one (f := fun z : ℤ => |(z : ℝ)| * geoWeight r z) h1 h2
  have hT : r / (1 - r) ^ 2 + r / (1 - r) ^ 2 = 2 * r / (1 - r) ^ 2 := by ring
  rw [hT] at h
  exact h

/-- `@trace T-DP-UTIL` : E_μ|Z−μ| = 1/sinh(ln(1/r)), i.e. 2r/(1−r²). -/
theorem expected_abs_eq_sinh (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (μ : ℤ) :
    HasSum (fun z : ℤ => |((z - μ : ℤ) : ℝ)| * geoDens r μ z) (1 / Real.sinh (Real.log (1 / r))) := by
  have hW := hasSum_abs_geoWeight r hr0.le hr1
  have hcomp : HasSum ((fun z : ℤ => |(z : ℝ)| * geoWeight r z) ∘ (Equiv.subRight μ))
      (2 * r / (1 - r) ^ 2) := (Equiv.subRight μ).hasSum_iff.mpr hW
  have hshift : HasSum (fun z : ℤ => |((z - μ : ℤ) : ℝ)| * geoWeight r (z - μ))
      (2 * r / (1 - r) ^ 2) := hcomp
  have hsc := hshift.mul_left (geoC r)
  have hval : geoC r * (2 * r / (1 - r) ^ 2) = 1 / Real.sinh (Real.log (1 / r)) := by
    have hpos : 0 < 1 / r := by positivity
    have hsinh : Real.sinh (Real.log (1 / r)) = ((1 / r) - r) / 2 := by
      rw [Real.sinh_eq, Real.exp_neg, Real.exp_log hpos]
      congr 1
      rw [one_div, inv_inv]
    rw [hsinh]
    have h1 : (1 - r) ≠ 0 := by linarith
    have h2 : (1 + r) ≠ 0 := by linarith
    have hr : r ≠ 0 := by linarith
    have e : 1 / r - r = (1 - r) * (1 + r) / r := by
      field_simp
      ring
    rw [e]
    unfold geoC
    field_simp
    ring
  rw [hval] at hsc
  have key : ∀ z : ℤ, |((z - μ : ℤ) : ℝ)| * geoDens r μ z
      = geoC r * (|((z - μ : ℤ) : ℝ)| * geoWeight r (z - μ)) := fun z => by
    unfold geoDens
    ring
  simp only [key]
  exact hsc

end AtratorProb
