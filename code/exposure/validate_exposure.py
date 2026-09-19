"""Pre-specified validation: does the carry proxy rank NCBs like reported net interest income?

Benchmark: Banque de France Bulletin 260/6, NII after monetary income reallocation (EUR bn) and
Eurosystem key shares, as transcribed in data/hand/bdf_nii_benchmark.csv. Four NCBs x two years,
so this is descriptive (rank agreement), not a test. A failure means the treatment should rely on
reported results (Treatment A) rather than on the carry proxy (Treatment B) - decided in advance.
"""
import pandas as pd
from scipy.stats import spearmanr


def compare(expo_annual: pd.DataFrame, bench: pd.DataFrame) -> dict:
    b = bench.assign(nii_per_keypp=bench.nii_after_realloc_eur_bn / bench.key_share_pct)
    m = b.merge(expo_annual, on=["ncb", "year"], how="inner")
    if len(m) < 3:
        return dict(n=len(m), spearman=None, note="too few overlapping NCB-years")
    rho, p = spearmanr(m.nii_per_keypp, m.carry_per_keypp_eur_m_pa)
    return dict(n=len(m), spearman=float(rho), p_value_descriptive=float(p),
                pairs=m[["ncb", "year", "nii_per_keypp", "carry_per_keypp_eur_m_pa"]].to_dict("records"))
