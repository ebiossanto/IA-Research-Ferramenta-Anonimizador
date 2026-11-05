//! Teste diferencial: o Rust deve reproduzir os vetores gerados pelo oráculo Python
//! (trace/vectors.csv) — os MESMOS vetores são checados por `decide` em lean/AtratorExtras/Vectors.lean.
//!
//! @trace T-D-REM @trace T-D-CONTRACT @trace T-ISS-INV @trace T-LAT @trace T-RNG @trace T-GOLD

use atrator::exposure::{bound_b, disch, discharge_ceil, rate, removal, settle_steps, step};
use atrator::rng::{derive_seed, SplitMix64};

const VECTORS: &str = include_str!("../../trace/vectors.csv");

#[test]
fn vectors_match_oracle() {
    let mut n: u32 = 0;
    for raw in VECTORS.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let f: Vec<&str> = line.split(',').collect();
        let nums: Vec<u64> = f[1..].iter().map(|s| s.parse::<u64>().expect("número")).collect();
        match f[0] {
            "removal" => assert_eq!(removal(nums[0], nums[1], nums[2]), nums[3], "{}", line),
            "discharge_ceil" => assert_eq!(discharge_ceil(nums[0], nums[1], nums[2]), nums[3], "{}", line),
            "rate" => assert_eq!(rate(nums[0], nums[1], nums[2], nums[3]), nums[4], "{}", line),
            "disch" => assert_eq!(disch(nums[0], nums[1], nums[2], nums[3], nums[4]), nums[5], "{}", line),
            "step" => assert_eq!(step(nums[0], nums[1], nums[2], nums[3], nums[4], nums[5]), nums[6], "{}", line),
            "bound_b" => assert_eq!(bound_b(nums[0], nums[1], nums[2], nums[3], nums[4]), nums[5], "{}", line),
            "settle_steps" => assert_eq!(settle_steps(nums[0], nums[1], nums[2]), nums[3], "{}", line),
            "splitmix" => {
                let mut s = SplitMix64::new(nums[0]);
                let mut last: u64 = 0;
                for _ in 0..=nums[1] {
                    last = s.next_u64();
                }
                assert_eq!(last, nums[2], "{}", line);
            }
            "derive_seed" => assert_eq!(derive_seed(nums[0], nums[1], nums[2]), nums[3], "{}", line),
            other => panic!("função desconhecida em vectors.csv: {}", other),
        }
        n += 1;
    }
    assert!(n > 100, "poucos vetores: {}", n);
}
