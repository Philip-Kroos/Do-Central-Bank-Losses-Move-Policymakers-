"""High-recall multilingual prefilter for balance-sheet topics (codebook v0: Y1, Y2, Y3).

Purpose: go/no-go counting and routing passages to the classifier. NOT an outcome measure.
Terms are matched case-insensitively on word boundaries; a trailing * allows suffixes.
Every term list is a design choice to be reviewed at the codebook gate.
"""
from __future__ import annotations
import re

TERMS: dict[str, dict[str, list[str]]] = {
    "Y1_reserves": {
        "en": ["minimum reserve*", "reserve requirement*", "required reserves", "remuneration of reserves",
               "reserve remuneration", "interest on reserves", "remuneration of excess reserves",
               "excess reserves", "excess liquidity", "tiering", "two-tier system", "unremunerated reserves",
               "non-remunerated reserves"],
        "de": ["mindestreserve*", "verzinsung der reserven", "verzinsung von überschussreserven",
               "überschussreserven", "überschussliquidität", "unverzinst*", "zweistufige* system*"],
        "fr": ["réserves obligatoires", "rémunération des réserves", "réserves excédentaires",
               "excédent de liquidité", "système à deux paliers", "non rémunérées"],
        "it": ["riserva obbligatoria", "riserve obbligatorie", "remunerazione delle riserve",
               "riserve in eccesso", "liquidità in eccesso", "sistema a due livelli"],
        "es": ["reservas mínimas", "coeficiente de reservas", "remuneración de las reservas",
               "exceso de reservas", "exceso de liquidez", "sistema de dos tramos"],
        "nl": ["minimumreserve*", "reserveverplichting*", "rente op reserves", "vergoeding op reserves",
               "overtollige reserves", "overliquiditeit"],
    },
    "Y2_cb_pnl": {
        "en": ["central bank loss*", "our loss*", "negative equity", "loss carried forward", "provision for financial risks",
               "financial buffers", "recapitali*", "profit distribution", "net interest income"],
        "de": ["bundesbankverlust*", "verlustvortrag", "negatives eigenkapital", "wagnisrückstellung",
               "risikovorsorge", "gewinnausschüttung", "rekapitalisier*", "nettozinsergebnis"],
        "fr": ["pertes de la banque", "fonds pour risques généraux", "capitaux propres négatifs",
               "report à nouveau", "recapitalis*"],
        "it": ["perdita lorda", "fondo rischi generali", "patrimonio netto negativo", "ricapitalizz*"],
        "es": ["pérdidas operativas", "provisiones para riesgos", "patrimonio neto negativo", "recapitaliz*"],
        "nl": ["negatief eigen vermogen", "voorziening voor financiële risico's", "herkapitalis*"],
    },
    "Y3_balance_sheet": {
        "en": ["quantitative tightening", "balance sheet reduction", "active sales", "selling bonds",
               "bond sales", "run-off", "reinvestment*"],
        "de": ["bilanzabbau", "bilanzverkürzung", "anleiheverkäufe", "aktive* verkäufe", "wiederanlage*"],
        "fr": ["resserrement quantitatif", "réduction du bilan", "ventes actives", "réinvestissement*"],
        "it": ["riduzione del bilancio", "vendite attive", "reinvestiment*"],
        "es": ["endurecimiento cuantitativo", "reducción del balance", "ventas activas", "reinversion*", "reinversión"],
        "nl": ["balansverkorting", "actieve verkopen", "herinvestering*"],
    },
}


def _compile(term: str) -> re.Pattern:
    body = re.escape(term.rstrip("*")).replace(r"\ ", r"\s+")
    suffix = r"\w*" if term.endswith("*") else ""
    return re.compile(rf"(?<!\w){body}{suffix}(?!\w)", re.IGNORECASE)


PATTERNS = {topic: [_compile(t) for lang in langs.values() for t in lang] for topic, langs in TERMS.items()}


def flag_topics(text: str) -> dict[str, bool]:
    return {topic: any(p.search(text) for p in pats) for topic, pats in PATTERNS.items()}
