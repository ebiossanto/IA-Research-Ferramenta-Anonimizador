//! Atrator Compactador / Anonimizador — implementação em Rust.
//!
//! `std` + a crate `getrandom` (única dependência, para o CSPRNG do sistema operacional), sem
//! `unsafe` e sem mutabilidade interior. Aritmética inteira nos caminhos que entram nas saídas golden.
//!
//! Produção: `servico::Anonimizador` com `csprng::OsRng`. `SplitMix64` é só para testes e golden.
#![forbid(unsafe_code)]

pub mod compactor;
pub mod csprng;
pub mod exposure;
pub mod record;
pub mod report;
pub mod rng;
pub mod servico;
pub mod system;
