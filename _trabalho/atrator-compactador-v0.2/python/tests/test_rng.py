"""Testes do gerador e do amostrador.  @trace T-RNG  @trace T-SAM"""
import unittest
from fractions import Fraction

from . import _path  # noqa: F401
from atrator_ref.rng import SplitMix64, derive_seed, fnv1a64_ints


def pmf(p, q, z):
    return Fraction(q - p, q + p) * Fraction(p, q) ** abs(z)


class TestRng(unittest.TestCase):
    def test_known_answer_splitmix64_seed0(self):
        # @trace T-RNG : sequência de referência publicada do SplitMix64 com semente 0
        s = SplitMix64(0)
        self.assertEqual(s.next_u64(), 0xE220A8397B1DCDAF)
        self.assertEqual(s.next_u64(), 0x6E789E6AA1B965F4)
        self.assertEqual(s.next_u64(), 0x06C45D188009454F)

    def test_determinism_and_derive(self):
        a = [SplitMix64(42).next_u64() for _ in range(3)]
        b = [SplitMix64(42).next_u64() for _ in range(3)]
        self.assertEqual(a, b)
        self.assertNotEqual(derive_seed(1, 2, 3), derive_seed(1, 2, 4))
        self.assertNotEqual(derive_seed(1, 2, 3), derive_seed(1, 3, 3))

    def test_below_range_and_edge(self):
        r = SplitMix64(9)
        self.assertEqual(r.below(1), 0)
        for n in (2, 3, 7, 10, 1000, 2 ** 63 + 5):
            for _ in range(200):
                self.assertLess(r.below(n), n)

    def test_fnv_known(self):
        self.assertEqual(fnv1a64_ints([]), 0xCBF29CE484222325)
        self.assertNotEqual(fnv1a64_ints([1]), fnv1a64_ints([2]))

    def test_two_sided_geometric_matches_pmf(self):
        # @trace T-SAM : o amostrador bate com P[Z=z] = (q-p)/(q+p) (p/q)^|z|
        p, q, n = 39, 41, 40000
        r = SplitMix64(2026)
        counts = {}
        for _ in range(n):
            z = r.two_sided_geometric(p, q)
            counts[z] = counts.get(z, 0) + 1
        worst = 0.0
        for z in range(-12, 13):
            worst = max(worst, abs(counts.get(z, 0) / n - float(pmf(p, q, z))))
        self.assertLess(worst, 0.004)
        mean = sum(z * c for z, c in counts.items()) / n
        self.assertLess(abs(mean), 0.6)  # desvio-padrão teórico ≈ 28; erro-padrão da média ≈ 0.14


if __name__ == "__main__":
    unittest.main()
