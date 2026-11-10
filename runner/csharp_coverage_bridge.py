# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: _require(condition, message)@L45; _hash(value)@L51; _hex(value, length)@L56; _directory(path)@L61; _root(root)@L72; _missing(path)@L78; _regular(metadata)@L87; _read(path, maximum)@L95; _json(path)@L123; pairs(items)@L126; nonfinite(_value)@L131; _request(path)@L143; _validate_request(value, suffix)@L154; _publish(path, value)@L172; _bridge_hash()@L191; make_request(root, source_sha256, case_index, stdin_bytes)@L196; read_observation(request_path, request)@L224; observe(request_path, input_stream)@L254; main()@L293
# variables: ANALYSIS@L35; DOTNET@L36; ASSEMBLY@L37; MAX_INPUT@L38; MAX_JSON@L39; MAX_BRIDGE@L40; REQUEST_FIELDS@L41; OBSERVATION_FIELDS@L42; component@L64; metadata@L65; before@L97; flags@L100; stream@L103; opened@L104; body@L110; after@L111; value@L127; value@L134; match@L147; value@L149; body@L176; temporary@L178; flags@L179; descriptor@L180; stream@L182; suffix@L207; path@L208; value@L209; actual@L226; suffix@L229; value@L231; echoed@L233; name@L233; name@L236; request@L262; receipt@L263; raw@L269; completed@L277; name@L283; value@L283
# parameters: condition@L45; message@L45; value@L51; length@L56; value@L56; path@L61; root@L72; path@L78; metadata@L87; maximum@L95; path@L95; path@L123; items@L126; _value@L131; path@L143; suffix@L154; value@L154; path@L172; value@L172; case_index@L196; root@L196; source_sha256@L196; stdin_bytes@L196; request@L224; request_path@L224; input_stream@L254; request_path@L254
# </code-map>

"""Jason Stys: observe the instrumented .NET target independently of Coverlet's exit.

Coverlet runs this trusted, isolated-mode Python file as its fixed target. The
bridge forwards approved stdin, waits for the fixed assembly and exclusively
publishes a small observation before returning success to the collector. A
collector failure remains a separate failure; no wrapper status is translated
into a guessed target exit. Only the restricted Linux worker may run the CLI.

Request/observation fields bind one fresh case, all-source hash and input bytes.
Targets share the worker UID and can interfere with job files, so these bindings
detect stale/mismatched evidence, not hostile-code forgery or trusted attestation.
No secrets, target output, network access, new process session or host execution
fallback is introduced. Declaration/variable locations: docs/code-index.md.
"""

import hashlib
import json
import os
import re
import secrets
import stat
import subprocess
import sys
from pathlib import Path
from typing import BinaryIO

ANALYSIS = Path("/tmp/project/.analysis")  # noqa: S108 -- fixed job-private worker tmpfs.
DOTNET = Path("/usr/share/dotnet/dotnet")
ASSEMBLY = ANALYSIS / "csharp" / "App.dll"
MAX_INPUT = 32768
MAX_JSON = 4096
MAX_BRIDGE = 128 * 1024
REQUEST_FIELDS = {"schema", "nonce", "case_index", "source_sha256", "stdin_sha256", "stdin_bytes", "receipt"}
OBSERVATION_FIELDS = (REQUEST_FIELDS - {"receipt"}) | {"target", "target_exit_code", "bridge_sha256"}


def _require(condition: bool, message: str) -> None:
    """Reject invalid protocol state explicitly, including under optimized Python."""
    if not condition:
        raise ValueError(message)


def _hash(value: bytes) -> str:
    """Hash exact bytes; never normalize source or input text."""
    return hashlib.sha256(value).hexdigest()


def _hex(value, length: int) -> bool:
    """Accept only lower-case hexadecimal strings of the required exact length."""
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{" + str(length) + "}", value) is not None


def _directory(path: Path) -> None:
    """Require real directory components instead of following a substituted link."""
    _require(path.is_absolute(), "Bridge path must be absolute")
    for component in (path, *path.parents):
        metadata = component.lstat()
        _require(
            stat.S_ISDIR(metadata.st_mode) and not component.is_symlink() and not component.is_junction(),
            "Bridge directory must not contain links",
        )


def _root(root: Path) -> None:
    """Allow only the fixed analysis root; callers cannot choose another output tree."""
    _require(isinstance(root, Path) and root == ANALYSIS, "Unexpected bridge root")
    _directory(root)


