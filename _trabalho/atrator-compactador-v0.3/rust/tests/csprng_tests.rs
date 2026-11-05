//! Testes do caminho de produção: CSPRNG (`OsRng`), serviço (`Anonimizador`) e clipping por entidade.
//! @trace T-RNG @trace T-SAM @trace T-F-ANON @trace T-F-EVICT @trace T-LAT @trace T-DP-EPS @trace T-CLIP

use std::collections::HashSet;

use atrator::csprng::OsRng;
use atrator::rng::Rng64;
use atrator::servico::{Anonimizador, Classe, Evento, Parametros};

fn par() -> Parametros {
    Parametros {
        m: 4, d: 16, g0: 1, g1: 4, theta: 60, q_max: 20, i_cap: 40, tau: 50, w: 8, p: 39, q: 41, m_e: None,
    }
}

/// Gerador de eventos de teste (SplitMix64 só para gerar a CARGA; o ruído do serviço é OsRng).
fn eventos_do_ciclo(load: &mut atrator::rng::SplitMix64, m: usize, q_max: u64) -> Vec<Evento> {
    let n = load.below(3);
    (0..n)
        .map(|_| Evento {
            ancora: load.below(m as u64) as usize,
            valor: 1 + load.below(q_max),
            classe: if load.below(10) == 0 { Classe::Irreversivel } else { Classe::Compensavel },
            entidade: load.below(5),
        })
        .collect()
}

#[test]
fn os_rng_produz_saidas_distintas() {
    let mut r = OsRng;
    let v: HashSet<u64> = (0..256).map(|_| r.next_u64()).collect();
    assert!(v.len() >= 255, "saídas repetidas demais: {}", v.len());
}

#[test]
fn duas_instancias_nao_compartilham_sequencia() {
    let mut a = OsRng;
    let mut b = OsRng;
    let xa: Vec<u64> = (0..8).map(|_| a.next_u64()).collect();
    let xb: Vec<u64> = (0..8).map(|_| b.next_u64()).collect();
    assert_ne!(xa, xb);
}

#[test]
fn ruido_csprng_segue_a_distribuicao_teorica() {
    // P[Z=0] = (q-p)/(q+p) = 2/80 = 0.025 ;  E|Z| = 1/sinh(ln(q/p)) ≈ 20.0
    let mut r = OsRng;
    let n: u64 = 40_000;
    let mut zeros = 0u64;
    let mut soma_abs = 0f64;
    for _ in 0..n {
        let z = r.two_sided_geometric(39, 41);
        if z == 0 {
            zeros += 1;
        }
        soma_abs += z.unsigned_abs() as f64;
    }
    let p0 = zeros as f64 / n as f64;
    let media_abs = soma_abs / n as f64;
    assert!((p0 - 0.025).abs() < 0.005, "P[Z=0] = {}", p0);
    assert!((media_abs - 20.0).abs() < 1.5, "E|Z| = {}", media_abs);
}

#[test]
fn estados_de_instancias_csprng_diferem_com_mesma_carga() {
    // Mesma carga de eventos, duas instâncias com OsRng: o ruído é independente.
    let mut carga_a = atrator::rng::SplitMix64::new(42);
    let mut carga_b = atrator::rng::SplitMix64::new(42);
    let mut sa = Anonimizador::new(par(), OsRng).unwrap();
    let mut sb = Anonimizador::new(par(), OsRng).unwrap();
    for _ in 0..200 {
        let ea = eventos_do_ciclo(&mut carga_a, 4, 20);
        let eb = eventos_do_ciclo(&mut carga_b, 4, 20);
        sa.ciclo(&ea).unwrap();
        sb.ciclo(&eb).unwrap();
    }
    assert_ne!(sa.estado().somas, sb.estado().somas);
}

#[test]
fn servico_respeita_cotas_e_evicao_com_csprng() {
    let p = par();
    let mut carga = atrator::rng::SplitMix64::new(9);
    let mut s = Anonimizador::new(p.clone(), OsRng).unwrap();
    for _ in 0..1500 {
        let ev = eventos_do_ciclo(&mut carga, p.m, p.q_max);
        s.ciclo(&ev).unwrap();
    }
    let r = s.relatorio();
    assert_eq!(r.violacoes_b, 0);
    assert_eq!(r.violacoes_latencia, 0);
    assert!(r.max_exposicao <= r.limite_b);
    assert!(r.max_latencia <= r.limite_latencia);
    assert!(r.janelas_no_anel <= p.w);
    assert_eq!(r.janelas_evictadas, r.janelas_seladas - r.janelas_no_anel as u64);
    assert_eq!(s.estado().somas.len(), 2 * p.m);
}

