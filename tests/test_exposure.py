import sys, pathlib
import numpy as np
import pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from code.exposure.own_yield import (Config, interpolate_yield, portfolio_yield, exposure,
                                     reference_rate, key_at, to_half_years, validate)
from code.exposure.validate_exposure import compare

M = lambda s: pd.Timestamp(s)

def curve(country, month, pts):
    return pd.DataFrame([dict(month=M(month), country=country, maturity_years=m, yield_pct=y) for m, y in pts])

def test_interpolation_and_fallbacks():
    y = curve("DE", "2020-01-01", [(2, 0.0), (10, 1.0)])
    assert interpolate_yield(y, "DE", M("2020-01-01"), 6)[0] == pytest.approx(0.5)
    assert interpolate_yield(y, "DE", M("2020-01-01"), 30)[0] == pytest.approx(1.0)       # flat extrapolation
    y1 = curve("IT", "2020-01-01", [(10, 2.0)])
    ea = curve("EA", "2020-01-01", [(2, 0.2), (10, 0.6)])[["month", "maturity_years", "yield_pct"]]
    v, meth = interpolate_yield(y1, "IT", M("2020-01-01"), 2, ea)
    assert v == pytest.approx(1.6) and meth == "single_maturity_ea_slope"
    assert interpolate_yield(y1, "IT", M("2020-01-01"), 2)[1] == "single_maturity_level_only"

def _setup(stocks, yields_by_month, wam=5.0, prog="PSPP"):
    months = [M(f"2020-{i+1:02d}-01") for i in range(len(stocks))]
    h = pd.DataFrame(dict(month=months, ncb="DE", programme=prog, holdings_eur_m=stocks))
    w = pd.DataFrame(dict(month=months, ncb="DE", programme=prog, wam_years=wam))
    y = pd.concat([curve("DE", m, [(1, yv), (30, yv)]) for m, yv in zip(months, yields_by_month)])
    return h, w, y

def test_weighted_average_and_runoff_net_flow():
    h, w, y = _setup([90, 180, 180, 90], [1.0, 3.0, 5.0, 7.0])
    cfg = Config(ncb_share={"PSPP": 1.0})
    p = portfolio_yield(h, w, y, cfg)
    assert p.portfolio_yield_pct.tolist() == pytest.approx([1.0, 2.0, 2.0, 2.0])   # runoff keeps yield

def test_ladder_replaces_redemptions_at_new_yield():
    h, w, y = _setup([120, 120], [1.0, 4.0], wam=1.0)          # redemptions 10/month, replaced at 4%
    p = portfolio_yield(h, w, y, Config(ncb_share={"PSPP": 1.0}, redemption_method="ladder"))
    assert p.portfolio_yield_pct.iloc[1] == pytest.approx((1.0 * 110 + 4.0 * 10) / 120)

def test_ncb_share_scales_stock_not_yield():
    h, w, y = _setup([90], [1.0])
    p = portfolio_yield(h, w, y)                               # default share 8/9
    assert p.stock_eur_m.iloc[0] == pytest.approx(80.0) and p.portfolio_yield_pct.iloc[0] == 1.0

def test_reference_rate_switch_and_exposure_sign():
    pr = pd.DataFrame(dict(month=[M("2024-12-01"), M("2025-01-01")], mro_pct=[3.15, 3.15], dfr_pct=[3.0, 3.0]))
    ref = reference_rate(pr)
    assert ref.loc[M("2024-12-01")] == 3.15 and ref.loc[M("2025-01-01")] == 3.0
    port = pd.DataFrame(dict(month=[M("2024-12-01"), M("2025-01-01")] * 2, ncb=["DE", "DE", "IT", "IT"],
                             programme="PSPP", stock_eur_m=[100.0] * 4, portfolio_yield_pct=[0.5, 0.5, 2.5, 2.5],
                             yield_method="interpolated"))
    key = pd.DataFrame(dict(ncb=["DE", "IT"], valid_from=[M("2020-01-01")] * 2, valid_to=[pd.NaT] * 2, key_share=[0.27, 0.16]))
    e = exposure(port, pr, key).set_index(["ncb", "month"])
    assert e.loc[("DE", M("2024-12-01")), "carry_eur_m_pa"] == pytest.approx(100 * (0.5 - 3.15) / 100)
    assert e.loc[("DE", M("2025-01-01")), "carry_per_keypp_eur_m_pa"] < e.loc[("IT", M("2025-01-01")), "carry_per_keypp_eur_m_pa"]
    assert e.groupby(level="month").carry_per_keypp_demeaned.sum().abs().max() < 1e-12
    hy = to_half_years(e.reset_index())
    assert set(hy.hy) == {"2024H2", "2025H1"}

def test_capital_key_periods():
    key = pd.DataFrame(dict(ncb=["DE", "DE"], valid_from=[M("2019-01-01"), M("2024-01-01")],
                            valid_to=[M("2023-12-01"), pd.NaT], key_share=[0.26, 0.27]))
    assert key_at(key, "DE", M("2023-06-01")) == 0.26 and key_at(key, "DE", M("2025-06-01")) == 0.27

def test_schema_validation_fails_loudly():
    with pytest.raises(KeyError):
        validate(pd.DataFrame(dict(month=["2020-01"], ncb=["DE"])), "holdings")

def test_validation_against_bdf_benchmark_runs():
    bench = pd.read_csv(ROOT / "data/hand/bdf_nii_benchmark.csv")
    fake = bench[["ncb", "year"]].assign(carry_per_keypp_eur_m_pa=bench.nii_after_realloc_eur_bn / bench.key_share_pct)
    res = compare(fake, bench)
    assert res["n"] == 8 and res["spearman"] == pytest.approx(1.0)
