# Projetos relacionados (contexto para retomar)

## Caracteres mutáveis (`I = T(χ, q, S)`)
Projeto seu sobre **representação computacional dinâmica**: parte da informação não fica armazenada explicitamente nos símbolos, mas na combinação
de uma representação simbólica compacta, uma **regra de transformação T**, **estado** `q` e **sinal externo** `S`. Pergunta central: *quanto da informação
computacional pode ser deslocada da representação explícita para T e S, e qual o limite teórico?* Você pediu investigação crítica (sem assumir originalidade; comparar com teoria da informação, autômatos, complexidade de Kolmogorov/MDL),
escolheu primeiro a formulação em que **T e S são fixos e amortizados sobre uma família de programas**, e um domínio real de software genérico (commits, configs, scripts parecidos) para testar a dependência causal. Continuação conceitual do projeto de primos (STC).

**Ligação com este pacote:** o compactador é uma instância de `T`: `χ` = registro bruto, `q` = anel de janelas, `S` = parâmetros públicos; `T_C = agregar ∘ ruído ∘ evictar`. O que sobra após apagar `χ` é `F(q')`; os teoremas de `docs/03` quantificam o que de `χ` ainda está em `(T, q)`. Ver `docs/00` §4.

## MUTA (MUTA Core 5.2)
Arquitetura proposta de **sandbox/VM para rodar código de agentes de IA**, com **histórico de estados em árvore de Merkle**, **verificação de efeitos colaterais** e painel web (MUTA Lab). Você pediu avaliação crítica (se está bom, aplicações, evolução, caminhos).
Os documentos entregues (manuais, pitch de patente, código) descrevem um sistema completo, mas **o código real fornecido era apenas um mock** (hash fixo, contador aleatório, sem CLI nem lógica de mutação/verificação/rollback).

**Ligação com este pacote:** cada poda de ramo da árvore de estados é um evento de apagamento ⇒ um **registro** no livro-razão de efeitos colaterais; as âncoras são os sistemas externos tocados (endpoints, volumes, caches). O primeiro passo prático **não** é o atrator: é implementar o livro-razão (tipos `Record`, `Class`, âncoras) — o crate Rust já define esses tipos.

## Orçamento de reversibilidade (patente)
Ver `docs/01` e `docs/02`: ideia com anterioridade de terceiros; este pacote segue o ângulo do resíduo/esquecimento.
