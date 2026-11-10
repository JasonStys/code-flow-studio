# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: analysis(monkeypatch, tmp_path)@L34; request(analysis, body, case_index)@L46; stub_observation(monkeypatch, analysis, body, exit_code)@L51; test_request_binds_full_unicode_byte_input_and_never_overwrites(analysis)@L61; test_request_invalid_context_rejected_before_process(analysis, kind)@L92; test_forced_request_name_collision_preserves_original(monkeypatch, analysis)@L112; test_actual_inert_child_exit_and_binary_stdin_are_preserved(analysis, exit_code)@L123; test_actual_inert_signal_exit_is_not_normalized_to_collector_exit(analysis)@L146; test_receipt_is_absent_until_process_wait_returns_and_argv_has_no_shell(monkeypatch, analysis)@L154; run(argv)@L161; test_changed_stdin_never_starts_target(monkeypatch, analysis)@L175; test_request_changed_during_target_cannot_publish_completion(monkeypatch, analysis)@L186; run(argv)@L190; test_missing_observation_never_looks_like_zero_exit(analysis)@L201; test_malformed_request_cannot_launch_the_target(monkeypatch, analysis, defect)@L221; test_existing_receipt_cannot_be_replaced_or_execute_again(monkeypatch, analysis)@L251; test_observation_tamper_and_malformed_bytes_rejected(monkeypatch, analysis, defect)@L283; test_reader_rejects_changed_expected_request(monkeypatch, analysis)@L317; test_aliasing_paths_are_not_accepted_as_owned_regular_receipts(monkeypatch, analysis, kind)@L327
# variables: SOURCE@L30; root@L36; target@L37; path@L53; value@L53; body@L63; path@L64; value@L64; another@L84; different@L84; body@L94; index@L94; source@L94; source@L96; source@L98; index@L100; index@L102; index@L104; body@L106; _value@L115; path@L115; original@L116; body@L125; witness@L126; path@L133; value@L133; observed@L136; key@L140; key@L141; val@L141; path@L149; value@L149; body@L156; path@L157; value@L157; receipt@L158; calls@L159; path@L177; value@L177; path@L188; value@L188; altered@L191; path@L203; value@L203; path@L223; value@L223; altered@L224; changes@L225; changed@L233; field@L233; content@L235; content@L237; content@L239; content@L241; path@L253; receipt@L253; value@L253; original@L254; path@L285; receipt@L285; value@L285; observed@L286; changes@L287; changed@L301; key@L301; body@L303; body@L305; body@L307; body@L309; body@L311; _receipt@L319; path@L319; value@L319; changed@L320; path@L329; receipt@L329; value@L329; selected@L330; alias@L331; original@L335
# parameters: monkeypatch@L34; tmp_path@L34; analysis@L46; body@L46; case_index@L46; analysis@L51; body@L51; exit_code@L51; monkeypatch@L51; args@L55; kwargs@L55; analysis@L61; analysis@L92; kind@L92; analysis@L112; monkeypatch@L112; count@L114; analysis@L123; exit_code@L123; analysis@L146; analysis@L154; monkeypatch@L154; argv@L161; kwargs@L161; analysis@L175; monkeypatch@L175; args@L179; kwargs@L179; analysis@L186; monkeypatch@L186; argv@L190; kwargs@L190; analysis@L201; analysis@L221; defect@L221; monkeypatch@L221; args@L244; kwargs@L244; analysis@L251; monkeypatch@L251; args@L256; kwargs@L256; analysis@L283; defect@L283; monkeypatch@L283; analysis@L317; monkeypatch@L317; analysis@L327; kind@L327; monkeypatch@L327
# </code-map>

"""Jason Stys: independent bridge receipt/process regressions; no Docker, compiler or submitted code.

Actual child tests execute only this file's inert Python fixture under the fixed
target interface. Shipping Coverlet/.NET acceptance remains separate hosted CI.
Symbol and variable locations are maintained in docs/code-index.md.
"""

import copy
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from runner import csharp_coverage_bridge as bridge

SOURCE = hashlib.sha256(b"independent synthetic source").hexdigest()


