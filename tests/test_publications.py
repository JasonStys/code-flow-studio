# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: validate_publications(root)@L30; copy_publications(tmp_path)@L145; rewrite_package(root, filename, change)@L155; test_actual_reviewed_publications_are_bound_to_source_and_workflows()@L173; test_actual_binary_tamper_fails_digest(tmp_path)@L178; test_renamed_publication_cannot_select_an_external_path(tmp_path)@L187; test_rehashed_active_office_members_still_fail(tmp_path, member)@L202; test_rehashed_zip_without_document_root_fails(tmp_path)@L214; test_rehashed_workbook_missing_actual_filter_fails(tmp_path)@L222; remove_filter(entries)@L226; test_rehashed_workbook_changed_formula_fails(tmp_path)@L238; change_formula(entries)@L242
# variables: FILES@L26; NS@L27; reports@L32; manifest@L33; source@L34; records@L41; r@L42; workflows@L44; r@L45; r@L56; record@L59; stream@L62; payload@L63; package@L70; members@L71; m@L72; names@L72; required@L73; m@L81; xml@L83; member@L84; lower@L85; marker@L87; text@L97; marker@L98; relation@L102; approval@L110; count@L111; n@L115; name@L119; node@L119; tables@L119; t@L123; cells@L126; node@L128; c@L129; n@L132; row@L133; expected@L134; actual@L140; c@L140; source@L147; target@L148; name@L150; path@L157; original@L158; entries@L159; m@L159; package@L161; content@L162; name@L162; manifest_path@L164; manifest@L165; r@L166; record@L166; payload@L167; root@L180; path@L181; root@L189; path@L190; record@L191; root@L204; root@L216; root@L224; n@L228; name@L228; table@L229; root@L240; name@L244; sheet@L245; formula@L246
# parameters: root@L30; tmp_path@L145; change@L155; filename@L155; root@L155; tmp_path@L178; tmp_path@L187; member@L202; tmp_path@L202; entries@L208; tmp_path@L214; entries@L217; tmp_path@L222; entries@L226; tmp_path@L238; entries@L242
# </code-map>

"""Jason Stys: source-bound publication integrity with real Office tamper regressions.

Symbol locations: docs/code-index.md. These checks validate tracked documentation;
they do not run Office, reproduce visual review, authenticate authorship or read accounts.
"""

import hashlib
import io
import json
import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import pytest
from defusedxml import ElementTree as ET

