#!/usr/bin/env python3
"""Verificador de rastreabilidade (estrutural).  @trace T-GOLD

Varre documentos, Lean, Python (impl. e testes) e Rust (impl. e testes) atrás de etiquetas
`@trace <ID>` e confere contra trace/policy.csv:
  1. toda etiqueta encontrada existe na política (sem etiquetas órfãs);
  2. todo ID da política aparece em TODAS as categorias que ele exige
     (doc, lean, py, rs, tpy, trs);
  3. trace/matrix.csv (gerada) está atualizada. `--write` regrava a matriz.
Isto garante correspondência ESTRUTURAL código <-> matemática; a correspondência SEMÂNTICA vem dos
testes diferenciais (vetores, golden) e, no futuro, de extração verificada (ver docs/06-roadmap.md).
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = re.compile(r"@trace\s+(T-[A-Z0-9][A-Z0-9-]*)")
CATS = [
    ("doc", "docs", (".md",)),
    ("lean", "lean", (".lean",)),
    ("py", os.path.join("python", "atrator_ref"), (".py",)),
    ("rs", os.path.join("rust", "src"), (".rs",)),
    ("tpy", os.path.join("python", "tests"), (".py",)),
    ("trs", os.path.join("rust", "tests"), (".rs",)),
]


def scan():
    found = {}
    for cat, sub, exts in CATS:
        base = os.path.join(ROOT, sub)
        for dp, dns, fns in os.walk(base):
            dns[:] = [d for d in dns if d not in (".lake", "target", "__pycache__", "arquivo")]
            for fn in sorted(fns):
                if not fn.endswith(exts):
                    continue
                path = os.path.join(dp, fn)
                rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
                with open(path, encoding="utf-8") as f:
                    for tid in set(TAG.findall(f.read())):
                        found.setdefault(tid, {}).setdefault(cat, set()).add(rel)
    return found


def load_policy():
    pol = {}
    with open(os.path.join(ROOT, "trace", "policy.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pol[row["id"]] = (row["titulo"], row["exige"].split())
    return pol


def matrix_text(found, pol):
    out = ["id,titulo,doc,lean,python,rust,testes_python,testes_rust"]
    names = ["doc", "lean", "py", "rs", "tpy", "trs"]
    for tid in sorted(pol):
        titulo, _ = pol[tid]
        cols = []
        for c in names:
            files = sorted(found.get(tid, {}).get(c, set()))
            cols.append(";".join(files) if files else "-")
        out.append(",".join([tid, '"%s"' % titulo.replace('"', "'")] + cols))
    return "\n".join(out) + "\n"


def main():
    write = "--write" in sys.argv
    found = scan()
    pol = load_policy()
    errors = []
    for tid in sorted(found):
        if tid not in pol:
            errors.append("etiqueta órfã (não está em policy.csv): %s em %s" % (
                tid, sorted(set(f for c in found[tid].values() for f in c))))
    for tid, (_, exige) in sorted(pol.items()):
        for cat in exige:
            if cat not in found.get(tid, {}):
                errors.append("%s: falta categoria obrigatória '%s'" % (tid, cat))
    text = matrix_text(found, pol)
    mpath = os.path.join(ROOT, "trace", "matrix.csv")
    if write:
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(text)
        print("trace/matrix.csv regravada (%d IDs)" % len(pol))
    else:
        cur = open(mpath, encoding="utf-8").read() if os.path.exists(mpath) else ""
        if cur != text:
            errors.append("trace/matrix.csv desatualizada — rode: python3 scripts/trace_check.py --write")
    if errors:
        print("RASTREABILIDADE: FALHOU")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("RASTREABILIDADE: OK — %d teoremas/itens, todas as categorias exigidas presentes, sem etiquetas órfãs" % len(pol))


if __name__ == "__main__":
    main()