@pytest.fixture
def analysis(monkeypatch, tmp_path):
    """Replace only trusted fixed tool paths with an owned temporary inert Python target."""
    root = tmp_path / ".analysis"
    target = root / "csharp" / "App.dll"
    target.parent.mkdir(parents=True)
    target.write_text("pass\n", encoding="utf-8")
    monkeypatch.setattr(bridge, "ANALYSIS", root)
    monkeypatch.setattr(bridge, "ASSEMBLY", target)
    monkeypatch.setattr(bridge, "DOTNET", Path(sys.executable))
    return root


def request(analysis, body=b"approved stdin", case_index=0):
    """Construct the real on-disk request with independent authored source/input values."""
    return bridge.make_request(analysis, SOURCE, case_index, body)


def stub_observation(monkeypatch, analysis, body=b"approved stdin", exit_code=0):
    """Run the actual bridge writer around a nonexecuting process double, then read real bytes."""
    path, value = request(analysis, body)
    monkeypatch.setattr(
        bridge.subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args[0], exit_code)
    )
    assert bridge.observe(path, io.BytesIO(body)) == 0
    return path, value, analysis / value["receipt"]


def test_request_binds_full_unicode_byte_input_and_never_overwrites(analysis):
    """The 8192-character four-byte Unicode boundary is 32768 bytes, not 8192 bytes."""
    body = ("\U0001f680" * 8192).encode()
    path, value = request(analysis, body, 63)
    assert path.parent == analysis
    assert re.fullmatch(r"csharp-request-[a-f0-9]{32}\.json", path.name)
    assert value == json.loads(path.read_bytes())
    assert set(value) == {
        "schema",
        "nonce",
        "case_index",
        "source_sha256",
        "stdin_sha256",
        "stdin_bytes",
        "receipt",
    }
    assert type(value["schema"]) is int and value["schema"] == 1
    assert type(value["case_index"]) is int and value["case_index"] == 63
    assert value["source_sha256"] == SOURCE
    assert value["stdin_bytes"] == 32768
    assert value["stdin_sha256"] == hashlib.sha256(body).hexdigest()
    assert re.fullmatch(r"[a-f0-9]{64}", value["nonce"])
    assert value["receipt"] == path.name.replace("csharp-request-", "csharp-exit-")
    another, different = request(analysis, body, 63)
    assert another != path and different["nonce"] != value["nonce"]


@pytest.mark.parametrize(
    "kind",
    ["source-short", "source-uppercase", "case-bool", "case-negative", "case-large", "input-too-large"],
)
def test_request_invalid_context_rejected_before_process(analysis, kind):
    """Invalid identities and byte/case limits cannot become valid measurements."""
    source, index, body = SOURCE, 0, b"input"
    if kind == "source-short":
        source = "a" * 63
    elif kind == "source-uppercase":
        source = SOURCE.upper()
    elif kind == "case-bool":
        index = True
    elif kind == "case-negative":
        index = -1
    elif kind == "case-large":
        index = 64
    else:
        body = b"x" * 32769
    with pytest.raises((ValueError, OSError)):
        bridge.make_request(analysis, source, index, body)
    assert not list(analysis.glob("csharp-request-*.json"))


def test_forced_request_name_collision_preserves_original(monkeypatch, analysis):
    """Even a forced random-name collision must fail rather than overwrite approved context."""
    monkeypatch.setattr(bridge.secrets, "token_hex", lambda count: "a" * (count * 2))
    path, _value = request(analysis)
    original = path.read_bytes()
    with pytest.raises((ValueError, OSError)):
        request(analysis, b"different", 1)
    assert path.read_bytes() == original


@pytest.mark.parametrize("exit_code", [0, 2, 7, 255])
def test_actual_inert_child_exit_and_binary_stdin_are_preserved(analysis, exit_code):
    """Actual child exits differ from the bridge's successful collection exit of zero."""
    body = "\x00first\n\U0001f680last\n".encode()
    witness = analysis / "child-input.bin"
    bridge.ASSEMBLY.write_text(
        "import pathlib,sys\n"
        f"pathlib.Path({str(witness)!r}).write_bytes(sys.stdin.buffer.read())\n"
        f"sys.exit({exit_code})\n",
        encoding="utf-8",
    )
    path, value = request(analysis, body)
    assert bridge.observe(path, io.BytesIO(body)) == 0
    assert witness.read_bytes() == body
    observed = bridge.read_observation(path, value)
    assert observed["target_exit_code"] == exit_code and type(observed["target_exit_code"]) is int
    assert observed["target"] == str(bridge.ASSEMBLY)
    assert observed["bridge_sha256"] == hashlib.sha256(Path(bridge.__file__).read_bytes()).hexdigest()
    assert {key: observed[key] for key in value if key != "receipt"} == {
        key: val for key, val in value.items() if key != "receipt"
    }


