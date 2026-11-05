# Atrator Compactador de Resíduo Ambiental

**Documento de continuidade — v0.1**
**Data:** 25 de setembro de 2026
**Escopo:** mecanismo de gestão de resíduo ambiental para sandboxes de agentes de IA (aplicação direta: MUTA Core), desacoplado do orçamento de segurança/irreversibilidade.
**Natureza deste documento:** notas técnicas para continuar o desenvolvimento. Não é parecer jurídico nem substitui uma busca profissional de anterioridade em base de patentes.

---

## Resumo

A ideia original — um "orçamento de reversibilidade" que acumula um score de irreversibilidade por ação de um agente de IA e força reautorização humana ao estourar um limite — já está publicada por terceiros (§1). O que **não** está publicado é um mecanismo *ativo* que reduza automaticamente o resíduo deixado no ambiente por ações já apagadas/podadas do histórico de um agente. Este documento formaliza esse mecanismo — o **atrator compactador** — como um par de operadores (descarga por limiar + compactação por granulação grossa) com uma garantia de limite provada (Estabilidade Entrada-Estado), desenhado para a arquitetura do MUTA Core.

---

## 1. Por que este ângulo, e não o orçamento de reversibilidade

A busca de anterioridade (24–25/set/2026) mostrou que o núcleo conceitual do "orçamento de reversibilidade" já está publicado de forma muito próxima:

- **"The Controllability Trap"** (governança de agentes de IA militares, arXiv 2603.03515) define formalmente um *Irreversibility Budget*: score ι(a) ∈ [0,1] por ação, soma cumulativa I_C(t) = Σ ι(a_j), pausa e reautorização humana quando I_C(t) ≥ I_B.
- **"The Irreversibility Budget: Fleet-Level Risk Accounting and Admission Control for Agent Operating Systems"** (Max Planck Institute for Software Systems, arXiv 2609.00275) estende isso a frotas de agentes, tratando irreversibilidade como recurso de primeira classe cobrado por um runtime antes de cada efeito.
- **revoco** (github.com/rsh1k/revoco, também no PyPI) é implementação real e aberta, com classe `IrreversibilityBudget`, taxonomia **reversível / compensável / irreversível** por ação resolvida, e reposição do orçamento **manual por decisão deliberada** dos autores — para manter um humano no laço de decisão.
- **irredux** (PyPI) é um pacote correlato, mesma taxonomia de três vias, mesmo framing de "orçamento" para tráfego de agentes.

**Conclusão:** o núcleo (contar irreversibilidade, comparar a um teto, pausar) não é patenteável para este caso — é anterioridade de terceiros. Insistir nele é gastar esforço numa porta já fechada.

**O que sobra em aberto:** nenhuma das fontes acima descreve um mecanismo que reduza o resíduo automaticamente. O revoco, pelo contrário, torna a reposição manual *de propósito*, para não enfraquecer o objetivo de segurança de manter um humano no controle. Isso aponta o ângulo certo: **não automatizar o perdão do orçamento de segurança** (essa tentativa esbarraria na mesma objeção que os próprios autores já anteciparam). Mas existe uma grandeza distinta, que nenhuma fonte trata: o resíduo que sobra no ambiente depois que uma ação foi computada e um ramo do histórico do agente foi podado — arquivos escritos, chamadas de rede já feitas, entradas de cache, nós órfãos numa árvore de estados. Gerir *essa* grandeza é faxina, não perdão de risco — e não compete com a segurança.

---

## 2. Duas noções de "entropia" — e por que a distinção importa

A intuição original ("apagar informação deixa resíduo que aumenta a entropia") tem base física real via **Princípio de Landauer**: apagar um bit dissipa no mínimo k_BT ln2 de calor. Isso é genuíno, mas em temperatura ambiente equivale a ≈3×10⁻²¹ J/bit — irrelevante para qualquer decisão de engenharia num data center. Um documento técnico sério não pode se apoiar nisso como grandeza prática.

O que Landauer garante, e que vale manter como motivação, é o **argumento de inevitabilidade**: nenhum apagamento lógico é "limpo" sem custo em algum lugar; ele sempre transfere informação/correlação para fora do sistema que a apagou (isso resolve também o paradoxo do Demônio de Maxwell — Bennett, 1982). É esse argumento, não os joules, que justifica por que resíduo ambiental é estruturalmente inevitável, não um bug corrigível por engenharia melhor.

