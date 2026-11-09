# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_checksum_download_filename(tmp_path, name)@L32; test_product_and_worker_release_versions_remain_coherent()@L41
# variables: path@L34; expected@L37; root@L43; relative@L45; data@L51
# parameters: name@L32; tmp_path@L32
# </code-map>

"""Jason Stys: canonical public checksum records, without executing or publishing fixture binaries."""

import hashlib
import json
import tomllib
from pathlib import Path

import pytest

from scripts.release_archive import write_release_checksum
from studio import __version__
from studio.execution import IMAGE


@pytest.mark.parametrize(
    "name",
    [
        "Code Flow Studio Setup 0.4.0.exe",
        "Code Flow Studio-0.4.0-arm64.dmg",
        "Code Flow Studio-0.4.0.AppImage",
        "CodeFlowStudio-0.4.0-windows-x64.zip",
    ],
)
def test_checksum_download_filename(tmp_path, name):
    """Records match the actual GitHub asset name and digest, not a pre-upload space-containing filename."""
    path = tmp_path / name
    path.write_bytes(b"Fictional package bytes - never executable")
    write_release_checksum(path)
    expected = hashlib.sha256(path.read_bytes()).hexdigest() + "  " + name.replace(" ", ".") + "\n"
    assert path.with_name(name + ".sha256").read_text() == expected


def test_product_and_worker_release_versions_remain_coherent():
    """Prevent mixed-version installers, health metadata or stale worker-image readiness."""
    root = Path(__file__).resolve().parents[1]
    assert tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"] == __version__
    for relative in [
        "package.json",
        "package-lock.json",
        "runner/tools/package.json",
        "runner/tools/package-lock.json",
    ]:
        data = json.loads((root / relative).read_text())
        assert data["version"] == __version__
        if "packages" in data:
            assert data["packages"][""]["version"] == __version__
    assert IMAGE == f"code-flow-worker:{__version__}"
    assert IMAGE in (root / ".github/workflows/validate.yml").read_text()
    assert f"/ v{'.'.join(__version__.split('.')[:2])}" in (root / "ui/App.tsx").read_text()
    assert (root / f"docs/releases/v{__version__}.md").is_file()
