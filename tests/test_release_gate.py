# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Connection@L412
# functions: source_responses()@L41; strict_reader(responses)@L81; read(endpoint)@L84; release_record()@L92; test_real_source_response_contract_passes(monkeypatch)@L110; test_zero_unknown_or_noninteger_codeql_rule_counts_never_authorize_release(monkeypatch, count)@L117; test_source_failures_cannot_authorize_release(monkeypatch, defect)@L149; test_unknown_or_full_scan_pages_fail_closed(monkeypatch)@L193; test_prepared_numeric_id_cannot_be_public_or_swapped(monkeypatch, change)@L210; test_actual_workflow_policy_rejects_security_mutants(before, after)@L234; test_package_schema_is_strict(value)@L245; test_metadata_duplicates_nonfinite_and_nonobjects_are_errors(source)@L253; portable(file, value, worker, system, symlink)@L259; test_actual_platform_archive_metadata(tmp_path, system, suffix)@L283; test_archive_metadata_link_is_never_followed(tmp_path)@L290; staged(tmp_path, monkeypatch)@L298; test_invalid_local_or_remote_package_cannot_reach_upload(tmp_path, monkeypatch, defect)@L339; test_exact_staged_files_upload_to_prepared_id_without_overwrite(tmp_path, monkeypatch)@L370; send(identifier, file, name, digest)@L375; test_fixed_https_transport_id_digest_and_redirect_refusal(tmp_path, monkeypatch, status, digest_ok)@L405; __init__(self, host, timeout)@L415; putrequest(self, method, url)@L418; putheader(self, key, value)@L421; endheaders(self)@L425; send(self, block)@L428; getresponse(self)@L431; close(self)@L447; test_cli_command_allowlist_precedes_execution(monkeypatch)@L462; test_tag_absence_distinguishes_real404_from_permission_errors(monkeypatch)@L477; prepared_context(tmp_path, monkeypatch)@L500; test_actual_prepare_orders_all_checks_before_the_only_write(tmp_path, monkeypatch, defect)@L524; transport(endpoint, body)@L545; test_untrusted_context_never_reaches_github(tmp_path, monkeypatch, field, value)@L586; test_final_verification_rechecks_security_but_keeps_release_draft(tmp_path, monkeypatch, capsys)@L595; test_dirty_source_and_publish_operation_are_refused_before_network(tmp_path, monkeypatch)@L623; test_actual_checked_in_product_version_and_worker_metadata()@L636; test_api_structured_body_and_fixed_namespace(monkeypatch)@L641; execute(arguments, data)@L645
# variables: SOURCE@L30; VALUE@L31; result@L43; workflow@L44; category@L73; index@L73; prefix@L94; responses@L119; row@L120; responses@L151; key@L152; row@L153; field@L155; value@L155; analyses@L177; original@L236; changed@L238; bad@L247; prefix@L261; members@L262; archive@L267; content@L268; name@L268; archive@L271; content@L272; name@L272; entry@L273; file@L285; file@L292; directory@L302; installer@L304; archive@L306; file@L308; digest@L309; record@L324; changes@L341; directory@L348; record@L348; _@L372; record@L372; writes@L373; row@L378; row@L380; file@L407; digest@L409; events@L410; key@L459; value@L459; arguments@L467; accepted@L480; code@L480; error@L480; output@L480; workflow@L502; key@L509; value@L509; responses@L527; listing@L528; record@L540; reads@L543; writes@L543; record@L600; system@L601; name@L602; responses@L612; result@L617; error@L631; calls@L643; body@L651
# parameters: responses@L81; endpoint@L84; kwargs@L84; changes@L92; monkeypatch@L110; count@L117; monkeypatch@L117; defect@L149; monkeypatch@L149; monkeypatch@L193; endpoint@L195; change@L210; monkeypatch@L210; tag@L213; after@L234; before@L234; value@L245; source@L253; file@L259; symlink@L259; system@L259; value@L259; worker@L259; suffix@L283; system@L283; tmp_path@L283; tmp_path@L290; metadata_changes@L298; monkeypatch@L298; tmp_path@L298; tag@L325; endpoint@L329; defect@L339; monkeypatch@L339; tmp_path@L339; args@L364; monkeypatch@L370; tmp_path@L370; digest@L375; file@L375; identifier@L375; name@L375; digest_ok@L405; monkeypatch@L405; status@L405; tmp_path@L405; host@L415; self@L415; timeout@L415; method@L418; self@L418; url@L418; key@L421; self@L421; value@L421; self@L425; block@L428; self@L428; self@L431; limit@L437; self@L437; self@L447; monkeypatch@L462; args@L465; kwargs@L465; monkeypatch@L477; name@L479; args@L489; code@L489; error@L489; kwargs@L489; output@L489; monkeypatch@L500; tmp_path@L500; defect@L524; monkeypatch@L524; tmp_path@L524; body@L545; endpoint@L545; tag@L565; field@L586; monkeypatch@L586; tmp_path@L586; value@L586; args@L590; kwargs@L590; capsys@L595; monkeypatch@L595; tmp_path@L595; tag@L615; monkeypatch@L623; tmp_path@L623; args@L627; kwargs@L627; monkeypatch@L641; arguments@L645; data@L645
# </code-map>