def _missing(path: Path) -> None:
    """Reject any existing name, including a dangling symlink, before target launch."""
    try:
        path.lstat()
    except FileNotFoundError:
        return
    raise ValueError("Bridge output already exists")


def _regular(metadata: os.stat_result) -> None:
    """Only one-link regular files are eligible for protocol reads."""
    _require(
        stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1,
        "Bridge protocol requires a one-link regular file",
    )


def _read(path: Path, maximum: int) -> bytes:
    """Read at most the explicit bound through the same checked file descriptor."""
    before = path.lstat()
    _regular(before)
    _require(not path.is_symlink() and not path.is_junction(), "Bridge file must not be a link")
    flags = (
        os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    )
    with os.fdopen(os.open(path, flags), "rb") as stream:
        opened = os.fstat(stream.fileno())
        _regular(opened)
        _require(
            os.path.samestat(before, opened) and 0 <= opened.st_size <= maximum,
            "Bridge file identity or size changed",
        )
        body = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        _regular(after)
        _require(
            len(body) <= maximum
            and len(body) == opened.st_size == after.st_size
            and opened.st_mtime_ns == after.st_mtime_ns
            and os.path.samestat(after, path.lstat()),
            "Bridge file changed during its bounded read",
        )
    return body


def _json(path: Path) -> dict:
    """Reject duplicate fields, nonfinite constants, non-UTF8 bytes and non-object JSON."""

    def pairs(items):
        value = dict(items)
        _require(len(value) == len(items), "Duplicate bridge JSON field")
        return value

    def nonfinite(_value):
        raise ValueError("Nonfinite bridge JSON value")

    value = json.loads(
        _read(path, MAX_JSON).decode("utf-8"),
        object_pairs_hook=pairs,
        parse_constant=nonfinite,
    )
    _require(isinstance(value, dict), "Bridge JSON must be an object")
    return value


def _request(path: Path) -> dict:
    """Validate a fixed-root request filename and every declared context field."""
    _require(isinstance(path, Path), "Bridge request must be a path")
    _root(path.parent)
    match = re.fullmatch(r"csharp-request-([a-f0-9]{32})\.json", path.name)
    _require(match is not None, "Invalid bridge request name")
    value = _json(path)
    _validate_request(value, match[1])
    return value


def _validate_request(value: dict, suffix: str) -> None:
    """Require exact schema/types/ranges and the receipt paired with this request."""
    _require(set(value) == REQUEST_FIELDS, "Unexpected bridge request fields")
    _require(type(value["schema"]) is int and value["schema"] == 1, "Invalid bridge schema")
    _require(_hex(value["nonce"], 64), "Invalid bridge nonce")
    _require(
        type(value["case_index"]) is int and 0 <= value["case_index"] <= 63,
        "Invalid bridge case index",
    )
    _require(_hex(value["source_sha256"], 64), "Invalid bridge source hash")
    _require(_hex(value["stdin_sha256"], 64), "Invalid bridge stdin hash")
    _require(
        type(value["stdin_bytes"]) is int and 0 <= value["stdin_bytes"] <= MAX_INPUT,
        "Invalid bridge stdin size",
    )
    _require(value["receipt"] == f"csharp-exit-{suffix}.json", "Invalid bridge receipt name")


def _publish(path: Path, value: dict) -> None:
    """Fsync a private temporary file, then publish using an exclusive hard link."""
    _root(path.parent)
    _missing(path)
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    _require(len(body) <= MAX_JSON, "Bridge JSON exceeds its byte bound")
    temporary = path.parent / ("csharp-publish-" + secrets.token_hex(16) + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path, follow_symlinks=False)
    finally:
        temporary.unlink(missing_ok=True)


def _bridge_hash() -> str:
    """Bind observations to the actual bounded trusted bridge source, not a claimed digest."""
    return _hash(_read(Path(__file__), MAX_BRIDGE))


