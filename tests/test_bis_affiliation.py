import sys, pathlib
import pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from code.corpus.bis_affiliation import parse

CASES = [
    ("Speech by Mr Gediminas Šimkus, Chairman of the Board of the Bank of Lithuania, at the Baltic Anti Money Laundering (AML) Forum 2021, Vilnius, 12 October 2021.", "LT", "ncb_head"),
    ("Speech by Mr Klaas Knot, Chair of the Financial Stability Board and President of De Nederlandsche Bank, at the CFA Institute Systemic Risk Council, Washington DC", "NL", "ncb_head"),
    ("Address by Ms Sharon Donnery, Deputy Governor of the Central Bank of Ireland, at the Peterson Institute", "IE", "ncb_other"),
    ("Opening speech by Prof Claudia Buch, Deputy President of the Deutsche Bundesbank, at the 15th Meeting of the Ottawa Group", "DE", "ncb_other"),
    ("Welcome speech by Prof Joachim Wuermeling, Member of the Executive Board of the Deutsche Bundesbank, at the Deutsche Bundesbank reception", "DE", "ncb_other"),
    ("Dinner speech by Dr Jens Weidmann, President of the Deutsche Bundesbank and Chairman of the Board of Directors of the Bank for International Settlements, at the Annual Meeting", "DE", "ncb_head"),
    ("Keynote speech by Mr Luis de Guindos, Vice-President of the European Central Bank, at the First Annual Conference, organised by the Central Bank of Cyprus, Limassol", "ECB", "ecb_board"),
    ("Opening address by Ms Rosanna Costa, Governor of the Central Bank of Chile, at the IV Meeting of Heads of Financial Risk Management in Central Banks, organised jointly by the Bank of Spain", None, None),
    ("Keynote speech by Ms Tina Žumer, Deputy Governor of Bank of Slovenia, at the ACI Slovenia Annual Assembly", "SI", "ncb_other"),
    ("Speech by Mr François Villeroy de Galhau, Governor of the Bank of France, at the Bank of France high-level conference", "FR", "ncb_head"),
    ("Introductory statement by Ms Christine Lagarde, President of the European Central Bank, and Mr Luis de Guindos, Vice-President of the European Central Bank, Frankfurt am Main", "ECB", "ecb_president"),
    ("Remarks by Mr Gabriel Makhlouf, Governor of the Central Bank of Ireland, after the Central Bank of Irelands' Briefing, Dublin", "IE", "ncb_head"),
]

@pytest.mark.parametrize("desc,inst,role", CASES)
def test_parse(desc, inst, role):
    r = parse(desc)
    assert r["inst"] == inst and r["role_class"] == role, r

def test_masking():
    from code.validation.mask import build_masker
    m = build_masker(["Joachim Nagel", "François Villeroy de Galhau"])
    out = m("Nagel of the Deutsche Bundesbank said German inflation in Berlin and France is high; the ECB decides.")
    assert "Nagel" not in out and "Bundesbank" not in out and "German" not in out and "Berlin" not in out and "France" not in out
    assert "ECB" in out
    out2 = build_masker(["Isabel Schnabel"])("Speech by Isabel Schnabel, Member of the Executive Board of the ECB, at a conference. The ECB raised rates.")
    assert "Executive Board" not in out2 and "[ROLE]" in out2 and "The ECB raised" in out2
