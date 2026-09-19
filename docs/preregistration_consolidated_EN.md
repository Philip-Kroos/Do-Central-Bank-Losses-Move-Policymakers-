---
title: "Pre-Registration: Central Bank Losses and Rate Advocacy in the Eurosystem"
subtitle: "Consolidated analysis plan (status v2.3) and out-of-sample protocol"
author: "Philip [surname]"
date: "11 September 2026"
geometry: margin=2.4cm
fontsize: 11pt
---

# Status and integrity

This document consolidates the analysis plan as of 11 September 2026, 12:15 UTC. It is a faithful English translation. The dated German source documents are authoritative and were frozen with the following SHA-256 hashes:

- Design (`pap_v2_amendment.md`):\
  `d93eda714c2c03fb22014b712b2e9d7cae6ef1ef5149393cfad28107186fad0b`
- Power; dose design primary (`pap_v2_1_amendment.md`):\
  `3a93f4e7a016d585b7df393d12fe92e5ce0388b60ceaf7f28dabee57d6f64e1b`
- Controls; collinearity rule (`pap_v2_2_amendment.md`):\
  `2b8b35b0874f206f7deaac8747b2eee48d14fe5e2bd48e7acc0be144225a3e59`
- Jackknife-studentised inference (`pap_v2_3_amendment.md`):\
  `a01546a10d7a0b8ca70c0444992661ffb0e33daf817684a3e00f00e2d27f5f27`

**Data seen before registration.** Counts of keyword-matched passages per central bank and half-year; treatment data (published results of national central banks); exposure data built from public ECB statistics; debt and yield data. Eighteen passages matching a reserve-remuneration keyword filter were read to check filter precision. **No passage on rate stance has been read, coded, classified or linked to outcomes.**

# Question and hypotheses

**Question.** Do members of the ECB Governing Council advocate lower policy rates when their own national central bank (NCB) bears larger losses from its non-pooled sovereign bond portfolio?

| # | Hypothesis | Role |
|---|---|---|
| H3 | Rate advocacy of NCB governors becomes more dovish as the NCB-specific carry exposure rises ($\beta<0$) | **primary** |
| H1 | Advocacy becomes more dovish after the NCB first publishes a net loss | secondary (low power disclosed) |
| H2 | Publication of a net loss matters more than a pre-provision loss fully covered by provisions | exploratory |
| H4 | Effects are larger for reappointable governors and former ministers | secondary |
| H5 | NCBs change provisioning or distribution policy after their first net loss | secondary, descriptive |
| H6 | Out-of-sample prediction for 2026H2 to 2027H2 (Section 7) | separate |

# Sample and outcome

- **Speakers:** heads of the 20 euro area NCBs excluding Bulgaria (including acting heads); ECB Executive Board members as a separate comparison group.
- **Corpus:** BIS central bankers' speeches, 1 January 2016 to 30 June 2026.
- **Passages:** five sentences each, with speaker, institution, role, country and capital names masked.
- **Classification universe:** 4,442 passages matching a rate-stance keyword filter (1,991 by NCB heads, 2,451 by Board members). The filter is expanded before classification if its estimated recall is below 0.80 (Section 5).
- **Coding:** Topic = the passage states or reports a view on the direction, level or pace of policy rates or the monetary policy stance. Position: $-1$ = favours lower rates or warns against over-tightening; $0$ = neutral, reporting or data-dependent without direction; $+1$ = favours higher rates or warns against early easing. Retrospective = the passage only evaluates past decisions.
- **Outcome:** passage-weighted mean position per governor and half-year (2016H1 to 2026H1).

# Treatment

**Exposure (H3).** Non-pooled carry of the NCB's own PSPP and PEPP sovereign holdings per percentage point of Eurosystem capital key:
$\text{carry}_{n,t} = S_{n,t}(s_{n,t} - r^{\text{ref}}_t)$,
where $r^{\text{ref}}$ is the MRO rate until 2024 and the deposit facility rate from 2025. The measure is demeaned across NCBs within each half-year and standardised. Baseline construction: net-flow method, NCB share 8/9, purchase maturity equal to WAM. Eleven further variants are pre-specified robustness checks.

**Published net loss (H1).** Indicator for half-years starting after the first official publication of a net loss (loss reduces equity or is carried forward; technical tax losses excluded). The half-year of publication is dropped. NCBs with undocumented status are excluded from H1.

# Estimation

