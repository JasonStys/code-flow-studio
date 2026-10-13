# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: main()@L16
# variables: root@L18; platform@L19; folder@L20; base@L29; path@L31; stream@L33; digest@L34
# </code-map>

"""Jason Stys: checksummed portable desktop archives, alongside tested one-click OS installers."""

import hashlib
import shutil
import sys
from pathlib import Path


def main():
    """Archive only the generated packaged app and checksum archive/installer files, never runtime accounts."""
    root = Path(__file__).resolve().parents[1] / "release" / "installers"
    platform = {"win32": "windows-x64", "darwin": "macos-arm64", "linux": "linux-x64"}[sys.platform]
    folder = root / (
        "win-unpacked"
        if sys.platform == "win32"
        else "mac-arm64"
        if sys.platform == "darwin"
        else "linux-unpacked"
    )
    if not folder.is_dir():
        raise ValueError("Expected packaged application is absent")
    base = root / f"CodeFlowStudio-0.2.0-{platform}"
    shutil.make_archive(str(base), "zip" if sys.platform == "win32" else "gztar", root_dir=folder)
    for path in root.iterdir():
        if path.is_file() and path.name.endswith((".exe", ".dmg", ".AppImage", ".zip", ".tar.gz")):
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            path.with_name(path.name + ".sha256").write_text(
                digest + "  " + path.name + "\n", encoding="ascii"
            )


if __name__ == "__main__":
    main()
