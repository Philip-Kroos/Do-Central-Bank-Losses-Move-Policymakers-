"""Build long-format inputs for run_exposure.py from data/raw (stage 2a)."""
import pandas as pd
from code.exposure import ecb_inputs as ei
R, D = "data/raw/", "data/derived/"
H1, W1 = ei.programme(R + "PSPP_breakdown_history.csv", "PSPP")
H2, W2 = ei.programme(R + "PEPP_public_sector_securities_breakdown_history.csv", "PEPP")
pd.concat([H1, H2]).to_csv(D + "holdings.csv", index=False)
pd.concat([W1, W2]).to_csv(D + "wam.csv", index=False)
ei.irs_yields(R + "irs_10y_monthly.csv").to_csv(D + "yields.csv", index=False)
ei.ea_curve(R + "yc_aaa_daily.csv").to_csv(D + "ea_curve.csv", index=False)
ei.policy_rates(R + "key_rates_daily.csv").to_csv(D + "policy_rates.csv", index=False)
k = pd.read_csv("data/hand/capital_key_eurosystem.csv")
k.loc[k.valid_from == "2024-01", "valid_from"] = "2014-01"      # APPROXIMATION flagged in file notes
k[["ncb", "valid_from", "valid_to", "key_share"]].to_csv(D + "capital_key.csv", index=False)
print("inputs written")
