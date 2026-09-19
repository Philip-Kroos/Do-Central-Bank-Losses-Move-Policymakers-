import sys, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from code.validation.analyse_validation import alphas, recall

def _coder(ids, topic, pos):
    return pd.DataFrame(dict(topic=topic, position=pos), index=pd.Index(ids, name="id"))

def test_perfect_agreement_and_noise():
    rng = np.random.default_rng(0)
    ids = [f"V{i:03d}" for i in range(100)]
    t = rng.integers(0, 2, 100); p = np.where(t == 1, rng.integers(-1, 2, 100), np.nan)
    a = _coder(ids, t, p)
    r = alphas(a, a.copy())
    assert abs(r["alpha_topic"] - 1) < 1e-9 and abs(r["alpha_position"] - 1) < 1e-9
    b = _coder(ids, rng.integers(0, 2, 100), rng.integers(-1, 2, 100).astype(float))
    r2 = alphas(a, b)
    assert abs(r2["alpha_topic"]) < 0.3

def test_recall_weighting():
    key = pd.DataFrame(dict(id=[f"V{i}" for i in range(20)], stratum=["head_big_pre"] * 10 + ["nonhit"] * 10))
    coder = _coder(key.id, [1] * 10 + [1] + [0] * 9, [0] * 20)
    res = recall(coder, key, pop_nonhit=26567)
    # 10% topic among ~26.6k non-hits dwarfs 1,991 hits -> recall far below 0.8
    assert res["est_recall"] < 0.5 and res["expand_prefilter"]
