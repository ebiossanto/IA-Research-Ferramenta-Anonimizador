/-!
# SplitMix64 em Lean (UInt64) — mesma definição do oráculo Python e do Rust

`@trace T-RNG`

STATUS: escrito e revisado à mão; NÃO compilado no ambiente que gerou este pacote.
AVISO DE SEGURANÇA: SplitMix64 é determinístico e NÃO é criptograficamente seguro; serve a testes
reprodutíveis. Em produção o ruído da compactação exige CSPRNG (ver docs/03, "Limites").
-/

namespace Atrator

def kGolden : UInt64 := 0x9E3779B97F4A7C15
def kMix1 : UInt64 := 0xBF58476D1CE4E5B9
def kMix2 : UInt64 := 0x94D049BB133111EB
def kSeedB : UInt64 := 0xD1B54A32D192ED03

/-- Um passo: (novo estado, saída). -/
def splitmixNext (s : UInt64) : UInt64 × UInt64 :=
  let s' := s + kGolden
  let z1 := (s' ^^^ (s' >>> 30)) * kMix1
  let z2 := (z1 ^^^ (z1 >>> 27)) * kMix2
  (s', z2 ^^^ (z2 >>> 31))

/-- `n`-ésima saída (0-based) da semente `seed`. -/
def splitmixNth (seed : UInt64) : Nat → UInt64
  | 0 => (splitmixNext seed).2
  | n + 1 => splitmixNth (splitmixNext seed).1 n

def deriveSeed (seed a b : UInt64) : UInt64 :=
  (splitmixNext (seed ^^^ (a * kGolden) ^^^ (b * kSeedB))).2

end Atrator
