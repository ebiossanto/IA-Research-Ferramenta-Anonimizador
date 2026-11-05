//! Serviço de anonimização para uso real (espelha `python/atrator_ref/servico.py`).
//!
//! Eventos chegam de fora por ciclo: (âncora, valor, classe). Cada ciclo admite os eventos (com
//! teto I por âncora), descarrega cada âncora (D), e a cada `tau` ciclos sela uma janela (C):
//! agrega, apaga o bruto e soma ruído geométrico. O anel mantém no máximo `w` janelas (evicção).
//!
//! O objeto NÃO armazena semente: o ruído vem da fonte `R` (em produção, `csprng::OsRng`), e o
//! estado exposto (`Estado`) contém só somas por coordenada, sem identificadores.
//!
//! Validação: `ciclo` valida todos os eventos ANTES de alterar o estado (sem efeito parcial).
//!
//! @trace T-LAT      latência de liquidação <= settle_steps(d,g0,B+I) - 1
//! @trace T-F-EVICT  o anel mantém no máximo W janelas seladas
//! @trace T-F-ANON   o estado não contém identidade, payload nem semente
//! @trace T-DP-SENS  um registro altera exatamente uma coordenada do agregado, em <= Q
//! @trace T-WIPE     zeragem (best-effort) do valor bruto antes de descartar
use std::collections::{BTreeMap, VecDeque};

