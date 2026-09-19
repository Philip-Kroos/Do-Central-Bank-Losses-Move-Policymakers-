"""Validation analysis (PAP v2 §8, clarified in deviations log 2026-09-11 10:50).

Inputs: coder CSVs exported by validierung_kodierung.jsx (A: 400, B: 100 double-coded), model results CSV for
klass_input_validation.json. Key: data/derived/validation_key.csv (strata).
Gate (both required): Krippendorff alpha human-human >= 0.667 for (i) topic (nominal) and (ii) position among
passages both coders code as topic (interval). Prefilter recall is estimated with population weights; if the
estimated recall of stance passages is below 0.80 the prefilter is expanded before the full classification.
usage: python3 code/validation/analyse_validation.py A.csv [B.csv] [model.csv]
"""
from __future__ import annotations
import json, sys
import numpy as np, pandas as pd
import krippendorff

GATE = 0.667
RECALL_MIN = 0.80
POP = {"hit": 1991, "nonhit": None}      # heads 2016-2026 Y4-prefilter hits; nonhit filled from data


def load_coder(path):
    d = pd.read_csv(path)
    d["topic"] = d["y4_topic"].astype(str).str.lower().map({"true": 1, "false": 0})
    d["position"] = pd.to_numeric(d["y4_position"], errors="coerce")
    return d.set_index("id")[["topic", "position"]]


def load_model(path):
    d = pd.read_csv(path)
    d = d[d["valid"].astype(str).str.lower() == "true"].copy()
    d["topic"] = d["topic"].astype(str).str.lower().map({"true": 1, "false": 0})
    d["position"] = pd.to_numeric(d["position"], errors="coerce")
    return d.set_index("id")[["topic", "position"]]


def alphas(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    ids = a.index.intersection(b.index)
    if len(ids) < 10:
        return dict(n=len(ids), alpha_topic=None, alpha_position=None)
    at = krippendorff.alpha(reliability_data=np.vstack([a.loc[ids, "topic"], b.loc[ids, "topic"]]).astype(float), level_of_measurement="nominal")
    both = [i for i in ids if a.at[i, "topic"] == 1 and b.at[i, "topic"] == 1]
    ap = krippendorff.alpha(reliability_data=np.vstack([a.loc[both, "position"], b.loc[both, "position"]]).astype(float),
                            level_of_measurement="interval") if len(both) >= 10 else None
    comb = lambda d, i: (d.loc[i, "position"].fillna(9) * d.loc[i, "topic"] + 9 * (1 - d.loc[i, "topic"])).astype(float)
    ac = krippendorff.alpha(reliability_data=np.vstack([comb(a, ids), comb(b, ids)]), level_of_measurement="nominal")
    conf = pd.crosstab(comb(a, ids).rename("first"), comb(b, ids).rename("second")).rename(index={9.0: "no topic"}, columns={9.0: "no topic"})
    return dict(n=len(ids), n_both_topic=len(both), alpha_topic=float(at), alpha_position=None if ap is None else float(ap),
                alpha_combined_nominal=float(ac), agreement_combined=float((comb(a, ids) == comb(b, ids)).mean()), confusion=conf.to_dict())


def recall(coder: pd.DataFrame, key: pd.DataFrame, pop_nonhit: int) -> dict:
    k = key.set_index("id")
    heads = k[k.stratum.str.startswith("head")].index.intersection(coder.index)
    non = k[k.stratum == "nonhit"].index.intersection(coder.index)
    if len(heads) == 0 or len(non) == 0:
        return dict(recall=None)
    p_hit = coder.loc[heads, "topic"].mean(); p_non = coder.loc[non, "topic"].mean()
    T_hit, T_non = p_hit * POP["hit"], p_non * pop_nonhit
    r = T_hit / (T_hit + T_non) if (T_hit + T_non) > 0 else None
    return dict(share_topic_in_hits=float(p_hit), share_topic_in_nonhits=float(p_non), est_recall=None if r is None else float(r),
                expand_prefilter=bool(r is not None and r < RECALL_MIN))


def main(argv):
    key = pd.read_csv("data/derived/validation_key.csv")
    A = load_coder(argv[0])
    out = dict(coder_A_n=int(len(A)))
    if len(argv) > 1 and argv[1] != "-":
        B = load_coder(argv[1]); hh = alphas(A, B); out["human_human"] = hh
        out["gate_passed"] = bool(hh["alpha_topic"] is not None and hh["alpha_topic"] >= GATE and hh["alpha_position"] is not None and hh["alpha_position"] >= GATE)
    if len(argv) > 2:
        out["model_vs_A"] = alphas(A, load_model(argv[2]))
    out["prefilter"] = recall(A, key, pop_nonhit=26567)
    print(json.dumps(out, indent=2, default=str))
    return out


if __name__ == "__main__":
    main(sys.argv[1:])
