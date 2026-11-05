# MutaCore P0

Protótipo da Fronteira Invariante Autogovernada. O controlador não confiável propõe; o sintetizador produz evidência candidata; o verificador decide a validade; o motor seleciona execução ou recuperação; e somente o gateway altera o simulador.

## Comandos

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cargo run -p p0-cli -- run-demo
```

## Garantia-alvo

Sob as hipóteses formais do P0, `Invariant(s0)` e uma execução mediada exclusivamente pelo gateway implicam `Invariant(sn)` para todo estado alcançável.
