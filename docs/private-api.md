# Private API contract

Local only: literal `http://127.0.0.1:<port>`. Host/Origin must match the actual listener. Mutations require JSON and `X-CFS-Request: v1`. Bodies are bounded at 4 MiB; unknown fields are rejected. HttpOnly SameSite=Strict cookies live under /private and never become URL/bearer/localStorage credentials. Every project/history/provider call also requires this session's independent key proof. No caller-selectable owner, filesystem root or executable is accepted.

| Route | Contract |
|---|---|
| GET /health | Nonsecret version/mode/author and launcher correlation nonce; not authorization. |
| POST /private/register, /private/login | Alias/password. Registration returns a once-shown random recovery code; login does not unlock source. |
| POST /private/reset | Alias/new password/one-use recovery code. Seal first, rotate credentials/code, revoke sessions; encryption phrase is independent. |
| GET /private/account | Own alias/salt/configured/unlocked/busy/recovery/save-failure/idle state. Never another owner's history or alias. |
| POST /private/unlock | Base64 32-byte browser-derived key and initial 16-byte salt. AES-GCM key proof, scoped recovery and actual controller lifecycle. |
| POST /private/activity | Proven session chooses/renews 600/1800/7200-second human-idle interval. Passive reads never renew this clock. |
| POST /private/save | Complete encrypted snapshot; active compiler jobs must finish first. |
| POST /private/lock, /private/logout | Cancel only owned jobs, seal/drop managed plaintext/key; failures preserve recovery state. Logout revokes the presented session. |
| GET /private/backup | Own encrypted archive only; complete cold-root backup also needs account/key configuration. |
| POST /private/delete | Current password and confirm=true, affecting only this live account and its archive. Backups/exports/disk sectors are not erased. |
| GET, PUT /private/providers | Sanitized own destinations/readiness/routes/revision; PUT accepts up to eight closed provider records and own secret inputs. Keys are never returned. Destination changes cannot reuse old keys. |
| /private/api/* | Preserved controller endpoints for revisions/runs/catalog/compare/reports/AI, scoped to the proven account. POST review returns genuine non-executing static evidence. New revisions/run queues stop at history capacity; reads and exports remain available. |
| POST /private/api/ai | Also requires `X-CFS-Provider-Revision` matching reviewed settings and consent=true. Stale configuration is rejected before outbound calls. Proposals are unverified. |
| POST /launcher/shutdown | Process-local native launcher bearer only, never exposed to the renderer. Browser controller shutdown is forbidden. |

Errors do not reflect submitted credentials/source. The response boundary adds no-store, no-referrer, nosniff, frame/permission restrictions and CSP even to denials/downloads. Scripts/connect destinations are self-only in the renderer; inline styles are intentionally allowed for Monaco. TLS verification remains on for explicitly approved HTTPS model endpoints, with proxies/redirects disabled. Do not expose this service as a public backend.