"""Jason Stys: independent real-shape main/security/draft fixtures and actual archive/transport oracles.

No GitHub mutations occur: exact endpoint fixtures replace only network transport,
while production gate/policy/archive code runs. Payloads are inert synthetic bytes.
"""

import copy
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

from scripts import release_gate as gate

SOURCE = "a" * 40
VALUE = {
    "schema": 1,
    "product": "code-flow-studio",
    "version": "0.4.1",
    "source": SOURCE,
    "source_dirty": False,
    "worker_sha256": hashlib.sha256(b"fixed worker fixture").hexdigest(),
}


def source_responses():
    """Independent documented GitHub shapes: exactly one main push and three processed categories."""
    result = {gate.BASE + "/git/ref/heads/main": {"object": {"sha": SOURCE}}}
    for workflow in ("validate.yml", "packages.yml", "codeql.yml"):
        result[f"{gate.BASE}/actions/workflows/{workflow}/runs?head_sha={SOURCE}&per_page=100"] = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 101,
                    "head_sha": SOURCE,
                    "event": "push",
                    "head_branch": "main",
                    "status": "completed",
                    "conclusion": "success",
                    "path": ".github/workflows/" + workflow,
                    "repository": {"full_name": "JasonStys/code-flow-studio"},
                }
            ],
        }
    result[gate.BASE + "/code-scanning/analyses?ref=refs%2Fheads%2Fmain&per_page=100&page=1"] = [
        {
            "id": index + 200,
            "commit_sha": SOURCE,
            "ref": "refs/heads/main",
            "category": category,
            "analysis_key": ".github/workflows/codeql.yml:analyze",
            "tool": {"name": "CodeQL"},
            "error": "",
            "warning": "",
            "results_count": 0,
            "rules_count": 50,
        }
        for index, category in enumerate(
            ("/language:python", "/language:javascript-typescript", "/language:actions")
        )
    ]
    result[gate.BASE + "/code-scanning/alerts?ref=refs%2Fheads%2Fmain&state=open&per_page=100&page=1"] = []
    return result


def strict_reader(responses):
    """Unknown endpoints fail, rather than a blanket successful API stub hiding a missing check."""

    def read(endpoint, **kwargs):
        """Return only an independently specified read response; unexpected writes fail the test."""
        assert not kwargs and endpoint in responses, endpoint
        return copy.deepcopy(responses[endpoint])

    return read


def release_record(**changes):
    """Authenticated untagged draft URL is legitimate; numeric API and upload URLs bind its identity."""
    prefix = gate.BASE + "/releases/123"
    return {
        "id": 123,
        "tag_name": "v0.4.1",
        "target_commitish": SOURCE,
        "draft": True,
        "prerelease": False,
        "url": "https://api.github.com/" + prefix,
        "upload_url": "https://uploads.github.com/" + prefix + "/assets{?name,label}",
        "assets_url": "https://api.github.com/" + prefix + "/assets",
        "assets": [],
        "html_url": "https://github.com/JasonStys/code-flow-studio/releases/untagged-valid-alias",
        **changes,
    }


def test_real_source_response_contract_passes(monkeypatch):
    """Exercise the actual gate with complete, independently authored main and scan response fields."""
    monkeypatch.setattr(gate, "api", strict_reader(source_responses()))
    gate.require_source(VALUE)


