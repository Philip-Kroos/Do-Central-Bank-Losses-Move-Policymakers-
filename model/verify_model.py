"""
Symbolic/numerical verification of the advocacy model (Section 3).

Governor i states preferred settings for three instruments:
    r : policy rate
    q : share of reserves NOT remunerated (q = 1 - rho); higher q = advocating lower remuneration
    a : active sales of the NCB's own (non-pooled) sovereign portfolio

Loss (per unit of Eurosystem capital key):
    L = 1/2 (g - kappa r - eta a)^2 + 1/2 zeta a^2 + 1/2 chi q^2 + 1/2 phi r^2 - omega * Pi
    Pi = S s - (1 - q) D r + B r - a delta (r - s)

g      : perceived inflation pressure (hawkishness / beliefs)
phi    : cost of the rate itself (without it, sales are never used at omega = 0)
omega  : effective weight on own P&L = psi * (1 + ell * 1{Pi_i + buffer_i < 0})
D, B   : reserves, banknotes per unit of key (POOLED -> identical across NCBs)
delta,s: duration and yield of own sovereign portfolio (NON-POOLED -> NCB-specific)

AUDIT LOG
v1 asserted a "hawk vs accountant" sign pattern on asset sales (da/dg > 0, da/domega < 0).
It FAILS in 151 of 194 admissible draws: an accountant cuts the (expensive) rate and
substitutes into sales when unit sales losses delta*(r - s) are small relative to the
rate exposure (1-q)D - B. That prediction is dropped. The propositions below are the
ones that survive.
v2 also asserted da*/d(delta) < 0; it fails in 15 of 266 draws (duration raises rate
exposure too). Only the own-yield shifter s is retained for P3.
"""
import random
import sympy as sp

r, q, a = sp.symbols("r q a", real=True)
g, kappa, eta, zeta, chi, omega, phi = sp.symbols("g kappa eta zeta chi omega phi", positive=True)
D, B, S, s, delta = sp.symbols("D B S s delta", positive=True)

Pi = S * s - (1 - q) * D * r + B * r - a * delta * (r - s)
C = (sp.Rational(1, 2) * (g - kappa * r - eta * a) ** 2 + sp.Rational(1, 2) * zeta * a ** 2
     + sp.Rational(1, 2) * chi * q ** 2 + sp.Rational(1, 2) * phi * r ** 2)
L = C - omega * Pi
x = sp.Matrix([r, q, a])
F = sp.Matrix([sp.diff(L, v) for v in x])
H = F.jacobian(x)

# ---------------------------------------------------------------- P1: stance neutrality at omega = 0
H0, F0 = H.subs(omega, 0), F.subs(omega, 0)
x0 = sp.solve(list(F0), list(x), dict=True)[0]
dx_dg0 = sp.simplify(-H0.inv() * F0.diff(g))
assert sp.simplify(x0[q]) == 0 and sp.simplify(dx_dg0[1]) == 0
assert all(bool(sp.simplify(e) > 0) for e in (dx_dg0[0], dx_dg0[2]))
dx_dw0 = sp.simplify((-H.inv() * F.diff(omega)).subs(omega, 0).subs(x0))
print("P1  q*(omega=0) = 0;  dq*/dg|0 = 0;  dq*/domega|0 =", sp.factor(dx_dw0[1]))
assert bool(sp.simplify(dx_dw0[1] - D * x0[r] / chi) == 0)

# ---------------------------------------------------------------- P4: pooled instrument
assert sp.simplify(sp.diff(F[1], omega) + D * r) == 0      # common per unit of key
assert sp.simplify(sp.diff(F[2], omega) - delta * (r - s)) == 0
print("P4  dF_q/domega = -D r (common across NCBs); dF_a/domega = delta (r - s) (NCB-specific)")

# ---------------------------------------------------------------- numerical checks P2, P3
random.seed(20260910)
def draw():
    return {g: random.uniform(0.02, 0.06), kappa: random.uniform(0.8, 1.5), eta: random.uniform(0.05, 0.4),
            zeta: random.uniform(0.5, 3.0), phi: random.uniform(0.2, 2.0), chi: random.uniform(0.5, 3.0),
            omega: random.uniform(0.001, 0.05), D: random.uniform(0.5, 1.0), B: random.uniform(0.1, 0.3),
            S: random.uniform(0.3, 0.8), s: random.uniform(0.0, 0.015), delta: random.uniform(3.0, 9.0)}

def optimum(p):
    sol = sp.nsolve(list(F.subs(p)), list(x), [p[g] / p[kappa], 0.01, 0.01], tol=1e-14, maxsteps=200)
    return {r: sol[0], q: sol[1], a: sol[2]}

counts = dict(n=0, P2=0, P3_delta=0, P3_s=0, naive_sales=0)
for _ in range(400):
    p = draw()
    try:
        o = optimum(p)
    except Exception:
        continue
    pt = {**p, **o}
    Hn = H.subs(pt)
    if not all(bool(m > 0) for m in (Hn[0, 0], Hn[:2, :2].det(), Hn.det())):
        continue
    if not bool(o[r] > p[s] and 0 < o[q] < 1 and o[a] > 0):
        continue
    counts["n"] += 1
    Hinv = Hn.inv()
    dx_dw = -Hinv * F.diff(omega).subs(pt)
    # P2 revealed P&L monotonicity: dPi(x*)/domega = grad Pi . dx*/domega >= 0
    gradPi = sp.Matrix([sp.diff(Pi, v) for v in x]).subs(pt)
    counts["P2"] += bool((gradPi.T * dx_dw)[0] >= -1e-12)
    # P3 non-pooled heterogeneity: higher duration -> fewer sales; higher own yield -> more sales
    dx_dd = -Hinv * F.diff(delta).subs(pt)
    dx_ds = -Hinv * F.diff(s).subs(pt)
    counts["P3_delta"] += bool(dx_dd[2] < 0)
    counts["P3_s"] += bool(dx_ds[2] > 0)
    counts["naive_sales"] += bool(dx_dw[2] < 0)

print("draws", counts)
n = counts["n"]
assert n > 100 and counts["P2"] == n, "P2 violated"
assert counts["P3_s"] == n, "P3 violated"
print(f"P2  revealed P&L monotonicity holds in {counts['P2']}/{n} draws")
print(f"P3  da*/ds > 0 in {counts['P3_s']}/{n}")
print(f"DROPPED duration prediction da*/d(delta) < 0 holds in {counts['P3_delta']}/{n} (not robust: delta also raises rate exposure)")
print(f"DROPPED naive prediction da*/domega < 0 holds in only {counts['naive_sales']}/{n}")
print("All retained model checks passed.")
