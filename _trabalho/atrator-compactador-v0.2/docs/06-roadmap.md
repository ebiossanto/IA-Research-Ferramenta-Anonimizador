# Roteiro (priorizado, com critério de aceite)

| # | item | critério de aceite |
|---|---|---|
| 1 | **Primeira execução real:** `scripts/reproduce.sh` com Rust e Lean | todos os passos passam; `STATUS.md` atualizado; correções registradas em `docs/01` |
| 2 | **CSPRNG e semente fora do estado** (Rust) | teste prova que o estado serializado não contém a semente; ruído vem de CSPRNG; `SplitMix64` só em testes |
| 3 | **Medir o Rust** | `results/rust/perf.txt` e seção em `docs/05` |
| 4 | **Livro-razão de efeitos colaterais no MUTA** | tipos `Record/Class/âncora` integrados; cada poda de ramo gera registro; integração com `Compactor::seal` |
| 5 | **Lean + Mathlib (fase 2):** ε-DP completo (normalização do pmf geométrico, razão de probabilidades reais), composição paralela, informação mútua `≤ log2(2e^ε/(e^ε+1))`, esperança `1/sinh(ε0/Q)` | cada teorema marcado `[L]` em `docs/03` sem `sorry`; `lake build` verde |
| 6 | **Verificação do Rust (L4):** Charon/Aeneas → Lean para `exposure.rs` e `compactor.rs`; Kani para propriedades limitadas | teorema Lean sobre a função **extraída** do Rust (não só sobre o modelo) |
| 7 | **Formalizar em Lean:** forma fechada ISS (Teo. 3), latência (Teo. 4) | substituir `[P][T]` por `[P][L][T]` |
| 8 | **Clipping por entidade** + ε por entidade | limite `M_e` imposto no selo; teste de que `Σ` por entidade ≤ `M_max` |
| 9 | **Janela aberta:** ruído local na entrada ou `τ` adaptativo | medida da troca ε × utilidade; nova linha do tempo |
| 10 | **Remanência:** zeragem em memória não paginável (`mlock`), criptografia em repouso com chave efêmera, política de descarte de snapshots | documentado e testado onde possível; limites explícitos |
| 11 | **Auditoria × privacidade:** modo duplo (log exato com acesso restrito + agregado ruidoso público) | parecer jurídico sobre retenção; documentação |
| 12 | **Busca profissional de anterioridade** e parecer de PI **antes** de publicar | relatório do profissional |
| 13 | **Relatório técnico/artigo** (após 12) | texto com `docs/03` como núcleo, resultados M1–M7 e Rust/Lean verificados |
