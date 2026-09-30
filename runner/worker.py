# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: execute(argv, stdin, timeout)@L32; adapter(language, entry)@L68; seeds(project)@L103; coverage(command, project)@L151; mutants(command, project)@L186; instrumented_fuzz(project)@L234; main()@L280
# variables: DEADLINE@L28; WORK@L29; remaining@L34; started@L37; errors@L38; output@L38; child@L40; expired@L45; expired@L49; code@L50; size@L54; plans@L70; rng@L105; case@L106; corpus@L106; boundaries@L107; dictionary@L108; enabled@L109; method@L111; rows@L114; index@L115; method@L118; value@L120; _@L122; value@L122; value@L124; value@L131; data@L133; position@L134; strategy@L135; value@L146; case@L158; measured@L174; data@L177; entry@L178; path@L195; original@L196; tree@L197; node@L198; sites@L198; outcomes@L199; index@L201; candidate@L202; node@L203; target@L203; compile_check@L211; killed@L215; case@L216; result@L217; killed@L218; item@L225; valid@L225; item@L229; engine@L236; harness@L237; result@L244; build@L248; argv@L261; build@L263; argv@L266; result@L269; project@L282; file@L284; build@L301; command@L301; compilation@L302; report@L303; times@L319; case@L320; result@L321; passed@L322; _@L330; benchmark@L331; findings@L354; corpus@L355; method@L356; value@L356; result@L357; method@L383
# parameters: argv@L32; stdin@L32; timeout@L32; entry@L68; language@L68; project@L103; command@L151; project@L151; command@L186; project@L186; project@L234
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


def execute(argv: list[str], stdin: str = "", timeout: float = 3) -> dict:
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
                child.communicate(stdin.encode(), timeout=min(timeout, remaining))
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
            ["tsc", entry, "--target", "ES2022", "--module", "commonjs", "--outDir", "compiled"],
            ["node", f"compiled/{Path(entry).stem}.js"],
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


def seeds(project: dict) -> list[tuple[str, str]]:
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
            value = data[:8192].decode(errors="replace")
        rows.append((method, value))
    return rows


def coverage(command: list[str], project: dict) -> dict:
    """Measure Python line/branch coverage using approved cases; never invent condition coverage."""
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
                "--parallel-mode",
                "--branch",
                "--source",
                ".",
                project["entry"],
            ],
            case["stdin"],
        )
    execute(["python", "-m", "coverage", "combine"])
    measured = execute(["python", "-m", "coverage", "json", "-o", "coverage.json"])
    if measured["exit_code"] != 0 or not (WORK / "coverage.json").exists():
        return {"status": "blocked", "reason": measured["stderr"]}
    data = json.loads((WORK / "coverage.json").read_text())
    entry = data["files"].get(project["entry"], {}).get("summary", {})
    return {
        "status": "measured",
        "entry": entry,
        "scope": "Entry source only, approved CLI cases; line and branch, not condition/MC/DC",
    }


def mutants(command: list[str], project: dict) -> dict:
    """Bounded Python operator mutation; only valid, compilable mutants enter the denominator."""
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
            for case in project["cases"]:
                result = execute(command, case["stdin"])
                killed |= (
                    result["stdout"].strip() != case["stdout"].strip()
                    or result["exit_code"] != case["exit_code"]
                )
            outcomes.append({"index": index, "status": "killed" if killed else "survived"})
    finally:
        path.write_text(original)
    valid = [item for item in outcomes if item["status"] != "invalid"]
    return {
        "status": "measured",
        "mutants": outcomes,
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
                    if benchmark["exit_code"] == case["exit_code"] and not benchmark["timeout"]:
                        times.append(benchmark["ms"])
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
            if report["checks"]["failed"] == 0
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
                            "input_base64": base64.b64encode(value.encode()).decode(),
                            "sha256": hashlib.sha256(value.encode()).hexdigest(),
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
