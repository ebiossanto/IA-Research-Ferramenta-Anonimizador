"""Imprime a saída golden (KV, só inteiros). @trace T-GOLD"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atrator_ref.system import golden_text  # noqa: E402

if __name__ == "__main__":
    sys.stdout.write(golden_text())
