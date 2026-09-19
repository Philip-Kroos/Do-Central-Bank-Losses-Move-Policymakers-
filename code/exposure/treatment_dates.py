"""Derive staggered treatment timing from hand-collected NCB results (data/hand/ncb_results_v0.csv).

Three pre-specified definitions (design_pap_v1 §3.1):
  gross : first FY with a pre-provision loss (column gross_loss == 1; amounts optional)
  net   : first FY with a negative net result after provisions (loss hits equity / carried forward);
          losses flagged net_loss_technical == 1 (e.g. deferred-tax effects) are excluded
  remit : first FY with a zero transfer to the state
Treatment switches on in the half-year AFTER publication of that FY's accounts. If the
publication date is missing, the half-year after 31 March of FY+1 is used and flagged.
Exit: first later FY with a positive net result.
Left-censoring is flagged when the condition already holds in the first FY collected;
such NCBs need earlier years before they can enter the estimation sample.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

ASSUMED_PUB = "03-31"


def half_year(ts: pd.Timestamp) -> str:
    return f"{ts.year}H{1 if ts.month <= 6 else 2}"


def next_half_year(label: str) -> str:
    y, h = int(label[:4]), int(label[-1])
    return f"{y}H2" if h == 1 else f"{y + 1}H1"


def _first(df: pd.DataFrame, mask: pd.Series):
    sub = df[mask].sort_values("fy")
    return None if sub.empty else sub.iloc[0]


def derive(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ncb, g in df.groupby("ncb"):
        g = g.sort_values("fy")
        defs = {
            "gross": g["gross_loss"] == 1,
            "net": (g["net_result_eur_m"] < 0) & (g.get("net_loss_technical", 0) != 1),
            "remit": g["transfer_to_state_eur_m"] == 0,
        }
        rec = {"ncb": ncb, "fy_covered": f"{g.fy.min()}-{g.fy.max()}"}
        for name, mask in defs.items():
            first = _first(g, mask.fillna(False))
            if first is None:
                rec[f"{name}_fy"] = rec[f"{name}_on"] = rec[f"{name}_pub_assumed"] = None
                rec[f"{name}_left_censored"] = None
                continue
            pub = first["publication_date"]
            assumed = pd.isna(pub)
            ts = pd.Timestamp(f"{int(first.fy) + 1}-{ASSUMED_PUB}") if assumed else pd.Timestamp(pub)
            rec[f"{name}_fy"] = int(first.fy)
            rec[f"{name}_on"] = next_half_year(half_year(ts))
            rec[f"{name}_pub_assumed"] = bool(assumed)
            # left-censoring: condition already holds in the first FY we have data for
            rec[f"{name}_left_censored"] = bool(int(first.fy) == int(g.fy.min()))
        # exit from net-loss region
        exit_row = None
        if rec.get("net_fy"):
            exit_row = _first(g, (g.fy > rec["net_fy"]) & (g["net_result_eur_m"] > 0))
        rec["net_exit_fy"] = None if exit_row is None else int(exit_row.fy)
        rows.append(rec)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/hand/ncb_results_v0.csv")
    out = derive(pd.read_csv(src))
    print(out.to_string(index=False))
    out.to_csv(src.parent / "treatment_dates_v0.csv", index=False)
