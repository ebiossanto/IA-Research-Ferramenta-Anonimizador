# Medição

**Como ler.** Todos os números abaixo foram **medidos no oráculo Python** (Python 3.12.3), com sementes fixas, e são regenerados por
`python3 python/run_analysis.py` (também chamado por `scripts/reproduce.sh`). Colunas marcadas "exato" são aritmética inteira/racional;
estatísticas com ponto flutuante aparecem só aqui (nunca no golden). **Nada aqui foi medido em Rust ou Lean.**
Para medir o Rust: `cd rust && cargo run --release --bin experiments -- --perf` (vazão em ciclos/s e registros/s; não determinístico) —
cole o resultado na seção "Desempenho do Rust" abaixo.

**Interpretação rápida.**
* M1: nenhuma cota (ISS, latência, idade do bruto) foi violada; `burst` chegou a 140 contra `B = 141`.
* M3: a cota ε0 é **justa** (TPR/FPR = e^ε0 = 2,7188 para τ ≥ Q).
* M4: a informação mútua real (0,128 bit em ε0 ≈ 1) é bem menor que a cota garantida (0,548 bit).
* M5: curva privacidade × utilidade no sistema completo (erro relativo de 84,5 % em ε0=0,1 a 0,9 % em ε0=8).
* M6: o vazamento cai de ε0 para **exatamente 0** na evicção.

## Desempenho do Rust

*(não medido no ambiente de geração — preencher após `experiments --perf`)*

---

Ambiente: Python 3.12.3, Linux-6.18.44-fc-v139-x86_64-with-glibc2.39. **Rust e Lean não foram executados** na geração deste relatório; os números abaixo vêm só da implementação de referência em Python (inteiros exatos onde indicado). Floats aparecem apenas em estatísticas/relatórios, nunca no golden.

## M1. Cenários (os mesmos do golden)

| cenário | registros | descartados (cap I) | descargas reforçadas | exposição máx / B | latência máx / cota | idade bruta máx / cota | registros apagados → ints retidos | erro rel. (‰) | viol. B/contrato/lat. |
|---|---|---|---|---|---|---|---|---|---|
| steady | 8156 | 0 | 182 | 58 / 120 | 5 / 45 | 54 / 94 | 8153 → 64 | 73 | 0/0/0 |
| burst | 3396 | 2 | 92 | 140 / 141 | 11 / 50 | 39 / 89 | 3365 → 36 | 92 | 0/0/0 |
| stop | 2104 | 0 | 46 | 290 / 291 | 33 / 94 | 51 / 118 | 2104 → 16 | 0 | 0/0/0 |
| exact | 3993 | 0 | 81 | 58 / 120 | 6 / 45 | 53 / 94 | 3985 → 64 | 0 | 0/0/0 |

No cenário `stop`: exposição somada no instante da parada = **522**; zerou em **32** ciclos (cota teórica por âncora: 90).


## M2. Fidelidade do amostrador (N=60000, p/q=39/41)

| métrica | medido | teoria |
|---|---|---|
| média | 0.0075 | 0 |
| variância | 794.2 | 799.5 |
| distância de variação total (TV) ao pmf exato | 0.02115 | → 0 com N |
| máx abs(freq − pmf) para z de −15 a 15 | 0.00112 | ~ 1/√N ≈ 0.0041 |


## M3. Ataque de pertinência (presença de um registro de magnitude Q=20), ε0 = 1.0002

Teste do tipo "decidir *presente* se saída ≥ τ". TPR/FPR analítico é exato; coluna final é Monte Carlo (N=60000 por braço).

| τ | TPR (exato) | FPR (exato) | TPR/FPR (exato) | TPR/FPR (MC) |
|---|---|---|---|---|
| -20 | 0.93405 | 0.82070 | 1.1381 | 1.1421 |
| 0 | 0.82070 | 0.51250 | 1.6014 | 1.6010 |
| 10 | 0.70435 | 0.31081 | 2.2661 | 2.2981 |
| 20 | 0.51250 | 0.18850 | 2.7188 | 2.7828 |
| 30 | 0.31081 | 0.11432 | 2.7188 | 2.7776 |
| 40 | 0.18850 | 0.06933 | 2.7188 | 2.7924 |
| 60 | 0.06933 | 0.02550 | 2.7188 | 2.7704 |
| 80 | 0.02550 | 0.00938 | 2.7188 | 2.8490 |

