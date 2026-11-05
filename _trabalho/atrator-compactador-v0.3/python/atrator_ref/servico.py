"""Serviço de anonimização para uso real: ingestão -> descarga (D) -> selagem com ruído (C) -> evicção.

Diferente de `system.run` (simulador com geração interna e semente fixa), aqui os eventos chegam de fora
e o ruído vem de um CSPRNG (`secrets`). Não há semente no objeto, não há identificadores no estado e o
estado exposto é apenas a soma por coordenada sobre o anel de janelas seladas.

Entrada de um evento: (ancora, valor, classe[, entidade]) com classe "compensavel" ou "irreversivel".
A entidade (ex.: usuário) é opcional; sem ela, os registros formam uma única entidade anônima.
Identificadores externos do registro nunca são lidos.

@trace T-LAT        latência de liquidação <= settle_steps(d,g0,B+I) - 1
@trace T-F-EVICT    o estado do anel não depende de janelas com idade >= W
@trace T-F-ANON     o estado não contém identidade, payload nem semente
@trace T-DP-SENS    um registro altera exatamente uma coordenada do agregado, em <= Q
@trace T-DP-EPS     ruído geométrico bilateral por coordenada => razão e^eps0 = (q/p)^Q
@trace T-WIPE       zeragem (best-effort) do valor bruto antes de descartar
@trace T-CLIP       limite M_e por entidade e janela no selo => ε por entidade = M_e ln(q/p)
"""
import math
import secrets
from collections import deque

from .rng import SplitMix64
from .spec import bound_B, rate, removal, settle_steps

COMPENSAVEL = "compensavel"
IRREVERSIVEL = "irreversivel"
CLASSES = (COMPENSAVEL, IRREVERSIVEL)


class CsprngRng(SplitMix64):
    """Mesmos amostradores exatos da especificação, com bytes do sistema operacional.

    Não há semente: o estado do gerador é inacessível de fora e não entra no estado exposto.
    """

    def __init__(self):
        self.state = 0

    def below(self, n):
        if n < 1:
            raise ValueError("n deve ser >= 1")
        return secrets.randbelow(n)


class _Registro:
    __slots__ = ("ancora", "valor", "classe", "nascimento", "entidade")

    def __init__(self, ancora, valor, classe, nascimento, entidade):
        self.ancora = ancora
        self.valor = valor
        self.classe = classe
        self.nascimento = nascimento
        self.entidade = entidade

    def apagar(self):
        self.ancora = -1
        self.valor = 0
        self.nascimento = -1
        self.entidade = None


