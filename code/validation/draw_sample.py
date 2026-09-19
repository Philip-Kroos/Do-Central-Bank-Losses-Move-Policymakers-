"""Draw the PAP v2 §8 validation sample (400 masked passages; 100 double-coded). Seed fixed.
Writes: output/validation/sample_masked.json (texts, no metadata) and data/derived/validation_key.csv
(id -> url, ncb, role, date, stratum; NOT shown to coders). Prints only counts."""
import json, re, sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from code.validation.mask import build_masker
from code.corpus import go_nogo

SEED = 20260911
rng = np.random.default_rng(SEED)
P = pd.read_pickle("data/derived/bis_ea_passages_prefilter.pkl")
meta = pd.read_pickle("data/derived/bis_ea_meta.pkl")
y4 = re.compile(r"\b(?:policy rates?|key interest rates?|deposit facility rate|interest rate (?:hikes?|increases?|cuts?|decisions?)|rate (?:hikes?|cuts?)|raise (?:interest )?rates|cut (?:interest )?rates|monetary (?:policy )?tightening|tighten\w*|monetary policy stance|restrictive (?:territory|monetary)|accommodative|easing cycle)\b", re.I)
P = P[(P.date >= "2016-01-01") & (P.date <= "2026-06-30")].copy()
P["y4hit"] = P.text.str.contains(y4)
P["period"] = np.where(P.date >= "2022-01-01", "post", "pre")
BIG, MID = {"DE", "FR", "IT", "ES"}, {"NL", "FI", "IE", "GR", "BE", "AT", "PT"}
P["size"] = np.where(P.ncb.isin(BIG), "big", np.where(P.ncb.isin(MID), "mid", "small"))
P = P.sort_values(["url", "pid"]).reset_index(drop=True)
P["prev_text"] = P.groupby("url").text.shift(1).fillna("")

def take(df, n, label):
    n = min(n, len(df))
    idx = rng.choice(df.index.to_numpy(), size=n, replace=False)
    return df.loc[idx].assign(stratum=label)

heads = P[(P.role == "ncb_head") & P.y4hit & P.ncb.ne("BG")]
parts = []
alloc = {("big", "pre"): 50, ("big", "post"): 50, ("mid", "pre"): 60, ("mid", "post"): 60, ("small", "pre"): 40, ("small", "post"): 40}
for (sz, per), n in alloc.items():
    parts.append(take(heads[(heads["size"] == sz) & (heads.period == per)], n, f"head_{sz}_{per}"))
got = sum(len(p) for p in parts)
if got < 300:                                          # refill shortfall from mid, then big
    used = pd.concat(parts).index
    pool = heads.drop(used)
    parts.append(take(pool[pool["size"] == "mid"], 300 - got, "head_refill"))
    got = sum(len(p) for p in parts)
    if got < 300:
        pool = heads.drop(pd.concat(parts).index)
        parts.append(take(pool, 300 - got, "head_refill"))
parts.append(take(P[P.role.isin(["ecb_board", "ecb_president"]) & P.y4hit], 50, "ecb_board"))
parts.append(take(P[(P.role == "ncb_head") & ~P.y4hit], 50, "nonhit"))
S = pd.concat(parts)
S = S.sample(frac=1, random_state=SEED).reset_index(drop=True)
S["id"] = [f"V{i+1:03d}" for i in range(len(S))]
S["double_code"] = False
S.loc[rng.choice(len(S), 100, replace=False), "double_code"] = True

mask = build_masker(meta.author.dropna().unique().tolist())
items = [dict(id=r.id, text=mask(r.text), context=mask(r.prev_text)[-350:], double=bool(r.double_code)) for r in S.itertuples()]
import pathlib
pathlib.Path("output/validation").mkdir(parents=True, exist_ok=True)
json.dump(items, open("output/validation/sample_masked.json", "w"), ensure_ascii=False)
S[["id", "url", "pid", "ncb", "role", "date", "stratum", "double_code", "y4hit"]].to_csv("data/derived/validation_key.csv", index=False)
print("sample:", len(S), S.stratum.value_counts().to_dict(), "double-coded:", int(S.double_code.sum()))
print("json bytes:", pathlib.Path("output/validation/sample_masked.json").stat().st_size)
