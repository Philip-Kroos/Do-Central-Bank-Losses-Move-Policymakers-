"""PAP v2.2 collinearity rule, evaluated OUTCOME-BLIND on the cell structure implied by keyword-matched passages
(weights = prefilter counts; no positions). The same rule is re-evaluated on classified topic passages in the real run."""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from code.estimate import panel as pn

key = pd.read_csv("data/derived/classify_key.csv", parse_dates=["date"])
key = key[key.role == "ncb_head"].copy()
key["hy"] = pn.hy(key.date); key["gov"] = key.author.map(pn.gov_id)
cells = key.groupby(["ncb", "gov", "hy"]).size().rename("n").reset_index()
cells = cells[cells.hy.isin(pn.LABELS)]
E = pn.exposure_panel(pd.read_csv("output/exposure/exposure_halfyear_net_flow_pepp0.889_mm1.csv"))
S = pn.spread_panel(pd.read_csv("data/derived/yields.csv"))
rates = pd.read_csv("data/derived/policy_rates.csv", parse_dates=["month"])
PS = pn.pre_period_x_rate(S, "spread_de", rates)
PD = pn.pre_period_x_rate(pd.read_csv("data/derived/debt_ratio_hy.csv"), "debt_ratio", rates)
d = cells.merge(E, on=["ncb", "hy"]).merge(PS, on=["ncb", "hy"], how="left").merge(PD, on=["ncb", "hy"], how="left")
d = d.dropna(subset=["E", "pre_spread_de_x_dfr", "pre_debt_ratio_x_dfr"])
fe = pn.residual_variance_share(d)
res = dict(cells=int(len(d)), ncbs=int(d.ncb.nunique()), share_after_fe=fe)
for name, ctrls, core in [("spread_x_dfr", ("pre_spread_de_x_dfr",), False),
                          ("debt_x_dfr", ("pre_debt_ratio_x_dfr",), False),
                          ("main_v2_2_spread_and_debt", ("pre_spread_de_x_dfr", "pre_debt_ratio_x_dfr"), False),
                          ("main_plus_core_x_hy", ("pre_spread_de_x_dfr", "pre_debt_ratio_x_dfr"), True)]:
    s = pn.residual_variance_share(d, controls=ctrls, extra_fe="core_x_hy" if core else None)
    res[name] = dict(share=s, ratio_to_fe=s / fe)
res["rule_triggered_main"] = bool(res["main_v2_2_spread_and_debt"]["ratio_to_fe"] < 0.25)
# raw within correlation between exposure and debt x DFR after FE (descriptive)
govs = sorted(d.gov.unique()); gi = d.gov.map({g: i for i, g in enumerate(govs)}).to_numpy(); ti = d.hy.map({l: i for i, l in enumerate(pn.LABELS)}).to_numpy()
Z = pn.fe_design(gi, ti, len(govs), len(pn.LABELS)); w = np.sqrt(d.n.to_numpy(float))
def res_(v):
    c, *_ = np.linalg.lstsq(Z * w[:, None], v * w, rcond=None); return v * w - (Z * w[:, None]) @ c
res["within_corr_E_debt_x_dfr"] = float(np.corrcoef(res_(d.E.to_numpy()), res_(d.pre_debt_ratio_x_dfr.to_numpy()))[0, 1])
json.dump(res, open("output/collinearity_rule_v2_2_outcome_blind.json", "w"), indent=2)
print(json.dumps(res, indent=2))