class Anonimizador:
    def __init__(self, m, d, g0, g1, theta, Q, I, tau, W, p, q, rng=None, m_e=None):
        _validar(m, d, g0, g1, theta, Q, I, tau, W, p, q, m_e)
        self.m = m
        self.d = d
        self.g0 = g0
        self.g1 = g1
        self.theta = theta
        self.Q = Q
        self.I = I
        self.tau = tau
        self.W = W
        self.p = p
        self.q = q
        self.m_e = m_e
        self.B = bound_B(d, theta, g0, g1, I)
        self.limite_latencia = settle_steps(d, g0, self.B + I) - 1
        self._rng = rng if rng is not None else CsprngRng()
        self._filas = [deque() for _ in range(m)]
        self._u = [0] * m
        self._liquidados = []
        self._anel = []
        self.t = 0
        self.recebidos = 0
        self.rejeitados = 0
        self.irreversiveis = 0
        self.apagados = 0
        self.janelas_seladas = 0
        self.janelas_evictadas = 0
        self.max_exposicao = 0
        self.violacoes_B = 0
        self.max_latencia = 0
        self.violacoes_latencia = 0
        self.recortados = 0
        self.valor_recortado = 0
        self.max_valor_entidade_janela = 0

    def ciclo(self, eventos):
        """Processa um ciclo: valida todos os eventos, admite, descarrega e sela se for a hora.

        A validação é feita antes de qualquer alteração: um lote inválido não deixa efeito parcial.
        """
        m = self.m
        t = self.t
        normalizados = [_normalizar_evento(ev, m, self.Q) for ev in eventos]
        injetado = [0] * m
        for ancora, valor, classe, entidade in normalizados:
            self.recebidos += 1
            if classe == COMPENSAVEL:
                if injetado[ancora] + valor > self.I:
                    self.rejeitados += 1
                    continue
                injetado[ancora] += valor
                self._filas[ancora].append(_Registro(ancora, valor, classe, t, entidade))
                self._u[ancora] += valor
            else:
                self._liquidados.append(_Registro(ancora, valor, classe, t, entidade))
                self.irreversiveis += 1

        for a in range(m):
            v = self._u[a]
            g = rate(self.theta, self.g0, self.g1, v)
            orcamento = removal(self.d, g, v)
            acumulado = 0
            fila = self._filas[a]
            while acumulado < orcamento and fila:
                r = fila.popleft()
                acumulado += r.valor
                self._liquidados.append(r)
                latencia = t - r.nascimento
                if latencia > self.max_latencia:
                    self.max_latencia = latencia
                if latencia > self.limite_latencia:
                    self.violacoes_latencia += 1
            u2 = v - acumulado
            if u2 > self.B:
                self.violacoes_B += 1
            if u2 > self.max_exposicao:
                self.max_exposicao = u2
            self._u[a] = u2

        if (t + 1) % self.tau == 0:
            self._selar(t)
        self.t += 1

    def _recortar(self, registros):
        """Clipping por entidade (T-CLIP): cada entidade contribui no máximo M_e de valor à janela.

        O excedente é apagado e não entra na agregação. Quem fica é decidido pela ordem de chegada.
        """
        acumulado = {}
        aceitos = []
        for r in registros:
            total = acumulado.get(r.entidade, 0)
            if total + r.valor <= self.m_e:
                acumulado[r.entidade] = total + r.valor
                aceitos.append(r)
            else:
                self.recortados += 1
                self.valor_recortado += r.valor
                r.apagar()
        if acumulado:
            self.max_valor_entidade_janela = max(
                self.max_valor_entidade_janela, max(acumulado.values()))
        return aceitos

    def _selar(self, t):
        m = self.m
        registros = self._liquidados
        self._liquidados = []
        n = len(registros)
        if self.m_e is not None:
            registros = self._recortar(registros)
        somas = [0] * (2 * m)
        for r in registros:
            c = r.ancora if r.classe == COMPENSAVEL else m + r.ancora
            somas[c] += r.valor
        for r in registros:
            r.apagar()
        self.apagados += n
        for c in range(2 * m):
            somas[c] += self._rng.two_sided_geometric(self.p, self.q)
        self._anel.append(somas)
        self.janelas_seladas += 1
        while len(self._anel) > self.W:
            self._anel.pop(0)
            self.janelas_evictadas += 1

    def estado(self):
        """Estado preservado: somas ruidosas por coordenada sobre o anel. Sem ids, sem semente."""
        m = self.m
        soma = [0] * (2 * m)
        for somas in self._anel:
            for c in range(2 * m):
                soma[c] += somas[c]
        rotulos = ["%s/ancora%d" % (k, a) for k in CLASSES for a in range(m)]
        return {
            "ciclo": self.t,
            "janelas_no_anel": len(self._anel),
            "coordenadas": rotulos,
            "somas": soma,
        }

    def relatorio(self):
        registros_brutos = sum(len(f) for f in self._filas) + len(self._liquidados)
        return {
            "ciclos": self.t,
            "eventos_recebidos": self.recebidos,
            "rejeitados_por_limite_I": self.rejeitados,
            "irreversiveis": self.irreversiveis,
            "brutos_ainda_no_estado": registros_brutos,
            "exposicao_viva_atual": sum(self._u),
            "max_exposicao": self.max_exposicao,
            "limite_B": self.B,
            "violacoes_B": self.violacoes_B,
            "max_latencia": self.max_latencia,
            "limite_latencia": self.limite_latencia,
            "violacoes_latencia": self.violacoes_latencia,
            "registros_apagados": self.apagados,
            "janelas_seladas": self.janelas_seladas,
            "janelas_evictadas": self.janelas_evictadas,
            "janelas_no_anel": len(self._anel),
            "epsilon_por_registro": round(self.Q * math.log(self.q / self.p), 6),
            "limite_entidade_M_e": self.m_e,
            "registros_recortados": self.recortados,
            "valor_recortado": self.valor_recortado,
            "max_valor_entidade_janela": self.max_valor_entidade_janela,
            "epsilon_por_entidade_por_janela":
                None if self.m_e is None else round(self.m_e * math.log(self.q / self.p), 6),
        }


def _validar(m, d, g0, g1, theta, Q, I, tau, W, p, q, m_e=None):
    if not (isinstance(m, int) and m >= 1):
        raise ValueError("m (número de âncoras) deve ser inteiro >= 1")
    if not (1 <= g0 <= g1 <= d):
        raise ValueError("exige 1 <= g0 <= g1 <= d")
    if not (theta >= 0 and Q >= 1 and I >= 1 and tau >= 1 and W >= 1):
        raise ValueError("exige theta >= 0 e Q, I, tau, W >= 1")
    if not (0 < p < q):
        raise ValueError("ruído exige 0 < p < q")
    if m_e is not None and not (isinstance(m_e, int) and m_e >= 1):
        raise ValueError("limite por entidade M_e deve ser inteiro >= 1 (ou None)")


def _normalizar_evento(evento, m, Q):
    """Valida e devolve (ancora, valor, classe, entidade). Lança ValueError se inválido."""
    if not (isinstance(evento, (tuple, list)) and len(evento) in (3, 4)):
        raise ValueError("evento deve ser (ancora, valor, classe[, entidade]): %r" % (evento,))
    ancora, valor, classe = evento[0], evento[1], evento[2]
    entidade = evento[3] if len(evento) == 4 else None
    if not (isinstance(ancora, int) and 0 <= ancora < m):
        raise ValueError("âncora fora de [0, %d): %r" % (m, ancora))
    if not (isinstance(valor, int) and 1 <= valor <= Q):
        raise ValueError("valor fora de [1, %d]: %r" % (Q, valor))
    if classe not in CLASSES:
        raise ValueError("classe inválida: %r" % (classe,))
    return ancora, valor, classe, entidade
