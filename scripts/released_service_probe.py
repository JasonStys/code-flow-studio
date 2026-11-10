# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Evidence@L117; Service@L421
# functions: require(condition, message)@L72; strict_json(body)@L78; pairs(items)@L81; constant(_value)@L86; hosted_output(output)@L92; __init__(self, output)@L120; save(self)@L134; stage(self, stage)@L141; bounded_body(response, maximum)@L147; api_json(client, path)@L156; release_assets(release, tag)@L164; download_url(url, initial)@L216; download(client, row, target)@L240; preflight_tar(stream)@L280; unpack(archive, destination)@L316; service_environment(home, token, nonce)@L392; request_json(client, method, path, data)@L410; __init__(self, executable, data, home)@L424; ready(self)@L437; stop(self)@L471; validate_export(exported, result, revision)@L484; exercise(service, data, evidence)@L536; restored(service, data, private)@L607; canonical_digest(value)@L640; cleanup_owned(services, temporary)@L647; main()@L670
# variables: SOURCE@L42; WORKER_SHA256@L43; VERSION@L44; RELEASE_ID@L45; REPOSITORY@L46; API@L47; PAYLOAD@L48; PAYLOAD_ID@L49; PAYLOAD_BYTES@L50; PAYLOAD_SHA256@L51; MAX_ARCHIVE@L52; MAX_EXPANDED@L53; MAX_MEMBER@L54; MAX_RESPONSE@L55; EXPECTED_LANGUAGES@L56; result@L82; workspace@L102; selected@L104; temporary@L135; body@L149; chunk@L150; response@L159; rows@L182; row@L184; row@L188; row@L189; row@L190; found@L193; row@L193; maximum@L201; name@L201; row@L202; expected@L211; prefix@L219; parsed@L221; initial@L242; url@L251; started@L252; _@L253; response@L256; url@L258; digest@L262; measured@L262; stream@L263; chunk@L264; measured@L265; expanded@L282; headers@L282; raw@L283; header@L285; expanded@L286; expanded@L290; chunk@L292; expanded@L293; headers@L296; number@L298; size@L300; kind@L301; limit@L303; remaining@L305; chunk@L307; remaining@L311; expanded@L312; expanded@L319; seen@L319; stream@L320; package@L324; index@L325; member@L325; name@L326; parts@L329; c@L337; part@L338; key@L341; expanded@L346; selected@L348; source@L353; measured@L355; output@L356; chunk@L357; measured@L358; resources@L363; metadata@L364; value@L366; worker@L382; service@L387; config@L394; response@L416; output@L428; deadline@L439; source@L441; body@L442; matches@L444; origin@L447; candidate@L448; health@L456; key@L488; value@L488; history@L491; snapshot@L504; attempt@L518; actual@L519; key@L526; alias@L539; password@L539; key@L540; client@L544; stored@L549; language@L550; project@L552; revision@L556; identifier@L557; job@L563; deadline@L565; result@L567; exported@L574; digest@L580; client@L609; history@L617; row@L620; row@L623; result@L624; exported@L625; failed@L649; service@L650; failed@L660; service@L661; parser@L672; args@L676; output@L677; evidence@L678; temporary@L679; services@L681; client@L683; payload@L684; sidecar@L684; archive@L688; checksum@L688; digest@L689; executable@L696; data@L698; first@L700; private@L703; second@L706; row@L715
# parameters: condition@L72; message@L72; body@L78; items@L81; _value@L86; output@L92; output@L120; self@L120; self@L134; public@L141; self@L141; stage@L141; maximum@L147; response@L147; client@L156; path@L156; release@L164; tag@L164; initial@L216; url@L216; client@L240; row@L240; target@L240; stream@L280; archive@L316; destination@L316; home@L392; nonce@L392; token@L392; client@L410; data@L410; method@L410; path@L410; data@L424; executable@L424; home@L424; self@L424; self@L437; self@L471; exported@L484; result@L484; revision@L484; data@L536; evidence@L536; service@L536; data@L607; private@L607; service@L607; value@L640; services@L647; temporary@L647
# </code-map>

