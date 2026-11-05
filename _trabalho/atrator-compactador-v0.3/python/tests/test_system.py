"""Testes do sistema completo (injeção -> D -> C -> evicção).
@trace T-LAT @trace T-F-EVICT @trace T-F-DROP @trace T-F-ANON @trace T-DP-SENS
@trace T-WIPE @trace T-TIMELINE @trace T-GOLD
"""
import os
import unittest

from . import _path  # noqa: F401
from .test_rng import pmf  # noqa: F401
from atrator_ref.rng import SplitMix64
from atrator_ref.spec import bound_B, settle_steps
from atrator_ref.system import (COMP, IRR, SCENARIOS, Compactor, Record, golden_text, run)

GOLDEN = os.path.join(_path.PKG_ROOT, "results", "golden", "scenarios.kv")


def synth_records(widx, m=3, n=6, Q=20, start_id=0):
    rng = SplitMix64(1000 + widx)
    out = []
    for i in range(n):
        a = rng.below(m)
        q = 1 + rng.below(Q)
        klass = IRR if rng.below(5) == 0 else COMP
        out.append(Record(start_id + i, a, q, klass, widx))
    return out


class TestScenarios(unittest.TestCase):
    def test_invariants_all_scenarios(self):
        for cfg in SCENARIOS:
            mt, ring, _ = run(cfg)
            self.assertEqual(mt["bound_violations"], 0, cfg["name"])
            self.assertEqual(mt["contract_violations"], 0, cfg["name"])
            self.assertEqual(mt["latency_violations"], 0, cfg["name"])
            self.assertLessEqual(mt["max_settle_latency"], mt["latency_bound"])       # T-LAT
            self.assertLessEqual(mt["max_raw_age_at_erase"], mt["raw_age_bound"])      # T-TIMELINE
            self.assertLessEqual(mt["max_exposure"], mt["bound_B"])                    # T-ISS-INV
            self.assertEqual(mt["bytes_erased"], 8 * mt["records_erased"])             # T-WIPE
            self.assertLessEqual(len(ring), cfg["W"])
            self.assertEqual(mt["windows_evicted"], mt["windows_sealed"] - len(ring))  # T-F-EVICT
            self.assertEqual(mt["records_injected"] + mt["records_dropped_by_cap"], mt["records_generated"])

    def test_cap_drops_happen_in_burst(self):
        burst = [c for c in SCENARIOS if c["name"] == "burst"][0]
        mt, _, _ = run(burst)
        self.assertGreater(mt["records_dropped_by_cap"], 0)

    def test_exact_mode_has_zero_error(self):
        exact = [c for c in SCENARIOS if c["name"] == "exact"][0]
        mt, _, _ = run(exact)
        self.assertEqual(mt["abs_error_sum"], 0)

    def test_stop_scenario_decays_to_zero(self):
        # @trace T-TIMELINE : "resíduo tende a zero" quando a injeção cessa
        cfg = [c for c in SCENARIOS if c["name"] == "stop"][0]
        mt, _, _ = run(cfg)
        self.assertGreater(mt["exposure_at_stop"], 0)
        self.assertGreaterEqual(mt["first_zero_after_stop"], cfg["stop_at"])
        B = bound_B(cfg["d"], cfg["theta"], cfg["g0"], cfg["g1"], cfg["I"])
        self.assertLessEqual(mt["first_zero_after_stop"] - cfg["stop_at"], settle_steps(cfg["d"], cfg["g0"], B))
        self.assertEqual(mt["live_final_exposure"], 0)

    def test_determinism(self):
        cfg = SCENARIOS[0]
        a, _, _ = run(cfg)
        b, _, _ = run(cfg)
        self.assertEqual(a, b)

    def test_golden_file_matches(self):
        # @trace T-GOLD
        with open(GOLDEN, encoding="utf-8") as f:
            self.assertEqual(golden_text(), f.read())

    def test_identity_is_erased_structurally(self):
        # @trace T-F-ANON : trocar id/payload de TODOS os registros não muda nada no estado
        cfg = SCENARIOS[0]
        base, ring0, _ = run(cfg)

        def scramble(rec):
            rec.id = (rec.id * 7919 + 13) & 0xFFFFFFFF
            rec.payload[:] = bytearray([(rec.id + i) & 0xFF for i in range(8)])

        mt, ring1, _ = run(cfg, tamper=scramble)
        self.assertEqual(base, mt)
        self.assertEqual(ring0, ring1)


