//! Saída golden (KV, só inteiros) — idêntica byte a byte à do oráculo Python.
//!
//! @trace T-GOLD
//! @trace T-SAM
use crate::system::{run, sampler_histogram, scenarios};

pub fn golden_text() -> String {
    let mut out = String::new();
    out.push_str("# atrator-compactador golden v0.2\n");
    for cfg in scenarios().iter() {
        let (mt, _ring) = run(cfg);
        out.push_str(&format!("[{}]\n", cfg.name));
        for (k, v) in mt.kv().iter() {
            out.push_str(&format!("{}={}\n", k, v));
        }
    }
    let n: u64 = 20000;
    let p: u64 = 39;
    let q: u64 = 41;
    let seed: u64 = 12345;
    let lo: i64 = -8;
    let hi: i64 = 8;
    let (counts, below, above, s, sa) = sampler_histogram(n, p, q, seed, lo, hi);
    out.push_str("[sampler]\n");
    out.push_str(&format!("n={}\n", n));
    out.push_str(&format!("p={}\n", p));
    out.push_str(&format!("q={}\n", q));
    out.push_str(&format!("seed={}\n", seed));
    for (i, c) in counts.iter().enumerate() {
        out.push_str(&format!("count[{}]={}\n", lo + i as i64, c));
    }
    out.push_str(&format!("below={}\n", below));
    out.push_str(&format!("above={}\n", above));
    out.push_str(&format!("sum={}\n", s));
    out.push_str(&format!("sum_abs={}\n", sa));
    out
}
