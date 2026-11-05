//! Propriedades do ruído geométrico bilateral (espelham python/tests/test_dp.py).
//!
//! @trace T-SAM @trace T-DP-EPS @trace T-DP-INFO @trace T-DP-UTIL

use atrator::system::sampler_histogram;

fn pmf(p: f64, q: f64, z: i64) -> f64 {
    let a = p / q;
    (1.0 - a) / (1.0 + a) * a.powi(z.unsigned_abs() as i32)
}

#[test]
fn sampler_matches_pmf() {
    // @trace T-SAM : o amostrador bate com P[Z=z] = (q-p)/(q+p) (p/q)^|z|
    let (p, q, n) = (39u64, 41u64, 40000u64);
    let (counts, _below, _above, s, _sa) = sampler_histogram(n, p, q, 2026, -12, 12);
    let mut worst: f64 = 0.0;
    for (i, c) in counts.iter().enumerate() {
        let z = -12 + i as i64;
        let dev = ((*c as f64) / (n as f64) - pmf(p as f64, q as f64, z)).abs();
        if dev > worst {
            worst = dev;
        }
    }
    assert!(worst < 0.004, "desvio máximo {}", worst);
    let mean = (s as f64) / (n as f64);
    assert!(mean.abs() < 0.6, "média {}", mean);
}

#[test]
fn eps0_value() {
    // @trace T-DP-EPS : eps0 = Q ln(q/p) com Q=20, p/q=39/41
    let eps0 = 20.0 * (41.0f64 / 39.0).ln();
    assert!((eps0 - 1.0002).abs() < 1e-3, "eps0 {}", eps0);
}

#[test]
fn pmf_ratio_is_bounded_and_tight() {
    // @trace T-DP-EPS : razão exata dos pmf <= (q/p)^s e atingida nas caudas
    let (p, q) = (39.0f64, 41.0f64);
    for s in 0i64..=20 {
        let bound = (q / p).powi(s as i32);
        let mut worst: f64 = 0.0;
        for z in -300i64..=300 {
            let r = pmf(p, q, z) / pmf(p, q, z - s);
            if r > worst {
                worst = r;
            }
            assert!(r <= bound * (1.0 + 1e-9));
        }
        assert!((worst / bound - 1.0).abs() < 1e-9);
    }
}

#[test]
fn utility_closed_form() {
    // @trace T-DP-UTIL : E|Z| = 2a/(1-a^2) ; Var = 2a/(1-a)^2
    let (p, q) = (39.0f64, 41.0f64);
    let a = p / q;
    let mut ez = 0.0;
    let mut var = 0.0;
    for z in -4000i64..=4000 {
        ez += (z.unsigned_abs() as f64) * pmf(p, q, z);
        var += (z as f64) * (z as f64) * pmf(p, q, z);
    }
    assert!((ez - 2.0 * a / (1.0 - a * a)).abs() < 1e-6);
    assert!((var - 2.0 * a / ((1.0 - a) * (1.0 - a))).abs() < 1e-3);
}

#[test]
fn mutual_information_bound() {
    // @trace T-DP-INFO : I(X;Y) <= log2( 2 e^eps / (e^eps + 1) ) <= min(eps*log2 e, 1)
    for &(p, q, big_q) in [(39.0f64, 41.0f64, 20i64), (19.0, 20.0, 10), (9.0, 10.0, 3), (1.0, 2.0, 1)].iter() {
        let eps = (big_q as f64) * (q / p).ln();
        let mut mi = 0.0;
        for y in -600i64..(600 + big_q) {
            let p0 = pmf(p, q, y);
            let p1 = pmf(p, q, y - big_q);
            let pm = 0.5 * (p0 + p1);
            if p0 > 0.0 {
                mi += 0.5 * p0 * (p0 / pm).log2();
            }
            if p1 > 0.0 {
                mi += 0.5 * p1 * (p1 / pm).log2();
            }
        }
        let bound = (2.0 * eps.exp() / (eps.exp() + 1.0)).log2();
        assert!(mi <= bound + 1e-9, "mi {} bound {}", mi, bound);
        let loose = (eps * std::f64::consts::E.log2()).min(1.0);
        assert!(bound <= loose + 1e-12);
    }
}
