#!/usr/bin/env bash
set -euo pipefail

ROOT="${LF_FULL_SMOKE_ROOT:-/tmp/loveforlove-full-smoke-products}"
COLLECTION="wedding-day-set"
PREPRESS_ROOT="$ROOT/$COLLECTION/prepress"
OUTPUT_ROOT="$ROOT/$COLLECTION/full-package-smoke"

rm -rf "$ROOT/$COLLECTION"
mkdir -p "$ROOT/$COLLECTION"

python3 prepress/check_environment.py --require-profiles

xvfb-run -a scribus -g -ns -py \
  prepress/make_base_templates.py \
  "$COLLECTION" \
  "$ROOT"

TEMPLATE_COUNT="$(find "$PREPRESS_ROOT" -type f -name '*.sla' | wc -l | tr -d ' ')"
if [ "$TEMPLATE_COUNT" != "30" ]; then
  echo "Expected 30 Scribus templates, generated $TEMPLATE_COUNT" >&2
  exit 1
fi

xvfb-run -a scribus -g -ns -py \
  prepress/check_template_fonts.py \
  "$PREPRESS_ROOT"

python3 prepress/configure_template_cms.py "$PREPRESS_ROOT"

python3 prepress/build_package.py \
  prepress/JOB_EXAMPLE.json \
  "$OUTPUT_ROOT" \
  --product-root "$ROOT"

PDF_COUNT="$(find "$OUTPUT_ROOT" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
if [ "$PDF_COUNT" != "60" ]; then
  echo "Expected 60 professional smoke PDFs, generated $PDF_COUNT" >&2
  exit 1
fi

if [ ! -f "$OUTPUT_ROOT/PRINT_PACKAGE_MANIFEST.json" ]; then
  echo "Missing PRINT_PACKAGE_MANIFEST.json" >&2
  exit 1
fi

python3 - "$OUTPUT_ROOT/PRINT_PACKAGE_MANIFEST.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
if data.get("status") != "preflight_passed":
    raise SystemExit(f"Unexpected package status: {data.get('status')}")
if data.get("professional_pdf_count") != 60:
    raise SystemExit(f"Expected manifest count 60, got {data.get('professional_pdf_count')}")
files = data.get("files") or []
if len(files) != 60 or any(item.get("status") != "passed" for item in files):
    raise SystemExit("Manifest does not contain 60 passed PDF entries")
print("Full professional package manifest confirms 60 structurally preflighted PDFs.")
PY

chmod -R a+rX "$ROOT/$COLLECTION"
echo "Full 60-file package smoke ready at: $OUTPUT_ROOT"
