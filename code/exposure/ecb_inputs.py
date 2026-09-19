"""Convert raw ECB downloads into the long-format schemas of own_yield.SCHEMAS.

Raw files (data/raw/): PSPP_breakdown_history.csv, PEPP_public_sector_securities_breakdown_history.csv
(block-structured wide CSVs), irs_10y_monthly.csv (IRS dataset), yc_aaa_daily.csv (YC dataset),
key_rates_daily.csv (FM key rates). Holdings are cumulative net purchases (acquisition cost minus
redeemed nominal), the ECB's own stock concept for these tables.
"""
from __future__ import annotations
import csv
import re
import pandas as pd

NAME2ISO = {"Austria": "AT", "Belgium": "BE", "Cyprus": "CY", "Germany": "DE", "Estonia": "EE", "Spain": "ES",
            "Finland": "FI", "France": "FR", "Greece": "GR", "Ireland": "IE", "Italy": "IT", "Lithuania": "LT",
            "Luxembourg": "LU", "Latvia": "LV", "Malta": "MT", "The Netherlands": "NL", "Netherlands": "NL",
            "Portugal": "PT", "Slovenia": "SI", "Slovakia": "SK", "Croatia": "HR", "Bulgaria": "BG"}


def _blocks(path: str) -> dict[str, pd.DataFrame]:
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    out, i = {}, 0
    while i < len(rows):
        title = rows[i][0].strip()
        if i + 1 < len(rows) and rows[i + 1][0].strip() == "" and sum(bool(x.strip()) for x in rows[i + 1][1:]) > 10:
            header = rows[i + 1]
            body = []
            j = i + 2
            while j < len(rows) and rows[j][0].strip() and sum(bool(x.strip()) for x in rows[j][1:]) > 0:
                body.append(rows[j]); j += 1
            df = pd.DataFrame(body, columns=["name"] + header[1:])
            out[title] = df
            i = j
        else:
            i += 1
    return out


def _month(label: str) -> pd.Timestamp | None:
    label = (label or "").strip()
    if not label:
        return None
    for fmt in ("%d/%m/%Y", "%b-%y"):
        try:
            ts = pd.to_datetime(label, format=fmt)
        except ValueError:
            continue
        if pd.notna(ts):
            return ts.to_period("M").to_timestamp()
    return None


def _long(df: pd.DataFrame, value: str) -> pd.DataFrame:
    m = df.melt(id_vars="name", var_name="label", value_name=value)
    m["month"] = m.label.map(_month)
    m = m.dropna(subset=["month"])
    m["ncb"] = m.name.str.strip().str.lower().map({k.lower(): v for k, v in NAME2ISO.items()})
    m = m.dropna(subset=["ncb"])
    m[value] = pd.to_numeric(m[value].str.replace(",", ""), errors="coerce")
    return m[["month", "ncb", value]]


def programme(path: str, programme: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    b = _blocks(path)
    flow_key = next(k for k in b if "net purchases" in k.lower())
    wam_key = next(k for k in b if k.lower().startswith("wam of") and "eligible" not in k.lower())
    flows = _long(b[flow_key], "net_purchases_eur_m").sort_values(["ncb", "month"])
    flows["holdings_eur_m"] = flows.groupby("ncb").net_purchases_eur_m.cumsum()
    flows["programme"] = programme
    wam = _long(b[wam_key], "wam_years").assign(programme=programme)
    return flows[["month", "ncb", "programme", "holdings_eur_m"]], wam[["month", "ncb", "programme", "wam_years"]]


def irs_yields(path: str) -> pd.DataFrame:
    d = pd.read_csv(path, usecols=["REF_AREA", "TIME_PERIOD", "OBS_VALUE"])
    d = d[d.REF_AREA.str.len() == 2]
    return pd.DataFrame(dict(month=pd.to_datetime(d.TIME_PERIOD).dt.to_period("M").dt.to_timestamp(),
                             country=d.REF_AREA, maturity_years=10.0, yield_pct=d.OBS_VALUE))


def ea_curve(path: str) -> pd.DataFrame:
    d = pd.read_csv(path, usecols=["KEY", "TIME_PERIOD", "OBS_VALUE"])
    d["maturity_years"] = d.KEY.str.extract(r"SR_(\d+)Y")[0].astype(float)
    d["month"] = pd.to_datetime(d.TIME_PERIOD).dt.to_period("M").dt.to_timestamp()
    return d.groupby(["month", "maturity_years"], as_index=False).OBS_VALUE.mean().rename(columns={"OBS_VALUE": "yield_pct"})


def policy_rates(path: str) -> pd.DataFrame:
    d = pd.read_csv(path)
    dfr = next(c for c in d.columns if "FM.D.U2.EUR.4F.KR.DFR.LEV" in c)
    mro = next(c for c in d.columns if "FM.D.U2.EUR.4F.KR.MRR_RT.LEV" in c)
    d["DATE"] = pd.to_datetime(d.DATE)
    d = d.set_index("DATE")[[dfr, mro]].ffill()
    m = d.resample("MS").mean()
    return pd.DataFrame(dict(month=m.index, dfr_pct=m[dfr].values, mro_pct=m[mro].values))
