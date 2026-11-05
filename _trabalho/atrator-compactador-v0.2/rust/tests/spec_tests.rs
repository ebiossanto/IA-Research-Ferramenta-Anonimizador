//! Testes da especificação inteira (espelham python/tests/test_spec.py e test_rng.py).
//!
//! @trace T-RNG @trace T-D-REM @trace T-D-CONTRACT @trace T-D-MONO @trace T-D-POS
//! @trace T-ISS-LYAP @trace T-ISS-INV @trace T-ISS-CLOSED @trace T-LAT @trace T-DP-GEO
//! @trace T-DP-TRI

use atrator::exposure::*;
use atrator::rng::{derive_seed, SplitMix64};

#[test]
fn known_answer_splitmix64_seed0() {
    // @trace T-RNG : sequência de referência publicada do SplitMix64 com semente 0
    let mut s = SplitMix64::new(0);
    assert_eq!(s.next_u64(), 0xE220A8397B1DCDAF);
    assert_eq!(s.next_u64(), 0x6E789E6AA1B965F4);
    assert_eq!(s.next_u64(), 0x06C45D188009454F);
}

#[test]
fn determinism_and_derive() {
    let a = SplitMix64::new(42).next_u64();
    let b = SplitMix64::new(42).next_u64();
    assert_eq!(a, b);
    assert_ne!(derive_seed(1, 2, 3), derive_seed(1, 2, 4));
    assert_ne!(derive_seed(1, 2, 3), derive_seed(1, 3, 3));
}

#[test]
fn below_range_and_edge() {
    let mut r = SplitMix64::new(9);
    assert_eq!(r.below(1), 0);
    for &n in [2u64, 3, 7, 10, 1000, (1u64 << 63) + 5].iter() {
        for _ in 0..200 {
            assert!(r.below(n) < n);
        }
    }
}

#[test]
fn removal_spec_exhaustive() {
    // @trace T-D-REM
    for d in 1u64..=40 {
        for g in 1u64..=d {
            for v in 0u64..=300 {
                let r = removal(d, g, v);
                assert!(g * v <= d * r, "d={} g={} v={}", d, g, v);
                assert!(r <= v);
            }
        }
    }
}

#[test]
fn discharge_contract_exhaustive() {
    // @trace T-D-CONTRACT
    for d in 1u64..=40 {
        for g in 1u64..=d {
            for v in 0u64..=300 {
                let u2 = discharge_ceil(d, g, v);
                assert!(contract_holds(d, g, v, u2));
                assert!(u2 <= v);
            }
        }
    }
}

#[test]
fn mono_aux() {
    // @trace T-D-MONO
    for d in 1u64..=12 {
        for g in 0u64..=d {
            for a in 0u64..=20 {
                for b in a..=20 {
                    assert!(mono_aux_holds(d, g, a, b));
                }
            }
        }
    }
}

#[test]
fn positive_removal_and_strict_decrease() {
    // @trace T-D-POS
    for d in 1u64..=40 {
        for g in 1u64..=d {
            for v in 1u64..200 {
                assert!(removal(d, g, v) >= 1);
                assert!(discharge_ceil(d, g, v) < v);
            }
        }
    }
}

#[test]
fn f_is_monotone_with_unit_increments() {
    // @trace T-LAT : base da prova — f(R) = R - removal(d,g,R) é não decrescente, incrementos 0/1
    for d in 1u64..=40 {
        for g in 1u64..=d {
            let mut prev: i64 = 0;
            for r in 0u64..=500 {
                let fr = (r - removal(d, g, r)) as i64;
                if r > 0 {
                    let diff = fr - prev;
                    assert!(diff == 0 || diff == 1, "d={} g={} r={}", d, g, r);
                }
                prev = fr;
            }
        }
    }
}

