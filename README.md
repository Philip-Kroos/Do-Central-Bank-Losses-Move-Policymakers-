# Do Central Bank Losses Move Policymakers?
## Pre-Registered Evidence from the Eurosystem

**Philip Kroos — 15 September 2026**

This repository contains the paper, code, derived and hand-collected data, pre-registration documents, coded passage labels, and replication outputs for:

> **Do Central Bank Losses Move Policymakers? Pre-Registered Evidence from the Eurosystem**

[Read the paper (PDF)](paper/main.pdf)

## Research question

Since 2022, euro-area national central banks have incurred large losses on bond portfolios purchased under quantitative easing. The paper asks whether these losses affect the publicly stated interest-rate preferences of the governors who sit on the ECB Governing Council.

The empirical design uses cross-NCB variation in non-pooled sovereign-bond carry exposure and a blinded text-as-data measure of rate advocacy. The analysis is based on 1,991 filtered passages from speeches by euro-area NCB governors between 2016 and 2026; 1,248 passages state a view on the policy rate and enter the governor-half-year panel.

## Main result

The baseline estimate is **0.034 rate-stance scale points per standard deviation of exposure** (SE 0.187; permutation p-value 0.81; 95% CI [-0.33, 0.40]). The result is stable across the pre-specified exposure constructions and robustness checks. The paper therefore finds no detectable response of individual rate advocacy to the finances of the governor's own central bank, while smaller effects cannot be excluded.

## Repository structure

```text
.
├── paper/                 Final PDF, LaTeX source, bibliography, figures
├── code/                  Corpus, classification, exposure, estimation, validation code
├── data/
│   ├── hand/              Hand-collected institutional inputs
│   └── derived/           Derived inputs used by the analysis
├── output/                Frozen coding labels and final analysis outputs
├── power/                 Ex-ante power and sensitivity calculations
├── model/                 Numerical/symbolic model verification
├── docs/                  Pre-registration, amendments, codebook, deviations, hashes
├── tests/                 Unit and pipeline tests
├── README_REPLICATION.md  Detailed replication notes
└── requirements.txt       Python dependencies
```

## Measurement disclosure

The final 1,991 filtered passages were coded in a single blinded language-model pass under the frozen codebook. No independent human validation sample was ultimately coded, so the repository contains no human-model agreement statistic or estimate of filter recall. This is treated as the paper's main measurement limitation.

The repository contains the masked coding queue and the frozen labels used in estimation. The complete BIS speech archive is not redistributed here; instructions for obtaining external source data are in [`docs/data_download.md`](docs/data_download.md).

## Reproduction

The analysis was developed under **Python 3.12.3**. Install the listed dependencies, then see [`README_REPLICATION.md`](README_REPLICATION.md) for the full workflow.

A typical starting point is:

```bash
python -m pip install -r requirements.txt
python -m pytest -q -p no:debugging tests
```

The `-p no:debugging` option avoids a namespace collision between the repository's historical `code/` package name and Python's standard-library `code` module when pytest loads its debugging plugin.

## Pre-registration and deviations

The analysis plan and subsequent amendments are stored in [`docs/`](docs/), together with SHA-256 hashes. [`docs/deviations.md`](docs/deviations.md) records departures from the frozen plan and the information available when each change was made.

## Citation

If you use this repository, please cite the paper:

> Kroos, Philip (2026). *Do Central Bank Losses Move Policymakers? Pre-Registered Evidence from the Eurosystem*. Draft, 15 September 2026.
