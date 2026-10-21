# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Evidence@L25
# functions: __setitem__(self, key, value)@L28; main()@L38
# variables: path@L31; temporary@L33; reports@L40; language@L41; result@L42; python@L46; bad@L60; invalid@L64; item@L69; attack@L71; code@L77; name@L77; target@L78; cpp@L82; web_demo@L121; located@L127; measured@L144; item@L151; crashing@L153; item@L170; mapped@L172; item@L189; item@L199
# parameters: key@L28; self@L28; value@L28
# </code-map>

"""Real compiler, generated-test, fuzz and adversarial-container integration checks.

Symbol and variable locations: docs/code-index.md. Requires the trusted worker
image. Failure evidence is exported even when a target intentionally fails.
"""

import asyncio
import json
from pathlib import Path

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
