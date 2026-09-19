"""H4 is only valid if attributes cover enough of the classification universe (PAP v2 §5, H4)."""
import sys, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from code.estimate.panel import gov_id

def coverage(col):
    k = pd.read_csv(ROOT / "data/derived/classify_key.csv")
    k = k[k.role == "ncb_head"].assign(gov=lambda d: d.author.map(gov_id))
    r = pd.read_csv(ROOT / "data/hand/governor_roster.csv").assign(gov=lambda d: d.speaker_name.map(gov_id))
    m = r.dropna(subset=[col]).groupby("gov")[col].max()
    return k.gov.isin(m.index).mean()

def test_attribute_coverage_is_reported_not_assumed():
    cov = {c: coverage(c) for c in ("former_minister", "reappointable")}
    # H4 requires >= 80% of passages covered; currently it is not met and must be disclosed, not silently estimated
    assert all(0 <= v <= 1 for v in cov.values())
    assert cov["former_minister"] < 0.8 or cov["reappointable"] < 0.8, "coverage reached: update this test and enable H4"

def test_ncb_actions_summary():
    from code.estimate.ncb_actions import build, summary
    s = summary(build(str(ROOT / "data/hand/ncb_actions.csv"), str(ROOT / "data/hand/treatment_dates_v0.csv")))
    assert s["n_actions"] >= 6 and s["n_ncbs"] >= 5
