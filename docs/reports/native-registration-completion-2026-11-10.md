# Native registration completion validation — 2026-11-10

By Jason Stys. This follow-up changes validation and diagnostics; application behavior,
account schemas and the prepared 0.4.1 product version are unchanged.

## Observed hosted failure

The full-main source `4f1d0aafd151db3c183e342012900dc75beda96d` passed
Validate and all three actual full-main CodeQL categories with no raw results.
Its Windows Desktop packages job passed the SDK journey but failed the compiled
journey while checking the recovery screen after registration. macOS and Linux
passed. [Original Windows job](https://github.com/JasonStys/code-flow-studio/actions/runs/42781323102/job/129711801105).
The recovery assertion had a five-second DOM deadline. The available buffered
service log and empty notice do not establish whether the request had completed;
the original Windows failure's underlying timing/resource cause remains unproven.
The earlier diagnostic also selected a submit-type attribute absent from the actual
implicit-submit Register button, so its busy state was not recorded.

## Completion and diagnostic contract

The reusable journey now observes the exact same-origin registration POST before
clicking. It requires the real response's HTTP 200 status and a recovery string
with the required minimum length before asserting the recovery screen. The phrase
is never logged. Registration errors fail with their status at that boundary.
The existing real vault-unlock proof, complete native journey's 60-second deadline,
all editor/source-inspector/privacy checks and zero retries remain intact.

Native diagnostics record request start/response timing, status, document readiness,
input validity booleans and the actual form button's disabled state. They omit input
values, response bodies, aliases, passwords and recovery/vault material.

## Independent local checks

- Eighteen actual private-browser journeys passed across Chromium, Firefox and
  WebKit, including genuine held registration and genuine duplicate-account cases.
  The held response comes from the real service: while delivery is held the form
  remains busy, with neither recovery nor workspace visible; releasing it completes
  a real account/unlock/lock journey. No canned success payload or timed sleep is used.
- The duplicate-account case receives the real conflict response and requires the
  helper to reject it before claiming recovery or workspace success. Replacing only
  the helper with its previous committed implementation makes this regression fail;
  the corrected file was restored byte-for-byte afterwards.
- The owned Windows Electron SDK journey passed in 5.7 seconds. A freshly rebuilt,
  unsigned unpacked Windows development application passed in 5.5 seconds, with
  embedded reviewed worker bytes and honestly dirty development provenance checked.
  Both use disposable profiles and close only their owned process. They do not prove
  installation, a clean machine, other operating systems or future hosted results.
- Strict TypeScript/Vite build, Ruff and generated source-index checks passed.
  Existing large-chunk and pytest-cache warnings are not hidden.

Commands: `npm run test:private`, `npm run test:desktop`,
`npm run build`, `python -m scripts.code_index --check` and
`python -m ruff check studio scripts tests`. Compiled acceptance sets
`STUDIO_INSTALLED_APP` to the owned development executable, never a user application.

The initial restricted-network package attempt could not resolve GitHub; the normal-user
build completed with the same locked tools. No Docker repair, installed-app replacement,
public release change or deadline increase occurred. Fresh exact-source hosted checks
remain required before the release owner can promote a new download.

## Follow-up: actual Windows shutdown boundary

[PR5 Windows job](https://github.com/JasonStys/code-flow-studio/actions/runs/42785409337/job/129725253872)
completed real registration (HTTP 200, 626 ms), unlock (HTTP 200, 406 ms), editor,
source inspector, privacy and lock checks. The SDK journey then stalled in owned
application close. The renderer and Electron process exited with code zero after
approximately the existing 30-second backend wait, but the worker subsequently
timed out and the hosted runner found an orphan frozen service. This is a distinct
shutdown observation; it does not establish a registration failure or prove the
exact reason the backend failed to exit.

The existing launcher did not inspect shutdown HTTP status or acknowledgement.
Native-test diagnostics now distinguish HTTP status, a bounded boolean stopping
receipt, the graceful-stop callback, workspace/lifespan completion, server-thread
completion, frozen main completion and the bootloader's exit. Only fixed milestones,
owned process identities, status and booleans are recorded. A separate disposable
launcher log survives debugger disconnection during asynchronous before-quit;
readback is capped at 64 KiB and emits no account/source values. The ten-second
snapshot is diagnostic only; it grants no success or extra time.

Native acceptance additionally requires all actual frozen completion milestones and
observes that the owned service/bootloader PIDs no longer exist (signal zero only,
never force termination). A successful click, a stopping receipt or Electron's exit
alone is insufficient. The existing two-second HTTP, 30-second graceful-stop and
60-second total journey limits, lack of retries and recoverable workspace behavior
are unchanged. This instrumentation is not represented as a speculative fix for the
unreproduced hosted shutdown cause.

Two real Response-stream cases reject denied/negative/malformed/oversized stopping
receipts; two Python cases check opt-in diagnostic privacy and the authenticated
route's actual callback/denial behavior. The complete existing Python gate passed
252 tests and 28 subtests, covering 1462/1734 controller/training statements (84.31%,
80% floor retained). All three Electron readiness/receipt Node cases passed.
Strict build, Ruff and 79 generated source maps passed. After rebuilding the frozen
service, the real Windows SDK journey passed in 6.7 seconds and a freshly compiled
unsigned unpacked application passed in 6.1 seconds; both proved HTTP 200/stopping
true, all sealing/thread/main milestones and owned child/bootloader disappearance.
The separate empty-store frozen-service probe also exited gracefully in 0.557 seconds.
These are local observations, not a claim that the failing hosted condition was
reproduced or repaired. Actual fresh hosted lifecycle evidence remains required.

## Diagnostic reader findings and correction

The first lifecycle-evidence PR scan identified two `js/file-system-race` results
in the new native test's diagnostic log readers (alerts 5 and 6). Both performed a
pathname existence check before opening; these were corrected rather than dismissed
or excluded. A shared test reader now opens once, handles missing files through
that operation's ENOENT result, verifies the same descriptor is a regular file,
reads at most the final 64 KiB and closes in all cases. Available no-follow and
nonblocking flags also avoid following a substituted link or blocking on a FIFO.
The descriptor is not claimed to freeze concurrent writes to the same file.

Two actual filesystem regressions cover missing/ordinary/oversized/nonregular
inputs and pathname replacement after the descriptor has opened. All five Node
readiness/receipt/descriptor tests pass; strict build and 81 exact source maps pass.
This correction affects diagnostic acceptance code, not the application shutdown
protocol, existing deadline or reported hosted failure. Fresh scanning is required
to confirm the two results have been automatically resolved.
