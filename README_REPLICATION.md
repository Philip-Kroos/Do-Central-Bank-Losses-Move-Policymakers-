# Replication notes

## Overview

This repository contains the code and analysis inputs used to build:

1. the governor-level rate-stance measure from BIS speeches;
2. NCB-specific non-pooled carry exposure from ECB programme and yield data;
3. hand-collected NCB loss, provision, treatment-date and governor information; and
4. the estimates, robustness checks, power calculations, figures and tables reported in the paper.

The final classification labels are hash-frozen in `docs/classification_freeze.sha256`.

## Data availability

| Data | Source | Included here? |
|---|---|---|
| BIS central-bank speech archive | Bank for International Settlements | Full archive: **No**. Masked coding queue and final labels used in the analysis: **Yes** |
| PSPP/PEPP purchase histories, ECB rates and yield inputs | European Central Bank | Raw source downloads: **No**. Derived analysis inputs: **Yes** |
| Government debt ratios, 2019-2021 | Eurostat / hand transcription | **Yes** |
| Eurosystem capital-key inputs | ECB / hand transcription | **Yes** |
| NCB results, loss dates, provisions and governor information | NCB annual accounts, releases and related public sources | **Yes** |
| Final language-model classification labels | Frozen coding output | **Yes** |
| Independent human validation codes | — | **No; not performed** |
| National HICP control from the pre-analysis plan | ECB/Eurostat | **No; not implemented in the reported analysis** |

See `docs/data_download.md` and `docs/deviations.md` for source and deviation details.

## Software

The analysis was developed with Python 3.12.3. The original environment documented:

- sympy 1.14.0
- numpy 2.4.4
- pandas 3.0.2
- statsmodels 0.15.0
- scipy 1.17.1
- matplotlib 3.10.8
- pytest
- krippendorff

LaTeX (`pdflatex`, `bibtex`) is required to rebuild the paper.

## Suggested workflow

### 1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Run tests

```bash
python -m pytest -q -p no:debugging tests
```

The debugging plugin is disabled because the historical package name `code/` collides with Python's standard-library `code` module when pytest imports `pdb`.

### 3. Build exposure inputs

```bash
python build_exposure_inputs.py
```

For a complete from-scratch rebuild, download the external source files described in `docs/data_download.md` first.

### 4. Rebuild exposure measures

```bash
python run_exposure.py
```

The robustness grid is produced by `run_exposure_grid.sh`.

### 5. Rebuild treatment dates and corpus counts

```bash
python code/exposure/treatment_dates.py
python run_go_nogo.py --bis <BIS_SPEECH_FILE> --roster data/hand/governor_roster.csv
```

### 6. Classification stage

The scripts and frozen codebook are retained for auditability. The labels actually used in the final analysis are in:

```text
output/coding/results_heads_frozen.csv
```

The masked queue is:

```text
output/coding/queue_heads.json
```

No independent human validation coding was completed; see `docs/deviations.md` and the paper's measurement discussion.

### 7. Estimation and full report

```bash
python run_estimation.py --results output/coding/results_heads_frozen.csv
python run_full_report.py
```

The final stored outputs used for the paper are under `output/estimation_full/`, `output/exposure/`, and `output/exposure_grid/`.

### 8. Rebuild the paper

```bash
cd paper
pdflatex main
bibtex main
pdflatex main
pdflatex main
```
