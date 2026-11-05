# STATUS — o que foi de fato verificado (17/out/2026)

Regra deste pacote: **nunca** declarar verificado o que não foi executado. O ambiente que gerou este pacote tinha
**Python 3.12.3** e `zip`, mas **não tinha Lean nem Rust** (e a rede estava desligada).

| componente | situação | como verificar | resultado esperado |
|---|---|---|---|
| Oráculo Python (`python/atrator_ref`) | **EXECUTADO** | `cd python && python3 -m unittest discover -s tests -t .` | `Ran 34 tests … OK` |
| Golden (4 cenários + amostrador) | **EXECUTADO** (Python) | `python3 python/run_golden.py \| diff - results/golden/scenarios.kv` | sem diferenças |
| Medição M1–M7 | **EXECUTADA** (Python) | `python3 python/run_analysis.py` | mesmas tabelas de `docs/05` |
| Rastreabilidade | **EXECUTADA** | `python3 scripts/trace_check.py` | `RASTREABILIDADE: OK — 22 …` |
| Rust (`rust/`) | escrito, **NÃO compilado** | `cd rust && cargo test --release` | 31 testes OK |
| Golden Rust = golden Python | escrito, **NÃO executado** | `cargo run --release --bin experiments \| diff - ../results/golden/scenarios.kv` | sem diferenças |
| Lean núcleo (`lean/AtratorCore`) | escrito, **NÃO compilado** | `cd lean && lake build` | sem erros |
| Lean extras (`lean/AtratorExtras`) | escrito, **NÃO compilado** | `lake build AtratorExtras` | sem erros; 525 vetores OK |
| Desempenho do Rust | harness pronto, **sem números** | `cargo run --release --bin experiments -- --perf` | linhas `perf.*` |

## Pontos mais prováveis de ajuste no primeiro build

* **Lean:** (a) `Int.natAbs` com `omega` em `Distance.lean` (há alternativa manual); (b) nomes/assinaturas de lemas do núcleo
  (`Nat.div_add_mod`, `Nat.mod_lt`, `Nat.div_lt_of_lt_mul`, `Nat.div_pos`, `Nat.mul_pos`, `Nat.pow_le_pow_left`, `Nat.lt_succ_of_lt`);
  (c) `simp` em `Aggregation.lean`; (d) `native_decide` em 525 vetores (demora; pode ser trocado por `decide`).
  Toolchain fixada: `leanprover/lean4:v4.15.0`.
* **Rust:** nenhum ponto conhecido, mas **nunca foi compilado**; toolchain fixada em 1.80.0 (`rust-toolchain.toml`).
  `Cargo.lock` mínimo (sem dependências).

## O que NÃO é garantido (mesmo depois de tudo compilar)

* O Rust **não** é provado correto: a correspondência com a matemática é **estrutural** (IDs `@trace`) + **diferencial** (vetores, golden)
  + **testes de propriedade**. Prova formal exigiria extração verificada (Aeneas → Lean; ver `docs/06-roadmap.md`).
* A probabilidade real (ε-DP completo, normalização, composição, informação mútua) está provada **em papel** e testada
  numericamente; não está em Lean (exige Mathlib).
* `wipe` é best-effort em memória do processo; remanência física está fora do modelo.

## Registro de verificações (preencha ao rodar)

| data | quem | passo | resultado | observações |
|---|---|---|---|---|
| | | | | |