@pytest.mark.skipif(os.name != "posix", reason="Negative signal return codes are POSIX subprocess semantics")
def test_actual_inert_signal_exit_is_not_normalized_to_collector_exit(analysis):
    """An actual SIGTERM result remains -15 instead of being confused with bridge zero."""
    bridge.ASSEMBLY.write_text("import os,signal\nos.kill(os.getpid(), signal.SIGTERM)\n", encoding="utf-8")
    path, value = request(analysis)
    assert bridge.observe(path, io.BytesIO(b"approved stdin")) == 0
    assert bridge.read_observation(path, value)["target_exit_code"] == -15


def test_receipt_is_absent_until_process_wait_returns_and_argv_has_no_shell(monkeypatch, analysis):
    """Spy on the real call boundary, independently checking no premature completion receipt."""
    body = b"$(not-a-shell); & literal input"
    path, value = request(analysis, body)
    receipt = analysis / value["receipt"]
    calls = []

    def run(argv, **kwargs):
        assert not receipt.exists()
        assert argv == [str(bridge.DOTNET), str(bridge.ASSEMBLY)]
        assert kwargs["input"] == body and kwargs["check"] is False
        assert not kwargs.get("shell", False) and not kwargs.get("capture_output", False)
        assert kwargs.get("stdout") is None and kwargs.get("stderr") is None
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 7)

    monkeypatch.setattr(bridge.subprocess, "run", run)
    assert bridge.observe(path, io.BytesIO(body)) == 0 and len(calls) == 1
    assert bridge.read_observation(path, value)["target_exit_code"] == 7


def test_changed_stdin_never_starts_target(monkeypatch, analysis):
    """Same-length altered bytes cannot borrow a request's approved input hash."""
    path, value = request(analysis, b"expected")
    monkeypatch.setattr(
        bridge.subprocess, "run", lambda *args, **kwargs: pytest.fail("Target must not start")
    )
    with pytest.raises((ValueError, OSError)):
        bridge.observe(path, io.BytesIO(b"modified"))
    assert not (analysis / value["receipt"]).exists()


