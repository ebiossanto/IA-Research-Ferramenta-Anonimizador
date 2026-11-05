# Teoria do Atrator Compactador como Anonimizador

**Versão 0.2 — 16/out/2026.** Este é o texto matemático do pacote. Cada resultado traz um rótulo `@trace T-…`
que o verificador (`scripts/trace_check.py`) cruza com o Lean, o Python de referência, o Rust e os testes.

**Níveis de verificação usados em cada resultado** (ver `STATUS.md` para o estado real):

| símbolo | significado |
|---|---|
| **[P]** | prova em papel (neste documento) |
| **[L]** | enunciado + prova escritos em Lean 4 (`lean/`) — *escritos, ainda não compilados* |
| **[T]** | testado: exaustivo/propriedade/vetores no oráculo Python (executado) e no Rust (escrito, não executado) |

---

## 0. Objetivo e resultado em uma frase

> **Apagar** o dado bruto de um sistema complexo e ainda **preservar o estado** necessário (contabilidade de exposição),
> com (i) exposição viva *limitada* e *decaindo a zero* quando a injeção cessa, (ii) identidade apagada *exatamente*,
> (iii) vazamento residual sobre presença/magnitude de qualquer registro *limitado por ε0* e (iv) vazamento *exatamente zero*
> depois da evicção.

O “atrator compactador” tem duas coordenadas que contraem: a **exposição viva** `u` (limite ISS) e o **resíduo de informação** `Λ`
(perfil `ε0` enquanto a janela está no anel; `0` depois). Esta é a versão quantitativa do desejo original de que “os resíduos tendam a zero”.

---

## 1. Modelo

**Registro** `r = (id, a, q, κ, t)`: identidade/payload `id`, âncora `a ∈ {0..m−1}`, magnitude `q ∈ {1..Q}`,
classe `κ ∈ {C (compensável), N (irreversível)}`, ciclo de nascimento `t`.

**Ciclo de vida:** vivo (fila FIFO por âncora, só `κ=C`) → liquidado → **anonimizado** (bruto apagado; resta um agregado ruidoso) → **evictado**.
Registros `κ=N` nascem liquidados (não há o que compensar; formam o *piso* irreversível).

**Por ciclo `t`:**

1. *Injeção.* Por âncora, a exposição compensável injetada `ι ≤ I` (excedentes são descartados pelo corte `I`).
2. *Descarga D.* Com `v = u + ι`: taxa `g(v) = g1` se `v > θ`, senão `g0` (`1 ≤ g0 ≤ g1 ≤ d`); orçamento `⌈g(v)·v/d⌉`;
   liquida registros em FIFO até o acumulado atingir o orçamento; `u' = v − acumulado`.
3. *Selagem C (a cada `τ` ciclos).* Agrega os liquidados em `A ∈ ℕ^{2m}` (coordenada `(a,κ)`), **zera o payload bruto**,
   soma ruído geométrico bilateral `Z` (parâmetro `α = p/q`) a cada coordenada, empurra a janela no anel e **evicta** acima de `W`.

**Estado preservado:** `S_K = (Y_{K−W+1}, …, Y_K)` (as `W` janelas seladas mais recentes), `Y_i = A(R_i) + Z_i`.
`Modo exato` = sem ruído (`Z = 0`): apaga identidade, não protege presença/magnitude.

**Adversário (leitor pós-apagamento).** Obtém uma cópia de `S_K` num instante `K` (intrusão única, noção de *pan-privacy* de Dwork–Naor–Pitassi–Rothblum–Yekhanin, ICS 2010).
Os registros de janelas já seladas foram apagados. **Fora do teorema:** registros vivos, liquidados e ainda não selados (a *janela aberta*), e cópias físicas fora do processo (§7).

**Aritmética.** Inteira em todo o caminho do golden. Motivo: implementações de mecanismos de DP em ponto flutuante são vulneráveis (Mironov, CCS 2012);
o mecanismo geométrico em inteiros evita o problema. Pré-condição: `1 ≤ d ≤ 2³²`, `v < 2⁶⁴` (sem estouro em `u128`).

---

## 2. Parte I — Exposição viva: contração e limite ISS

**Lema 1 (removal).** *[P][L][T]* `@trace T-D-REM`
Para `d ≥ 1`, `0 ≤ g ≤ d` e `ρ = ⌈g·v/d⌉ = ⌊(g·v + d − 1)/d⌋`: `g·v ≤ d·ρ` e `ρ ≤ v`.

