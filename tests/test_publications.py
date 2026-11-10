# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: BoundedInflater@L295
# functions: validate_publications(root)@L34; copy_publications(tmp_path)@L153; rewrite_package(root, filename, change)@L163; test_actual_reviewed_publications_are_bound_to_source_and_workflows()@L181; test_actual_binary_tamper_fails_digest(tmp_path)@L186; test_renamed_publication_cannot_select_an_external_path(tmp_path)@L195; test_rehashed_active_office_members_still_fail(tmp_path, member)@L210; test_rehashed_zip_without_document_root_fails(tmp_path)@L222; test_rehashed_workbook_missing_actual_filter_fails(tmp_path)@L230; remove_filter(entries)@L234; test_rehashed_workbook_changed_formula_fails(tmp_path)@L246; change_formula(entries)@L250; test_dishonest_compressed_xml_uses_bounded_actual_decompression(tmp_path, monkeypatch)@L263; __init__(self, actual)@L298; decompress(self, data, max_length)@L302; __getattr__(self, attribute)@L309; observed_factory(compression)@L313
# variables: FILES@L29; NS@L30; XML_BYTES@L31; reports@L36; manifest@L37; source@L38; records@L45; r@L46; workflows@L48; r@L49; r@L60; record@L63; stream@L66; payload@L67; package@L74; members@L75; m@L76; names@L76; required@L77; m@L85; xml@L87; member@L88; lower@L89; marker@L91; xml_stream@L101; xml_bytes@L102; text@L105; marker@L106; relation@L110; approval@L118; count@L119; n@L123; name@L127; node@L127; tables@L127; t@L131; cells@L134; node@L136; c@L137; n@L140; row@L141; expected@L142; actual@L148; c@L148; source@L155; target@L156; name@L158; path@L165; original@L166; entries@L167; m@L167; package@L169; content@L170; name@L170; manifest_path@L172; manifest@L173; r@L174; record@L174; payload@L175; root@L188; path@L189; root@L197; path@L198; record@L199; root@L212; root@L224; root@L232; n@L236; name@L236; table@L237; root@L248; name@L252; sheet@L253; formula@L254; root@L265; name@L266; path@L270; payload@L271; end@L272; cursor@L273; changed@L274; comment_size@L276; extra_size@L276; filename_size@L276; filename@L277; local@L279; changed@L283; cursor@L284; manifest_path@L287; manifest@L288; r@L289; record@L289; limits@L292; factory@L293; actual@L315
# parameters: root@L34; tmp_path@L153; change@L163; filename@L163; root@L163; tmp_path@L186; tmp_path@L195; member@L210; tmp_path@L210; entries@L216; tmp_path@L222; entries@L225; tmp_path@L230; entries@L234; tmp_path@L246; entries@L250; monkeypatch@L263; tmp_path@L263; entries@L268; actual@L298; self@L298; data@L302; max_length@L302; self@L302; attribute@L309; self@L309; compression@L313
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
import struct
import zipfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import pytest
from defusedxml import ElementTree as ET

FILES = {"project-guide.docx", "validation-review.docx", "validation-evidence.xlsx"}
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
XML_BYTES = 8 * 1024 * 1024


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
                    with package.open(member) as xml_stream:
                        xml_bytes = xml_stream.read(XML_BYTES + 1)
                    if len(xml_bytes) > XML_BYTES or len(xml_bytes) != member.file_size:
                        raise ValueError("Publication actual XML budget/length")
                    text = xml_bytes.decode("utf-8", errors="strict")
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


def test_dishonest_compressed_xml_uses_bounded_actual_decompression(tmp_path, monkeypatch):
    """A small real ZIP with understated sizes exercises actual zlib under an independent allocation-request budget."""
    root = copy_publications(tmp_path)
    name = "word/dishonest.xml"
    rewrite_package(
        root, "project-guide.docx", lambda entries: entries.update({name: b"<r>" + b"x" * 65536 + b"</r>"})
    )
    path = root / "docs" / "reports" / "project-guide.docx"
    payload = bytearray(path.read_bytes())
    end = payload.rfind(b"PK\x05\x06")
    cursor = struct.unpack_from("<I", payload, end + 16)[0]
    changed = False
    while payload[cursor : cursor + 4] == b"PK\x01\x02":
        filename_size, extra_size, comment_size = struct.unpack_from("<HHH", payload, cursor + 28)
        filename = payload[cursor + 46 : cursor + 46 + filename_size].decode("utf-8")
        if filename == name:
            local = struct.unpack_from("<I", payload, cursor + 42)[0]
            assert payload[local : local + 4] == b"PK\x03\x04"
            struct.pack_into("<I", payload, cursor + 24, 1)
            struct.pack_into("<I", payload, local + 22, 1)
            changed = True
        cursor += 46 + filename_size + extra_size + comment_size
    assert changed
    path.write_bytes(payload)
    manifest_path = path.parent / "publications.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = next(r for r in manifest["documents"] if r["filename"] == "project-guide.docx")
    record["bytes"], record["sha256"] = len(payload), hashlib.sha256(payload).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    limits = []
    factory = zipfile._get_decompressor

    class BoundedInflater:
        """Delegate actual native zlib while rejecting unbounded output requests before allocation."""

        def __init__(self, actual):
            """Retain the genuine stdlib decompressor; no substitute inflated payloads."""
            self.actual = actual

        def decompress(self, data, max_length=0):
            """Record and enforce output-request size independently of attacker-controlled ZIP metadata."""
            limits.append(max_length)
            if not 0 < max_length <= 8 * 1024 * 1024 + 1:
                raise AssertionError("Actual inflater output request must be explicitly bounded")
            return self.actual.decompress(data, max_length)

        def __getattr__(self, attribute):
            """Preserve genuine eof/tail/flush behavior instead of mocking ZIP acceptance."""
            return getattr(self.actual, attribute)

    def observed_factory(compression):
        """Instrument only construction; all compressed input is processed by the actual native decoder."""
        actual = factory(compression)
        return BoundedInflater(actual) if actual is not None else None

    monkeypatch.setattr(zipfile, "_get_decompressor", observed_factory)
    # CRC rejects the understated member, but that rejection alone would not establish a memory bound.
    with pytest.raises(zipfile.BadZipFile, match="CRC"):
        validate_publications(root)
    assert limits and max(limits) <= 8 * 1024 * 1024 + 1
