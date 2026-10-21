# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: execute(argv, stdin, timeout)@L32; adapter(language, entry)@L70; seeds(project)@L115; coverage(command, project)@L163; mutants(command, project)@L232; instrumented_fuzz(project)@L292; main()@L338
# variables: DEADLINE@L28; WORK@L29; remaining@L34; started@L37; errors@L38; output@L38; child@L40; expired@L47; expired@L51; code@L52; size@L56; plans@L72; rng@L117; case@L118; corpus@L118; boundaries@L119; dictionary@L120; enabled@L121; method@L123; rows@L126; index@L127; method@L130; value@L132; _@L134; value@L134; value@L136; value@L143; data@L145; position@L146; strategy@L147; value@L158; case@L170; measured@L187; data@L190; files@L191; measured_files@L192; budget@L193; file@L194; name@L195; measured_file@L198; record@L205; key@L214; measured_file@L215; name@L215; values@L216; budget@L218; entry@L220; file@L227; path@L241; original@L242; tree@L243; node@L244; sites@L244; outcomes@L245; index@L247; candidate@L248; node@L249; target@L249; compile_check@L257; killed@L261; inconclusive@L262; case@L263; result@L264; inconclusive@L265; killed@L266; result@L271; inconclusive@L272; killed@L273; item@L282; valid@L282; item@L287; engine@L294; harness@L295; result@L302; build@L306; argv@L319; build@L321; argv@L324; result@L327; project@L340; file@L342; build@L359; command@L359; compilation@L360; report@L361; times@L377; case@L378; result@L379; passed@L380; _@L388; benchmark@L389; findings@L422; corpus@L423; method@L424; value@L424; result@L425; method@L451
# parameters: argv@L32; stdin@L32; timeout@L32; entry@L70; language@L70; project@L115; command@L163; project@L163; command@L232; project@L232; project@L292
# </code-map>

"""Container-only compiler/test/fuzz worker. Never import this module on the host.

Symbol and variable locations: docs/code-index.md. Projects are untrusted; a
restricted container is mandatory. Child output, time, corpus and files are bounded.
"""

import base64
import hashlib
import json
import os
import random
import resource
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEADLINE = time.monotonic() + 150
WORK = Path("/tmp/project")  # noqa: S108 -- private, fresh, per-job container tmpfs; never host /tmp


def execute(argv: list[str], stdin: str | bytes = "", timeout: float = 3) -> dict:
    """Execute argv without a shell; retain a bounded tail and real elapsed wall time."""
    remaining = DEADLINE - time.monotonic()
    if remaining <= 0:
        return {"exit_code": None, "stdout": "", "stderr": "Run budget exhausted", "timeout": True, "ms": 0}
    started = time.perf_counter()
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        try:
            child = subprocess.Popen(
                argv, cwd=WORK, stdin=subprocess.PIPE, stdout=output, stderr=errors, start_new_session=True
            )
            try:
                child.communicate(
                    stdin.encode() if isinstance(stdin, str) else stdin, timeout=min(timeout, remaining)
                )
                expired = False
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, 9)
                child.communicate()
                expired = True
            code = child.returncode
        except OSError as error:
            return {"exit_code": None, "stdout": "", "stderr": str(error)[:1000], "timeout": False, "ms": 0}
        output.seek(0, 2)
        size = output.tell()
        output.seek(max(0, size - 8192))
        errors.seek(0, 2)
        errors.seek(max(0, errors.tell() - 8192))
        return {
            "exit_code": code,
            "stdout": output.read(8192).decode(errors="replace"),
            "stderr": errors.read(8192).decode(errors="replace"),
            "timeout": expired,
            "ms": (time.perf_counter() - started) * 1000,
            "output_truncated": size > 8192,
        }


