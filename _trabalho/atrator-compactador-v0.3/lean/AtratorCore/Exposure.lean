import AtratorCore.Contraction

/-!
# Exposição viva: duas camadas de descarga e invariância (limite último / ISS)

* `rate θ g0 g1 v`: taxa de fundo `g0` sempre; reforço `g1` acima do limiar `θ` (avalanche);
* `disch`, `step`: um ciclo (injeta `ι`, depois descarrega);
* `boundB`: menor `B` com `d·θ ≤ d·B + g0·θ` e `d·cap ≤ g1·B + g1·cap`;
* teorema de invariância: `u ≤ B` ⇒ `u' ≤ B`, para QUALQUER `u'` que satisfaça o contrato em `v = u + ι`
  (vale para a função `disch` e para a descarga FIFO por registros do Rust/Python).

`@trace T-ISS-LYAP` `@trace T-ISS-INV`

STATUS: escrito e revisado à mão; NÃO compilado no ambiente que gerou este pacote.
-/

namespace Atrator

def rate (theta g0 g1 v : Nat) : Nat := if theta < v then g1 else g0

theorem rate_pos {theta g0 g1 v : Nat} (h : theta < v) : rate theta g0 g1 v = g1 := by
  unfold rate
  exact if_pos h

theorem rate_neg {theta g0 g1 v : Nat} (h : ¬ theta < v) : rate theta g0 g1 v = g0 := by
  unfold rate
  exact if_neg h

theorem rate_ge {theta g0 g1 v : Nat} (h : g0 ≤ g1) : g0 ≤ rate theta g0 g1 v := by
  by_cases hc : theta < v
  · rw [rate_pos hc]
    exact h
  · rw [rate_neg hc]
    exact Nat.le_refl g0

def disch (d theta g0 g1 v : Nat) : Nat := dischargeCeil d (rate theta g0 g1 v) v

def step (d theta g0 g1 u iota : Nat) : Nat := disch d theta g0 g1 (u + iota)

def ceilDiv (a b : Nat) : Nat := (a + (b - 1)) / b

def boundB (d theta g0 g1 cap : Nat) : Nat :=
  max (ceilDiv ((d - g0) * theta) d) (ceilDiv ((d - g1) * cap) g1)

/-- Nº de iterações de `f(R) = R - removal d g0 R` até 0 (com combustível `fuel`). -/
def settleStepsFuel (d g0 : Nat) : Nat → Nat → Nat
  | 0, _ => 0
  | fuel + 1, R => if R = 0 then 0 else 1 + settleStepsFuel d g0 fuel (R - removal d g0 R)

/-- `@trace T-LAT` (definição): cota de latência `settleSteps d g0 (B + cap) - 1`. -/
def settleSteps (d g0 R : Nat) : Nat := settleStepsFuel d g0 R R

/-- A função `disch` satisfaz o contrato com a taxa efetiva `rate`. -/
theorem disch_contract (d theta g0 g1 v : Nat) (hd : 0 < d) (hg0 : g0 ≤ d) (hg1 : g1 ≤ d) :
    d * disch d theta g0 g1 v + rate theta g0 g1 v * v ≤ d * v := by
  have hr : rate theta g0 g1 v ≤ d := by
    by_cases hc : theta < v
    · rw [rate_pos hc]
      exact hg1
    · rw [rate_neg hc]
      exact hg0
  have h := (dischargeCeil_contract d (rate theta g0 g1 v) hd hr v).2
  exact h

/-- `@trace T-ISS-LYAP` : decréscimo de Lyapunov com a taxa de fundo `g0`. -/
theorem lyap_step (d theta g0 g1 u iota u' : Nat) (hg01 : g0 ≤ g1)
    (hstep : d * u' + rate theta g0 g1 (u + iota) * (u + iota) ≤ d * (u + iota)) :
    d * u' + g0 * (u + iota) ≤ d * (u + iota) := by
  have h : g0 * (u + iota) ≤ rate theta g0 g1 (u + iota) * (u + iota) :=
    Nat.mul_le_mul (rate_ge hg01) (Nat.le_refl _)
  omega

/-- `@trace T-ISS-INV` : invariância de `[0, B]` em um ciclo. -/
theorem invariant_step (d theta g0 g1 B cap u iota u' : Nat)
    (hd : 0 < d) (hg0 : g0 ≤ g1) (hg1 : g1 ≤ d)
    (hB1 : d * theta ≤ d * B + g0 * theta)
    (hB2 : d * cap ≤ g1 * B + g1 * cap)
    (hu : u ≤ B) (hi : iota ≤ cap)
    (hstep : d * u' + rate theta g0 g1 (u + iota) * (u + iota) ≤ d * (u + iota)) :
    u' ≤ B := by
  by_cases hc : theta < u + iota
  · rw [rate_pos hc] at hstep
    have hm := mono_aux d g1 (u + iota) (B + cap) hg1 (by omega)
    have e1 : d * (B + cap) = d * B + d * cap := Nat.mul_add d B cap
    have e2 : g1 * (B + cap) = g1 * B + g1 * cap := Nat.mul_add g1 B cap
    have h : d * u' ≤ d * B := by omega
    exact cancel_left_le hd h
  · rw [rate_neg hc] at hstep
    have hm := mono_aux d g0 (u + iota) theta (by omega) (by omega)
    have h : d * u' ≤ d * B := by omega
    exact cancel_left_le hd h

/-- `@trace T-ISS-INV` : invariância ao longo de uma trajetória inteira. -/
theorem invariant_traj (d theta g0 g1 B cap : Nat)
    (hd : 0 < d) (hg0 : g0 ≤ g1) (hg1 : g1 ≤ d)
    (hB1 : d * theta ≤ d * B + g0 * theta)
    (hB2 : d * cap ≤ g1 * B + g1 * cap)
    (u iota : Nat → Nat)
    (hi : ∀ k, iota k ≤ cap)
    (hstep : ∀ k, d * u (k + 1) + rate theta g0 g1 (u k + iota k) * (u k + iota k) ≤ d * (u k + iota k))
    (h0 : u 0 ≤ B) : ∀ k, u k ≤ B := by
  intro k
  induction k with
  | zero => exact h0
  | succ n ih =>
    exact invariant_step d theta g0 g1 B cap (u n) (iota n) (u (n + 1)) hd hg0 hg1 hB1 hB2 ih (hi n) (hstep n)

end Atrator
