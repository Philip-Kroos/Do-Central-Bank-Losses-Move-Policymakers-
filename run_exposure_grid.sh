#!/usr/bin/env bash
# Pre-specified sensitivity grid for the carry exposure (assumptions A1-A3 in code/exposure/own_yield.py).
# usage: bash run_exposure_grid.sh H.csv W.csv Y.csv K.csv R.csv [EA.csv]
set -euo pipefail
EA_ARG=""; [ "${6:-}" != "" ] && EA_ARG="--ea-curve $6"
for method in net_flow ladder; do
  for pepp in 0.889 1.0; do
    for mm in 0.75 1.0 1.5; do
      python3 run_exposure.py --holdings "$1" --wam "$2" --yields "$3" --capital-key "$4" --rates "$5" $EA_ARG \
        --method "$method" --pepp-share "$pepp" --maturity-mult "$mm" --out output/exposure_grid > /dev/null
    done
  done
done
echo "12 configurations written to output/exposure_grid/"
