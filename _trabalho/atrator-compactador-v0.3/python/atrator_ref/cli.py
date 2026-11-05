"""Linha de comando do Atrator Compactador / Anonimizador.

Comandos:
  demo        gera um arquivo de eventos sintéticos (JSON Lines) para experimentar
  anonimizar  lê eventos, anonimiza e grava o estado preservado + relatório

Formato de cada linha de entrada (JSON Lines):
  {"ciclo": 0, "ancora": 1, "valor": 7, "classe": "compensavel"}
Campos extras (ex.: id, nome, e-mail) são ignorados e nunca entram no estado.
"""
import argparse
import json
import random
import sys

from .servico import CLASSES, COMPENSAVEL, IRREVERSIVEL, Anonimizador

PADROES = dict(m=4, d=16, g0=1, g1=4, theta=60, Q=20, I=40, tau=50, W=8, p=39, q=41)


def _adicionar_parametros(parser):
    g = parser.add_argument_group("parâmetros (padrão = cenário steady da especificação)")
    g.add_argument("--ancoras", type=int, default=PADROES["m"], dest="m", help="nº de âncoras (m)")
    g.add_argument("--d", type=int, default=PADROES["d"], help="denominador da descarga")
    g.add_argument("--g0", type=int, default=PADROES["g0"], help="descarga de fundo")
    g.add_argument("--g1", type=int, default=PADROES["g1"], help="descarga de reforço (acima de theta)")
    g.add_argument("--theta", type=int, default=PADROES["theta"], help="limiar de reforço")
    g.add_argument("--Q", type=int, default=PADROES["Q"], help="valor máximo de um registro (sensibilidade)")
    g.add_argument("--I", type=int, default=PADROES["I"], help="teto de injeção por âncora e ciclo")
    g.add_argument("--tau", type=int, default=PADROES["tau"], help="ciclos por janela")
    g.add_argument("--W", type=int, default=PADROES["W"], help="janelas seladas mantidas no anel")
    g.add_argument("--p", type=int, default=PADROES["p"], help="ruído: numerador de p/q (0 < p < q)")
    g.add_argument("--q", type=int, default=PADROES["q"], help="ruído: denominador de p/q")


def _ler_eventos(caminho):
    grupos = {}
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, 1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                obj = json.loads(linha)
                ciclo = obj["ciclo"]
                evento = (obj["ancora"], obj["valor"], obj.get("classe", COMPENSAVEL))
            except (ValueError, KeyError, TypeError) as e:
                raise SystemExit("linha %d inválida (%s): %s" % (n, e, linha[:80]))
            if not (isinstance(ciclo, int) and ciclo >= 0):
                raise SystemExit("linha %d: 'ciclo' deve ser inteiro >= 0" % n)
            grupos.setdefault(ciclo, []).append(evento)
    return grupos


def _anonimizar(args):
    grupos = _ler_eventos(args.entrada)
    fim = max(grupos) + 1 if grupos else 0
    if args.ciclos is not None:
        fim = max(fim, args.ciclos)
    svc = Anonimizador(args.m, args.d, args.g0, args.g1, args.theta, args.Q,
                       args.I, args.tau, args.W, args.p, args.q)
    for t in range(fim):
        try:
            svc.ciclo(grupos.get(t, []))
        except ValueError as e:
            raise SystemExit("ciclo %d: %s" % (t, e))

    estado = svc.estado()
    rel = svc.relatorio()
    with open(args.estado, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if args.relatorio:
        with open(args.relatorio, "w", encoding="utf-8") as f:
            json.dump(rel, f, ensure_ascii=False, indent=2)
            f.write("\n")

    print("Ciclos processados ........ %d" % rel["ciclos"])
    print("Eventos recebidos ......... %d" % rel["eventos_recebidos"])
    print("Rejeitados (teto I) ....... %d" % rel["rejeitados_por_limite_I"])
    print("Registros brutos apagados . %d" % rel["registros_apagados"])
    print("Brutos ainda no estado .... %d" % rel["brutos_ainda_no_estado"])
    print("Janelas seladas / evictadas %d / %d" % (rel["janelas_seladas"], rel["janelas_evictadas"]))
    print("Exposição máx / limite B .. %d / %d" % (rel["max_exposicao"], rel["limite_B"]))
    print("Latência máx / limite ..... %d / %d" % (rel["max_latencia"], rel["limite_latencia"]))
    print("epsilon por registro ...... %s" % rel["epsilon_por_registro"])
    print("Estado gravado em ......... %s" % args.estado)

    violacoes = rel["violacoes_B"] + rel["violacoes_latencia"]
    if violacoes:
        print("ATENÇÃO: %d violação(ões) das cotas teóricas" % violacoes, file=sys.stderr)
        return 1
    return 0


def _demo(args):
    rng = random.Random(args.semente)
    with open(args.saida, "w", encoding="utf-8") as f:
        total = 0
        for t in range(args.ciclos):
            for ancora in range(args.m):
                for _ in range(rng.randrange(3)):
                    classe = IRREVERSIVEL if rng.randrange(10) == 0 else COMPENSAVEL
                    linha = {"ciclo": t, "ancora": ancora, "valor": 1 + rng.randrange(args.Q),
                             "classe": classe, "id": "cliente-%06d" % total}
                    f.write(json.dumps(linha, ensure_ascii=False) + "\n")
                    total += 1
    print("Gravados %d eventos sintéticos em %s" % (total, args.saida))
    return 0


def construir_parser():
    parser = argparse.ArgumentParser(prog="atrator", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="comando", required=True)

    pa = sub.add_parser("anonimizar", help="anonimiza um arquivo de eventos")
    pa.add_argument("entrada", help="arquivo JSON Lines de eventos")
    pa.add_argument("--estado", required=True, help="arquivo JSON de saída com o estado preservado")
    pa.add_argument("--relatorio", help="arquivo JSON de saída com o relatório")
    pa.add_argument("--ciclos", type=int, help="processa pelo menos este nº de ciclos (ciclos vazios)")
    _adicionar_parametros(pa)
    pa.set_defaults(func=_anonimizar)

    pd = sub.add_parser("demo", help="gera eventos sintéticos para experimentar")
    pd.add_argument("saida", help="arquivo JSON Lines a gravar")
    pd.add_argument("--ciclos", type=int, default=200)
    pd.add_argument("--semente", type=int, default=1, help="semente só para reproduzir a DEMO")
    _adicionar_parametros(pd)
    pd.set_defaults(func=_demo)
    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)
    return args.func(args)
