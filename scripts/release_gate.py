# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: strict_object(source)@L43; pairs(items)@L46; invalid_constant(value)@L52; valid_metadata(value)@L61; command(arguments, data, missing)@L88; api(endpoint, body)@L121; no_tag(tag)@L130; product_version()@L142; metadata()@L171; workflow_policy(text)@L185; context()@L244; complete_list(endpoint)@L260; require_source(value)@L272; draft(identifier, value)@L324; names(version, system)@L338; attached(record, version, complete)@L349; archive_metadata(file, system)@L379; upload_bytes(identifier, file, name, expected_digest)@L426; upload(value, identifier)@L478; main()@L536
# variables: ROOT@L35; REPOSITORY@L36; BASE@L37; WORKFLOWS@L38; CATEGORIES@L39; MAX_ASSET@L40; result@L48; value@L56; executable@L101; result@L104; arguments@L124; arguments@L126; version@L144; name@L150; value@L156; assignments@L160; runtime@L161; node@L163; t@L165; source@L173; operation@L196; verifier@L209; fields@L210; line@L211; field@L214; permissions@L221; scopes@L222; line@L224; scope@L227; _@L232; name@L232; value@L246; rows@L262; page@L263; current@L264; source@L274; workflow@L276; envelope@L277; rows@L278; row@L283; row@L293; analyses@L296; current@L297; row@L297; row@L299; row@L302; record@L326; values@L340; name@L346; payload@L346; expected@L351; name@L352; system@L352; result@L354; identifiers@L355; row@L356; name@L357; prefix@L385; expected@L386; found@L387; archive@L389; member@L392; member@L395; archive@L406; expanded@L407; index@L408; member@L408; expanded@L410; name@L412; stream@L418; value@L421; token@L428; connection@L430; started@L431; stream@L433; size@L434; key@L439; value@L439; remaining@L449; uploaded_digest@L450; block@L453; remaining@L457; response@L462; content@L464; result@L466; system@L480; name@L481; paths@L481; receipt@L482; archive@L496; archive_value@L497; worker@L497; payload@L502; sidecar@L502; stream@L511; digest@L512; existing@L517; file@L519; file@L522; current@L523; name@L524; stream@L526; digest@L527; observed@L529; parser@L538; operation@L540; target@L542; value@L546; tag@L549; created@L554; record@L565; output@L567; raw@L570; identifier@L572; record@L577
# parameters: source@L43; items@L46; value@L52; value@L61; arguments@L88; data@L88; missing@L88; body@L121; endpoint@L121; tag@L130; text@L185; endpoint@L260; value@L272; identifier@L324; value@L324; system@L338; version@L338; complete@L349; record@L349; version@L349; file@L379; system@L379; expected_digest@L426; file@L426; identifier@L426; name@L426; identifier@L478; value@L478
# </code-map>

"""Jason Stys: exact-main CodeQL-gated, numeric-ID-bound draft preparation and uploads.

The workflow never publishes. The release owner's final download/installer verification is
separate. Read operations fail closed; binary uploads use a fixed HTTPS host and
numeric release ID, never a provider-selected URL or clobber operation.
"""

import argparse
import ast
import hashlib
import http.client
import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
import time
import tomllib
import urllib.parse
import zipfile
from pathlib import Path

from scripts.draft_lookup import find_release, read_by_id, require

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "JasonStys/code-flow-studio"
BASE = f"repos/{REPOSITORY}"
WORKFLOWS = ("validate.yml", "packages.yml", "codeql.yml", "compiler-execution.yml")
CATEGORIES = {"/language:python", "/language:javascript-typescript", "/language:actions"}
MAX_ASSET = 1024**3


def strict_object(source: str | bytes) -> dict:
    """Reject duplicate metadata fields and nonfinite values before identity comparisons."""

    def pairs(items):
        """A duplicate key cannot replace a checked source/version field."""
        result = dict(items)
        require(len(result) == len(items), "Duplicate metadata field")
        return result

    def invalid_constant(value):
        """Nonfinite metadata is never a valid provenance value."""
        raise ValueError("Nonfinite metadata")

    value = json.loads(source, object_pairs_hook=pairs, parse_constant=invalid_constant)
    require(isinstance(value, dict), "Metadata object required")
    return value