*Prova.* Seja `q = ⌊(gv+d−1)/d⌋`, `r = (gv+d−1) mod d`. Então `d·q + r = gv + d − 1` e `r ≤ d−1`, logo `d·q ≥ gv`.
Como `gv ≤ dv`, `gv + d − 1 < d(v+1)`, logo `q < v+1`. ∎

**Lema 2 (contrato da descarga).** *[P][L][T]* `@trace T-D-CONTRACT`
`D(v) = v − ρ` satisfaz `d·D(v) + g·v ≤ d·v` (isto é, `D(v) ≤ (1 − g/d)·v`).

*Prova.* `d(v−ρ) = dv − dρ ≤ dv − gv` pelo Lema 1. ∎

**Lema 3 (monotonia).** *[P][L][T]* `@trace T-D-MONO`
Se `g ≤ d` e `a ≤ b`: `d·a + g·b ≤ d·b + g·a` (equivale a `(d−g)(b−a) ≥ 0`).

**Lema 4 (positividade).** *[P][L][T]* `@trace T-D-POS`
Se `g ≥ 1` e `v ≥ 1` então `ρ ≥ 1` e `D(v) < v`. Logo, **sem injeção a exposição chega a 0** em ≤ `N(u)` passos (`N` do Teorema 4).

**Descarga admissível.** Qualquer regra que, de `v = u + ι`, produza `u'` com `d·u' + g(v)·v ≤ d·v`. Tanto a função `disch`
quanto a descarga FIFO por registros (que liquida *pelo menos* o orçamento) são admissíveis.

**Teorema 1 (Lyapunov).** *[P][L][T]* `@trace T-ISS-LYAP`
Para descarga admissível: `d·u' + g0·(u+ι) ≤ d·(u+ι)`, ou seja `u' ≤ (1 − γ0)(u+ι)` com `γ0 = g0/d`.
(*Prova:* `g(v) ≥ g0`.)

**Teorema 2 (invariância / limite último).** *[P][L][T]* `@trace T-ISS-INV`
Se `B` satisfaz **(B1)** `d·θ ≤ d·B + g0·θ` e **(B2)** `d·I ≤ g1·B + g1·I`, então `u ≤ B` e `ι ≤ I` implicam `u' ≤ B`.
O menor tal `B` é `B* = max(⌈(d−g0)θ/d⌉, ⌈(d−g1)I/g1⌉)`. Portanto `u_0 ≤ B ⇒ u_k ≤ B ∀k`.

*Prova.* Caso `v = u+ι > θ`: `d·u' ≤ d·v − g1·v`; por (Lema 3) com `a=v ≤ b=B+I`: `d·v − g1·v ≤ d(B+I) − g1(B+I) = dB + dI − g1B − g1I ≤ dB` por (B2).
Caso `v ≤ θ`: `d·u' ≤ d·v − g0·v ≤ dθ − g0θ ≤ dB` (Lema 3 com `b=θ`, depois (B1)). Em ambos, `u' ≤ B` pelo cancelamento em `d > 0`. ∎

**Teorema 3 (cota ISS fechada).** *[P][T]* `@trace T-ISS-CLOSED`
Para qualquer `u_0` (inclusive acima de `B`) e `ι_k ≤ I`, com `c = d − g0`:
`d^k·g0·u_k + c·I·c^k ≤ c^k·g0·u_0 + c·I·d^k`, equivalente a
`u_k ≤ (1−γ0)^k·u_0 + ((1−γ0)/γ0)·I` — a estimativa ISS com `β(s,k) = (1−γ0)^k s` e `φ(r) = ((1−γ0)/γ0) r` (Sontag).

*Prova (indução).* `k=0` é igualdade. Do Teorema 1, `d·u_{k+1} ≤ c(u_k + I)`. Multiplicando por `d^k g0` e usando a hipótese:
`d^{k+1} g0 u_{k+1} ≤ c[c^k g0 u_0 + cI d^k − cI c^k] + c g0 I d^k = c^{k+1} g0 u_0 + cI d^{k+1} − cI c^{k+1}`, pois `c + g0 = d`. ∎

*Nota de correção (v0.1).* O doc v0.1 usava `U(t+τ) ≤ (1−γ)U(t) + I` com descarga *condicionada* a um limiar; essa recursão só vale se há descarga em todo ciclo.
A formulação de **duas camadas** (fundo `g0>0` sempre + reforço `g1` acima de `θ`) restaura a validade e dá `B*` acima (o `max` com o termo de `θ` é o efeito do limiar).

