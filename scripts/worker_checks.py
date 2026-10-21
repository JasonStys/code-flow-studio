# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Evidence@L26
# functions: __setitem__(self, key, value)@L29; main()@L39; assert_native_locations(language, result, project, unused_line, missing_line)@L82; original_scenarios(reports)@L96
# variables: path@L32; temporary@L34; reports@L41; language@L42; result@L43; acceptance@L47; native_errors@L48; language@L49; missing_line@L50; project@L50; unused_line@L50; result@L51; key@L58; item@L88; measured_file@L91; python@L98; bad@L112; invalid@L116; item@L121; attack@L123; code@L134; name@L134; target@L135; cpp@L139; web_demo@L178; located@L184; measured@L201; item@L208; crashing@L210; item@L227; mapped@L229; item@L246; item@L256
# parameters: key@L29; self@L29; value@L29; language@L82; missing_line@L82; project@L82; result@L82; unused_line@L82; reports@L96
# </code-map>

"""Real compiler, generated-test, fuzz and adversarial-container integration checks.

Symbol and variable locations: docs/code-index.md. Requires the trusted worker
image. Failure evidence is exported even when a target intentionally fails.
"""

import asyncio
import json
from pathlib import Path

from examples.language_locations import SAMPLES, location_fixture
from examples.projects import fixture
from studio.execution import run
from studio.models import LANGUAGES, Project


class Evidence(dict):
    """Persist each completed scenario before assertions so failed CI retains diagnostics."""

    def __setitem__(self, key, value):
        """Record a bounded worker result and atomically replace this job's evidence file."""
        super().__setitem__(key, value)
        path = Path("artifacts/worker-evidence.json")
        path.parent.mkdir(exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self, indent=2), encoding="utf-8")
        temporary.replace(path)


async def main():
    """Exercise each adapter and verify failures, output limits, isolation and instrumentation."""
    reports = Evidence()
    for language in LANGUAGES:
        result = await run(fixture(language))
        reports[language] = result
        assert result["tool_status"] == "completed", (language, result)
        assert result["checks"]["passed"] == 1 and result["checks"]["failed"] == 0, (language, result)
    acceptance = {}
    native_errors = []
    for language in SAMPLES:
        project, unused_line, missing_line = location_fixture(language)
        result = await run(project)
        reports[f"{language}-locations"] = result
        print(
            "NATIVE_RESULT="
            + json.dumps(
                {
                    language: {
                        key: result.get(key) for key in ("tool_status", "coverage", "unused", "diagnostics")
                    }
                }
            ),
            flush=True,
        )
        try:
            assert_native_locations(language, result, project, unused_line, missing_line)
        except (AssertionError, KeyError):
            native_errors.append(language)
            continue
        acceptance[language] = {
            "entry": project.entry,
            "unused_line": unused_line,
            "missing_line": missing_line,
            "coverage": result["coverage"],
            "unused": result["unused"]["findings"],
        }
        print("NATIVE_ACCEPTANCE=" + json.dumps({language: acceptance[language]}), flush=True)
    assert not native_errors, ("Native location contract failures", native_errors)

    await original_scenarios(reports)


def assert_native_locations(language, result, project, unused_line, missing_line):
    """Require independently authored exact anchors; no missing tool or empty report counts as a pass."""
    assert result["tool_status"] == "completed" and result["checks"]["passed"] == 1, (language, result)
    assert result["unused"]["status"] == "completed", (language, result)
    assert any(
        item["file"] == project.entry and item["line"] == unused_line and item["stage"] == "unused-code"
        for item in result["diagnostics"]
    ), (language, unused_line, result)
    assert result["coverage"]["status"] == "measured", (language, result)
    measured_file = result["coverage"]["files"][project.entry]
    assert missing_line in measured_file["missing_lines"], (language, missing_line, result)
    assert measured_file["executed_lines"] and measured_file["source_sha256"], (language, result)


