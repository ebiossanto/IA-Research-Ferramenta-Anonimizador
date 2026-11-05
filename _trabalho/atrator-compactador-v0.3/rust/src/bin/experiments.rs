//! Executa os cenários.  Sem argumentos: imprime a saída golden (stdout).
//! `--perf`: mede vazão (NÃO determinístico; não entra no golden).
//!
//! @trace T-GOLD
use std::time::Instant;

use atrator::csprng::OsRng;
use atrator::report::golden_text;
use atrator::rng::{Rng64, SplitMix64};
use atrator::servico::{Anonimizador, Classe, Evento, Parametros};
use atrator::system::{run, scenarios};

/// Mede o serviço de produção (`Anonimizador`) com uma fonte de ruído dada.
fn medir_servico<R: Rng64>(nome: &str, fonte: R) {
    let par = Parametros { m: 4, d: 16, g0: 1, g1: 4, theta: 60, q_max: 20, i_cap: 40, tau: 50, w: 8, p: 39, q: 41, m_e: None };
    let ciclos_por_rep: u64 = 2000;
    let reps: u64 = 50;
    let ciclos = ciclos_por_rep * reps;
    let mut carga = SplitMix64::new(20261015);
    let mut s = Anonimizador::new(par.clone(), fonte).expect("parâmetros válidos");
    let mut eventos: u64 = 0;
    let start = Instant::now();
    for _ in 0..ciclos {
        let n = carga.below(3);
        let ev: Vec<Evento> = (0..n)
            .map(|_| Evento {
                ancora: carga.below(par.m as u64) as usize,
                valor: 1 + carga.below(par.q_max),
                classe: if carga.below(10) == 0 { Classe::Irreversivel } else { Classe::Compensavel },
                entidade: carga.below(5),
            })
            .collect();
        eventos += n;
        s.ciclo(&ev).expect("eventos válidos");
    }
    let secs = start.elapsed().as_secs_f64();
    println!(
        "perf.{}.cycles_per_s={:.0} perf.{}.events_per_s={:.0} perf.{}.seconds={:.4}",
        nome,
        (ciclos as f64) / secs,
        nome,
        (eventos as f64) / secs,
        nome,
        secs
    );
}

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
        medir_servico("servico_splitmix", SplitMix64::new(1));
        medir_servico("servico_csprng", OsRng);
        return;
    }
    print!("{}", golden_text());
}