`e^ε0 = 2.7188`; máximo de TPR/FPR sobre τ∈[−100,400): **2.7188** (a cota é atingida: é justa).


## M4. Informação residual sobre a presença de um registro (bits)

Prior uniforme sobre {ausente, presente}; Q=20. `I exata` por soma numérica; `cota` = log2(2e^ε/(e^ε+1)).

| ε0 | p/q | I(X;Y) exata | cota DP | ε0·log2 e (cota folgada) |
|---|---|---|---|---|
| 0.1003 | 9950/10000 | 0.00175 | 0.07050 | 0.14463 |
| 0.2496 | 9876/10000 | 0.01033 | 0.16881 | 0.36003 |
| 0.5002 | 9753/10000 | 0.03808 | 0.31616 | 0.72164 |
| 1.0006 | 9512/10000 | 0.12792 | 0.54830 | 1.44359 |
| 2.0008 | 9048/10000 | 0.35796 | 0.81702 | 2.88658 |
| 4.0008 | 8187/10000 | 0.72059 | 0.97383 | 5.77186 |


## M5. Utilidade × ε0 no sistema (cenário `steady`, só o ruído varia)

| ε0 | p/q | E[abs Z] teoria | E[abs Z] MC (N=3000) | soma abs(erro) no anel | soma abs(verdadeiro) no anel | erro rel. (‰) |
|---|---|---|---|---|---|---|
| 0.100 | 9950/10000 | 199.50 | 197.80 | 14584 | 17241 | 845 |
| 0.250 | 9876/10000 | 80.14 | 78.69 | 5908 | 17241 | 342 |
| 0.500 | 9753/10000 | 39.98 | 38.50 | 2461 | 17241 | 142 |
| 1.001 | 9512/10000 | 19.98 | 19.39 | 1267 | 17241 | 73 |
| 2.001 | 9048/10000 | 9.98 | 9.75 | 698 | 17241 | 40 |
| 4.001 | 8187/10000 | 4.97 | 4.87 | 386 | 17241 | 22 |
| 8.001 | 6703/10000 | 2.43 | 2.44 | 156 | 17241 | 9 |


## M6. Perfil de esquecimento (execução acoplada: mesmo ruído, um registro extra de magnitude 17 na janela 0; W=8)

| janelas seladas após a janela 0 | ‖estado − estado'‖₁ | vazamento residual |
|---|---|---|
| 0 | 17 | ε0 |
| 1 | 17 | ε0 |
| 2 | 17 | ε0 |
| 3 | 17 | ε0 |
| 4 | 17 | ε0 |
| 5 | 17 | ε0 |
| 6 | 17 | ε0 |
| 7 | 17 | ε0 |
| 8 | 0 | 0 (exato) |
| 9 | 0 | 0 (exato) |
| 10 | 0 | 0 (exato) |
| 11 | 0 | 0 (exato) |

A diferença é exatamente a magnitude do registro enquanto a janela está no anel e **exatamente zero** após a evicção.


## M7. Verificações exaustivas (todas passaram)

| propriedade | casos verificados |
|---|---|
| T-D-REM / T-D-CONTRACT: removal e contrato de descarga (d≤40, 1≤g≤d, v≤300) | 246820 |
| T-DP-GEO: p^(m+Q) q^n ≤ p^n q^(m+Q) (q≤9, Q≤5, m≤12) | 33345 |

## Desempenho do Rust (v0.3)

Fonte: 
esults/rust/perf.txt, gerado por cargo run --release --bin experiments -- --perf.
Máquina: AMD Ryzen 3 3200G (4 núcleos), Windows 11 Pro, Rust 1.80.0 (MSVC). **Não determinístico**.

| caminho | medida | valor |
| --- | --- | --- |
| cenários golden (
un, SplitMix, 5 repetições) | steady / burst / stop / exact | 1,1 · 1,7 · 2,0 · 1,3 M ciclos/s |
| serviço de produção, fonte SplitMix (50×2000 ciclos) | ciclos/s | 2,5 M |
| serviço de produção, fonte CSPRNG OsRng (50×2000 ciclos) | ciclos/s | 1,07 M (≈ 2,4× mais lento) |

Leitura: o CSPRNG custa cerca de 2,4× no serviço (uma chamada ao SO por palavra de 64 bits). Ainda assim
passa de 1 M de ciclos por segundo, muito acima de qualquer taxa de eventos de um agente real. Os
cenários golden medem tempos de poucos ms, então têm precisão menor; use as linhas do serviço para comparação.
