import AtratorProb.Geometric

/-!
Fase 2 (roadmap item 5): distribuição geométrica bilateral NORMALIZADA como `PMF ℤ`, e a razão
de massas entre centros vizinhos (ε-DP por saída).

P_μ(z) = c · r^|z − μ|  com  c = (1 − r)/(1 + r),  r = p/q ∈ (0,1).

@trace T-DP-GEO   razão de massas normalizadas: P_μ(z) ≤ (1/r)^Q · P_μ'(z) se |μ − μ'| ≤ Q
@trace T-DP-SENS  um registro desloca o centro em no máximo Q
@trace T-DP-EPS   e^ε0 = (1/r)^Q = (q/p)^Q, ε0 = Q ln(q/p)
-/

namespace AtratorProb

open Real

/-- Constante de normalização do geométrico bilateral com razão `r`. -/
noncomputable def geoC (r : ℝ) : ℝ := (1 - r) / (1 + r)

/-- `Σ_{z∈ℤ} r^|z| = (1+r)/(1−r)` em ℝ, para `0 ≤ r < 1`. -/
theorem hasSum_geoWeight (r : ℝ) (hr0 : 0 ≤ r) (hr1 : r < 1) :
    HasSum (fun z : ℤ => geoWeight r z) ((1 + r) / (1 - r)) := by
  have hsum := hasSum_geometric_of_lt_one hr0 hr1
  have h1 : HasSum (fun n : ℕ => geoWeight r (n : ℤ)) (1 - r)⁻¹ := by
    have e : (fun n : ℕ => geoWeight r (n : ℤ)) = fun n : ℕ => r ^ n := by
      funext n
      simp [geoWeight]
    rw [e]
    exact hsum
  have h2 : HasSum (fun n : ℕ => geoWeight r (-((n : ℤ) + 1))) (r * (1 - r)⁻¹) := by
    have e : (fun n : ℕ => geoWeight r (-((n : ℤ) + 1))) = fun n : ℕ => r * r ^ n := by
      funext n
      have hn : (-((n : ℤ) + 1)).natAbs = n + 1 := by omega
      simp only [geoWeight, hn, pow_succ]
      ring
    rw [e]
    exact hsum.mul_left r
  have h := HasSum.of_nat_of_neg_add_one h1 h2
  have hT : (1 - r)⁻¹ + r * (1 - r)⁻¹ = (1 + r) / (1 - r) := by
    have hne : (1 - r) ≠ 0 := by linarith
    field_simp
  rw [hT] at h
  exact h

/-- Peso normalizado centrado em `μ`. -/
noncomputable def geoDens (r : ℝ) (μ z : ℤ) : ℝ := geoC r * geoWeight r (z - μ)

theorem hasSum_geoDens (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (μ : ℤ) :
    HasSum (geoDens r μ) 1 := by
  have hW := hasSum_geoWeight r hr0.le hr1
  have hshift : HasSum (fun z : ℤ => geoWeight r (z - μ)) ((1 + r) / (1 - r)) := by
    have := (Equiv.subRight μ).hasSum_iff.mpr hW
    exact this
  have hsc := hshift.mul_left (geoC r)
  have hc : geoC r * ((1 + r) / (1 - r)) = 1 := by
    have h1 : (1 - r) ≠ 0 := by linarith
    have h2 : (1 + r) ≠ 0 := by linarith
    unfold geoC
    field_simp
  rw [hc] at hsc
  exact hsc

/-- Distribuição geométrica normalizada centrada em `μ`, como `PMF ℤ`. -/
noncomputable def geoPMF (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (μ : ℤ) : PMF ℤ :=
  ⟨fun z => ENNReal.ofReal (geoDens r μ z), by
    have hnn : ∀ z, 0 ≤ geoDens r μ z := by
      intro z
      unfold geoDens geoC geoWeight
      have hc : 0 ≤ (1 - r) / (1 + r) := by
        apply div_nonneg <;> linarith
      positivity
    have h1 : ∑' z, ENNReal.ofReal (geoDens r μ z) = 1 := by
      rw [← ENNReal.ofReal_tsum_of_nonneg hnn (hasSum_geoDens r hr0 hr1 μ).summable,
        (hasSum_geoDens r hr0 hr1 μ).tsum_eq, ENNReal.ofReal_one]
    have := (ENNReal.summable (f := fun z => ENNReal.ofReal (geoDens r μ z))).hasSum
    rwa [h1] at this⟩

theorem geoPMF_apply (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (μ z : ℤ) :
    geoPMF r hr0 hr1 μ z = ENNReal.ofReal (geoDens r μ z) := rfl

/-- `@trace T-DP-GEO` `@trace T-DP-SENS` : razão de massas normalizadas entre centros vizinhos
    (|μ − μ'| ≤ Q) é limitada por `(1/r)^Q` em CADA saída `z`. -/
theorem geoPMF_ratio_le (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (Q : ℕ) (μ μ' : ℤ)
    (h : (μ - μ').natAbs ≤ Q) (z : ℤ) :
    geoPMF r hr0 hr1 μ z ≤ ENNReal.ofReal ((1 / r) ^ Q) * geoPMF r hr0 hr1 μ' z := by
  rw [geoPMF_apply, geoPMF_apply, ← ENNReal.ofReal_mul (by positivity)]
  apply ENNReal.ofReal_le_ofReal
  unfold geoDens
  have hd : (z - μ - (z - μ')).natAbs ≤ Q := by
    rw [show z - μ - (z - μ') = -(μ - μ') by ring, Int.natAbs_neg]
    exact h
  have hw := geoWeight_ratio_le r hr0 hr1.le Q (z - μ) (z - μ') hd
  have hc : 0 ≤ geoC r := by
    unfold geoC
    apply div_nonneg <;> linarith
  calc geoC r * geoWeight r (z - μ)
      ≤ geoC r * ((1 / r) ^ Q * geoWeight r (z - μ')) :=
        mul_le_mul_of_nonneg_left hw hc
    _ = (1 / r) ^ Q * (geoC r * geoWeight r (z - μ')) := by ring

/-- `@trace T-DP-EPS` : a cota em log é `Q · ln(1/r)` (= `Q · ln(q/p)` com r = p/q). -/
theorem geoPMF_log_bound (r : ℝ) (Q : ℕ) : Real.log ((1 / r) ^ Q) = Q * Real.log (1 / r) :=
  log_ratio_bound r Q

end AtratorProb
