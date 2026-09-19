"""End-to-end smoke test on SYNTHETIC inputs (no real data; numbers are meaningless)."""
import json, subprocess, sys, pathlib
import numpy as np
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]

def test_run_exposure_end_to_end(tmp_path):
    months = pd.date_range("2022-01-01", "2025-06-01", freq="MS")
    ncbs = {"DE": 0.27, "FR": 0.20, "IT": 0.16, "ES": 0.12}
    rng = np.random.default_rng(0)
    H, W, Y = [], [], []
    for n in ncbs:
        stock = 100.0
        for m in months:
            stock *= 0.99
            H.append(dict(month=m.strftime("%Y-%m"), ncb=n, programme="PSPP", holdings_eur_m=stock))
            W.append(dict(month=m.strftime("%Y-%m"), ncb=n, programme="PSPP", wam_years=7.0))
            for mat in (2, 10):
                Y.append(dict(month=m.strftime("%Y-%m"), country=n, maturity_years=mat, yield_pct=float(rng.uniform(0, 3))))
    K = [dict(ncb=n, valid_from="2019-01", valid_to="", key_share=k) for n, k in ncbs.items()]
    R = [dict(month=m.strftime("%Y-%m"), mro_pct=2.0, dfr_pct=1.9) for m in months]
    paths = {}
    for name, rows in dict(holdings=H, wam=W, yields=Y, key=K, rates=R).items():
        p = tmp_path / f"{name}.csv"; pd.DataFrame(rows).to_csv(p, index=False); paths[name] = str(p)
    cmd = [sys.executable, "run_exposure.py", "--holdings", paths["holdings"], "--wam", paths["wam"], "--yields", paths["yields"],
           "--capital-key", paths["key"], "--rates", paths["rates"], "--out", str(tmp_path / "out"), "--method", "ladder"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rep = json.loads(r.stdout)
    assert rep["n_ncb"] == 4 and rep["validation"]["n"] == 8
    assert (tmp_path / "out").glob("exposure_halfyear_*.csv")
