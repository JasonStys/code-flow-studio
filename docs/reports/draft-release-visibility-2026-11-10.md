# Draft release visibility correction — 2026-11-10

By Jason Stys.

## Actual observed failure

Release run [42830936957](https://github.com/JasonStys/code-flow-studio/actions/runs/42830936957)
used immutable source `5d6e594605b04f37429d5e1cd96ad4e98fe43c3b`.
Windows, Linux and macOS builds all passed actual compiled native acceptance and
uploaded their accepted payloads/checksums. The final
[verify-draft job 129887436962](https://github.com/JasonStys/code-flow-studio/actions/runs/42830936957/job/129887436962)
failed while reading prepared numeric draft ID 440443517, before completing final
draft/asset verification. Its metadata command returned nonzero and failed closed;
the bounded diagnostic does not establish a specific HTTP status.

An independent authenticated owner read found the draft present, unpublished,
non-prerelease, bound to that exact source, with all twelve assets uploaded and
provider SHA-256 digests. The successful prepare/build jobs had contents-write
credentials; the failed final job had only contents-read visibility. This is a
release-workflow permission fault, not a demonstrated application/native failure.

## Provider requirement and narrow correction

[GitHub's official release API documentation](https://docs.github.com/en/rest/releases/releases#list-releases)
states that draft release listings require push access. The final main-only manual
verification job now receives `contents: write` solely for draft metadata visibility.
Its `actions: read` and `security-events: read` scopes remain unchanged. The actual
`verify` command still makes reads only, validates the prepared numeric ID/source,
rechecks current-main validation and processed CodeQL/open-alert evidence, and
preserves the draft. It cannot publish or overwrite an asset.

The actual workflow policy now requires that exact final-job permission set.
Mutation tests alter only the real final job's scopes to reject contents-read/none
visibility and expanded unrelated write scopes. Commented mappings, duplicate keys,
unparsed expressions and duplicate whole permission blocks are rejected; legitimate
inline explanations retain their parsed scope. This is a deliberately narrow
reviewed workflow-format contract, not a general YAML parser. The existing integrated final CLI
test still supplies only allowed metadata reads and proves the release remains a
draft. Immutable main checkouts, no privileged PR trigger, serial uploads and all
existing source/security/native/payload gates are retained.

## Fresh version and preserved history

Version 0.4.2 is a fresh coherent product/runtime/UI/Python/npm/worker/installer
identity. Application algorithms, account/vault/consent schemas and UI workflows
retain the previously accepted implementation; only metadata/display/required
matching worker-image identity changes accompany the CI correction. No data
migration, Docker repair or host-execution fallback is added.

The failed 0.4.1 draft and its assets/tags are not deleted, overwritten or retargeted.
The 0.4.0 published release also remains unchanged. Historical source/native/CodeQL
reports keep their original source and execution scope. Approved Word/Excel bytes
remain snapshots of runtime baseline `7d2158a57bb49e8f837fffbfe23b301902465412`.

## Validation boundary

Local validation passed 286 tests and 28 subtests in 48.77 seconds, measuring
1,539/1,808 controller/data statements (85.12%, unchanged 80% floor). This includes
the actual workflow mutants and coherent product/worker metadata checks. Ruff,
87 exact source maps, strict TypeScript/Vite build and unchanged publication-byte/
source/link validation passed. All four npm metadata files were independently
compared with the prior source: only product/root versions changed, with no
dependency-graph update. Existing cache/chunk warnings remain visible.

A freshly frozen and compiled local Windows 0.4.2 application passed its real
account/editor/privacy/lock journey in 6.3 seconds, including matching product/
health version, fixed worker bytes, actual HTTP drain/sealing and disappearance
of both owned service/bootloader PIDs. This was an unsigned dirty development
build, not a published download or clean-machine installer claim. Existing
0.4.1 draft assets and all approved Word/Excel bytes remain unchanged.

Passing local
fixtures cannot prove GitHub token visibility; the fresh authorized 0.4.2 release
workflow must demonstrate that provider boundary. Full current-main CodeQL,
three-OS native acceptance and independent downloaded installer checks remain
separate required gates before owner publication. No automatic rerun or bypass
turns the failed historical run into a pass.
