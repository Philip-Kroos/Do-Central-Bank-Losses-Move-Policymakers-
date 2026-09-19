"""Master script, stage 2: public ECB inputs -> NCB carry exposure (monthly and half-yearly) + validation.

usage:
python3 run_exposure.py --holdings H.csv --wam W.csv --yields Y.csv --capital-key K.csv --rates R.csv \
    [--ea-curve EA.csv] [--method net_flow|ladder] [--pepp-share 0.889] [--maturity-mult 1.0] [--out output/]
All inputs are long-format CSVs matching code/exposure/own_yield.SCHEMAS (see docs/data_download.md).
"""
import argparse, json, pathlib
import pandas as pd
from code.exposure.own_yield import Config, validate, portfolio_yield, exposure, to_half_years
from code.exposure.validate_exposure import compare

ap = argparse.ArgumentParser()
for a in ("holdings", "wam", "yields", "capital-key", "rates"):
    ap.add_argument(f"--{a}", required=True)
ap.add_argument("--ea-curve"); ap.add_argument("--method", default="net_flow")
ap.add_argument("--pepp-share", type=float, default=8 / 9); ap.add_argument("--maturity-mult", type=float, default=1.0)
ap.add_argument("--out", default="output")
a = ap.parse_args()

H = validate(pd.read_csv(a.holdings), "holdings"); W = validate(pd.read_csv(a.wam), "wam")
Y = validate(pd.read_csv(a.yields), "yields"); K = validate(pd.read_csv(a.capital_key), "capital_key")
R = validate(pd.read_csv(a.rates), "policy_rates")
EA = pd.read_csv(a.ea_curve).assign(month=lambda d: pd.to_datetime(d.month).dt.to_period("M").dt.to_timestamp()) if a.ea_curve else None

cfg = Config(ncb_share={"PSPP": 8 / 9, "PEPP": a.pepp_share}, maturity_multiplier=a.maturity_mult, redemption_method=a.method)
port = portfolio_yield(H, W, Y, cfg, EA)
expo = exposure(port, R, K)
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
tag = f"{a.method}_pepp{a.pepp_share:.3f}_mm{a.maturity_mult:g}"
port.to_csv(out / f"portfolio_monthly_{tag}.csv", index=False)
expo.to_csv(out / f"exposure_monthly_{tag}.csv", index=False)
to_half_years(expo).to_csv(out / f"exposure_halfyear_{tag}.csv", index=False)

annual = (expo.assign(year=expo.month.dt.year).groupby(["ncb", "year"], as_index=False)
              .carry_per_keypp_eur_m_pa.mean())
val = compare(annual, pd.read_csv("data/hand/bdf_nii_benchmark.csv"))
report = dict(config=tag, n_ncb=int(expo.ncb.nunique()), months=[str(expo.month.min().date()), str(expo.month.max().date())],
              share_approximated_yields=float(port.yield_method.ne("interpolated").mean()), validation=val)
json.dump(report, open(out / f"exposure_report_{tag}.json", "w"), indent=2, default=str)
print(json.dumps(report, indent=2, default=str))
