# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_hosted_guard_refuses_user_pc_before_any_work(monkeypatch, tmp_path)@L27; test_hosted_output_is_confined_and_verifier_source_explicit(monkeypatch, tmp_path)@L36; metadata()@L56; test_publication_or_replaced_asset_never_authorizes_execution(defect)@L95; test_download_binds_canonical_hosts_actual_bytes_and_digest(tmp_path)@L117; transport(request)@L129; archive(path, monkeypatch, extra, bad_schema)@L153; test_real_tar_provenance_and_no_setuid_preservation(monkeypatch, tmp_path)@L180; test_actual_tar_negative_members_fail_closed(monkeypatch, tmp_path, kind)@L194; test_service_environment_cannot_inherit_provider_cloud_or_github_keys(monkeypatch, tmp_path)@L219; test_failed_startup_cleanup_targets_only_owned_child_and_preserves_live_recovery(tmp_path, can_exit)@L230; terminate()@L238; wait(timeout)@L241; test_actual_store_timeline_identity_and_shape_fail_closed(tmp_path, defect)@L255; test_incremental_receipt_and_full_restored_export_equality(monkeypatch, tmp_path)@L283; request(_client, method, path, body)@L291; validate(result, project)@L331
# variables: name@L39; value@L39; prefix@L58; rows@L59; i@L77; rows@L77; release@L97; tag@L97; body@L119; initial@L120; row@L121; seen@L127; client@L143; digest@L144; worker@L155; value@L157; output@L165; body@L166; name@L166; member@L171; content@L176; member@L176; source@L181; service@L183; source@L195; member@L196; content@L199; content@L204; result@L223; key@L225; temporary@L232; calls@L235; state@L236; process@L248; store@L257; revision@L258; identifier@L259; result@L263; exported@L264; timeline@L266; data@L285; store@L287; validations@L288; tamper@L289; revision@L300; identifier@L301; project@L302; result@L303; identifier@L311; result@L312; evidence@L337; service@L338; private@L339; row@L341; text@L342
# parameters: monkeypatch@L27; tmp_path@L27; monkeypatch@L36; tmp_path@L36; defect@L95; tmp_path@L117; request@L129; bad_schema@L153; extra@L153; monkeypatch@L153; path@L153; monkeypatch@L180; tmp_path@L180; kind@L194; monkeypatch@L194; tmp_path@L194; monkeypatch@L219; tmp_path@L219; can_exit@L230; tmp_path@L230; timeout@L241; defect@L255; tmp_path@L255; monkeypatch@L283; tmp_path@L283; _client@L291; body@L291; method@L291; path@L291; project@L331; result@L331
# </code-map>

"""Jason Stys: published-package/ownership/protocol negatives; no local Docker, network or service runs."""

import copy
import gzip
import hashlib
import io
import json
import os
import tarfile
from types import SimpleNamespace

import httpx
import pytest

from scripts import released_service_probe as probe
from studio.store import Store


def test_hosted_guard_refuses_user_pc_before_any_work(monkeypatch, tmp_path):
    """Even spoofed Actions variables cannot make a Windows machine an allowed Linux runner."""
    monkeypatch.setattr(probe.sys, "platform", "win32")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(ValueError, match="GitHub-hosted Linux"):
        probe.hosted_output(tmp_path / "evidence")
    assert not (tmp_path / "evidence").exists()


def test_hosted_output_is_confined_and_verifier_source_explicit(monkeypatch, tmp_path):
    """A valid disposable context still cannot select a report outside its workspace."""
    monkeypatch.setattr(probe.sys, "platform", "linux")
    for name, value in {
        "GITHUB_ACTIONS": "true",
        "RUNNER_OS": "Linux",
        "RUNNER_ENVIRONMENT": "github-hosted",
        "GITHUB_REPOSITORY": probe.REPOSITORY,
        "GITHUB_WORKSPACE": str(tmp_path),
        "GITHUB_SHA": "a" * 40,
    }.items():
        monkeypatch.setenv(name, value)
    assert probe.hosted_output(tmp_path / "artifacts") == tmp_path / "artifacts/released-service-probe.json"
    with pytest.raises(ValueError, match="inside"):
        probe.hosted_output(tmp_path.parent / "outside-receipt")
    monkeypatch.setenv("GITHUB_SHA", "main")
    with pytest.raises(ValueError, match="identity"):
        probe.hosted_output(tmp_path / "artifacts")


