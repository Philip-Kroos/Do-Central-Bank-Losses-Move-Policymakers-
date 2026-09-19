import sys, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from code.estimate.full_report import romano_wolf, Linear

def test_romano_wolf_monotone_and_bounds():
    rng = np.random.default_rng(0)
    null = rng.normal(size=(999, 3))
    p = romano_wolf(np.array([4.0, 2.0, 0.1]), null)
    assert p[0] <= p[1] <= p[2] and p[0] < 0.01 and p[2] > 0.5

def test_linear_recovers_coefficient():
    rng = np.random.default_rng(1)
    rows = []
    for n_i, ncb in enumerate(list("ABCDEFGHIJ")):
        a = rng.normal()
        for t in range(12):
            x = rng.normal()
            rows.append(dict(ncb=ncb, gov=ncb, hy=f"{2016 + t // 2}H{t % 2 + 1}", n=5, x=x, y=a + 0.05 * t - 0.5 * x + rng.normal(0, 0.05)))
    d = pd.DataFrame(rows)
    L = Linear(d)
    b, t, V = L.stat(d.x.to_numpy()[:, None])
    assert abs(b[0] + 0.5) < 0.03 and t[0] < -10