def valid_metadata(value: dict) -> None:
    """Require strict closed identity types; booleans cannot stand in for a schema integer."""
    require(
        set(value) == {"schema", "product", "version", "source", "source_dirty", "worker_sha256"},
        "Unexpected package metadata fields",
    )
    require(
        type(value["schema"]) is int
        and value["schema"] == 1
        and value["product"] == "code-flow-studio"
        and type(value["source_dirty"]) is bool,
        "Invalid package metadata types",
    )
    require(
        isinstance(value["source"], str)
        and re.fullmatch(r"[a-f0-9]{40}", value["source"]) is not None
        and isinstance(value["worker_sha256"], str)
        and re.fullmatch(r"[a-f0-9]{64}", value["worker_sha256"]) is not None,
        "Invalid package identity hashes",
    )
    require(
        isinstance(value["version"], str)
        and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value["version"]) is not None,
        "Invalid package version",
    )


def command(arguments: list[str], *, data: str | None = None, missing: bool = False) -> str | None:
    """Run only fixed git/gh commands; never disclose authentication environment or server error bodies."""
    require(
        arguments in (["git", "rev-parse", "HEAD"], ["git", "status", "--porcelain"])
        or len(arguments) >= 3
        and arguments[:2] == ["gh", "api"]
        and arguments[2].startswith(BASE + "/")
        and (
            len(arguments) == 3
            or arguments == ["gh", "api", BASE + "/releases", "--method", "POST", "--input", "-"]
        ),
        "Only fixed repository git/gh commands are permitted",
    )
    executable = shutil.which(arguments[0])
    require(executable is not None and Path(executable).is_absolute(), "Trusted installed CLI unavailable")
    # Executable and argument domain are explicitly allowlisted above; no shell or caller-provided command.
    result = subprocess.run(  # noqa: S603
        [executable, *arguments[1:]],
        cwd=ROOT,
        input=data,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    if result.returncode:
        if missing and arguments[2].startswith(BASE + "/git/ref/tags/") and "(HTTP 404)" in result.stderr:
            return None
        raise RuntimeError("Release metadata command failed; no further mutation authorized")
    require(len(result.stdout) <= 16 * 1024 * 1024, "Metadata response exceeds limit")
    return result.stdout


def api(endpoint: str, *, body: dict | None = None):
    """Read fixed same-repository metadata, or create a draft with an explicit structured body."""
    require(endpoint.startswith(BASE + "/"), "Foreign API endpoint")
    arguments = ["gh", "api", endpoint]
    if body is not None:
        arguments += ["--method", "POST", "--input", "-"]
    return json.loads(command(arguments, data=json.dumps(body) if body is not None else None))


def no_tag(tag: str) -> None:
    """Only an actual404 proves a tag absent; no authentication or transport fallback permits mutation."""
    require(
        re.fullmatch(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", tag) is not None,
        "Invalid tag identity",
    )
    require(
        command(["gh", "api", f"{BASE}/git/ref/tags/{tag}"], missing=True) is None,
        "Version tag exists or absence is unknown",
    )


def product_version() -> str:
    """Require coherent data-only runtime/product/worker metadata without importing the service."""
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    require(
        isinstance(version, str)
        and re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version) is not None,
        "Invalid version",
    )
    for name in (
        "package.json",
        "package-lock.json",
        "runner/tools/package.json",
        "runner/tools/package-lock.json",
    ):
        value = json.loads((ROOT / name).read_text(encoding="utf-8"))
        require(value.get("version") == version, "Product/worker metadata mismatch")
        if "packages" in value:
            require(value["packages"][""].get("version") == version, "Lock root version mismatch")
    assignments = ast.parse((ROOT / "studio/__init__.py").read_text(encoding="utf-8")).body
    runtime = [
        ast.literal_eval(node.value)
        for node in assignments
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets)
    ]
    require(runtime == [version], "Runtime version mismatch")
    return version


