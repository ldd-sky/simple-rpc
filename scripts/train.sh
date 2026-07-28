#!/usr/bin/env bash

set -euo pipefail

# Set these paths to your local datasets, or export them before launching:
#   export BSERGB_ROOT=/path/to/BSERGB/3_TRAINING
#   export GOPRO_ROOT=/path/to/GOPRO
: "${BSERGB_ROOT:?Please set BSERGB_ROOT to the BSERGB training-set root.}"
: "${GOPRO_ROOT:?Please set GOPRO_ROOT to the GoPro dataset root.}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

python -m dser.cli.train \
  --bsergb_root "${BSERGB_ROOT}" \
  --gopro_root "${GOPRO_ROOT}" \
  --epoch 100 \
  --batch_size 6 \
  --num_worker 4 \
  "$@"