A grandeza prática a ser gerida é outra: **entropia estrutural/informacional** no substrato de armazenamento e na superfície de observabilidade — nós órfãos num content-addressed store (CAS), efeitos colaterais de ramos podados sem contrapartida de compensação, entradas de log/auditoria que crescem sem limite. É sobre isso que o mecanismo abaixo atua.

---

## 3. Modelo formal

### 3.1 Substrato

Seja H = (N, E) o grafo de histórico do agente (Merkle-DAG do MUTA): nós N são snapshots endereçados por conteúdo, arestas E são passos de mutação. Cada nó n carrega:

- um conjunto de efeitos colaterais SE(n) (chamadas externas feitas durante aquele passo);
- uma classe de reversibilidade por efeito — **reversível / compensável / irreversível** (taxonomia emprestada do revoco/irredux, com crédito explícito — já é o vocabulário estabelecido nesta área);
- refcount(n): quantos ramos vivos ou ponteiros externos ainda referenciam n.

Definem-se dois campos de resíduo distintos:

- **ρ_interno(n)** — lixo dentro do CAS: nós sem referência, blobs órfãos, locks obsoletos. É *coleta de lixo clássica* (mark-sweep, mark-compact, geracional) — bem entendida, não é o ponto original deste documento.
- **ρ_externo(j)** — resíduo por âncora externa j (um endpoint de API, um domínio de dados, um sistema a jusante): soma dos efeitos colaterais compensáveis ainda não revertidos, vindos de nós já podados que tocaram aquela âncora. **Este é o alvo novo**: GC clássico não alcança fora da fronteira do processo.

### 3.2 Operadores

**D — Descarga por limiar (criticalidade auto-organizada).** Cada âncora j acumula ρ_externo(j). Ao ultrapassar um limiar ρc(j) — calibrável pela sensibilidade da âncora a chamadas repetidas / rate limits do sistema a jusante — dispara-se um lote de ações de compensação (a "avalanche"): não uma compensação por evento (caro, e sujeito a rate limit), mas um lote batched, no espírito do sandpile de Bak-Tang-Wiesenfeld com dissipação de volume γ(j) > 0 — a fração de exposição efetivamente revertida por ciclo de descarga. A variante **não conservativa** do sandpile é essencial aqui: dissipação real é o que garante convergência, não apenas criticalidade.

**C — Compactação por granulação grossa.** A cada janela τ, entradas do log de efeitos colaterais já reconciliadas (ρ_externo revertido) ou decaídas além de uma "meia-vida de auditoria" são fundidas em estatística-resumo (contagem, exposição total, janela temporal) em vez de mantidas linha a linha — evitando crescimento ilimitado do log sem apagar o rastro exigível por auditoria (ver §5 sobre a tensão com retenção regulatória).

### 3.3 Garantia formal — por que é ISS, não Banach

Como há apagamento contínuo (o agente nunca para de podar ramos), o resíduo **não** converge a zero por um ponto fixo de contração pura — converge a um **limite dependente da taxa de entrada**, que é a definição de **Estabilidade Entrada-Estado** (ISS, Sontag 1989), paradigma dominante em controle não linear para sistemas com perturbação persistente (validado em robótica, sistemas de potência, biologia de sistemas — mas, pelo que a busca encontrou, **não aplicado à gestão de resíduo de efeitos colaterais de agentes de IA**; essa aplicação parece ser o ponto genuinamente original aqui).

Seja U(t) a exposição total não reconciliada (soma ponderada por risco de ρ_externo sobre todas as âncoras). Por ciclo de descarga de duração τ:

```
U(t+τ) ≤ (1−γ)·U(t) + I(t, t+τ)
```

onde I(t,t+τ) é o resíduo novo injetado no intervalo (efeitos colaterais compensáveis de ramos recém-podados) e γ = min_j γ(j) é a taxa de reconciliação garantida no pior caso. Isso dá o limite ISS padrão:

```
U(t) ≤ (1−γ)^(t/τ)·U(0) + I_max/γ
```

**Consequência importante e honesta:** o resíduo *compensável* fica limitado e decai geometricamente na ausência de nova injeção — mas nunca converge a zero de verdade enquanto o agente segue operando, e a fração **irreversível** (sem ação de compensação possível — ex.: informação já vazada) não é tocada pelo atrator: ela deve ser **exposta como piso residual auditável**, não escondida por compactação. Isso estende a taxonomia estática do revoco/irredux dando-lhe **dinâmica com limite provado**, em vez de apenas uma etiqueta por evento.

---

## 4. Arquitetura proposta para o MUTA

