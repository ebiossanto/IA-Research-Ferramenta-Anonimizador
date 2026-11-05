"""SplitMix64 + amostradores inteiros exatos (sem float).

AVISO DE SEGURANÇA: SplitMix64 é determinístico e NÃO é criptograficamente seguro. Serve para testes
reprodutíveis. A garantia de privacidade (ε-DP) exige que o ruído seja imprevisível para quem lê o estado:
em produção use um CSPRNG semeado com entropia do SO e NÃO armazene a semente no estado exposto.

@trace T-RNG   gerador determinístico, idêntico em Python/Rust/Lean
@trace T-SAM   amostrador geométrico bilateral exato (P[Z=z] = (1-a)/(1+a) * a^|z|, a = p/q)
"""
MASK64 = (1 << 64) - 1
K_GOLDEN = 0x9E3779B97F4A7C15
K_MIX1 = 0xBF58476D1CE4E5B9
K_MIX2 = 0x94D049BB133111EB
K_SEED_B = 0xD1B54A32D192ED03


class SplitMix64:
    def __init__(self, seed):
        self.state = seed & MASK64

    def next_u64(self):
        self.state = (self.state + K_GOLDEN) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * K_MIX1) & MASK64
        z = ((z ^ (z >> 27)) * K_MIX2) & MASK64
        return z ^ (z >> 31)

    def below(self, n):
        """Uniforme em [0, n), por rejeição (sem viés de módulo). Consome >= 1 palavra."""
        if n < 1 or n > MASK64:
            raise ValueError("n fora de [1, 2^64-1]")
        limit = ((1 << 64) // n) * n  # maior múltiplo de n <= 2^64
        while True:
            x = self.next_u64()
            if x < limit:
                return x % n

    def bernoulli(self, p, q):
        """True com probabilidade p/q (0 <= p <= q, q >= 1)."""
        return self.below(q) < p

    def geometric(self, p, q):
        """Nº de sucessos antes da primeira falha: P[G=k] = (p/q)^k (1 - p/q)."""
        k = 0
        while self.bernoulli(p, q):
            k += 1
        return k

    def two_sided_geometric(self, p, q):
        """Z = G1 - G2 (G1, G2 iid): P[Z=z] = ((q-p)/(q+p)) (p/q)^|z|."""
        a = self.geometric(p, q)
        b = self.geometric(p, q)
        return a - b


def derive_seed(seed, a, b):
    s = (seed ^ ((a * K_GOLDEN) & MASK64) ^ ((b * K_SEED_B) & MASK64)) & MASK64
    return SplitMix64(s).next_u64()


def fnv1a64_ints(values):
    """FNV-1a 64 sobre inteiros (cada um como 8 bytes little-endian, complemento de 2)."""
    h = 0xCBF29CE484222325
    for v in values:
        w = v & MASK64
        for i in range(8):
            h ^= (w >> (8 * i)) & 0xFF
            h = (h * 0x100000001B3) & MASK64
    return h