**Teorema 4 (latência de liquidação FIFO).** *[P][T]* `@trace T-LAT`
Seja `f(R) = R − ⌈g0·R/d⌉` e `N(R) = min{k : f^k(R) = 0}`. Todo registro compensável é liquidado em no máximo `N(B+I) − 1` ciclos.

*Prova.* `f` é não decrescente com incrementos em `{0,1}` (pois `g0 ≤ d`). Seja `R_j` a exposição não liquidada *à frente de e incluindo* o registro no ciclo `j` desde a admissão;
`R_0 ≤ u+ι ≤ B + I`. A descarga remove da cabeça pelo menos `⌈g(v)v/d⌉ ≥ ⌈g0·R_j/d⌉` (porque `g ≥ g0` e `v ≥ R_j`) — e só da frente enquanto o registro não foi liquidado. Logo `R_{j+1} ≤ f(R_j) ≤ f^{j+1}(R_0) ≤ f^{j+1}(B+I)`.
O registro é liquidado quando `R_{j+1} = 0`, o que ocorre para `j + 1 ≥ N(B+I)`. ∎

---

## 3. Parte II — Esquecimento: apagamento estrutural, ruído geométrico, evicção

**Definição (agregado).** `A(R)_{(a,κ)} = Σ q` dos registros de `R` com âncora `a` e classe `κ`. `A` **ignora** `id`, payload e tempo.

**Proposição 1 (apagamento estrutural da identidade).** *[P][L][T]* `@trace T-F-ANON`
Para qualquer reescrita de identidades `φ`: `A(φ(R)) = A(R)`. A saída do compactador depende de `R` só por `A(R)`, logo a informação mútua entre a identidade/payload e a saída, condicionada a `A`, é **exatamente 0 bits** (sem ruído, sem ε).

**Proposição 2 (sensibilidade).** *[P][L][T]* `@trace T-DP-SENS`
Se `R ≃ R'` diferem por **um** registro de magnitude `q_r ≤ Q`, então `A(R)` e `A(R')` diferem em **uma única coordenada**, por `q_r`; logo `‖A(R) − A(R')‖₁ ≤ Q`.
(*Substituição* de um registro = remover + adicionar: `≤ 2Q`; grupo de `g` registros: `≤ gQ`.)

**Mecanismo.** `M(R) = A(R) + Z`, `Z_c` i.i.d. com `P[Z_c = z] = ((q−p)/(q+p))·(p/q)^{|z|}` (geométrico bilateral; `α = p/q`).

**Amostrador.** *[T]* `@trace T-SAM`
`Z = G₁ − G₂` com `G_i` i.i.d. geométricas (`P[G=k] = (1−α)α^k`), cada tentativa um `bernoulli(p,q)` exato por `below(q) < p` com rejeição sem viés de módulo. `@trace T-RNG`:
`SplitMix64` (sequência de referência publicada, vetor de teste com semente 0) com `derive_seed(seed, tag, índice)` para fluxos independentes por janela.

**Lema 5 (razão de massas geométrica).** *[P][L][T]* `@trace T-DP-GEO`
Se `p ≤ q` e `n ≤ m + Q`: `p^{m+Q}·q^n ≤ p^n·q^{m+Q}`, isto é, `(p/q)^m ≤ (q/p)^Q·(p/q)^n`.

*Prova.* Escreva `m+Q = n+t`, `t ≥ 0`. Então `p^{n+t}q^n = p^n q^n p^t ≤ p^n q^n q^t = p^n q^{n+t}` pois `p^t ≤ q^t`. ∎

**Lema 6 (triangular).** *[P][L][T]* `@trace T-DP-TRI`
`|x − z| ≤ |x − y| + |y − z|` em ℤ.

**Teorema 5 (ε0-DP justo).** *[P][L-parcial][T]* `@trace T-DP-EPS`
`M` é **ε0-diferencialmente privado** com `ε0 = Q·ln(q/p)`: para vizinhos `R ≃ R'` e toda saída `y`, `P[M(R)=y] ≤ e^{ε0}·P[M(R')=y]`. A cota é **justa** (atingida para `q_r = Q` e `y` abaixo de ambos os centros).

*Prova.* A constante de normalização `((q−p)/(q+p))^{2m}` não depende do centro, logo a razão é `α^{‖y−A‖₁ − ‖y−A'‖₁}`. Pelo Lema 6, `‖y−A'‖₁ ≤ ‖y−A‖₁ + ‖A−A'‖₁ ≤ ‖y−A‖₁ + Q`, e pelo Lema 5 a razão `≤ α^{−Q} = (q/p)^Q = e^{ε0}`. ∎
*(Em Lean está o núcleo combinatório — `geo_ratio`, `dp_ratio`; a normalização e a passagem a probabilidades reais ficam para Mathlib — ver roteiro.)*

