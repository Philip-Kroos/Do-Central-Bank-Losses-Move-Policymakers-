"""End-to-end planted-effect test on SYNTHETIC positions: the panel + dose estimator must recover the sign
of a planted negative exposure effect and reject; with no effect it must not systematically reject."""
import sys, pathlib
import numpy as np, pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
pytestmark = pytest.mark.skipif(not (ROOT / "data/derived/classify_key.csv").exists(), reason="derived data missing")
from code.estimate import panel as pn

def _heads(plant, seed):
    key = pd.read_csv(ROOT / "data/derived/classify_key.csv", parse_dates=["date"])
    key["role_group"] = np.where(key.role == "ncb_head", "heads", "ecb")
    E = pn.exposure_panel(pd.read_csv(ROOT / "output/exposure/exposure_halfyear_net_flow_pepp0.889_mm1.csv"))
    k = key.assign(hy=pn.hy(key.date)).merge(E, on=["ncb", "hy"], how="left")
    rng = np.random.default_rng(seed)
    z = plant * k.E.fillna(0).to_numpy() + rng.normal(0, 1, len(k))
    pos = np.where(z < -0.6, -1, np.where(z > 0.6, 1, 0)).astype(float)
    res = pd.DataFrame(dict(id=k.id, valid=True, topic=True, position=pos))
    Y = pn.outcome_panel(res, key)
    return Y[Y.role_group == "heads"].merge(E, on=["ncb", "hy"], how="left")

def test_planted_dose_effect_recovered():
    r = pn.dose_estimate(_heads(-0.8, 3), n_perm=199, rng=np.random.default_rng(0))
    assert r["beta"] < 0 and r["p_ri"] < 0.05

def test_no_effect_no_rejection():
    r = pn.dose_estimate(_heads(0.0, 4), n_perm=199, rng=np.random.default_rng(1))
    assert r["p_ri"] > 0.05
