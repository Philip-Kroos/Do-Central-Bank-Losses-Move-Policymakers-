"""
Ex-ante power for the staggered loss-salience design (workflow step 4).

Everything below is an ASSUMPTION to be replaced by corpus counts once the speech data
arrive. No number here is an estimate of anything in the world.

Design simulated
  units      : 20 NCB governors (Executive Board placebo not needed for power)
  periods    : half-years 2016H1-2026H2 (22)
  treatment  : D_it = 1 from the half-year after the NCB first publishes a loss / zero
               distribution; staggered cohorts (ASSUMED): 5 NCBs 2024H1, 5 in 2025H1,
               4 in 2026H1, 6 not treated within sample
  data       : N_it ~ Poisson(lambda) passages on reserve remuneration per governor-half-year
               (lambda is the key unknown -> grid)
  outcome    : passage position y in [-1, 1] (support for lower remuneration)
               y = alpha_i + gamma_t + beta * D_it + u_it + e_p,
               u_it ~ N(0, 0.15)  governor-period shock
               e_p  ~ N(0, 0.64)  passage noise incl. LLM measurement error (sqrt(0.5^2 + 0.4^2))
  estimator  : two-way FE on governor-period means, weights N_it (homogeneous effect ->
               TWFE unbiased here; the real analysis uses heterogeneity-robust estimators)
  inference  : randomization inference, permuting cohort labels across NCBs (199 draws),
               two-sided 5%
Outputs power by (lambda, beta) and the MDE at 80% power.
"""
import itertools
import json
import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260910)
N_UNITS, N_PER = 20, 22                      # 2016H1 .. 2026H2
PERIOD_2024H1 = 16                           # index: 2016H1 = 0
COHORTS = [15] * 4 + [17] * 2 + [19] * 3 + [np.inf] * 11   # SENSITIVITY v2: net-loss definition, 6 of 13 collected NCBs treated, scaled to 20 [ASSUMPTION]
SD_UNIT_PERIOD, SD_PASSAGE = 0.15, float(np.hypot(0.5, 0.4))
N_PERM, N_REP = 199, 150
LAMBDAS = [1.0, 2.0, 4.0]
BETAS = [0.0, 0.3, 0.45, 0.6]


def treatment_matrix(cohorts):
    t = np.arange(N_PER)[None, :]
    return (t >= np.asarray(cohorts, dtype=float)[:, None]).astype(float)


def simulate_panel(lam, beta):
    alpha = RNG.normal(0, 0.3, N_UNITS)[:, None]
    gamma = np.cumsum(RNG.normal(0, 0.05, N_PER))[None, :]
    D = treatment_matrix(COHORTS)
    n = RNG.poisson(lam, (N_UNITS, N_PER))
    mean_latent = alpha + gamma + beta * D + RNG.normal(0, SD_UNIT_PERIOD, (N_UNITS, N_PER))
    # mean of n passage draws: latent + N(0, sd/sqrt(n))
    with np.errstate(divide="ignore", invalid="ignore"):
        ybar = mean_latent + RNG.normal(0, 1, (N_UNITS, N_PER)) * SD_PASSAGE / np.sqrt(n)
    obs = n > 0
    return ybar, n, obs


def fe_design(obs):
    i, t = np.nonzero(obs)
    X = np.zeros((len(i), N_UNITS + N_PER - 1))
    X[np.arange(len(i)), i] = 1.0
    tt = t > 0
    X[np.arange(len(i))[tt], N_UNITS + t[tt] - 1] = 1.0
    return i, t, X


def beta_hats(ybar, n, obs, D_stack):
    """FWL: residualise y and all candidate treatment columns on FE, weighted by n."""
    i, t, X = fe_design(obs)
    w = np.sqrt(n[i, t])
    Xw = X * w[:, None]
    y = ybar[i, t] * w
    Dm = D_stack[:, i, t].T * w[:, None]                 # obs x K
    coef, *_ = np.linalg.lstsq(Xw, np.column_stack([y, Dm]), rcond=None)
    resid = np.column_stack([y, Dm]) - Xw @ coef
    ry, rD = resid[:, 0], resid[:, 1:]
    denom = (rD ** 2).sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (rD * ry[:, None]).sum(axis=0) / denom


def one_rep(lam, beta):
    ybar, n, obs = simulate_panel(lam, beta)
    perms = [COHORTS] + [list(RNG.permutation(COHORTS)) for _ in range(N_PERM)]
    D_stack = np.stack([treatment_matrix(c) for c in perms])
    b = beta_hats(ybar, n, obs, D_stack)
    b = b[np.isfinite(b)]
    if len(b) < 50:
        return np.nan, np.nan
    p = (np.abs(b[1:]) >= np.abs(b[0])).mean()
    return b[0], p


rows = []
for lam, beta in itertools.product(LAMBDAS, BETAS):
    res = np.array([one_rep(lam, beta) for _ in range(N_REP)])
    ok = np.isfinite(res[:, 1])
    rows.append(dict(passages_per_gov_halfyear=lam, beta=beta,
                     power=float((res[ok, 1] < 0.05).mean()),
                     mean_beta_hat=float(np.nanmean(res[:, 0])),
                     sd_beta_hat=float(np.nanstd(res[:, 0])),
                     expected_passages_total=lam * N_UNITS * N_PER))
    print(rows[-1], flush=True)

df = pd.DataFrame(rows)
df.to_csv("power_grid_net_definition.csv", index=False)

mde = {}
for lam, g in df.groupby("passages_per_gov_halfyear"):
    g = g.sort_values("beta")
    above = g[(g.beta > 0) & (g.power >= 0.8)]
    mde[str(lam)] = float(above.beta.min()) if len(above) else None
with open("mde_net_definition.json", "w") as f:
    json.dump(dict(mde_at_80pct_power=mde, n_rep=N_REP, n_perm=N_PERM,
                   size_at_beta0={str(k): float(v) for k, v in
                                  df[df.beta == 0].set_index("passages_per_gov_halfyear").power.items()}),
              f, indent=2)
print(json.dumps(mde, indent=2))