**Teorema 6 (esquecimento exato por evicção; perfil de vazamento).** *[P][L][T]* `@trace T-F-EVICT`
Seja `r` um registro da janela `i` e `K ≥ i`. Defina o vazamento residual `Λ_K(r)` como o supremo, sobre vizinhos `R_i ≃ R_i'`, da divergência máxima (log-razão) entre as leis de `S_K`. Então

```
Λ_K(r) ≤ q_r · ln(q/p)  ≤  ε0      se  K − i < W      (a janela está no anel)
Λ_K(r) = 0                          se  K − i ≥ W      (a janela foi evictada)
```

*Prova.* `S_K` é função de `(Y_{K−W+1..K})`. Se `K − i ≥ W`, `Y_i` não entra em `S_K`: duas histórias que diferem *arbitrariamente* em `R_i` (mesmo não vizinhas) dão o **mesmo** `S_K` sob o mesmo ruído — esse é o `retained_congr` do Lean. Se `K−i < W`, as janelas têm ruído independente, a lei conjunta fatora e a razão total é a da janela `i`: `≤ e^{ε0}` pelo Teorema 5. ∎

**Corolário (intrusões repetidas na parte selada não acumulam perda).** Cada `Y_i` é *escrito uma vez* ao selar. Um adversário com várias cópias de `S` em instantes diferentes vê o **mesmo** `Y_i`: a perda sobre `r` continua `≤ ε0` (não `k·ε0`). Contraste: consultas adaptativas ao dado bruto acumulariam.

**Corolário (entidade).** Uma entidade com magnitude total `M_e` no anel tem perda `≤ M_e · ln(q/p)` (a razão fatora por janela; em cada janela a variação L1 é a magnitude da entidade ali).

**Proposição 3 (descarte exato de janela).** *[P][T]* `@trace T-F-DROP`
`drop_window(i)` torna o estado **independente de todo o conteúdo** de `R_i` (equivale a descartar um *shard* no SISA, ao custo da utilidade daquela janela).
Quando o dado bruto já foi apagado, é a única forma de esquecimento *exato por pedido*; antes disso vale a garantia `ε0`.

**Teorema 7 (informação residual em bits).** *[P][T]* `@trace T-DP-INFO`
Seja `M` ε-DP e `X ~ Bernoulli(½)` a presença de um registro (demais fixos). Então
`I(X;Y) ≤ log₂( 2e^ε / (e^ε + 1) ) ≤ min( ε·log₂ e , 1 )` bits.

*Prova.* `P₁/P_Y = 2P₁/(P₀+P₁) = 2/(1+P₀/P₁) ≤ 2/(1+e^{−ε}) = 2e^ε/(e^ε+1)` ponto a ponto (idem para `P₀`); logo cada termo de KL e a informação mútua são `≤ ln(2e^ε/(e^ε+1))`. E `2e^ε/(e^ε+1) ≤ min(e^ε, 2)`. ∎
*Medido (M4):* com `ε0 ≈ 1,0006` a cota é 0,548 bit e a informação mútua exata é 0,128 bit.

**Teorema 8 (utilidade).** *[P][T]* `@trace T-DP-UTIL`
Com `α = e^{−ε0/Q}`: `E|Z| = 2α/(1−α²) = 1/sinh(ε0/Q) ≈ Q/ε0` e `Var Z = 2α/(1−α)²`.
O erro do estado (soma de `W` janelas) é `≤ W·E|Z|` por coordenada em média, com desvio `√(W·Var Z)`.
*Prova.* `E|Z| = 2·((1−α)/(1+α))·Σ_{k≥1} kα^k = 2α/(1−α²)`; com `α = e^{−x}`, `2e^{−x}/(1−e^{−2x}) = 1/sinh x`. ∎
Compromisso privacidade–utilidade: erro `∝ Q/ε0`. (O mecanismo geométrico é ótimo para contagens: Ghosh–Roughgarden–Sundararajan.)

---

## 4. Teorema principal e linha do tempo

**Teorema 9 (Compactador Anonimizador).** Sob as hipóteses do §1 (descarga admissível, `ι ≤ I`, `B ≥ B*`, mecanismo `M`), para todo registro `r`:

