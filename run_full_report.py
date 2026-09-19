"""Stage 4b: complete pre-specified report (PAP v2-v2.3): H3, R1-R11, F1, F6, H1, R6, R8, H4 with joint RI + Romano-Wolf,
all 12 exposure variants, LaTeX table and coefficient figure.
--synthetic writes a DRY RUN (random positions) to output/dryrun_full; real runs require frozen classification results."""
import argparse, glob, hashlib, json, pathlib, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from code.estimate import panel as pn
from code.estimate.full_report import run_all, Linear, exposure_regressor

ap = argparse.ArgumentParser()
ap.add_argument("--synthetic", action="store_true"); ap.add_argument("--results", nargs="*"); ap.add_argument("--perm", type=int, default=999)
ap.add_argument("--plant", type=float, default=0.0, help="synthetic only: planted latent effect of exposure")
a = ap.parse_args()

key = pd.read_csv("data/derived/classify_key.csv", parse_dates=["date"]); key["role_group"] = np.where(key.role == "ncb_head", "heads", "ecb")
paths = {}
for f in sorted(glob.glob("output/exposure_grid/exposure_halfyear_*.csv")):
    tag = f.split("exposure_halfyear_")[1].replace(".csv", "")
    e = pn.exposure_panel(pd.read_csv(f)); paths[tag] = e.pivot(index="ncb", columns="hy", values="E").reindex(columns=pn.LABELS)
if a.synthetic:
    rng = np.random.default_rng(7)
    k = key.assign(hy=pn.hy(key.date))
    ex = paths["net_flow_pepp0.889_mm1"]
    z = np.array([a.plant * ex.at[c, h] if (c in ex.index and h in ex.columns and np.isfinite(ex.at[c, h])) else 0 for c, h in zip(k.ncb, k.hy)]) + rng.normal(0, 1, len(k))
    res = pd.DataFrame(dict(id=k.id, valid=True, topic=rng.random(len(k)) < 0.7, position=np.where(z < -0.6, -1, np.where(z > 0.6, 1, 0)).astype(float),
                            retrospective=rng.random(len(k)) < 0.2))
    outdir = pathlib.Path("output/dryrun_full")
else:
    frozen = pathlib.Path("docs/classification_freeze.sha256")
    if not frozen.exists(): sys.exit("Refusing real run: classification results are not frozen.")
    rec = dict(l.split()[::-1] for l in frozen.read_text().splitlines() if l.strip())
    for f in a.results:
        if rec.get(f) != hashlib.sha256(open(f, "rb").read()).hexdigest(): sys.exit(f"Refusing real run: {f} not frozen.")
    res = pd.concat([pd.read_csv(f) for f in a.results])
    for c in ("valid", "topic", "retrospective"):
        if c in res: res[c] = res[c].astype(str).str.lower() == "true"
    outdir = pathlib.Path("output/estimation_full")
outdir.mkdir(parents=True, exist_ok=True)

rates = pd.read_csv("data/derived/policy_rates.csv", parse_dates=["month"])
S = pn.spread_panel(pd.read_csv("data/derived/yields.csv"))
PS = pn.pre_period_x_rate(S, "spread_de", rates)
PD = pn.pre_period_x_rate(pd.read_csv("data/derived/debt_ratio_hy.csv"), "debt_ratio", rates)
def build(results):
    Y = pn.outcome_panel(results, key)
    return (Y[Y.role_group == "heads"].merge(S, on=["ncb", "hy"], how="left").merge(PS, on=["ncb", "hy"], how="left")
            .merge(PD, on=["ncb", "hy"], how="left"))
heads = build(res)
retro = pn.outcome_panel(res, key, exclude_retrospective=True); retro = retro[retro.role_group == "heads"].merge(PS, on=["ncb", "hy"], how="left").merge(PD, on=["ncb", "hy"], how="left")
main_controls = ("pre_spread_de_x_dfr", "pre_debt_ratio_x_dfr")
hicp = pathlib.Path("data/derived/hicp_hy.csv")
if hicp.exists():
    H = pd.read_csv(hicp); heads = heads.merge(H, on=["ncb", "hy"], how="left"); retro = retro.merge(H, on=["ncb", "hy"], how="left"); main_controls = ("hicp",) + main_controls
