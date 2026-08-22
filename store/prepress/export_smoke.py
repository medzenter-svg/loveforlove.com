"""Export and structurally preflight one Invitation across all release variants.

This smoke test proves the real Scribus export path before attempting the complete
15-piece / 60-file wedding package. It exports:
- international_metric + PDF/X-4
- international_metric + PDF/X-1a
- north_america + PDF/X-4
- north_america + PDF/X-1a
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

STORE_DIR = Path(__file__).resolve().parents[1]
if str(STORE_DIR) not in sys.path:
    sys.path.insert(0, str(STORE_DIR))

from prepress.build_package import _scribus_command
from prepress.job import PrintJobValidationError, normalize_print_job
from prepress.preflight import PreflightError, preflight_pdf
from prepress.template_preflight import TemplatePreflightError, validate_template


PIECE = "invitation"
SIZE_FAMILIES = ("international_metric", "north_america")
PRINT_PROFILES = ("pdfx4_worldwide", "pdfx1a_compatibility")


def _load_and_normalize_job(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise RuntimeError("Smoke print job must be a JSON object")
    collection_slug = raw.get("collection_slug")
    if not collection_slug:
        raise RuntimeError("Smoke print job is missing collection_slug")
    try:
        return normalize_print_job(collection_slug, raw)
    except PrintJobValidationError as exc:
        raise RuntimeError(f"Invalid smoke print job: {exc}") from exc


def _filename(collection_slug: str, size_family: str, profile: str) -> str:
    family_token = "METRIC" if size_family == "international_metric" else "NA"
    profile_token = "PDFX4" if profile == "pdfx4_worldwide" else "PDFX1A"
    return f"{collection_slug}__{PIECE}__{family_token}__{profile_token}.pdf"


def run(template_root: Path, output_root: Path, job_file: Path, scribus_bin: str = "scribus"):
    template_root = template_root.resolve()
    output_root = output_root.resolve()
    job_file = job_file.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    if any(output_root.iterdir()):
        raise RuntimeError(f"Smoke PDF output directory must be empty: {output_root}")

    job = _load_and_normalize_job(job_file)
    normalized_job = output_root / "_normalized_job.json"
    normalized_job.write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")

    results = []
    try:
        for size_family in SIZE_FAMILIES:
            template = template_root / size_family / f"{PIECE}.sla"
            try:
                validate_template(template, size_family, PIECE)
            except TemplatePreflightError as exc:
                raise RuntimeError(
                    f"Template preflight failed for {PIECE}/{size_family}: {exc}"
                ) from exc

            for profile in PRINT_PROFILES:
                filename = _filename(job["collection_slug"], size_family, profile)
                output = output_root / filename
                command = _scribus_command(
                    scribus_bin,
                    template,
                    output,
                    normalized_job,
                    profile,
                )
                proc = subprocess.run(command, text=True, capture_output=True)
                if proc.returncode != 0:
                    raise RuntimeError(
                        f"Scribus smoke export failed for {filename}\n"
                        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
                    )
                try:
                    preflight_pdf(output, size_family, PIECE, profile)
                except PreflightError as exc:
                    raise RuntimeError(f"PDF smoke preflight failed for {filename}: {exc}") from exc

                results.append({
                    "filename": filename,
                    "piece": PIECE,
                    "size_family": size_family,
                    "print_profile": profile,
                    "status": "passed",
                    "bytes": output.stat().st_size,
                })
    finally:
        normalized_job.unlink(missing_ok=True)

    if len(results) != 4:
        raise RuntimeError(f"Expected 4 Invitation smoke PDFs, produced {len(results)}")

    manifest = {
        "collection_slug": job["collection_slug"],
        "piece": PIECE,
        "status": "structural_preflight_passed",
        "pdf_count": len(results),
        "files": results,
        "note": (
            "Real Scribus PDF/X exports passed structural preflight. This is not yet "
            "a certified PDF/X conformance validation or final visual design approval."
        ),
    }
    manifest_path = output_root / "INVITATION_EXPORT_SMOKE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template_root")
    parser.add_argument("output_root")
    parser.add_argument("job_file")
    parser.add_argument("--scribus", default="scribus")
    args = parser.parse_args()

    manifest = run(
        Path(args.template_root),
        Path(args.output_root),
        Path(args.job_file),
        scribus_bin=args.scribus,
    )
    print(f"Invitation export smoke passed: {manifest}")


if __name__ == "__main__":
    main()
