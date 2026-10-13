# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_checksum_download_filename(tmp_path, name)@L27
# variables: path@L29; expected@L32
# parameters: name@L27; tmp_path@L27
# </code-map>

"""Jason Stys: canonical public checksum records, without executing or publishing fixture binaries."""

import hashlib

import pytest

from scripts.release_archive import write_release_checksum


@pytest.mark.parametrize(
    "name",
    [
        "Code Flow Studio Setup 0.2.0.exe",
        "Code Flow Studio-0.2.0-arm64.dmg",
        "Code Flow Studio-0.2.0.AppImage",
        "CodeFlowStudio-0.2.0-windows-x64.zip",
    ],
)
def test_checksum_download_filename(tmp_path, name):
    """Records match the actual GitHub asset name and digest, not a pre-upload space-containing filename."""
    path = tmp_path / name
    path.write_bytes(b"Fictional package bytes - never executable")
    write_release_checksum(path)
    expected = hashlib.sha256(path.read_bytes()).hexdigest() + "  " + name.replace(" ", ".") + "\n"
    assert path.with_name(name + ".sha256").read_text() == expected
