#!/usr/bin/env bash
set -euo pipefail

python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium

echo "Render build complete: Python dependencies, Chromium, and Linux browser dependencies installed."
