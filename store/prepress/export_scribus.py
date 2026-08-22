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

STORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from prepress.template_contract import required_frame_names


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


def _piece_from_template(template):
    return os.path.splitext(os.path.basename(template))[0]


def _check_required_frames(piece):
    missing = sorted(
        frame for frame in required_frame_names(piece)
        if not scribus.objectExists(frame)
    )
    if missing:
        raise RuntimeError(
            f"Template {piece} is missing required editable frames: " + ", ".join(missing)
        )


def _relayout_text_frame(frame_name):
    """Force Scribus to recompute text layout after programmatic replacement."""
    layout_text = getattr(scribus, "layoutText", None)
    if callable(layout_text):
        layout_text(frame_name)
        return

    layout_chain = getattr(scribus, "layoutTextChain", None)
    if callable(layout_chain):
        layout_chain(frame_name)
        return

    redraw_all = getattr(scribus, "redrawAll", None)
    if callable(redraw_all):
        redraw_all()
        return

    raise RuntimeError("Scribus does not expose a text relayout API")


def _replace_text_preserving_formatting(frame_name, value):
    """Replace placeholder text without discarding the template's direct styling.

    Scribus setText() clears the old story before inserting new text. With direct
    formatting, that can also discard the font/size/alignment attached to the
    placeholder and make replacement text fall back to document defaults.

    Appending the replacement first makes it inherit the placeholder formatting;
    deleting only the original prefix then leaves the new content styled exactly
    like the template. This is intentionally done for every editable field/label.
    """
    new_text = str(value or "")
    old_length = scribus.getTextLength(frame_name)

    if old_length > 0 and new_text:
        scribus.insertText(new_text, old_length, frame_name)
        scribus.selectText(0, old_length, frame_name)
        scribus.deleteText(frame_name)
    elif old_length > 0:
        scribus.selectText(0, old_length, frame_name)
        scribus.deleteText(frame_name)
    else:
        # Structural templates are expected to contain non-empty placeholders.
        # Keep a defensive fallback for custom templates while still validating
        # the resulting layout before export.
        scribus.setText(new_text, frame_name)

    _relayout_text_frame(frame_name)


def _replace_frames(prefix, values):
    changed = []
    for key, value in (values or {}).items():
        frame_name = f"{prefix}{key}"
        if not scribus.objectExists(frame_name):
            continue
        _replace_text_preserving_formatting(frame_name, value)
        changed.append(frame_name)
    return changed


def _check_text_overflow():
    overflow = []
    checked = 0
    for item in scribus.getAllObjects():
        if not (item.startswith("txt__") or item.startswith("lbl__")):
            continue
        try:
            _relayout_text_frame(item)
            is_overflow = scribus.textOverflows(item, 1)
        except Exception as exc:
            raise RuntimeError(f"Could not validate text layout for frame {item}: {exc}") from exc
        checked += 1
        if is_overflow:
            overflow.append(item)

    if checked == 0:
        raise RuntimeError("Template contains no editable text frames to validate")
    if overflow:
        raise RuntimeError("Text overflow in frames: " + ", ".join(sorted(overflow)))


def _required_cms_profiles():
    profiles = {
        "output": os.environ.get("LF_OUTPUT_PROFILE_NAME"),
        "rgb": os.environ.get("LF_RGB_PROFILE_NAME"),
        "cmyk": os.environ.get("LF_CMYK_PROFILE_NAME"),
    }
    missing = [key for key, value in profiles.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing CMS environment configuration: " + ", ".join(missing)
        )
    return profiles


def _export_pdf(output_path, profile, piece):
    cms = _required_cms_profiles()
    pdf = scribus.PDFfile()
    pdf.file = output_path
    pdf.version = PDF_VERSION[profile]

    pdf.resolution = 300
    pdf.downsample = 0
    pdf.quality = 0
    pdf.compress = 1
    pdf.outdst = 1
    pdf.useDocBleeds = True

    # Explicit color-management inputs/output. The SLA preflight already checks
    # that document CMS is enabled and uses the same profile names.
    pdf.profiles = 1
    pdf.profilei = 1
    pdf.noembicc = 0
    pdf.solidpr = cms["cmyk"]
    pdf.imagepr = cms["rgb"]
    pdf.printprofc = cms["output"]
    pdf.intents = 1   # relative colorimetric for solid/vector colors
    pdf.intenti = 0   # perceptual for photographic/raster imagery
    pdf.info = f"Love For Love — {piece} — professional print master"

    # Universal masters are delivered without printer marks. The receiving
    # printer imposes the piece and adds marks for its own sheet/finishing flow.
    pdf.cropMarks = False
    pdf.bleedMarks = False
    pdf.registrationMarks = False
    pdf.colorMarks = False
    pdf.docInfoMarks = False

    # PDF/X forces proper font embedding in Scribus. Keep mode 0 so Scribus can
    # fully embed or subset each used font according to its own compatibility rules.
    pdf.fontEmbedding = 0
    pdf.save()


def main():
    template, output, job_path, profile = _arguments()
    template = os.path.abspath(template)
    output = os.path.abspath(output)
    job_path = os.path.abspath(job_path)
    piece = _piece_from_template(template)

    if not os.path.isfile(template):
        raise RuntimeError(f"Template not found: {template}")
    if not os.path.isfile(job_path):
        raise RuntimeError(f"Job file not found: {job_path}")

    os.makedirs(os.path.dirname(output), exist_ok=True)
    job = _load_job(job_path)

    scribus.openDoc(template)
    try:
        _check_required_frames(piece)
        _replace_frames("txt__", job.get("fields"))
        _replace_frames("lbl__", job.get("labels"))
        _check_text_overflow()
        _export_pdf(output, profile, piece)
    finally:
        scribus.closeDoc()


if __name__ == "__main__":
    main()