"""Jason Stys: hosted-only published0.4.2 frozen-service -> Docker -> sealed-history acceptance.

The CLI guards network/process work before starting. Helpers have independent
byte/protocol tests; no test invokes local Docker. Locations: docs/code-index.md.
No credential, recovery value, account path, raw service log or report body is emitted.
"""

import argparse
import base64
import gzip
import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urljoin, urlsplit

import httpx
import psutil

from examples.practical_projects import practical_project
from scripts.compiler_acceptance import validate_positive
from studio.models import LANGUAGES

SOURCE = "eb9b1cd0c3e3fd1e70e397edeffb059073464f74"
WORKER_SHA256 = "750b665e545b7cf0806d4c493db86174f7f4e7ab2218aa239718e652ccdce158"
VERSION = "0.4.2"
RELEASE_ID = 440504623
REPOSITORY = "JasonStys/code-flow-studio"
API = "https://api.github.com/repos/" + REPOSITORY
PAYLOAD = "CodeFlowStudio-0.4.2-linux-x64.tar.gz"
PAYLOAD_ID = 731850461
PAYLOAD_BYTES = 188603375
PAYLOAD_SHA256 = "1e75085bae4ab2611ead61a513b60f444941495608840cf33875d940cf963ebe"
MAX_ARCHIVE = 512 * 1024 * 1024
MAX_EXPANDED = 2 * 1024 * 1024 * 1024
MAX_MEMBER = 512 * 1024 * 1024
MAX_RESPONSE = 2 * 1024 * 1024
EXPECTED_LANGUAGES = {
    "python",
    "javascript",
    "typescript",
    "cpp",
    "c",
    "java",
    "csharp",
    "rust",
    "php",
    "bash",
    "sql",
    "assembly",
}


def require(condition: bool, message: str) -> None:
    """Raise a fixed authored error without relying on removable Python assertions."""
    if not condition:
        raise ValueError(message)


def strict_json(body: bytes):
    """Reject duplicate/nonfinite JSON, without echoing the original data."""

    def pairs(items):
        result = dict(items)
        require(len(result) == len(items), "Duplicate JSON field")
        return result

    def constant(_value):
        raise ValueError("Nonfinite JSON value")

    return json.loads(body, object_pairs_hook=pairs, parse_constant=constant)


def hosted_output(output: Path) -> Path:
    """Refuse every execution path before network/process work outside the disposable hosted Linux job."""
    require(
        sys.platform == "linux"
        and os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("RUNNER_OS") == "Linux"
        and os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted"
        and os.environ.get("GITHUB_REPOSITORY") == REPOSITORY,
        "Published service probe requires the owned GitHub-hosted Linux job",
    )
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", "")).resolve()
    require(workspace.is_dir() and bool(os.environ.get("GITHUB_WORKSPACE")), "Hosted workspace unavailable")
    selected = output.resolve()
    require(
        selected.is_relative_to(workspace) and selected != workspace,
        "Receipt must stay inside the owned workspace",
    )
    require(
        re.fullmatch(r"[a-f0-9]{40}", os.environ.get("GITHUB_SHA", "")) is not None,
        "Verifier source identity unavailable",
    )
    require(not selected.exists() or selected.is_dir(), "Receipt output must be a directory")
    return selected / "released-service-probe.json"