@pytest.mark.parametrize("count", [None, 0, True, -1, "50"])
def test_zero_unknown_or_noninteger_codeql_rule_counts_never_authorize_release(monkeypatch, count):
    """An error-free category without actual executed rules is not a processed security prerequisite."""
    responses = source_responses()
    row = responses[gate.BASE + "/code-scanning/analyses?ref=refs%2Fheads%2Fmain&per_page=100&page=1"][0]
    if count is None:
        del row["rules_count"]
    else:
        row["rules_count"] = count
    monkeypatch.setattr(gate, "api", strict_reader(responses))
    with pytest.raises(ValueError, match="actual executed rules"):
        gate.require_source(VALUE)


@pytest.mark.parametrize(
    "defect",
    [
        "running",
        "failed",
        "wrong-sha",
        "pr-only",
        "wrong-branch",
        "missing",
        "ambiguous",
        "truncated",
        "main-moved",
        "missing-category",
        "pr-analysis",
        "analysis-error",
        "analysis-warning",
        "open-alert",
    ],
)
def test_source_failures_cannot_authorize_release(monkeypatch, defect):
    """Status, event, source, completeness and actual code-scanning results are independent prerequisites."""
    responses = source_responses()
    key = f"{gate.BASE}/actions/workflows/validate.yml/runs?head_sha={SOURCE}&per_page=100"
    row = responses[key]["workflow_runs"][0]
    if defect in {"running", "failed", "wrong-sha", "pr-only", "wrong-branch"}:
        field, value = {
            "running": ("status", "in_progress"),
            "failed": ("conclusion", "failure"),
            "wrong-sha": ("head_sha", "b" * 40),
            "pr-only": ("event", "pull_request"),
            "wrong-branch": ("head_branch", "feature"),
        }[defect]
        row[field] = value
    elif defect == "missing":
        responses[key] = {"total_count": 0, "workflow_runs": []}
    elif defect == "ambiguous":
        responses[key]["workflow_runs"].append(copy.deepcopy(row))
        responses[key]["total_count"] = 2
    elif defect == "truncated":
        responses[key]["total_count"] = 2
    elif defect == "main-moved":
        responses[gate.BASE + "/git/ref/heads/main"]["object"]["sha"] = "b" * 40
    elif defect == "open-alert":
        responses[
            gate.BASE + "/code-scanning/alerts?ref=refs%2Fheads%2Fmain&state=open&per_page=100&page=1"
        ] = [{"number": 1}]
    else:
        analyses = responses[
            gate.BASE + "/code-scanning/analyses?ref=refs%2Fheads%2Fmain&per_page=100&page=1"
        ]
        if defect == "missing-category":
            analyses.pop()
        elif defect == "pr-analysis":
            analyses[0]["ref"] = "refs/pull/1/merge"
        elif defect == "analysis-error":
            analyses[0]["error"] = "extraction failed"
        else:
            analyses[0]["warning"] = "incomplete scan"
    monkeypatch.setattr(gate, "api", strict_reader(responses))
    with pytest.raises(ValueError):
        gate.require_source(VALUE)


def test_unknown_or_full_scan_pages_fail_closed(monkeypatch):
    """A full three-page cap, absent authorization or unavailable metadata cannot establish zero alerts."""
    monkeypatch.setattr(gate, "api", lambda endpoint: [{}] * 100)
    with pytest.raises(ValueError, match="complete review bound"):
        gate.complete_list(gate.BASE + "/code-scanning/alerts?state=open")


@pytest.mark.parametrize(
    "change",
    [
        {"draft": False},
        {"prerelease": True},
        {"target_commitish": "b" * 40},
        {"tag_name": "v0.4.0"},
        {"id": 124},
    ],
)
def test_prepared_numeric_id_cannot_be_public_or_swapped(monkeypatch, change):
    """The real list/detail identity helper and source/state checks run before any binary transport."""
    monkeypatch.setattr(gate, "api", strict_reader({gate.BASE + "/releases/123": release_record(**change)}))
    monkeypatch.setattr(gate, "no_tag", lambda tag: None)
    with pytest.raises(ValueError):
        gate.draft(123, VALUE)


