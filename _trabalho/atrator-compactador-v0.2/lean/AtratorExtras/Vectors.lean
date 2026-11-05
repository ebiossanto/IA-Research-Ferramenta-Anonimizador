import AtratorCore.Exposure
import AtratorExtras.Prng

/-!
# Vetores diferenciais (gerado por `scripts/gen_vectors.py` — NÃO editar à mão)

Cada `example` afirma que a definição em Lean produz o mesmo valor que o oráculo Python e a
implementação Rust (`trace/vectors.csv`). Usa `native_decide` (avaliação compilada).
@trace T-RNG @trace T-D-REM @trace T-D-CONTRACT @trace T-ISS-INV @trace T-LAT @trace T-GOLD
-/

open Atrator

example : removal 1 1 0 = 0 := by native_decide
example : dischargeCeil 1 1 0 = 0 := by native_decide
example : removal 1 1 1 = 1 := by native_decide
example : dischargeCeil 1 1 1 = 0 := by native_decide
example : removal 1 1 2 = 2 := by native_decide
example : dischargeCeil 1 1 2 = 0 := by native_decide
example : removal 1 1 3 = 3 := by native_decide
example : dischargeCeil 1 1 3 = 0 := by native_decide
example : removal 1 1 7 = 7 := by native_decide
example : dischargeCeil 1 1 7 = 0 := by native_decide
example : removal 1 1 8 = 8 := by native_decide
example : dischargeCeil 1 1 8 = 0 := by native_decide
example : removal 1 1 9 = 9 := by native_decide
example : dischargeCeil 1 1 9 = 0 := by native_decide
example : removal 1 1 100 = 100 := by native_decide
example : dischargeCeil 1 1 100 = 0 := by native_decide
example : removal 1 1 12345 = 12345 := by native_decide
example : dischargeCeil 1 1 12345 = 0 := by native_decide
example : removal 1 1 1000000 = 1000000 := by native_decide
example : dischargeCeil 1 1 1000000 = 0 := by native_decide
example : removal 2 1 0 = 0 := by native_decide
example : dischargeCeil 2 1 0 = 0 := by native_decide
example : removal 2 1 1 = 1 := by native_decide
example : dischargeCeil 2 1 1 = 0 := by native_decide
example : removal 2 1 2 = 1 := by native_decide
example : dischargeCeil 2 1 2 = 1 := by native_decide
example : removal 2 1 3 = 2 := by native_decide
example : dischargeCeil 2 1 3 = 1 := by native_decide
example : removal 2 1 7 = 4 := by native_decide
example : dischargeCeil 2 1 7 = 3 := by native_decide
example : removal 2 1 8 = 4 := by native_decide
example : dischargeCeil 2 1 8 = 4 := by native_decide
example : removal 2 1 9 = 5 := by native_decide
example : dischargeCeil 2 1 9 = 4 := by native_decide
example : removal 2 1 100 = 50 := by native_decide
example : dischargeCeil 2 1 100 = 50 := by native_decide
example : removal 2 1 12345 = 6173 := by native_decide
example : dischargeCeil 2 1 12345 = 6172 := by native_decide
example : removal 2 1 1000000 = 500000 := by native_decide
example : dischargeCeil 2 1 1000000 = 500000 := by native_decide
example : removal 2 2 0 = 0 := by native_decide
example : dischargeCeil 2 2 0 = 0 := by native_decide
example : removal 2 2 1 = 1 := by native_decide
example : dischargeCeil 2 2 1 = 0 := by native_decide
example : removal 2 2 2 = 2 := by native_decide
example : dischargeCeil 2 2 2 = 0 := by native_decide
example : removal 2 2 3 = 3 := by native_decide
example : dischargeCeil 2 2 3 = 0 := by native_decide
example : removal 2 2 7 = 7 := by native_decide
example : dischargeCeil 2 2 7 = 0 := by native_decide
example : removal 2 2 8 = 8 := by native_decide
example : dischargeCeil 2 2 8 = 0 := by native_decide
example : removal 2 2 9 = 9 := by native_decide
example : dischargeCeil 2 2 9 = 0 := by native_decide
example : removal 2 2 100 = 100 := by native_decide
example : dischargeCeil 2 2 100 = 0 := by native_decide
example : removal 2 2 12345 = 12345 := by native_decide
example : dischargeCeil 2 2 12345 = 0 := by native_decide
example : removal 2 2 1000000 = 1000000 := by native_decide
example : dischargeCeil 2 2 1000000 = 0 := by native_decide
example : removal 3 1 0 = 0 := by native_decide
example : dischargeCeil 3 1 0 = 0 := by native_decide
example : removal 3 1 1 = 1 := by native_decide
example : dischargeCeil 3 1 1 = 0 := by native_decide
example : removal 3 1 2 = 1 := by native_decide
example : dischargeCeil 3 1 2 = 1 := by native_decide
example : removal 3 1 3 = 1 := by native_decide
example : dischargeCeil 3 1 3 = 2 := by native_decide
example : removal 3 1 7 = 3 := by native_decide
example : dischargeCeil 3 1 7 = 4 := by native_decide
example : removal 3 1 8 = 3 := by native_decide
example : dischargeCeil 3 1 8 = 5 := by native_decide
example : removal 3 1 9 = 3 := by native_decide
example : dischargeCeil 3 1 9 = 6 := by native_decide
example : removal 3 1 100 = 34 := by native_decide
example : dischargeCeil 3 1 100 = 66 := by native_decide
example : removal 3 1 12345 = 4115 := by native_decide
example : dischargeCeil 3 1 12345 = 8230 := by native_decide
example : removal 3 1 1000000 = 333334 := by native_decide
example : dischargeCeil 3 1 1000000 = 666666 := by native_decide
example : removal 3 3 0 = 0 := by native_decide
example : dischargeCeil 3 3 0 = 0 := by native_decide
example : removal 3 3 1 = 1 := by native_decide
example : dischargeCeil 3 3 1 = 0 := by native_decide
example : removal 3 3 2 = 2 := by native_decide
example : dischargeCeil 3 3 2 = 0 := by native_decide
example : removal 3 3 3 = 3 := by native_decide
example : dischargeCeil 3 3 3 = 0 := by native_decide
example : removal 3 3 7 = 7 := by native_decide
example : dischargeCeil 3 3 7 = 0 := by native_decide
example : removal 3 3 8 = 8 := by native_decide
example : dischargeCeil 3 3 8 = 0 := by native_decide
example : removal 3 3 9 = 9 := by native_decide
example : dischargeCeil 3 3 9 = 0 := by native_decide
example : removal 3 3 100 = 100 := by native_decide
example : dischargeCeil 3 3 100 = 0 := by native_decide
example : removal 3 3 12345 = 12345 := by native_decide
example : dischargeCeil 3 3 12345 = 0 := by native_decide
example : removal 3 3 1000000 = 1000000 := by native_decide
example : dischargeCeil 3 3 1000000 = 0 := by native_decide
example : removal 8 1 0 = 0 := by native_decide
example : dischargeCeil 8 1 0 = 0 := by native_decide
example : removal 8 1 1 = 1 := by native_decide
example : dischargeCeil 8 1 1 = 0 := by native_decide
example : removal 8 1 2 = 1 := by native_decide
example : dischargeCeil 8 1 2 = 1 := by native_decide
example : removal 8 1 3 = 1 := by native_decide
example : dischargeCeil 8 1 3 = 2 := by native_decide
example : removal 8 1 7 = 1 := by native_decide
example : dischargeCeil 8 1 7 = 6 := by native_decide
example : removal 8 1 8 = 1 := by native_decide
example : dischargeCeil 8 1 8 = 7 := by native_decide
example : removal 8 1 9 = 2 := by native_decide
example : dischargeCeil 8 1 9 = 7 := by native_decide
example : removal 8 1 100 = 13 := by native_decide
example : dischargeCeil 8 1 100 = 87 := by native_decide
example : removal 8 1 12345 = 1544 := by native_decide
example : dischargeCeil 8 1 12345 = 10801 := by native_decide
example : removal 8 1 1000000 = 125000 := by native_decide
example : dischargeCeil 8 1 1000000 = 875000 := by native_decide
example : removal 8 4 0 = 0 := by native_decide
example : dischargeCeil 8 4 0 = 0 := by native_decide
example : removal 8 4 1 = 1 := by native_decide
example : dischargeCeil 8 4 1 = 0 := by native_decide
example : removal 8 4 2 = 1 := by native_decide
example : dischargeCeil 8 4 2 = 1 := by native_decide
example : removal 8 4 3 = 2 := by native_decide
example : dischargeCeil 8 4 3 = 1 := by native_decide
example : removal 8 4 7 = 4 := by native_decide
example : dischargeCeil 8 4 7 = 3 := by native_decide
example : removal 8 4 8 = 4 := by native_decide
example : dischargeCeil 8 4 8 = 4 := by native_decide
example : removal 8 4 9 = 5 := by native_decide
example : dischargeCeil 8 4 9 = 4 := by native_decide
example : removal 8 4 100 = 50 := by native_decide
example : dischargeCeil 8 4 100 = 50 := by native_decide
example : removal 8 4 12345 = 6173 := by native_decide
example : dischargeCeil 8 4 12345 = 6172 := by native_decide
example : removal 8 4 1000000 = 500000 := by native_decide
example : dischargeCeil 8 4 1000000 = 500000 := by native_decide
example : removal 8 8 0 = 0 := by native_decide
example : dischargeCeil 8 8 0 = 0 := by native_decide
example : removal 8 8 1 = 1 := by native_decide
example : dischargeCeil 8 8 1 = 0 := by native_decide
example : removal 8 8 2 = 2 := by native_decide
example : dischargeCeil 8 8 2 = 0 := by native_decide
example : removal 8 8 3 = 3 := by native_decide
example : dischargeCeil 8 8 3 = 0 := by native_decide
example : removal 8 8 7 = 7 := by native_decide
example : dischargeCeil 8 8 7 = 0 := by native_decide
example : removal 8 8 8 = 8 := by native_decide
example : dischargeCeil 8 8 8 = 0 := by native_decide
example : removal 8 8 9 = 9 := by native_decide
example : dischargeCeil 8 8 9 = 0 := by native_decide
example : removal 8 8 100 = 100 := by native_decide
example : dischargeCeil 8 8 100 = 0 := by native_decide
example : removal 8 8 12345 = 12345 := by native_decide
example : dischargeCeil 8 8 12345 = 0 := by native_decide
example : removal 8 8 1000000 = 1000000 := by native_decide
example : dischargeCeil 8 8 1000000 = 0 := by native_decide
example : removal 16 1 0 = 0 := by native_decide
example : dischargeCeil 16 1 0 = 0 := by native_decide
example : removal 16 1 1 = 1 := by native_decide
example : dischargeCeil 16 1 1 = 0 := by native_decide
example : removal 16 1 2 = 1 := by native_decide
example : dischargeCeil 16 1 2 = 1 := by native_decide
example : removal 16 1 3 = 1 := by native_decide
example : dischargeCeil 16 1 3 = 2 := by native_decide
example : removal 16 1 7 = 1 := by native_decide
example : dischargeCeil 16 1 7 = 6 := by native_decide
example : removal 16 1 8 = 1 := by native_decide
example : dischargeCeil 16 1 8 = 7 := by native_decide
example : removal 16 1 9 = 1 := by native_decide
example : dischargeCeil 16 1 9 = 8 := by native_decide
example : removal 16 1 100 = 7 := by native_decide
example : dischargeCeil 16 1 100 = 93 := by native_decide
example : removal 16 1 12345 = 772 := by native_decide
example : dischargeCeil 16 1 12345 = 11573 := by native_decide
example : removal 16 1 1000000 = 62500 := by native_decide
example : dischargeCeil 16 1 1000000 = 937500 := by native_decide
example : removal 16 8 0 = 0 := by native_decide
example : dischargeCeil 16 8 0 = 0 := by native_decide
example : removal 16 8 1 = 1 := by native_decide
example : dischargeCeil 16 8 1 = 0 := by native_decide
example : removal 16 8 2 = 1 := by native_decide
example : dischargeCeil 16 8 2 = 1 := by native_decide
example : removal 16 8 3 = 2 := by native_decide
example : dischargeCeil 16 8 3 = 1 := by native_decide
example : removal 16 8 7 = 4 := by native_decide
example : dischargeCeil 16 8 7 = 3 := by native_decide
example : removal 16 8 8 = 4 := by native_decide
example : dischargeCeil 16 8 8 = 4 := by native_decide
example : removal 16 8 9 = 5 := by native_decide
example : dischargeCeil 16 8 9 = 4 := by native_decide
example : removal 16 8 100 = 50 := by native_decide
example : dischargeCeil 16 8 100 = 50 := by native_decide
example : removal 16 8 12345 = 6173 := by native_decide
example : dischargeCeil 16 8 12345 = 6172 := by native_decide
example : removal 16 8 1000000 = 500000 := by native_decide
example : dischargeCeil 16 8 1000000 = 500000 := by native_decide
example : removal 16 16 0 = 0 := by native_decide
example : dischargeCeil 16 16 0 = 0 := by native_decide
example : removal 16 16 1 = 1 := by native_decide
example : dischargeCeil 16 16 1 = 0 := by native_decide
example : removal 16 16 2 = 2 := by native_decide
example : dischargeCeil 16 16 2 = 0 := by native_decide
example : removal 16 16 3 = 3 := by native_decide
example : dischargeCeil 16 16 3 = 0 := by native_decide
example : removal 16 16 7 = 7 := by native_decide
example : dischargeCeil 16 16 7 = 0 := by native_decide
example : removal 16 16 8 = 8 := by native_decide
example : dischargeCeil 16 16 8 = 0 := by native_decide
example : removal 16 16 9 = 9 := by native_decide
example : dischargeCeil 16 16 9 = 0 := by native_decide
example : removal 16 16 100 = 100 := by native_decide
example : dischargeCeil 16 16 100 = 0 := by native_decide
example : removal 16 16 12345 = 12345 := by native_decide
example : dischargeCeil 16 16 12345 = 0 := by native_decide
example : removal 16 16 1000000 = 1000000 := by native_decide
example : dischargeCeil 16 16 1000000 = 0 := by native_decide
example : removal 32 1 0 = 0 := by native_decide
example : dischargeCeil 32 1 0 = 0 := by native_decide
example : removal 32 1 1 = 1 := by native_decide
example : dischargeCeil 32 1 1 = 0 := by native_decide
example : removal 32 1 2 = 1 := by native_decide
example : dischargeCeil 32 1 2 = 1 := by native_decide
example : removal 32 1 3 = 1 := by native_decide
example : dischargeCeil 32 1 3 = 2 := by native_decide
example : removal 32 1 7 = 1 := by native_decide
example : dischargeCeil 32 1 7 = 6 := by native_decide
example : removal 32 1 8 = 1 := by native_decide
example : dischargeCeil 32 1 8 = 7 := by native_decide
example : removal 32 1 9 = 1 := by native_decide
example : dischargeCeil 32 1 9 = 8 := by native_decide
example : removal 32 1 100 = 4 := by native_decide
example : dischargeCeil 32 1 100 = 96 := by native_decide
example : removal 32 1 12345 = 386 := by native_decide
example : dischargeCeil 32 1 12345 = 11959 := by native_decide
example : removal 32 1 1000000 = 31250 := by native_decide
example : dischargeCeil 32 1 1000000 = 968750 := by native_decide
example : removal 32 16 0 = 0 := by native_decide
example : dischargeCeil 32 16 0 = 0 := by native_decide
example : removal 32 16 1 = 1 := by native_decide
example : dischargeCeil 32 16 1 = 0 := by native_decide
example : removal 32 16 2 = 1 := by native_decide
example : dischargeCeil 32 16 2 = 1 := by native_decide
example : removal 32 16 3 = 2 := by native_decide
example : dischargeCeil 32 16 3 = 1 := by native_decide
example : removal 32 16 7 = 4 := by native_decide
example : dischargeCeil 32 16 7 = 3 := by native_decide
example : removal 32 16 8 = 4 := by native_decide
example : dischargeCeil 32 16 8 = 4 := by native_decide
example : removal 32 16 9 = 5 := by native_decide
example : dischargeCeil 32 16 9 = 4 := by native_decide
example : removal 32 16 100 = 50 := by native_decide
example : dischargeCeil 32 16 100 = 50 := by native_decide
example : removal 32 16 12345 = 6173 := by native_decide
example : dischargeCeil 32 16 12345 = 6172 := by native_decide
example : removal 32 16 1000000 = 500000 := by native_decide
example : dischargeCeil 32 16 1000000 = 500000 := by native_decide
example : removal 32 32 0 = 0 := by native_decide
example : dischargeCeil 32 32 0 = 0 := by native_decide
example : removal 32 32 1 = 1 := by native_decide
example : dischargeCeil 32 32 1 = 0 := by native_decide
example : removal 32 32 2 = 2 := by native_decide
example : dischargeCeil 32 32 2 = 0 := by native_decide
example : removal 32 32 3 = 3 := by native_decide
example : dischargeCeil 32 32 3 = 0 := by native_decide
example : removal 32 32 7 = 7 := by native_decide
example : dischargeCeil 32 32 7 = 0 := by native_decide
example : removal 32 32 8 = 8 := by native_decide
example : dischargeCeil 32 32 8 = 0 := by native_decide
example : removal 32 32 9 = 9 := by native_decide
example : dischargeCeil 32 32 9 = 0 := by native_decide
example : removal 32 32 100 = 100 := by native_decide
example : dischargeCeil 32 32 100 = 0 := by native_decide
example : removal 32 32 12345 = 12345 := by native_decide
example : dischargeCeil 32 32 12345 = 0 := by native_decide
example : removal 32 32 1000000 = 1000000 := by native_decide
example : dischargeCeil 32 32 1000000 = 0 := by native_decide
example : removal 100 1 0 = 0 := by native_decide
example : dischargeCeil 100 1 0 = 0 := by native_decide
example : removal 100 1 1 = 1 := by native_decide
example : dischargeCeil 100 1 1 = 0 := by native_decide
example : removal 100 1 2 = 1 := by native_decide
example : dischargeCeil 100 1 2 = 1 := by native_decide
example : removal 100 1 3 = 1 := by native_decide
example : dischargeCeil 100 1 3 = 2 := by native_decide
example : removal 100 1 7 = 1 := by native_decide
example : dischargeCeil 100 1 7 = 6 := by native_decide
example : removal 100 1 8 = 1 := by native_decide
example : dischargeCeil 100 1 8 = 7 := by native_decide
example : removal 100 1 9 = 1 := by native_decide
example : dischargeCeil 100 1 9 = 8 := by native_decide
example : removal 100 1 100 = 1 := by native_decide
example : dischargeCeil 100 1 100 = 99 := by native_decide
example : removal 100 1 12345 = 124 := by native_decide
example : dischargeCeil 100 1 12345 = 12221 := by native_decide
example : removal 100 1 1000000 = 10000 := by native_decide
example : dischargeCeil 100 1 1000000 = 990000 := by native_decide
example : removal 100 50 0 = 0 := by native_decide
example : dischargeCeil 100 50 0 = 0 := by native_decide
example : removal 100 50 1 = 1 := by native_decide
example : dischargeCeil 100 50 1 = 0 := by native_decide
example : removal 100 50 2 = 1 := by native_decide
example : dischargeCeil 100 50 2 = 1 := by native_decide
example : removal 100 50 3 = 2 := by native_decide
example : dischargeCeil 100 50 3 = 1 := by native_decide
example : removal 100 50 7 = 4 := by native_decide
example : dischargeCeil 100 50 7 = 3 := by native_decide
example : removal 100 50 8 = 4 := by native_decide
example : dischargeCeil 100 50 8 = 4 := by native_decide
example : removal 100 50 9 = 5 := by native_decide
example : dischargeCeil 100 50 9 = 4 := by native_decide
example : removal 100 50 100 = 50 := by native_decide
example : dischargeCeil 100 50 100 = 50 := by native_decide
example : removal 100 50 12345 = 6173 := by native_decide
example : dischargeCeil 100 50 12345 = 6172 := by native_decide
example : removal 100 50 1000000 = 500000 := by native_decide
example : dischargeCeil 100 50 1000000 = 500000 := by native_decide
example : removal 100 100 0 = 0 := by native_decide
example : dischargeCeil 100 100 0 = 0 := by native_decide
example : removal 100 100 1 = 1 := by native_decide
example : dischargeCeil 100 100 1 = 0 := by native_decide
example : removal 100 100 2 = 2 := by native_decide
example : dischargeCeil 100 100 2 = 0 := by native_decide
example : removal 100 100 3 = 3 := by native_decide
example : dischargeCeil 100 100 3 = 0 := by native_decide
example : removal 100 100 7 = 7 := by native_decide
example : dischargeCeil 100 100 7 = 0 := by native_decide
example : removal 100 100 8 = 8 := by native_decide
example : dischargeCeil 100 100 8 = 0 := by native_decide
example : removal 100 100 9 = 9 := by native_decide
example : dischargeCeil 100 100 9 = 0 := by native_decide
example : removal 100 100 100 = 100 := by native_decide
example : dischargeCeil 100 100 100 = 0 := by native_decide
example : removal 100 100 12345 = 12345 := by native_decide
example : dischargeCeil 100 100 12345 = 0 := by native_decide
example : removal 100 100 1000000 = 1000000 := by native_decide
example : dischargeCeil 100 100 1000000 = 0 := by native_decide
example : removal 1000 1 0 = 0 := by native_decide
example : dischargeCeil 1000 1 0 = 0 := by native_decide
example : removal 1000 1 1 = 1 := by native_decide
example : dischargeCeil 1000 1 1 = 0 := by native_decide
example : removal 1000 1 2 = 1 := by native_decide
example : dischargeCeil 1000 1 2 = 1 := by native_decide
example : removal 1000 1 3 = 1 := by native_decide
example : dischargeCeil 1000 1 3 = 2 := by native_decide
example : removal 1000 1 7 = 1 := by native_decide
example : dischargeCeil 1000 1 7 = 6 := by native_decide
example : removal 1000 1 8 = 1 := by native_decide
example : dischargeCeil 1000 1 8 = 7 := by native_decide
example : removal 1000 1 9 = 1 := by native_decide
example : dischargeCeil 1000 1 9 = 8 := by native_decide
example : removal 1000 1 100 = 1 := by native_decide
example : dischargeCeil 1000 1 100 = 99 := by native_decide
example : removal 1000 1 12345 = 13 := by native_decide
example : dischargeCeil 1000 1 12345 = 12332 := by native_decide
example : removal 1000 1 1000000 = 1000 := by native_decide
example : dischargeCeil 1000 1 1000000 = 999000 := by native_decide
example : removal 1000 500 0 = 0 := by native_decide
example : dischargeCeil 1000 500 0 = 0 := by native_decide
example : removal 1000 500 1 = 1 := by native_decide
example : dischargeCeil 1000 500 1 = 0 := by native_decide
example : removal 1000 500 2 = 1 := by native_decide
example : dischargeCeil 1000 500 2 = 1 := by native_decide
example : removal 1000 500 3 = 2 := by native_decide
example : dischargeCeil 1000 500 3 = 1 := by native_decide
example : removal 1000 500 7 = 4 := by native_decide
example : dischargeCeil 1000 500 7 = 3 := by native_decide
example : removal 1000 500 8 = 4 := by native_decide
example : dischargeCeil 1000 500 8 = 4 := by native_decide
example : removal 1000 500 9 = 5 := by native_decide
example : dischargeCeil 1000 500 9 = 4 := by native_decide
example : removal 1000 500 100 = 50 := by native_decide
example : dischargeCeil 1000 500 100 = 50 := by native_decide
example : removal 1000 500 12345 = 6173 := by native_decide
example : dischargeCeil 1000 500 12345 = 6172 := by native_decide
example : removal 1000 500 1000000 = 500000 := by native_decide
example : dischargeCeil 1000 500 1000000 = 500000 := by native_decide
example : removal 1000 1000 0 = 0 := by native_decide
example : dischargeCeil 1000 1000 0 = 0 := by native_decide
example : removal 1000 1000 1 = 1 := by native_decide
example : dischargeCeil 1000 1000 1 = 0 := by native_decide
example : removal 1000 1000 2 = 2 := by native_decide
example : dischargeCeil 1000 1000 2 = 0 := by native_decide
example : removal 1000 1000 3 = 3 := by native_decide
example : dischargeCeil 1000 1000 3 = 0 := by native_decide
example : removal 1000 1000 7 = 7 := by native_decide
example : dischargeCeil 1000 1000 7 = 0 := by native_decide
example : removal 1000 1000 8 = 8 := by native_decide
example : dischargeCeil 1000 1000 8 = 0 := by native_decide
example : removal 1000 1000 9 = 9 := by native_decide
example : dischargeCeil 1000 1000 9 = 0 := by native_decide
example : removal 1000 1000 100 = 100 := by native_decide
example : dischargeCeil 1000 1000 100 = 0 := by native_decide
example : removal 1000 1000 12345 = 12345 := by native_decide
example : dischargeCeil 1000 1000 12345 = 0 := by native_decide
example : removal 1000 1000 1000000 = 1000000 := by native_decide
example : dischargeCeil 1000 1000 1000000 = 0 := by native_decide
example : rate 0 1 4 0 = 1 := by native_decide
example : rate 0 1 4 49 = 4 := by native_decide
example : rate 0 1 4 50 = 4 := by native_decide
example : rate 0 1 4 51 = 4 := by native_decide
example : rate 0 1 4 1000 = 4 := by native_decide
example : rate 0 2 16 0 = 2 := by native_decide
example : rate 0 2 16 49 = 16 := by native_decide
example : rate 0 2 16 50 = 16 := by native_decide
example : rate 0 2 16 51 = 16 := by native_decide
example : rate 0 2 16 1000 = 16 := by native_decide
example : rate 0 3 3 0 = 3 := by native_decide
example : rate 0 3 3 49 = 3 := by native_decide
example : rate 0 3 3 50 = 3 := by native_decide
example : rate 0 3 3 51 = 3 := by native_decide
example : rate 0 3 3 1000 = 3 := by native_decide
example : rate 50 1 4 0 = 1 := by native_decide
example : rate 50 1 4 49 = 1 := by native_decide
example : rate 50 1 4 50 = 1 := by native_decide
example : rate 50 1 4 51 = 4 := by native_decide
example : rate 50 1 4 1000 = 4 := by native_decide
example : rate 50 2 16 0 = 2 := by native_decide
example : rate 50 2 16 49 = 2 := by native_decide
example : rate 50 2 16 50 = 2 := by native_decide
example : rate 50 2 16 51 = 16 := by native_decide
example : rate 50 2 16 1000 = 16 := by native_decide
example : rate 50 3 3 0 = 3 := by native_decide
example : rate 50 3 3 49 = 3 := by native_decide
example : rate 50 3 3 50 = 3 := by native_decide
example : rate 50 3 3 51 = 3 := by native_decide
example : rate 50 3 3 1000 = 3 := by native_decide
example : disch 16 60 1 4 0 = 0 := by native_decide
example : disch 16 60 1 4 1 = 0 := by native_decide
example : disch 16 60 1 4 59 = 55 := by native_decide
example : disch 16 60 1 4 60 = 56 := by native_decide
example : disch 16 60 1 4 61 = 45 := by native_decide
example : disch 16 60 1 4 200 = 150 := by native_decide
example : disch 16 60 1 4 1000 = 750 := by native_decide
example : step 16 60 1 4 0 0 = 0 := by native_decide
example : step 16 60 1 4 0 40 = 37 := by native_decide
example : step 16 60 1 4 58 40 = 73 := by native_decide
example : step 16 60 1 4 120 0 = 90 := by native_decide
example : step 16 60 1 4 291 50 = 255 := by native_decide
example : boundB 16 60 1 4 0 = 57 := by native_decide
example : boundB 16 60 1 4 1 = 57 := by native_decide
example : boundB 16 60 1 4 40 = 120 := by native_decide
example : boundB 16 60 1 4 80 = 240 := by native_decide
example : disch 32 150 2 16 0 = 0 := by native_decide
example : disch 32 150 2 16 1 = 0 := by native_decide
example : disch 32 150 2 16 59 = 55 := by native_decide
example : disch 32 150 2 16 60 = 56 := by native_decide
example : disch 32 150 2 16 61 = 57 := by native_decide
example : disch 32 150 2 16 200 = 100 := by native_decide
example : disch 32 150 2 16 1000 = 500 := by native_decide
example : step 32 150 2 16 0 0 = 0 := by native_decide
example : step 32 150 2 16 0 40 = 37 := by native_decide
example : step 32 150 2 16 58 40 = 91 := by native_decide
example : step 32 150 2 16 120 0 = 112 := by native_decide
example : step 32 150 2 16 291 50 = 170 := by native_decide
example : boundB 32 150 2 16 0 = 141 := by native_decide
example : boundB 32 150 2 16 1 = 141 := by native_decide
example : boundB 32 150 2 16 40 = 141 := by native_decide
example : boundB 32 150 2 16 80 = 141 := by native_decide
example : disch 32 300 1 8 0 = 0 := by native_decide
example : disch 32 300 1 8 1 = 0 := by native_decide
example : disch 32 300 1 8 59 = 57 := by native_decide
example : disch 32 300 1 8 60 = 58 := by native_decide
example : disch 32 300 1 8 61 = 59 := by native_decide
example : disch 32 300 1 8 200 = 193 := by native_decide
example : disch 32 300 1 8 1000 = 750 := by native_decide
example : step 32 300 1 8 0 0 = 0 := by native_decide
example : step 32 300 1 8 0 40 = 38 := by native_decide
example : step 32 300 1 8 58 40 = 94 := by native_decide
example : step 32 300 1 8 120 0 = 116 := by native_decide
example : step 32 300 1 8 291 50 = 255 := by native_decide
example : boundB 32 300 1 8 0 = 291 := by native_decide
example : boundB 32 300 1 8 1 = 291 := by native_decide
example : boundB 32 300 1 8 40 = 291 := by native_decide
example : boundB 32 300 1 8 80 = 291 := by native_decide
example : disch 8 0 1 8 0 = 0 := by native_decide
example : disch 8 0 1 8 1 = 0 := by native_decide
example : disch 8 0 1 8 59 = 0 := by native_decide
example : disch 8 0 1 8 60 = 0 := by native_decide
example : disch 8 0 1 8 61 = 0 := by native_decide
example : disch 8 0 1 8 200 = 0 := by native_decide
example : disch 8 0 1 8 1000 = 0 := by native_decide
example : step 8 0 1 8 0 0 = 0 := by native_decide
example : step 8 0 1 8 0 40 = 0 := by native_decide
example : step 8 0 1 8 58 40 = 0 := by native_decide
example : step 8 0 1 8 120 0 = 0 := by native_decide
example : step 8 0 1 8 291 50 = 0 := by native_decide
example : boundB 8 0 1 8 0 = 0 := by native_decide
example : boundB 8 0 1 8 1 = 0 := by native_decide
example : boundB 8 0 1 8 40 = 0 := by native_decide
example : boundB 8 0 1 8 80 = 0 := by native_decide
example : settleSteps 16 1 160 = 46 := by native_decide
example : settleSteps 32 2 221 = 51 := by native_decide
example : settleSteps 32 1 341 = 95 := by native_decide
example : settleSteps 8 1 100 = 24 := by native_decide
example : settleSteps 1 1 50 = 1 := by native_decide
example : settleSteps 100 7 2000 = 76 := by native_decide
example : settleSteps 16 1 0 = 0 := by native_decide
example : splitmixNth (0 : UInt64) 0 = (16294208416658607535 : UInt64) := by native_decide
example : splitmixNth (0 : UInt64) 1 = (7960286522194355700 : UInt64) := by native_decide
example : splitmixNth (0 : UInt64) 2 = (487617019471545679 : UInt64) := by native_decide
example : splitmixNth (0 : UInt64) 3 = (17909611376780542444 : UInt64) := by native_decide
example : splitmixNth (0 : UInt64) 4 = (1961750202426094747 : UInt64) := by native_decide
example : splitmixNth (1 : UInt64) 0 = (10451216379200822465 : UInt64) := by native_decide
example : splitmixNth (1 : UInt64) 1 = (13757245211066428519 : UInt64) := by native_decide
example : splitmixNth (1 : UInt64) 2 = (17911839290282890590 : UInt64) := by native_decide
example : splitmixNth (1 : UInt64) 3 = (8196980753821780235 : UInt64) := by native_decide
example : splitmixNth (1 : UInt64) 4 = (8195237237126968761 : UInt64) := by native_decide
example : splitmixNth (12345 : UInt64) 0 = (2454886589211414944 : UInt64) := by native_decide
example : splitmixNth (12345 : UInt64) 1 = (3778200017661327597 : UInt64) := by native_decide
example : splitmixNth (12345 : UInt64) 2 = (2205171434679333405 : UInt64) := by native_decide
example : splitmixNth (12345 : UInt64) 3 = (3248800117070709450 : UInt64) := by native_decide
example : splitmixNth (12345 : UInt64) 4 = (9350289611492784363 : UInt64) := by native_decide
example : splitmixNth (18446744073709551615 : UInt64) 0 = (16490336266968443936 : UInt64) := by native_decide
example : splitmixNth (18446744073709551615 : UInt64) 1 = (16834447057089888969 : UInt64) := by native_decide
example : splitmixNth (18446744073709551615 : UInt64) 2 = (4048727598324417001 : UInt64) := by native_decide
example : splitmixNth (18446744073709551615 : UInt64) 3 = (7862637804313477842 : UInt64) := by native_decide
example : splitmixNth (18446744073709551615 : UInt64) 4 = (13015481187462834606 : UInt64) := by native_decide
example : deriveSeed (0 : UInt64) (0 : UInt64) (0 : UInt64) = (16294208416658607535 : UInt64) := by native_decide
example : deriveSeed (99 : UInt64) (336337654597 : UInt64) (3 : UInt64) = (8983281105084649067 : UInt64) := by native_decide
example : deriveSeed (20261015 : UInt64) (336337654597 : UInt64) (39 : UInt64) = (10395921172376395319 : UInt64) := by native_decide
example : deriveSeed (18446744073709551615 : UInt64) (1 : UInt64) (2 : UInt64) = (2419298318913870571 : UInt64) := by native_decide
