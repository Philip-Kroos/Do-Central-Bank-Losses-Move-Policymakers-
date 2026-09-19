import sys, pathlib
import pandas as pd
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from code.corpus.segment import split_sentences, passages
from code.corpus.keywords import flag_topics
from code.corpus import go_nogo
from code.exposure.treatment_dates import derive

def test_abbreviations_and_decimals():
    t = "Rates rose to 2.5 per cent. See e.g. the ECB. Die Bundesbank, vgl. S. 12, meldet Verluste. Fine."
    s = split_sentences(t)
    assert s == ["Rates rose to 2.5 per cent.", "See e.g. the ECB.", "Die Bundesbank, vgl. S. 12, meldet Verluste.", "Fine."]

def test_passages_size():
    t = " ".join(f"Sentence {i} ends here." for i in range(12))
    p = passages(t)
    assert len(p) == 3 and p[0].count("ends here.") == 5 and p[2].count("ends here.") == 2

@pytest.mark.parametrize("text,topic", [
    ("We should not remunerate minimum reserves at the deposit rate.", "Y1_reserves"),
    ("Die Mindestreservepflicht sollte erhöht werden.", "Y1_reserves"),
    ("La rémunération des réserves pèse sur nos comptes.", "Y1_reserves"),
    ("Il fondo rischi generali è stato utilizzato.", "Y2_cb_pnl"),
    ("De balansverkorting verloopt geleidelijk.", "Y3_balance_sheet"),
])
def test_keyword_hits(text, topic):
    assert flag_topics(text)[topic]

def test_keyword_no_false_hit_on_substring():
    assert not flag_topics("Tiered pricing of loans is common in retail banking.")["Y1_reserves"]

def test_go_nogo_rule():
    ncbs = [f"N{i}" for i in range(14)]
    dates = pd.date_range("2022-01-15", "2026-06-15", freq="6MS") + pd.Timedelta(days=14)
    rows = [dict(ncb=n, date=d, Y1_reserves=True, Y3_balance_sheet=False) for n in ncbs for d in dates]
    assert go_nogo.decide(pd.DataFrame(rows), ncbs)["decision"] == "Y1_primary"
    y1_sparse = [dict(r) for i, r in enumerate(rows) if i % 3 == 0]          # Y1 mean ~ 0.33 per cell
    y3_dense = [dict(r, Y1_reserves=False, Y3_balance_sheet=True) for r in rows] * 2
    res = go_nogo.decide(pd.DataFrame(y1_sparse + y3_dense), ncbs)
    assert res["Y1"]["mean_per_cell"] < 1 and res["pooled"]["mean_per_cell"] >= 1
    assert res["decision"] == "pooled_index"
    assert go_nogo.decide(pd.DataFrame(rows[:5]), ncbs)["decision"] == "stop_speech_design"

def test_treatment_dates_on_hand_data():
    out = derive(pd.read_csv(ROOT / "data/hand/ncb_results_v0.csv")).set_index("ncb")
    assert out.loc["NL", "net_on"] == "2023H2"          # FY2022 loss, publication assumed March 2023
    assert out.loc["FR", "net_on"] == "2025H2" and out.loc["FR", "net_exit_fy"] == 2025
    assert pd.isna(out.loc["IT", "net_fy"])             # never a net loss (provisions + tax)
    assert bool(out.loc["AT", "net_left_censored"]) is False
    assert pd.isna(out.loc["PT", "net_fy"])              # technical deferred-tax loss excluded
    assert pd.isna(out.loc["GR", "gross_fy"])            # high-yield own portfolio: no gross loss collected
