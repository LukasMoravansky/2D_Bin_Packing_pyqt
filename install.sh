#!/usr/bin/env bash
set -euo pipefail
ENV_NAME="${ENV_NAME:-2d-bin-packing}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found. Install Miniconda or use: pip install -r requirements.txt"
  exit 1
fi
conda create -n "$ENV_NAME" python=3.11 -y
# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
python -m pip install --upgrade pip
python -m pip install -r "$ROOT/requirements.txt"
echo "Done. Activate: conda activate $ENV_NAME"
echo "Run app: python -m App.main"
echo "Verify: python verify.py"
