"""Testes do serviço de anonimização (ingestão real, CSPRNG, CLI).
@trace T-LAT @trace T-F-EVICT @trace T-F-ANON @trace T-DP-SENS @trace T-WIPE
"""
import io
import json
import os
import random
import tempfile
import unittest
from contextlib import redirect_stdout

from . import _path  # noqa: F401
from atrator_ref.cli import main
from atrator_ref.rng import SplitMix64
from atrator_ref.servico import COMPENSAVEL, IRREVERSIVEL, Anonimizador, CsprngRng

PARAMS = dict(m=4, d=16, g0=1, g1=4, theta=60, Q=20, I=40, tau=50, W=8, p=39, q=41)


def svc(rng=None, **over):
    cfg = dict(PARAMS)
    cfg.update(over)
    return Anonimizador(rng=rng, **cfg)


def eventos_aleatorios(seed, ciclos, m=4, Q=20):
    r = random.Random(seed)
    return [[(r.randrange(m), 1 + r.randrange(Q),
              IRREVERSIVEL if r.randrange(10) == 0 else COMPENSAVEL)
             for _ in range(r.randrange(3))] for _ in range(ciclos)]


class TestPrivacidadeDoEstado(unittest.TestCase):
    def test_estado_so_tem_somas_e_metadados(self):
        s = svc(rng=SplitMix64(5))
        for ev in eventos_aleatorios(1, 120):
            s.ciclo(ev)
        self.assertEqual(set(s.estado().keys()), {"ciclo", "janelas_no_anel", "coordenadas", "somas"})
        self.assertEqual(len(s.estado()["somas"]), 2 * PARAMS["m"])

    def test_gerador_padrao_nao_guarda_semente(self):
        g = CsprngRng()
        self.assertEqual(g.state, 0)
        self.assertFalse(any("seed" in k for k in vars(g)))

    def test_ids_externos_nao_aparecem_nem_na_saida_da_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = os.path.join(tmp, "e.jsonl")
            estado = os.path.join(tmp, "s.json")
            with open(entrada, "w", encoding="utf-8") as f:
                for t in range(60):
                    f.write(json.dumps({"ciclo": t, "ancora": 0, "valor": 3,
                                        "classe": "compensavel",
                                        "nome": "MARCADOR-SECRETO-%d" % t}) + "\n")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["anonimizar", entrada, "--estado", estado]), 0)
            with open(estado, encoding="utf-8") as f:
                self.assertNotIn("MARCADOR", f.read())


class TestEvicção(unittest.TestCase):
    def test_anel_respeita_W_e_conta_evicoes(self):
        s = svc(rng=SplitMix64(9))
        ciclos = PARAMS["tau"] * (PARAMS["W"] + 5)
        for ev in eventos_aleatorios(2, ciclos):
            s.ciclo(ev)
        self.assertEqual(len(s._anel), PARAMS["W"])
        self.assertEqual(s.janelas_evictadas, s.janelas_seladas - PARAMS["W"])

    def test_selagem_com_evicao_troca_exatamente_uma_janela(self):
        # @trace T-F-DROP : ao selar com anel cheio, o estado muda só pela janela nova menos a mais antiga.
        s = svc(rng=SplitMix64(77))
        for ev in eventos_aleatorios(3, PARAMS["tau"] * PARAMS["W"]):
            s.ciclo(ev)
        antes = [list(w) for w in s._anel]
        soma_antes = [sum(col) for col in zip(*antes)]
        for _ in range(PARAMS["tau"]):
            s.ciclo([])
        depois = s._anel
        self.assertEqual(len(depois), PARAMS["W"])
        self.assertEqual(depois[:-1], antes[1:])
        esperado = [soma_antes[c] - antes[0][c] + depois[-1][c] for c in range(2 * PARAMS["m"])]
        self.assertEqual(s.estado()["somas"], esperado)


class TestLimitesDaEspecificacao(unittest.TestCase):
    def test_teto_I_rejeita_excesso_por_ancora_e_ciclo(self):
        s = svc(rng=SplitMix64(1), I=10)
        s.ciclo([(0, 6, COMPENSAVEL), (0, 6, COMPENSAVEL), (0, 4, COMPENSAVEL)])
        self.assertEqual(s.rejeitados, 1)
        self.assertEqual(s.recebidos, 3)

    def test_cotas_nunca_violadas_em_carga_pesada(self):
        s = svc(rng=SplitMix64(3))
        for ev in eventos_aleatorios(5, 1500):
            s.ciclo(ev)
        r = s.relatorio()
        self.assertEqual(r["violacoes_B"], 0)
        self.assertEqual(r["violacoes_latencia"], 0)
        self.assertLessEqual(r["max_exposicao"], r["limite_B"])
        self.assertLessEqual(r["max_latencia"], r["limite_latencia"])

    def test_bruto_apagado_ao_selar(self):
        s = svc(rng=SplitMix64(2))
        for ev in eventos_aleatorios(6, PARAMS["tau"]):
            s.ciclo(ev)
        pendentes = sum(len(f) for f in s._filas)
        self.assertEqual(s._liquidados, [])
        self.assertEqual(s.relatorio()["brutos_ainda_no_estado"], pendentes)
        self.assertEqual(s.apagados, s.recebidos - s.rejeitados - pendentes)

    def test_entradas_invalidas_sao_recusadas(self):
        s = svc(rng=SplitMix64(1))
        for ev in [(9, 1, COMPENSAVEL), (0, 0, COMPENSAVEL), (0, 21, COMPENSAVEL), (0, 1, "outra")]:
            with self.assertRaises(ValueError):
                s.ciclo([ev])

    def test_parametros_invalidos_sao_recusados(self):
        with self.assertRaises(ValueError):
            svc(p=41, q=41)
        with self.assertRaises(ValueError):
            svc(g0=5, g1=4)


class TestCli(unittest.TestCase):
    def test_demo_depois_anonimizar(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = os.path.join(tmp, "ev.jsonl")
            est = os.path.join(tmp, "est.json")
            rel = os.path.join(tmp, "rel.json")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["demo", ev, "--ciclos", "120", "--semente", "4"]), 0)
                self.assertEqual(main(["anonimizar", ev, "--estado", est, "--relatorio", rel]), 0)
            with open(rel, encoding="utf-8") as f:
                r = json.load(f)
            self.assertEqual(r["violacoes_B"], 0)
            self.assertEqual(r["ciclos"], 120)
            self.assertLessEqual(r["janelas_no_anel"], PARAMS["W"])

    def test_linha_invalida_gera_erro_claro(self):
        with tempfile.TemporaryDirectory() as tmp:
            ev = os.path.join(tmp, "ruim.jsonl")
            with open(ev, "w", encoding="utf-8") as f:
                f.write('{"ancora": 0}\n')
            with self.assertRaises(SystemExit):
                main(["anonimizar", ev, "--estado", os.path.join(tmp, "e.json")])


if __name__ == "__main__":
    unittest.main()