def adapter(language: str, entry: str) -> tuple[list[str] | None, list[str]]:
    """Map a validated language to fixed compiler and stdin/stdout process commands."""
    plans = {
        "python": (["python", "-m", "py_compile", entry], ["python", entry]),
        "javascript": (["node", "--check", entry], ["node", entry]),
        "typescript": (
            [
                "tsc",
                entry,
                "--target",
                "ES2022",
                "--module",
                "commonjs",
                "--sourceMap",
                "--outDir",
                "compiled",
            ],
            ["node", "--enable-source-maps", f"compiled/{Path(entry).stem}.js"],
        ),
        "cpp": (["g++", "-std=c++20", "-O2", "-Wall", "-Wextra", entry, "-o", "target"], ["./target"]),
        "c": (["gcc", "-std=c17", "-O2", "-Wall", "-Wextra", entry, "-o", "target"], ["./target"]),
        "java": (["javac", entry], ["java", "-XX:MaxRAMPercentage=60", "-cp", ".", Path(entry).stem]),
        "rust": (["rustc", "--edition", "2021", "-O", entry, "-o", "target"], ["./target"]),
        "php": (["php", "-l", entry], ["php", entry]),
        "bash": (["bash", "-n", entry], ["bash", entry]),
        "sql": (None, ["python", "sql_driver.py"]),
        "assembly": (["gcc", entry, "-o", "target"], ["./target"]),
        "csharp": (
            [
                "dotnet",
                "build",
                "App.csproj",
                "--nologo",
                "--verbosity",
                "quiet",
                "--ignore-failed-sources",
                "-o",
                "compiled",
            ],
            ["dotnet", "compiled/App.dll"],
        ),
    }
    return plans[language]


