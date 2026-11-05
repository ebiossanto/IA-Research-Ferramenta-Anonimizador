#!/usr/bin/env bash
# Reproduz tudo o que o ambiente permitir. Pula (avisando) o que não estiver instalado.
# Sai com código != 0 se algum passo EXECUTADO falhar.
set -u
cd "$(dirname "$0")/.."
FAIL=0; SKIP=""
mkdir -p results/py results/rust results/analysis

run() { # run "descrição" comando...
  local desc="$1"; shift
  echo; echo "== $desc =="
  if "$@"; then echo "   -> OK"; else echo "   -> FALHOU"; FAIL=1; fi
}
skip() { echo; echo "== $1 == PULADO ($2)"; SKIP="$SKIP\n - $1 ($2)"; }

run "1/7 rastreabilidade" python3 scripts/trace_check.py
run "2/7 testes Python (oráculo)" bash -c "cd python && python3 -m unittest discover -s tests -t ."
run "3/7 golden Python == golden de referência" bash -c "python3 python/run_golden.py > results/py/scenarios.kv && diff -u results/golden/scenarios.kv results/py/scenarios.kv"

if command -v lake >/dev/null 2>&1; then
  run "4/7 Lean: núcleo" bash -c "cd lean && lake build"
  run "4/7 Lean: extras (vetores)" bash -c "cd lean && lake build AtratorExtras"
else skip "4/7 Lean" "lake não encontrado"; fi

if command -v cargo >/dev/null 2>&1; then
  run "5/7 Rust: testes" bash -c "cd rust && cargo test --release"
  run "6/7 golden Rust == golden Python (byte a byte)" bash -c "cd rust && cargo run --release --quiet --bin experiments > ../results/rust/scenarios.kv && diff -u ../results/golden/scenarios.kv ../results/rust/scenarios.kv"
  run "7/7 desempenho Rust (não determinístico)" bash -c "cd rust && cargo run --release --quiet --bin experiments -- --perf | tee ../results/rust/perf.txt"
else skip "5-7/7 Rust" "cargo não encontrado"; fi

run "medição Python (regenera results/analysis/medicao.md)" bash -c "python3 python/run_analysis.py > results/analysis/medicao.md"

echo; echo "================ RESUMO ================"
if [ -n "$SKIP" ]; then echo -e "Pulados:$SKIP"; fi
if [ "$FAIL" -eq 0 ]; then echo "Todos os passos executados passaram."; else echo "HÁ FALHAS — veja acima."; fi
exit $FAIL
