//! Sistema completo: injeção -> descarga (D) -> selagem/compactação (C) -> evicção.
//!
//! Ciclo de vida: vivo (fila FIFO por âncora) -> liquidado -> anonimizado (bruto apagado,
//! só resta agregado com ruído) -> evictado (nenhum vestígio no estado).
//!
//! @trace T-LAT        latência de liquidação <= settle_steps(d,g0,B+I) - 1
//! @trace T-ISS-INV    exposição pós-descarga <= B em todo ciclo
//! @trace T-TIMELINE   linha do tempo: bruto <= L + tau - 1 ; zero residual após evicção
//! @trace T-GOLD       saída golden idêntica à do oráculo Python
//! @trace T-F-ANON     tamper de identidade/payload não altera nenhuma métrica
use std::collections::{BTreeMap, VecDeque};

use crate::compactor::Compactor;
use crate::exposure::{bound_b, contract_holds, rate, removal, settle_steps};
use crate::record::{Class, Record};
use crate::rng::{fnv1a64_ints, Rng64, SplitMix64};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Steady,
    Burst,
    Stop,
}

#[derive(Clone, Debug)]
pub struct Config {
    pub name: &'static str,
    pub kind: Kind,
    pub m: usize,
    pub d: u64,
    pub g0: u64,
    pub g1: u64,
    pub theta: u64,
    pub q_max: u64,
    pub i_cap: u64,
    pub tau: u64,
    pub w: usize,
    pub noise: Option<(u64, u64)>,
    pub cycles: u64,
    pub stop_at: u64,
    pub seed: u64,
}

