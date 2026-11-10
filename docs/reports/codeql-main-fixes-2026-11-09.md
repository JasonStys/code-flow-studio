# Full-main CodeQL fixes — 2026-11-09

By Jason Stys. This report separates observed full-source findings, local fixes
and still-required source/release acceptance.

## Actual full-main baseline

The first non-PR scan analyzed
`d1c1326591fa26cab63dede34566c5e61ffe1182` in
[CodeQL run 42771727567](https://github.com/JasonStys/code-flow-studio/actions/runs/42771727567).
All three actual job logs identify CodeQL 2.27.4 and this main checkout, with no PR
diff-range step or automatic incremental query filter. Processed SARIF contains
one Python and one JavaScript result, with zero Actions results. Both alerts were
open at that observation. The separate Validate and Desktop packages workflows
also passed; those green jobs did not clear these findings. Earlier PR zero
results covered changed-line alerts only.

| Alert | Rule and original location | Diagnosis and correction |
|---|---|---|
| 1 | `py/redos`, `tests/test_contracts.py:186` | The demo-source contract regex admitted a backslash through both alternatives, allowing exponential ambiguity on malformed unterminated literals. The escaped-character and ordinary-character alternatives are now disjoint. This is a development test pattern, not a live application input handler. |
| 2 | `js/file-system-race`, `runner/node_checks.cjs:24` | File size was checked through a path before a separate unbounded path read. A growing file or path replacement could invalidate that observation. The reader now opens one descriptor, checks its metadata, rejects non-regular files, caps actual bytes and closes in `finally`. |

No query exclusion, blanket suppression, fabricated SARIF result or alert dismissal
is used. Updated exact-source scans must independently verify the correction.

## Independent regressions and observed local results

The original demo-source equality check remains. Three 200,000-character
unterminated strings exercise repeated escaped ampersands, escaped quotes and
ordinary characters. Explicit short test IDs keep diagnostics and temporary paths
bounded; the synthetic text is not printed into test identifiers.

Seven Node tests import the actual worker bridge without launching analyzers or
executing submitted target code. They check Unicode JSON at exactly eight MiB,
empty/malformed JSON, oversized files, a stale small size observation against
larger real bytes, directories, propagated I/O failure with a closed descriptor,
and an actual pathname replacement after opening. The original descriptor still
returns original contents while the replaced pathname contains different JSON.

On Windows/Python 3.14.6/Node 24, all 158 controller/privacy/provider/parser/training-
data Python checks passed with 1,448/1,714 measured statement lines (84.48%), above
the unchanged 80% floor. All seven worker-reader tests and the four separately
locked inert analyzer fixtures passed. Ruff, exact source maps and the strict
TypeScript/Vite build passed. The existing local pytest-cache warning remains
visible. Local Docker was left unchanged: real compiler, sanitizer, fuzz, coverage
and sandbox checks still require the original hosted isolated-worker gate.

## Delivery and version boundary

Source prepares product hotfix 0.4.1, with matching Python/npm/runtime/UI/installer
and worker-image metadata. The fixed distributed resource is
`runner/node_checks.cjs`. The Dockerfile copies it to `/opt/node_checks.cjs`; the
reviewed image must be rebuilt as `code-flow-worker:0.4.1`. The controller does not
silently select an older worker, repair Docker, run targets directly on the host,
or relax existing network/filesystem/resource isolation.

Electron's existing `extraResources` contract also copies this reviewed file to
`resources/runner/node_checks.cjs` in each platform package. Actual packaged-native
acceptance now compares its SHA-256 with the current reviewed checkout, in addition
to all original account/source-inspection/sandbox/lock assertions. This proves
the packaged resource bytes; it does not claim a matching Docker image is already
installed on the user's machine. The worker Dockerfile and analyzer locks remain
included, with Linux-compatible runner line endings.

Fresh exact-main CodeQL result/alert review, all original source gates and all
three operating systems' SDK/compiled-native acceptance remain required before a
new release. Installer/download acceptance is separate from local source tests.
This report does not claim a 0.4.1 release is published. Published 0.4.0 assets/tags,
account data, vault/database/report/consent schemas and installed applications
remain unchanged by this source work.

## Release authorization and additional acceptance

The final local suite passed 248 Python tests and 28 independent subtests while
retaining the original 1,448/1,714 controller/training-data line measurement and
80% floor. Separately, 90 release/draft tests and 28 subtests covered 310/319
measured helper statement lines (97.18%); the draft lookup module reached 100%,
the release gate 96.43%. These denominators remain separate from application and
worker-runtime coverage. An independent read-only review found and corrected a
zero-rule analysis admission gap; missing/zero/boolean/string/negative rule counts
now fail. Release builds/uploads are serialized without changing the three
platforms or the 35-minute per-job budget.

The actual Windows SDK-shell journey passed in 7.2 seconds and the newly built
compiled app in 7.1 seconds, using disposable profiles. Genuine unlock proofs took
164/160 ms. The compiled journey verified embedded source/version metadata and
the exact fixed worker SHA-256, then completed editor/history/source inspection,
catalog, sandbox, lock and clean owned-process exit. A real 214,917,076-byte
Windows archive also passed bounded provenance/worker-member verification; its
SHA-256 was `8149f0ce9cd55b7c0fa23fb27fb37b4d84164fe56f749f48a654f155f193c040`.
This local development archive honestly recorded `source_dirty: true`, so it is
not a publishable clean-source release. The owned temporary archive was removed
after verification to conserve disk. No local installer or user application was
installed/replaced by these checks.

The trusted manual release workflow requires a clean current-main checkout,
complete successful exact-source Validate/Desktop packages/CodeQL histories and
one successful main push per lane. It separately verifies actual processed full-
main CodeQL categories, positive integer rule counts, no processing warnings or
errors, and zero open main alerts. A bounded complete release listing and numeric
ID reread prevent the published-only tag lookup mistake for untagged drafts.
Existing tags, drafts, public releases, ambiguous or unavailable metadata and
asset collisions stop the operation; there is no delete, force or clobber path.

Every build embeds data-only source/version/dirty-state/worker-hash metadata. The
actual compiled-native journey must pass before writing its generated acceptance
receipt. Upload authorization checks that receipt, actual portable archive
metadata and worker bytes, exact filenames and SHA-256 sidecars. Binary streaming
uses the fixed GitHub uploads HTTPS host and prepared numeric release ID, with
size/time limits, no redirect following, and provider digest/size checks before
and after each new asset. Only draft preparation/upload jobs have release write
scope; security-event read scope stays in prerequisite/final gates. The final
read-only job requires all twelve assets and leaves the release draft for the
owner's separate download/installer acceptance and publication.

Release coordination assumes other privileged repository actors do not publish or
modify this draft during the workflow. State is checked around each upload;
GitHub does not provide an atomic draft-only upload transaction. A partial or
failed draft is preserved for explicit review rather than automatically reused,
deleted or retargeted. There is no zero-alert claim for the unscanned corrective
source or claim of a new published release from these local observations.

## Remaining technical limits

Descriptor identity prevents following a replacement pathname; it is not an
immutable snapshot against a process modifying the same open file in place.
Actual reads remain bounded even when size metadata is stale. POSIX nonblocking
and no-follow flags are used where the Node platform supplies them; no universal
Windows symlink-protection claim is made. JSON syntax failures and I/O errors
remain failures, never empty successful coverage reports. Static analysis and
bounded regression cases do not establish absence of every defect or a precise
performance/complexity guarantee.
