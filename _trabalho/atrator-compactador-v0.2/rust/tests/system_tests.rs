//! Testes do sistema completo (espelham python/tests/test_system.py).
//!
//! @trace T-ISS-INV @trace T-LAT @trace T-F-EVICT @trace T-F-ANON @trace T-F-DROP
//! @trace T-DP-SENS @trace T-TIMELINE @trace T-WIPE @trace T-GOLD @trace T-DP-EPS

use atrator::compactor::Compactor;
use atrator::exposure::{bound_b, settle_steps};
use atrator::record::{wipe, Class, Record};
use atrator::report::golden_text;
use atrator::rng::SplitMix64;
use atrator::system::{run, run_with, scenarios};

const GOLDEN: &str = include_str!("../../results/golden/scenarios.kv");

fn synth_records(widx: u64, m: usize, n: usize, q_max: u64, start_id: u64) -> Vec<Record> {
    let mut rng = SplitMix64::new(1000 + widx);
    let mut out: Vec<Record> = Vec::new();
    for i in 0..n {
        let a = rng.below(m as u64) as usize;
        let q = 1 + rng.below(q_max);
        let class = if rng.below(5) == 0 { Class::Irreversible } else { Class::Compensable };
        out.push(Record::new(start_id + i as u64, a, q, class, widx));
    }
    out
}

#[test]
fn invariants_all_scenarios() {
    // @trace T-ISS-INV @trace T-LAT @trace T-TIMELINE @trace T-WIPE
    for cfg in scenarios().iter() {
        let (mt, ring) = run(cfg);
        assert_eq!(mt.bound_violations, 0, "{}", cfg.name);
        assert_eq!(mt.contract_violations, 0, "{}", cfg.name);
        assert_eq!(mt.latency_violations, 0, "{}", cfg.name);
        assert!(mt.max_settle_latency <= mt.latency_bound);
        assert!(mt.max_raw_age_at_erase <= mt.raw_age_bound);
        assert!(mt.max_exposure <= mt.bound_b);
        assert_eq!(mt.bytes_erased, 8 * mt.records_erased);
        assert!(ring.len() <= cfg.w);
        assert_eq!(mt.windows_evicted, mt.windows_sealed - ring.len() as u64);
        assert_eq!(mt.records_injected + mt.records_dropped_by_cap, mt.records_generated);
    }
}

#[test]
fn cap_drops_happen_in_burst() {
    let all = scenarios();
    let cfg = all.iter().find(|c| c.name == "burst").expect("burst");
    let (mt, _) = run(cfg);
    assert!(mt.records_dropped_by_cap > 0);
}

#[test]
fn exact_mode_has_zero_error() {
    let all = scenarios();
    let cfg = all.iter().find(|c| c.name == "exact").expect("exact");
    let (mt, _) = run(cfg);
    assert_eq!(mt.abs_error_sum, 0);
}

#[test]
fn stop_scenario_decays_to_zero() {
    // @trace T-TIMELINE : "resíduo tende a zero" quando a injeção cessa
    let all = scenarios();
    let cfg = all.iter().find(|c| c.name == "stop").expect("stop");
    let (mt, _) = run(cfg);
    assert!(mt.exposure_at_stop > 0);
    assert!(mt.first_zero_after_stop >= cfg.stop_at as i64);
    let b = bound_b(cfg.d, cfg.theta, cfg.g0, cfg.g1, cfg.i_cap);
    let after_stop = (mt.first_zero_after_stop - (cfg.stop_at as i64)) as u64;
    assert!(after_stop <= settle_steps(cfg.d, cfg.g0, b));
    assert_eq!(mt.live_final_exposure, 0);
}

#[test]
fn determinism() {
    let all = scenarios();
    let (a, ra) = run(&all[0]);
    let (b, rb) = run(&all[0]);
    assert_eq!(a, b);
    assert_eq!(ra, rb);
}

#[test]
fn golden_file_matches() {
    // @trace T-GOLD : saída do Rust == saída do oráculo Python, byte a byte
    assert_eq!(golden_text(), GOLDEN);
}

#[test]
fn identity_is_erased_structurally() {
    // @trace T-F-ANON : trocar id/payload de TODOS os registros não muda nada no estado
    let all = scenarios();
    let cfg = &all[0];
    let (base, ring0) = run(cfg);
    let mut scramble = |rec: &mut Record| {
        rec.id = (rec.id.wrapping_mul(7919).wrapping_add(13)) & 0xFFFF_FFFF;
        let id = rec.id;
        for (i, b) in rec.payload.iter_mut().enumerate() {
            *b = ((id as usize + i) & 0xFF) as u8;
        }
    };
    let (mt, ring1) = run_with(cfg, &mut scramble);
    assert_eq!(base, mt);
    assert_eq!(ring0, ring1);
}

