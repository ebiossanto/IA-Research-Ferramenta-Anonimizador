# Histórico e decisões do desenvolvimento

## Linha do tempo

| data | o que aconteceu |
|---|---|
| 24/set/2026 | Você pediu uma ideia original baseada em matemática para desenvolver e patentear; escolheu começar por **busca de anterioridade** (não pelo modelo formal) da ideia "orçamento de reversibilidade" para agentes de IA. |
| 25/set | Premissa sua: em um sistema complexo, a informação apagada deixa **resíduos** que se acumulam e fomentam a entropia; pediu um "atrator compactador" que os leve a zero. 1.ª proposta: Landauer (motivação) + descarga por limiar tipo *sandpile* + compactação por granulação grossa (renormalização), convergência por ponto fixo de Banach. **Corrigida na mesma etapa** para Estabilidade Entrada-Estado (ISS): com apagamento contínuo o resíduo não vai a zero por contração pura, fica limitado por uma função da taxa de entrada. |
| 25/set | **Busca de anterioridade:** o orçamento de irreversibilidade para agentes já está publicado (arXiv 2603.03515; arXiv 2609.00275) e implementado (revoco, irredux; reposição *manual* de propósito). O **ângulo próprio** passou a ser o *resíduo ambiental* (limpeza), separado do orçamento de segurança. Doc de continuidade **v0.1**. |
| 26/set | Você confirmou seguir com o resíduo ambiental aplicado à sandbox de agentes (MUTA) e pediu o documento detalhado. |
| 15/out | Você ligou o tema a "informações residuais de estado legíveis depois que o original é apagado" e declarou a intenção: **provar que dá para anonimizar (apagar) e ainda manter o estado, sem os dados originais**. Fundamentação encontrada: privacidade diferencial, pan-privacy, unlearning, SISA, "Data Unlearning with Model State History"; ligação com `I = T(χ,q,S)` (caracteres mutáveis). |
| 16/out | Objetivo definido: o atrator compactador **é um anonimizador**. Exigências finais: Lean 4, Rust, rastreabilidade, medição, testes reprodutíveis; pacote `.zip`; doc de continuidade atualizado; **prova de quanto resíduo se esquece, em termos de ε**. |
| 16–17/out | Construção do pacote: tratado (`docs/03`), oráculo Python executado (34 testes), Rust e Lean escritos (não compilados), rastreabilidade, medição, este documento. |

## Decisões e por quê

1. **Separar segurança de limpeza.** O orçamento de irreversibilidade é um teto com reposição humana *por desenho*; perdoar débito automaticamente enfraqueceria o propósito. A limpeza do resíduo não compete com ele.
2. **ISS em vez de Banach.** Com injeção contínua, o resíduo converge a um limite que depende da taxa de entrada. ISS é o formalismo certo.
3. **Duas camadas de descarga.** A recursão da v0.1 com descarga condicionada a limiar estava errada para sub-limiar; fundo `g0 > 0` + reforço `g1` acima de `θ` conserta e dá a cota `B*`.
4. **Aritmética inteira.** Evita a classe de vulnerabilidades de DP em ponto flutuante (Mironov 2012) e dá igualdade byte a byte entre Python, Rust e Lean.
5. **Evicção em vez de decaimento exponencial.** Em inteiros, o arredondamento deixa uma diferença de 1 unidade entre históricos vizinhos indefinidamente (ex.: `⌊λx⌋` e `⌊λ(x−1)⌋` podem diferir por 1 para sempre quando há entrada contínua); a evicção dá vazamento **exatamente 0** e `retained_congr` é fácil de provar.
6. **Mecanismo geométrico bilateral amostrado por `G₁ − G₂`.** Exato com inteiros e rejeição sem viés; razão de massas `(q/p)^Q` provada em naturais (`geo_ratio`).
7. **Lean "core" sem Mathlib para o núcleo.** Roda offline e isola o risco; a probabilidade real fica para uma segunda fase com Mathlib.
8. **Oráculo executável em Python.** Era a única linguagem disponível no ambiente; passou a ser o oráculo dos vetores e dos golden contra os quais Rust e Lean são verificados.
9. **Rust no subconjunto seguro** (sem `unsafe`, sem mutabilidade interior): deixa aberta a rota Aeneas/Charon → Lean.
10. **Cota de latência apertada `N(B+I)−1`** (iteração da função monótona `f`) em vez de `B+I`.

## Caminhos descartados (e por quê)

* Patentear o "orçamento de reversibilidade" em si → anterioridade forte e recente.
* Decaimento exponencial do estado como mecanismo de esquecimento → piso de quantização (decisão 5).
* Declarar "Landauer" como a grandeza prática → ≈3×10⁻²¹ J/bit é irrelevante em engenharia; fica como motivação.
* Afirmar que a compactação "preserva a auditoria" → agregados ruidosos não são auditoria fiel.

## Lições do processo

* Cada pesquisa de anterioridade foi **rápida (web)**; nenhuma substitui busca profissional.
* Duas correções importantes vieram de revisão: (a) Banach → ISS; (b) recursão com limiar. Registrá-las evita regressão.
* Vários itens deste pacote foram escritos sem poder compilar Lean/Rust: o `STATUS.md` existe para impedir que isso vire "verificado" por esquecimento.
