"""Medições numéricas (float permitido: NÃO entram no golden; são relatório).
Gera um relatório Markdown com tabelas. Determinístico (sementes fixas), exceto por diferenças
de último dígito de ponto flutuante entre plataformas.

@trace T-SAM @trace T-DP-EPS @trace T-DP-INFO @trace T-DP-UTIL @trace T-F-EVICT @trace T-TIMELINE
"""
import math
import platform
import sys
from fractions import Fraction

from .rng import SplitMix64
from .spec import bound_B, settle_steps
from .system import COMP, SCENARIOS, Compactor, Record, run


def pmf_f(p, q, z):
    a = p / q
    return (1 - a) / (1 + a) * a ** abs(z)


def choose_pq(eps, Q, den=10000):
    alpha = math.exp(-eps / Q)
    p = int(round(alpha * den))
    p = min(p, den - 1)
    return p, den


def eps_of(p, q, Q):
    return Q * math.log(q / p)


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def m_sampler(p=39, q=41, n=60000, seed=2026):
    rng = SplitMix64(seed)
    counts = {}
    s = 0
    s2 = 0
    for _ in range(n):
        z = rng.two_sided_geometric(p, q)
        counts[z] = counts.get(z, 0) + 1
        s += z
        s2 += z * z
    tv = 0.0
    for z in range(-400, 401):
        tv += abs(counts.get(z, 0) / n - pmf_f(p, q, z))
    tv = 0.5 * (tv + sum(c for z, c in counts.items() if abs(z) > 400) / n)
    worst = max(abs(counts.get(z, 0) / n - pmf_f(p, q, z)) for z in range(-15, 16))
    a = p / q
    return {"n": n, "mean": s / n, "var": s2 / n - (s / n) ** 2, "var_theory": 2 * a / (1 - a) ** 2,
            "tv": tv, "max_dev_center": worst}


def m_attack(p=39, q=41, Q=20, n=60000, seed=99):
    a = p / q
    c = (q - p) / (q + p)
    lo, hi = -600, 4000
    f0 = {y: c * a ** abs(y) for y in range(lo, hi)}
    f1 = {y: c * a ** abs(y - Q) for y in range(lo, hi)}
    tail0, tail1 = {}, {}
    t0 = t1 = 0.0
    for tau in range(hi - 1, lo - 1, -1):
        t0 += f0[tau]
        t1 += f1[tau]
        tail0[tau] = t0
        tail1[tau] = t1
    rng0 = SplitMix64(seed)
    rng1 = SplitMix64(seed + 1)
    s0 = [rng0.two_sided_geometric(p, q) for _ in range(n)]
    s1 = [Q + rng1.two_sided_geometric(p, q) for _ in range(n)]
    rows = []
    e = (q / p) ** Q
    for tau in (-20, 0, 10, 20, 30, 40, 60, 80):
        fpr = tail0[tau]
        tpr = tail1[tau]
        efpr = sum(1 for y in s0 if y >= tau) / n
        etpr = sum(1 for y in s1 if y >= tau) / n
        rows.append((tau, "%.5f" % tpr, "%.5f" % fpr, "%.4f" % (tpr / fpr), "%.4f" % (etpr / efpr if efpr else float("nan"))))
    mx = max(tail1[t] / tail0[t] for t in range(-100, 400))
    return rows, e, mx


def m_mi(Q=20):
    rows = []
    for eps_t in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0):
        p, q = choose_pq(eps_t, Q)
        eps = eps_of(p, q, Q)
        mi = 0.0
        span = int(60 * q / (q - p)) + 3 * Q + 50
        for y in range(-span, span + Q):
            p0 = pmf_f(p, q, y)
            p1 = pmf_f(p, q, y - Q)
            pm = 0.5 * (p0 + p1)
            if p0 > 0:
                mi += 0.5 * p0 * math.log2(p0 / pm)
            if p1 > 0:
                mi += 0.5 * p1 * math.log2(p1 / pm)
        bound = math.log2(2 * math.exp(eps) / (math.exp(eps) + 1))
        rows.append(("%.4f" % eps, "%d/%d" % (p, q), "%.5f" % mi, "%.5f" % bound, "%.5f" % (eps * math.log2(math.e))))
    return rows