1. **Livro-razão de efeitos colaterais** — estende a verificação de efeitos colaterais já prevista no MUTA: cada efeito registrado com âncora, classe de reversibilidade, referência à ação de compensação (se compensável), timestamp, nó do Merkle-DAG.
2. **Campo de resíduo** — acumulador ρ_externo por âncora.
3. **Motor de descarga** — processo de fundo; limiar ρc por âncora; dispara lote de compensações; mede γ empiricamente por âncora.
4. **Motor de compactação** — rollup periódico do livro-razão já reconciliado/decaído.
5. **Painel (MUTA Lab)** — expõe U(t) por âncora, o piso irreversível, e atividade de descarga/compactação — extensão natural do painel de monitoramento já previsto no MUTA.

*Nota de honestidade sobre o MUTA*: o código do MUTA avaliado anteriormente era um mock (hash fixo, contador aleatório, sem CLI nem lógica de mutação/verificação/rollback implementada). Esta arquitetura é uma proposta de design sobre uma base que ainda não existe em funcionamento — o primeiro passo prático não é "adicionar o atrator", é ter o livro-razão de efeitos colaterais (item 1) implementado de verdade.

---

## 5. Riscos de anterioridade ainda a verificar

Esta busca foi rápida (web, não base de patentes profissional). Áreas com risco de anterioridade mais próxima, a checar antes de qualquer depósito:

- **Saga pattern / compensating transactions** (Garcia-Molina & Salem, 1987; onipresente em microsserviços) — cobre "efeito com compensação", mas dispara a compensação **imediatamente** na falha, não por acumulação/limiar. A diferença (acúmulo + limiar + lote + limite ISS provado) parece genuína, mas um examinador vai comparar com isto primeiro.
- **Circuit breakers / bulkheads** — padrão de limiar, mas para *bloquear* chamadas, não para *reverter* débito acumulado.
- **Coleta de lixo geracional / tracing GC** — cobre ρ_interno, não ρ_externo; útil citar para diferenciar escopo explicitamente numa eventual reivindicação.
- **Reconciliação em event sourcing / CDC (change data capture)** — jobs de reconciliação em lote já existem; verificar se algum já usa acumulador com limiar tipo sandpile em vez de agendamento fixo.

---

## 6. Esqueleto de reivindicação (rascunho técnico, não linguagem jurídica final)

> Método para gerenciar resíduo de efeitos colaterais de agentes de IA em um ambiente de sandbox, compreendendo: registrar efeitos colaterais associados a nós podados de um histórico de estados como incrementos localizados a um campo de resíduo por âncora externa; disparar, mediante um limiar local, um lote de ações de compensação que dissipam uma fração do resíduo local a uma âncora verdadeira; fundir periodicamente entradas de resíduo já reconciliado em representação estatística compacta; caracterizado por a composição dos dois mecanismos manter a exposição total limitada por uma função da taxa de apagamento (propriedade de estabilidade entrada-estado), com convergência ao repouso apenas na ausência de novas operações, e por expor separadamente a fração de resíduo irreversível como piso auditável não sujeito à compactação.

---

## 7. Questões em aberto

- Calibração empírica de γ(j) por tipo de âncora — precisa de dados reais de operação, não só teoria.
- Resíduos correlacionados: se vários ramos podados tocaram a mesma âncora com o mesmo efeito, o acúmulo ingênuo superconta — o paper de fleet-level já aponta esse problema em outro contexto (perdas correlacionadas entre agentes).
- **Tensão regulatória**: compactar/resumir o log pode conflitar com exigências de retenção auditável (SR 11-7, AI Act) que a própria literatura de reversibilidade cita como motivação. A compactação proposta preserva resumo estatístico, não o registro linha a linha — pode não bastar para todo regime regulatório. Precisa de opinião jurídica real, não desta análise.
- Vale simular o par D/C num histórico de MUTA sintético antes de qualquer implementação real, para validar γ e ρc empiricamente em vez de assumidos.

---

## 8. Referências (busca de 25/set/2026)

- The Controllability Trap: A Governance Framework for Military AI Agents — arXiv:2603.03515
- The Irreversibility Budget: Fleet-Level Risk Accounting and Admission Control for Agent Operating Systems — arXiv:2609.00275
- revoco — github.com/rsh1k/revoco
- irredux — pypi.org/project/irredux
- Bak, P., Tang, C., Wiesenfeld, K. (1987) — sandpile e criticalidade auto-organizada
- Sontag, E. (1989) — Input-to-State Stability
- Landauer, R. (1961); Bennett, C. (1982) — princípio de Landauer e resolução do Demônio de Maxwell
- Garcia-Molina, H., Salem, K. (1987) — Sagas
