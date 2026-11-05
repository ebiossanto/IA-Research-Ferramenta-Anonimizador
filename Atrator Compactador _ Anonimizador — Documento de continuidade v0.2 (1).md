# Atrator Compactador / Anonimizador — Documento de continuidade v0.2

**Data:** 17 de outubro de 2026 · **Substitui:** v0.1 (25/set/2026, preservada em `docs/arquivo/`) **Objetivo do projeto (definido por você em 16/out):** o atrator compactador é um **anonimizador de informações** — *apaga* a informação e *preserva o "estado"*. **Entregáveis finais pedidos:** (1) base matemática formal em Lean 4, (2) implementação em Rust, (3) rastreabilidade código ↔ matemática, (4) medição, (5) testes reproduzíveis. **Natureza deste documento:** ponto de retomada completo. Não é parecer jurídico.

---

## 1. Resumo em um minuto

- **Resposta à pergunta central — "quanto resíduo o compactador consegue esquecer, em termos de um ε?"** Para qualquer registro apagado: a **identidade** deixa **0 bits** (apagamento estrutural, sem ruído); a **presença/magnitude** deixa no máximo **ε0 = Q·ln(q/p)** (cota justa) enquanto a janela está no anel, o que equivale a **≤ log₂(2e^ε0/(e^ε0+1)) bits** (≤ 0,548 bit para ε0 ≈ 1; medido 0,128 bit); e, depois de `W` selos, o vazamento é **exatamente 0**.
- **O "atrator" ganhou duas coordenadas que contraem:** a exposição viva `u` (limite ISS: `u ≤ B`, e `u → 0` quando a injeção cessa) e o resíduo de informação `Λ` (perfil `ε0 → 0` por evicção). Isto é a versão quantitativa do pedido original "que os resíduos tendam a zero".
- **O que existe agora:** texto matemático completo (9 teoremas, 6 lemas e 5 proposições, `docs/03`), oráculo executável em **Python (34 testes, 4 cenários, medições reais)**, implementação em **Rust** e base **Lean 4** (22 teoremas + 525 vetores) — **estas duas últimas foram escritas e revisadas, mas NÃO compiladas/executadas aqui** (o ambiente não tinha toolchain nem rede) —, rastreabilidade (22 itens, verificador executado: OK) e o pacote `.zip`.
- **O primeiro passo ao retomar:** rodar `scripts/reproduce.sh` numa máquina com Rust e Lean. É a verificação real; espere pequenos ajustes (nomes de lemas do Lean, detalhes de compilação do Rust).

---

## 2. O resultado central: o que o leitor pós-apagamento consegue obter

Leitor pós-apagamento = quem copia o estado interno num instante `K` depois do apagamento (intrusão única, noção de *pan-privacy*).

| fase do registro | o que está no estado | vazamento sobre o registro |
| --- | --- | --- |
| vivo (fila FIFO) | dado bruto (necessário para compensar) | **total** — fora do teorema |
| liquidado, ainda não selado (*janela aberta*) | dado bruto | **total** — fora do teorema (≤ L+τ−1 ciclos) |
| selado, no anel (idade \< W) | só o agregado com ruído geométrico | identidade: **0 bits**; presença/magnitude: **≤ ε0 = Q ln(q/p)** |
| evictado (idade ≥ W) | nada | **exatamente 0** |

**Parâmetros do cenário de referência** (`Q=20`, `p/q=39/41`): `ε0 = 1,0002`, `e^ε0 = 2,7188`.

