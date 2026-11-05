"""Sistema completo: injeção -> descarga (D) -> selagem/compactação (C) -> evicção.

Ciclo de vida de um registro:  vivo (fila FIFO por âncora)  ->  liquidado  ->  anonimizado
(bruto apagado, só resta agregado com ruído)  ->  evictado (nenhum vestígio no estado).

@trace T-LAT        latência de liquidação <= settle_steps(d,g0,B+I) - 1
@trace T-F-EVICT    o estado do anel não depende de janelas com idade >= W
@trace T-F-DROP     descartar uma janela torna o estado independente do seu conteúdo
@trace T-F-ANON     o agregado ignora identidade/payload (erasure estrutural, 0 bits)
@trace T-DP-SENS    um registro altera exatamente uma coordenada do agregado, em <= Q
@trace T-DP-EPS     ruído geométrico bilateral por coordenada => razão e^eps0 = (q/p)^Q
@trace T-WIPE       zeragem (best-effort) do payload bruto antes de descartar
@trace T-TIMELINE   linha do tempo: bruto <= L + tau ; zero residual <= L + tau + W*tau
@trace T-GOLD       saída golden idêntica em Python e Rust
"""
from collections import deque

from .rng import SplitMix64, derive_seed, fnv1a64_ints
from .spec import removal, rate, bound_B, settle_steps

COMP = 0   # compensável (entra na fila viva, é liquidado por D)
IRR = 1    # irreversível (piso: nada a compensar; vai direto a "liquidado")
TAG_NOISE = 0x4E4F495345  # "NOISE"


class Record:
    __slots__ = ("id", "anchor", "q", "klass", "born", "payload")

    def __init__(self, rid, anchor, q, klass, born):
        self.id = rid
        self.anchor = anchor
        self.q = q
        self.klass = klass
        self.born = born
        self.payload = bytearray(rid.to_bytes(8, "little"))


def wipe(rec):
    """Zera o payload bruto. Retorna nº de bytes apagados. (@trace T-WIPE)"""
    n = len(rec.payload)
    for i in range(n):
        rec.payload[i] = 0
    return n


class Compactor:
    """Anel de W janelas seladas. Só guarda agregados (com ruído); nunca guarda registros."""

    def __init__(self, m, W, noise):
        self.m = m
        self.W = W
        self.noise = noise          # None (modo exato) ou (p, q) com 0 < p < q
        self.windows = []           # [(indice, [int]*2m)], mais antigo primeiro

    def seal(self, window_index, records, master_seed, now):
        m = self.m
        sums = [0] * (2 * m)
        max_age = 0
        for r in records:
            c = r.anchor if r.klass == COMP else m + r.anchor
            sums[c] += r.q
            if now - r.born > max_age:
                max_age = now - r.born
        erased_records = len(records)
        erased_bytes = 0
        for r in records:
            erased_bytes += wipe(r)
        true_sums = list(sums)
        if self.noise is not None:
            p, q = self.noise
            rng = SplitMix64(derive_seed(master_seed, TAG_NOISE, window_index))
            for c in range(2 * m):
                sums[c] += rng.two_sided_geometric(p, q)
        self.windows.append((window_index, sums))
        evicted = 0
        while len(self.windows) > self.W:
            self.windows.pop(0)
            evicted += 1
        return {"true_sums": true_sums, "erased_records": erased_records,
                "erased_bytes": erased_bytes, "evicted": evicted, "max_age": max_age}

    def drop_window(self, window_index):
        """Esquecimento exato por pedido (análogo a descartar um shard no SISA)."""
        for i, (idx, _) in enumerate(self.windows):
            if idx == window_index:
                del self.windows[i]
                return True
        return False

    def state(self):
        """Estado preservado: soma por coordenada sobre o anel."""
        out = [0] * (2 * self.m)
        for _, s in self.windows:
            for c in range(2 * self.m):
                out[c] += s[c]
        return out


KEYS = [
    "cycles", "records_generated", "records_dropped_by_cap", "records_injected",
    "records_compensable", "records_irreversible", "exposure_injected", "exposure_settled",
    "discharge_events", "boosted_events", "max_exposure", "bound_B", "bound_violations",
    "contract_violations", "max_settle_latency", "latency_bound", "latency_violations",
    "windows_sealed", "windows_evicted", "ring_len_final", "records_erased", "bytes_erased",
    "ledger_peak_records", "ledger_final_records", "live_final_exposure", "retained_state_ints",
    "abs_error_sum", "true_abs_sum", "rel_error_permille", "state_checksum",
    "first_zero_after_stop", "exposure_at_stop", "max_raw_age_at_erase", "raw_age_bound",
]