**H3 main specification.**
$y_{g,t} = \alpha_g + \gamma_t + \beta E_{n(g),t} + \delta_1 \pi_{n,t} + \delta_2 (\overline{\text{spread}}^{2019\text{-}21}_n \times \text{DFR}_t) + \delta_3 (\overline{\text{debt}}^{2019\text{-}21}_n \times \text{DFR}_t) + \varepsilon_{g,t}$,
with governor fixed effects $\alpha_g$, half-year fixed effects $\gamma_t$, national HICP inflation $\pi$, and weights equal to the number of passages.

**Inference.** Randomisation inference: entire exposure paths are permuted across NCBs (999 draws). The test statistic is $\hat\beta$ divided by a leave-one-NCB-out jackknife standard error. Simulated size with actual passage counts: 5.2%. Two-sided test at 5%.

**H1.** Imputation estimator (Borusyak, Jaravel and Spiess) with governor and half-year fixed effects; randomisation inference over NCB cohort assignments.

**Multiple testing.** H3 is the single primary test. H1, H2 and H4 are adjusted with Romano-Wolf.

**Robustness (all reported).** R1 NCB instead of governor fixed effects; R3 dropping successors appointed after 2022; R4 no controls; R5 share-based outcome; R6 gross-loss treatment; R7 alternative classifier or human-only subsample; R8 Callaway-Sant'Anna for H1; R9 core-by-half-year fixed effects; R10 contemporaneous spread and debt; R11 excluding retrospective passages; all 12 exposure variants.

**Falsification.** F1 leads of exposure jointly zero; F2 Executive Board comparison smaller or zero; F3 placebo event dates for never-treated NCBs; F4 Slovenia's acting head without voting rights (descriptive); F5 R9 keeps sign and magnitude; F6 debt $\times$ DFR against exposure.

**What refutes H3.** $\hat\beta \geq 0$; or $\hat\beta$ vanishes under R9 or with the debt control; or significant leads.

# Measurement validation gate

- **Sample:** 400 masked passages, stratified by NCB size group and period; 50 Executive Board passages; 50 passages outside the keyword filter.
- **Coders:** 100 passages are coded by two independent human coders.
- **Gate:** Krippendorff's $\alpha \geq 0.667$ between humans for topic (nominal) **and** position (interval, passages both coders mark as on topic). Otherwise the codebook is revised and a new sample drawn before full classification.
- **Filter recall:** estimated with population weights. If below 0.80, the keyword filter is expanded before classification.
- **Classifier:** fixed model version, temperature 0, verbatim evidence quote required, all prompts and raw responses archived. Classification is completed and hash-frozen before any link to institution, date or treatment; the estimation code refuses to run otherwise.

# Pre-registered diagnostics already evaluated (outcome-blind)

- **Power (H3, controls, jackknife RI):** 74% at 0.25 and 88% at 0.30 scale points per standard deviation of exposure.
- **Power (H1):** 38 to 55% at 0.30 scale points. This is disclosed as underpowered.
- **Collinearity rule:** Pre-period debt $\times$ DFR leaves 99% of post-fixed-effects exposure variance; the within correlation is 0.09. The rule is not triggered.

# Out-of-sample protocol (H6)

**Window.** All NCB-head speeches dated 1 July 2026 to 31 December 2027 in the next BIS extracts. None of these passages is contained in the data used so far.

**Prediction, derived from theory and not from the estimate of $\beta$.** Governors whose NCB's relative exposure deteriorates more between 2026H1 and the out-of-sample window advocate relatively lower rates. Formally, across NCB heads, the change in mean stance $\Delta y_g$ (out-of-sample window minus 2026H1) is negatively rank-correlated with the change in standardised relative exposure $\Delta E_n$ over the same windows.

**Test.** Spearman rank correlation between $\Delta y_g$ and $-\Delta E_n$. Included are governors with at least two classified stance passages in both windows; if the governor changed, the NCB is used. One-sided permutation test (10,000 draws); prediction confirmed if $\rho>0$ with $p<0.05$. Exposure is computed with the baseline construction from ECB data available at the time of testing.

**Status of exposure at registration.** Most negative relative carry (end-August 2026): Germany, France, Belgium, Austria, the Netherlands, Finland. Least negative: Estonia, Greece, Malta, Latvia, Lithuania. Because policy rates rose in June and September 2026, relative exposure will deteriorate most for NCBs with above-average own holdings per point of key.

# Deviations

All deviations are logged with date, reason and data seen at the time in `docs/deviations.md`.
