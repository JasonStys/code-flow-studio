# Sanitizer and worker-analyzer compatibility

The worker has a separate npm lockfile under `runner/tools/`. A clean desktop npm audit does not
audit this graph. Both the controller workflow and Docker build now install it frozen, reject
moderate-or-higher advisories, and the controller checks real JS/TS analyzer exact-line fixtures.
The narrow `minimatch@>=7 <11.0.1` override applies independently in this graph; no advisory is
suppressed, target configuration loaded or parser source executed.

The first coordinated worker run after source navigation (42712484989, job 129485375442) compiled
the benign libFuzzer fixture but its instrumented executable exited with SIGSEGV in about 114 ms,
without fuzzer stdout/stderr. The original report correctly kept that as findings/unlocated. A
successful compiler or different workflow does not establish a successful fuzz run.

The image's default Debian Clang 14 sanitizer predates an upstream allocator-address change for
32-bit mmap ASLR. [LLVM's actual patch](https://github.com/llvm/llvm-project/commit/fb77ca05ffb4f8e666878f2f6718a9fb4d686839)
and [the runner compatibility report](https://github.com/actions/runner/issues/3481) describe a
startup collision on newer kernels. This is consistent with that failure, rather than proof from
an empty target log alone. The benign harness reads `data[0]` only when size is positive; it has no
deliberate out-of-bounds path.

LibFuzzer now explicitly uses Debian's [Clang 19](https://packages.debian.org/bookworm/clang-19),
matching [compiler runtime](https://packages.debian.org/bookworm/libclang-rt-19-dev) and symbolizer.
Default Clang/LLVM 14 stays available for existing AFL++ dependencies. The fuzzer still uses
`-fsanitize=fuzzer,address,undefined`, debug information, the original run/length/time budgets and
the exact original container restrictions. There is no sanitizer suppression, non-PIE workaround,
ASLR/sysctl change, extra capability, unconfined seccomp, network, host compiler fallback or retry
that hides a failed run.

## Bounded acceptance probe

`scripts/worker_checks.py` runs the trusted `runner/sanitizer_probe.py` first, inside a separate
owned container with the same fixed worker flags: non-root, no network, read-only root, dropped
capabilities, no-new-privileges, 1 GiB memory/swap ceiling, 128 PIDs, 2 CPUs and private 256 MiB tmpfs.
Only the standard single read-only job-file mount is present. No account/provider data is mounted.

The probe compiles an original, fixed benign harness under default and Clang 19 runtimes, then
records **all 16 process starts of each** with unchanged kernel ASLR. These are comparison data,
not automatic retries of a submitted project: every old/new result remains in the dossier. Every
candidate start must pass. A separate deliberate one-byte heap allocation with an out-of-bounds
write must produce an actual nonzero ASan heap-buffer-overflow diagnostic. That positive control
proves instrumentation has not simply been disabled to make a benign program pass.

The probe records compiler versions, kernel, ASLR settings, UID and available cgroup memory limit.
Each compiler/run has a 10-second process deadline; the broker caps the owned probe at 90 seconds
and 192 KiB of output, then removes only its exact owned container. No fixture source is supplied
by an application user. Normal user-harness failures still remain findings; a silent crash is
never reclassified as a completed fuzz result.

Hosted execution supplies the decisive before/after evidence. Local Windows protocol tests check
the unchanged flags and fail-closed/cleanup behavior; they do not run or claim Linux sanitizer
results. Docker Desktop remains unchanged. Created by Jason Stys.
