"""H5 (descriptive): do NCBs change provisioning or distribution policy after their first published net loss?

Output: for each documented NCB, the treatment half-year (net-loss definition) and buffer-strengthening actions
before and after. With 8 to 10 events this is a descriptive exhibit, not a test (PAP v2 §1, H5).
"""
from __future__ import annotations
import pandas as pd
from code.estimate.panel import LABELS, hy

STRENGTHEN = {"strengthen_buffers"}


def build(actions_path="data/hand/ncb_actions.csv", treat_path="data/hand/treatment_dates_v0.csv") -> pd.DataFrame:
    a = pd.read_csv(actions_path, parse_dates=["date"])
    a = a[a.action_type != "external_pressure"].copy()
    a["hy"] = hy(a.date)
    t = pd.read_csv(treat_path).set_index("ncb")
    rows = []
    for ncb, g in a.groupby("ncb"):
        on = t.net_on.get(ncb) if ncb in t.index else None
        idx = LABELS.index(on) if isinstance(on, str) and on in LABELS else None
        for r in g.itertuples():
            pos = LABELS.index(r.hy) if r.hy in LABELS else None
            rows.append(dict(ncb=ncb, hy=r.hy, action_type=r.action_type, direction=r.direction,
                             treated_from=on, after_treatment=None if (idx is None or pos is None) else pos >= idx,
                             strengthening=r.direction in STRENGTHEN))
    return pd.DataFrame(rows)


def summary(df: pd.DataFrame) -> dict:
    treated = df[df.after_treatment.notna()]
    return dict(n_actions=int(len(df)), n_ncbs=int(df.ncb.nunique()),
                strengthening_after=int(((treated.after_treatment == True) & treated.strengthening).sum()),
                strengthening_before=int(((treated.after_treatment == False) & treated.strengthening).sum()),
                actions_in_never_treated=int(df.after_treatment.isna().sum()),
                note="descriptive only; 8-10 events, no inference")
