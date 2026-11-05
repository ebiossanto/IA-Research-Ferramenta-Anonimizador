"""Testes da especificação inteira.
@trace T-D-REM @trace T-D-CONTRACT @trace T-D-MONO @trace T-D-POS @trace T-ISS-LYAP
@trace T-ISS-INV @trace T-ISS-CLOSED @trace T-DP-GEO @trace T-LAT @trace T-DP-TRI
"""
import unittest

from . import _path  # noqa: F401
from atrator_ref.rng import SplitMix64
from atrator_ref.spec import (bound_B, contract_holds, disch, discharge_ceil, geo_ratio_holds,
                              iss_closed_holds, mono_aux_holds, rate, removal, settle_steps, step)


class TestDischarge(unittest.TestCase):
    def test_removal_spec_exhaustive(self):
        # @trace T-D-REM
        n = 0
        for d in range(1, 41):
            for g in range(1, d + 1):
                for v in range(0, 301):
                    r = removal(d, g, v)
                    self.assertLessEqual(g * v, d * r)
                    self.assertLessEqual(r, v)
                    n += 1
        self.assertGreater(n, 100000)

    def test_discharge_contract_exhaustive(self):
        # @trace T-D-CONTRACT
        for d in range(1, 41):
            for g in range(1, d + 1):
                for v in range(0, 301):
                    self.assertTrue(contract_holds(d, g, v, discharge_ceil(d, g, v)))
                    self.assertLessEqual(discharge_ceil(d, g, v), v)

    def test_mono_aux(self):
        # @trace T-D-MONO
        for d in range(1, 13):
            for g in range(0, d + 1):
                for a in range(0, 21):
                    for b in range(a, 21):
                        self.assertTrue(mono_aux_holds(d, g, a, b))

    def test_positive_removal_and_strict_decrease(self):
        # @trace T-D-POS
        for d in range(1, 41):
            for g in range(1, d + 1):
                for v in range(1, 200):
                    self.assertGreaterEqual(removal(d, g, v), 1)
                    self.assertLess(discharge_ceil(d, g, v), v)

    def test_f_is_monotone_with_unit_increments(self):
        # base da prova de T-LAT: f(R) = R - removal(d,g0,R) é não decrescente com incrementos 0/1
        for d in range(1, 41):
            for g in range(1, d + 1):
                prev = 0
                for R in range(0, 501):
                    fR = R - removal(d, g, R)
                    if R > 0:
                        self.assertIn(fR - prev, (0, 1))
                    prev = fR


class TestIss(unittest.TestCase):
    def test_bound_is_minimal_and_valid(self):
        for d in range(2, 20):
            for g0 in range(1, d + 1):
                for g1 in range(g0, d + 1):
                    for theta in (0, 7, 60):
                        for I in (0, 1, 13, 80):
                            B = bound_B(d, theta, g0, g1, I)
                            self.assertLessEqual(d * theta, d * B + g0 * theta)
                            self.assertLessEqual(d * I, g1 * B + g1 * I)
                            if B > 0:
                                Bm = B - 1
                                ok = (d * theta <= d * Bm + g0 * theta) and (d * I <= g1 * Bm + g1 * I)
                                self.assertFalse(ok)

    def test_lyapunov_and_invariance_random(self):
        # @trace T-ISS-LYAP @trace T-ISS-INV
        rng = SplitMix64(1234)
        for _ in range(4000):
            d = 2 + rng.below(63)
            g0 = 1 + rng.below(d)
            g1 = g0 + rng.below(d - g0 + 1)
            theta = rng.below(300)
            I = 1 + rng.below(60)
            B = bound_B(d, theta, g0, g1, I)
            u = rng.below(B + 1)
            for _k in range(120):
                iota = rng.below(I + 1)
                v = u + iota
                u2 = step(d, theta, g0, g1, u, iota)
                self.assertLessEqual(d * u2 + g0 * v, d * v)       # Lyapunov (g0)
                self.assertLessEqual(u2, B)                         # invariância de [0,B]
                self.assertTrue(contract_holds(d, rate(theta, g0, g1, v), v, u2))
                u = u2

    def test_closed_form_random(self):
        # @trace T-ISS-CLOSED : vale para QUALQUER u0 (inclusive acima de B)
        rng = SplitMix64(777)
        for _ in range(3000):
            d = 2 + rng.below(40)
            g0 = 1 + rng.below(d)
            g1 = g0 + rng.below(d - g0 + 1)
            theta = rng.below(200)
            I = 1 + rng.below(50)
            u0 = rng.below(5000)
            u = u0
            for k in range(1, 31):
                u = step(d, theta, g0, g1, u, rng.below(I + 1))
                self.assertTrue(iss_closed_holds(d, g0, I, u0, k, u), (d, g0, g1, theta, I, u0, k, u))

    def test_decay_to_zero_without_input(self):
        # @trace T-D-POS : sem injeção a exposição chega a 0 em <= settle_steps(d,g0,u0) passos
        rng = SplitMix64(5)
        for _ in range(500):
            d = 2 + rng.below(40)
            g0 = 1 + rng.below(d)
            g1 = g0 + rng.below(d - g0 + 1)
            u = rng.below(3000)
            bound = settle_steps(d, g0, u)
            k = 0
            while u > 0:
                u = disch(d, rng.below(100), g0, g1, u)
                k += 1
                self.assertLessEqual(k, bound)


class TestGeoRatio(unittest.TestCase):
    def test_geo_ratio_exhaustive(self):
        # @trace T-DP-GEO
        for q in range(1, 10):
            for p in range(1, q + 1):
                for Q in range(0, 6):
                    for m in range(0, 13):
                        for n in range(0, m + Q + 1):
                            self.assertTrue(geo_ratio_holds(p, q, Q, m, n))

    def test_dist_triangle_inequality(self):
        # @trace T-DP-TRI : |x-z| <= |x-y| + |y-z| (espelha lean/AtratorExtras/Distance.lean)
        for x in range(-20, 21):
            for y in range(-20, 21):
                for z in range(-20, 21):
                    self.assertLessEqual(abs(x - z), abs(x - y) + abs(y - z))

    def test_geo_ratio_fails_without_triangle(self):
        # sanidade: se n > m+Q (viola a desigualdade triangular) e p<q, a desigualdade falha
        self.assertFalse(geo_ratio_holds(1, 2, 1, 0, 5))


if __name__ == "__main__":
    unittest.main()