FILES = {"project-guide.docx", "validation-review.docx", "validation-evidence.xlsx"}
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def validate_publications(root: Path) -> None:
    """Require exact reviewed bytes, immutable provenance and bounded inactive Office structures."""
    reports = root / "docs" / "reports"
    manifest = json.loads((reports / "publications.json").read_text(encoding="utf-8"))
    source = manifest["sourceBaseline"]
    if manifest["functionalEvidenceBaseline"] != source:
        raise ValueError("Publication functional source identity")
    if not re.fullmatch(r"[0-9a-f]{40}", source) or manifest["project"] != "code-flow-studio":
        raise ValueError("Publication source identity")
    if manifest["sourceUrl"] != "https://github.com/JasonStys/code-flow-studio/tree/" + source:
        raise ValueError("Publication source URL")
    records = manifest["documents"]
    if len(records) != 3 or {r["filename"] for r in records} != FILES:
        raise ValueError("Exact named publication set")
    workflows = manifest["workflowEvidence"]
    if {r["name"] for r in workflows} != {
        "Validate",
        "CodeQL",
        "Desktop packages",
    } or len(workflows) != 3:
        raise ValueError("Publication workflow set")
    if any(
        r["headSha"] != source
        or r["status"] != "completed"
        or r["conclusion"] != "success"
        or r["event"] != "push"
        for r in workflows
    ):
        raise ValueError("Publication workflow identity/outcome")
    for record in records:
        if record["sourceBaseline"] != source or record["visualReview"]["approved"] is not True:
            raise ValueError("Publication approval/source")
        with (reports / record["filename"]).open("rb") as stream:
            payload = stream.read(20 * 1024 * 1024 + 1)
        if (
            len(payload) > 20 * 1024 * 1024
            or len(payload) != record["bytes"]
            or hashlib.sha256(payload).hexdigest() != record["sha256"]
        ):
            raise ValueError("Publication digest/size")
        with ZipFile(io.BytesIO(payload)) as package:
            members = package.infolist()
            names = [m.filename for m in members]
            required = "xl/workbook.xml" if record["filename"].endswith(".xlsx") else "word/document.xml"
            if (
                len(members) > 256
                or len(names) != len(set(names))
                or required not in names
                or "[Content_Types].xml" not in names
            ):
                raise ValueError("Publication ZIP roots/identities")
            if sum(m.file_size for m in members) > 32 * 1024 * 1024:
                raise ValueError("Publication expanded budget")
            xml = {}
            for member in members:
                lower = "/" + member.filename.replace("\\", "/").lower()
                if any(
                    marker in lower for marker in ["/embeddings/", "/activex/", "vbaproject"]
                ) or ".." in member.filename.replace("\\", "/").split("/"):
                    raise ValueError("Active/embedded publication member")
                if (
                    member.file_size > 8 * 1024 * 1024
                    or member.flag_bits & 1
                    or member.compress_type not in {ZIP_STORED, ZIP_DEFLATED}
                ):
                    raise ValueError("Publication member budget/type")
                if member.filename.endswith((".xml", ".rels")):
                    text = package.read(member).decode("utf-8", errors="strict")
                    if any(marker in text.lower() for marker in ["<!doctype", "<!entity", "macroenabled"]):
                        raise ValueError("Active publication XML")
                    xml[member.filename] = ET.fromstring(text, forbid_dtd=True)
                    if member.filename.endswith(".rels"):
                        for relation in xml[member.filename]:
                            if relation.get("TargetMode") == "External" and not relation.get(
                                "Type", ""
                            ).endswith("/hyperlink"):
                                raise ValueError("External publication dependency")
            if package.testzip() is not None:
                raise ValueError("Publication CRC")
            if record["filename"].endswith(".docx"):
                approval = record["visualReview"]
                count = approval["pageCount"]
                if (
                    type(count) is not int
                    or count <= 0
                    or set(approval["renderedPageSha256"]) != {f"page-{n}.png" for n in range(1, count + 1)}
                ):
                    raise ValueError("Publication page approval")
            else:
                tables = [node for name, node in xml.items() if name.startswith("xl/tables/")]
                if len(tables) != 2 or any(
                    t.find("x:autoFilter", NS) is None
                    or t.find("x:autoFilter", NS).get("ref") != t.get("ref")
                    for t in tables
                ):
                    raise ValueError("Publication Excel Tables/filters")
                cells = [
                    c
                    for node in xml.values()
                    for c in node.findall(".//x:c", NS)
                    if c.find("x:f", NS) is not None
                ]
                n = len(workflows)
                row = 9 + n
                expected = [
                    (f"B{row}", f"COUNTA(A8:A{7 + n})", str(n)),
                    (f"B{row + 1}", f'COUNTIFS(B8:B{7 + n},"success")', str(n)),
                    (f"B{row + 2}", f'COUNTIFS(B8:B{7 + n},"failure")', "0"),
                    (f"B{row + 3}", f"B{row}-B{row + 1}-B{row + 2}", "0"),
                ]
                actual = [(c.get("r"), c.find("x:f", NS).text, c.find("x:v", NS).text) for c in cells]
                if actual != expected or record["visualReview"]["formulaCount"] != 4:
                    raise ValueError("Publication formula/cached outcome")


