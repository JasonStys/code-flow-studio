# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: process(argv, directory)@L41; compile_probe(compiler, source, directory, name)@L59; optional_metadata(path)@L82; main()@L90
# variables: BENIGN@L24; FAULT@L31; STARTUPS@L38; result@L43; raw@L50; retained@L51; file@L61; binary@L63; built@L64; report@L92; file@L93; name@L93; path@L98; temporary@L100; directory@L101; corpus@L102; compiler@L105; key@L105; version@L106; binary@L107; attempts@L108; _@L110; item@L115; binary@L117; finding@L118; detected@L120
# parameters: argv@L41; directory@L41; compiler@L59; directory@L59; name@L59; source@L59; path@L82
# </code-map>

"""Container-only trusted sanitizer startup diagnosis by Jason Stys.

Compare old/new fixed compiler runtimes under unchanged cgroup, ASLR and seccomp
limits; require every candidate startup and a heap-overflow detection control.
Never imports a target project or weakens execution flags. Source variables and
function positions are generated in docs/code-index.md.
"""

import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path

BENIGN = """#include <cstddef>
#include <cstdint>
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size > 0) { volatile uint8_t value = data[0]; (void)value; }
  return 0;
}
"""
FAULT = """#include <cstddef>
#include <cstdint>
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  if (size > 0) { volatile uint8_t* value = new uint8_t[1]; value[2] = data[0]; delete[] value; }
  return 0;
}
"""
STARTUPS = 16


def process(argv, directory):
    """Bound execution of fixed trusted probes; never execute submitted source or use a shell."""
    result = subprocess.run(  # noqa: S603 -- fixed compiler/probe argv in an already restricted CI container
        argv,
        cwd=directory,
        capture_output=True,
        timeout=10,
        env={**os.environ, "ASAN_SYMBOLIZER_PATH": "/usr/bin/llvm-symbolizer-19"},
    )
    raw = result.stderr
    retained = raw if len(raw) <= 4096 else raw[:2048] + b"\n[bounded diagnostic excerpt]\n" + raw[-2048:]
    return {
        "exit_code": result.returncode,
        "stderr": retained.decode(errors="replace"),
        "output_truncated": len(raw) > 4096,
    }


def compile_probe(compiler, source, directory, name):
    """Compile one fixed probe with all original fuzzer, address and undefined sanitizers enabled."""
    file = directory / f"{name}.cpp"
    file.write_text(source, encoding="utf-8")
    binary = directory / name
    built = process(
        [
            compiler,
            "-std=c++20",
            "-g",
            "-O1",
            "-fsanitize=fuzzer,address,undefined",
            str(file),
            "-o",
            str(binary),
        ],
        directory,
    )
    if built["exit_code"] != 0:
        raise RuntimeError(f"Sanitizer probe compilation failed: {built}")
    return binary


def optional_metadata(path):
    """Record unavailable proc/cgroup metadata without relaxing the container to read it."""
    try:
        return path.read_text().strip()
    except OSError as error:
        return "unavailable (" + type(error).__name__ + ")"


def main():
    """Emit old/new startup evidence and require both a clean candidate and a real ASan finding."""
    report = {"probe_version": 1, "kernel": platform.release(), "uid": os.getuid()}
    for name, file in [
        ("mmap_rnd_bits", "/proc/sys/vm/mmap_rnd_bits"),
        ("randomize_va_space", "/proc/sys/kernel/randomize_va_space"),
        ("memory_max", "/sys/fs/cgroup/memory.max"),
    ]:
        path = Path(file)
        report[name] = optional_metadata(path)
    with tempfile.TemporaryDirectory(prefix="cfs-sanitizer-probe-") as temporary:
        directory = Path(temporary)
        corpus = directory / "corpus"
        corpus.mkdir()
        (corpus / "seed").write_bytes(b"4")
        for key, compiler in [("baseline", "clang++"), ("candidate", "clang++-19")]:
            version = subprocess.run([compiler, "--version"], capture_output=True, timeout=5, check=True)  # noqa: S603 -- trusted compiler metadata
            binary = compile_probe(compiler, BENIGN, directory, key)
            attempts = [
                process([str(binary), "-runs=128", "-max_len=4096", str(corpus)], directory)
                for _ in range(STARTUPS)
            ]
            report[key] = {
                "compiler": version.stdout.decode().splitlines()[0],
                "attempts": attempts,
                "failures": sum(item["exit_code"] != 0 for item in attempts),
            }
        binary = compile_probe("clang++-19", FAULT, directory, "positive-control")
        finding = process([str(binary), "-runs=128", str(corpus)], directory)
        report["positive_control"] = finding
        detected = finding["exit_code"] != 0 and "AddressSanitizer: heap-buffer-overflow" in finding["stderr"]
        report["status"] = "passed" if report["candidate"]["failures"] == 0 and detected else "failed"
    print("SANITIZER_PROBE=" + json.dumps(report), flush=True)
    if report["status"] != "passed":
        raise SystemExit("Candidate sanitizer startups or deliberate-fault detection failed")


if __name__ == "__main__":
    main()