SCENARIOS = [
    dict(name="steady", kind="steady", m=4, d=16, g0=1, g1=4, theta=60, Q=20, I=40,
         tau=50, W=8, noise=(39, 41), cycles=2000, stop_at=0, seed=20261015),
    dict(name="burst", kind="burst", m=3, d=32, g0=2, g1=16, theta=150, Q=25, I=80,
         tau=40, W=6, noise=(39, 41), cycles=1500, stop_at=0, seed=20261016),
    dict(name="stop", kind="stop", m=2, d=32, g0=1, g1=8, theta=300, Q=10, I=50,
         tau=25, W=4, noise=(19, 20), cycles=1000, stop_at=300, seed=20261017),
    dict(name="exact", kind="steady", m=4, d=16, g0=1, g1=4, theta=60, Q=20, I=40,
         tau=50, W=8, noise=None, cycles=1000, stop_at=0, seed=7),
]


def gen_cycle(cfg, rng, t):
    """Registros gerados no ciclo t, por âncora (antes do corte por I). Ordem de consumo
    do RNG fixa: para cada âncora: n; depois, para cada registro: q e classe."""
    out = []
    for _a in range(cfg["m"]):
        kind = cfg["kind"]
        if kind == "steady":
            n = rng.below(3)
        elif kind == "burst":
            n = (2 + rng.below(3)) if (t % 200) < 20 else rng.below(2)
        else:  # stop: carga pesada (2..5 registros) até stop_at, depois silêncio (sem consumir RNG)
            n = (2 + rng.below(4)) if t < cfg["stop_at"] else 0
        lst = []
        for _i in range(n):
            q = 1 + rng.below(cfg["Q"])
            klass = IRR if rng.below(10) == 0 else COMP
            lst.append((q, klass))
        out.append(lst)
    return out


