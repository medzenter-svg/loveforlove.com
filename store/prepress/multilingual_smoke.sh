#!/usr/bin/env bash
set -euo pipefail

ROOT="${LF_MULTILINGUAL_SMOKE_ROOT:-/tmp/loveforlove-multilingual-smoke}"
COLLECTION="wedding-day-set"
PREPRESS_ROOT="$ROOT/$COLLECTION/prepress"
OUTPUT_ROOT="$ROOT/$COLLECTION/multilingual"
REVIEW_ROOT="$ROOT/$COLLECTION/multilingual-review"

rm -rf "$ROOT/$COLLECTION"
mkdir -p "$ROOT/$COLLECTION"

python3 prepress/check_environment.py --require-profiles

xvfb-run -a scribus -g -ns -py \
  prepress/make_base_templates.py \
  "$COLLECTION" \
  "$ROOT"

python3 prepress/configure_template_cms.py "$PREPRESS_ROOT"

test "$(find "$PREPRESS_ROOT" -type f -name '*.sla' | wc -l | tr -d ' ')" = "30"

python3 prepress/multilingual_smoke.py \
  "$PREPRESS_ROOT" \
  "$OUTPUT_ROOT" \
  prepress/JOB_EXAMPLE.json

PDF_COUNT="$(find "$OUTPUT_ROOT" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
if [ "$PDF_COUNT" != "195" ]; then
  echo "Expected 195 multilingual PDF/X smoke files, generated $PDF_COUNT" >&2
  exit 1
fi

test -f "$OUTPUT_ROOT/MULTILINGUAL_SMOKE_MANIFEST.json"

# Keep the full 195-file set inside the job for validation, but upload a compact
# visual-review artifact: all 13 languages for three typography-sensitive pieces.
mkdir -p "$REVIEW_ROOT"
cp "$OUTPUT_ROOT/MULTILINGUAL_SMOKE_MANIFEST.json" "$REVIEW_ROOT/"
for language in en de fr it es pt nl pl el ru uk tr he; do
  for piece in invitation coordinator program_day_1; do
    cp "$OUTPUT_ROOT/${language}__${piece}__METRIC__PDFX4.pdf" "$REVIEW_ROOT/"
  done
done

chmod -R a+rX "$ROOT/$COLLECTION"

echo "Validated 195 multilingual PDFs."
echo "Review artifact ready at: $REVIEW_ROOT"
