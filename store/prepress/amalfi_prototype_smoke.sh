#!/usr/bin/env bash
set -euo pipefail

ROOT="${LF_AMALFI_SMOKE_ROOT:-/tmp/loveforlove-amalfi-prototype}"
COLLECTION="wedding-day-set"
PREPRESS_ROOT="$ROOT/$COLLECTION/prepress"
OUTPUT_ROOT="$ROOT/$COLLECTION/amalfi-invitation-prototype"

rm -rf "$ROOT/$COLLECTION"
mkdir -p "$ROOT/$COLLECTION"

python3 prepress/check_environment.py --require-profiles

xvfb-run -a scribus -g -ns -py \
  prepress/make_base_templates.py \
  "$COLLECTION" \
  "$ROOT"

test "$(find "$PREPRESS_ROOT" -type f -name '*.sla' | wc -l | tr -d ' ')" = "30"

# Apply only the gated Amalfi Invitation prototype. The theme remains blocked
# from full-package export and sale.
xvfb-run -a scribus -g -ns -py \
  prepress/apply_amalfi_prototype.py \
  "$PREPRESS_ROOT"

xvfb-run -a scribus -g -ns -py \
  prepress/check_template_fonts.py \
  "$PREPRESS_ROOT"

python3 prepress/configure_template_cms.py "$PREPRESS_ROOT"

python3 prepress/export_smoke.py \
  "$PREPRESS_ROOT" \
  "$OUTPUT_ROOT" \
  prepress/AMALFI_PROTOTYPE_JOB.json

PDF_COUNT="$(find "$OUTPUT_ROOT" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
if [ "$PDF_COUNT" != "4" ]; then
  echo "Expected 4 Amalfi Invitation prototype PDFs, generated $PDF_COUNT" >&2
  exit 1
fi

test -f "$OUTPUT_ROOT/INVITATION_EXPORT_SMOKE_MANIFEST.json"

chmod -R a+rX "$ROOT/$COLLECTION"

echo "Amalfi Luce Invitation prototype ready at: $OUTPUT_ROOT"
