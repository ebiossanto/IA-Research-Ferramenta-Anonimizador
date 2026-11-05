"""Gera o relatório de medição em Markdown (stdout)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atrator_ref.analysis import build_report  # noqa: E402

if __name__ == "__main__":
    sys.stdout.write(build_report())
