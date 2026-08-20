#!/usr/bin/env bash
set -euo pipefail

ROOT="${LF_SMOKE_ROOT:-/tmp/loveforlove-smoke-products}"
COLLECTION="wedding-day-set"
PREPRESS_ROOT="$ROOT/$COLLECTION/prepress"

rm -rf "$ROOT/$COLLECTION"
mkdir -p "$ROOT/$COLLECTION"

python3 prepress/check_environment.py --require-profiles

xvfb-run -a scribus -g -ns -py \
  prepress/make_base_templates.py \
  "$COLLECTION" \
  "$ROOT"

COUNT="$(find "$PREPRESS_ROOT" -type f -name '*.sla' | wc -l | tr -d ' ')"
if [ "$COUNT" != "30" ]; then
  echo "Expected 30 Scribus templates, generated $COUNT" >&2
  exit 1
fi

python3 prepress/configure_template_cms.py "$PREPRESS_ROOT"

python3 - "$PREPRESS_ROOT" <<'PY'
import sys
from pathlib import Path

from prepress.template_preflight import validate_template
from print_package import PIECE_ORDER
from print_piece_specs import PRINT_PIECE_SPECS

root = Path(sys.argv[1])
validated = 0
for family in PRINT_PIECE_SPECS:
    for piece in PIECE_ORDER:
        path = root / family / f"{piece}.sla"
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"Missing/empty template: {path}")
        validate_template(path, family, piece)
        validated += 1

if validated != 30:
    raise SystemExit(f"Expected to validate 30 templates, validated {validated}")
print(f"Validated {validated} Scribus templates: geometry, bleed and CMS all passed.")
PY

# Files are created by the container's root user on a bind-mounted host path.
# Make the validated smoke package readable/traversable by the GitHub runner so
# actions/upload-artifact can zip it without changing template contents.
chmod -R a+rX "$ROOT/$COLLECTION"

echo "Smoke package ready at: $PREPRESS_ROOT"