- **Cota é justa:** um teste "presente se saída ≥ τ" atinge exatamente `TPR/FPR = e^ε0 = 2,7188` para τ ≥ 20 (medida M3).
- **Em bits:** cota 0,548 bit; informação mútua exata 0,128 bit (M4).
- **Utilidade:** o erro esperado por janela e coordenada é `1/sinh(ε0/Q) ≈ Q/ε0`; no cenário `steady` (8 153 registros → 64 inteiros retidos, ≈ 127 : 1) o erro relativo é **7,3 %** em ε0 ≈ 1 (M5: 84,5 % em ε0=0,1; 14,2 % em 0,5; 4,0 % em 2; 0,9 % em 8).
- **"Orçamento de esquecimento":** ε0 é gasto **uma vez**, no selo (composição *paralela* — registros disjuntos), e é **devolvido pela evicção**. Na DP clássica o orçamento nunca volta porque o dado persiste. Teto de política `E` ⇒ escolha `p/q ≥ e^{−E/Q}`. *(Não confundir com o "orçamento de irreversibilidade" de segurança da literatura de agentes — ver `02`.)*
- **Linha do tempo (ciclos):** bruto presente ≤ `L + τ − 1`; vazamento ε0 por ≤ `W·τ`; esquecimento total ≤ `L + τ − 1 + W·τ`, com `L = N(B+I) − 1` (cota de latência). Nos 4 cenários as cotas nunca foram violadas (0 violações; folga de 1,7× a 9×).

---

## 3. O que mudou desde a v0.1 (correções e decisões)

| # | v0.1 dizia | agora |
| --- | --- | --- |
| 1 | `U(t+τ) ≤ (1−γ)U(t) + I` com descarga **condicionada** a limiar | só vale com descarga a cada ciclo. **Corrigido:** duas camadas (fundo `g0>0` sempre + reforço `g1` acima de `θ`); cota `B* = max(⌈(d−g0)θ/d⌉, ⌈(d−g1)I/g1⌉)` |
| 2 | "converge por Banach" (1.ª resposta) → ISS (v0.1) | ISS formalizado: Lyapunov (Teo. 1), invariância (Teo. 2), forma fechada (Teo. 3) |
| 3 | compactação "preserva o rastro auditável" | agregados **ruidosos** não são auditoria fiel; ε0 é o botão; modo **exato** (sem ruído) só apaga identidade |
| 4 | Landauer como grandeza | é **motivação** (≈3×10⁻²¹ J/bit, irrelevante em engenharia); a grandeza é a entropia estrutural medida aqui |
| 5 | misturava orçamento de segurança e limpeza | **separados**: orçamento de irreversibilidade já tem anterioridade de terceiros; o ângulo próprio é o resíduo/esquecimento |
| 6 | (não tratado) | aritmética **inteira** (implementações de DP em float são vulneráveis — Mironov 2012) |
| 7 | decaimento "tende a zero" | **evicção** em vez de decaimento exponencial do estado: em inteiros, o arredondamento deixa uma diferença de 1 unidade entre históricos vizinhos para sempre; a evicção dá zero **exato** |
| 8 | latência ≤ B+I | cota apertada `N(B+I) − 1` (45 contra 160 no cenário `steady`) |

---

## 4. Fundamentação e ligações formais

**Privacidade diferencial / pan-privacy.** O mecanismo é o **geométrico** (Ghosh–Roughgarden–Sundararajan) sobre um histograma de sensibilidade `Q`; o leitor pós-apagamento é o adversário de **intrusão única** de pan-privacy (Dwork–Naor–Pitassi–Rothblum–Yekhanin, ICS 2010). Ganho local: cada janela é *escrita uma vez* (intrusões repetidas na parte selada não acumulam perda) e a evicção devolve o orçamento.

**Unlearning e SISA.**

| SISA / unlearning | aqui |
| --- | --- |
| *shard* (partição do treino) | janela selada (cada registro vive em exatamente uma) |
| esquecimento exato = retreinar só o shard afetado | **evicção** (custo O(1)); `drop_window` quando o bruto já não existe |
| remoção aproximada/certificada `(ε,δ)` | para toda janela no anel, o estado já é `e^ε0`-indistinguível do estado sem o registro — a identidade é um *unlearner* `(ε0,0)` |
| *Data Unlearning with Model State History* (usa o histórico de estados) | analogia **estrutural** com a árvore de estados do MUTA (podar um ramo ≈ descartar/recomputar uma janela); não é equivalência |

