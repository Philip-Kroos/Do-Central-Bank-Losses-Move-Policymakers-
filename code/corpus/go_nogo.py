"""Pre-registered go/no-go rule (design_pap_v1 §4). Uses COUNTS ONLY, never positions.

Input: passage-level table with columns ncb, date, and boolean topic flags
       (prefilter flags for an upper bound; classifier topic labels for the binding count).
Rule, window 2022H1-2026H1 on the full NCB x half-year grid (zeros included):
  1. Y1 primary          if mean Y1 passages per NCB-half-year >= 1 and >= 12 NCBs have any Y1 passage
  2. pooled P&L index    else if the same holds for passages flagged Y1 or Y3 (or rate stance, if supplied)
  3. stop speech design  otherwise (fallback: NCB action design)
"""
from __future__ import annotations
import pandas as pd

WINDOW = ("2022H1", "2026H1")
MIN_MEAN, MIN_NCBS = 1.0, 12


def half_year_label(d: pd.Series) -> pd.Series:
    d = pd.to_datetime(d)
    return d.dt.year.astype(str) + "H" + ((d.dt.month > 6) + 1).astype(str)


def _grid(ncbs, start=WINDOW[0], end=WINDOW[1]):
    labels, y, h = [], int(start[:4]), int(start[-1])
    while f"{y}H{h}" <= end:
        labels.append(f"{y}H{h}")
        y, h = (y, 2) if h == 1 else (y + 1, 1)
    return pd.MultiIndex.from_product([sorted(ncbs), labels], names=["ncb", "hy"])


def cell_counts(df: pd.DataFrame, flag_cols: list[str], ncbs) -> pd.Series:
    d = df.assign(hy=half_year_label(df["date"]))
    d = d[(d.hy >= WINDOW[0]) & (d.hy <= WINDOW[1])]
    hit = d[flag_cols].any(axis=1)
    counts = d[hit].groupby(["ncb", "hy"]).size()
    return counts.reindex(_grid(ncbs), fill_value=0)


def decide(df: pd.DataFrame, ncbs, y1="Y1_reserves", pooled=("Y1_reserves", "Y3_balance_sheet")) -> dict:
    out = {}
    for name, cols in (("Y1", [y1]), ("pooled", [c for c in pooled if c in df.columns])):
        c = cell_counts(df, cols, ncbs)
        per_ncb = c.groupby(level="ncb").sum()
        out[name] = dict(mean_per_cell=float(c.mean()), ncbs_with_any=int((per_ncb > 0).sum()),
                         cells=int(len(c)), passes=bool(c.mean() >= MIN_MEAN and (per_ncb > 0).sum() >= MIN_NCBS))
    out["decision"] = ("Y1_primary" if out["Y1"]["passes"]
                       else "pooled_index" if out["pooled"]["passes"] else "stop_speech_design")
    return out
