//! Compactador C: sela janelas (agrega, apaga o bruto, adiciona ruído) e evicta.
//!
//! @trace T-F-EVICT    o estado do anel não depende de janelas com idade >= W
//! @trace T-F-DROP     descartar uma janela torna o estado independente do seu conteúdo
//! @trace T-F-ANON     o agregado ignora identidade/payload
//! @trace T-DP-SENS    um registro altera exatamente uma coordenada, em <= Q
//! @trace T-DP-EPS     ruído geométrico bilateral por coordenada => e^eps0 = (q/p)^Q
//! @trace T-WIPE       o bruto é zerado antes de ser descartado
use std::collections::VecDeque;

use crate::record::{wipe, Class, Record};
use crate::rng::{derive_seed, SplitMix64};

pub const TAG_NOISE: u64 = 0x4E4F495345; // "NOISE"

pub struct Compactor {
    pub m: usize,
    pub w: usize,
    /// None: modo exato (sem ruído). Some((p, q)): ruído geométrico bilateral com alfa = p/q.
    pub noise: Option<(u64, u64)>,
    /// (índice da janela, agregados com ruído); mais antigo primeiro
    pub windows: VecDeque<(u64, Vec<i64>)>,
}

pub struct SealReport {
    pub true_sums: Vec<i64>,
    pub erased_records: u64,
    pub erased_bytes: u64,
    pub evicted: u64,
    pub max_age: u64,
}

impl Compactor {
    pub fn new(m: usize, w: usize, noise: Option<(u64, u64)>) -> Compactor {
        Compactor {
            m,
            w,
            noise,
            windows: VecDeque::new(),
        }
    }

    pub fn seal(
        &mut self,
        window_index: u64,
        mut records: Vec<Record>,
        master_seed: u64,
        now: u64,
    ) -> SealReport {
        let m = self.m;
        let mut sums: Vec<i64> = vec![0; 2 * m];
        let mut max_age: u64 = 0;
        for r in records.iter() {
            let c = match r.class {
                Class::Compensable => r.anchor,
                Class::Irreversible => m + r.anchor,
            };
            sums[c] += r.q as i64;
            let age = now - r.born;
            if age > max_age {
                max_age = age;
            }
        }
        let erased_records = records.len() as u64;
        let mut erased_bytes: u64 = 0;
        for r in records.iter_mut() {
            erased_bytes += wipe(r);
        }
        drop(records);
        let true_sums = sums.clone();
        if let Some((p, q)) = self.noise {
            let mut rng = SplitMix64::new(derive_seed(master_seed, TAG_NOISE, window_index));
            for c in 0..(2 * m) {
                sums[c] += rng.two_sided_geometric(p, q);
            }
        }
        self.windows.push_back((window_index, sums));
        let mut evicted: u64 = 0;
        while self.windows.len() > self.w {
            let _ = self.windows.pop_front();
            evicted += 1;
        }
        SealReport {
            true_sums,
            erased_records,
            erased_bytes,
            evicted,
            max_age,
        }
    }

    /// Esquecimento exato por pedido (análogo a descartar um shard no SISA).
    pub fn drop_window(&mut self, window_index: u64) -> bool {
        let mut pos: Option<usize> = None;
        for (i, entry) in self.windows.iter().enumerate() {
            if entry.0 == window_index {
                pos = Some(i);
                break;
            }
        }
        match pos {
            Some(i) => {
                let _ = self.windows.remove(i);
                true
            }
            None => false,
        }
    }

    /// Estado preservado: soma por coordenada sobre o anel.
    pub fn state(&self) -> Vec<i64> {
        let mut out: Vec<i64> = vec![0; 2 * self.m];
        for entry in self.windows.iter() {
            for c in 0..(2 * self.m) {
                out[c] += entry.1[c];
            }
        }
        out
    }
}