@pytest.mark.parametrize(
    "before,after",
    [
        ("workflow_dispatch:", "pull_request_target:"),
        ("python -m scripts.release_gate prepare", "echo skipped-gate"),
        ("python -m scripts.release_gate upload", "gh release upload --clobber"),
        ("python -m scripts.release_gate verify", "gh release edit --draft=false"),
        ("security-events: read", "security-events: write"),
        ("EXPECTED_RELEASE_ID: ${{ needs.prepare.outputs.release_id }}", "EXPECTED_RELEASE_ID: guessed"),
        ("ref: ${{ github.sha }}", "ref: main"),
        ("ref: ${{ github.sha }}", "ref: ${{ needs.prepare.outputs.sha }}"),
        ("if: github.ref == 'refs/heads/main'", "if: always()"),
        ("npm run test:desktop", "echo skipped-native"),
        ("max-parallel: 1", "max-parallel: 3"),
    ],
)
def test_actual_workflow_policy_rejects_security_mutants(before, after):
    """Mutate the real checked-in workflow, not a hand-made proxy manifest or an implementation echo."""
    original = (gate.ROOT / ".github/workflows/release-native.yml").read_text()
    gate.workflow_policy(original)
    changed = original.replace(before, after)
    assert changed != original
    with pytest.raises(ValueError):
        gate.workflow_policy(changed)


@pytest.mark.parametrize("value", [True, "1", 2])
def test_package_schema_is_strict(value):
    """Python boolean/integer equality must not authorize malformed package provenance."""
    bad = {**VALUE, "schema": value}
    with pytest.raises(ValueError):
        gate.valid_metadata(bad)


@pytest.mark.parametrize("source", ['{"schema":1,"schema":1}', '{"schema":NaN}', "[]"])
def test_metadata_duplicates_nonfinite_and_nonobjects_are_errors(source):
    """Parsed values must retain one unambiguous identity rather than silently choosing a later field."""
    with pytest.raises(ValueError):
        gate.strict_object(source)


def portable(file, value=VALUE, worker=b"fixed worker fixture", *, system="Windows", symlink=False):
    """Build real small archive bytes with the same relative resource layout as the actual Electron package."""
    prefix = "Code Flow Studio.app/Contents/Resources/" if system == "macOS" else "resources/"
    members = {
        prefix + "metadata/source-release.json": json.dumps(value).encode(),
        prefix + "runner/node_checks.cjs": worker,
    }
    if system == "Windows":
        with zipfile.ZipFile(file, "w") as archive:
            for name, content in members.items():
                archive.writestr(name, content)
    else:
        with tarfile.open(file, "w:gz") as archive:
            for name, content in members.items():
                entry = tarfile.TarInfo(name)
                if symlink:
                    entry.type, entry.linkname = tarfile.SYMTYPE, "../../outside"
                    archive.addfile(entry)
                else:
                    entry.size = len(content)
                    archive.addfile(entry, io.BytesIO(content))


@pytest.mark.parametrize("system,suffix", [("Windows", ".zip"), ("Linux", ".tar.gz"), ("macOS", ".tar.gz")])
def test_actual_platform_archive_metadata(tmp_path, system, suffix):
    """Each existing platform layout binds real archive metadata and fixed worker bytes without extraction."""
    file = tmp_path / ("fixture" + suffix)
    portable(file, system=system)
    assert gate.archive_metadata(file, system) == (VALUE, VALUE["worker_sha256"])


def test_archive_metadata_link_is_never_followed(tmp_path):
    """A POSIX link cannot impersonate either source identity or a regular fixed-worker member."""
    file = tmp_path / "fixture.tar.gz"
    portable(file, system="Linux", symlink=True)
    with pytest.raises(ValueError, match="nonregular"):
        gate.archive_metadata(file, "Linux")


def staged(tmp_path, monkeypatch, **metadata_changes):
    """Make two real inert Windows payloads, sidecars and a compiled-acceptance receipt for upload gates."""
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setenv("RUNNER_OS", "Windows")
    directory = tmp_path / "release/installers"
    directory.mkdir(parents=True)
    installer = directory / "Code Flow Studio Setup 0.4.1.exe"
    installer.write_bytes(b"inert fixture, never executable")
    archive = directory / "CodeFlowStudio-0.4.1-windows-x64.zip"
    portable(archive, {**VALUE, **metadata_changes})
    for file in (installer, archive):
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        file.with_name(file.name + ".sha256").write_text(f"{digest}  {file.name.replace(' ', '.')}\n")
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts/native-resource-acceptance.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "version": "0.4.1",
                "source": SOURCE,
                "worker_sha256": VALUE["worker_sha256"],
                "compiled_app": True,
                "journey": "passed",
            }
        )
    )
    record = release_record()
    monkeypatch.setattr(gate, "no_tag", lambda tag: None)
    monkeypatch.setattr(
        gate,
        "api",
        lambda endpoint: copy.deepcopy(record)
        if endpoint == gate.BASE + "/releases/123"
        else pytest.fail(endpoint),
    )
    return record, directory