def m_utility(Q=20):
    """Utilidade x epsilon: no sistema real (cenário steady), variando só o ruído."""
    base = [c for c in SCENARIOS if c["name"] == "steady"][0]
    rows = []
    for eps_t in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0):
        p, q = choose_pq(eps_t, base["Q"])
        eps = eps_of(p, q, base["Q"])
        cfg = dict(base)
        cfg["noise"] = (p, q)
        mt, _, _ = run(cfg)
        a = p / q
        ez = 2 * a / (1 - a * a)
        rng = SplitMix64(31337)
        N = 3000
        mc = sum(abs(rng.two_sided_geometric(p, q)) for _ in range(N)) / N
        rows.append(("%.3f" % eps, "%d/%d" % (p, q), "%.2f" % ez, "%.2f" % mc,
                     mt["abs_error_sum"], mt["true_abs_sum"], mt["rel_error_permille"]))
    return rows


def m_forgetting_profile(M=3, W=8, noise=(39, 41), seed=99, qx=17):
    def synth(widx):
        rng = SplitMix64(1000 + widx)
        out = []
        for i in range(6):
            a = rng.below(M)
            q = 1 + rng.below(20)
            out.append(Record(i, a, q, COMP, widx))
        return out

    ca = Compactor(M, W, noise)
    cb = Compactor(M, W, noise)
    rows = []
    for w in range(W + 4):
        ra = synth(w)
        rb = synth(w)
        if w == 0:
            rb.append(Record(999, 1, qx, COMP, 0))
        ca.seal(w, ra, seed, now=w)
        cb.seal(w, rb, seed, now=w)
        diff = sum(abs(x - y) for x, y in zip(ca.state(), cb.state()))
        age = w  # idade da janela 0 em janelas seladas desde então
        rows.append((age, diff, "ε0" if diff else "0 (exato)"))
    return rows


def m_scenarios():
    rows = []
    for cfg in SCENARIOS:
        mt, _, _ = run(cfg)
        B = bound_B(cfg["d"], cfg["theta"], cfg["g0"], cfg["g1"], cfg["I"])
        rows.append((cfg["name"], mt["records_injected"], mt["records_dropped_by_cap"], mt["boosted_events"],
                     "%d / %d" % (mt["max_exposure"], B), "%d / %d" % (mt["max_settle_latency"], mt["latency_bound"]),
                     "%d / %d" % (mt["max_raw_age_at_erase"], mt["raw_age_bound"]),
                     "%d → %d" % (mt["records_erased"], mt["retained_state_ints"]),
                     mt["rel_error_permille"],
                     "%d/%d/%d" % (mt["bound_violations"], mt["contract_violations"], mt["latency_violations"])))
    stop = [c for c in SCENARIOS if c["name"] == "stop"][0]
    mt, _, _ = run(stop)
    B = bound_B(stop["d"], stop["theta"], stop["g0"], stop["g1"], stop["I"])
    stop_info = (mt["exposure_at_stop"], mt["first_zero_after_stop"] - stop["stop_at"], settle_steps(stop["d"], stop["g0"], B))
    return rows, stop_info