use crate::compactor::Compactor;
use crate::exposure::{bound_b, contract_holds, rate, removal, settle_steps};
use crate::record::{wipe, Class, Record};
use crate::rng::Rng64;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Classe {
    Compensavel,
    Irreversivel,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Evento {
    pub ancora: usize,
    pub valor: u64,
    pub classe: Classe,
    pub entidade: u64,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Parametros {
    pub m: usize,
    pub d: u64,
    pub g0: u64,
    pub g1: u64,
    pub theta: u64,
    pub q_max: u64,
    pub i_cap: u64,
    pub tau: u64,
    pub w: usize,
    pub p: u64,
    pub q: u64,
    /// Limite M_e de valor de uma entidade por janela selada (clipping, T-CLIP). None: desligado.
    pub m_e: Option<u64>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Estado {
    pub ciclo: u64,
    pub janelas_no_anel: usize,
    pub somas: Vec<i64>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Relatorio {
    pub ciclos: u64,
    pub eventos_recebidos: u64,
    pub rejeitados_por_limite_i: u64,
    pub irreversiveis: u64,
    pub brutos_ainda_no_estado: u64,
    pub exposicao_viva_atual: u64,
    pub max_exposicao: u64,
    pub limite_b: u64,
    pub violacoes_b: u64,
    pub max_latencia: u64,
    pub limite_latencia: u64,
    pub violacoes_latencia: u64,
    pub registros_apagados: u64,
    pub janelas_seladas: u64,
    pub janelas_evictadas: u64,
    pub janelas_no_anel: usize,
    pub epsilon_por_registro: f64,
    pub registros_recortados: u64,
    pub valor_recortado: u64,
    pub max_valor_entidade_janela: u64,
    pub epsilon_por_entidade_por_janela: f64,
}

pub struct Anonimizador<R: Rng64> {
    par: Parametros,
    b: u64,
    limite_latencia: u64,
    rng: R,
    comp: Compactor,
    filas: Vec<VecDeque<Record>>,
    u: Vec<u64>,
    liquidados: Vec<Record>,
    t: u64,
    recebidos: u64,
    rejeitados: u64,
    irreversiveis: u64,
    apagados: u64,
    janelas_seladas: u64,
    janelas_evictadas: u64,
    max_exposicao: u64,
    violacoes_b: u64,
    max_latencia: u64,
    violacoes_latencia: u64,
    registros_recortados: u64,
    valor_recortado: u64,
    max_valor_entidade_janela: u64,
}

impl<R: Rng64> Anonimizador<R> {
    pub fn new(par: Parametros, rng: R) -> Result<Anonimizador<R>, String> {
        validar_parametros(&par)?;
        let b = bound_b(par.d, par.theta, par.g0, par.g1, par.i_cap);
        let limite_latencia = settle_steps(par.d, par.g0, b + par.i_cap) - 1;
        Ok(Anonimizador {
            comp: Compactor::new(par.m, par.w, Some((par.p, par.q))),
            filas: (0..par.m).map(|_| VecDeque::new()).collect(),
            u: vec![0; par.m],
            liquidados: Vec::new(),
            t: 0,
            recebidos: 0,
            rejeitados: 0,
            irreversiveis: 0,
            apagados: 0,
            janelas_seladas: 0,
            janelas_evictadas: 0,
            max_exposicao: 0,
            violacoes_b: 0,
            max_latencia: 0,
            violacoes_latencia: 0,
            registros_recortados: 0,
            valor_recortado: 0,
            max_valor_entidade_janela: 0,
            b,
            limite_latencia,
            rng,
            par,
        })
    }

    /// Processa um ciclo. Valida todos os eventos antes de qualquer alteração.
    pub fn ciclo(&mut self, eventos: &[Evento]) -> Result<(), String> {
        for ev in eventos {
            validar_evento(ev, &self.par)?;
        }
        let m = self.par.m;
        let t = self.t;
        let mut injetado: Vec<u64> = vec![0; m];
        for ev in eventos {
            self.recebidos += 1;
            match ev.classe {
                Classe::Compensavel => {
                    if injetado[ev.ancora] + ev.valor > self.par.i_cap {
                        self.rejeitados += 1;
                        continue;
                    }
                    injetado[ev.ancora] += ev.valor;
                    let mut rec = Record::new(0, ev.ancora, ev.valor, Class::Compensable, t);
                    rec.entidade = ev.entidade;
                    self.filas[ev.ancora].push_back(rec);
                    self.u[ev.ancora] += ev.valor;
                }
                Classe::Irreversivel => {
                    let mut rec = Record::new(0, ev.ancora, ev.valor, Class::Irreversible, t);
                    rec.entidade = ev.entidade;
                    self.liquidados.push(rec);
                    self.irreversiveis += 1;
                }
            }
        }

        for a in 0..m {
            let v = self.u[a];
            let g = rate(self.par.theta, self.par.g0, self.par.g1, v);
            let orcamento = removal(self.par.d, g, v);
            let mut acumulado: u64 = 0;
            while acumulado < orcamento {
                match self.filas[a].pop_front() {
                    Some(r) => {
                        acumulado += r.q;
                        let latencia = t - r.born;
                        if latencia > self.max_latencia {
                            self.max_latencia = latencia;
                        }
                        if latencia > self.limite_latencia {
                            self.violacoes_latencia += 1;
                        }
                        self.liquidados.push(r);
                    }
                    None => break,
                }
            }
            let u2 = v - acumulado;
            if u2 > self.b {
                self.violacoes_b += 1;
            }
            if u2 > self.max_exposicao {
                self.max_exposicao = u2;
            }
            debug_assert!(contract_holds(self.par.d, g, v, u2));
            self.u[a] = u2;
        }

        if (t + 1) % self.par.tau == 0 {
            let widx = (t + 1) / self.par.tau - 1;
            let recs = std::mem::take(&mut self.liquidados);
            let n = recs.len() as u64;
            let recs = self.recortar(recs);
            let rep = self.comp.seal_with(widx, recs, &mut self.rng, t);
            self.apagados += n;
            self.janelas_seladas += 1;
            self.janelas_evictadas += rep.evicted;
        }
        self.t += 1;
        Ok(())
    }

    /// Estado preservado: somas ruidosas por coordenada sobre o anel. Sem ids, sem semente.
    pub fn estado(&self) -> Estado {
        Estado {
            ciclo: self.t,
            janelas_no_anel: self.comp.windows.len(),
            somas: self.comp.state(),
        }
    }

    /// Clipping por entidade (T-CLIP): no selo, cada entidade contribui no máximo `M_e` de valor
    /// à janela. O excedente é apagado e não entra na agregação. Ordem de chegada define quem
    /// fica (determinístico). Sem `m_e`, devolve os registros intactos.
    fn recortar(&mut self, recs: Vec<Record>) -> Vec<Record> {
        let me = match self.par.m_e {
            Some(me) => me,
            None => return recs,
        };
        let mut acumulado: BTreeMap<u64, u64> = BTreeMap::new();
        let mut aceitos = Vec::with_capacity(recs.len());
        for mut r in recs {
            let total = acumulado.entry(r.entidade).or_insert(0);
            if *total + r.q <= me {
                *total += r.q;
                aceitos.push(r);
            } else {
                self.registros_recortados += 1;
                self.valor_recortado += r.q;
                wipe(&mut r);
            }
        }
        for &total in acumulado.values() {
            if total > self.max_valor_entidade_janela {
                self.max_valor_entidade_janela = total;
            }
        }
        aceitos
    }

    pub fn relatorio(&self) -> Relatorio {
        let brutos: u64 = self.filas.iter().map(|f| f.len() as u64).sum::<u64>()
            + self.liquidados.len() as u64;
        Relatorio {
            ciclos: self.t,
            eventos_recebidos: self.recebidos,
            rejeitados_por_limite_i: self.rejeitados,
            irreversiveis: self.irreversiveis,
            brutos_ainda_no_estado: brutos,
            exposicao_viva_atual: self.u.iter().sum(),
            max_exposicao: self.max_exposicao,
            limite_b: self.b,
            violacoes_b: self.violacoes_b,
            max_latencia: self.max_latencia,
            limite_latencia: self.limite_latencia,
            violacoes_latencia: self.violacoes_latencia,
            registros_apagados: self.apagados,
            janelas_seladas: self.janelas_seladas,
            janelas_evictadas: self.janelas_evictadas,
            janelas_no_anel: self.comp.windows.len(),
            epsilon_por_registro: (self.par.q_max as f64) * ((self.par.q as f64) / (self.par.p as f64)).ln(),
            registros_recortados: self.registros_recortados,
            valor_recortado: self.valor_recortado,
            max_valor_entidade_janela: self.max_valor_entidade_janela,
            epsilon_por_entidade_por_janela: match self.par.m_e {
                Some(me) => (me as f64) * ((self.par.q as f64) / (self.par.p as f64)).ln(),
                None => f64::INFINITY,
            },
        }
    }
}

fn validar_parametros(par: &Parametros) -> Result<(), String> {
    if par.m < 1 {
        return Err("m (número de âncoras) deve ser >= 1".into());
    }
    if !(1 <= par.g0 && par.g0 <= par.g1 && par.g1 <= par.d) {
        return Err("exige 1 <= g0 <= g1 <= d".into());
    }
    if !(par.q_max >= 1 && par.i_cap >= 1 && par.tau >= 1 && par.w >= 1) {
        return Err("exige Q, I, tau, W >= 1".into());
    }
    if !(0 < par.p && par.p < par.q) {
        return Err("ruído exige 0 < p < q".into());
    }
    if par.m_e == Some(0) {
        return Err("limite por entidade M_e deve ser >= 1 (ou None)".into());
    }
    Ok(())
}

fn validar_evento(ev: &Evento, par: &Parametros) -> Result<(), String> {
    if ev.ancora >= par.m {
        return Err(format!("âncora fora de [0, {}): {}", par.m, ev.ancora));
    }
    if !(1 <= ev.valor && ev.valor <= par.q_max) {
        return Err(format!("valor fora de [1, {}]: {}", par.q_max, ev.valor));
    }
    Ok(())
}
