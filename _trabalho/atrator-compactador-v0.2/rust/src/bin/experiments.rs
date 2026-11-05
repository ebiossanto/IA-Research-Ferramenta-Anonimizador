//! Executa os cenários.  Sem argumentos: imprime a saída golden (stdout).
//! `--perf`: mede vazão (NÃO determinístico; não entra no golden).
//!
//! @trace T-GOLD
use std::time::Instant;

use atrator::report::golden_text;
use atrator::system::{run, scenarios};

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.iter().any(|a| a == "--perf") {
        let reps: u32 = 5;
        println!("# desempenho (não determinístico) — {} repetições por cenário", reps);
        for cfg in scenarios().iter() {
            let mut records: u64 = 0;
            let start = Instant::now();
            for _ in 0..reps {
                let (mt, _ring) = run(cfg);
                records += mt.records_injected;
            }
            let secs = start.elapsed().as_secs_f64();
            let cycles = (cfg.cycles as f64) * (reps as f64);
            println!(
                "perf.{}.cycles_per_s={:.0} perf.{}.records_per_s={:.0} perf.{}.seconds={:.4}",
                cfg.name,
                cycles / secs,
                cfg.name,
                (records as f64) / secs,
                cfg.name,
                secs
            );
        }
        return;
    }
    print!("{}", golden_text());
}
