# Rastreabilidade

* `policy.csv` — **o que cada resultado exige**: categorias `doc lean py rs tpy trs` (documento, Lean, Python impl., Rust impl.,
  testes Python, testes Rust). Editado por humanos.
* `matrix.csv` — **gerada** por `python3 scripts/trace_check.py --write`: em quais arquivos cada ID aparece.
* `vectors.csv` — 525 vetores diferenciais gerados pelo oráculo Python (`scripts/gen_vectors.py`); o Rust os lê
  (`rust/tests/vectors_tests.rs`) e o Lean os verifica (`lean/AtratorExtras/Vectors.lean`, gerado).
* Etiqueta: o texto `@trace` seguido de um ID (padrão `T-…`) em comentários/docstrings. O verificador falha se houver etiqueta
  sem política, ou ID sem alguma categoria exigida, ou matriz desatualizada.

Níveis: L0 doc↔ID · L1 ID↔Lean↔Rust↔testes (automático) · L2 vetores/golden · L3 testes de propriedade ·
L4 extração verificada (roadmap).