**Operador C e `I = T(χ, q, S)` (caracteres mutáveis).** `χ` = registro bruto; `q` = estado interno (o anel); `S` = sinal externo (parâmetros públicos `Q, W, τ, (p,q)`, índice da janela); `T_C` = *agregar ∘ ruído ∘ evictar*, com `q' = T_C(χ, q, S)`. A informação que sobra após apagar `χ` é `I = F(q')`. A pergunta central do projeto — quanto da informação pode ser deslocada do símbolo explícito para `(T, q)` — tem aqui uma resposta quantitativa para um caso particular: o que sobra é **só o agregado** (estatística suficiente para a contabilidade), com vazamento sobre `χ` nulo para a identidade e `≤ ε0` para presença/magnitude. É compressão **com perda** (MDL: taxa × distorção): 8 153 → 64 inteiros a 7,3 % de erro.

**MUTA.** Cada poda de ramo da árvore (Merkle) de estados é um evento de apagamento ⇒ um registro no livro-razão de efeitos colaterais. **O código atual do MUTA é um mock**; o primeiro passo prático é implementar o livro-razão, não "adicionar o atrator".

---

## 5. Estado do trabalho (honesto)

| exigência | o que existe | evidência | **não** verificado |
| --- | --- | --- | --- |
| **1. Lean 4** | 8 arquivos, 22 teoremas (núcleo sem Mathlib + extras), 525 vetores `native_decide` | revisão à mão | **compilação (`lake build`)** |
| **2. Rust** | crate `std`-only, `#![forbid(unsafe_code)]`, 792 linhas + 559 de testes (31 `#[test]`) | revisão à mão; mesma lógica do oráculo | **compilação e `cargo test`** |
| **3. Rastreabilidade** | 22 itens; `trace/policy.csv` + `matrix.csv` gerada; `scripts/trace_check.py` | verificador **executado: OK** | correspondência *semântica* formal (só estrutural + diferencial) |
| **4. Medição** | relatório M1–M7 (`docs/05`) a partir do oráculo Python | **executado** (Python 3.12.3) | desempenho do Rust (`experiments --perf` pronto, sem números) |
| **5. Testes reprodutíveis** | 34 testes Python, 4 cenários golden, 525 vetores, sementes fixas, `reproduce.sh` | Python **executado**: 34/34 OK; golden determinístico | igualdade Python = Rust byte a byte (teste escrito, não rodado) |

**Níveis de garantia da rastreabilidade:** L0 doc ↔ ID · L1 ID ↔ Lean ↔ Rust ↔ testes (**automático, executado**) · L2 vetores diferenciais e golden (Python executado; Rust/Lean aguardam execução) · L3 testes de propriedade que espelham hipóteses e conclusões dos teoremas · L4 extração verificada Rust → Lean (Aeneas) — **roadmap**. Portanto hoje "o código corresponde à matemática" está garantido até L1 e *testado* em L2–L3; **não** é prova formal do Rust.

---

## 6. Medições principais (Python de referência; detalhes em `docs/05`)

| cenário | exposição máx / B | latência máx / cota | idade do bruto máx / cota | registros → ints retidos | erro rel. | violações |
| --- | --- | --- | --- | --- | --- | --- |
| steady | 58 / 120 | 5 / 45 | 54 / 94 | 8 153 → 64 | 7,3 % | 0 |
| burst | 140 / 141 | 11 / 50 | 39 / 89 | 3 365 → 36 | 9,2 % | 0 |
| stop | 290 / 291 | 33 / 94 | 51 / 118 | 2 104 → 16 | — | 0 |
| exact | 58 / 120 | 6 / 45 | 53 / 94 | 3 985 → 64 | 0 % | 0 |

- `stop`: a exposição somada era 522 no instante da parada e **zerou em 32 ciclos** (cota 90): "tende a zero" observado.
- `burst`: exposição máxima **140 contra B = 141** — a cota ISS é quase atingida (praticamente justa).
- Verificações exaustivas: 246 820 casos de contrato da descarga e 33 345 da razão geométrica, todas OK.
- Perfil de esquecimento acoplado: diferença de estado = **exatamente** a magnitude do registro (17) por 8 selos e **exatamente 0** depois.

---

## 7. Novidade e anterioridade (resumo; completo em `docs/02`)

