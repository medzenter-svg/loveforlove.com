"""Validate that a machine can build Love For Love professional print packages."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys


REQUIRED_TOOLS = {
    "scribus": "Scribus",
    "gs": "Ghostscript",
    "pdfinfo": "Poppler pdfinfo",
    "pdffonts": "Poppler pdffonts",
    "exiftool": "ExifTool",
}

OPTIONAL_HEADLESS_TOOLS = {
    "xvfb-run": "X virtual framebuffer wrapper",
}


def _version(command):
    proc = subprocess.run(command, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def _scribus_version_ok(output):
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", output)
    if not match:
        return False, None
    version = tuple(int(part or 0) for part in match.groups())
    return version >= (1, 6, 0), version


def main():
    failed = False
    print("Love For Love prepress environment check")
    print("=" * 44)

    paths = {}
    for binary, label in REQUIRED_TOOLS.items():
        path = shutil.which(binary)
        paths[binary] = path
        if path:
            print(f"OK   {label}: {path}")
        else:
            failed = True
            print(f"FAIL {label}: '{binary}' not found")

    for binary, label in OPTIONAL_HEADLESS_TOOLS.items():
        path = shutil.which(binary)
        if path:
            print(f"OK   {label}: {path}")
        else:
            print(f"WARN {label}: '{binary}' not found (may be required on headless Linux)")

    if paths.get("scribus"):
        code, output = _version([paths["scribus"], "--version"])
        ok, parsed = _scribus_version_ok(output)
        if code != 0 or not ok:
            failed = True
            print(f"FAIL Scribus version: {output or 'unknown'}; require 1.6.0+")
        else:
            print(f"OK   Scribus version: {'.'.join(map(str, parsed))}")

    if paths.get("gs"):
        code, output = _version([paths["gs"], "--version"])
        print(("OK   " if code == 0 else "FAIL ") + f"Ghostscript version: {output}")
        failed = failed or code != 0

    if paths.get("exiftool"):
        code, output = _version([paths["exiftool"], "-ver"])
        print(("OK   " if code == 0 else "FAIL ") + f"ExifTool version: {output}")
        failed = failed or code != 0

    if failed:
        print("\nEnvironment is NOT ready for professional export.")
        return 1

    print("\nEnvironment has the required prepress executables.")
    print("ICC profiles, approved fonts and actual PDF/X output are still validated per collection.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
