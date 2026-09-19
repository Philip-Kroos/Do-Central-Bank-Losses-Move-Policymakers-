"""Parser checks against figures displayed on the ECB APP/PEPP pages (fetched 2026-09-11)."""
import sys, pathlib
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from code.exposure import ecb_inputs as ei
RAW = ROOT / "data/raw"
pytestmark = pytest.mark.skipif(not (RAW / "PSPP_breakdown_history.csv").exists(), reason="raw data not present")

def test_pspp_matches_ecb_page():
    H, W = ei.programme(str(RAW / "PSPP_breakdown_history.csv"), "PSPP")
    h = H[H.month == "2026-08-01"].set_index("ncb").holdings_eur_m
    assert h["DE"] == pytest.approx(435323, abs=5) and h["NL"] == pytest.approx(96593, abs=5) and h["IT"] == pytest.approx(282861, abs=5)
    assert W[W.month == "2026-08-01"].set_index("ncb").wam_years["IT"] == pytest.approx(7.38)
    assert H.ncb.nunique() == 18

def test_pepp_matches_ecb_page():
    H, W = ei.programme(str(RAW / "PEPP_public_sector_securities_breakdown_history.csv"), "PEPP")
    h = H[H.month == "2026-08-01"].set_index("ncb").holdings_eur_m
    assert h["GR"] == pytest.approx(33649, abs=10) and h["DE"] == pytest.approx(299921, abs=10)