def make_request(root: Path, source_sha256: str, case_index: int, stdin_bytes: bytes) -> tuple[Path, dict]:
    """Create a fresh case request without executing a target or replacing existing evidence.

    root is exactly ANALYSIS; source_sha256 binds the canonical complete source
    list supplied by the worker. case_index is the approved zero-based case.
    stdin_bytes are the exact UTF8-encoded input, including all newlines.
    """
    _root(root)
    _require(_hex(source_sha256, 64), "Invalid bridge source hash")
    _require(type(case_index) is int and 0 <= case_index <= 63, "Invalid bridge case index")
    _require(type(stdin_bytes) is bytes and len(stdin_bytes) <= MAX_INPUT, "Invalid bridge stdin")
    suffix = secrets.token_hex(16)
    path = root / f"csharp-request-{suffix}.json"
    value = {
        "schema": 1,
        "nonce": secrets.token_hex(32),
        "case_index": case_index,
        "source_sha256": source_sha256,
        "stdin_sha256": _hash(stdin_bytes),
        "stdin_bytes": len(stdin_bytes),
        "receipt": f"csharp-exit-{suffix}.json",
    }
    _validate_request(value, suffix)
    _missing(root / value["receipt"])
    _publish(path, value)
    return path, value


def read_observation(request_path: Path, request: dict) -> dict:
    """Require a fresh on-disk request and fully bound observed status from this bridge."""
    actual = _request(request_path)
    _require(isinstance(request, dict) and actual == request, "Bridge request context changed")
    # Revalidate caller types too: Python equality alone would accept True as 1.
    suffix = re.fullmatch(r"csharp-request-([a-f0-9]{32})\.json", request_path.name)[1]
    _validate_request(request, suffix)
    value = _json(request_path.parent / request["receipt"])
    _require(set(value) == OBSERVATION_FIELDS, "Unexpected bridge observation fields")
    echoed = {name: value[name] for name in REQUEST_FIELDS - {"receipt"}}
    _validate_request({**echoed, "receipt": request["receipt"]}, suffix)
    _require(
        echoed == {name: request[name] for name in REQUEST_FIELDS - {"receipt"}},
        "Bridge observation context mismatch",
    )
    _require(
        type(value["target"]) is str and value["target"] == str(ASSEMBLY),
        "Bridge observation target mismatch",
    )
    _require(
        type(value["target_exit_code"]) is int and -128 <= value["target_exit_code"] <= 255,
        "Invalid observed target exit",
    )
    _require(
        _hex(value["bridge_sha256"], 64) and value["bridge_sha256"] == _bridge_hash(),
        "Bridge source hash mismatch",
    )
    return value


def observe(request_path: Path, input_stream: BinaryIO) -> int:
    """Wait for the fixed target and publish its real status before reporting collector success.

    The existing worker owns the outer deadline/process group. This child never
    starts a detached session, inherits output/error streams, and forwards exact
    already-validated input bytes. Launch/write/protocol errors produce no valid
    observation and propagate to the fixed-error CLI.
    """
    request = _request(request_path)
    receipt = request_path.parent / request["receipt"]
    _missing(receipt)
    _require(Path(ASSEMBLY) == ANALYSIS / "csharp" / "App.dll", "Unexpected fixed assembly")
    _directory(Path(ASSEMBLY).parent)
    _regular(Path(ASSEMBLY).lstat())
    _require(not Path(ASSEMBLY).is_symlink(), "Assembly must not be a link")
    raw = input_stream.read(MAX_INPUT + 1)
    _require(
        type(raw) is bytes
        and len(raw) <= MAX_INPUT
        and len(raw) == request["stdin_bytes"]
        and _hash(raw) == request["stdin_sha256"],
        "Bridge stdin differs from the approved case",
    )
    completed = subprocess.run([str(DOTNET), str(ASSEMBLY)], input=raw, check=False)
    _require(
        type(completed.returncode) is int and -128 <= completed.returncode <= 255,
        "Target completion status is unavailable",
    )
    _require(_request(request_path) == request, "Bridge request changed during target execution")
    value = {name: request[name] for name in REQUEST_FIELDS - {"receipt"}}
    value.update(
        target=str(ASSEMBLY),
        target_exit_code=completed.returncode,
        bridge_sha256=_bridge_hash(),
    )
    _publish(receipt, value)
    return 0


def main() -> int:
    """Accept one fixed-root request path and emit only an authored failure on error."""
    try:
        _require(len(sys.argv) == 2, "One bridge request is required")
        return observe(Path(sys.argv[1]), sys.stdin.buffer)
    except (OSError, ValueError, TypeError, KeyError):
        print("C# coverage target observation failed", file=sys.stderr)
        return 125


if __name__ == "__main__":
    raise SystemExit(main())