1. **Estabilidade.** A exposição viva de cada âncora satisfaz `u_k ≤ B` (Teo. 2) e a estimativa ISS (Teo. 3); cessada a injeção, `u → 0` em `≤ N(u)` passos (Lema 4).
2. **Latência.** `r` é liquidado em `≤ L := N(B+I) − 1` ciclos (Teo. 4).
3. **Esquecimento.** Identidade: vazamento exatamente 0 (Prop. 1). Presença/magnitude: `≤ ε0` enquanto a janela está no anel; **exatamente 0** depois (Teo. 6). Em bits: `≤ log₂(2e^{ε0}/(e^{ε0}+1))` (Teo. 7).
4. **Utilidade.** O estado preservado tem erro `1/sinh(ε0/Q)` por janela e coordenada (Teo. 8); a exposição viva **não** depende do ruído (a descarga age sobre dados brutos vivos), logo (1) não é afetado.

**Linha do tempo de um registro** *[P][T]* `@trace T-TIMELINE`:

```
nascimento ── ≤ L ciclos ──▶ liquidado ── ≤ τ−1 ──▶ SELADO (bruto apagado; ruído ε0) ── W·τ ciclos ──▶ EVICTADO (vazamento 0)
bruto presente: ≤ L + τ − 1        vazamento ε0: ≤ W·τ        esquecimento total: ≤ L + τ − 1 + W·τ
```

*Prova.* Liquidado em `s ≤ nasc + L`; selado na primeira fronteira `t_s ≥ s` com `(t_s+1) mod τ = 0`, logo `t_s − s ≤ τ−1`; a janela permanece `W` selos. ∎
**Atrator (quantitativo):** com injeção nula a partir de `K`, `u → 0` em `N(u_K)` ciclos e o vazamento de todo registro anterior chega a 0 em `≤ L + τ − 1 + W·τ` ciclos.

**“Orçamento de esquecimento”.** O ε0 é gasto **uma vez**, no selo (composição *paralela* entre janelas disjuntas) e é **restituído por evicção** — ao contrário da DP clássica, em que o orçamento nunca volta porque o dado persiste. O teto de política `E` exige `Q·ln(q/p) ≤ E`, i.e. `p/q ≥ e^{−E/Q}` (escolha de `(p,q)`: `analysis.choose_pq`).
*(Para evitar confusão: isto não é o “orçamento de irreversibilidade” de segurança da literatura de agentes — ver `02-anterioridade-e-referencias.md`.)*

**Proposição 4 (zeragem do bruto).** *[T]* `@trace T-WIPE`
Antes de descartar, o selo zera o payload de cada registro selado (`wipe`) e conta os bytes apagados
(`bytes_erased = 8·registros_apagados` nos cenários). É apagamento *best-effort em memória do processo*
(escrita de zeros + `black_box` para evitar eliminação pelo otimizador, sem `unsafe`). O que **não** garante: cópias do
buffer feitas pelo sistema (swap, páginas de cache, snapshots, SSD com *wear-leveling*, DRAM) — ver §7.3.

**Proposição 5 (reprodutibilidade entre implementações).** *[T]* `@trace T-GOLD`
Todas as grandezas inteiras dos 4 cenários e o histograma do amostrador são **idênticas, byte a byte**, no oráculo Python
(`results/golden/scenarios.kv`, executado) e no Rust (`cargo test`, escrito, ainda não executado); os mesmos 525 vetores
(`trace/vectors.csv`) são checados em Python, em Rust e em Lean (`native_decide`). Isto é verificação *diferencial*, não prova de correção do Rust.

---

## 5. Ligações formais

**Privacidade diferencial e pan-privacy.** `M` é o mecanismo geométrico (Ghosh et al.) aplicado a um histograma com sensibilidade `Q`; o leitor pós-apagamento é o adversário de *intrusão única* de pan-privacy. O ganho aqui: o estado é *escrito uma vez* por janela e a evicção devolve o orçamento.

**Unlearning e SISA.** O anel de janelas é a estrutura de *shards*: cada registro vive em exatamente uma janela; `evicção` = *esquecimento exato* a custo O(1) (no SISA, retreinar o shard afetado); `drop_window` = descarte do shard quando o dado bruto já não existe;
e, para qualquer janela ainda no anel, `S_K` já é `e^{ε0}`-indistinguível do estado sem o registro — a identidade é um *unlearner* (ε0,0)-certificado no sentido de remoção aproximada (Ginart et al.; Guo et al.). A analogia com “Data Unlearning with Model State History” (usar o histórico de estados para reconstituir um modelo sem o conjunto a esquecer) é **estrutural**, não uma equivalência: no MUTA, podar um ramo da árvore de estados corresponde a descartar/recomputar uma janela.