- **Não é novo:** DP geométrica, pan-privacy, ISS, unlearning/SISA, Saga/compensação, formalização de DP em assistentes de prova com aritmética finita (Coq, 2023). O **orçamento de irreversibilidade** para agentes já tem artigos (arXiv 2603.03515 e 2609.00275) e implementações abertas (revoco, irredux).
- **O que este pacote combina:** (a) duas contrações acopladas (exposição ISS + resíduo de informação com evicção) no mesmo ciclo de vida de registros; (b) cota de latência e linha do tempo em ciclos; (c) orçamento de esquecimento *restituído por evicção*; (d) formalização em Lean do núcleo; (e) o contexto de sandbox de agentes. Se houver algo protegível, estará na **combinação** — **exige busca profissional de anterioridade e parecer de advogado de PI**; esta pesquisa foi web, rápida.
- **Cuidado:** publicar o repositório/artigo antes de decidir sobre patente pode afetar a patenteabilidade (períodos de graça variam por jurisdição) — consulte um profissional **antes** de publicar.

---

## 8. Riscos e limites (os que mais importam)

1. **Janela aberta:** o bruto existe até o selo; o teorema cobre só janelas seladas (reduzir `τ`; ruído local na entrada).
2. **Aleatoriedade:** `SplitMix64` é para testes. Produção exige **CSPRNG** e a semente **não** pode ficar no estado exposto (senão o ruído é subtraído).
3. **Remanência física:** `wipe` zera o buffer em memória; swap, SSD, cache e DRAM estão fora do modelo.
4. **Modo exato ≠ privado.**
5. **Auditoria × privacidade:** agregados ruidosos não substituem registro de auditoria; retenção regulatória exige parecer jurídico.
6. **Unidade de proteção:** ε0 protege *um registro*; entidades com muitos registros pagam `M_e·ln(q/p)`; falta *clipping* por entidade.
7. **MUTA** ainda é mock.
8. **Lean/Rust não compilados** neste ambiente.

---

## 9. Próximos passos (ordem sugerida)

1. **Rodar `scripts/reproduce.sh`** (Rust + Lean) e corrigir o que quebrar; registrar em `STATUS.md`.
2. **CSPRNG** no Rust + remoção da semente do estado; teste de que `master_seed` não é serializado.
3. **Medir o Rust** (`experiments --perf`) e anexar a `docs/05`.
4. **Livro-razão de efeitos colaterais** no MUTA (item 1 da arquitetura da v0.1) com os tipos `Record/Class` do crate.
5. **Lean + Mathlib:** probabilidade real (ε-DP completo, normalização, composição, informação mútua).
6. **Verificação do Rust:** extração Rust → Lean com Aeneas/Charon (o crate foi mantido em subconjunto seguro por isso); Kani para propriedades limitadas.
7. **Clipping por entidade** e estudo de ε por entidade; janela aberta: ruído local.
8. **Busca profissional de anterioridade** + parecer de PI; só então decidir sobre publicação (artigo/relatório técnico).

---

## 10. Mapa do pacote e como reproduzir

```
README.md            visão geral          STATUS.md   estado real de cada verificação
docs/                00 (este) · 01 histórico e decisões · 02 anterioridade · 03 TEORIA (tratado) · 04 projetos relacionados · 05 medição · 06 roadmap · arquivo/v0.1
lean/                AtratorCore (4 arquivos) · AtratorExtras (4) · lakefile.toml · lean-toolchain
rust/                crate `atrator` (lib + bin `experiments`) · testes · Cargo.toml · rust-toolchain.toml
python/              oráculo executável (atrator_ref) · testes · run_golden.py · run_analysis.py
trace/               policy.csv · matrix.csv · vectors.csv · README
results/             golden/ (scenarios.kv) · analysis/ (medicao.md) · py/ · rust/
scripts/             reproduce.sh · trace_check.py · gen_vectors.py
references/          bibliografia.md (com status de verificação)
```

```bash
bash scripts/reproduce.sh        # rastreabilidade → Python → golden → Lean (se houver) → Rust (se houver) → golden Rust → medição
python3 scripts/trace_check.py   # só a rastreabilidade
cd python && python3 -m unittest discover -s tests -t .   # só os testes Python (34)
```

**Referências principais:** ver `references/bibliografia.md` (DP, pan-privacy, geometric mechanism, Mironov 2012, unlearning/SISA, ISS, Aeneas, Landauer/Bennett, Saga, remanência).