class Evidence:
    """Atomically preserve only public provenance, controlled stages, counts and hashes."""

    def __init__(self, output: Path):
        self.output = output
        self.record = {
            "schema": 1,
            "version": VERSION,
            "released_source": SOURCE,
            "verifier_source": os.environ.get("GITHUB_SHA"),
            "status": "running",
            "stage": "starting",
            "languages": [],
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        self.save()

    def save(self):
        temporary = self.output.with_name(self.output.name + ".tmp")
        temporary.write_text(
            json.dumps(self.record, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        temporary.replace(self.output)

    def stage(self, stage: str, **public):
        self.record.update(public)
        self.record["stage"] = stage
        self.save()


def bounded_body(response: httpx.Response, maximum: int) -> bytes:
    """Bound actual response bytes, including decompressed JSON, before parsing."""
    body = bytearray()
    for chunk in response.iter_bytes(8192):
        body.extend(chunk)
        require(len(body) <= maximum, "Response byte budget exceeded")
    return bytes(body)


def api_json(client: httpx.Client, path: str):
    """Read only fixed public repository API endpoints with no token or redirect."""
    require(path in {"/releases/tags/v0.4.2", "/git/ref/tags/v0.4.2"}, "Unknown public metadata endpoint")
    with client.stream("GET", API + path, headers={"Accept": "application/vnd.github+json"}) as response:
        require(response.status_code == 200, "Public release metadata unavailable")
        return strict_json(bounded_body(response, 256 * 1024))


def release_assets(release: dict, tag: dict) -> tuple[dict, dict]:
    """Bind the actual published release, immutable tag and unique known Linux assets."""
    require(
        release.get("id") == RELEASE_ID
        and type(release.get("id")) is int
        and release.get("tag_name") == "v" + VERSION
        and release.get("draft") is False
        and release.get("prerelease") is False
        and release.get("target_commitish") == SOURCE
        and bool(release.get("published_at")),
        "Published release identity mismatch",
    )
    require(
        tag.get("ref") == "refs/tags/v" + VERSION
        and tag.get("object", {}).get("type") == "commit"
        and tag["object"].get("sha") == SOURCE,
        "Published tag source mismatch",
    )
    rows = release.get("assets")
    require(
        isinstance(rows, list) and len(rows) == 12 and all(isinstance(row, dict) for row in rows),
        "Published asset inventory mismatch",
    )
    require(
        len({row.get("name") for row in rows}) == 12
        and all(type(row.get("id")) is int and row["id"] > 0 for row in rows)
        and len({row["id"] for row in rows}) == 12,
        "Ambiguous published assets",
    )
    found = {row["name"]: row for row in rows}
    require(PAYLOAD in found and PAYLOAD + ".sha256" in found, "Published Linux payload/sidecar missing")
    require(
        found[PAYLOAD].get("id") == PAYLOAD_ID
        and found[PAYLOAD].get("size") == PAYLOAD_BYTES
        and found[PAYLOAD].get("digest") == "sha256:" + PAYLOAD_SHA256,
        "Accepted published payload was replaced",
    )
    for name, maximum in [(PAYLOAD, MAX_ARCHIVE), (PAYLOAD + ".sha256", 4096)]:
        row = found[name]
        require(
            type(row.get("size")) is int
            and 0 < row["size"] <= maximum
            and row.get("state") == "uploaded"
            and isinstance(row.get("digest"), str)
            and re.fullmatch(r"sha256:[a-f0-9]{64}", row["digest"]),
            "Published asset size/digest mismatch",
        )
        expected = "https://github.com/" + REPOSITORY + "/releases/download/v" + VERSION + "/" + quote(name)
        require(row.get("browser_download_url") == expected, "Published asset URL mismatch")
    return found[PAYLOAD], found[PAYLOAD + ".sha256"]


def download_url(url: str, initial: str) -> None:
    """Allow canonical public GitHub URL or bounded signed release-CDN redirects only."""
    require(isinstance(url, str) and len(url) <= 16384, "Download URL outside budget")
    prefix = "https://github.com/" + REPOSITORY + "/releases/download/v" + VERSION + "/"
    require(initial in {prefix + PAYLOAD, prefix + PAYLOAD + ".sha256"}, "Unknown canonical release download")
    parsed = urlsplit(url)
    require(
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and parsed.port is None
        and not parsed.fragment,
        "Unsafe download destination",
    )
    if parsed.hostname == "github.com":
        require(url == initial, "Unexpected repository download redirect")
    else:
        require(
            parsed.hostname in {"release-assets.githubusercontent.com", "objects.githubusercontent.com"}
            and re.match(r"^/github-production-release-asset(?:-[a-f0-9]+)?/", parsed.path),
            "Foreign download redirect",
        )


def download(client: httpx.Client, row: dict, target: Path) -> str:
    """Stream exactly the provider-declared bytes, enforce a total deadline and verify its SHA256."""
    initial = row["browser_download_url"]
    require(
        row.get("name") in {PAYLOAD, PAYLOAD + ".sha256"}
        and type(row.get("size")) is int
        and 0 < row["size"] <= (4096 if row["name"].endswith(".sha256") else MAX_ARCHIVE)
        and isinstance(row.get("digest"), str)
        and re.fullmatch(r"sha256:[a-f0-9]{64}", row["digest"]),
        "Invalid download size/digest",
    )
    url = initial
    started = time.monotonic()
    for _ in range(5):
        download_url(url, initial)
        client.cookies.clear()
        with client.stream("GET", url) as response:
            if response.status_code in {301, 302, 303, 307, 308}:
                url = urljoin(url, response.headers.get("location", ""))
                require(time.monotonic() - started < 180, "Download deadline exceeded")
                continue
            require(response.status_code == 200, "Published asset download unavailable")
            measured, digest = 0, hashlib.sha256()
            with target.open("xb") as stream:
                for chunk in response.iter_raw(65536):
                    measured += len(chunk)
                    require(
                        measured <= row["size"] and time.monotonic() - started < 180,
                        "Download length/deadline exceeded",
                    )
                    stream.write(chunk)
                    digest.update(chunk)
            require(
                measured == row["size"] and "sha256:" + digest.hexdigest() == row["digest"],
                "Downloaded bytes fail provider digest",
            )
            return digest.hexdigest()
    raise ValueError("Download redirect budget exceeded")


def preflight_tar(stream) -> None:
    """Bound physical gzip expansion and tar extension sizes before tarfile interprets PAX/long names."""
    expanded, headers = 0, 0
    with gzip.GzipFile(fileobj=stream) as raw:
        while True:
            header = raw.read(512)
            expanded += len(header)
            require(expanded <= MAX_EXPANDED and len(header) == 512, "Truncated/oversize tar stream")
            if not any(header):
                require(raw.read(512) == bytes(512), "Tar end marker mismatch")
                expanded += 512
                require(expanded <= MAX_EXPANDED, "Archive expansion exceeded")
                while chunk := raw.read(65536):
                    expanded += len(chunk)
                    require(expanded <= MAX_EXPANDED and not any(chunk), "Tar trailer/expansion mismatch")
                return
            headers += 1
            require(headers <= 30000, "Tar member count exceeded")
            number = header[124:136].strip(b"\0 ") or b"0"
            require(re.fullmatch(rb"[0-7]{1,12}", number) is not None, "Unsupported tar size encoding")
            size = int(number, 8)
            kind = header[156:157]
            require(kind in {b"0", b"\0", b"5", b"x", b"g", b"L", b"K"}, "Unsupported archive member type")
            limit = 65536 if kind in {b"x", b"g", b"L", b"K"} else MAX_MEMBER
            require(size <= limit and (kind != b"5" or size == 0), "Tar member budget exceeded")
            remaining = ((size + 511) // 512) * 512
            while remaining:
                chunk = raw.read(min(65536, remaining))
                require(bool(chunk), "Truncated tar member")
                if kind in {b"x", b"g"}:
                    require(b"GNU.sparse" not in chunk, "Sparse archive metadata unsupported")
                remaining -= len(chunk)
                expanded += len(chunk)
                require(expanded <= MAX_EXPANDED, "Archive expansion exceeded")


def unpack(archive: Path, destination: Path) -> Path:
    """Extract only bounded regular files/directories into a fresh private tree; no links or devices."""
    destination.mkdir(mode=0o700)
    seen, expanded = set(), 0
    with archive.open("rb") as stream:
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "Archive must be a regular file")
        preflight_tar(stream)
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode="r:gz") as package:
            for index, member in enumerate(package):
                name = member.name.removeprefix("./")
                if name in {"", "."} and member.isdir():
                    continue
                parts = PurePosixPath(name).parts
                require(
                    index < 15000
                    and len(name) <= 512
                    and name not in seen
                    and not name.startswith("/")
                    and "\\" not in name
                    and ":" not in name
                    and not any(ord(c) < 32 for c in name)
                    and all(part not in {".", "..", ""} for part in name.split("/"))
                    and (member.isfile() or member.isdir())
                    and not member.linkname
                    and not any(key.startswith("GNU.sparse") for key in member.pax_headers),
                    "Unsafe or duplicate archive path/member",
                )
                seen.add(name)
                require(0 <= member.size <= MAX_MEMBER, "Archive member size exceeded")
                expanded += member.size
                require(expanded <= MAX_EXPANDED, "Archive extracted size exceeded")
                selected = destination.joinpath(*parts)
                if member.isdir():
                    selected.mkdir(parents=True, exist_ok=True, mode=0o700)
                    continue
                selected.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                source = package.extractfile(member)
                require(source is not None, "Missing archive file data")
                measured = 0
                with source, selected.open("xb") as output:
                    while chunk := source.read(65536):
                        measured += len(chunk)
                        require(measured <= member.size, "Archive actual-read size exceeded")
                        output.write(chunk)
                require(measured == member.size, "Archive file data truncated")
                selected.chmod(0o700 if member.mode & 0o111 else 0o600)
    resources = destination / "resources"
    metadata = resources / "metadata/source-release.json"
    require(metadata.is_file() and metadata.stat().st_size <= 4096, "Embedded release metadata missing")
    value = strict_json(metadata.read_bytes())
    require(
        isinstance(value, dict)
        and type(value.get("schema")) is int
        and type(value.get("source_dirty")) is bool
        and value
        == {
            "schema": 1,
            "product": "code-flow-studio",
            "version": VERSION,
            "source": SOURCE,
            "source_dirty": False,
            "worker_sha256": WORKER_SHA256,
        },
        "Embedded release provenance differs",
    )
    worker = resources / "runner/node_checks.cjs"
    require(worker.is_file() and worker.stat().st_size <= 1024 * 1024, "Embedded worker missing")
    require(
        hashlib.sha256(worker.read_bytes()).hexdigest() == WORKER_SHA256, "Embedded worker digest differs"
    )
    service = resources / "service/code-flow-service"
    require(service.is_file() and os.access(service, os.X_OK), "Frozen released service unavailable")
    return service


def service_environment(home: Path, token: str, nonce: str) -> dict:
    """Pass no provider/GitHub/cloud credentials to the frozen service or Docker CLI."""
    config = home / "docker-config"
    config.mkdir(mode=0o700)
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "TMPDIR": str(home),
        "LANG": "C.UTF-8",
        "DOCKER_CONFIG": str(config),
        "DOCKER_HOST": "unix:///var/run/docker.sock",
        "CFS_LAUNCH_TOKEN": token,
        "CFS_LAUNCH_NONCE": nonce,
        "CFS_PARENT_PID": str(os.getpid()),
        "CFS_PARENT_STARTED": str(psutil.Process().create_time()),
    }


def request_json(client: httpx.Client, method: str, path: str, data=None):
    """Use the owned loopback session only, with bounded no-redirect JSON responses."""
    require(
        path.startswith(("/private/", "/health", "/launcher/shutdown")) and ".." not in path,
        "Unexpected service route",
    )
    with client.stream(method, path, json=data) as response:
        require(response.status_code == 200, "Released service request failed")
        return strict_json(bounded_body(response, MAX_RESPONSE))


class Service:
    """Own one frozen service and nonce-bound listener, never adopt an existing server."""

    def __init__(self, executable: Path, data: Path, home: Path):
        self.token, self.nonce = secrets.token_hex(32), secrets.token_hex(32)
        home.mkdir(mode=0o700)
        self.log = home / "service-output.txt"
        with self.log.open("wb") as output:
            self.process = subprocess.Popen(  # noqa: S603 - digest-verified executable/fixed argv, hosted guard in main.
                [str(executable), "--no-browser", "--port", "0", "--data", str(data)],
                env=service_environment(home, self.token, self.nonce),
                stdout=output,
                stderr=subprocess.STDOUT,
            )
        self.client = None

    def ready(self):
        """Wait only after the caller has recorded ownership of this child process."""
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline and self.process.poll() is None:
            with self.log.open("rb") as source:
                body = source.read(65537)
            require(len(body) <= 65536, "Service startup output exceeded")
            matches = re.findall(rb"Code Flow Studio - Jason Stys: http://127\.0\.0\.1:([0-9]{1,5})/", body)
            if matches:
                require(len(matches) == 1 and 1024 <= int(matches[0]) <= 65535, "Ambiguous service readiness")
                origin = "http://127.0.0.1:" + matches[0].decode()
                candidate = httpx.Client(
                    base_url=origin,
                    trust_env=False,
                    follow_redirects=False,
                    timeout=15,
                    headers={"X-CFS-Request": "v1", "Content-Type": "application/json", "Origin": origin},
                )
                try:
                    health = request_json(candidate, "GET", "/health")
                    require(
                        health.get("launcher_nonce") == self.nonce
                        and health.get("version") == VERSION
                        and health.get("mode") == "private-local-accounts",
                        "Owned released service identity mismatch",
                    )
                except Exception:
                    candidate.close()
                    raise
                self.client = candidate
                return
            time.sleep(0.1)
        raise ValueError("Released service startup deadline/exit")

    def stop(self):
        """Request the shipping authenticated graceful shutdown and require actual owned process exit."""
        require(self.client is not None, "Owned service was not ready")
        self.client.headers["Authorization"] = "Bearer " + self.token
        require(
            request_json(self.client, "POST", "/launcher/shutdown", {}) == {"stopping": True},
            "Graceful shutdown unacknowledged",
        )
        self.process.wait(timeout=35)
        self.client.close()
        require(self.process.returncode == 0, "Released service exit failed")


def validate_export(exported: dict, result: dict, revision: dict) -> None:
    """Bind the shipping Store.timeline object to this exact saved project, revision and run."""
    require(
        isinstance(exported, dict)
        and {key: value for key, value in exported.items() if key != "iteration_history"} == result,
        "JSON export differs from actual run",
    )
    history = exported.get("iteration_history")
    require(
        isinstance(history, dict)
        and set(history) == {"project_id", "revisions", "truncated", "scope"}
        and isinstance(revision.get("project_id"), str)
        and history["project_id"] == revision["project_id"]
        and history["truncated"] is False
        and history["scope"]
        == "Latest 50 revisions; latest 10 attempts each. Full source/logs remain in their individual exports."
        and isinstance(history["revisions"], list)
        and len(history["revisions"]) == 1,
        "JSON export timeline schema/project differs",
    )
    snapshot = history["revisions"][0]
    require(
        isinstance(snapshot, dict)
        and snapshot.get("id") == revision["id"]
        and snapshot.get("parent_id") is None
        and snapshot.get("snapshot_sha256")
        == hashlib.sha256(json.dumps(revision["project"]).encode()).hexdigest()
        and snapshot.get("priorities") == revision["project"]["priorities"]
        and isinstance(snapshot.get("created"), str)
        and bool(snapshot["created"])
        and isinstance(snapshot.get("attempts"), list)
        and len(snapshot["attempts"]) == 1,
        "JSON export timeline revision differs",
    )
    attempt = snapshot["attempts"][0]
    actual = result["result"]
    require(
        isinstance(attempt, dict)
        and attempt.get("id") == result["id"]
        and attempt.get("status") == "completed"
        and isinstance(attempt.get("created"), str)
        and bool(attempt["created"])
        and attempt.get("checks") == {key: actual.get("checks", {}).get(key) for key in ("passed", "failed")}
        and attempt.get("benchmark") == actual.get("benchmark", {})
        and attempt.get("coverage") == actual.get("coverage", {})
        and attempt.get("mutation_score") == actual.get("mutation", {}).get("score")
        and attempt.get("fuzz_status") == actual.get("fuzz", {}).get("status")
        and attempt.get("generated_tests_exit") == actual.get("generated_tests", {}).get("exit_code"),
        "JSON export timeline attempt differs",
    )


def exercise(service: Service, data: Path, evidence: Evidence) -> dict:
    """Run real literal-oracle projects through HTTP, then save/seal before a full process restart."""
    require(set(LANGUAGES) == EXPECTED_LANGUAGES and len(LANGUAGES) == 12, "Language inventory changed")
    alias, password = "hosted_release042", secrets.token_urlsafe(30)
    key = {
        "key": base64.b64encode(secrets.token_bytes(32)).decode(),
        "salt": base64.b64encode(secrets.token_bytes(16)).decode(),
    }
    client = service.client
    request_json(client, "POST", "/private/register", {"alias": alias, "password": password})
    require(
        request_json(client, "POST", "/private/unlock", key).get("unlocked") is True, "Vault did not unlock"
    )
    stored = {}
    for language in LANGUAGES:
        evidence.stage("executing-" + language)
        project = practical_project(language)
        require(
            project.language == language and len(project.cases) >= 4, "Practical fixture lacks approved cases"
        )
        revision = request_json(client, "POST", "/private/api/revisions", project.model_dump())
        identifier = revision.get("id")
        require(
            isinstance(identifier, str) and re.fullmatch(r"[a-f0-9-]{36}", identifier),
            "Invalid revision identifier",
        )
        require(revision.get("project") == project.model_dump(), "Saved source/oracles differ")
        job = request_json(client, "POST", f"/private/api/revisions/{identifier}/run", {}).get("id")
        require(isinstance(job, str) and re.fullmatch(r"[a-f0-9-]{36}", job), "Invalid job identifier")
        deadline = time.monotonic() + 200
        while True:
            result = request_json(client, "GET", "/private/api/runs/" + job)
            if result.get("status") not in {"queued", "running"}:
                break
            require(time.monotonic() < deadline, "Released worker job deadline exceeded")
            time.sleep(0.25)
        require(result.get("status") == "completed", "Released worker did not complete")
        validate_positive(result.get("result", {}), project, historical_source=SOURCE)
        exported = request_json(client, "GET", f"/private/api/runs/{job}/report?format=json")
        require(
            result.get("id") == job and result.get("revision_id") == identifier,
            "Run/revision identity differs",
        )
        validate_export(exported, result, revision)
        digest = canonical_digest(result["result"])
        stored[language] = {
            "revision": identifier,
            "job": job,
            "digest": digest,
            "run_digest": canonical_digest(result),
            "export_digest": canonical_digest(exported),
        }
        evidence.record["languages"].append(
            {
                "language": language,
                "approved_cases": len(project.cases),
                "status": "passed",
                "result_sha256": digest,
            }
        )
        evidence.save()
    request_json(client, "POST", "/private/save", {})
    require(
        request_json(client, "POST", "/private/lock", {}) == {"locked": True}
        and not (data / "active").exists()
        and len(list((data / "encrypted").glob("*.cfsvault"))) == 1,
        "Vault sealing evidence incomplete",
    )
    return {"alias": alias, "password": password, "key": key, "stored": stored}


def restored(service: Service, data: Path, private: dict) -> None:
    """Require a new login/key and byte-identical durable reports after restarting the actual binary."""
    client = service.client
    request_json(
        client, "POST", "/private/login", {"alias": private["alias"], "password": private["password"]}
    )
    require(
        request_json(client, "POST", "/private/unlock", private["key"]).get("unlocked") is True,
        "Restarted vault did not unlock",
    )
    history = request_json(client, "GET", "/private/api/revisions")
    require(
        isinstance(history, list)
        and {row.get("id") for row in history} == {row["revision"] for row in private["stored"].values()},
        "Reopened revision history differs",
    )
    for row in private["stored"].values():
        result = request_json(client, "GET", "/private/api/runs/" + row["job"])
        exported = request_json(client, "GET", f"/private/api/runs/{row['job']}/report?format=json")
        require(
            result.get("status") == "completed"
            and canonical_digest(result.get("result")) == row["digest"]
            and canonical_digest(result) == row["run_digest"]
            and canonical_digest(exported) == row["export_digest"],
            "Reopened run or JSON export differs",
        )
    require(
        request_json(client, "POST", "/private/lock", {}) == {"locked": True}
        and not (data / "active").exists(),
        "Restarted vault failed to seal",
    )


def canonical_digest(value) -> str:
    """Bind every JSON result field without retaining its body in the public receipt."""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def cleanup_owned(services: list, temporary: Path) -> bool:
    """Stop only recorded children; retain private recovery data if a child cannot stop normally."""
    failed = False
    for service in services:
        if service.process.poll() is None:
            try:
                if service.client is not None:
                    service.stop()
                else:
                    # No account operation began; SIGTERM targets only this recorded hosted child.
                    service.process.terminate()
                    service.process.wait(timeout=10)
            except Exception:
                failed = True
    if all(service.process.poll() is not None for service in services):
        require(
            temporary.name.startswith("cfs-released042-") and not temporary.is_symlink(),
            "Invalid owned temporary directory",
        )
        shutil.rmtree(temporary)
    return not failed


def main():
    """Perform only this fixed hosted acceptance, retaining sanitized incremental failure evidence."""
    parser = argparse.ArgumentParser(
        description="Validate the actual published0.4.2 Linux service with hosted Docker"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = hosted_output(args.output)
    evidence = Evidence(output)
    temporary = Path(tempfile.mkdtemp(prefix="cfs-released042-", dir=os.environ.get("RUNNER_TEMP")))
    temporary.chmod(0o700)
    services = []
    try:
        with httpx.Client(trust_env=False, follow_redirects=False, timeout=30) as client:
            payload, sidecar = release_assets(
                api_json(client, "/releases/tags/v0.4.2"), api_json(client, "/git/ref/tags/v0.4.2")
            )
            evidence.stage("release-verified", release_id=RELEASE_ID)
            archive, checksum = temporary / PAYLOAD, temporary / (PAYLOAD + ".sha256")
            digest = download(client, payload, archive)
            download(client, sidecar, checksum)
            require(
                checksum.read_bytes() == f"{digest}  {PAYLOAD}\n".encode("ascii"),
                "Published checksum record differs",
            )
        evidence.stage("download-verified", payload_sha256=digest, payload_bytes=payload["size"])
        executable = unpack(archive, temporary / "package")
        evidence.stage("embedded-provenance-verified", worker_sha256=WORKER_SHA256)
        data = temporary / "accounts"
        evidence.stage("starting-released-service")
        first = Service(executable, data, temporary / "first-service")
        services.append(first)
        first.ready()
        private = exercise(first, data, evidence)
        first.stop()
        evidence.stage("first-service-sealed-and-exited")
        second = Service(executable, data, temporary / "second-service")
        services.append(second)
        second.ready()
        restored(second, data, private)
        second.stop()
        evidence.stage(
            "complete",
            status="passed",
            restored_reports=len(private["stored"]),
            approved_cases=sum(row["approved_cases"] for row in evidence.record["languages"]),
            scope="Published Linux service with a fresh source-bound0.4.2 hosted Docker worker; not a local PC compiler run or historical image-byte proof",
        )
    except Exception as error:
        evidence.stage(
            "failed", status="failed", failed_stage=evidence.record["stage"], error_type=type(error).__name__
        )
        raise SystemExit(
            "Published service acceptance failed; inspect the bounded sanitized receipt"
        ) from None
    finally:
        if not cleanup_owned(services, temporary):
            evidence.stage("cleanup-failed", status="failed", failed_stage=evidence.record["stage"])
            raise SystemExit(
                "Owned released service did not stop normally; private ephemeral recovery data was retained"
            )


if __name__ == "__main__":
    main()