async def original_scenarios(reports):
    """Retain Python, fuzz, generated-test, source-map and sandbox acceptance without weakening prior gates."""
    python = fixture("python").model_dump()
    python.update(
        {
            "tests": "def test_generated():\n    import subprocess\n    assert subprocess.run(['python','main.py'], input='3', text=True, capture_output=True).stdout.strip() == '6'\n",
            "fuzz_cases": 12,
            "fuzz_methods": ["generation", "mutation", "grammar", "dictionary", "boundary"],
            "mutation": True,
        }
    )
    reports["python-full"] = await run(Project.model_validate(python))
    assert reports["python-full"]["generated_tests"]["exit_code"] == 0
    assert reports["python-full"]["coverage"]["status"] == "measured"
    assert reports["python-full"]["mutation"]["status"] == "measured"
    assert reports["python-full"]["fuzz"]["executed"] == 12
    bad = fixture("python").model_dump()
    bad["cases"][0]["stdout"] = "wrong"
    reports["wrong-oracle"] = await run(Project.model_validate(bad))
    assert reports["wrong-oracle"]["checks"]["failed"] == 1
    invalid = fixture("cpp").model_dump()
    invalid["files"][0]["content"] = "not valid C++"
    reports["compile-error"] = await run(Project.model_validate(invalid))
    assert reports["compile-error"]["tool_status"] == "compile-error"
    assert any(
        item["file"] == "main.cpp" and item["line"] == 1 for item in reports["compile-error"]["diagnostics"]
    )
    attack = fixture("python").model_dump()
    attack["files"][0]["content"] = (
        '"""Probe only this job’s security boundary."""\nimport errno,os,socket\nassert not os.environ.get("STUDIO_OPENAI_KEY")\ntry:\n open("/opt/probe.txt","w").write("blocked")\n raise AssertionError("root writable")\nexcept OSError as error:\n assert error.errno in (errno.EROFS,errno.EACCES,errno.EPERM)\ns=socket.socket();s.settimeout(.2)\ntry:\n s.connect(("1.1.1.1",443));raise AssertionError("network connected")\nexcept OSError: pass\nprint(4)\n'
    )
    attack["files"][0]["content"] += (
        '\nimport stat\nruntime = os.environ["XDG_RUNTIME_DIR"]\ninfo = os.stat(runtime)\n'
        'assert runtime == "/tmp/code-flow-runtime"\nassert info.st_uid == os.getuid()\n'
        "assert stat.S_IMODE(info.st_mode) == 0o700\n"
    )
    reports["boundary-probes"] = await run(Project.model_validate(attack))
    assert reports["boundary-probes"]["checks"]["passed"] == 1
    for name, code in (("timeout", "while True: pass\n"), ("bounded-output", "print('x' * 10000)\n")):
        target = fixture("python").model_dump()
        target["files"][0]["content"] = code
        reports[name] = await run(Project.model_validate(target))
        assert reports[name]["checks"]["failed"] == 1
    cpp = fixture("cpp").model_dump()
    cpp.update(
        {
            "fuzz_engine": "libfuzzer",
            "fuzz_harness": '#include <cstddef>\n#include <cstdint>\nextern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) { if (size > 0) { volatile uint8_t value = data[0]; (void)value; } return 0; }\n',
        }
    )
    reports["libfuzzer"] = await run(Project.model_validate(cpp))
    assert reports["libfuzzer"]["fuzz"]["status"] == "completed", reports["libfuzzer"]
    cpp.update(
        {
            "fuzz_engine": "aflplusplus",
            "fuzz_harness": "#include <iostream>\nint main() { std::string input; std::getline(std::cin,input); if (!input.empty() && input[0] == 'x') std::cout << \"x\"; return 0; }\n",
        }
    )
    reports["aflplusplus"] = await run(Project.model_validate(cpp))
    assert reports["aflplusplus"]["fuzz"]["status"] == "completed", reports["aflplusplus"]
    python.update(
        {
            "fuzz_engine": "atheris",
            "fuzz_harness": "import sys,atheris\n@atheris.instrument_func\ndef test_input(data):\n if data and data[0] == 120:\n  return len(data)\natheris.Setup(sys.argv,test_input)\natheris.Fuzz()\n",
        }
    )
    reports["atheris"] = await run(Project.model_validate(python))
    assert reports["atheris"]["fuzz"]["status"] == "completed", reports["atheris"]
    python.update(
        {"tests": "def test_reject():\n assert False\n", "fuzz_engine": "blackbox", "fuzz_cases": 0}
    )
    reports["failed-generated-test"] = await run(Project.model_validate(python))
    assert reports["failed-generated-test"]["generated_tests"]["exit_code"] != 0
    assert reports["failed-generated-test"]["mutation"]["status"] == "blocked"
    python.update({"tests": "", "mutation": False, "fuzz_cases": 5, "fuzz_methods": ["mutation"]})
    python["files"][0]["content"] = (
        "import sys\ndata=sys.stdin.buffer.read()\nif data == b'2\\n': print(4)\nelse: raise SystemExit(2)\n"
    )
    reports["binary-mutation"] = await run(Project.model_validate(python))
    assert reports["binary-mutation"]["fuzz"]["executed"] == 5
    assert reports["binary-mutation"]["checks"]["passed"] == 1
    # Seeds are raw bytes, not replacement-decoded text; an empty findings list is valid.
    web_demo = Project.model_validate_json(Path("examples/web-demo.project.json").read_text())
    reports["web-demo"] = await run(web_demo)
    assert reports["web-demo"]["checks"]["passed"] == 3, reports["web-demo"]
    assert reports["web-demo"]["checks"]["failed"] == 0, reports["web-demo"]
    assert reports["web-demo"]["generated_tests"]["exit_code"] == 0, reports["web-demo"]
    assert reports["web-demo"]["fuzz"]["status"] == "completed", reports["web-demo"]
    located = fixture("python").model_dump()
    located.update(
        {
            "files": [
                {"name": "main.py", "content": "import helper\nprint(helper.scale(2))\n", "encoding": "text"},
                {
                    "name": "helper.py",
                    "content": "def scale(value):\n    if value < 0:\n        return 0\n    return value * 2\n",
                    "encoding": "text",
                },
                {"name": "unused.py", "content": "def unused():\n    return 7\n", "encoding": "text"},
            ],
            "fuzz_cases": 0,
            "benchmark_repeats": 1,
        }
    )
    reports["multifile-locations"] = await run(Project.model_validate(located))
    measured = reports["multifile-locations"]
    assert measured["checks"]["passed"] == 1, measured
    assert measured["coverage"]["files"]["helper.py"]["missing_lines"] == [3], measured
    assert [2, 3] in measured["coverage"]["files"]["helper.py"]["missing_branches"], measured
    assert measured["coverage"]["files"]["unused.py"]["missing_lines"] == [1, 2], measured
    assert any(
        item["file"] == "unused.py" and item["line"] == 1 and item["code"] == "PY-UNUSED-FUNCTION"
        for item in measured["static"]["findings"]
    ), measured
    crashing = fixture("python").model_dump()
    crashing.update(
        {
            "fuzz_cases": 0,
            "files": [
                {
                    "name": "main.py",
                    "encoding": "text",
                    "content": "def fail():\n    return 1 / 0\n\nfail()\n",
                }
            ],
        }
    )
    reports["runtime-locations"] = await run(Project.model_validate(crashing))
    assert reports["runtime-locations"]["checks"]["failed"] == 1
    assert any(
        item["file"] == "main.py" and item["line"] == 2
        for item in reports["runtime-locations"]["diagnostics"]
    )
    mapped = fixture("typescript").model_dump()
    mapped.update(
        {
            "fuzz_cases": 0,
            "files": [
                {
                    "name": mapped["entry"],
                    "encoding": "text",
                    "content": "function fail(): never {\n  throw new Error('fixture');\n}\nfail();\n",
                }
            ],
        }
    )
    reports["typescript-original-location"] = await run(Project.model_validate(mapped))
    assert reports["typescript-original-location"]["checks"]["failed"] == 1
    assert any(
        item["file"] == mapped["entry"] and item["line"] == 2
        for item in reports["typescript-original-location"]["diagnostics"]
    ), reports["typescript-original-location"]
    assert reports["wrong-oracle"]["unlocated_failures"], (
        "Wrong answers must not fabricate source root causes"
    )
    print(
        "LOCATED_ACCEPTANCE="
        + json.dumps(
            {
                "coverage": measured["coverage"],
                "unused": [item for item in measured["static"]["findings"] if item["file"] == "unused.py"],
                "runtime": reports["runtime-locations"]["diagnostics"],
                "typescript": reports["typescript-original-location"]["diagnostics"],
                "compiler": reports["compile-error"]["diagnostics"],
                "unlocated_oracle": reports["wrong-oracle"]["unlocated_failures"],
            }
        )
    )
    print(f"Validated {len(reports)} real isolated worker scenarios")


if __name__ == "__main__":
    asyncio.run(main())
