//! SplitMix64 e amostradores inteiros exatos (sem ponto flutuante).
//!
//! AVISO DE SEGURANÇA: SplitMix64 é determinístico e NÃO é criptograficamente seguro; serve a testes
//! reprodutíveis. A garantia ε-DP exige ruído imprevisível para quem lê o estado: em produção use um
//! CSPRNG com entropia do SO e não armazene a semente no estado exposto.
//!
//! @trace T-RNG   gerador determinístico, idêntico em Python/Rust/Lean
//! @trace T-SAM   amostrador geométrico bilateral: P[Z=z] = (q-p)/(q+p) * (p/q)^|z|

pub const K_GOLDEN: u64 = 0x9E3779B97F4A7C15;
pub const K_MIX1: u64 = 0xBF58476D1CE4E5B9;
pub const K_MIX2: u64 = 0x94D049BB133111EB;
pub const K_SEED_B: u64 = 0xD1B54A32D192ED03;

#[derive(Clone, Debug)]
pub struct SplitMix64 {
    state: u64,
}

impl SplitMix64 {
    pub fn new(seed: u64) -> SplitMix64 {
        SplitMix64 { state: seed }
    }

    pub fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_add(K_GOLDEN);
        let mut z = self.state;
        z = (z ^ (z >> 30)).wrapping_mul(K_MIX1);
        z = (z ^ (z >> 27)).wrapping_mul(K_MIX2);
        z ^ (z >> 31)
    }

    /// Uniforme em [0, n) por rejeição (sem viés de módulo). Consome >= 1 palavra.
    pub fn below(&mut self, n: u64) -> u64 {
        assert!(n >= 1, "below: n deve ser >= 1");
        let limit: u128 = ((1u128 << 64) / (n as u128)) * (n as u128);
        loop {
            let x = self.next_u64();
            if (x as u128) < limit {
                return x % n;
            }
        }
    }

    /// Verdadeiro com probabilidade p/q.
    pub fn bernoulli(&mut self, p: u64, q: u64) -> bool {
        self.below(q) < p
    }

    /// Nº de sucessos antes da primeira falha: P[G=k] = (p/q)^k (1 - p/q).
    pub fn geometric(&mut self, p: u64, q: u64) -> u64 {
        let mut k: u64 = 0;
        while self.bernoulli(p, q) {
            k += 1;
        }
        k
    }

    /// Z = G1 - G2 (G1, G2 iid): P[Z=z] = ((q-p)/(q+p)) (p/q)^|z|.
    pub fn two_sided_geometric(&mut self, p: u64, q: u64) -> i64 {
        let a = self.geometric(p, q);
        let b = self.geometric(p, q);
        (a as i64) - (b as i64)
    }
}

pub fn derive_seed(seed: u64, a: u64, b: u64) -> u64 {
    SplitMix64::new(seed ^ a.wrapping_mul(K_GOLDEN) ^ b.wrapping_mul(K_SEED_B)).next_u64()
}

/// FNV-1a 64 sobre inteiros (cada um como 8 bytes little-endian, complemento de 2).
pub fn fnv1a64_ints(values: &[i64]) -> u64 {
    let mut h: u64 = 0xCBF29CE484222325;
    for &v in values.iter() {
        let w = v as u64;
        for i in 0..8u32 {
            h ^= (w >> (8 * i)) & 0xFF;
            h = h.wrapping_mul(0x100000001B3);
        }
    }
    h
}
