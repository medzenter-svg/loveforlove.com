#!/usr/bin/env bash
set -euo pipefail

ROOT="/tmp/loveforlove-smoke-products"
COLLECTION="wedding-day-set"

rm -rf "$ROOT"
mkdir -p "$ROOT/$COLLECTION"

xvfb-run -a scribus -g -ns -py \
  prepress/make_base_templates.py \
  "$COLLECTION" \
  "$ROOT"

COUNT="$(find "$ROOT/$COLLECTION/prepress" -type f -name '*.sla' | wc -l | tr -d ' ')"
if [ "$COUNT" != "30" ]; then
  echo "Expected 30 Scribus templates, generated $COUNT" >&2
  exit 1
fi

for family in international_metric north_america; do
  for piece in \
    invitation venue_address rsvp menu table_number place_card program thank_you \
    accommodation coordinator dress_code envelope envelope_liner program_day_1 program_day_2; do
    test -s "$ROOT/$COLLECTION/prepress/$family/$piece.sla"
  done
done

echo "Generated and verified 30 non-empty Scribus templates."
