"""Validate that a machine can build Love For Love professional print packages."""

from __future__ import annotations

import argparse
import os
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

PROFILE_ENV = {
    "LF_RGB_PROFILE_NAME": "RGB input profile",
    "LF_CMYK_PROFILE_NAME": "CMYK input/exchange profile",
    "LF_OUTPUT_PROFILE_NAME": "PDF/X output intent profile",
}


def _version(command):
    proc = subprocess.run(command, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def _scribus_command(scribus_path, *args):
    """Build a Scribus command that also works on headless Linux.

    Scribus/Qt still initializes a GUI platform plugin for CLI operations such as
    --version and -pi. In CI/Docker, where DISPLAY is unset, wrap Scribus with
    xvfb-run when it is available. On a normal desktop keep the direct command.
    """
    command = [scribus_path, *args]
    if os.name == "posix" and not os.environ.get("DISPLAY"):
        xvfb_run = shutil.which("xvfb-run")
        if xvfb_run:
            command = [xvfb_run, "-a", *command]
    return command


def _scribus_version_ok(output):
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", output)
    if not match:
        return False, None
    version = tuple(int(part or 0) for part in match.groups())
    return version >= (1, 6, 0), version


def _profile_listing(scribus_path):
    proc = subprocess.run(
        _scribus_command(scribus_path, "-g", "-pi"),
        text=True,
        capture_output=True,
    )
    return proc.returncode, (proc.stdout + "\n" + proc.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-profiles",
        action="store_true",
        help="Fail unless configured ICC profile names are present and visible to Scribus.",
    )
    args = parser.parse_args(argv)

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

    headless_paths = {}
    for binary, label in OPTIONAL_HEADLESS_TOOLS.items():
        path = shutil.which(binary)
        headless_paths[binary] = path
        if path:
            print(f"OK   {label}: {path}")
        else:
            print(f"WARN {label}: '{binary}' not found (may be required on headless Linux)")

    if paths.get("scribus"):
        if os.name == "posix" and not os.environ.get("DISPLAY") and not headless_paths.get("xvfb-run"):
            failed = True
            print("FAIL Headless Linux requires xvfb-run for Scribus CLI checks")
        else:
            code, output = _version(_scribus_command(paths["scribus"], "--version"))
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

    configured_profiles = {name: os.environ.get(name) for name in PROFILE_ENV}
    missing_profiles = [name for name, value in configured_profiles.items() if not value]

    if missing_profiles:
        message = "CMS profile variables not configured: " + ", ".join(missing_profiles)
        if args.require_profiles:
            failed = True
            print("FAIL " + message)
        else:
            print("WARN " + message)
    elif paths.get("scribus"):
        code, listing = _profile_listing(paths["scribus"])
        if code != 0:
            failed = True
            print("FAIL Could not read Scribus color profile listing")
            if listing.strip():
                print(listing.strip())
        else:
            for env_name, profile_name in configured_profiles.items():
                if profile_name in listing:
                    print(f"OK   {PROFILE_ENV[env_name]}: {profile_name}")
                else:
                    failed = True
                    print(f"FAIL {PROFILE_ENV[env_name]} not visible to Scribus: {profile_name}")

    if failed:
        print("\nEnvironment is NOT ready for professional export.")
        return 1

    print("\nEnvironment has the required prepress executables.")
    if not missing_profiles:
        print("Configured ICC profile names are visible to Scribus.")
    else:
        print("Run again with --require-profiles after approved ICC profiles are configured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
