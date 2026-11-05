"""Especificação executável em aritmética inteira (espelha lean/AtratorCore/*.lean).

@trace T-D-REM        removal: g*v <= d*removal  e  removal <= v
@trace T-D-CONTRACT   discharge_ceil satisfaz  d*D(v) + g*v <= d*v
@trace T-D-MONO       lema de monotonia  d*a + g*b <= d*b + g*a  (a<=b, g<=d)
@trace T-D-POS        v>=1, g>=1  =>  removal>=1  e  D(v) < v
@trace T-ISS-LYAP     decréscimo de Lyapunov: d*u' + g0*(u+i) <= d*(u+i)
@trace T-ISS-INV      invariância de [0,B] (limite último)
@trace T-ISS-CLOSED   forma fechada ISS (aditiva, inteira)
@trace T-DP-GEO       p^(m+Q) q^n <= p^n q^(m+Q)  quando n <= m+Q, p <= q
@trace T-LAT          settle_steps: nº de iterações de f(R)=R-removal(d,g0,R) até 0 (cota de latência)
"""


def ceil_div(a, b):
    return (a + b - 1) // b


def removal(d, g, v):
    """ceil(g*v/d): quanto a descarga reverte de uma exposição v."""
    return (g * v + (d - 1)) // d


def discharge_ceil(d, g, v):
    return v - removal(d, g, v)


def rate(theta, g0, g1, v):
    """Duas camadas: descarga de fundo g0 sempre; reforço g1 acima do limiar (avalanche)."""
    return g1 if v > theta else g0


def disch(d, theta, g0, g1, v):
    return discharge_ceil(d, rate(theta, g0, g1, v), v)


def step(d, theta, g0, g1, u, iota):
    return disch(d, theta, g0, g1, u + iota)


def bound_B(d, theta, g0, g1, I):
    """Menor B com  d*theta <= d*B + g0*theta  e  d*I <= g1*B + g1*I."""
    return max(ceil_div((d - g0) * theta, d), ceil_div((d - g1) * I, g1))


def contract_holds(d, g, v, u2):
    return d * u2 + g * v <= d * v


def mono_aux_holds(d, g, a, b):
    return d * a + g * b <= d * b + g * a


def iss_closed_holds(d, g0, I, u0, k, uk):
    """d^k g0 u_k + c I c^k <= c^k g0 u0 + c I d^k,  c = d - g0  (equiv. à cota ISS fechada)."""
    c = d - g0
    return d ** k * g0 * uk + c * I * c ** k <= c ** k * g0 * u0 + c * I * d ** k


def geo_ratio_holds(p, q, Q, m, n):
    return p ** (m + Q) * q ** n <= p ** n * q ** (m + Q)


def settle_steps(d, g0, R):
    """N(R) = menor k com f^k(R) = 0, f(R) = R - removal(d, g0, R).  f é monótona (incrementos 0/1),
    logo a latência de liquidação FIFO de qualquer registro admitido com R <= B+I é <= N(B+I) - 1."""
    k = 0
    while R > 0:
        R = R - removal(d, g0, R)
        k += 1
    return k