def metadata():
    """Independent real-shaped public metadata; unrelated assets are never downloaded."""
    prefix = "https://github.com/" + probe.REPOSITORY + "/releases/download/v0.4.2/"
    rows = [
        {
            "id": probe.PAYLOAD_ID,
            "name": probe.PAYLOAD,
            "size": probe.PAYLOAD_BYTES,
            "digest": "sha256:" + probe.PAYLOAD_SHA256,
            "state": "uploaded",
            "browser_download_url": prefix + probe.PAYLOAD,
        },
        {
            "id": 2,
            "name": probe.PAYLOAD + ".sha256",
            "size": 104,
            "digest": "sha256:" + "b" * 64,
            "state": "uploaded",
            "browser_download_url": prefix + probe.PAYLOAD + ".sha256",
        },
    ]
    rows += [{"id": i + 10, "name": "other-accepted-asset-" + str(i)} for i in range(10)]
    return (
        {
            "id": probe.RELEASE_ID,
            "tag_name": "v0.4.2",
            "draft": False,
            "prerelease": False,
            "target_commitish": probe.SOURCE,
            "published_at": "2026-11-10T15:00:00Z",
            "assets": rows,
        },
        {"ref": "refs/tags/v0.4.2", "object": {"type": "commit", "sha": probe.SOURCE}},
    )


@pytest.mark.parametrize(
    "defect", ["draft", "source", "tag", "replaced", "duplicate", "large-sidecar", "foreign-url"]
)
def test_publication_or_replaced_asset_never_authorizes_execution(defect):
    """Valid tag/version strings alone cannot authorize a different draft, source or binary."""
    release, tag = metadata()
    probe.release_assets(release, tag)
    if defect == "draft":
        release["draft"] = True
    elif defect == "source":
        release["target_commitish"] = "main"
    elif defect == "tag":
        tag["object"]["sha"] = "c" * 40
    elif defect == "replaced":
        release["assets"][0]["digest"] = "sha256:" + "c" * 64
    elif defect == "duplicate":
        release["assets"][-1] = copy.deepcopy(release["assets"][0])
    elif defect == "large-sidecar":
        release["assets"][1]["size"] = 4097
    else:
        release["assets"][0]["browser_download_url"] = "https://example.invalid/payload"
    with pytest.raises(ValueError):
        probe.release_assets(release, tag)


def test_download_binds_canonical_hosts_actual_bytes_and_digest(tmp_path):
    """A real streamed mock response exercises redirect scope and content checks, not the internet."""
    body = b"synthetic archive bytes"
    initial = metadata()[0]["assets"][0]["browser_download_url"]
    row = {
        "name": probe.PAYLOAD,
        "size": len(body),
        "digest": "sha256:" + hashlib.sha256(body).hexdigest(),
        "browser_download_url": initial,
    }
    seen = []

    def transport(request):
        seen.append(request)
        assert "authorization" not in request.headers and "cookie" not in request.headers
        if request.url.host == "github.com":
            return httpx.Response(
                302,
                headers={
                    "location": "https://release-assets.githubusercontent.com/github-production-release-asset/owned/file?signature=synthetic"
                },
            )
        return httpx.Response(200, stream=httpx.ByteStream(body))

    with httpx.Client(
        transport=httpx.MockTransport(transport), trust_env=False, follow_redirects=False
    ) as client:
        digest = probe.download(client, row, tmp_path / "payload")
    assert len(seen) == 2 and digest == hashlib.sha256(body).hexdigest()
    assert (tmp_path / "payload").read_bytes() == body
    with pytest.raises(ValueError, match="Foreign"):
        probe.download_url("https://example.invalid/payload", initial)
    with pytest.raises(ValueError, match="Unknown canonical"):
        probe.download_url(initial, "https://github.com/other/repo/releases/download/v1/file")


