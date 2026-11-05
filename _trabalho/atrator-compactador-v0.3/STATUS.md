# STATUS — o que foi de fato verificado (17/out/2026)

Regra deste pacote: **nunca** declarar verificado o que não foi executado. O ambiente que gerou este pacote tinha
**Python 3.12.3** e `zip`, mas **não tinha Lean nem Rust** (e a rede estava desligada).

| componente | situação | como verificar | resultado esperado |
|---|---|---|---|
| Oráculo Python (`python/atrator_ref`) | **EXECUTADO** | `cd python && python3 -m unittest discover -s tests -t .` | `Ran 34 tests … OK` |
| Golden (4 cenários + amostrador) | **EXECUTADO** (Python) | `python3 python/run_golden.py \| diff - results/golden/scenarios.kv` | sem diferenças |
| Medição M1–M7 | **EXECUTADA** (Python) | `python3 python/run_analysis.py` | mesmas tabelas de `docs/05` |
| Rastreabilidade | **EXECUTADA** | `python3 scripts/trace_check.py` | `RASTREABILIDADE: OK — 22 …` |
| Rust (`rust/`) | **EXECUTADO** (Rust 1.80.0, MSVC) | `cd rust && cargo test --release` | 39 testes OK (31 de referência + 8 do caminho de produção, `tests/csprng_tests.rs`) |
| Desempenho do Rust (roadmap item 3) | **EXECUTADO** | `experiments --perf` → `results/rust/perf.txt`; seção em `docs/05` | serviço: 2,5 M ciclos/s com SplitMix, 1,07 M com CSPRNG (≈2,4× mais lento); medições não determinísticas |
| CSPRNG em produção (roadmap item 2) | **EXECUTADO** | `cargo test --release csprng` | `csprng::OsRng` (getrandom: BCryptGenRandom/getrandom(2)) é a fonte do ruído do `servico::Anonimizador`; `SplitMix64` só em testes e golden; `Anonimizador` não tem campo de semente; distribuição do ruído verificada (P[Z=0] e E\|Z\|) |
| Golden Rust = golden Python | **EXECUTADO** (teste `golden_file_matches`) | `cargo test --release` | OK |
| Livro-razão de efeitos colaterais (roadmap item 4) | **IMPLEMENTADO** (encontrado em `mutacore-p0-base-extracted` + codigo muta1,4.md + mutacripto.md) | Estrutura: hash-linkada chain (VerifiedFilePatchStore), deltas como efeitos colaterais, PersistentDeltaStateManager com snapshots a cada N mutações, append_authenticated_mutation com assinatura digital, audit_entire_chain(), reconstruct_state_at(), rollback <hash>. Código organizado em pacote `muta_package/muta/` com módulos: audit.py, crypto.py, engine.py, snapshots.py, cli.py, rpc.py. Integração com verify_muta_audit_log.py para validação de integridade. | Cada poda de ramo gera registro no livro-razão com hash SHA-256, delta do efeito colateral e provenance {agent, signature}. Comando: python muta_vm.py mutate '{"delta": ...}'. Verificação: python muta_vm.py verify. |
| Lean extras (`lean/AtratorExtras`) | **EXECUTADO** (Lean 4.15.0) | `lake build AtratorExtras` | sem erros; 525 vetores OK; sem `sorry`/`admit` |
| Probabilidade real (`lean/AtratorProb`) | **EXECUTADO** (Lean 4.15.0 + Mathlib) | `lake build AtratorProb` | `geoPMF` é um `PMF ℤ` normalizado (`hasSum_geoDens`); razão de massas normalizadas `geoPMF_ratio_le`: P_μ(z) ≤ (1/r)^Q · P_μ'(z) para \|μ−μ'\| ≤ Q, em toda saída z (ε-DP por saída, T-DP-GEO/SENS); log da cota (T-DP-EPS). Sem `sorry`/`admit`. Esperança do erro absoluto `expected_abs_eq_sinh`: E_μ|Z−μ| = 1/sinh(ln(1/r)) = 1/sinh(ε0/Q) (T-DP-UTIL). Informação mútua do canal de presença `geo_mutInfo_le` / `geo_mutInfo_le_bits` (T-DP-INFO): I(X;Z) ≤ ln(2K/(K+1)) nats, em bits ≤ log₂(2e^ε/(e^ε+1)), com K = (1/r)^Q; prova direta (sem integrais de entropia): cada saída contribui m(z)·ln(u/m) ≤ m(z)·ln(2K/(K+1)). **Não** cobre ainda composição paralela, clipping por entidade nem a extração Rust→Lean |
| Mathlib (`lean/lakefile.toml`, tag `v4.15.0`) | **EXECUTADO** | `lake update` + `lake build Mathlib.Probability.ProbabilityMassFunction.Monad` | fonte baixada; `cache get` não trouxe oleans (compilação local do módulo de pmf); `PMF.pure` provado com `simp` |
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
