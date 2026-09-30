# Language contracts

Every adapter runs inside the trusted Linux worker and receives developer-approved stdin/stdout cases. Language recognition and editor syntax highlighting are broader than execution support. Current contracts use a flat project and one entry point; framework projects, package downloads and arbitrary archives are not automatically supported.

| Adapter | Compiler/runtime | Contract |
|---|---|---|
| Python | CPython 3.12, pytest, coverage.py, Hypothesis | Entry script; local imports/data files; custom pytest harness; built-in line/branch coverage and bounded operator mutation. |
| JavaScript | Node from Debian | Node CLI script with standard-library/local-module dependencies. |
| TypeScript | tsc 5.9.3 + Node | ES2022 CommonJS compilation; explicitly declare APIs or provide types. No automatic npm dependency installation. |
| C++ / C | g++ C++20 / gcc C17 | Single translation unit, local include files, stdin/stdout executable. Rich projects need an explicitly reviewed custom harness/build integration. |
| Java | OpenJDK 17 | Source filename matches public main class. No implicit Maven/Gradle resolution. |
| C# | .NET SDK 8 | Flat console project, implicit standard-library usings, offline built-in framework restore. No NuGet network downloads. |
| Rust | Debian rustc, edition 2021 | Standalone standard-library entry; no implicit Cargo crates/network. |
| PHP | Debian PHP CLI | CLI script and local files; no Composer download. |
| Bash | bash | Syntax check and stdin/stdout script. It cannot escape the container by invoking shell tools. |
| SQL | SQLite via Python | Entry creates in-memory schema/data; test stdin supplies query; rows join with `|`. This is not PostgreSQL/MySQL/T-SQL portability proof. |
| Assembly | GNU assembler through gcc | Linux x86-64 `.S` and C ABI. Other ISAs need a separate assembler/emulator adapter. |

## New adapters

Update the validated language enumeration, trusted Dockerfile, fixed compiler/process mapping, renderer selector, compiler fixtures, failure tests and this matrix together. Pin/audit downloads. Do not let an uploaded manifest supply Docker flags, arbitrary host commands, mounts, images or API credentials. Prove both working compilation and syntax/error handling through real isolated CI before calling an adapter validated.

## Test and fuzz harnesses

Reviewed pytest code can exercise Python functions or launch any preinstalled CLI through argv-based subprocesses inside the worker. Keep test oracles independent from target code. Coverage-guided C/C++ libFuzzer requires `LLVMFuzzerTestOneInput`; AFL++ requires an instrumented stdin/file harness. Atheris requires a Python byte-input harness and proper instrumentation. A recognized engine with no reviewed compatible harness reports blocked, not successful black-box coverage.

