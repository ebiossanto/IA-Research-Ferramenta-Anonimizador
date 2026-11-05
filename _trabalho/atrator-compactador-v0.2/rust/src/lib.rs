//! Atrator Compactador / Anonimizador — implementação em Rust.
//!
//! Somente `std`, sem `unsafe` e sem mutabilidade interior (subconjunto compatível com
//! verificação por tradução funcional, p.ex. Aeneas -> Lean; ver docs/06-roadmap.md).
//! Aritmética inteira nos caminhos que entram nas saídas golden.
#![forbid(unsafe_code)]

pub mod compactor;
pub mod exposure;
pub mod record;
pub mod report;
pub mod rng;
pub mod system;
