#!/usr/bin/env bash
set -euo pipefail

ROOT="${LF_PROTOTYPE_SMOKE_ROOT:-/tmp/loveforlove-invitation-prototypes}"
COLLECTION="wedding-day-set"
THEMES=("amalfi-luce" "monaco-regatta" "como-sereno")

rm -rf "$ROOT"
mkdir -p "$ROOT"

python3 prepress/check_environment.py --require-profiles

for THEME in "${THEMES[@]}"; do
  THEME_ROOT="$ROOT/$THEME"
  PREPRESS_ROOT="$THEME_ROOT/$COLLECTION/prepress"
  EXPORT_ROOT="$THEME_ROOT/export"
  MARKER="$PREPRESS_ROOT/.loveforlove-prototype-$THEME"

  mkdir -p "$THEME_ROOT"

  xvfb-run -a scribus -g -ns -py \
    prepress/make_base_templates.py \
    "$COLLECTION" \
    "$THEME_ROOT"

  test "$(find "$PREPRESS_ROOT" -type f -name '*.sla' | wc -l | tr -d ' ')" = "30"

  xvfb-run -a scribus -g -ns -py \
    prepress/apply_premium_design.py \
    "$PREPRESS_ROOT" \
    "$THEME" \
    --prototype \
    --piece=invitation

  # Scribus can occasionally exit 0 after an internal Scripter exception. Require
  # an explicit success marker plus theme-specific vector objects in both sizes.
  test -f "$MARKER"
  grep -q "^theme=$THEME$" "$MARKER"
  grep -q '^piece=invitation$' "$MARKER"
  grep -q '^templates=2$' "$MARKER"

  for SLA in \
    "$PREPRESS_ROOT/international_metric/invitation.sla" \
    "$PREPRESS_ROOT/north_america/invitation.sla"
  do
    case "$THEME" in
      amalfi-luce)
        grep -q 'design__amalfi_arch' "$SLA"
        grep -q 'design__amalfi_olive_left' "$SLA"
        grep -q 'design__amalfi_coral_mark' "$SLA"
        ;;
      monaco-regatta)
        grep -q 'design__monaco_mast' "$SLA"
        grep -q 'design__monaco_signal' "$SLA"
        grep -q 'design__monaco_diagonal' "$SLA"
        ;;
      como-sereno)
        grep -q 'design__como_water_1' "$SLA"
        grep -q 'design__como_water_2' "$SLA"
        grep -q 'design__como_sage' "$SLA"
        ;;
      *)
        echo "Unknown prototype theme: $THEME" >&2
        exit 1
        ;;
    esac
  done

  xvfb-run -a scribus -g -ns -py \
    prepress/check_template_fonts.py \
    "$PREPRESS_ROOT"

  python3 prepress/configure_template_cms.py "$PREPRESS_ROOT"

  python3 prepress/export_smoke.py \
    "$PREPRESS_ROOT" \
    "$EXPORT_ROOT" \
    prepress/JOB_EXAMPLE.json

  PDF_COUNT="$(find "$EXPORT_ROOT" -maxdepth 1 -type f -name '*.pdf' | wc -l | tr -d ' ')"
  if [ "$PDF_COUNT" != "4" ]; then
    echo "Expected 4 Invitation PDFs for $THEME, generated $PDF_COUNT" >&2
    exit 1
  fi

  mv "$EXPORT_ROOT/INVITATION_EXPORT_SMOKE_MANIFEST.json" "$EXPORT_ROOT/${THEME}__MANIFEST.json"
  echo "$THEME: 4 Invitation PDF/X prototype files passed structural preflight."
done

TOTAL="$(find "$ROOT" -type f -name '*.pdf' | wc -l | tr -d ' ')"
if [ "$TOTAL" != "12" ]; then
  echo "Expected 12 total prototype PDFs, generated $TOTAL" >&2
  exit 1
fi

chmod -R a+rX "$ROOT"
echo "Three-theme Invitation prototype smoke ready at: $ROOT"
