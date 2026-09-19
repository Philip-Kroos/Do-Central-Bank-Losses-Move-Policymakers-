"""NCB-specific carry exposure from own (non-pooled) sovereign QE portfolios.

Mechanism (Banque de France Bulletin 260/6; Decision (EU) 2016/2248): sovereign bonds bought
since 2015 are neither risk- nor income-pooled; each NCB funds them with pooled deposits and
pays the reference rate (MRO until 31.12.2024, DFR from 1.1.2025) on the pooled net asset.
Hence the NCB-specific component of net interest income is

    carry_i,t = S_i,t * (s_i,t - ref_t)            [EUR m per year]

with S the NCB's own holdings and s their average purchase yield. Everything pooled is common
per unit of capital key and is absorbed by time fixed effects.

Public inputs (ECB website): PSPP holdings and WAM by jurisdiction (monthly), PEPP
jurisdictional composition and WAM (monthly, with history), country yields, capital key,
key ECB rates. Exact file layouts are [UNVERIFIED]; inputs are validated against the schemas
below and every approximation is flagged in the output.

ASSUMPTIONS (each has a switch for sensitivity analysis)
A1 NCB-own share of a jurisdiction's PSPP government holdings = 8/9 (80% NCB vs 10% ECB of
   total purchases; the remaining 10% supranationals are risk-shared). PEPP share = parameter.
A2 Purchase maturity = holdings WAM x multiplier (default 1.0).
A3 Redemptions: 'net_flow' (stock yield changes only with positive net flows) or 'ladder'
   (uniform maturity ladder: monthly redemptions = stock / (12 * WAM), replaced at current yield).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

REF_SWITCH = pd.Timestamp("2025-01-01")

SCHEMAS = {
    "holdings": ["month", "ncb", "programme", "holdings_eur_m"],
    "wam": ["month", "ncb", "programme", "wam_years"],
    "yields": ["month", "country", "maturity_years", "yield_pct"],
    "capital_key": ["ncb", "valid_from", "valid_to", "key_share"],
    "policy_rates": ["month", "mro_pct", "dfr_pct"],
}


@dataclass
class Config:
    ncb_share: dict = None               # programme -> NCB-own share of jurisdiction holdings
    maturity_multiplier: float = 1.0
    redemption_method: str = "net_flow"  # or "ladder"

    def __post_init__(self):
        if self.ncb_share is None:
            self.ncb_share = {"PSPP": 8 / 9, "PEPP": 8 / 9}   # PEPP split [UNVERIFIED] -> sensitivity


def validate(df: pd.DataFrame, name: str) -> pd.DataFrame:
    missing = [c for c in SCHEMAS[name] if c not in df.columns]
    if missing:
        raise KeyError(f"{name}: missing columns {missing}; found {list(df.columns)}")
    out = df.copy()
    for c in ("month", "valid_from", "valid_to"):
        if c in out.columns:
            out[c] = pd.to_datetime(out[c]).dt.to_period("M").dt.to_timestamp()
    return out


def interpolate_yield(yields: pd.DataFrame, country: str, month: pd.Timestamp, maturity: float,
                      ea_curve: pd.DataFrame | None = None) -> tuple[float, str]:
    """Linear interpolation across maturities; flat extrapolation at the ends.
    Fallback with a single country maturity: shift it by the euro area curve slope."""
    sub = yields[(yields.country == country) & (yields.month == month)].sort_values("maturity_years")
    if sub.empty:
        return np.nan, "missing"
    if len(sub) >= 2:
        return float(np.interp(maturity, sub.maturity_years, sub.yield_pct)), "interpolated"
    m0, y0 = float(sub.maturity_years.iloc[0]), float(sub.yield_pct.iloc[0])
    if ea_curve is not None:
        ea = ea_curve[ea_curve.month == month].sort_values("maturity_years")
        if len(ea) >= 2:
            slope_adj = np.interp(maturity, ea.maturity_years, ea.yield_pct) - np.interp(m0, ea.maturity_years, ea.yield_pct)
            return y0 + float(slope_adj), "single_maturity_ea_slope"
    return y0, "single_maturity_level_only"


def portfolio_yield(holdings: pd.DataFrame, wam: pd.DataFrame, yields: pd.DataFrame,
                    cfg: Config = Config(), ea_curve: pd.DataFrame | None = None) -> pd.DataFrame:
    """Monthly NCB-own stock and average yield per NCB x programme."""
    h = holdings.merge(wam, on=["month", "ncb", "programme"], how="left").sort_values(["ncb", "programme", "month"])
    rows = []
    for (ncb, prog), g in h.groupby(["ncb", "programme"], sort=False):
        share = cfg.ncb_share.get(prog, 1.0)
        stock_prev, s_prev = 0.0, np.nan
        for r in g.itertuples():
            stock = share * float(r.holdings_eur_m)
            wam_y = float(r.wam_years) if pd.notna(r.wam_years) else np.nan
            y_new, method = interpolate_yield(yields, ncb, r.month, wam_y * cfg.maturity_multiplier, ea_curve) \
                if pd.notna(wam_y) else (np.nan, "missing_wam")
            flow = stock - stock_prev
            if cfg.redemption_method == "ladder" and stock_prev > 0 and pd.notna(wam_y) and wam_y > 0:
                redemptions = min(stock_prev, stock_prev / (12.0 * wam_y))
            else:
                redemptions = 0.0
            gross = max(flow + redemptions, 0.0)
            retained = max(stock_prev - redemptions, 0.0) if flow + redemptions >= 0 else stock
            if stock <= 0:
                s = np.nan
            elif np.isnan(s_prev) or retained == 0:
                s = y_new
            elif gross > 0 and pd.notna(y_new):
                s = (s_prev * retained + y_new * gross) / (retained + gross)
            else:
                s = s_prev                        # runoff without replacement: pro-rata, yield unchanged
            rows.append(dict(month=r.month, ncb=ncb, programme=prog, stock_eur_m=stock,
                             gross_purchases_eur_m=gross, purchase_yield_pct=y_new,
                             portfolio_yield_pct=s, yield_method=method))
            stock_prev, s_prev = stock, s
    return pd.DataFrame(rows)


def reference_rate(policy_rates: pd.DataFrame) -> pd.Series:
    pr = policy_rates.set_index("month").sort_index()
    return pd.Series(np.where(pr.index < REF_SWITCH, pr.mro_pct, pr.dfr_pct), index=pr.index, name="ref_pct")


def key_at(capital_key: pd.DataFrame, ncb: str, month: pd.Timestamp) -> float:
    k = capital_key[(capital_key.ncb == ncb) & (capital_key.valid_from <= month) &
                    ((capital_key.valid_to.isna()) | (capital_key.valid_to >= month))]
    if len(k) != 1:
        raise ValueError(f"capital key for {ncb} {month:%Y-%m}: {len(k)} matching rows")
    return float(k.key_share.iloc[0])


def exposure(port: pd.DataFrame, policy_rates: pd.DataFrame, capital_key: pd.DataFrame) -> pd.DataFrame:
    """NCB x month carry exposure, per unit of key, and cross-sectionally demeaned version."""
    agg = (port.dropna(subset=["portfolio_yield_pct"])
               .assign(w=lambda d: d.stock_eur_m * d.portfolio_yield_pct)
               .groupby(["ncb", "month"], as_index=False)
               .agg(stock_eur_m=("stock_eur_m", "sum"), w=("w", "sum"),
                    approx_share=("yield_method", lambda x: float((x != "interpolated").mean()))))
    agg["portfolio_yield_pct"] = agg.w / agg.stock_eur_m
    ref = reference_rate(policy_rates)
    agg["ref_pct"] = agg.month.map(ref)
    agg["carry_eur_m_pa"] = agg.stock_eur_m * (agg.portfolio_yield_pct - agg.ref_pct) / 100.0
    agg["key_share"] = [key_at(capital_key, n, m) for n, m in zip(agg.ncb, agg.month)]
    agg["carry_per_keypp_eur_m_pa"] = agg.carry_eur_m_pa / (100.0 * agg.key_share)
    agg["carry_per_keypp_demeaned"] = agg.carry_per_keypp_eur_m_pa - agg.groupby("month").carry_per_keypp_eur_m_pa.transform("mean")
    return agg.drop(columns="w")


def to_half_years(expo: pd.DataFrame) -> pd.DataFrame:
    e = expo.assign(hy=expo.month.dt.year.astype(str) + "H" + ((expo.month.dt.month > 6) + 1).astype(str))
    cols = ["stock_eur_m", "portfolio_yield_pct", "ref_pct", "carry_eur_m_pa", "carry_per_keypp_eur_m_pa",
            "carry_per_keypp_demeaned", "approx_share"]
    return e.groupby(["ncb", "hy"], as_index=False)[cols].mean()