def build_report():
    out = []
    out.append("# Medição (Python de referência) — gerada por `python/run_analysis.py`\n")
    out.append("Ambiente: Python %s, %s. **Rust e Lean não foram executados** na geração deste relatório; "
               "os números abaixo vêm só da implementação de referência em Python (inteiros exatos onde indicado). "
               "Floats aparecem apenas em estatísticas/relatórios, nunca no golden.\n" % (sys.version.split()[0], platform.platform()))

    rows, stop_info = m_scenarios()
    out.append("## M1. Cenários (os mesmos do golden)\n")
    out.append(md_table(["cenário", "registros", "descartados (cap I)", "descargas reforçadas", "exposição máx / B",
                         "latência máx / cota", "idade bruta máx / cota", "registros apagados → ints retidos",
                         "erro rel. (‰)", "viol. B/contrato/lat."], rows))
    out.append("\nNo cenário `stop`: exposição somada no instante da parada = **%d**; zerou em **%d** ciclos "
               "(cota teórica por âncora: %d)." % stop_info)

    s = m_sampler()
    out.append("\n\n## M2. Fidelidade do amostrador (N=%d, p/q=39/41)\n" % s["n"])
    out.append(md_table(["métrica", "medido", "teoria"], [
        ("média", "%.4f" % s["mean"], "0"),
        ("variância", "%.1f" % s["var"], "%.1f" % s["var_theory"]),
        ("distância de variação total (TV) ao pmf exato", "%.5f" % s["tv"], "→ 0 com N"),
        ("máx abs(freq − pmf) para z de −15 a 15", "%.5f" % s["max_dev_center"], "~ 1/√N ≈ %.4f" % (1 / math.sqrt(s["n"])))]))

    rows, e, mx = m_attack()
    out.append("\n\n## M3. Ataque de pertinência (presença de um registro de magnitude Q=20), ε0 = %.4f\n" % eps_of(39, 41, 20))
    out.append("Teste do tipo \"decidir *presente* se saída ≥ τ\". TPR/FPR analítico é exato; coluna final é Monte Carlo (N=60000 por braço).\n")
    out.append(md_table(["τ", "TPR (exato)", "FPR (exato)", "TPR/FPR (exato)", "TPR/FPR (MC)"], rows))
    out.append("\n`e^ε0 = %.4f`; máximo de TPR/FPR sobre τ∈[−100,400): **%.4f** (a cota é atingida: é justa)." % (e, mx))

    out.append("\n\n## M4. Informação residual sobre a presença de um registro (bits)\n")
    out.append("Prior uniforme sobre {ausente, presente}; Q=20. `I exata` por soma numérica; `cota` = log2(2e^ε/(e^ε+1)).\n")
    out.append(md_table(["ε0", "p/q", "I(X;Y) exata", "cota DP", "ε0·log2 e (cota folgada)"], m_mi()))

    out.append("\n\n## M5. Utilidade × ε0 no sistema (cenário `steady`, só o ruído varia)\n")
    out.append(md_table(["ε0", "p/q", "E[abs Z] teoria", "E[abs Z] MC (N=3000)", "soma abs(erro) no anel", "soma abs(verdadeiro) no anel", "erro rel. (‰)"], m_utility()))

    out.append("\n\n## M6. Perfil de esquecimento (execução acoplada: mesmo ruído, um registro extra de magnitude 17 na janela 0; W=8)\n")
    out.append(md_table(["janelas seladas após a janela 0", "‖estado − estado'‖₁", "vazamento residual"], m_forgetting_profile()))
    out.append("\nA diferença é exatamente a magnitude do registro enquanto a janela está no anel e **exatamente zero** após a evicção.")

    rep = {}
    # contagens das verificações exaustivas (reexecutadas aqui para o relatório)
    from .spec import contract_holds, discharge_ceil, geo_ratio_holds, removal
    n1 = n2 = 0
    for d in range(1, 41):
        for g in range(1, d + 1):
            for v in range(0, 301):
                assert g * v <= d * removal(d, g, v) and removal(d, g, v) <= v
                n1 += 1
                assert contract_holds(d, g, v, discharge_ceil(d, g, v))
    for q in range(1, 10):
        for p in range(1, q + 1):
            for Q in range(0, 6):
                for m in range(0, 13):
                    for n in range(0, m + Q + 1):
                        assert geo_ratio_holds(p, q, Q, m, n)
                        n2 += 1
    out.append("\n\n## M7. Verificações exaustivas (todas passaram)\n")
    out.append(md_table(["propriedade", "casos verificados"], [
        ("T-D-REM / T-D-CONTRACT: removal e contrato de descarga (d≤40, 1≤g≤d, v≤300)", n1),
        ("T-DP-GEO: p^(m+Q) q^n ≤ p^n q^(m+Q) (q≤9, Q≤5, m≤12)", n2)]))
    return "\n".join(out) + "\n"
