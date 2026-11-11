# Installed Windows application validation 10 November 2026

By Jason Stys. This edition documents actual published **0.4.4** installed
bytes built from `8a533a0b9838b994c18ec0475d91a4f8db1be6fa`. Earlier Office editions retain their
historical source baselines and byte identities.

## Observed results

All 12 downloaded assets matched provider/sidecar hashes; all 3 archives carried the exact 0.4.4 source manifest. Actual installed runtime is CPython 3.14.10/Electron 44.11.

The full installed registration, WebCrypto unlock, editor, source inspection and 48-category journey passed. Both complete saved revisions also survived a real 0.4.3 to 0.4.4 same-account vault upgrade.

The journey checked vault lock, owned service drain, sealing and actual service and bootloader exit.

422 source tests,2 Windows platform skips and 28 subtests passed, with 85.13 percent coverage at the unchanged 80 percent controller/training floor. Current main/compiler/package/CodeQL workflows passed.

Actual target exits 0, 1, 2, 7, 255 and malformed input 2 were measured; argument rejection, report write failure and timeout were blocked.

## Illustrated workflow and implementation

The [four-page application guide](windows-application-guide-0.4.4.docx) contains actual installed
application screenshots, prepared inputs used within the full app, operating
steps and important code excerpts from the immutable runtime source. Every page
was inspected and the OOXML schema passed validation. The [review manifest](windows-application-guide-0.4.4.json)
records Word, screenshot, source and rendered-page identities.

## User data and limits

Use the matching versioned Windows installer and its SHA256 sidecar from Releases. The existing per user installation and shortcut are retained; no IntelliJ, system Python or package manager setup is needed to open the app.

Account archives live separately in the OS user application data directory named CodeFlowStudioAccounts. Preserve the complete directory and your private vault phrase before a later upgrade. Login recovery does not imply recovery of a lost encryption phrase.

Local compilation needs a working isolated engine and matching 0.4.4 worker image. Hosted compiler checks passed; Docker on this PC was unchanged.

Measured instrumentation does not mean 100 percent line coverage or proven correctness. Same identity file bindings check consistency and are not tamper proof attestation of a malicious worker target. Unused candidates require developer review.

Unsigned packages trust the local OS and service while unlocked. Synthetic upgrade records matched exactly; normal archives were backed up and checksum-compared without decrypting them.

Desktop and Start-menu target identities were verified where created. A complete
actual installed executable journey is separate from normal shortcut activation;
this report does not claim an additional manual shortcut-button test. No Docker
configuration, real credential or existing account data was used by the synthetic
acceptance. Prepared scenarios are inputs to the full product, never separate demo
applications.

This documentation commit must pass its own hosted checks. Earlier runtime results
do not certify future source changes.