def archive(path, monkeypatch, extra=None, bad_schema=False):
    """Create actual small compressed tar bytes; the inert service is never launched."""
    worker = b"synthetic worker bytes"
    monkeypatch.setattr(probe, "WORKER_SHA256", hashlib.sha256(worker).hexdigest())
    value = {
        "schema": True if bad_schema else 1,
        "product": "code-flow-studio",
        "version": "0.4.2",
        "source": probe.SOURCE,
        "source_dirty": False,
        "worker_sha256": probe.WORKER_SHA256,
    }
    with tarfile.open(path, "w:gz") as output:
        for name, body in {
            "resources/metadata/source-release.json": json.dumps(value).encode(),
            "resources/runner/node_checks.cjs": worker,
            "resources/service/code-flow-service": b"inert-not-executable-code",
        }.items():
            member = tarfile.TarInfo(name)
            member.size = len(body)
            member.mode = 0o755
            output.addfile(member, io.BytesIO(body))
        if extra:
            member, content = extra
            output.addfile(member, io.BytesIO(content))


def test_real_tar_provenance_and_no_setuid_preservation(monkeypatch, tmp_path):
    source = tmp_path / "archive.tar.gz"
    archive(source, monkeypatch)
    service = probe.unpack(source, tmp_path / "unpacked")
    assert service.read_bytes() == b"inert-not-executable-code"
    if os.name == "posix":
        assert service.stat().st_mode & 0o7777 == 0o700
    else:
        assert service.stat().st_mode & 0o7000 == 0


@pytest.mark.parametrize(
    "kind", ["traversal", "absolute", "symlink", "hardlink", "duplicate", "schema-bool", "oversize-header"]
)
def test_actual_tar_negative_members_fail_closed(monkeypatch, tmp_path, kind):
    source = tmp_path / "archive.tar.gz"
    member = tarfile.TarInfo(
        "../outside" if kind == "traversal" else "/outside" if kind == "absolute" else "extra"
    )
    content = b"x"
    member.size = 1
    if kind in {"symlink", "hardlink"}:
        member.type = tarfile.SYMTYPE if kind == "symlink" else tarfile.LNKTYPE
        member.linkname, member.size = "../../outside", 0
        content = b""
    if kind == "duplicate":
        member.name = "resources/runner/node_checks.cjs"
    if kind == "oversize-header":
        member.size = probe.MAX_MEMBER + 1
        source.write_bytes(gzip.compress(member.tobuf() + bytes(1024)))
    else:
        archive(
            source, monkeypatch, (member, content) if kind != "schema-bool" else None, kind == "schema-bool"
        )
    with pytest.raises((ValueError, tarfile.TarError)):
        probe.unpack(source, tmp_path / "unpacked")
    assert not (tmp_path / "outside").exists()


