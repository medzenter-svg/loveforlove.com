"""Build and preflight the complete professional print package for one order.

The build is atomic: all PDFs are generated and validated in a temporary staging
directory. Nothing is published to the requested output directory unless every
expected piece passes template checks, Scribus export and PDF structural preflight.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STORE_DIR = Path(__file__).resolve().parents[1]
if str(STORE_DIR) not in sys.path:
    sys.path.insert(0, str(STORE_DIR))

from print_package import build_manifest
from prepress.job import PrintJobValidationError, normalize_print_job
from prepress.preflight import PreflightError, preflight_pdf
from prepress.template_preflight import TemplatePreflightError, validate_template


SCRIPT_DIR = Path(__file__).resolve().parent
SCRIBUS_EXPORT_SCRIPT = SCRIPT_DIR / "export_scribus.py"


def _load_job(path):
    with open(path, "r", encoding="utf-8") as handle:
        raw_job = json.load(handle)
    if not isinstance(raw_job, dict):
        raise RuntimeError("Print job JSON must be an object")

    collection_slug = raw_job.get("collection_slug")
    if not isinstance(collection_slug, str) or not collection_slug:
        raise RuntimeError("Print job is missing collection_slug")

    try:
        return normalize_print_job(collection_slug, raw_job)
    except PrintJobValidationError as exc:
        raise RuntimeError(f"Invalid print job: {exc}") from exc


def _enabled_optional(job):
    return set(job.get("enabled_optional") or [])


def _scribus_command(scribus_bin, template, output, job_file, profile):
    command = [
        scribus_bin,
        "-g",
        "-ns",
        "-py",
        str(SCRIBUS_EXPORT_SCRIPT),
        str(template),
        str(output),
        str(job_file),
        profile,
    ]
    if os.name != "nt" and shutil.which("xvfb-run"):
        command = ["xvfb-run", "-a"] + command
    return command


def _template_path(product_root, collection_slug, size_family, piece):
    return product_root / collection_slug / "prepress" / size_family / f"{piece}.sla"


def _write_normalized_temp_job(job):
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="loveforlove-print-job-",
        encoding="utf-8",
        delete=False,
    )
    try:
        json.dump(job, handle, ensure_ascii=False, indent=2)
        handle.flush()
        return Path(handle.name)
    finally:
        handle.close()


def _ensure_clean_destination(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = list(output_dir.glob("*.pdf"))
    manifest = output_dir / "PRINT_PACKAGE_MANIFEST.json"
    if existing or manifest.exists():
        raise RuntimeError(
            "Output directory already contains a professional package. "
            "Use a fresh order/package directory to prevent mixed revisions."
        )


def build(job_file, output_dir, scribus_bin="scribus", product_root=None):
    job_file = Path(job_file).resolve()
    output_dir = Path(output_dir).resolve()
    product_root = Path(product_root or (STORE_DIR.parent / "products")).resolve()
    _ensure_clean_destination(output_dir)

    job = _load_job(job_file)
    collection_slug = job["collection_slug"]
    manifest = build_manifest(collection_slug, _enabled_optional(job))
    normalized_job_file = _write_normalized_temp_job(job)

    results = []
    try:
        with tempfile.TemporaryDirectory(prefix="loveforlove-prepress-stage-") as staging_raw:
            staging_dir = Path(staging_raw)

            for item in manifest:
                template = _template_path(
                    product_root,
                    collection_slug,
                    item["size_family"],
                    item["piece"],
                )
                try:
                    validate_template(template, item["size_family"], item["piece"])
                except TemplatePreflightError as exc:
                    raise RuntimeError(
                        f"Template preflight failed for {item['piece']}/{item['size_family']}: {exc}"
                    ) from exc

                staged_output = staging_dir / item["filename"]
                command = _scribus_command(
                    scribus_bin,
                    template,
                    staged_output,
                    normalized_job_file,
                    item["print_profile"],
                )
                proc = subprocess.run(command, text=True, capture_output=True)
                if proc.returncode != 0:
                    raise RuntimeError(
                        f"Scribus export failed for {item['filename']}\n"
                        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
                    )

                try:
                    preflight_pdf(
                        staged_output,
                        item["size_family"],
                        item["piece"],
                        item["print_profile"],
                    )
                except PreflightError as exc:
                    raise RuntimeError(
                        f"PDF preflight failed for {item['filename']}: {exc}"
                    ) from exc

                results.append({
                    "filename": item["filename"],
                    "piece": item["piece"],
                    "size_family": item["size_family"],
                    "print_profile": item["print_profile"],
                    "status": "passed",
                })

            release_manifest = {
                "collection_slug": collection_slug,
                "status": "preflight_passed",
                "professional_pdf_count": len(results),
                "files": results,
                "note": (
                    "Structural preflight passed. Final commercial release should also be "
                    "checked in the designated certified PDF/X validation workflow."
                ),
            }
            staged_manifest = staging_dir / "PRINT_PACKAGE_MANIFEST.json"
            staged_manifest.write_text(
                json.dumps(release_manifest, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            # Atomic publication at package level: only move verified artifacts
            # into the customer output directory after the complete set passed.
            for artifact in staging_dir.iterdir():
                shutil.move(str(artifact), str(output_dir / artifact.name))
    finally:
        try:
            normalized_job_file.unlink(missing_ok=True)
        except Exception:
            pass

    return output_dir / "PRINT_PACKAGE_MANIFEST.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("job_file")
    parser.add_argument("output_dir")
    parser.add_argument("--scribus", default=os.environ.get("SCRIBUS_BIN", "scribus"))
    parser.add_argument("--product-root", default=None)
    args = parser.parse_args()

    manifest = build(
        args.job_file,
        args.output_dir,
        scribus_bin=args.scribus,
        product_root=args.product_root,
    )
    print(manifest)


if __name__ == "__main__":
    main()
