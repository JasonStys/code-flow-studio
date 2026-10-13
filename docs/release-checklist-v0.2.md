# Local release checklist — 0.2

Release scope: local accounts and downloadable OS apps, not public account hosting. Public repository/release visibility was explicitly approved. Released runtime commit is b18265c24dd76ff3b80742883075ac97ef51687c.

Completed gates: threat-boundary/owner/CSRF/credential/crypto/path/lifecycle review; independent session key proof; no global-key borrowing; pinned local engine plus empty Docker config; no host fallback; failed-write and capacity recovery regressions; dependency and history/source scans; checked documentation/source maps; real browser/compiler/training evidence; actual packages tested on three OS runners; exact-source release gate; all six checksum records verified; downloaded Windows executable tested and installed; local website visibly open with author/contact/help.

No account/source migration or irreversible old-runtime cleanup occurred. Existing applicant/image apps and data are unchanged. No Docker repair, security-setting change, live AI cost, paid host/domain, public backend or Actions cleanup was performed.

Rollback: close the new app normally and preserve/cold-back up its entire protected account root. Keep encrypted archives, salt/key configuration and recovery materials together. Revert deployment to a separately tested compatible release only after backup; do not run an older service against the new root or assume archive format compatibility. Legacy data remains separate. Do not reset/delete unrelated Docker or account directories.

Stop release/operation on failed independent cases, corrupted archives, inability to seal, unexpected network destinations, host-execution fallback, lost owner binding or source-map/CI failure. Preserve recovery data; never silently delete it to satisfy a quota. Unsigned packages and active plaintext/OS compromise limitations remain disclosed.
