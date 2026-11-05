import AtratorProb.Normalized

/-!
Fase 2 (roadmap item 5): informação mútua do canal de presença.

Entrada X uniforme em {0,1} (registro ausente / presente) e saída Z com P(Z|X=0) = p0 e
P(Z|X=1) = p1. Com ε-DP por saída (p0 ≤ K·p1 e p1 ≤ K·p0, K = e^ε), a informação mútua
(em nats) satisfaz  I(X;Z) ≤ ln(2K/(K+1)),  ou seja, em bits  I ≤ log₂(2e^ε/(e^ε+1)).

@trace T-DP-INFO  informação mútua ≤ log₂(2e^ε/(e^ε+1))
-/

namespace AtratorProb

open Real

/-- Informação mútua (nats) entre X uniforme em {0,1} e Z, com densidades `p0`, `p1`. -/
noncomputable def mutInfo (p0 p1 : ℤ → ℝ) : ℝ :=
  ∑' z, (1 / 2) * (p0 z * Real.log (p0 z / ((p0 z + p1 z) / 2))
    + p1 z * Real.log (p1 z / ((p0 z + p1 z) / 2)))

/-- Termo de uma das duas hipóteses: `x · ln(x / m) ≤ x · ln(2K/(K+1))` quando `x ≤ K·y`. -/
theorem term_le (K x y : ℝ) (hK : 1 ≤ K) (hx : 0 ≤ x) (hxy : 0 < x + y)
    (h : x ≤ K * y) :
    x * Real.log (x / ((x + y) / 2)) ≤ x * Real.log (2 * K / (K + 1)) := by
  rcases eq_or_lt_of_le hx with hx0 | hxpos
  · rw [← hx0]
    simp
  · apply mul_le_mul_of_nonneg_left _ hx
    apply Real.log_le_log
    · apply div_pos hxpos
      linarith
    · rw [div_le_div_iff₀ (by linarith) (by linarith)]
      nlinarith

/-- `@trace T-DP-INFO` : cota da informação mútua (nats) sob ε-DP por saída. -/
theorem mutInfo_le (p0 p1 : ℤ → ℝ) (K : ℝ) (hK : 1 ≤ K)
    (h0 : ∀ z, 0 ≤ p0 z) (h1 : ∀ z, 0 ≤ p1 z)
    (hs0 : HasSum p0 1) (hs1 : HasSum p1 1)
    (r01 : ∀ z, p0 z ≤ K * p1 z) (r10 : ∀ z, p1 z ≤ K * p0 z) :
    mutInfo p0 p1 ≤ Real.log (2 * K / (K + 1)) := by
  have hc0 : 0 ≤ Real.log (2 * K / (K + 1)) := by
    apply Real.log_nonneg
    rw [le_div_iff₀ (by linarith)]
    linarith
  have hsm : HasSum (fun z => (p0 z + p1 z) / 2) 1 := by
    have := (hs0.add hs1).div_const 2
    norm_num at this
    exact this
  have pw : ∀ z, (1 / 2) * (p0 z * Real.log (p0 z / ((p0 z + p1 z) / 2))
      + p1 z * Real.log (p1 z / ((p0 z + p1 z) / 2)))
      ≤ ((p0 z + p1 z) / 2) * Real.log (2 * K / (K + 1)) := by
    intro z
    have hu := h0 z
    have hv := h1 z
    rcases eq_or_lt_of_le (add_nonneg hu hv) with hsum | hspos
    · have hu0 : p0 z = 0 := by linarith
      have hv0 : p1 z = 0 := by linarith
      rw [hu0, hv0]
      simp
    · have t1 := term_le K (p0 z) (p1 z) hK hu hspos (r01 z)
      have t2 := term_le K (p1 z) (p0 z) hK hv (by linarith) (r10 z)
      rw [add_comm (p1 z) (p0 z)] at t2
      nlinarith
  by_cases hs : Summable (fun z => (1 / 2) * (p0 z * Real.log (p0 z / ((p0 z + p1 z) / 2))
      + p1 z * Real.log (p1 z / ((p0 z + p1 z) / 2))))
  · unfold mutInfo
    calc _ ≤ ∑' z, ((p0 z + p1 z) / 2) * Real.log (2 * K / (K + 1)) :=
          tsum_le_tsum pw hs (hsm.mul_right _).summable
      _ = Real.log (2 * K / (K + 1)) := by
          rw [tsum_mul_right, hsm.tsum_eq, one_mul]
  · unfold mutInfo
    rw [tsum_eq_zero_of_not_summable hs]
    exact hc0

