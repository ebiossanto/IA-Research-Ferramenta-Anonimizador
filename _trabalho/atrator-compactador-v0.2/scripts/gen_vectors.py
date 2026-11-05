#!/usr/bin/env python3
"""Gera os vetores diferenciais a partir do ORÁCULO Python:
   trace/vectors.csv                  (consumido por rust/tests/vectors_tests.rs)
   lean/AtratorExtras/Vectors.lean    (checado por `native_decide` no `lake build AtratorExtras`)
Determinístico. @trace T-GOLD
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "python"))
from atrator_ref.rng import SplitMix64, derive_seed  # noqa: E402
from atrator_ref.spec import (bound_B, disch, discharge_ceil, rate, removal,  # noqa: E402
                              settle_steps, step)

rows = []  # (função, args..., esperado)

for d in (1, 2, 3, 8, 16, 32, 100, 1000):
    for g in sorted({1, max(1, d // 2), d}):
        for v in (0, 1, 2, 3, 7, 8, 9, 100, 12345, 1000000):
            rows.append(("removal", d, g, v, removal(d, g, v)))
            rows.append(("discharge_ceil", d, g, v, discharge_ceil(d, g, v)))

for theta in (0, 50):
    for (g0, g1) in ((1, 4), (2, 16), (3, 3)):
        for v in (0, 49, 50, 51, 1000):
            rows.append(("rate", theta, g0, g1, v, rate(theta, g0, g1, v)))

for (d, theta, g0, g1) in ((16, 60, 1, 4), (32, 150, 2, 16), (32, 300, 1, 8), (8, 0, 1, 8)):
    for v in (0, 1, 59, 60, 61, 200, 1000):
        rows.append(("disch", d, theta, g0, g1, v, disch(d, theta, g0, g1, v)))
    for (u, iota) in ((0, 0), (0, 40), (58, 40), (120, 0), (291, 50)):
        rows.append(("step", d, theta, g0, g1, u, iota, step(d, theta, g0, g1, u, iota)))
    for cap in (0, 1, 40, 80):
        rows.append(("bound_b", d, theta, g0, g1, cap, bound_B(d, theta, g0, g1, cap)))

for (d, g0, R) in ((16, 1, 160), (32, 2, 221), (32, 1, 341), (8, 1, 100), (1, 1, 50), (100, 7, 2000), (16, 1, 0)):
    rows.append(("settle_steps", d, g0, R, settle_steps(d, g0, R)))

for seed in (0, 1, 12345, (1 << 64) - 1):
    s = SplitMix64(seed)
    for idx in range(5):
        rows.append(("splitmix", seed, idx, s.next_u64()))

for (seed, a, b) in ((0, 0, 0), (99, 0x4E4F495345, 3), (20261015, 0x4E4F495345, 39), ((1 << 64) - 1, 1, 2)):
    rows.append(("derive_seed", seed, a, b, derive_seed(seed, a, b)))

with open(os.path.join(ROOT, "trace", "vectors.csv"), "w", encoding="utf-8") as f:
    f.write("# vetores diferenciais gerados por scripts/gen_vectors.py (oráculo Python). função,args...,esperado\n")
    for r in rows:
        f.write(",".join(str(x) for x in r) + "\n")

lean = ['import AtratorCore.Exposure', 'import AtratorExtras.Prng', '',
        '/-!', '# Vetores diferenciais (gerado por `scripts/gen_vectors.py` — NÃO editar à mão)', '',
        'Cada `example` afirma que a definição em Lean produz o mesmo valor que o oráculo Python e a',
        'implementação Rust (`trace/vectors.csv`). Usa `native_decide` (avaliação compilada).',
        '@trace T-RNG @trace T-D-REM @trace T-D-CONTRACT @trace T-ISS-INV @trace T-LAT @trace T-GOLD', '-/', '',
        'open Atrator', '']
for r in rows:
    fn, args, exp = r[0], r[1:-1], r[-1]
    a = " ".join(str(x) for x in args)
    if fn == "removal":
        lean.append("example : removal %s = %d := by native_decide" % (a, exp))
    elif fn == "discharge_ceil":
        lean.append("example : dischargeCeil %s = %d := by native_decide" % (a, exp))
    elif fn == "rate":
        lean.append("example : rate %s = %d := by native_decide" % (a, exp))
    elif fn == "disch":
        lean.append("example : disch %s = %d := by native_decide" % (a, exp))
    elif fn == "step":
        lean.append("example : step %s = %d := by native_decide" % (a, exp))
    elif fn == "bound_b":
        lean.append("example : boundB %s = %d := by native_decide" % (a, exp))
    elif fn == "settle_steps":
        lean.append("example : settleSteps %s = %d := by native_decide" % (a, exp))
    elif fn == "splitmix":
        lean.append("example : splitmixNth (%d : UInt64) %d = (%d : UInt64) := by native_decide" % (args[0], args[1], exp))
    elif fn == "derive_seed":
        lean.append("example : deriveSeed (%d : UInt64) (%d : UInt64) (%d : UInt64) = (%d : UInt64) := by native_decide"
                    % (args[0], args[1], args[2], exp))
with open(os.path.join(ROOT, "lean", "AtratorExtras", "Vectors.lean"), "w", encoding="utf-8") as f:
    f.write("\n".join(lean) + "\n")
print("vetores:", len(rows))
