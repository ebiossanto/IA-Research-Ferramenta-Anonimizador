"""Propriedades de privacidade do ruído geométrico bilateral.
@trace T-DP-EPS @trace T-DP-INFO @trace T-DP-UTIL @trace T-DP-GEO
"""
import math
import unittest
from fractions import Fraction

from . import _path  # noqa: F401
from .test_rng import pmf


class TestDp(unittest.TestCase):
    P, Q_, Q = 39, 41, 20

    def test_pmf_ratio_bounded_and_tight(self):
        # @trace T-DP-EPS : e^eps0 = (q/p)^Q ; razão exata dos pmf <= isso para todo z; atingida nas caudas
        p, q, Q = self.P, self.Q_, self.Q
        bound = Fraction(q, p) ** Q
        for s in range(0, Q + 1):
            worst = Fraction(0)
            for z in range(-300, 301):
                r = pmf(p, q, z) / pmf(p, q, z - s)
                self.assertLessEqual(r, Fraction(q, p) ** s)
                worst = max(worst, r)
            self.assertEqual(worst, Fraction(q, p) ** s)           # tight
        self.assertEqual(pmf(p, q, -300) / pmf(p, q, -300 - Q), bound)

    def test_eps0_value(self):
        eps0 = self.Q * math.log(self.Q_ / self.P)
        self.assertAlmostEqual(eps0, 1.0004, places=3)

    def test_normalization(self):
        s = sum(float(pmf(self.P, self.Q_, z)) for z in range(-4000, 4001))
        self.assertAlmostEqual(s, 1.0, places=9)

    def test_utility_closed_form(self):
        # @trace T-DP-UTIL : E|Z| = 2a/(1-a^2) = 1/sinh(eps0/Q) ; Var = 2a/(1-a)^2
        a = self.P / self.Q_
        ez = sum(abs(z) * float(pmf(self.P, self.Q_, z)) for z in range(-4000, 4001))
        self.assertAlmostEqual(ez, 2 * a / (1 - a * a), places=7)
        self.assertAlmostEqual(ez, 1 / math.sinh(-math.log(a)), places=7)
        var = sum(z * z * float(pmf(self.P, self.Q_, z)) for z in range(-4000, 4001))
        self.assertAlmostEqual(var, 2 * a / (1 - a) ** 2, places=5)

    def test_mutual_information_bound(self):
        # @trace T-DP-INFO : I(X;Y) <= log2( 2 e^eps / (e^eps + 1) ) <= min(eps*log2 e, 1)
        for (p, q, Q) in ((39, 41, 20), (19, 20, 10), (9, 10, 3), (1, 2, 1)):
            eps = Q * math.log(q / p)
            mi = 0.0
            for y in range(-600, 600 + Q):
                p0 = float(pmf(p, q, y))
                p1 = float(pmf(p, q, y - Q))
                pm = 0.5 * (p0 + p1)
                if p0 > 0:
                    mi += 0.5 * p0 * math.log2(p0 / pm)
                if p1 > 0:
                    mi += 0.5 * p1 * math.log2(p1 / pm)
            bound = math.log2(2 * math.exp(eps) / (math.exp(eps) + 1))
            self.assertLessEqual(mi, bound + 1e-9)
            self.assertLessEqual(bound, min(eps * math.log2(math.e), 1.0) + 1e-12)

    def test_any_test_has_advantage_bounded_by_eps(self):
        # consequência operacional da DP: TPR <= e^eps * FPR para todo limiar (somas de cauda em float)
        p, q, Q = self.P, self.Q_, self.Q
        a = p / q
        c = (q - p) / (q + p)
        lo, hi = -400, 3000
        f0 = {y: c * a ** abs(y) for y in range(lo, hi)}          # saída sob "ausente"
        f1 = {y: c * a ** abs(y - Q) for y in range(lo, hi)}      # saída sob "presente"
        e = (q / p) ** Q
        t0 = t1 = 0.0
        for tau in range(hi - 1, lo - 1, -1):                     # soma de cauda incremental
            t0 += f0[tau]
            t1 += f1[tau]
            if -120 <= tau < 160:
                self.assertLessEqual(t1, e * t0 + 1e-12)


if __name__ == "__main__":
    unittest.main()