@pytest.mark.parametrize(
    "defect", ["wrong-source", "dirty-source", "bad-sidecar", "missing-receipt", "colliding-asset"]
)
def test_invalid_local_or_remote_package_cannot_reach_upload(tmp_path, monkeypatch, defect):
    """Real archive/checksum/receipt bytes and existing asset state independently prevent the transport call."""
    changes = (
        {"source": "b" * 40}
        if defect == "wrong-source"
        else {"source_dirty": True}
        if defect == "dirty-source"
        else {}
    )
    record, directory = staged(tmp_path, monkeypatch, **changes)
    if defect == "bad-sidecar":
        (directory / "Code Flow Studio Setup 0.4.1.exe.sha256").write_text("wrong")
    elif defect == "missing-receipt":
        (tmp_path / "artifacts/native-resource-acceptance.json").unlink()
    elif defect == "colliding-asset":
        record["assets"] = [
            {
                "id": 77,
                "name": "Code.Flow.Studio.Setup.0.4.1.exe",
                "size": 12,
                "state": "uploaded",
                "digest": "sha256:" + "c" * 64,
            }
        ]
    monkeypatch.setattr(
        gate, "upload_bytes", lambda *args: pytest.fail("Invalid inputs reached a release write")
    )
    with pytest.raises((ValueError, OSError)):
        gate.upload(VALUE, 123)


def test_exact_staged_files_upload_to_prepared_id_without_overwrite(tmp_path, monkeypatch):
    """A real valid archive/receipt/sidecar admits exactly four same-platform new assets with matching provider bytes."""
    record, _ = staged(tmp_path, monkeypatch)
    writes = []

    def send(identifier, file, name, digest):
        """Only the transport is substituted; production rereads the updated numeric-ID metadata after each upload."""
        assert identifier == 123
        assert name not in {row["name"] for row in record["assets"]}
        assert digest == hashlib.sha256(file.read_bytes()).hexdigest()
        row = {
            "id": 100 + len(writes),
            "name": name,
            "size": file.stat().st_size,
            "state": "uploaded",
            "digest": "sha256:" + digest,
        }
        record["assets"].append(row)
        writes.append(name)
        return row

    monkeypatch.setattr(gate, "upload_bytes", send)
    gate.upload(VALUE, 123)
    assert set(writes) == {
        "Code.Flow.Studio.Setup.0.4.1.exe",
        "Code.Flow.Studio.Setup.0.4.1.exe.sha256",
        "CodeFlowStudio-0.4.1-windows-x64.zip",
        "CodeFlowStudio-0.4.1-windows-x64.zip.sha256",
    }
    with pytest.raises(ValueError, match="collision"):
        gate.upload(VALUE, 123)
    assert len(writes) == 4


@pytest.mark.parametrize("status,digest_ok", [(201, True), (302, True), (403, True), (201, False)])
def test_fixed_https_transport_id_digest_and_redirect_refusal(tmp_path, monkeypatch, status, digest_ok):
    """Inspect actual HTTP request construction/streaming; no redirect, foreign host or mismatched provider digest passes."""
    file = tmp_path / "fixture.zip"
    file.write_bytes(b"inert streamed fixture")
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    events = []

    class Connection:
        """Independent HTTPS transport fake records the exact host, method, URL, headers and binary chunks."""

        def __init__(self, host, timeout):
            assert host == "uploads.github.com" and timeout == 30

        def putrequest(self, method, url):
            events.append((method, url))

        def putheader(self, key, value):
            if key != "Authorization":
                events.append((key, value))

        def endheaders(self):
            pass

        def send(self, block):
            events.append(("bytes", block))

        def getresponse(self):
            return type(
                "Response",
                (),
                {
                    "status": status,
                    "read": lambda self, limit: json.dumps(
                        {
                            "name": "fixture.zip",
                            "size": file.stat().st_size,
                            "digest": "sha256:" + (digest if digest_ok else "c" * 64),
                        }
                    ).encode(),
                },
            )()

        def close(self):
            events.append(("closed", True))

    monkeypatch.setattr(gate.http.client, "HTTPSConnection", Connection)
    monkeypatch.setenv("GH_TOKEN", "synthetic-test-value-never-sent")
    if status == 201 and digest_ok:
        gate.upload_bytes(123, file, "fixture.zip", digest)
    else:
        with pytest.raises(ValueError):
            gate.upload_bytes(123, file, "fixture.zip", digest)
    assert events[0] == ("POST", "/repos/JasonStys/code-flow-studio/releases/123/assets?name=fixture.zip")
    assert events[-1] == ("closed", True)
    assert b"".join(value for key, value in events if key == "bytes") == file.read_bytes()


