"""Implementação de referência (executável) do Atrator Compactador / Anonimizador.

Papel deste pacote: ser o ORÁCULO executável da especificação. Rust (rust/) e Lean (lean/)
são verificados contra ele por vetores de teste e por saídas "golden" byte a byte.
Somente aritmética inteira (sem float) nas partes que entram nos testes golden.
"""
__version__ = "0.2.0"
