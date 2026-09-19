import sys, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from code.estimate.imputation import att, ri_pvalue

def _panel(beta, seed=0, noise=0.05):
    rng = np.random.default_rng(seed)
    rows = []
    coh = {"A": 5, "B": 7, "C": np.inf, "D": np.inf, "E": 6}
    for u, c in coh.items():
        a = rng.normal()
        for t in range(10):
            D = int(t >= c)
            rows.append(dict(unit=u, t=t, D=D, w=1 + rng.integers(0, 3), y=a + 0.1 * t + beta * D + rng.normal(0, noise)))
    return pd.DataFrame(rows), coh

def test_att_recovers_effect():
    df, _ = _panel(0.5, noise=0.005)
    assert abs(att(df) - 0.5) < 0.02

def test_att_zero_without_effect_and_ri_runs():
    df, coh = _panel(0.0, seed=1, noise=0.3)
    base, p, null = ri_pvalue(df.drop(columns="D"), coh, {t: t for t in range(10)}, n_perm=99, rng=np.random.default_rng(2))
    assert abs(base) < 0.5 and 0 < p <= 1 and len(null) > 50

def test_fast_matches_pandas_version():
    from code.estimate.fast_impute import Panel
    df, coh = _panel(0.3, seed=4, noise=0.2)
    units = sorted(df.unit.unique()); ui = df.unit.map({u: i for i, u in enumerate(units)})
    p = Panel(ui, df.t, df.y, df.w, len(units), 10)
    cvec = [coh[u] for u in units]
    df2 = df.assign(D=(df.t >= df.unit.map(coh)).astype(int))
    df2 = df2[df2.t != df2.unit.map(coh) - 1]
    assert abs(p.att(cvec) - att(df2)) < 1e-10
    assert p.jackknife_se(cvec) > 0
