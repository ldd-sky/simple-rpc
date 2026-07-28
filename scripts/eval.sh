#!/usr/bin/env bash

set -euo pipefail

# Set these paths locally, or export them before launching:
#   export EVAL_ROOT=/path/to/evaluation_dataset
#   export CHECKPOINT=/path/to/checkpoint.pth
: "${EVAL_ROOT:?Please set EVAL_ROOT to the directory containing evaluation scenes.}"
: "${CHECKPOINT:?Please set CHECKPOINT to a DSER checkpoint.}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

python -m dser.cli.evaluate \
  --data_root "${EVAL_ROOT}" \
  --checkpoint "${CHECKPOINT}" \
  --frame_dir "${FRAME_DIR:-images}" \
  --event_dir "${EVENT_DIR:-events}" \
  --intervals "${INTERVALS:-1,3,7,15}" \
  --device "${DEVICE:-cuda}" \
  "$@"