/-- Informação mútua em bits: `I/ln 2 ≤ log₂(2K/(K+1))`. -/
theorem mutInfo_le_bits (p0 p1 : ℤ → ℝ) (K : ℝ) (hK : 1 ≤ K)
    (h0 : ∀ z, 0 ≤ p0 z) (h1 : ∀ z, 0 ≤ p1 z)
    (hs0 : HasSum p0 1) (hs1 : HasSum p1 1)
    (r01 : ∀ z, p0 z ≤ K * p1 z) (r10 : ∀ z, p1 z ≤ K * p0 z) :
    mutInfo p0 p1 / Real.log 2 ≤ Real.log (2 * K / (K + 1)) / Real.log 2 :=
  div_le_div_of_nonneg_right (mutInfo_le p0 p1 K hK h0 h1 hs0 hs1 r01 r10)
    (Real.log_nonneg (by norm_num))

/-- Densidade geométrica não-negativa. -/
theorem geoDens_nonneg (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (μ z : ℤ) : 0 ≤ geoDens r μ z := by
  unfold geoDens geoC geoWeight
  have hc : 0 ≤ (1 - r) / (1 + r) := by
    apply div_nonneg <;> linarith
  positivity

/-- Razão de densidades geométricas reais entre centros a distância ≤ Q. -/
theorem geoDens_ratio_le (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (Q : ℕ) (μ μ' z : ℤ)
    (h : (μ - μ').natAbs ≤ Q) :
    geoDens r μ z ≤ (1 / r) ^ Q * geoDens r μ' z := by
  unfold geoDens
  have hd : (z - μ - (z - μ')).natAbs ≤ Q := by
    rw [show z - μ - (z - μ') = -(μ - μ') by ring, Int.natAbs_neg]
    exact h
  have hw := geoWeight_ratio_le r hr0 hr1.le Q (z - μ) (z - μ') hd
  have hc : 0 ≤ geoC r := by
    unfold geoC
    apply div_nonneg <;> linarith
  calc geoC r * geoWeight r (z - μ)
      ≤ geoC r * ((1 / r) ^ Q * geoWeight r (z - μ')) := mul_le_mul_of_nonneg_left hw hc
    _ = (1 / r) ^ Q * (geoC r * geoWeight r (z - μ')) := by ring

theorem one_le_geoK (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (Q : ℕ) : 1 ≤ (1 / r) ^ Q :=
  one_le_pow₀ ((one_le_div hr0).mpr hr1.le)

/-- `@trace T-DP-INFO` : canal de presença (ausente = centro 0, presente = centro δ, |δ| ≤ Q):
    I(X;Z) ≤ ln(2K/(K+1)) nats com K = (1/r)^Q = e^{ε0}. -/
theorem geo_mutInfo_le (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (Q : ℕ) (δ : ℤ)
    (hδ : δ.natAbs ≤ Q) :
    mutInfo (geoDens r 0) (geoDens r δ)
      ≤ Real.log (2 * (1 / r) ^ Q / ((1 / r) ^ Q + 1)) :=
  mutInfo_le _ _ _ (one_le_geoK r hr0 hr1 Q)
    (fun z => geoDens_nonneg r hr0 hr1 0 z) (fun z => geoDens_nonneg r hr0 hr1 δ z)
    (hasSum_geoDens r hr0 hr1 0) (hasSum_geoDens r hr0 hr1 δ)
    (fun z => geoDens_ratio_le r hr0 hr1 Q 0 δ z (by rw [zero_sub, Int.natAbs_neg]; exact hδ))
    (fun z => geoDens_ratio_le r hr0 hr1 Q δ 0 z (by rw [sub_zero]; exact hδ))

/-- Mesmo resultado em bits: `I/ln 2 ≤ log₂(2e^ε/(e^ε+1))`, com e^ε = (1/r)^Q. -/
theorem geo_mutInfo_le_bits (r : ℝ) (hr0 : 0 < r) (hr1 : r < 1) (Q : ℕ) (δ : ℤ)
    (hδ : δ.natAbs ≤ Q) :
    mutInfo (geoDens r 0) (geoDens r δ) / Real.log 2
      ≤ Real.log (2 * (1 / r) ^ Q / ((1 / r) ^ Q + 1)) / Real.log 2 :=
  div_le_div_of_nonneg_right (geo_mutInfo_le r hr0 hr1 Q δ hδ) (Real.log_nonneg (by norm_num))

end AtratorProb