const M: usize = 3;
const W: usize = 4;
const SEED: u64 = 99;

fn ring_after(extra: Option<Record>, windows: u64) -> Vec<(Vec<i64>, Vec<(u64, Vec<i64>)>)> {
    let mut c = Compactor::new(M, W, Some((39, 41)));
    let mut snaps: Vec<(Vec<i64>, Vec<(u64, Vec<i64>)>)> = Vec::new();
    for w in 0..windows {
        let mut recs = synth_records(w, M, 6, 20, 0);
        if w == 0 {
            if let Some(r) = extra.clone() {
                recs.push(r);
            }
        }
        let _ = c.seal(w, recs, SEED, w);
        snaps.push((c.state(), c.windows.iter().cloned().collect()));
    }
    snaps
}

#[test]
fn eviction_makes_state_independent_of_old_window() {
    // @trace T-F-EVICT : janela 0 contém (ou não) um registro extra de magnitude 17 na coordenada 1
    let extra = Record::new(10_000, 1, 17, Class::Compensable, 0);
    let a = ring_after(None, W as u64 + 3);
    let b = ring_after(Some(extra), W as u64 + 3);
    for j in 0..(W + 3) {
        if j + 1 <= W {
            let diff: Vec<i64> = a[j].0.iter().zip(b[j].0.iter()).map(|(x, y)| y - x).collect();
            assert_eq!(diff, vec![0, 17, 0, 0, 0, 0]);
        } else {
            assert_eq!(a[j].0, b[j].0);
            assert_eq!(a[j].1, b[j].1);
        }
    }
}

#[test]
fn drop_window_gives_exact_independence() {
    // @trace T-F-DROP
    let extra = Record::new(10_000, 2, 9, Class::Irreversible, 0);
    let mut ca = Compactor::new(M, 10, Some((39, 41)));
    let mut cb = Compactor::new(M, 10, Some((39, 41)));
    for w in 0u64..5 {
        let ra = synth_records(w, M, 6, 20, 0);
        let mut rb = synth_records(w, M, 6, 20, 0);
        if w == 2 {
            rb.push(extra.clone());
        }
        let _ = ca.seal(w, ra, SEED, w);
        let _ = cb.seal(w, rb, SEED, w);
    }
    assert_ne!(ca.state(), cb.state());
    assert!(ca.drop_window(2));
    assert!(cb.drop_window(2));
    assert_eq!(ca.windows, cb.windows);
    assert_eq!(ca.state(), cb.state());
    assert!(!ca.drop_window(2));
}

#[test]
fn sensitivity_one_record_one_coordinate() {
    // @trace T-DP-SENS (modo exato: sem ruído) @trace T-DP-EPS
    let cases = [(Class::Compensable, 0usize, 20u64), (Class::Irreversible, 2, 5), (Class::Compensable, 1, 1)];
    for &(class, anchor, q) in cases.iter() {
        let mut c1 = Compactor::new(M, 3, None);
        let mut c2 = Compactor::new(M, 3, None);
        let _ = c1.seal(0, synth_records(0, M, 6, 20, 0), 1, 0);
        let mut with_extra = synth_records(0, M, 6, 20, 0);
        with_extra.push(Record::new(77, anchor, q, class, 0));
        let _ = c2.seal(0, with_extra, 1, 0);
        let diff: Vec<i64> = c1.state().iter().zip(c2.state().iter()).map(|(x, y)| y - x).collect();
        let idx = if class == Class::Compensable { anchor } else { M + anchor };
        let mut expect = vec![0i64; 2 * M];
        expect[idx] = q as i64;
        assert_eq!(diff, expect);
    }
}

#[test]
fn wipe_zeroes_payload() {
    // @trace T-WIPE
    let mut rec = Record::new(0x0102030405060708, 0, 3, Class::Compensable, 0);
    assert!(rec.payload.iter().any(|&b| b != 0));
    let n = wipe(&mut rec);
    assert_eq!(n, 8);
    assert!(rec.payload.iter().all(|&b| b == 0));
    let mut c = Compactor::new(M, 3, None);
    let recs = synth_records(0, M, 6, 20, 0);
    let count = recs.len() as u64;
    let rep = c.seal(0, recs, 1, 0);
    assert_eq!(rep.erased_records, count);
    assert_eq!(rep.erased_bytes, 8 * count);
}
