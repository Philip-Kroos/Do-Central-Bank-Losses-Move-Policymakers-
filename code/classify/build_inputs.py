"""Build blind classification inputs (PAP v2 §8): masked Y4-prefilter passages of NCB heads and ECB board,
2016-01-01..2026-06-30, excl. BG. Random order, opaque IDs, split into files <= 1,150 passages.
Key file (id -> url, pid, ncb, role, date) stays in data/derived and is NOT given to the classifier."""
import json, re, sys, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from code.validation.mask import build_masker

SEED = 20260912
Y4 = re.compile(r"\b(?:policy rates?|key interest rates?|deposit facility rate|interest rate (?:hikes?|increases?|cuts?|decisions?)|rate (?:hikes?|cuts?)|raise (?:interest )?rates|cut (?:interest )?rates|monetary (?:policy )?tightening|tighten\w*|monetary policy stance|restrictive (?:territory|monetary)|accommodative|easing cycle)\b", re.I)
P = pd.read_pickle("data/derived/bis_ea_passages_prefilter.pkl")
meta = pd.read_pickle("data/derived/bis_ea_meta.pkl")
P = P[(P.date >= "2016-01-01") & (P.date <= "2026-06-30")].sort_values(["url", "pid"]).copy()
P["prev_text"] = P.groupby("url").text.shift(1).fillna("")
U = P[P.role.isin(["ncb_head", "ecb_board", "ecb_president"]) & P.ncb.ne("BG") & P.text.str.contains(Y4)]
U = U.sample(frac=1, random_state=SEED).reset_index(drop=True)
U["group"] = np.where(U.role == "ncb_head", "heads", "ecb")
U = pd.concat([U[U.group == "heads"], U[U.group == "ecb"]]).reset_index(drop=True)   # heads first
U["id"] = [f"C{i+1:05d}" for i in range(len(U))]
mask = build_masker(meta.author.dropna().unique().tolist())
out = pathlib.Path("output/classify"); out.mkdir(parents=True, exist_ok=True)
files = []
for g, sub in U.groupby("group", sort=False):
    n_files = int(np.ceil(len(sub) / 1150))
    for k in range(n_files):
        chunk = sub.iloc[k * int(np.ceil(len(sub) / n_files)):(k + 1) * int(np.ceil(len(sub) / n_files))]
        name = f"klass_input_{g}_{k+1}.json"
        json.dump(dict(file=name, items=[dict(id=r.id, text=mask(r.text), context=mask(r.prev_text)[-350:]) for r in chunk.itertuples()]),
                  open(out / name, "w"), ensure_ascii=False)
        files.append((name, len(chunk), (out / name).stat().st_size))
U[["id", "url", "pid", "ncb", "role", "author", "date"]].to_csv("data/derived/classify_key.csv", index=False)
# validation sample in the same input format (for model-human agreement)
V = json.load(open("output/validation/sample_masked.json"))
json.dump(dict(file="klass_input_validation.json", items=[dict(id=v["id"], text=v["text"], context=v["context"]) for v in V]),
          open(out / "klass_input_validation.json", "w"), ensure_ascii=False)
for f in files: print(f)
print("validation file items:", len(V))
