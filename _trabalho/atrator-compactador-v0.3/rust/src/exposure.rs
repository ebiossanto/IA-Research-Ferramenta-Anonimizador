//! Descarga com cota ISS — aritmética inteira (espelha lean/AtratorCore/*.lean).
//!
//! @trace T-D-REM        removal: g*v <= d*removal  e  removal <= v
//! @trace T-D-CONTRACT   discharge_ceil satisfaz  d*D(v) + g*v <= d*v
//! @trace T-D-MONO       lema de monotonia  d*a + g*b <= d*b + g*a  (a<=b, g<=d)
//! @trace T-D-POS        v>=1, g>=1  =>  removal>=1  e  D(v) < v
//! @trace T-ISS-LYAP     decréscimo de Lyapunov: d*u' + g0*(u+i) <= d*(u+i)
//! @trace T-ISS-INV      invariância de [0,B] (limite último)
//! @trace T-ISS-CLOSED   forma fechada ISS (aditiva, inteira)
//! @trace T-DP-GEO       p^(m+Q) q^n <= p^n q^(m+Q)  quando n <= m+Q, p <= q
//! @trace T-LAT          settle_steps: nº de iterações de f(R)=R-removal(d,g0,R) até 0
//!
//! Pré-condições (verificadas por testes, assumidas aqui): 1 <= d <= 2^32, 1 <= g <= d,
//! v < 2^64  =>  nenhum estouro nas contas intermediárias em u128.

/// ceil(g*v/d): quanto a descarga reverte de uma exposição v.
pub fn removal(d: u64, g: u64, v: u64) -> u64 {
    (((g as u128) * (v as u128) + (d as u128) - 1) / (d as u128)) as u64
}

pub fn discharge_ceil(d: u64, g: u64, v: u64) -> u64 {
    v - removal(d, g, v)
}

/// Duas camadas: descarga de fundo g0 sempre; reforço g1 acima do limiar (avalanche).
pub fn rate(theta: u64, g0: u64, g1: u64, v: u64) -> u64 {
    if v > theta {
        g1
    } else {
        g0
    }
}

pub fn disch(d: u64, theta: u64, g0: u64, g1: u64, v: u64) -> u64 {
    discharge_ceil(d, rate(theta, g0, g1, v), v)
}

pub fn step(d: u64, theta: u64, g0: u64, g1: u64, u: u64, iota: u64) -> u64 {
    disch(d, theta, g0, g1, u + iota)
}

pub fn ceil_div_u128(a: u128, b: u128) -> u128 {
    (a + b - 1) / b
}

/// Menor B com  d*theta <= d*B + g0*theta  e  d*I <= g1*B + g1*I.
pub fn bound_b(d: u64, theta: u64, g0: u64, g1: u64, i: u64) -> u64 {
    let b1 = ceil_div_u128(((d - g0) as u128) * (theta as u128), d as u128);
    let b2 = ceil_div_u128(((d - g1) as u128) * (i as u128), g1 as u128);
    (if b1 > b2 { b1 } else { b2 }) as u64
}

pub fn contract_holds(d: u64, g: u64, v: u64, u2: u64) -> bool {
    (d as u128) * (u2 as u128) + (g as u128) * (v as u128) <= (d as u128) * (v as u128)
}

pub fn mono_aux_holds(d: u64, g: u64, a: u64, b: u64) -> bool {
    (d as u128) * (a as u128) + (g as u128) * (b as u128)
        <= (d as u128) * (b as u128) + (g as u128) * (a as u128)
}

fn pow_u128(base: u128, exp: u32) -> Option<u128> {
    let mut r: u128 = 1;
    for _ in 0..exp {
        r = r.checked_mul(base)?;
    }
    Some(r)
}

/// d^k g0 u_k + c I c^k <= c^k g0 u0 + c I d^k,  c = d - g0.  None se estourar u128.
pub fn iss_closed_holds(d: u64, g0: u64, i: u64, u0: u64, k: u32, uk: u64) -> Option<bool> {
    let c = (d - g0) as u128;
    let dk = pow_u128(d as u128, k)?;
    let ck = pow_u128(c, k)?;
    let ci = c.checked_mul(i as u128)?;
    let lhs = dk
        .checked_mul(g0 as u128)?
        .checked_mul(uk as u128)?
        .checked_add(ci.checked_mul(ck)?)?;
    let rhs = ck
        .checked_mul(g0 as u128)?
        .checked_mul(u0 as u128)?
        .checked_add(ci.checked_mul(dk)?)?;
    Some(lhs <= rhs)
}

/// p^(m+Q) q^n <= p^n q^(m+Q).  None se estourar u128.
pub fn geo_ratio_holds(p: u64, q: u64, big_q: u32, m: u32, n: u32) -> Option<bool> {
    let lhs = pow_u128(p as u128, m + big_q)?.checked_mul(pow_u128(q as u128, n)?)?;
    let rhs = pow_u128(p as u128, n)?.checked_mul(pow_u128(q as u128, m + big_q)?)?;
    Some(lhs <= rhs)
}

/// N(R) = menor k com f^k(R) = 0, f(R) = R - removal(d, g0, R).  Requer g0 >= 1.
pub fn settle_steps(d: u64, g0: u64, r: u64) -> u64 {
    let mut r = r;
    let mut k: u64 = 0;
    while r > 0 {
        r -= removal(d, g0, r);
        k += 1;
    }
    k
}
