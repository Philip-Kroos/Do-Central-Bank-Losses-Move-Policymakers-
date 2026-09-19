"""Stage 4: estimation per PAP v2/v2.1.
--synthetic : DRY RUN with random positions (seeded) to test the pipeline end-to-end. Writes only to output/dryrun.
Real runs require --results <classification CSVs> and a frozen hash file for them (docs/classification_freeze.sha256)."""
import argparse, glob, hashlib, json, pathlib, sys
import numpy as np, pandas as pd
from code.estimate import panel as pn

ap = argparse.ArgumentParser()
ap.add_argument("--synthetic", action="store_true"); ap.add_argument("--results", nargs="*"); ap.add_argument("--perm", type=int, default=999)
a = ap.parse_args()
key = pd.read_csv("data/derived/classify_key.csv", parse_dates=["date"])
key["role_group"] = np.where(key.role == "ncb_head", "heads", "ecb")
if a.synthetic:
    rng = np.random.default_rng(1)
    res = pd.DataFrame(dict(id=key.id, valid=True, topic=rng.random(len(key)) < 0.7, position=rng.integers(-1, 2, len(key)).astype(float)))
    outdir = pathlib.Path("output/dryrun")
else:
    frozen = pathlib.Path("docs/classification_freeze.sha256")
    if not frozen.exists():
        sys.exit("Refusing real run: classification results are not frozen (docs/classification_freeze.sha256 missing).")
    recorded = dict(line.split()[::-1] for line in frozen.read_text().splitlines() if line.strip())
    for f in a.results:
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()
        if recorded.get(f) != h:
            sys.exit(f"Refusing real run: {f} does not match frozen hash.")
    res = pd.concat([pd.read_csv(f) for f in a.results])
    res["valid"] = res.valid.astype(str).str.lower() == "true"; res["topic"] = res.topic.astype(str).str.lower() == "true"
    outdir = pathlib.Path("output/estimation")
outdir.mkdir(parents=True, exist_ok=True)

Y = pn.outcome_panel(res, key)
E = pn.exposure_panel(pd.read_csv("output/exposure/exposure_halfyear_net_flow_pepp0.889_mm1.csv"))
S = pn.spread_panel(pd.read_csv("data/derived/yields.csv"))
coh = pn.treatment_cohorts(pd.read_csv("data/hand/treatment_dates_v0.csv"))
rates = pd.read_csv("data/derived/policy_rates.csv", parse_dates=["month"])
PS = pn.pre_period_x_rate(S, "spread_de", rates)
heads = Y[Y.role_group == "heads"].merge(E, on=["ncb", "hy"], how="left").merge(S, on=["ncb", "hy"], how="left").merge(PS, on=["ncb", "hy"], how="left")
debt_path = pathlib.Path("data/derived/debt_ratio_hy.csv")                     # ncb, hy, debt_ratio (pending download)
main_controls = ["pre_spread_de_x_dfr"]
if debt_path.exists():
    PD = pn.pre_period_x_rate(pd.read_csv(debt_path), "debt_ratio", rates)
    heads = heads.merge(PD, on=["ncb", "hy"], how="left"); main_controls.append("pre_debt_ratio_x_dfr")
rng = np.random.default_rng(20260911)
report = dict(mode="SYNTHETIC DRY RUN - NOT RESULTS" if a.synthetic else "REAL",
              panel=dict(cells=int(len(heads)), governors=int(heads.gov.nunique()), ncbs=int(heads.ncb.nunique()), passages=int(heads.n.sum())))
fe_share = pn.residual_variance_share(heads)
ctrl_share = pn.residual_variance_share(heads, controls=tuple(main_controls))
report["collinearity_rule_v2_2"] = dict(share_after_fe=fe_share, share_after_fe_and_controls=ctrl_share,
                                        ratio=ctrl_share / fe_share, rule_triggered=bool(ctrl_share / fe_share < 0.25),
                                        debt_control_included="pre_debt_ratio_x_dfr" in main_controls)
report["H3_dose_main"] = pn.dose_estimate(heads, controls=tuple(main_controls), n_perm=a.perm, rng=rng)
report["H3_R9_core_x_hy"] = pn.dose_estimate(heads, controls=tuple(main_controls), extra_fe="core_x_hy", n_perm=a.perm, rng=rng)
report["H3_R10_contemporaneous_spread"] = pn.dose_estimate(heads, controls=("spread_de",), n_perm=a.perm, rng=rng)
documented = {k: v for k, v in coh["N"].items() if k in {"AT", "BE", "DE", "FR", "NL", "SK", "ES", "FI", "GR", "IE", "IT", "PT", "LU"}}
report["H1_event_N"] = pn.event_estimate(heads, documented, n_perm=a.perm, rng=rng)
report["notes"] = ["HICP and debt/GDP data not yet available: PAP v2.2 requires national HICP and pre-2019-2021 debt ratio x DFR in the main specification. Real runs without them are not valid main estimates."]
json.dump(report, open(outdir / "report.json", "w"), indent=2); print(json.dumps(report, indent=2))
