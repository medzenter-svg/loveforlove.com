"""Run inside Scribus Scripter to personalize one SLA template and export PDF/X.

CLI example:
  scribus -g -ns -py export_scribus.py template.sla output.pdf job.json pdfx4_worldwide

Scribus requires -py/--python-script to be the last Scribus option. Tokens after
the script path are passed directly to the Python script as arguments.

The SLA template owns all visual design, page geometry, document bleed and color
management. Editable text frames use these names:
  txt__<field-key>   for customer values
  lbl__<label-key>   for translated/custom labels

The script never changes the source template on disk.
"""

import json
import os
import sys

import scribus


PDF_VERSION = {
    # Current Scribus Scripter enum from objpdffile.cpp:
    # 10 = PDF/X-4, 11 = PDF/X-1a, 12 = PDF/X-3.
    "pdfx4_worldwide": 10,
    "pdfx1a_compatibility": 11,
}


def _arguments():
    args = sys.argv[1:]
    if len(args) != 4:
        raise RuntimeError(
            "Expected: template.sla output.pdf job.json <pdfx4_worldwide|pdfx1a_compatibility>"
        )
    template, output, job_path, profile = args
    if profile not in PDF_VERSION:
        raise RuntimeError(f"Unknown print profile: {profile}")
    return template, output, job_path, profile


def _load_job(path):
    with open(path, "r", encoding="utf-8") as handle:
        job = json.load(handle)
    if not isinstance(job, dict):
        raise RuntimeError("Print job JSON must be an object")
    return job


def _replace_frames(prefix, values):
    for key, value in (values or {}).items():
        frame_name = f"{prefix}{key}"
        if not scribus.objectExists(frame_name):
            continue
        scribus.setText(str(value or ""), frame_name)


def _check_text_overflow():
    overflow = []
    for item in scribus.getAllObjects():
        if not (item.startswith("txt__") or item.startswith("lbl__")):
            continue
        try:
            if scribus.textOverflows(item, 1):
                overflow.append(item)
        except Exception:
            continue
    if overflow:
        raise RuntimeError("Text overflow in frames: " + ", ".join(sorted(overflow)))


def _export_pdf(output_path, profile):
    pdf = scribus.PDFfile()
    pdf.file = output_path
    pdf.version = PDF_VERSION[profile]

    # Preserve the SLA template's professional color-management and font lists,
    # while making the non-negotiable production settings explicit.
    pdf.resolution = 300
    pdf.downsample = 0
    pdf.quality = 0
    pdf.compress = 1
    pdf.outdst = 1
    pdf.useDocBleeds = True

    # Universal masters are delivered without printer marks. The receiving
    # printer imposes the piece and adds marks for its own sheet/finishing flow.
    pdf.cropMarks = False
    pdf.bleedMarks = False
    pdf.registrationMarks = False
    pdf.colorMarks = False
    pdf.docInfoMarks = False

    # Embed/subset fonts according to the template's configured font lists.
    pdf.fontEmbedding = 0
    pdf.save()


def main():
    template, output, job_path, profile = _arguments()
    template = os.path.abspath(template)
    output = os.path.abspath(output)
    job_path = os.path.abspath(job_path)

    if not os.path.isfile(template):
        raise RuntimeError(f"Template not found: {template}")
    if not os.path.isfile(job_path):
        raise RuntimeError(f"Job file not found: {job_path}")

    os.makedirs(os.path.dirname(output), exist_ok=True)
    job = _load_job(job_path)

    scribus.openDoc(template)
    try:
        _replace_frames("txt__", job.get("fields"))
        _replace_frames("lbl__", job.get("labels"))
        _check_text_overflow()
        _export_pdf(output, profile)
    finally:
        scribus.closeDoc()


if __name__ == "__main__":
    main()