pub fn scenarios() -> Vec<Config> {
    vec![
        Config { name: "steady", kind: Kind::Steady, m: 4, d: 16, g0: 1, g1: 4, theta: 60, q_max: 20,
                 i_cap: 40, tau: 50, w: 8, noise: Some((39, 41)), cycles: 2000, stop_at: 0, seed: 20261015 },
        Config { name: "burst", kind: Kind::Burst, m: 3, d: 32, g0: 2, g1: 16, theta: 150, q_max: 25,
                 i_cap: 80, tau: 40, w: 6, noise: Some((39, 41)), cycles: 1500, stop_at: 0, seed: 20261016 },
        Config { name: "stop", kind: Kind::Stop, m: 2, d: 32, g0: 1, g1: 8, theta: 300, q_max: 10,
                 i_cap: 50, tau: 25, w: 4, noise: Some((19, 20)), cycles: 1000, stop_at: 300, seed: 20261017 },
        Config { name: "exact", kind: Kind::Steady, m: 4, d: 16, g0: 1, g1: 4, theta: 60, q_max: 20,
                 i_cap: 40, tau: 50, w: 8, noise: None, cycles: 1000, stop_at: 0, seed: 7 },
    ]
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Metrics {
    pub cycles: u64,
    pub records_generated: u64,
    pub records_dropped_by_cap: u64,
    pub records_injected: u64,
    pub records_compensable: u64,
    pub records_irreversible: u64,
    pub exposure_injected: u64,
    pub exposure_settled: u64,
    pub discharge_events: u64,
    pub boosted_events: u64,
    pub max_exposure: u64,
    pub bound_b: u64,
    pub bound_violations: u64,
    pub contract_violations: u64,
    pub max_settle_latency: u64,
    pub latency_bound: u64,
    pub latency_violations: u64,
    pub windows_sealed: u64,
    pub windows_evicted: u64,
    pub ring_len_final: u64,
    pub records_erased: u64,
    pub bytes_erased: u64,
    pub ledger_peak_records: u64,
    pub ledger_final_records: u64,
    pub live_final_exposure: u64,
    pub retained_state_ints: u64,
    pub abs_error_sum: u64,
    pub true_abs_sum: u64,
    pub rel_error_permille: u64,
    pub state_checksum: u64,
    pub first_zero_after_stop: i64,
    pub exposure_at_stop: u64,
    pub max_raw_age_at_erase: u64,
    pub raw_age_bound: u64,
}

impl Metrics {
    /// Pares chave/valor na MESMA ordem de `KEYS` do oráculo Python.
    pub fn kv(&self) -> Vec<(&'static str, String)> {
        vec![
            ("cycles", self.cycles.to_string()),
            ("records_generated", self.records_generated.to_string()),
            ("records_dropped_by_cap", self.records_dropped_by_cap.to_string()),
            ("records_injected", self.records_injected.to_string()),
            ("records_compensable", self.records_compensable.to_string()),
            ("records_irreversible", self.records_irreversible.to_string()),
            ("exposure_injected", self.exposure_injected.to_string()),
            ("exposure_settled", self.exposure_settled.to_string()),
            ("discharge_events", self.discharge_events.to_string()),
            ("boosted_events", self.boosted_events.to_string()),
            ("max_exposure", self.max_exposure.to_string()),
            ("bound_B", self.bound_b.to_string()),
            ("bound_violations", self.bound_violations.to_string()),
            ("contract_violations", self.contract_violations.to_string()),
            ("max_settle_latency", self.max_settle_latency.to_string()),
            ("latency_bound", self.latency_bound.to_string()),
            ("latency_violations", self.latency_violations.to_string()),
            ("windows_sealed", self.windows_sealed.to_string()),
            ("windows_evicted", self.windows_evicted.to_string()),
            ("ring_len_final", self.ring_len_final.to_string()),
            ("records_erased", self.records_erased.to_string()),
            ("bytes_erased", self.bytes_erased.to_string()),
            ("ledger_peak_records", self.ledger_peak_records.to_string()),
            ("ledger_final_records", self.ledger_final_records.to_string()),
            ("live_final_exposure", self.live_final_exposure.to_string()),
            ("retained_state_ints", self.retained_state_ints.to_string()),
            ("abs_error_sum", self.abs_error_sum.to_string()),
            ("true_abs_sum", self.true_abs_sum.to_string()),
            ("rel_error_permille", self.rel_error_permille.to_string()),
            ("state_checksum", self.state_checksum.to_string()),
            ("first_zero_after_stop", self.first_zero_after_stop.to_string()),
            ("exposure_at_stop", self.exposure_at_stop.to_string()),
            ("max_raw_age_at_erase", self.max_raw_age_at_erase.to_string()),
            ("raw_age_bound", self.raw_age_bound.to_string()),
        ]
    }
}

/// Registros gerados no ciclo t, por âncora (antes do corte por I). Ordem de consumo do RNG
/// fixa e idêntica à do oráculo: por âncora: n; depois, por registro: q e classe.
fn gen_cycle(cfg: &Config, rng: &mut SplitMix64, t: u64) -> Vec<Vec<(u64, Class)>> {
    let mut out: Vec<Vec<(u64, Class)>> = Vec::with_capacity(cfg.m);
    for _a in 0..cfg.m {
        let n: u64 = match cfg.kind {
            Kind::Steady => rng.below(3),
            Kind::Burst => {
                if (t % 200) < 20 {
                    2 + rng.below(3)
                } else {
                    rng.below(2)
                }
            }
            Kind::Stop => {
                if t < cfg.stop_at {
                    2 + rng.below(4)
                } else {
                    0
                }
            }
        };
        let mut lst: Vec<(u64, Class)> = Vec::new();
        for _i in 0..n {
            let q = 1 + rng.below(cfg.q_max);
            let class = if rng.below(10) == 0 {
                Class::Irreversible
            } else {
                Class::Compensable
            };
            lst.push((q, class));
        }
        out.push(lst);
    }
    out
}

pub type Ring = Vec<(u64, Vec<i64>)>;

pub fn run(cfg: &Config) -> (Metrics, Ring) {
    run_with(cfg, &mut |_r: &mut Record| {})
}

/// `tamper` é chamado em cada registro aceito (altera identidade/payload nos testes de
/// vizinhança sem tocar no RNG).
pub fn run_with(cfg: &Config, tamper: &mut dyn FnMut(&mut Record)) -> (Metrics, Ring) {
    assert!(cfg.i_cap >= 1 && cfg.tau >= 1 && cfg.d >= 1 && cfg.g0 >= 1 && cfg.g0 <= cfg.g1 && cfg.g1 <= cfg.d);
    let m = cfg.m;
    let b = bound_b(cfg.d, cfg.theta, cfg.g0, cfg.g1, cfg.i_cap);
    let lat_bound = settle_steps(cfg.d, cfg.g0, b + cfg.i_cap) - 1;
    let raw_bound = lat_bound + cfg.tau - 1;

    let mut rng = SplitMix64::new(cfg.seed);
    let mut comp = Compactor::new(m, cfg.w, cfg.noise);
    let mut queues: Vec<VecDeque<Record>> = (0..m).map(|_| VecDeque::new()).collect();
    let mut u: Vec<u64> = vec![0; m];
    let mut settled: Vec<Record> = Vec::new();
    let mut shadow: BTreeMap<u64, Vec<i64>> = BTreeMap::new();
    let mut next_id: u64 = 0;

    let mut mt = Metrics::default();
    mt.bound_b = b;
    mt.latency_bound = lat_bound;
    mt.raw_age_bound = raw_bound;
    mt.cycles = cfg.cycles;
    mt.first_zero_after_stop = -1;

    for t in 0..cfg.cycles {
        let generated = gen_cycle(cfg, &mut rng, t);
        for a in 0..m {
            let mut inj: u64 = 0;
            for &(q, class) in generated[a].iter() {
                mt.records_generated += 1;
                match class {
                    Class::Compensable => {
                        if inj + q > cfg.i_cap {
                            mt.records_dropped_by_cap += 1;
                            continue;
                        }
                        inj += q;
                        let mut rec = Record::new(next_id, a, q, Class::Compensable, t);
                        next_id += 1;
                        tamper(&mut rec);
                        let rq = rec.q;
                        queues[a].push_back(rec);
                        u[a] += rq;
                        mt.records_compensable += 1;
                        mt.exposure_injected += rq;
                    }
                    Class::Irreversible => {
                        let mut rec = Record::new(next_id, a, q, Class::Irreversible, t);
                        next_id += 1;
                        tamper(&mut rec);
                        settled.push(rec);
                        mt.records_irreversible += 1;
                    }
                }
                mt.records_injected += 1;
            }
        }
        let live: u64 = queues.iter().map(|qq| qq.len() as u64).sum();
        let total = live + settled.len() as u64;
        if total > mt.ledger_peak_records {
            mt.ledger_peak_records = total;
        }

        for a in 0..m {
            let v = u[a];
            let g = rate(cfg.theta, cfg.g0, cfg.g1, v);
            let budget = removal(cfg.d, g, v);
            let mut cum: u64 = 0;
            while cum < budget {
                match queues[a].pop_front() {
                    Some(r) => {
                        cum += r.q;
                        let lat = t - r.born;
                        if lat > mt.max_settle_latency {
                            mt.max_settle_latency = lat;
                        }
                        if lat > lat_bound {
                            mt.latency_violations += 1;
                        }
                        settled.push(r);
                    }
                    None => break,
                }
            }
            let u2 = v - cum;
            if !contract_holds(cfg.d, g, v, u2) {
                mt.contract_violations += 1;
            }
            if u2 > b {
                mt.bound_violations += 1;
            }
            if u2 > mt.max_exposure {
                mt.max_exposure = u2;
            }
            if cum > 0 {
                mt.discharge_events += 1;
                if v > cfg.theta {
                    mt.boosted_events += 1;
                }
                mt.exposure_settled += cum;
            }
            u[a] = u2;
        }

        if cfg.kind == Kind::Stop && t + 1 == cfg.stop_at {
            mt.exposure_at_stop = u.iter().sum::<u64>();
        }
        if cfg.kind == Kind::Stop
            && t >= cfg.stop_at
            && mt.first_zero_after_stop < 0
            && u.iter().sum::<u64>() == 0
        {
            mt.first_zero_after_stop = t as i64;
        }

        if (t + 1) % cfg.tau == 0 {
            let widx = (t + 1) / cfg.tau - 1;
            let recs = std::mem::take(&mut settled);
            let rep = comp.seal(widx, recs, cfg.seed, t);
            shadow.insert(widx, rep.true_sums.clone());
            mt.windows_sealed += 1;
            mt.windows_evicted += rep.evicted;
            mt.records_erased += rep.erased_records;
            mt.bytes_erased += rep.erased_bytes;
            if rep.max_age > mt.max_raw_age_at_erase {
                mt.max_raw_age_at_erase = rep.max_age;
            }
        }
    }

    mt.ring_len_final = comp.windows.len() as u64;
    mt.retained_state_ints = comp.windows.len() as u64 * 2 * m as u64;
    mt.ledger_final_records = queues.iter().map(|qq| qq.len() as u64).sum::<u64>() + settled.len() as u64;
    mt.live_final_exposure = u.iter().sum::<u64>();
    let mut err: i64 = 0;
    let mut tot: i64 = 0;
    let mut flat: Vec<i64> = Vec::new();
    for entry in comp.windows.iter() {
        let tr = shadow.get(&entry.0).expect("shadow ausente");
        for c in 0..(2 * m) {
            err += (entry.1[c] - tr[c]).abs();
            tot += tr[c].abs();
            flat.push(entry.1[c]);
        }
    }
    mt.abs_error_sum = err as u64;
    mt.true_abs_sum = tot as u64;
    mt.rel_error_permille = if tot > 0 { ((1000 * err) / tot) as u64 } else { 0 };
    mt.state_checksum = fnv1a64_ints(&flat);
    let ring: Ring = comp.windows.iter().cloned().collect();
    (mt, ring)
}

/// Histograma inteiro do amostrador bilateral (T-SAM).
/// Retorna (contagens de lo..=hi, abaixo, acima, soma, soma_abs).
pub fn sampler_histogram(n: u64, p: u64, q: u64, seed: u64, lo: i64, hi: i64) -> (Vec<u64>, u64, u64, i64, u64) {
    let mut rng = SplitMix64::new(seed);
    let width = (hi - lo + 1) as usize;
    let mut counts: Vec<u64> = vec![0; width];
    let mut below: u64 = 0;
    let mut above: u64 = 0;
    let mut s: i64 = 0;
    let mut sa: u64 = 0;
    for _ in 0..n {
        let z = rng.two_sided_geometric(p, q);
        s += z;
        sa += z.unsigned_abs();
        if z < lo {
            below += 1;
        } else if z > hi {
            above += 1;
        } else {
            counts[(z - lo) as usize] += 1;
        }
    }
    (counts, below, above, s, sa)
}