def test_cli_command_allowlist_precedes_execution(monkeypatch):
    """An arbitrary command or foreign API cannot turn the trusted release helper into a shell bridge."""
    monkeypatch.setattr(
        gate.subprocess, "run", lambda *args, **kwargs: pytest.fail("Unapproved command executed")
    )
    for arguments in (
        ["powershell", "-Command", "echo wrong"],
        ["gh", "api", "repos/foreign/repository/releases"],
        ["git", "checkout", "main"],
        ["gh", "api", gate.BASE + "/releases/123", "--method", "DELETE"],
    ):
        with pytest.raises(ValueError):
            gate.command(arguments)


def test_tag_absence_distinguishes_real404_from_permission_errors(monkeypatch):
    """A genuine missing tag is distinct from denied/network metadata; neither a public tag nor unknown state passes."""
    monkeypatch.setattr(gate.shutil, "which", lambda name: str(Path(__file__).resolve()))
    for code, error, output, accepted in (
        (1, "gh: Not Found (HTTP 404)", "", True),
        (1, "gh: Forbidden (HTTP 403)", "", False),
        (1, "connection failed", "", False),
        (0, "", "{}", False),
    ):
        monkeypatch.setattr(
            gate.subprocess,
            "run",
            lambda *args, code=code, error=error, output=output, **kwargs: subprocess.CompletedProcess(
                args, code, output, error
            ),
        )
        if accepted:
            gate.no_tag("v0.4.1")
        else:
            with pytest.raises((ValueError, RuntimeError)):
                gate.no_tag("v0.4.1")


def prepared_context(tmp_path, monkeypatch):
    """Bind synthetic CI source to the actual workflow, preserving its real guard calls and policy checks."""
    workflow = (gate.ROOT / ".github/workflows/release-native.yml").read_text()
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/release-native.yml").write_text(workflow)
    (tmp_path / "docs/releases").mkdir(parents=True)
    (tmp_path / "docs/releases/v0.4.1.md").write_text("Owned synthetic release notes")
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "metadata", lambda: copy.deepcopy(VALUE))
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": "JasonStys/code-flow-studio",
        "GITHUB_SHA": SOURCE,
        "EXPECTED_SOURCE": SOURCE,
        "GITHUB_OUTPUT": str(tmp_path / "outputs"),
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(sys, "argv", ["release_gate", "prepare"])


@pytest.mark.parametrize(
    "defect", ["none", "incomplete-main", "open-alert", "existing-draft", "existing-public"]
)
def test_actual_prepare_orders_all_checks_before_the_only_write(tmp_path, monkeypatch, defect):
    """Execute the actual CLI through complete endpoint fixtures; failed prerequisites never create or reuse a release."""
    prepared_context(tmp_path, monkeypatch)
    responses = source_responses()
    listing = gate.BASE + "/releases?per_page=100&page=1"
    responses[listing] = []
    responses[gate.BASE + "/releases/123"] = release_record()
    if defect == "incomplete-main":
        responses[f"{gate.BASE}/actions/workflows/validate.yml/runs?head_sha={SOURCE}&per_page=100"][
            "workflow_runs"
        ][0]["status"] = "in_progress"
    elif defect == "open-alert":
        responses[
            gate.BASE + "/code-scanning/alerts?ref=refs%2Fheads%2Fmain&state=open&per_page=100&page=1"
        ] = [{"number": 2}]
    elif defect.startswith("existing"):
        record = release_record(draft=defect == "existing-draft")
        responses[listing] = [record]
        responses[gate.BASE + "/releases/123"] = record
    reads, writes = [], []

    def transport(endpoint, *, body=None):
        """The mutation fixture accepts only the exact fresh structured draft request after prior reads."""
        if body is not None:
            assert endpoint == gate.BASE + "/releases"
            assert body == {
                "tag_name": "v0.4.1",
                "target_commitish": SOURCE,
                "draft": True,
                "prerelease": False,
                "name": "Code Flow Studio 0.4.1",
                "body": "Owned synthetic release notes",
            }
            assert listing in reads and len(reads) >= 6
            writes.append(body)
            return release_record()
        assert endpoint in responses, endpoint
        reads.append(endpoint)
        return copy.deepcopy(responses[endpoint])

    monkeypatch.setattr(gate, "api", transport)
    monkeypatch.setattr(gate, "no_tag", lambda tag: None)
    if defect == "none":
        gate.main()
        assert len(writes) == 1
        assert (tmp_path / "outputs").read_text() == f"sha={SOURCE}\ntag=v0.4.1\nrelease_id=123\n"
    else:
        with pytest.raises(ValueError):
            gate.main()
        assert writes == [] and not (tmp_path / "outputs").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("GITHUB_ACTIONS", "false"),
        ("GITHUB_REF", "refs/pull/1/merge"),
        ("GITHUB_REPOSITORY", "foreign/repo"),
        ("GITHUB_SHA", "b" * 40),
        ("EXPECTED_SOURCE", "b" * 40),
    ],
)
def test_untrusted_context_never_reaches_github(tmp_path, monkeypatch, field, value):
    """A branch/PR, moved source or foreign repository cannot even start release metadata requests."""
    prepared_context(tmp_path, monkeypatch)
    monkeypatch.setenv(field, value)
    monkeypatch.setattr(gate, "api", lambda *args, **kwargs: pytest.fail("Untrusted context reached GitHub"))
    with pytest.raises(ValueError):
        gate.main()


