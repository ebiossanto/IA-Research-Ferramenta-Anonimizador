# Lean 4 — base formal (núcleo + extras)

**Status honesto:** estes arquivos foram escritos e revisados à mão, mas **NÃO foram compilados** no ambiente que
gerou o pacote (não havia toolchain Lean e a rede estava desligada). O primeiro `lake build` é a verificação real.
Se algum `theorem` falhar, é provável que seja um nome de lema que mudou entre versões do Lean — corrija e
registre em `STATUS.md`.

```bash
cd lean
lake build                 # núcleo: Contraction, Exposure, GeoRatio, Forgetting (sem Mathlib)
lake build AtratorExtras   # extras: Aggregation, Distance (natAbs), Prng (UInt64), Vectors (native_decide)
```

* Toolchain fixada em `lean-toolchain` (v4.15.0, escolhida por ser uma versão estável conhecida; atualizar é seguro
  desde que se corrijam eventuais nomes de lemas).
* Nada aqui usa `sorry` nem `axiom`; `Vectors.lean` usa `native_decide` (avaliação compilada) para os testes
  diferenciais contra o oráculo Python / Rust.
* O que **não** está formalizado em Lean (só em papel + testes): forma fechada ISS, latência, normalização e
  esperança do ruído, informação mútua, composição. Ver `trace/policy.csv` e `docs/06-roadmap.md`.