def test_request_changed_during_target_cannot_publish_completion(monkeypatch, analysis):
    """A completed child cannot validate a context that changed while it was running."""
    path, value = request(analysis)

    def run(argv, **kwargs):
        altered = {**value, "case_index": 1}
        path.write_text(json.dumps(altered), encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(bridge.subprocess, "run", run)
    with pytest.raises((ValueError, OSError)):
        bridge.observe(path, io.BytesIO(b"approved stdin"))
    assert not (analysis / value["receipt"]).exists()


def test_missing_observation_never_looks_like_zero_exit(analysis):
    """A successful request is not itself proof of completion."""
    path, value = request(analysis)
    with pytest.raises((ValueError, OSError)):
        bridge.read_observation(path, value)


@pytest.mark.parametrize(
    "defect",
    [
        "schema-bool",
        "bytes-bool",
        "nonce",
        "receipt-traversal",
        "unknown",
        "duplicate",
        "truncated",
        "nonfinite",
    ],
)
def test_malformed_request_cannot_launch_the_target(monkeypatch, analysis, defect):
    """Treat the serialized request as an untrusted protocol, including duplicate/nonfinite JSON."""
    path, value = request(analysis)
    altered = copy.deepcopy(value)
    changes = {
        "schema-bool": ("schema", True),
        "bytes-bool": ("stdin_bytes", True),
        "nonce": ("nonce", "bad"),
        "receipt-traversal": ("receipt", "../outside.json"),
        "unknown": ("unexpected", "field"),
    }
    if defect in changes:
        field, changed = changes[defect]
        altered[field] = changed
        content = json.dumps(altered).encode()
    elif defect == "duplicate":
        content = json.dumps(altered).encode()[:-1] + b',"schema":1}'
    elif defect == "nonfinite":
        content = json.dumps(altered).replace('"case_index": 0', '"case_index": NaN').encode()
    else:
        content = b'{"schema":'
    path.write_bytes(content)
    monkeypatch.setattr(
        bridge.subprocess, "run", lambda *args, **kwargs: pytest.fail("Malformed request must not execute")
    )
    with pytest.raises((ValueError, OSError)):
        bridge.observe(path, io.BytesIO(b"approved stdin"))
    assert not (analysis / value["receipt"]).exists()


def test_existing_receipt_cannot_be_replaced_or_execute_again(monkeypatch, analysis):
    """Repeat collection refuses stale proof and preserves its original bytes."""
    path, value, receipt = stub_observation(monkeypatch, analysis, exit_code=2)
    original = receipt.read_bytes()
    monkeypatch.setattr(
        bridge.subprocess, "run", lambda *args, **kwargs: pytest.fail("Stale receipt must prevent execution")
    )
    with pytest.raises((ValueError, OSError)):
        bridge.observe(path, io.BytesIO(b"approved stdin"))
    assert receipt.read_bytes() == original and bridge.read_observation(path, value)["target_exit_code"] == 2


@pytest.mark.parametrize(
    "defect",
    [
        "nonce",
        "case",
        "source",
        "stdin",
        "bytes",
        "target",
        "bridge",
        "exit-bool",
        "exit-high",
        "exit-low",
        "unknown",
        "duplicate",
        "nonfinite",
        "truncated",
        "oversize",
    ],
)
def test_observation_tamper_and_malformed_bytes_rejected(monkeypatch, analysis, defect):
    """Alter real published receipt bytes; matching filenames alone never establish completion."""
    path, value, receipt = stub_observation(monkeypatch, analysis)
    observed = json.loads(receipt.read_bytes())
    changes = {
        "nonce": ("nonce", "c" * 64),
        "case": ("case_index", 1),
        "source": ("source_sha256", "c" * 64),
        "stdin": ("stdin_sha256", "c" * 64),
        "bytes": ("stdin_bytes", 0),
        "target": ("target", "/untrusted/other.dll"),
        "bridge": ("bridge_sha256", "c" * 64),
        "exit-bool": ("target_exit_code", True),
        "exit-high": ("target_exit_code", 256),
        "exit-low": ("target_exit_code", -129),
        "unknown": ("extra", 1),
    }
    if defect in changes:
        key, changed = changes[defect]
        observed[key] = changed
        body = json.dumps(observed).encode()
    elif defect == "duplicate":
        body = json.dumps(observed).encode()[:-1] + b',"schema":1}'
    elif defect == "nonfinite":
        body = json.dumps(observed).replace('"target_exit_code": 0', '"target_exit_code": NaN').encode()
    elif defect == "truncated":
        body = b'{"schema":1'
    else:
        body = b" " * 65537
    receipt.write_bytes(body)
    with pytest.raises((ValueError, OSError)):
        bridge.read_observation(path, value)


def test_reader_rejects_changed_expected_request(monkeypatch, analysis):
    """The caller's source/case identity must agree with the immutable on-disk request too."""
    path, value, _receipt = stub_observation(monkeypatch, analysis)
    changed = copy.deepcopy(value)
    changed["source_sha256"] = "d" * 64
    with pytest.raises((ValueError, OSError)):
        bridge.read_observation(path, changed)


@pytest.mark.parametrize("kind", ["request-hardlink", "receipt-hardlink", "receipt-symlink"])
def test_aliasing_paths_are_not_accepted_as_owned_regular_receipts(monkeypatch, analysis, kind):
    """Independent filesystem aliases must not bypass the descriptor/link-count contract."""
    path, value, receipt = stub_observation(monkeypatch, analysis)
    selected = path if kind == "request-hardlink" else receipt
    alias = analysis / "alias.json"
    if kind.endswith("hardlink"):
        alias.hardlink_to(selected)
    else:
        original = receipt.read_bytes()
        receipt.unlink()
        alias.write_bytes(original)
        try:
            receipt.symlink_to(alias)
        except OSError:
            pytest.skip("Symlink creation unavailable for this Windows test account")
    with pytest.raises((ValueError, OSError)):
        bridge.read_observation(path, value)