class TestForgetting(unittest.TestCase):
    M, W, NOISE, SEED = 3, 4, (39, 41), 99

    def _ring_after(self, extra, windows):
        c = Compactor(self.M, self.W, self.NOISE)
        snaps = []
        for w in range(windows):
            recs = synth_records(w, self.M)
            if extra is not None and w == 0:
                recs.append(extra)
            c.seal(w, recs, self.SEED, now=w)
            snaps.append((list(c.state()), [(i, list(s)) for i, s in c.windows]))
        return snaps

    def test_eviction_makes_state_independent_of_old_window(self):
        # @trace T-F-EVICT : janela 0 contém (ou não) um registro extra de magnitude 17 na coordenada 1
        extra = Record(10_000, 1, 17, COMP, 0)
        A = self._ring_after(None, self.W + 3)
        B = self._ring_after(extra, self.W + 3)
        for j in range(self.W + 3):                 # j+1 janelas seladas
            if j + 1 <= self.W:                     # janela 0 ainda no anel: diferença EXATA = 17 na coord 1
                diff = [b - a for a, b in zip(A[j][0], B[j][0])]
                self.assertEqual(diff, [0, 17, 0, 0, 0, 0])
            else:                                   # evictada: estados e anéis idênticos
                self.assertEqual(A[j][0], B[j][0])
                self.assertEqual(A[j][1], B[j][1])

    def test_drop_window_gives_exact_independence(self):
        # @trace T-F-DROP
        extra = Record(10_000, 2, 9, IRR, 0)
        ca = Compactor(self.M, 10, self.NOISE)
        cb = Compactor(self.M, 10, self.NOISE)
        for w in range(5):
            ra = synth_records(w, self.M)
            rb = synth_records(w, self.M)
            if w == 2:
                rb.append(extra)
            ca.seal(w, ra, self.SEED, now=w)
            cb.seal(w, rb, self.SEED, now=w)
        self.assertNotEqual(ca.state(), cb.state())
        self.assertTrue(ca.drop_window(2))
        self.assertTrue(cb.drop_window(2))
        self.assertEqual(ca.windows, cb.windows)
        self.assertEqual(ca.state(), cb.state())
        self.assertFalse(ca.drop_window(2))

    def test_sensitivity_one_record_one_coordinate(self):
        # @trace T-DP-SENS (modo exato: sem ruído)
        for klass, anchor, q in ((COMP, 0, 20), (IRR, 2, 5), (COMP, 1, 1)):
            c1 = Compactor(self.M, 3, None)
            c2 = Compactor(self.M, 3, None)
            base = synth_records(0, self.M)
            c1.seal(0, base, 1, now=0)
            c2.seal(0, synth_records(0, self.M) + [Record(77, anchor, q, klass, 0)], 1, now=0)
            diff = [b - a for a, b in zip(c1.state(), c2.state())]
            idx = anchor if klass == COMP else self.M + anchor
            expect = [0] * (2 * self.M)
            expect[idx] = q
            self.assertEqual(diff, expect)

    def test_wipe_zeroes_payload(self):
        # @trace T-WIPE
        c = Compactor(self.M, 3, None)
        recs = synth_records(0, self.M)
        self.assertTrue(any(any(r.payload) for r in recs))
        rep = c.seal(0, recs, 1, now=0)
        self.assertEqual(rep["erased_records"], len(recs))
        self.assertEqual(rep["erased_bytes"], 8 * len(recs))
        for r in recs:
            self.assertFalse(any(r.payload))


if __name__ == "__main__":
    unittest.main()
