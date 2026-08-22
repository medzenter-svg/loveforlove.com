"""Stress-test Scribus export across the 11 active store languages.

The test exports every one of the 15 wedding pieces in the tighter international
metric geometry using PDF/X-4. This gives 11 languages x 15 pieces = 165 real PDFs.
Each PDF must pass the same structural preflight used by production package builds.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

STORE_DIR = Path(__file__).resolve().parents[1]
if str(STORE_DIR) not in sys.path:
    sys.path.insert(0, str(STORE_DIR))

from print_package import PIECE_ORDER
from prepress.build_package import _scribus_command
from prepress.job import normalize_print_job
from prepress.preflight import PreflightError, preflight_pdf
from prepress.template_preflight import TemplatePreflightError, validate_template
from suite_locales import LANGUAGE_NAMES, SUITE_LOCALES
from suite_optional_locales import OPTIONAL_SUITE_LOCALES
from suite_weekend_locales import WEEKEND_SUITE_LOCALES


SIZE_FAMILY = "international_metric"
PRINT_PROFILE = "pdfx4_worldwide"
ACTIVE_LANGUAGES = (
    "en", "de", "fr", "it", "es", "pt", "nl", "pl", "el", "ru", "tr",
)

SCRIPT_STRESS_FIELDS = {
    "de": {"coupleNames": "Charlotte & Maximilian", "venueName": "Schloss Nymphenburg", "thankMessage": "Danke, dass ihr diesen besonderen Tag mit uns feiert."},
    "fr": {"coupleNames": "Élodie & François", "venueName": "Château de Vaux-le-Vicomte", "thankMessage": "Merci d'avoir partagé cette journée inoubliable avec nous."},
    "it": {"coupleNames": "Sofia & Alessandro", "venueName": "Villa del Balbianello", "thankMessage": "Grazie per aver festeggiato con noi questa giornata indimenticabile."},
    "es": {"coupleNames": "Lucía & Sebastián", "venueName": "Palacio de Cibeles", "thankMessage": "Gracias por celebrar con nosotros este día inolvidable."},
    "pt": {"coupleNames": "Inês & João", "venueName": "Palácio de Monserrate", "thankMessage": "Obrigado por celebrarem connosco este dia inesquecível."},
    "nl": {"coupleNames": "Sophie & Daan", "venueName": "Kasteel de Haar", "thankMessage": "Dank jullie wel dat jullie deze onvergetelijke dag met ons vieren."},
    "pl": {"coupleNames": "Zofia & Michał", "venueName": "Pałac w Wilanowie", "thankMessage": "Dziękujemy, że świętujecie z nami ten niezapomniany dzień."},
    "el": {
        "coupleNames": "Αλεξάνδρα & Νικόλαος",
        "venueName": "Κτήμα Αριάδνη",
        "guestName": "Ελένη Παπαδοπούλου",
        "thankMessage": "Σας ευχαριστούμε που γιορτάζετε μαζί μας αυτή την αξέχαστη ημέρα.",
        "dressStyle": "Λευκή γιορτή",
        "dayOneEvent1": "Καλωσόρισμα",
        "dayTwoEvent3": "Αποχαιρετιστήριο απεριτίφ",
    },
    "ru": {
        "coupleNames": "Екатерина & Александр",
        "venueName": "Вилла дель Бальбьянелло",
        "guestName": "София Миллер",
        "thankMessage": "Спасибо, что разделяете с нами этот незабываемый день.",
        "dressStyle": "Белая церемония",
        "dayOneEvent1": "Встреча гостей",
        "dayTwoEvent3": "Прощальный аперитив",
    },
    "tr": {"coupleNames": "İrem & Çağrı", "venueName": "Çırağan Sarayı", "thankMessage": "Bu unutulmaz günü bizimle kutladığınız için teşekkür ederiz."},
}


def _load_example(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError("JOB_EXAMPLE.json must contain an object")
    return raw


def _labels_for(language: str):
    labels = {}
    labels.update(SUITE_LOCALES[language])
    labels.update(OPTIONAL_SUITE_LOCALES[language])
    labels.update(WEEKEND_SUITE_LOCALES[language])
    return labels


def _job_for(language: str, example: dict):
    fields = dict(example.get("fields") or {})
    fields.update(SCRIPT_STRESS_FIELDS.get(language, {}))
    return normalize_print_job(example["collection_slug"], {
        "collection_slug": example["collection_slug"],
        "language": language,
        "enabled_optional": list(example.get("enabled_optional") or []),
        "fields": fields,
        "labels": _labels_for(language),
    })


def _run_scribus(template: Path, output: Path, job_file: Path, scribus_bin: str):
    proc = subprocess.run(
        _scribus_command(scribus_bin, template, output, job_file, PRINT_PROFILE),
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(
            f"Scribus multilingual export failed for {output.name}\n"
            f"Return code: {proc.returncode}\nSTDOUT:\n{proc.stdout or '(empty)'}\nSTDERR:\n{proc.stderr or '(empty)'}"
        )


def run(template_root: Path, output_root: Path, example_path: Path, scribus_bin: str = "scribus"):
    template_root = template_root.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if any(output_root.iterdir()):
        raise RuntimeError(f"Multilingual smoke output must be empty: {output_root}")

    for language in ACTIVE_LANGUAGES:
        if language not in SUITE_LOCALES or language not in OPTIONAL_SUITE_LOCALES or language not in WEEKEND_SUITE_LOCALES:
            raise RuntimeError(f"Missing locale data for active language: {language}")

    example = _load_example(example_path)
    results = []
    for language in ACTIVE_LANGUAGES:
        job = _job_for(language, example)
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"-{language}.json", encoding="utf-8", delete=False) as handle:
            json.dump(job, handle, ensure_ascii=False, indent=2)
            job_path = Path(handle.name)
        try:
            for piece in PIECE_ORDER:
                template = template_root / SIZE_FAMILY / f"{piece}.sla"
                try:
                    validate_template(template, SIZE_FAMILY, piece)
                except TemplatePreflightError as exc:
                    raise RuntimeError(f"Template preflight failed for {language}/{piece}: {exc}") from exc
                filename = f"{language}__{piece}__METRIC__PDFX4.pdf"
                output = output_root / filename
                _run_scribus(template, output, job_path, scribus_bin)
                try:
                    preflight_pdf(output, SIZE_FAMILY, piece, PRINT_PROFILE)
                except PreflightError as exc:
                    raise RuntimeError(f"PDF preflight failed for {language}/{piece}: {exc}") from exc
                results.append({
                    "language": language,
                    "language_name": LANGUAGE_NAMES[language],
                    "piece": piece,
                    "filename": filename,
                    "status": "passed",
                    "bytes": output.stat().st_size,
                })
        finally:
            job_path.unlink(missing_ok=True)

    expected_count = len(ACTIVE_LANGUAGES) * len(PIECE_ORDER)
    if len(results) != expected_count:
        raise RuntimeError(f"Expected {expected_count} multilingual PDFs, produced {len(results)}")

    manifest = {
        "status": "preflight_passed",
        "size_family": SIZE_FAMILY,
        "print_profile": PRINT_PROFILE,
        "languages": list(ACTIVE_LANGUAGES),
        "language_count": len(ACTIVE_LANGUAGES),
        "piece_count_per_language": len(PIECE_ORDER),
        "professional_pdf_count": len(results),
        "files": results,
        "note": "Typography/glyph/layout stress smoke only; final design and translation review remain separate release gates.",
    }
    manifest_path = output_root / "MULTILINGUAL_SMOKE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template_root")
    parser.add_argument("output_root")
    parser.add_argument("example_job")
    parser.add_argument("--scribus", default="scribus")
    args = parser.parse_args()
    manifest = run(Path(args.template_root), Path(args.output_root), Path(args.example_job), scribus_bin=args.scribus)
    print(f"Multilingual smoke passed: {manifest}")


if __name__ == "__main__":
    main()