def run(cfg, tamper=None):
    """Executa um cenário e devolve (metrics, ring_windows, compactor).
    `tamper`: função opcional (record) chamada em cada registro aceito — usada pelos
    testes de vizinhança (altera identidade/valor de UM registro) sem tocar no RNG."""
    m, d, g0, g1, theta = cfg["m"], cfg["d"], cfg["g0"], cfg["g1"], cfg["theta"]
    Q, I, tau, W = cfg["Q"], cfg["I"], cfg["tau"], cfg["W"]
    seed = cfg["seed"]
    B = bound_B(d, theta, g0, g1, I)
    lat_bound = settle_steps(d, g0, B + I) - 1
    raw_bound = lat_bound + tau - 1

    rng = SplitMix64(seed)
    comp = Compactor(m, W, cfg["noise"])
    queues = [deque() for _ in range(m)]
    u = [0] * m
    settled = []
    shadow = {}            # só na bancada de medição: somas verdadeiras por janela
    next_id = 0
    mt = {k: 0 for k in KEYS}
    mt["bound_B"] = B
    mt["latency_bound"] = lat_bound
    mt["raw_age_bound"] = raw_bound
    mt["cycles"] = cfg["cycles"]
    mt["first_zero_after_stop"] = -1

    for t in range(cfg["cycles"]):
        gen = gen_cycle(cfg, rng, t)
        for a in range(m):
            inj = 0
            for (q, klass) in gen[a]:
                mt["records_generated"] += 1
                if klass == COMP:
                    if inj + q > I:
                        mt["records_dropped_by_cap"] += 1
                        continue
                    inj += q
                    rec = Record(next_id, a, q, COMP, t)
                    next_id += 1
                    if tamper is not None:
                        tamper(rec)
                    queues[a].append(rec)
                    u[a] += rec.q
                    mt["records_compensable"] += 1
                    mt["exposure_injected"] += rec.q
                else:
                    rec = Record(next_id, a, q, IRR, t)
                    next_id += 1
                    if tamper is not None:
                        tamper(rec)
                    settled.append(rec)
                    mt["records_irreversible"] += 1
                mt["records_injected"] += 1
        live = sum(len(qq) for qq in queues)
        if live + len(settled) > mt["ledger_peak_records"]:
            mt["ledger_peak_records"] = live + len(settled)

        for a in range(m):
            v = u[a]
            g = rate(theta, g0, g1, v)
            budget = removal(d, g, v)
            cum = 0
            while cum < budget and queues[a]:
                r = queues[a].popleft()
                cum += r.q
                settled.append(r)
                lat = t - r.born
                if lat > mt["max_settle_latency"]:
                    mt["max_settle_latency"] = lat
                if lat > lat_bound:
                    mt["latency_violations"] += 1
            u2 = v - cum
            if not (d * u2 + g * v <= d * v):
                mt["contract_violations"] += 1
            if u2 > B:
                mt["bound_violations"] += 1
            if u2 > mt["max_exposure"]:
                mt["max_exposure"] = u2
            if cum > 0:
                mt["discharge_events"] += 1
                if v > theta:
                    mt["boosted_events"] += 1
                mt["exposure_settled"] += cum
            u[a] = u2

        if cfg["kind"] == "stop" and t == cfg["stop_at"] - 1:
            mt["exposure_at_stop"] = sum(u)
        if (cfg["kind"] == "stop" and t >= cfg["stop_at"] and mt["first_zero_after_stop"] < 0
                and sum(u) == 0):
            mt["first_zero_after_stop"] = t

        if (t + 1) % tau == 0:
            widx = (t + 1) // tau - 1
            rep = comp.seal(widx, settled, seed, t)
            settled = []
            shadow[widx] = rep["true_sums"]
            mt["windows_sealed"] += 1
            mt["windows_evicted"] += rep["evicted"]
            mt["records_erased"] += rep["erased_records"]
            mt["bytes_erased"] += rep["erased_bytes"]
            if rep["max_age"] > mt["max_raw_age_at_erase"]:
                mt["max_raw_age_at_erase"] = rep["max_age"]

    ring = comp.windows
    mt["ring_len_final"] = len(ring)
    mt["retained_state_ints"] = len(ring) * 2 * m
    mt["ledger_final_records"] = sum(len(qq) for qq in queues) + len(settled)
    mt["live_final_exposure"] = sum(u)
    err = 0
    tot = 0
    flat = []
    for (idx, sums) in ring:
        tr = shadow[idx]
        for c in range(2 * m):
            err += abs(sums[c] - tr[c])
            tot += abs(tr[c])
            flat.append(sums[c])
    mt["abs_error_sum"] = err
    mt["true_abs_sum"] = tot
    mt["rel_error_permille"] = (1000 * err) // tot if tot > 0 else 0
    mt["state_checksum"] = fnv1a64_ints(flat)
    return mt, ring, comp


def sampler_histogram(n, p, q, seed, lo=-8, hi=8):
    """Histograma inteiro do amostrador bilateral (T-SAM). Chaves: lo..hi, abaixo, acima."""
    rng = SplitMix64(seed)
    counts = {z: 0 for z in range(lo, hi + 1)}
    below_c = 0
    above_c = 0
    s = 0
    sa = 0
    for _ in range(n):
        z = rng.two_sided_geometric(p, q)
        s += z
        sa += abs(z)
        if z < lo:
            below_c += 1
        elif z > hi:
            above_c += 1
        else:
            counts[z] += 1
    return counts, below_c, above_c, s, sa


def golden_text():
    lines = ["# atrator-compactador golden v0.2"]
    for cfg in SCENARIOS:
        mt, _ring, _comp = run(cfg)
        lines.append("[%s]" % cfg["name"])
        for k in KEYS:
            lines.append("%s=%d" % (k, mt[k]))
    n, p, q, seed = 20000, 39, 41, 12345
    counts, bl, ab, s, sa = sampler_histogram(n, p, q, seed)
    lines.append("[sampler]")
    lines.append("n=%d" % n)
    lines.append("p=%d" % p)
    lines.append("q=%d" % q)
    lines.append("seed=%d" % seed)
    for z in sorted(counts):
        lines.append("count[%d]=%d" % (z, counts[z]))
    lines.append("below=%d" % bl)
    lines.append("above=%d" % ab)
    lines.append("sum=%d" % s)
    lines.append("sum_abs=%d" % sa)
    return "\n".join(lines) + "\n"
