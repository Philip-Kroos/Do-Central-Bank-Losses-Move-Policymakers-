import pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
def test_debt_2021_matches_release_headline():
    d = pd.read_csv(ROOT / "data/hand/debt_ratio_eurostat_oct2022.csv").set_index("ncb").y2021
    # headline sentence of Eurostat release 118/2022 (lowest and highest ratios end-2021)
    for k, v in dict(EE=17.6, BG=23.9, LU=24.5, GR=194.5, IT=150.3, PT=125.5, ES=118.3, FR=112.8, BE=109.2, CY=101.0).items():
        assert d[k] == v
    assert len(d) == 21
