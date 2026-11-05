//! Fonte CSPRNG para o ruído em produção: bytes do sistema operacional.
//!
//! Usa a crate `getrandom` (BCryptGenRandom no Windows, getrandom(2) no Linux). Não há semente:
//! o estado de `OsRng` é vazio, então nada a reproduz o ruído a partir do estado exposto.
//! Se o SO não fornecer entropia, o programa para (fail closed) em vez de usar um gerador fraco.
//!
//! @trace T-RNG   interface de fonte de palavras (mesmos amostradores exatos de `Rng64`)

use crate::rng::Rng64;

#[derive(Clone, Copy, Debug, Default)]
pub struct OsRng;

impl Rng64 for OsRng {
    fn next_u64(&mut self) -> u64 {
        let mut buf = [0u8; 8];
        getrandom::getrandom(&mut buf)
            .expect("gerador do sistema operacional indisponível (fail closed)");
        u64::from_le_bytes(buf)
    }
}
