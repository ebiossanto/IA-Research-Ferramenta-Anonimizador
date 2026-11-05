//! Registro (resíduo bruto) e apagamento best-effort.
//!
//! @trace T-WIPE   zeragem do payload bruto antes de descartar (limites: ver docs/03 §Limites)

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Class {
    /// compensável: entra na fila viva e é liquidado por D
    Compensable,
    /// irreversível: nada a compensar (piso); vai direto a "liquidado"
    Irreversible,
}

#[derive(Clone, Debug)]
pub struct Record {
    pub id: u64,
    pub anchor: usize,
    pub q: u64,
    pub class: Class,
    pub born: u64,
    pub payload: Vec<u8>,
}

impl Record {
    pub fn new(id: u64, anchor: usize, q: u64, class: Class, born: u64) -> Record {
        Record {
            id,
            anchor,
            q,
            class,
            born,
            payload: id.to_le_bytes().to_vec(),
        }
    }
}

/// Zera o payload. Retorna o nº de bytes apagados.
pub fn wipe(rec: &mut Record) -> u64 {
    let n = rec.payload.len();
    for b in rec.payload.iter_mut() {
        *b = 0;
    }
    let _ = std::hint::black_box(&rec.payload);
    n as u64
}