treat = pd.read_csv("data/hand/treatment_dates_v0.csv"); coh = pn.treatment_cohorts(treat)
documented = {"AT", "BE", "DE", "FR", "NL", "SK", "ES", "FI", "GR", "IE", "IT", "PT", "LU"}
roster = pd.read_csv("data/hand/governor_roster.csv", parse_dates=["term_start"])
roster["gov"] = roster.speaker_name.map(pn.gov_id)
attrs = roster.groupby("gov").agg(former_minister=("former_minister", "max"), reappointable=("reappointable", "max")).reset_index()
heads_gov = key[key.role == "ncb_head"].assign(gov=lambda d: d.author.map(pn.gov_id)).gov
attr_cov = {c: float(heads_gov.isin(attrs.dropna(subset=[c]).gov).mean()) for c in ("former_minister", "reappointable")}
H4_MIN_COVERAGE = 0.80                                             # PAP v2 H4: disclosed threshold
attrs_ok = {c: v >= H4_MIN_COVERAGE for c, v in attr_cov.items()}
attrs = attrs[["gov"] + [c for c, ok in attrs_ok.items() if ok]] if any(attrs_ok.values()) else attrs.iloc[:0]
first_seen = key[key.role == "ncb_head"].assign(gov=lambda d: d.author.map(pn.gov_id)).groupby("gov").date.min()
succ = set(roster.loc[roster.term_start > "2022-06-30", "gov"]) | set(first_seen[first_seen >= "2022-07-01"].index)

rep = dict(mode="SYNTHETIC DRY RUN - NOT RESULTS" if a.synthetic else "REAL", planted=a.plant if a.synthetic else None,
           controls=list(main_controls), hicp_included=hicp.exists(), cells=int(len(heads)), passages=int(heads.n.sum()),
           successors_after_2022=sorted(succ))
rep["H4_attribute_coverage"] = dict(coverage=attr_cov, threshold=H4_MIN_COVERAGE, estimated=attrs_ok)
rep["estimates"] = run_all(heads, paths, coh, documented, attrs, main_controls, n_perm=a.perm, retro_heads=retro, successors_after_2022=succ)
# F3: placebo event dates among never-treated NCBs (distribution of ATT; share at least as extreme as H1)
from code.estimate.full_report import event_stat
rng_f3 = np.random.default_rng(3)
never = [c for c in documented if not np.isfinite(coh["N"].get(c, np.inf))]
treated_idx = [v for v in coh["N"].values() if np.isfinite(v)]
plac = []
for _ in range(min(a.perm, 499)):
    fake = {c: np.inf for c in documented}
    for c in rng_f3.choice(never, size=min(3, len(never)), replace=False):
        fake[c] = float(rng_f3.choice(treated_idx))
    att, _ = event_stat(heads, fake, set(never)); plac.append(att)
plac = np.array(plac, float); plac = plac[np.isfinite(plac)]
h1 = rep["estimates"]["H1_net_loss"]["estimate"]
rep["estimates"]["F3_placebo_dates_never_treated"] = dict(mean_placebo_att=float(plac.mean()), share_as_extreme_as_H1=float(np.mean(np.abs(plac) >= abs(h1))), draws=int(len(plac)))
# H2 (exploratory): net-loss ATT minus covered-gross-loss ATT (point estimate)
rep["estimates"]["H2_net_minus_gross_exploratory"] = dict(estimate=float(rep["estimates"]["H1_net_loss"]["estimate"] - rep["estimates"]["R6_gross_loss"]["estimate"]))
# F2: Executive Board comparison, descriptive: EB mean stance change after ECB loss publication (2024H2+) minus never-net-loss governors
Yall = pn.outcome_panel(res, key)
def wmean(x): return np.average(x.y, weights=x.n) if len(x) else np.nan
eb = Yall[Yall.role_group == "ecb"]; nv = Yall[(Yall.role_group == "heads") & Yall.ncb.isin(never)]
post = lambda d: d[d.hy >= "2024H2"]; pre = lambda d: d[(d.hy >= "2022H1") & (d.hy <= "2023H2")]
rep["estimates"]["F2_board_vs_never_treated_descriptive"] = dict(estimate=float((wmean(post(eb)) - wmean(pre(eb))) - (wmean(post(nv)) - wmean(pre(nv)))),
    note="difference-in-differences of passage-weighted means, 2022H1-2023H2 vs 2024H2-2026H1; descriptive, no inference")