#[test]
fn estado_nao_expoe_ids_nem_semente() {
    // Estado = (ciclo, janelas, somas). Nenhum campo de identidade ou semente existe na struct.
    let mut s = Anonimizador::new(par(), OsRng).unwrap();
    s.ciclo(&[Evento { ancora: 0, valor: 3, classe: Classe::Compensavel, entidade: 77 }]).unwrap();
    let e = s.estado();
    assert_eq!(e.somas.len(), 2 * par().m);
    let dbg = format!("{:?}", e);
    assert!(!dbg.to_lowercase().contains("seed"));
    assert!(!dbg.to_lowercase().contains("rng"));
    assert!(!dbg.contains("77"));
}

#[test]
fn entrada_invalida_nao_altera_o_estado() {
    let mut s = Anonimizador::new(par(), OsRng).unwrap();
    s.ciclo(&[Evento { ancora: 0, valor: 5, classe: Classe::Compensavel, entidade: 1 }]).unwrap();
    let antes = s.relatorio();
    let lote = [
        Evento { ancora: 0, valor: 5, classe: Classe::Compensavel, entidade: 1 },
        Evento { ancora: 9, valor: 1, classe: Classe::Compensavel, entidade: 1 },
    ];
    assert!(s.ciclo(&lote).is_err());
    let depois = s.relatorio();
    assert_eq!(antes.ciclos, depois.ciclos);
    assert_eq!(antes.eventos_recebidos, depois.eventos_recebidos);
    assert!(Anonimizador::new(Parametros { p: 41, q: 41, ..par() }, OsRng).is_err());
    assert!(Anonimizador::new(Parametros { g0: 5, g1: 4, ..par() }, OsRng).is_err());
    assert!(Anonimizador::new(Parametros { m_e: Some(0), ..par() }, OsRng).is_err());
}

#[test]
fn teto_i_rejeita_excesso_por_ancora_e_ciclo() {
    let mut s = Anonimizador::new(Parametros { i_cap: 10, ..par() }, OsRng).unwrap();
    s.ciclo(&[
        Evento { ancora: 0, valor: 6, classe: Classe::Compensavel, entidade: 1 },
        Evento { ancora: 0, valor: 6, classe: Classe::Compensavel, entidade: 1 },
        Evento { ancora: 0, valor: 4, classe: Classe::Compensavel, entidade: 1 },
    ])
    .unwrap();
    let r = s.relatorio();
    assert_eq!(r.rejeitados_por_limite_i, 1);
    assert_eq!(r.eventos_recebidos, 3);
}

#[test]
fn clipping_limita_valor_de_cada_entidade_por_janela() {
    // @trace T-CLIP : uma entidade que envia muito não passa de M_e por janela (Σ por entidade ≤ M_max).
    let me = 25;
    let mut s = Anonimizador::new(Parametros { m_e: Some(me), i_cap: 200, ..par() }, OsRng).unwrap();
    let mut carga = atrator::rng::SplitMix64::new(3);
    for _ in 0..400 {
        let ev: Vec<Evento> = (0..3)
            .map(|_| Evento {
                ancora: carga.below(4) as usize,
                valor: 1 + carga.below(20),
                classe: Classe::Compensavel,
                entidade: 99,
            })
            .collect();
        s.ciclo(&ev).unwrap();
    }
    let r = s.relatorio();
    assert!(r.max_valor_entidade_janela <= me, "{} > {}", r.max_valor_entidade_janela, me);
    assert!(r.registros_recortados > 0);
    assert!(r.valor_recortado > 0);
}

#[test]
fn clipping_nao_corta_entidades_abaixo_do_limite() {
    let mut s = Anonimizador::new(Parametros { m_e: Some(1_000), ..par() }, OsRng).unwrap();
    let mut carga = atrator::rng::SplitMix64::new(5);
    for _ in 0..300 {
        let ev = eventos_do_ciclo(&mut carga, 4, 20);
        s.ciclo(&ev).unwrap();
    }
    let r = s.relatorio();
    assert_eq!(r.registros_recortados, 0);
    assert_eq!(r.valor_recortado, 0);
}

#[test]
fn epsilon_por_entidade_e_m_e_vezes_ln_q_sobre_p() {
    let s = Anonimizador::new(Parametros { m_e: Some(25), ..par() }, OsRng).unwrap();
    let eps = s.relatorio().epsilon_por_entidade_por_janela;
    let esperado = 25.0 * (41.0f64 / 39.0).ln();
    assert!((eps - esperado).abs() < 1e-9, "{} vs {}", eps, esperado);
    let sem = Anonimizador::new(par(), OsRng).unwrap().relatorio();
    assert!(sem.epsilon_por_entidade_por_janela.is_infinite());
}
