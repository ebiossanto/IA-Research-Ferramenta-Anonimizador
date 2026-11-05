/-!
# Contração da descarga (aritmética de naturais)

Espelha `python/atrator_ref/spec.py` e `rust/src/exposure.rs`.

* `removal d g v = ⌈g·v/d⌉` — quanto a descarga reverte de uma exposição `v`;
* `dischargeCeil d g v = v - removal d g v` — exposição restante;
* contrato: `d * D v + g * v ≤ d * v`  (≡ `D v ≤ (1 - g/d) v`).

`@trace T-D-REM` `@trace T-D-CONTRACT` `@trace T-D-MONO` `@trace T-D-POS`

STATUS: escrito e revisado à mão; NÃO compilado no ambiente que gerou este pacote (sem toolchain Lean).
-/

namespace Atrator

/-- Quanto a descarga reverte: `⌈g·v/d⌉` (em naturais: `(g*v + (d-1)) / d`). -/
def removal (d g v : Nat) : Nat := (g * v + (d - 1)) / d

/-- Exposição restante após a descarga. -/
def dischargeCeil (d g v : Nat) : Nat := v - removal d g v

/-- `@trace T-D-REM` : `g·v ≤ d·removal` e `removal ≤ v`. -/
theorem removal_spec (d g v : Nat) (hd : 0 < d) (hg : g ≤ d) :
    g * v ≤ d * removal d g v ∧ removal d g v ≤ v := by
  obtain ⟨q, hq⟩ : ∃ q, q = (g * v + (d - 1)) / d := ⟨_, rfl⟩
  obtain ⟨r, hr⟩ : ∃ r, r = (g * v + (d - 1)) % d := ⟨_, rfl⟩
  have h1 : d * q + r = g * v + (d - 1) := by
    rw [hq, hr]
    exact Nat.div_add_mod _ _
  have h2 : r < d := by
    rw [hr]
    exact Nat.mod_lt _ hd
  have h3 : g * v ≤ d * v := Nat.mul_le_mul hg (Nat.le_refl v)
  have h5 : d * (v + 1) = d * v + d := by rw [Nat.mul_add, Nat.mul_one]
  have h4 : q < v + 1 := by
    rw [hq]
    apply Nat.div_lt_of_lt_mul
    omega
  have e : removal d g v = q := hq.symm
  rw [e]
  omega

/-- `@trace T-D-POS` : com `g ≥ 1` e `v ≥ 1`, a descarga reverte pelo menos 1. -/
theorem removal_pos (d g v : Nat) (hd : 0 < d) (hg : 0 < g) (hv : 0 < v) :
    0 < removal d g v := by
  have h : 0 < g * v := Nat.mul_pos hg hv
  unfold removal
  apply Nat.lt_of_lt_of_le Nat.zero_lt_one
  rw [Nat.le_div_iff_mul_le hd]
  generalize g * v = w at h ⊢
  omega

/-- `@trace T-D-POS` : a descarga é estritamente decrescente para `v ≥ 1`. -/
theorem discharge_lt (d g v : Nat) (hd : 0 < d) (hg0 : 0 < g) (hg : g ≤ d) (hv : 0 < v) :
    dischargeCeil d g v < v := by
  have h1 := removal_pos d g v hd hg0 hv
  have h2 := (removal_spec d g v hd hg).2
  unfold dischargeCeil
  omega

/-- Aritmética pura: se `g·v ≤ d·r` e `r ≤ v`, então `d·(v-r) + g·v ≤ d·v`. -/
theorem sub_contract (d g v r : Nat) (hr1 : g * v ≤ d * r) (hr2 : r ≤ v) :
    d * (v - r) + g * v ≤ d * v := by
  obtain ⟨k, hk⟩ : ∃ k, v = r + k := ⟨v - r, by omega⟩
  have e1 : d * v = d * r + d * k := by rw [hk, Nat.mul_add]
  have e2 : v - r = k := by omega
  rw [e2]
  omega

/-- Contrato de uma descarga abstrata `D` com taxa `g` sobre denominador `d`. -/
abbrev Contract (d g : Nat) (D : Nat → Nat) : Prop :=
  ∀ v, D v ≤ v ∧ d * D v + g * v ≤ d * v

/-- `@trace T-D-CONTRACT` : `dischargeCeil` satisfaz o contrato. -/
theorem dischargeCeil_contract (d g : Nat) (hd : 0 < d) (hg : g ≤ d) :
    Contract d g (dischargeCeil d g) := by
  intro v
  obtain ⟨hr1, hr2⟩ := removal_spec d g v hd hg
  refine ⟨?_, ?_⟩
  · unfold dischargeCeil
    omega
  · unfold dischargeCeil
    exact sub_contract d g v (removal d g v) hr1 hr2

/-- `@trace T-D-MONO` : `(d-g)(b-a) ≥ 0`, em forma aditiva. -/
theorem mono_aux (d g a b : Nat) (hg : g ≤ d) (hab : a ≤ b) :
    d * a + g * b ≤ d * b + g * a := by
  obtain ⟨w, hw⟩ : ∃ w, b = a + w := ⟨b - a, by omega⟩
  have e1 : d * b = d * a + d * w := by rw [hw, Nat.mul_add]
  have e2 : g * b = g * a + g * w := by rw [hw, Nat.mul_add]
  have e3 : g * w ≤ d * w := Nat.mul_le_mul hg (Nat.le_refl w)
  omega

/-- Cancelamento à esquerda para `≤` em naturais (evita depender do nome de lema da biblioteca). -/
theorem cancel_left_le {d a b : Nat} (hd : 0 < d) (h : d * a ≤ d * b) : a ≤ b := by
  by_cases hab : a ≤ b
  · exact hab
  · have h1 : b + 1 ≤ a := by omega
    have h2 : d * (b + 1) ≤ d * a := Nat.mul_le_mul (Nat.le_refl d) h1
    have h3 : d * (b + 1) = d * b + d := by rw [Nat.mul_add, Nat.mul_one]
    omega

end Atrator