def seeds(project: dict) -> list[tuple[str, bytes]]:
    """Produce reproducible bounded generation, mutation, CSV/SQL grammar and dictionary inputs."""
    rng = random.Random(project["seed"])  # noqa: S311 -- reproducible fuzzing, never a credential
    corpus = [case["stdin"] for case in project["cases"]] or ["", "0\n", "hello\n"]
    boundaries = ["", "\n", "0", "-1", "2147483647", "NaN", "null", "\x00", "💡", "A" * 4096]
    dictionary = ["'", '"', "../", "SELECT", "DROP TABLE", "%s", "\\", "<script>", "=SUM(A1)"]
    enabled = [
        method
        for method in project["fuzz_methods"]
        if method in {"boundary", "dictionary", "generation", "mutation", "grammar"}
    ]
    rows = []
    for index in range(project["fuzz_cases"]):
        if not enabled:
            break
        method = enabled[index % len(enabled)]
        if method == "boundary":
            value = boundaries[(index // len(enabled)) % len(boundaries)]
        elif method == "generation":
            value = "".join(chr(rng.randrange(1, 128)) for _ in range(rng.randrange(1, 256)))
        elif method == "grammar":
            value = rng.choice(
                [
                    f"id,value\n{rng.randrange(100)},{rng.random()}\n",
                    "CREATE TABLE t(x INTEGER); INSERT INTO t VALUES(42); SELECT * FROM t;",
                ]
            )
        elif method == "dictionary":
            value = rng.choice(corpus) + rng.choice(dictionary)
        else:
            data = bytearray(rng.choice(corpus).encode() or b"0")
            position = rng.randrange(len(data))
            strategy = index % 5
            if strategy == 0:
                data[position] ^= 1 << rng.randrange(8)
            elif strategy == 1:
                data[position] = (data[position] + rng.choice([-1, 1, 16])) % 256
            elif strategy == 2:
                del data[position]
            elif strategy == 3:
                data[position:position] = bytes([rng.randrange(256)])
            else:
                data.extend(rng.choice(corpus).encode()[:128])
            value = bytes(data[:8192])
        rows.append((method, value.encode() if isinstance(value, str) else value))
    return rows


def coverage(command: list[str], project: dict) -> dict:
    """Retain per-supplied-file Python coverage locations; never invent condition or non-Python coverage."""
    if project["language"] != "python" or not project["cases"]:
        return {
            "status": "not-applicable",
            "reason": "Built-in line/branch coverage needs Python and approved cases",
        }
    for case in project["cases"]:
        execute(
            [
                "python",
                "-m",
                "coverage",
                "run",
                "--rcfile=/dev/null",
                "--parallel-mode",
                "--branch",
                "--source",
                ".",
                project["entry"],
            ],
            case["stdin"],
        )
    execute(["python", "-m", "coverage", "combine", "--rcfile=/dev/null"])
    measured = execute(["python", "-m", "coverage", "json", "--rcfile=/dev/null", "-o", "coverage.json"])
    if measured["exit_code"] != 0 or not (WORK / "coverage.json").exists():
        return {"status": "blocked", "reason": measured["stderr"]}
    data = json.loads((WORK / "coverage.json").read_text())
    files = {}
    measured_files = {}
    budget = 20000
    for file in project["files"]:
        name = file["name"]
        if file["encoding"] != "text" or not (name.endswith(".py") or name == project["entry"]):
            continue
        measured_file = data["files"].get(name)
        if measured_file is None:
            files[name] = {
                "status": "not-measured",
                "reason": "No coverage record; not assumed covered or uncovered",
            }
            continue
        record = {
            "status": "measured",
            "summary": measured_file["summary"],
            "source_sha256": hashlib.sha256(file["content"].encode()).hexdigest(),
            "truncated": False,
        }
        files[name] = record
        measured_files[name] = measured_file
    # Prioritize every file's missing locations before spending the shared budget on executed lines.
    for key in ("missing_lines", "missing_branches", "executed_lines", "excluded_lines"):
        for name, measured_file in measured_files.items():
            values = measured_file.get(key, [])
            files[name][key] = values[:budget]
            budget -= len(files[name][key])
            files[name]["truncated"] |= len(files[name][key]) != len(values)
    entry = files.get(project["entry"], {}).get("summary", {})
    if not entry:
        return {"status": "blocked", "reason": "No entry coverage record", "files": files}
    return {
        "status": "measured",
        "entry": entry,
        "files": files,
        "locations_truncated": any(file.get("truncated", False) for file in files.values()),
        "scope": "Supplied Python sources under approved CLI cases only, not generated pytest tests; line/branch, not condition/MC/DC. At most 20,000 location entries, missing before executed; negative branch destinations denote function exits.",
    }


def mutants(command: list[str], project: dict) -> dict:
    """Bounded Python mutation; exclude invalid/timeouts and retain approved case/test oracles."""
    if not project["mutation"]:
        return {"status": "not-selected"}
    if project["language"] != "python" or not project["cases"]:
        return {"status": "blocked", "reason": "Python and passing approved oracles are required"}
    import ast
    import copy

    path = WORK / project["entry"]
    original = path.read_text()
    tree = ast.parse(original)
    sites = [node for node in ast.walk(tree) if isinstance(node, (ast.Compare, ast.BinOp))][:8]
    outcomes = []
    try:
        for index in range(len(sites)):
            candidate = copy.deepcopy(tree)
            target = [node for node in ast.walk(candidate) if isinstance(node, (ast.Compare, ast.BinOp))][
                index
            ]
            if isinstance(target, ast.Compare):
                target.ops[0] = ast.NotEq() if isinstance(target.ops[0], ast.Eq) else ast.Eq()
            else:
                target.op = ast.Sub() if isinstance(target.op, ast.Add) else ast.Add()
            path.write_text(ast.unparse(candidate))
            compile_check = execute(["python", "-m", "py_compile", project["entry"]])
            if compile_check["exit_code"]:
                outcomes.append({"index": index, "status": "invalid"})
                continue
            killed = False
            inconclusive = False
            for case in project["cases"]:
                result = execute(command, case["stdin"])
                inconclusive |= result["timeout"] or result["exit_code"] is None
                killed |= (
                    result["stdout"].strip() != case["stdout"].strip()
                    or result["exit_code"] != case["exit_code"]
                )
            if project["tests"] and not inconclusive:
                result = execute(["python", "-m", "pytest", "-q", "test_generated.py"], timeout=15)
                inconclusive |= result["timeout"] or result["exit_code"] is None
                killed |= result["exit_code"] != 0
            outcomes.append(
                {
                    "index": index,
                    "status": "inconclusive" if inconclusive else "killed" if killed else "survived",
                }
            )
    finally:
        path.write_text(original)
    valid = [item for item in outcomes if item["status"] in {"killed", "survived"}]
    return {
        "status": "measured",
        "mutants": outcomes,
        "evaluated": len(valid),
        "score": sum(item["status"] == "killed" for item in valid) / len(valid) if valid else None,
        "caveat": "At most 8 operator mutants; survivors may be equivalent. Not an exhaustive mutation proof.",
    }


def instrumented_fuzz(project: dict) -> dict:
    """Run genuine libFuzzer/AFL++/Atheris only when a developer-supplied harness exists."""
    engine = project["fuzz_engine"]
    harness = project["fuzz_harness"]
    if not harness:
        return {"status": "blocked", "engine": engine, "reason": "Reviewed harness required"}
    (WORK / "corpus").mkdir(exist_ok=True)
    (WORK / "corpus/seed").write_text(project["cases"][0]["stdin"] if project["cases"] else "hello")
    if engine == "atheris" and project["language"] == "python":
        (WORK / "fuzz_harness.py").write_text(harness)
        result = execute(["python", "fuzz_harness.py", "-runs=128", "-max_len=4096", "corpus"], timeout=20)
    elif engine in {"libfuzzer", "aflplusplus"} and project["language"] in {"cpp", "c"}:
        (WORK / "fuzz_harness.cpp").write_text(harness)
        if engine == "libfuzzer":
            build = execute(
                [
                    "clang++",
                    "-std=c++20",
                    "-g",
                    "-O1",
                    "-fsanitize=fuzzer,address,undefined",
                    "fuzz_harness.cpp",
                    "-o",
                    "fuzz_target",
                ],
                timeout=30,
            )
            argv = ["./fuzz_target", "-runs=128", "-max_len=4096", "corpus"]
        else:
            build = execute(
                ["afl-clang-fast++", "-std=c++20", "-O1", "fuzz_harness.cpp", "-o", "fuzz_target"], timeout=30
            )
            argv = ["afl-fuzz", "-i", "corpus", "-o", "afl-results", "-V", "8", "--", "./fuzz_target"]
        if build["exit_code"] != 0:
            return {"status": "blocked", "engine": engine, "build": build}
        result = execute(argv, timeout=20)
    else:
        return {"status": "blocked", "engine": engine, "reason": "Unsupported language/engine combination"}
    return {
        "status": "findings" if result["exit_code"] != 0 else "completed",
        "engine": engine,
        "process": result,
        "caveat": "Instrumentation output retained verbatim. No synthetic edge counts.",
    }


def main() -> None:
    """Compile, execute approved tests, benchmark, fuzz and report one bounded project."""
    project = json.loads(Path("/input/job.json").read_text())
    WORK.mkdir()
    for file in project["files"]:
        (WORK / file["name"]).write_bytes(
            file["content"].encode() if file["encoding"] == "text" else base64.b64decode(file["content"])
        )
    if project["language"] == "sql":
        (WORK / "sql_driver.py").write_text(
            "import sqlite3,sys\nc=sqlite3.connect(':memory:')\nc.executescript(open("
            + repr(project["entry"])
            + ").read())\nfor row in c.execute(sys.stdin.read() or 'SELECT 1'):\n print('|'.join(map(str,row)))\n"
        )
    if project["language"] == "csharp":
        (WORK / "App.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings></PropertyGroup></Project>'
        )
        (WORK / "NuGet.Config").write_text(
            "<configuration><packageSources><clear/></packageSources></configuration>"
        )
    build, command = adapter(project["language"], project["entry"])
    compilation = execute(build, timeout=45) if build else {"exit_code": 0, "stdout": "", "stderr": ""}
    report = {
        "tool_status": "completed",
        "compilation": compilation,
        "checks": {"passed": 0, "failed": 0, "cases": []},
        "oracle_hash": hashlib.sha256(json.dumps(project["cases"], sort_keys=True).encode()).hexdigest(),
        "environment": {
            "worker": "polyglot-v1",
            "python": sys.version.split()[0],
            "language": project["language"],
            "machine": os.uname().machine,
            "benchmark_repeats": project["benchmark_repeats"],
        },
    }
    if compilation["exit_code"] != 0:
        report["tool_status"] = "compile-error"
    else:
        times = []
        for case in project["cases"]:
            result = execute(command, case["stdin"])
            passed = (
                result["exit_code"] == case["exit_code"]
                and result["stdout"].strip() == case["stdout"].strip()
                and not result["output_truncated"]
            )
            report["checks"]["passed" if passed else "failed"] += 1
            report["checks"]["cases"].append({"name": case["name"], "passed": passed, **result})
            if passed:
                for _ in range(project["benchmark_repeats"]):
                    benchmark = execute(command, case["stdin"])
                    if (
                        benchmark["exit_code"] == case["exit_code"]
                        and not benchmark["timeout"]
                        and not benchmark["output_truncated"]
                        and benchmark["stdout"].strip() == case["stdout"].strip()
                    ):
                        times.append(benchmark["ms"])
                    else:
                        report["checks"]["failed"] += 1
                        report["checks"]["cases"].append(
                            {"name": case["name"] + " benchmark-repeat", "passed": False, **benchmark}
                        )
        if project["tests"]:
            (WORK / "test_generated.py").write_text(project["tests"])
            report["generated_tests"] = execute(
                ["python", "-m", "pytest", "-q", "test_generated.py"], timeout=30
            )
        else:
            report["generated_tests"] = {"status": "not-provided"}
        report["benchmark"] = {
            "samples_ms": times,
            "median_ms": statistics.median(times) if times else None,
            "max_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "scope": "Process startup + workload; peak child RSS, not per-function memory. Exploratory measurements.",
        }
        report["coverage"] = coverage(command, project)
        report["mutation"] = (
            mutants(command, project)
            if report["checks"]["failed"] == 0 and report["generated_tests"].get("exit_code", 0) == 0
            else {"status": "blocked", "reason": "Baseline failures invalidate mutation"}
        )
        if project["fuzz_engine"] == "blackbox":
            findings = []
            corpus = seeds(project)
            for method, value in corpus:
                result = execute(command, value)
                if (
                    result["timeout"]
                    or result["exit_code"] is None
                    or (result["exit_code"] is not None and result["exit_code"] < 0)
                ):
                    findings.append(
                        {
                            "method": method,
                            "input_base64": base64.b64encode(value).decode(),
                            "sha256": hashlib.sha256(value).hexdigest(),
                            "process": result,
                        }
                    )
            report["fuzz"] = {
                "status": "findings" if findings else "completed",
                "engine": "blackbox",
                "executed": len(corpus),
                "seed": project["seed"],
                "findings": findings[:16],
                "nonzero_policy": "Ordinary nonzero exits are not automatically bugs; approved expected behavior is required",
                "blocked_methods": [
                    {
                        "method": method,
                        "reason": "Reference/relation/state model required via reviewed custom harness",
                    }
                    for method in project["fuzz_methods"]
                    if method in {"differential", "metamorphic", "stateful"}
                ],
                "coverage_guided": False,
            }
        else:
            report["fuzz"] = instrumented_fuzz(project)
    print("STUDIO_RESULT=" + json.dumps(report, allow_nan=False))


if __name__ == "__main__":
    main()
