"""Power sensitivity for PAP v2: (a) binary N with sigma_u in {0.1, 0.2}; (b) continuous dose design
(H3): demeaned, standardised non-pooled carry per key point, TWFE (unit + half-year FE, weights),
RI by permuting whole exposure paths across units. Actual passage counts, f = 0.6.
usage: python3 ... mode(binary|dose) beta sigma_u reps"""
import json, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from code.estimate.fast_impute import Panel

mode, beta, su, reps = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
WITH_CTRL = len(sys.argv) > 5 and sys.argv[5].startswith("ctrl")
JACK = len(sys.argv) > 5 and sys.argv[5] == "ctrl_jack"
NPERM = 99 if JACK else 199
rng = np.random.default_rng(abs(hash((mode, beta, su, reps))) % 2**32)
counts = pd.read_pickle("data/derived/y4_counts_heads.pkl")
labels = [f"{y}H{h}" for y in range(2016, 2027) for h in (1, 2)][:21]
COH = {"NL": 15, "BE": 15, "SK": 15, "AT": 17, "DE": 19, "FR": 19,
       "ES": np.inf, "FI": np.inf, "GR": np.inf, "IE": np.inf, "IT": np.inf, "PT": np.inf, "LU": np.inf}
if mode == "dose":
    ex = pd.read_csv("output/exposure/exposure_halfyear_net_flow_pepp0.889_mm1.csv")
    units = sorted(set(ex.ncb) & set(counts.index.get_level_values(0)))
    X = ex.pivot(index="ncb", columns="hy", values="carry_per_keypp_demeaned").reindex(index=units, columns=labels)
    X = X.fillna(0.0).to_numpy()                                   # pre-2015/absent programme = no exposure
    X = (X - X.mean()) / X.std()
    from code.estimate import panel as pn
    S_ = pn.spread_panel(pd.read_csv("data/derived/yields.csv")); rates_ = pd.read_csv("data/derived/policy_rates.csv", parse_dates=["month"])
    PS_ = pn.pre_period_x_rate(S_, "spread_de", rates_).pivot(index="ncb", columns="hy", values="pre_spread_de_x_dfr").reindex(index=units, columns=labels).to_numpy()
    PD_ = pn.pre_period_x_rate(pd.read_csv("data/derived/debt_ratio_hy.csv"), "debt_ratio", rates_).pivot(index="ncb", columns="hy", values="pre_debt_ratio_x_dfr").reindex(index=units, columns=labels).to_numpy()
else:
    units = list(COH)
C = counts.reindex(pd.MultiIndex.from_product([units, labels]), fill_value=0).to_numpy().reshape(len(units), len(labels))

def fwl(ui, ti, y, w, x):
    n = len(y); Z = np.zeros((n, len(units) + len(labels) - 1))
    Z[np.arange(n), ui] = 1; m = ti > 0; Z[np.arange(n)[m], len(units) + ti[m] - 1] = 1
    if mode == "dose" and WITH_CTRL:
        Z = np.hstack([Z, np.nan_to_num(PS_[ui, ti])[:, None], np.nan_to_num(PD_[ui, ti])[:, None]])
    sw = np.sqrt(w); Zw = Z * sw[:, None]
    B = np.column_stack([y * sw, x * sw[:, None]])
    coef, *_ = np.linalg.lstsq(Zw, B, rcond=None)
    R = B - Zw @ coef                               # weighted residualised y (col 0) and x (cols 1..)
    ry, rx = R[:, [0]], R[:, 1:]
    b = (rx * ry).sum(0) / (rx ** 2).sum(0)
    e = ry - rx * b                                  # residuals per permutation column
    score = rx * e
    G = np.zeros((len(units), rx.shape[1]))
    np.add.at(G, ui, score)                          # cluster sums by unit (CR0)
    se = np.sqrt((G ** 2).sum(0)) / (rx ** 2).sum(0)
    if JACK:                                         # CR3: leave-one-NCB-out jackknife SE
        ests = []
        for g in np.unique(ui):
            keep = ui != g
            Zk = Zw[keep]; Bk = B[keep]
            ck, *_ = np.linalg.lstsq(Zk, Bk, rcond=None); Rk = Bk - Zk @ ck
            ests.append((Rk[:, 1:] * Rk[:, [0]]).sum(0) / (Rk[:, 1:] ** 2).sum(0))
        ests = np.array(ests); G_ = len(ests)
        se = np.sqrt((G_ - 1) / G_ * ((ests - ests.mean(0)) ** 2).sum(0))
    return b / se                                    # studentised statistic

t0 = time.time(); ps = []
for _ in range(reps):
    alpha = rng.normal(0, 0.3, len(units)); gamma = np.cumsum(rng.normal(0, 0.08, len(labels)))
    N = rng.binomial(C, 0.6); ui, ti = np.nonzero(N); w = N[ui, ti].astype(float)
    noise = rng.normal(0, su, len(ui)) + rng.normal(0, 0.7, len(ui)) / np.sqrt(w)
    if mode == "dose":
        y = alpha[ui] + gamma[ti] + beta * X[ui, ti] + noise
        perms = [np.arange(len(units))] + [rng.permutation(len(units)) for _ in range(NPERM)]
        xs = np.column_stack([X[p][ui, ti] for p in perms])
        b = fwl(ui, ti, y, w, xs)
        ps.append((1 + (np.abs(b[1:]) >= abs(b[0])).sum()) / (1 + NPERM))
    else:
        coh = np.array([COH[u] for u in units])
        y = alpha[ui] + gamma[ti] + beta * (ti >= coh[ui]) + noise
        ps.append(Panel(ui, ti, y, w, len(units), len(labels)).ri(coh, 99, rng, studentize=False)[1])
out = dict(controls=WITH_CTRL, jackknife=JACK, mode=mode, beta=beta, sigma_u=su, reps=reps, n_units=len(units), power=float(np.mean(np.array(ps) <= 0.05)), seconds=round(time.time()-t0, 1))
open("power/power_sensitivity.jsonl", "a").write(json.dumps(out) + "\n"); print(out)
