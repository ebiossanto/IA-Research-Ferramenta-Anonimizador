# Anterioridade e referências (consolidado)

> Pesquisas feitas por busca na web em 24–25/set e 15–17/out/2026. **Não** são busca profissional em base de patentes e
> **não** são parecer jurídico. A bibliografia completa, com status de verificação, está em `references/bibliografia.md`.

## A. Orçamento de reversibilidade/irreversibilidade para agentes (NÃO é novo)

* **The Controllability Trap: A Governance Framework for Military AI Agents** — arXiv:2603.03515. Define um *Irreversibility Budget*: score de irreversibilidade por ação, soma cumulativa, pausa e reautorização humana ao exceder o limite.
* **The Irreversibility Budget: Fleet-Level Risk Accounting and Admission Control for Agent Operating Systems** (MPI-SWS) — arXiv:2609.00275. Estende a frotas; o runtime "cobra" o risco residual antes de cada efeito.
* **revoco** (github.com/rsh1k/revoco; PyPI) — implementação aberta com classe `IrreversibilityBudget`; taxonomia reversível/compensável/irreversível; reposição **manual por desenho**.
* **irredux** (PyPI) — pacote correlato com a mesma taxonomia de três vias.

**Consequência:** o núcleo "contar irreversibilidade, comparar a um teto, pausar" tem anterioridade de terceiros. Este pacote **não** o reivindica; usa só a taxonomia (reversível/compensável/irreversível) como vocabulário.

## B. Privacidade diferencial e ruído geométrico (NÃO é novo)

* Dwork–McSherry–Nissim–Smith, *Calibrating Noise to Sensitivity in Private Data Analysis* (TCC 2006; reimpressão J. Privacy and Confidentiality, 2016) — definição de ε-DP e sensibilidade.
* Ghosh–Roughgarden–Sundararajan, *Universally Utility-Maximizing Privacy Mechanisms* (STOC 2009; SIAM J. Comput. 2012; arXiv:0811.2841) — o **mecanismo geométrico** é ótimo para contagens.
* Mironov, *On Significance of the Least Significant Bits for Differential Privacy* (ACM CCS 2012) — ataques a DP em ponto flutuante ⇒ usamos inteiros.
* **Pan-privacy:** Dwork–Naor–Pitassi–Rothblum–Yekhanin, *Pan-Private Streaming Algorithms* (ICS 2010) — privacidade mesmo se o estado interno for observado (intrusão única); impossibilidade para duas intrusões não anunciadas em estimação de densidade (estado finito).
* **Formalização de DP em assistente de prova com aritmética finita:** *Verified Differential Privacy for Finite Computers* (CoqPL 2023) — mecanismo geométrico truncado verificado em Coq. **Isto é anterioridade para a ideia de formalizar o mecanismo geométrico em prova**; nossa formalização em Lean cobre o núcleo combinatório e não é pioneira.

## C. Unlearning e SISA (NÃO é novo)

* Bourtoule et al., *Machine Unlearning* (IEEE S&P 2021; arXiv:1912.03817) — **SISA** (shards/slices/agregação).
* *Revisiting the Past: Data Unlearning with Model State History* (arXiv:2506.20941) — usa o histórico de estados do modelo.
* Levantamentos: *Machine Unlearning: Solutions and Challenges* (arXiv:2308.07061); *An Introduction to Machine Unlearning* (arXiv:2209.00939).
* Remoção aproximada/certificada: Ginart et al. (2019), Guo et al. (2020), Sekhari et al. (2021) *(citados de memória — verificar)*.

## D. Controle, compensação e verificação

* ISS: Sontag (1989); Sontag–Wang (1995) *(de memória — verificar)*. Nenhuma fonte encontrada aplica ISS à gestão de resíduo de efeitos colaterais de agentes — isto é **aplicação**, não matemática nova.
* Saga / transações compensatórias: Garcia-Molina & Salem (1987) — compensação **imediata** por falha, não por acúmulo/limiar.
* Verificação de Rust: Ho & Protzenko, *Aeneas: Rust Verification by Functional Translation* (ICFP 2022) — tradução de Rust seguro para Lean/Coq/F*/HOL4 (rota L4).
* Remanência: Gutmann (1996); Halderman et al. (2008) *(de memória — verificar)*.

## E. O que sobra como possível combinação (hipótese a verificar por profissional)

(a) duas contrações acopladas (exposição ISS + resíduo de informação com evicção) num mesmo ciclo de vida de registros;
(b) cota de latência `N(B+I)−1` e linha do tempo bruto → ε0 → 0 em ciclos;
(c) **orçamento de esquecimento restituído por evicção** (ε0 gasto uma vez, devolvido ao evictar);
(d) formalização conjunta em Lean + oráculo + Rust + rastreabilidade;
(e) contexto de aplicação: sandbox de agentes com histórico em árvore de estados.
Riscos de anterioridade ainda **não** checados: sliding-window/continual-observation DP (exponential histograms), compactação de logs/event sourcing com agregação ruidosa, *retention policies* com DP em sistemas de telemetria.

## F. Cuidados

* **Publicar** (GitHub, arXiv) antes de decidir sobre patente pode prejudicar a patenteabilidade; períodos de graça variam por país. Consulte um profissional **antes**.
* Patentes de método matemático puro costumam ser difíceis; o que se protege, quando se protege, é uma implementação/aplicação técnica concreta.
