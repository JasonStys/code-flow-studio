# Native HTTP drain and coherent local cancellation — 2026-11-10

By Jason Stys.

## Observed defect and scope

The [Windows native job](https://github.com/JasonStys/code-flow-studio/actions/runs/42796136482/job/129761676463)
at documentation PR head `7fc7693aba990925d35010fc0644108644e8eb3c` completed account,
editor, privacy and explicit workspace-lock checks. Its actual shutdown response
was HTTP 200 with `stopping: true`, and the frozen process logged the shutdown
callback. It did not reach the lifespan-close milestone before the unchanged
30-second launcher wait. Acknowledgement was not proof of service termination.

The pinned Uvicorn 0.38 server was using its default unlimited graceful HTTP drain.
Real owned-loopback experiments reproduced that pre-lifespan wait with both a held
handler and an incomplete POST body. A finite drain cancels those requests and
allows normal vault sealing. These controls establish the mechanism; they do not
identify which request remained open in the historical Windows failure.

## Correction

The account entry point now uses a five-second HTTP-drain budget. `NativeServer`
retains Uvicorn's listener, connection and normal lifespan handling. At drain
expiry it cancels and joins its own remaining HTTP tasks before lifespan shutdown.
There is no `force_exit`, process termination, skipped sealing, deadline increase
or test retry.

Raw `asyncio.Task.cancel()` can otherwise release an awaiting request's mutex while
Starlette/AnyIO thread work continues. Retained shielded operations now finish real
disk work before propagating cancellation, including repeated cancellation.
Unlock and lock complete their full marker/controller/key and seal/remove transitions.
Provider publication completes disk settings, actual in-memory destinations/keys
and snapshot together; authorized deletion, logout and recovery reset also finish
their local transitions under the existing request mutex. Network requests, AI
calls and request-body reads are not made uncancellable.

The HTTP budget is not a universal process-exit deadline: critical disk work,
owned-container cleanup and authenticated sealing must finish safely. A stalled
disk or unavailable cleanup can still prevent clean termination; recovery data
must be preserved rather than forcibly deleted.

## Verification

The real HTTP tests create and authenticate fictional accounts, retain an actual
revision, and hold a handler, partial body, real snapshot or authenticated restore.
At genuine cancellation they verify the request mutex remains held until offloaded
work completes. Normal lifespan then seals the workspace, removes plaintext and
the owner marker, clears keys, and restores the exact revision from its real
AES-GCM archive. Separate repeated-cancel/success/error controls check actual
thread completion. Real provider/deletion tests check consent/destination and
data/account-row coherence after cancellation.

Local Windows validation used Python 3.14.6, pinned Uvicorn 0.38, Electron 44.10.2
and Playwright 1.64.1. The full controller/training gate, original coverage floor,
strict TypeScript build, three-engine controller/account journeys and native
acceptance remain required. Results and counts are recorded in the integration
handoff rather than inferred from source inspection.

A freshly frozen service passed the actual Electron SDK journey. The freshly
compiled unpacked Windows application passed the unchanged account/editor/privacy/
lock journey in 6.2 seconds. It reported six connections and zero tasks before
normal drain, then zero of each afterward, completed workspace/lifespan/server/
main milestones, and both owned Python-service and bootloader PIDs had exited.
This is local dirty-build evidence, not a published release or clean-machine
installation claim. Exact-source hosted checks on all three operating systems,
full-main CodeQL and later fresh draft/download acceptance remain separate gates.

## References and retained boundaries

- [Pinned Uvicorn shutdown implementation](https://github.com/encode/uvicorn/blob/0.38.0/uvicorn/server.py)
  drains connections/tasks before lifespan shutdown.
- [Python cancellation and shielding](https://docs.python.org/3.14/library/asyncio-task.html#shielding-from-cancellation)
  distinguishes a protected child from its still-cancelled caller and requires
  retaining a strong task reference.
- [Private account operation](../private-accounts.md) describes local trust,
  recovery and the required container-only compiler boundary.

No user account, installed application, existing public release, Docker engine,
source-consent rule or worker-isolation permission was changed by these tests.