**`I = T(χ, q, S)` (caracteres mutáveis).** Identificação: `χ` = registro bruto; `q` = estado interno (o anel); `S` = sinal externo (parâmetros públicos: `Q, W, τ, (p,q)`, índice da janela); `T_C` = agregar ∘ ruído ∘ evictar, com `q' = T_C(χ, q, S)`.
A informação que sobra depois de apagar `χ` é `I = F(q')`. Os teoremas respondem, neste caso particular, a quanto da informação de `χ` foi “deslocada” para `(T, q)`: **por construção** só o agregado (estatística suficiente *para a contabilidade*), com vazamento sobre `χ` limitado por `ε0` e nulo para a identidade. É a versão com compressão com perda (MDL: taxa × distorção) do projeto: no cenário `steady` 8 153 registros viram 64 inteiros retidos (≈ 127 : 1) a 7,3 % de erro relativo em `ε0 ≈ 1`.

**Landauer.** Motiva por que o resíduo é inevitável (apagar nunca é “limpo”); **não** fornece a grandeza prática (≈3×10⁻²¹ J/bit à temperatura ambiente). A grandeza prática é a entropia *estrutural/informacional* medida aqui.

**MUTA.** Cada poda de ramo da árvore (Merkle) de estados é um evento de apagamento ⇒ um registro no livro-razão de efeitos colaterais. *O código atual do MUTA é um mock*; o primeiro passo prático é o livro-razão (`docs/06-roadmap.md`).

---

## 6. Resumo do que é novo e do que não é

Nada do núcleo matemático (DP geométrica, pan-privacy, ISS, SISA) é novo. O que este pacote reúne e quantifica de forma explícita:
(a) *duas* contrações acopladas (exposição ISS + resíduo de informação com evicção) num mesmo ciclo de vida de registros;
(b) a cota de latência `N(B+I) − 1` e a linha do tempo bruto→ε0→0 em ciclos;
(c) a política “orçamento restituído por evicção” e a formalização em Lean do núcleo inteiro do mecanismo;
(d) o contexto de aplicação (sandbox de agentes com histórico em árvore). Se há algo patenteável, estaria na **combinação** — sujeita a busca profissional (ver `02`).

---

## 7. Limites (leia antes de confiar)

1. **Janela aberta.** O bruto existe do nascimento até o selo (`≤ L + τ − 1` ciclos); o teorema cobre só janelas seladas. Mitigações: `τ` pequeno; ruído local na entrada (mais ruído total).
2. **Intrusões múltiplas.** Dwork et al. provam impossibilidade para algoritmos de estado finito contra duas intrusões não anunciadas em estimação de densidade. Aqui, janelas seladas são *write-once* (imunes), mas a janela aberta e o estado vivo `u` são brutos em toda intrusão.
3. **Remanência física.** `wipe` é *best-effort* (zera o buffer e usa `black_box`); cópias em swap, SSD (wear-leveling), cache, DRAM (cold boot — Halderman et al. 2008; Gutmann 1996) estão **fora do modelo**. O teorema pressupõe que o bruto realmente sumiu.
4. **Modo exato ≠ privado.** Sem ruído só a identidade é apagada.
5. **Auditoria × privacidade.** Agregados com ruído não são registro de auditoria fiel; `ε0` é o botão. Retenção regulatória exige parecer jurídico.
6. **Sem estouro.** Em Lean `Nat` é ilimitado; no Rust assume-se `d ≤ 2³²`, `v < 2⁶⁴` (verificado por testes/assert).
7. **Aleatoriedade.** A garantia ε-DP exige ruído **imprevisível** para quem lê o estado. `SplitMix64` é determinístico e não é
   criptograficamente seguro: serve só a testes reprodutíveis. Em produção: CSPRNG com entropia do SO, e a semente **não** pode
   ficar no estado exposto (quem a conhece subtrai o ruído e recupera o agregado exato).
8. **Unidade de proteção.** O ε0 protege *um registro* (adição/remoção). Entidades com muitos registros pagam `M_e·ln(q/p)`
   (Corolário da entidade); limitar a contribuição por entidade (*clipping*) não está implementado.
9. **Lean e Rust não foram executados** no ambiente que gerou o pacote (ver `STATUS.md`).