def test_final_verification_rechecks_security_but_keeps_release_draft(tmp_path, monkeypatch, capsys):
    """Execute the final CLI path against full real-shape reads; it has no promotion transport or write."""
    prepared_context(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", ["release_gate", "verify"])
    monkeypatch.setenv("EXPECTED_RELEASE_ID", "123")
    record = release_record()
    for system in ("Windows", "Linux", "macOS"):
        for name in gate.names("0.4.1", system):
            record["assets"].append(
                {
                    "id": 100 + len(record["assets"]),
                    "name": name.replace(" ", "."),
                    "size": 12,
                    "state": "uploaded",
                    "digest": "sha256:" + "c" * 64,
                }
            )
    responses = source_responses()
    responses[gate.BASE + "/releases/123"] = record
    monkeypatch.setattr(gate, "api", strict_reader(responses))
    monkeypatch.setattr(gate, "no_tag", lambda tag: None)
    gate.main()
    result = json.loads(capsys.readouterr().out)
    assert result["draft"] is True and result["assets"] == 12 and result["source"] == SOURCE
    assert "pending" in result["publication"]
    assert record["draft"] is True


def test_dirty_source_and_publish_operation_are_refused_before_network(tmp_path, monkeypatch):
    """Neither a dirty local build nor an unimplemented promotion command can authorize release writes."""
    prepared_context(tmp_path, monkeypatch)
    monkeypatch.setattr(gate, "metadata", lambda: {**VALUE, "source_dirty": True})
    monkeypatch.setattr(gate, "api", lambda *args, **kwargs: pytest.fail("Dirty source reached GitHub"))
    with pytest.raises(ValueError):
        gate.main()
    monkeypatch.setattr(sys, "argv", ["release_gate", "publish"])
    with pytest.raises(SystemExit) as error:
        gate.main()
    assert error.value.code == 2


def test_actual_checked_in_product_version_and_worker_metadata():
    """Exercise the production data-only coherence reader independently of prepared-context fixtures."""
    assert gate.product_version() == "0.4.1"


def test_api_structured_body_and_fixed_namespace(monkeypatch):
    """The real API adapter serializes JSON data, never builds shell commands or accepts a foreign repository."""
    calls = []

    def execute(arguments, *, data=None):
        """Record the adapter's exact structured command boundary without contacting GitHub."""
        calls.append((arguments, data))
        return '{"id":123}'

    monkeypatch.setattr(gate, "command", execute)
    body = {"draft": True, "tag_name": "v0.4.1", "target_commitish": SOURCE}
    assert gate.api(gate.BASE + "/releases", body=body) == {"id": 123}
    assert calls[0][0] == ["gh", "api", gate.BASE + "/releases", "--method", "POST", "--input", "-"]
    assert json.loads(calls[0][1]) == body
    with pytest.raises(ValueError):
        gate.api("repos/foreign/repo/releases")
    assert len(calls) == 1