# F4: Slovenia acting head without voting rights, descriptive
si = Yall[(Yall.role_group == "heads") & (Yall.ncb == "SI")]
rep["estimates"]["F4_slovenia_acting_period_descriptive"] = dict(mean_acting=float(wmean(si[(si.hy >= "2025H1") & (si.hy <= "2026H1")])) if len(si) else None,
    mean_before=float(wmean(si[si.hy < "2025H1"])) if len(si) else None, cells=int(len(si)))
rep["open_items"] = ["HICP control pending" if not hicp.exists() else None,
                     f"H4 skipped: attribute coverage {attr_cov} below {H4_MIN_COVERAGE}" if not any(attrs_ok.values()) else None,
                     "R7 human-only subsample requires validation codes", "H5 NCB actions dataset not yet built"]
var = {}
for tag, pth in paths.items():
    L = Linear(heads, main_controls); b, t, _ = L.stat(exposure_regressor(L.d, pth, {c: c for c in heads.ncb.unique()})[:, None])
    var[tag] = dict(beta=float(b[0]), t=float(t[0]))
rep["exposure_variants_point_estimates"] = var
json.dump(rep, open(outdir / "report.json", "w"), indent=2)

E = rep["estimates"]; rows = [k for k in E if "estimate" in E[k] and "t" in E[k]]
label = lambda k: k.replace("_", " ")
with open(outdir / "table_main.tex", "w") as f:
    f.write("\\begin{tabular}{lccc}\\toprule\nSpecification & Estimate & $t$ (jackknife) & $p$ (RI) \\\\\\midrule\n")
    for k in rows:
        rw = f" [RW {E[k]['p_romano_wolf']:.3f}]" if "p_romano_wolf" in E[k] else ""
        f.write(f"{label(k)} & {E[k]['estimate']:.3f} & {E[k]['t']:.2f} & {E[k]['p_ri']:.3f}{rw} \\\\\n")
    f.write("\\bottomrule\\end{tabular}\n")
fig, ax = plt.subplots(figsize=(6.4, 4.6))
dose = [k for k in rows if k.startswith(("H3", "R1", "R3", "R4", "R9", "R10", "R11"))]
est = [E[k]["estimate"] for k in dose]; se = [abs(E[k]["estimate"] / E[k]["t"]) if E[k]["t"] else np.nan for k in dose]
ax.errorbar(est, range(len(dose)), xerr=1.96 * np.array(se), fmt="o", color="#1B2430", ecolor="#8A94A3", capsize=3)
ax.axvline(0, color="#9B3326", lw=0.8); ax.set_yticks(range(len(dose))); ax.set_yticklabels([label(k) for k in dose], fontsize=8); ax.invert_yaxis()
ax.set_xlabel("Effect on rate stance per SD of exposure (scale -1 to +1)")
ax.set_title(("SYNTHETIC - NOT RESULTS\n" if a.synthetic else "") + "Exposure effect across pre-specified specifications", fontsize=9)
fig.text(0.01, 0.005, "Bars: +/-1.96 jackknife SE (descriptive); inference uses randomisation p-values in table_main.tex.", fontsize=6.5)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(outdir / "fig_specifications.png", dpi=200)
print(json.dumps({k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in E.items()}, indent=1))
