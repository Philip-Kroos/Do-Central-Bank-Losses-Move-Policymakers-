"""Master script, stage 1: corpus -> passages -> prefilter -> go/no-go report (counts only).

usage: python3 run_go_nogo.py --bis <file> [--cbs <file>] --roster data/hand/governor_roster.csv
The roster maps speaker names to NCB and term dates (to be filled; only verified rows allowed).
"""
import argparse, json
import pandas as pd
from code.corpus.load import load_corpus
from code.corpus.segment import passages
from code.corpus.keywords import flag_topics
from code.corpus import go_nogo

ap = argparse.ArgumentParser()
ap.add_argument("--bis"); ap.add_argument("--cbs"); ap.add_argument("--roster", required=True)
ap.add_argument("--out", default="output/go_nogo_report.json")
a = ap.parse_args()

frames = [load_corpus(p, s) for p, s in ((a.bis, "BIS"), (a.cbs, "CBS")) if p]
corpus = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["speaker", "date", "title"], keep="first")
roster = pd.read_csv(a.roster, parse_dates=["term_start", "term_end"])
m = corpus.merge(roster, left_on=corpus["speaker"].str.lower().str.strip(),
                 right_on=roster["speaker_name"].str.lower().str.strip(), how="inner")
m["term_start_missing"] = m.term_start.isna()
m = m[(m.date >= m.term_start.fillna(pd.Timestamp("1900-01-01"))) & (m.date <= m.term_end.fillna(pd.Timestamp("2100-01-01")))]
if m.term_start_missing.any():
    print(f"WARNING: {int(m.term_start_missing.sum())} speeches matched to roster rows without a verified start date")
rows = [dict(ncb=r.ncb, role=r.role, date=r.date, **flag_topics(p))
        for r in m.itertuples() for p in passages(r.text)]
P = pd.DataFrame(rows)
gov = P[P.role == "governor"]
report = dict(n_speeches=int(len(m)), n_passages=int(len(P)),
              prefilter_upper_bound=go_nogo.decide(gov, sorted(roster[roster.role == "governor"].ncb.unique())))
import pathlib; pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
json.dump(report, open(a.out, "w"), indent=2, default=str)
print(json.dumps(report, indent=2, default=str))