def copy_publications(tmp_path: Path) -> Path:
    """Copy only the four tracked documentation files into a disposable regression fixture."""
    source = Path(__file__).resolve().parents[1] / "docs" / "reports"
    target = tmp_path / "docs" / "reports"
    target.mkdir(parents=True)
    for name in FILES | {"publications.json"}:
        shutil.copyfile(source / name, target / name)
    return tmp_path


def rewrite_package(root: Path, filename: str, change) -> None:
    """Make a real changed ZIP and rebind its hash so structural checks, not the digest check, are exercised."""
    path = root / "docs" / "reports" / filename
    with ZipFile(path) as original:
        entries = {m.filename: original.read(m) for m in original.infolist()}
    change(entries)
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as package:
        for name, content in entries.items():
            package.writestr(name, content)
    manifest_path = path.parent / "publications.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = next(r for r in manifest["documents"] if r["filename"] == filename)
    payload = path.read_bytes()
    record["bytes"] = len(payload)
    record["sha256"] = hashlib.sha256(payload).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_actual_reviewed_publications_are_bound_to_source_and_workflows():
    """Exercise actual tracked editions, not generated replicas or approval flags alone."""
    validate_publications(Path(__file__).resolve().parents[1])


def test_actual_binary_tamper_fails_digest(tmp_path):
    """A changed document cannot keep the original reviewed byte identity."""
    root = copy_publications(tmp_path)
    path = root / "docs" / "reports" / "project-guide.docx"
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="digest/size"):
        validate_publications(root)


def test_renamed_publication_cannot_select_an_external_path(tmp_path):
    """Manifest names are closed before any document is opened."""
    root = copy_publications(tmp_path)
    path = root / "docs" / "reports" / "publications.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record["documents"][0]["filename"] = "../external.docx"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="named publication set"):
        validate_publications(root)


@pytest.mark.parametrize(
    "member",
    ["word/embeddings/example.bin", "word/activeX/example.xml", "word/vbaProject.bin"],
)
def test_rehashed_active_office_members_still_fail(tmp_path, member):
    """A new digest never authorizes opaque embedded objects, ActiveX or macro members."""
    root = copy_publications(tmp_path)
    rewrite_package(
        root,
        "project-guide.docx",
        lambda entries: entries.update({member: b"synthetic fixture"}),
    )
    with pytest.raises(ValueError, match="Active/embedded"):
        validate_publications(root)


def test_rehashed_zip_without_document_root_fails(tmp_path):
    """A valid ZIP and matching hash do not make a Word document."""
    root = copy_publications(tmp_path)
    rewrite_package(root, "project-guide.docx", lambda entries: entries.pop("word/document.xml"))
    with pytest.raises(ValueError, match="ZIP roots"):
        validate_publications(root)


def test_rehashed_workbook_missing_actual_filter_fails(tmp_path):
    """Inspect actual exported Table XML; an approval field cannot replace an autoFilter."""
    root = copy_publications(tmp_path)

    def remove_filter(entries):
        """Remove the real first Table filter while leaving the rest of the actual workbook intact."""
        name = next(n for n in entries if n.startswith("xl/tables/"))
        table = ET.fromstring(entries[name])
        table.remove(table.find("x:autoFilter", NS))
        entries[name] = ET.tostring(table)

    rewrite_package(root, "validation-evidence.xlsx", remove_filter)
    with pytest.raises(ValueError, match="Tables/filters"):
        validate_publications(root)


def test_rehashed_workbook_changed_formula_fails(tmp_path):
    """A real changed formula is rejected even when its old cached value and new archive digest agree."""
    root = copy_publications(tmp_path)

    def change_formula(entries):
        """Change actual exported XML rather than mocking a formula parser."""
        name = "xl/worksheets/sheet1.xml"
        sheet = ET.fromstring(entries[name])
        formula = sheet.find(".//x:f", NS)
        formula.text = "SUM(A8:A10)"
        entries[name] = ET.tostring(sheet)

    rewrite_package(root, "validation-evidence.xlsx", change_formula)
    with pytest.raises(ValueError, match="formula/cached"):
        validate_publications(root)