def metadata() -> dict:
    """Bind package metadata to current checkout bytes; local dirty builds cannot authorize release."""
    source = command(["git", "rev-parse", "HEAD"]).strip()
    require(re.fullmatch("[a-f0-9]{40}", source) is not None, "Exact source SHA required")
    return {
        "schema": 1,
        "product": "code-flow-studio",
        "version": product_version(),
        "source": source,
        "source_dirty": bool(command(["git", "status", "--porcelain"]).strip()),
        "worker_sha256": hashlib.sha256((ROOT / "runner/node_checks.cjs").read_bytes()).hexdigest(),
    }


def workflow_policy(text: str) -> None:
    """Check the actual narrowly specified workflow before release; tests mutate each critical policy."""
    require(
        "pull_request_target:" not in text and "--clobber" not in text and "--draft=false" not in text,
        "Privileged trigger, overwrite or publication forbidden",
    )
    require(
        re.findall(r"^  ([a-z][a-z_-]*):\s*$", text, re.MULTILINE)
        == ["workflow_dispatch", "prepare", "build", "verify-draft"],
        "Manual-only draft workflow/job policy changed",
    )
    for operation in ("prepare", "upload", "verify"):
        require(f"python -m scripts.release_gate {operation}" in text, "Required release guard missing")
    require(
        text.count("security-events: read") == 2 and "security-events: write" not in text,
        "CodeQL read scope must remain gate-only",
    )
    require(
        text.count("ref: ${{ github.sha }}") == 3
        and text.count("if: github.ref == 'refs/heads/main'") == 3
        and "EXPECTED_RELEASE_ID: ${{ needs.prepare.outputs.release_id }}" in text,
        "Build source/prepared release binding missing",
    )
    require("max-parallel: 1" in text, "Release build/uploads must be serialized")
    verifier = text.split("\n  verify-draft:", 1)[1]
    fields = []
    for line in verifier.splitlines():
        if not re.match(r"^    [^ \t#]", line):
            continue
        field = re.match(r"^    ([a-z][a-z_-]*):(?:[ \t]|$)", line)
        require(field is not None, "Unparsed final verification job field")
        fields.append(field[1])
    require(
        fields == ["if", "needs", "runs-on", "timeout-minutes", "permissions", "steps"],
        "Duplicate or unknown final verification job field",
    )
    permissions = re.search(r"(?ms)^    permissions:\n(.*?)(?=^    [a-z][a-z_-]*:|\Z)", verifier)
    scopes = []
    require(permissions is not None, "Explicit draft verification permissions required")
    for line in permissions[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        scope = re.fullmatch(r"      ([a-z-]+): (read|write|none)(?:[ \t]+#[^\r\n]*)?[ \t]*", line)
        require(scope is not None, "Unparsed draft verification permission line")
        scopes.append(scope.groups())
    require(
        len(scopes) == 3
        and len({name for name, _ in scopes}) == len(scopes)
        and dict(scopes) == {"contents": "write", "actions": "read", "security-events": "read"},
        "Draft verification needs push-capable contents visibility and only read actions/security scopes",
    )
    require(
        "STUDIO_INSTALLED_APP" in text
        and "npm run test:desktop" in text
        and "python scripts/release_archive.py" in text,
        "Actual compiled package acceptance missing",
    )


def context() -> dict:
    """Require the selected trusted main checkout and unchanged actual workflow before network writes."""
    value = metadata()
    require(
        os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("GITHUB_REF") == "refs/heads/main"
        and os.environ.get("GITHUB_REPOSITORY") == REPOSITORY
        and os.environ.get("GITHUB_SHA") == value["source"]
        and os.environ.get("EXPECTED_SOURCE") == value["source"]
        and value["source_dirty"] is False,
        "Release requires a clean exact trusted-main workflow checkout",
    )
    workflow_policy((ROOT / ".github/workflows/release-native.yml").read_text(encoding="utf-8"))
    return value


def complete_list(endpoint: str) -> list:
    """Bound complete authenticated metadata pages; a full cap is unknown, never an empty result."""
    rows = []
    for page in range(1, 4):
        current = api(endpoint + f"&per_page=100&page={page}")
        require(isinstance(current, list) and len(current) <= 100, "Malformed metadata page")
        rows.extend(current)
        if len(current) < 100:
            return rows
    raise ValueError("Metadata history exceeds complete review bound")


def require_source(value: dict) -> None:
    """Bind complete successful main-push lanes, processed full-main categories and zero open main alerts."""
    source = value["source"]
    require(api(BASE + "/git/ref/heads/main")["object"]["sha"] == source, "Main moved; revalidate source")
    for workflow in WORKFLOWS:
        envelope = api(f"{BASE}/actions/workflows/{workflow}/runs?head_sha={source}&per_page=100")
        rows = envelope.get("workflow_runs")
        require(
            isinstance(rows, list) and 0 < len(rows) < 100 and envelope.get("total_count") == len(rows),
            "Missing/incomplete workflow history",
        )
        for row in rows:
            require(
                row.get("head_sha") == source
                and row.get("status") == "completed"
                and row.get("conclusion") == "success"
                and row.get("path") == f".github/workflows/{workflow}"
                and row.get("repository", {}).get("full_name") == REPOSITORY,
                "Source workflow is not complete successful exact source",
            )
        require(
            sum(row.get("event") == "push" and row.get("head_branch") == "main" for row in rows) == 1,
            "Exactly one successful main push per lane required",
        )
    analyses = complete_list(BASE + "/code-scanning/analyses?ref=refs%2Fheads%2Fmain")
    current = [row for row in analyses if row.get("commit_sha") == source]
    require(
        len(current) == 3 and {row.get("category") for row in current} == CATEGORIES,
        "All three current processed full-main CodeQL categories required",
    )
    for row in current:
        require(
            row.get("ref") == "refs/heads/main"
            and row.get("analysis_key") == ".github/workflows/codeql.yml:analyze"
            and row.get("tool", {}).get("name") == "CodeQL"
            and row.get("error") == ""
            and row.get("warning") == "",
            "Incomplete or differently sourced CodeQL analysis",
        )
        require(
            type(row.get("id")) is int
            and row["id"] > 0
            and type(row.get("rules_count")) is int
            and row["rules_count"] > 0,
            "A processed CodeQL analysis must identify actual executed rules",
        )
    require(
        not complete_list(BASE + "/code-scanning/alerts?ref=refs%2Fheads%2Fmain&state=open"),
        "Open main CodeQL alerts require review/correction",
    )


def draft(identifier: int, value: dict) -> dict:
    """Reread the prepared numeric ID; public, swapped, retargeted or tagged releases cannot accept bytes."""
    record = read_by_id(api, REPOSITORY, identifier)
    require(
        record["tag_name"] == "v" + value["version"]
        and record["target_commitish"] == value["source"]
        and record["draft"] is True
        and record["prerelease"] is False,
        "Prepared draft identity/state/source changed",
    )
    no_tag(record["tag_name"])
    return record


def names(version: str, system: str) -> list[str]:
    """Preserve the existing two payloads plus two sidecars per platform; no unrelated files are uploaded."""
    values = {
        "Windows": [f"Code Flow Studio Setup {version}.exe", f"CodeFlowStudio-{version}-windows-x64.zip"],
        "Linux": [f"Code Flow Studio-{version}.AppImage", f"CodeFlowStudio-{version}-linux-x64.tar.gz"],
        "macOS": [f"Code Flow Studio-{version}-arm64.dmg", f"CodeFlowStudio-{version}-macos-arm64.tar.gz"],
    }
    require(system in values, "Unsupported release platform")
    return [name for payload in values[system] for name in (payload, payload + ".sha256")]


def attached(record: dict, version: str, *, complete: bool = False) -> dict:
    """Require documented names, unique numeric IDs and provider digests; never accept duplicate/colliding assets."""
    expected = {
        name.replace(" ", ".") for system in ("Windows", "Linux", "macOS") for name in names(version, system)
    }
    result = {}
    identifiers = set()
    for row in record["assets"]:
        name = row.get("name")
        require(
            name in expected
            and name not in result
            and type(row.get("id")) is int
            and row["id"] > 0
            and row["id"] not in identifiers,
            "Unexpected, duplicate or malformed release asset",
        )
        require(
            type(row.get("size")) is int
            and 0 < row["size"] <= MAX_ASSET
            and row.get("state") == "uploaded"
            and re.fullmatch(r"sha256:[a-f0-9]{64}", row.get("digest", "")) is not None,
            "Invalid uploaded asset state/size/digest",
        )
        result[name] = row
        identifiers.add(row["id"])
    require(not complete or set(result) == expected, "All three platforms' twelve assets are required")
    return result


def archive_metadata(file: Path, system: str) -> tuple[dict, str]:
    """Read bounded regular metadata/worker members without extracting paths or following archive links."""
    require(
        file.is_file() and not file.is_symlink() and 0 < file.stat().st_size <= MAX_ASSET,
        "Invalid archive file/size",
    )
    prefix = "Code Flow Studio.app/Contents/Resources/" if system == "macOS" else "resources/"
    expected = {prefix + "metadata/source-release.json", prefix + "runner/node_checks.cjs"}
    found = {}
    if system == "Windows":
        with zipfile.ZipFile(file) as archive:
            require(len(archive.infolist()) < 100_000, "Archive entry limit exceeded")
            require(
                sum(member.file_size for member in archive.infolist()) <= 5 * MAX_ASSET,
                "Expanded archive size limit exceeded",
            )
            for member in archive.infolist():
                if member.filename in expected:
                    require(
                        member.filename not in found
                        and 0 < member.file_size <= 1024 * 1024
                        and stat.S_IFMT(member.external_attr >> 16) in {0, stat.S_IFREG}
                        and not member.flag_bits & 1,
                        "Unsafe duplicate/nonregular metadata member",
                    )
                    found[member.filename] = archive.read(member)
    else:
        with tarfile.open(file, "r:gz") as archive:
            expanded = 0
            for index, member in enumerate(archive):
                require(index < 100_000, "Archive entry limit exceeded")
                expanded += member.size
                require(expanded <= 5 * MAX_ASSET, "Expanded archive size limit exceeded")
                name = member.name.removeprefix("./")
                if name in expected:
                    require(
                        name not in found and member.isfile() and 0 < member.size <= 1024 * 1024,
                        "Unsafe duplicate/nonregular metadata member",
                    )
                    with archive.extractfile(member) as stream:
                        found[name] = stream.read(1024 * 1024 + 1)
    require(set(found) == expected, "Archive lacks exact package-source/worker provenance")
    value = strict_object(found[prefix + "metadata/source-release.json"])
    valid_metadata(value)
    return value, hashlib.sha256(found[prefix + "runner/node_checks.cjs"]).hexdigest()


def upload_bytes(identifier: int, file: Path, name: str, expected_digest: str) -> dict:
    """Stream one bounded asset to the fixed HTTPS numeric-ID upload endpoint; no redirects or retries."""
    token = os.environ.get("GH_TOKEN")
    require(bool(token), "Missing release transport credential")
    connection = http.client.HTTPSConnection("uploads.github.com", timeout=30)
    started = time.monotonic()
    try:
        with file.open("rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            require(0 < size <= MAX_ASSET, "Asset exceeds upload budget")
            connection.putrequest(
                "POST", f"/{BASE}/releases/{identifier}/assets?name={urllib.parse.quote(name, safe='')}"
            )
            for key, value in {
                "Authorization": "Bearer " + token,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/octet-stream",
                "Content-Length": str(size),
                "User-Agent": "CodeFlowStudio-reviewed-draft-uploader",
                "X-GitHub-Api-Version": "2022-11-28",
            }.items():
                connection.putheader(key, value)
            connection.endheaders()
            remaining = size
            uploaded_digest = hashlib.sha256()
            while remaining:
                require(time.monotonic() - started < 180, "Upload deadline exceeded")
                block = stream.read(min(1024 * 1024, remaining))
                require(bool(block), "Asset shrank during upload")
                connection.send(block)
                uploaded_digest.update(block)
                remaining -= len(block)
            require(
                not stream.read(1) and uploaded_digest.hexdigest() == expected_digest,
                "Asset changed during upload",
            )
            response = connection.getresponse()
            require(response.status == 201, "Asset upload failed; draft preserved for review")
            content = response.read(65537)
            require(len(content) <= 65536, "Upload metadata exceeds limit")
            result = json.loads(content)
            require(
                result.get("name") == name
                and result.get("size") == size
                and result.get("digest") == "sha256:" + expected_digest,
                "Uploaded bytes differ from accepted payload",
            )
            return result
    finally:
        connection.close()


def upload(value: dict, identifier: int) -> None:
    """Require a real compiled-native receipt and archive source bytes before immutable draft uploads."""
    system = os.environ.get("RUNNER_OS", "")
    paths = [ROOT / "release/installers" / name for name in names(value["version"], system)]
    receipt = strict_object((ROOT / "artifacts/native-resource-acceptance.json").read_text(encoding="utf-8"))
    require(type(receipt.get("schema")) is int, "Invalid receipt schema type")
    require(
        receipt
        == {
            "schema": 1,
            "version": value["version"],
            "source": value["source"],
            "worker_sha256": value["worker_sha256"],
            "compiled_app": True,
            "journey": "passed",
        },
        "Actual compiled native/source-resource acceptance required",
    )
    archive = paths[2]
    archive_value, worker = archive_metadata(archive, system)
    require(
        archive_value == value and worker == value["worker_sha256"],
        "Archive source/worker bytes do not match this accepted checkout",
    )
    for payload, sidecar in zip(paths[::2], paths[1::2], strict=True):
        require(
            payload.is_file() and not payload.is_symlink() and sidecar.is_file() and not sidecar.is_symlink(),
            "Regular local assets required",
        )
        require(
            0 < payload.stat().st_size <= MAX_ASSET and 0 < sidecar.stat().st_size <= 4096,
            "Asset/sidecar size outside budget",
        )
        with payload.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        require(
            sidecar.read_text(encoding="ascii") == f"{digest}  {payload.name.replace(' ', '.')}\n",
            "Checksum sidecar differs from payload",
        )
    existing = attached(draft(identifier, value), value["version"])
    require(
        not {file.name.replace(" ", ".") for file in paths} & set(existing),
        "Asset collision; overwrite forbidden",
    )
    for file in paths:
        current = attached(draft(identifier, value), value["version"])
        name = file.name.replace(" ", ".")
        require(name not in current, "Asset appeared; overwrite forbidden")
        with file.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        upload_bytes(identifier, file, name, digest)
        observed = attached(draft(identifier, value), value["version"])[name]
        require(
            observed["size"] == file.stat().st_size and observed["digest"] == "sha256:" + digest,
            "Published provider asset differs from accepted bytes",
        )


def main() -> None:
    """Prepare, upload or verify a draft; no publish/delete/force operation exists."""
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("metadata", "prepare", "upload", "verify"))
    operation = parser.parse_args().operation
    if operation == "metadata":
        target = ROOT / "release/metadata/source-release.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(metadata(), indent=2) + "\n", encoding="utf-8")
        return
    value = context()
    if operation == "prepare":
        require_source(value)
        tag = "v" + value["version"]
        no_tag(tag)
        require(
            find_release(api, REPOSITORY, tag, missing=True) is None, "Version already has a release/draft"
        )
        created = api(
            BASE + "/releases",
            body={
                "tag_name": tag,
                "target_commitish": value["source"],
                "draft": True,
                "prerelease": False,
                "name": "Code Flow Studio " + value["version"],
                "body": (ROOT / f"docs/releases/{tag}.md").read_text(encoding="utf-8"),
            },
        )
        record = draft(created["id"], value)
        require(not record["assets"], "Fresh draft unexpectedly has assets")
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"sha={value['source']}\ntag={tag}\nrelease_id={record['id']}\n")
        return
    raw = os.environ.get("EXPECTED_RELEASE_ID", "")
    require(re.fullmatch(r"[1-9][0-9]{0,18}", raw) is not None, "Prepared numeric release ID required")
    identifier = int(raw)
    if operation == "upload":
        upload(value, identifier)
    else:
        require_source(value)
        record = draft(identifier, value)
        attached(record, value["version"], complete=True)
        print(
            json.dumps(
                {
                    "release_id": identifier,
                    "source": value["source"],
                    "version": value["version"],
                    "assets": 12,
                    "draft": True,
                    "publication": "pending independent downloaded Windows installer acceptance",
                }
            )
        )


if __name__ == "__main__":
    main()