#[test]
fn bound_is_minimal_and_valid() {
    // @trace T-ISS-INV
    for d in 2u64..20 {
        for g0 in 1u64..=d {
            for g1 in g0..=d {
                for &theta in [0u64, 7, 60].iter() {
                    for &cap in [0u64, 1, 13, 80].iter() {
                        let b = bound_b(d, theta, g0, g1, cap);
                        assert!(d * theta <= d * b + g0 * theta);
                        assert!(d * cap <= g1 * b + g1 * cap);
                        if b > 0 {
                            let bm = b - 1;
                            let ok = d * theta <= d * bm + g0 * theta && d * cap <= g1 * bm + g1 * cap;
                            assert!(!ok);
                        }
                    }
                }
            }
        }
    }
}

#[test]
fn lyapunov_and_invariance_random() {
    // @trace T-ISS-LYAP @trace T-ISS-INV
    let mut rng = SplitMix64::new(1234);
    for _ in 0..4000 {
        let d = 2 + rng.below(63);
        let g0 = 1 + rng.below(d);
        let g1 = g0 + rng.below(d - g0 + 1);
        let theta = rng.below(300);
        let cap = 1 + rng.below(60);
        let b = bound_b(d, theta, g0, g1, cap);
        let mut u = rng.below(b + 1);
        for _ in 0..120 {
            let iota = rng.below(cap + 1);
            let v = u + iota;
            let u2 = step(d, theta, g0, g1, u, iota);
            assert!(d * u2 + g0 * v <= d * v); // Lyapunov (g0)
            assert!(u2 <= b); // invariância de [0,B]
            assert!(contract_holds(d, rate(theta, g0, g1, v), v, u2));
            u = u2;
        }
    }
}

#[test]
fn closed_form_random() {
    // @trace T-ISS-CLOSED : vale para QUALQUER u0 (inclusive acima de B); d <= 16, k <= 24 (sem estouro)
    let mut rng = SplitMix64::new(777);
    for _ in 0..3000 {
        let d = 2 + rng.below(15);
        let g0 = 1 + rng.below(d);
        let g1 = g0 + rng.below(d - g0 + 1);
        let theta = rng.below(200);
        let cap = 1 + rng.below(50);
        let u0 = rng.below(5000);
        let mut u = u0;
        for k in 1u32..=24 {
            u = step(d, theta, g0, g1, u, rng.below(cap + 1));
            assert_eq!(iss_closed_holds(d, g0, cap, u0, k, u), Some(true), "d={} g0={} k={}", d, g0, k);
        }
    }
}

#[test]
fn decay_to_zero_without_input() {
    // @trace T-D-POS @trace T-LAT : sem injeção a exposição chega a 0 em <= settle_steps(d,g0,u0) passos
    let mut rng = SplitMix64::new(5);
    for _ in 0..500 {
        let d = 2 + rng.below(40);
        let g0 = 1 + rng.below(d);
        let g1 = g0 + rng.below(d - g0 + 1);
        let mut u = rng.below(3000);
        let bound = settle_steps(d, g0, u);
        let mut k: u64 = 0;
        while u > 0 {
            u = disch(d, rng.below(100), g0, g1, u);
            k += 1;
            assert!(k <= bound);
        }
    }
}

#[test]
fn geo_ratio_exhaustive() {
    // @trace T-DP-GEO
    for q in 1u64..10 {
        for p in 1u64..=q {
            for big_q in 0u32..6 {
                for m in 0u32..13 {
                    for n in 0u32..=(m + big_q) {
                        assert_eq!(geo_ratio_holds(p, q, big_q, m, n), Some(true));
                    }
                }
            }
        }
    }
}

#[test]
fn dist_triangle_inequality() {
    // @trace T-DP-TRI : |x-z| <= |x-y| + |y-z| (espelha lean/AtratorExtras/Distance.lean)
    for x in -20i64..=20 {
        for y in -20i64..=20 {
            for z in -20i64..=20 {
                assert!((x - z).unsigned_abs() <= (x - y).unsigned_abs() + (y - z).unsigned_abs());
            }
        }
    }
}
