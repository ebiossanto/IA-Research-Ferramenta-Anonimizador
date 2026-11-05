# Atrator Compactador / Anonimizador — pacote v0.3

## Usar o produto (Python, sem dependências)

```bash
cd python
python -m atrator_ref demo eventos.jsonl --ciclos 300
python -m atrator_ref anonimizar eventos.jsonl --estado estado.json --relatorio relatorio.json
```

Entrada (uma linha JSON por evento): `{"ciclo": 0, "ancora": 1, "valor": 7, "classe": "compensavel"}`.
Campos extras (nome, id etc.) são ignorados e nunca entram no estado. O ruído usa `secrets` (CSPRNG) e a
semente não existe no objeto. `estado.json` contém somas ruidosas por coordenada sobre o anel de W janelas,
sem identificadores. Código de saída 1 se alguma cota teórica (B ou latência) for violada.

Testes: `cd python && python -m unittest discover -s tests -t .` (46 testes).

---

# Pacote v0.2 (base de pesquisa)

> **Objetivo:** um sistema que **apaga** a informação bruta e **preserva o "estado"** necessário, com o resíduo de
> exposição *limitado e tendendo a zero* e o vazamento sobre cada registro *limitado por ε* e *exatamente zero depois da evicção*.

**Comece por:** `docs/00-continuidade-v0.2.md` (documento de continuidade) → `STATUS.md` (o que está e o que não está verificado) →
`docs/03-teoria-esquecimento.md` (o tratado matemático).

## Os 5 entregáveis finais pedidos

| # | entregável | onde | estado |
|---|---|---|---|
| 1 | Base matemática formal (Lean 4) | `lean/` + `docs/03` | escrito (22 teoremas, 525 vetores); **não compilado** |
| 2 | Implementação Rust | `rust/` | escrita (std-only, sem `unsafe`); **não compilada** |
| 3 | Rastreabilidade | `trace/`, `scripts/trace_check.py` | 22 itens; verificador **executado: OK** |
| 4 | Medição | `docs/05-medicao.md`, `results/analysis/` | **executada** no oráculo Python; Rust (`--perf`) pronto, sem números |
| 5 | Testes reprodutíveis | `python/tests`, `rust/tests`, `results/golden`, `scripts/reproduce.sh` | Python **34/34 OK**; golden determinístico; Rust/Lean aguardam execução |

## Reproduzir

```bash
bash scripts/reproduce.sh
```

Executa, nesta ordem (pula, avisando, o que não estiver instalado): rastreabilidade → testes Python → golden Python →
`lake build` (Lean) → `cargo test` (Rust) → golden Rust vs. golden Python (`diff`) → medição.

## Aviso de segurança

`SplitMix64` (usado nos testes para reprodutibilidade) **não é criptograficamente seguro**. A garantia ε-DP exige ruído
imprevisível: em produção use CSPRNG e **não** armazene a semente no estado exposto. Detalhes: `docs/03` §7.
Este pacote não é parecer jurídico nem de patenteabilidade.