def test_service_environment_cannot_inherit_provider_cloud_or_github_keys(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_OPENAI_KEY", "synthetic-private-provider")
    monkeypatch.setenv("GH_TOKEN", "synthetic-private-github")
    monkeypatch.setenv("DOCKER_CONTEXT", "unexpected-remote")
    result = probe.service_environment(tmp_path, "synthetic-launch-token", "synthetic-nonce")
    assert result["DOCKER_HOST"] == "unix:///var/run/docker.sock"
    assert not any(key.startswith(("STUDIO_", "GH_", "GITHUB_", "AWS_", "AZURE_")) for key in result)
    assert "DOCKER_CONTEXT" not in result


@pytest.mark.parametrize("can_exit", [True, False])
def test_failed_startup_cleanup_targets_only_owned_child_and_preserves_live_recovery(tmp_path, can_exit):
    """A failed pre-auth launch cannot orphan a stopped child or delete data used by a live child."""
    temporary = tmp_path / "cfs-released042-owned-test"
    temporary.mkdir()
    (temporary / "private-recovery").write_bytes(b"synthetic-only")
    calls = []
    state = {"alive": True}

    def terminate():
        calls.append("terminate-owned")

    def wait(timeout):
        assert timeout == 10
        calls.append("wait-owned")
        if not can_exit:
            raise TimeoutError("synthetic failure")
        state["alive"] = False

    process = SimpleNamespace(poll=lambda: None if state["alive"] else 0, terminate=terminate, wait=wait)
    assert probe.cleanup_owned([SimpleNamespace(process=process, client=None)], temporary) is can_exit
    assert calls == ["terminate-owned", "wait-owned"]
    assert temporary.exists() is not can_exit


@pytest.mark.parametrize("defect", ["list", "project", "revision", "run", "checks", "truncated"])
def test_actual_store_timeline_identity_and_shape_fail_closed(tmp_path, defect):
    """Use real SQLite timeline output, then alter one independent identity or evidence field."""
    store = Store(tmp_path / "timeline.sqlite")
    revision = store.create(probe.practical_project("python").model_dump())
    identifier = store.queue(revision["id"])
    store.finish(
        identifier, "completed", {"checks": {"passed": 6, "failed": 0}, "coverage": {"status": "measured"}}
    )
    result = store.run(identifier)
    exported = {**result, "iteration_history": store.timeline(revision["id"])}
    probe.validate_export(exported, result, revision)
    timeline = exported["iteration_history"]
    if defect == "list":
        exported["iteration_history"] = timeline["revisions"]
    elif defect == "project":
        timeline["project_id"] = "another-project"
    elif defect == "revision":
        timeline["revisions"][0]["id"] = "another-revision"
    elif defect == "run":
        timeline["revisions"][0]["attempts"][0]["id"] = "another-run"
    elif defect == "checks":
        timeline["revisions"][0]["attempts"][0]["checks"]["failed"] = 1
    else:
        timeline["truncated"] = True
    with pytest.raises(ValueError, match="JSON export timeline"):
        probe.validate_export(exported, result, revision)


def test_incremental_receipt_and_full_restored_export_equality(monkeypatch, tmp_path):
    """Mock only HTTP/compilation for this lifecycle unit; real frozen/worker proof remains hosted."""
    data = tmp_path / "account-data"
    data.mkdir()
    store = Store(tmp_path / "actual-store.sqlite")
    validations = []
    tamper = {"export": False}

    def request(_client, method, path, body=None):
        if path in {"/private/register", "/private/login"}:
            return {"recovery": "synthetic-do-not-log-recovery"}
        if path == "/private/unlock":
            (data / "active").mkdir(exist_ok=True)
            return {"unlocked": True}
        if path == "/private/api/revisions" and method == "POST":
            return store.create(body)
        if path.endswith("/run"):
            revision = path.split("/")[-2]
            identifier = store.queue(revision)
            project = store.revision(revision)["project"]
            result = {
                "compilation": {"exit_code": 0},
                "checks": {"passed": len(project["cases"]), "failed": 0},
                "coverage": {"status": "measured"},
            }
            store.finish(identifier, "completed", result)
            return {"id": identifier}
        if path.startswith("/private/api/runs/"):
            identifier = path.split("/")[4]
            result = store.run(identifier)
            if "?format=json" in path:
                result["iteration_history"] = store.timeline(result["revision_id"])
                if tamper["export"]:
                    result["iteration_history"]["revisions"][0]["attempts"][0]["coverage"] = {
                        "status": "changed"
                    }
            return result
        if path == "/private/api/revisions":
            return store.history()
        if path == "/private/lock":
            (data / "active").rmdir()
            (data / "encrypted").mkdir(exist_ok=True)
            (data / "encrypted/synthetic.cfsvault").write_bytes(b"synthetic-sealed-fixture")
            return {"locked": True}
        if path == "/private/save":
            return {"saved": True}
        raise AssertionError("Unexpected route")

    def validate(result, project):
        assert result["compilation"]["exit_code"] == 0 and result["checks"]["passed"] == len(project.cases)
        validations.append(project.language)

    monkeypatch.setattr(probe, "request_json", request)
    monkeypatch.setattr(probe, "validate_positive", validate)
    evidence = probe.Evidence(tmp_path / "receipts/report.json")
    service = SimpleNamespace(client=object())
    private = probe.exercise(service, data, evidence)
    assert len(validations) == len(store.history()) == 12
    assert sum(row["approved_cases"] for row in evidence.record["languages"]) == 72
    text = evidence.output.read_text()
    assert (
        private["password"] not in text
        and private["key"]["key"] not in text
        and "synthetic-do-not-log-recovery" not in text
    )
    probe.restored(service, data, private)
    tamper["export"] = True
    with pytest.raises(ValueError, match="export differs"):
        probe.restored(service, data, private)
