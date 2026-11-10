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
