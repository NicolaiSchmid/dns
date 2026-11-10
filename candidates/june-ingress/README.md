# June ingress DNS candidate

Inactive source preparation for permanent DNS owner `NicolaiSchmid/dns`.
This directory is not a provider source in `production.yaml`. Merging this
candidate must not activate proxying. No provider operation is authorized here.

Source: June ingress withdrawal preparation (NicolaiSchmid/june#979), commit
`45f9948720a6a8c26d23c82754809a7e309a4986`,
`artifacts/junepartner-release/withdrawal-operations.json` and
`artifacts/junepartner-release/withdrawal-activation.md`.
The manifest's internal `sourcePin` identifies its earlier application baseline;
it is not the artifact commit. Consult those pinned files for the complete
Worker/origin sequence. The single live ledger remains June's
`.plans/2026-11-04-junepartner-release-readiness.md`; this is no deployment receipt.

## Exact declaration

`dearjune.ai.yaml` is a full candidate replacement for
`zones/general/dearjune.ai.yaml`, adding only
`octodns.cloudflare.proxied: true` to the following records:

| Name | Type | Content | Cloudflare record ID | Prior proxy |
| --- | --- | --- | --- | --- |
| dearjune.ai | A | 216.150.1.1 | a475416ccfb2b33475c4387ce13f71e4 | false |
| www.dearjune.ai | CNAME | f7742e391ac50f0a.vercel-dns-016.com. | 433cc12806c138a8b31129fa5817efc5 | false |

Zone ID: `d286575216add73551f89a402e467168`. IDs are guarded execution
identifiers, not OctoDNS record fields. Preserve TTL `1` (Cloudflare automatic),
TXT, existing auth CNAME, and every other field. Existing auth DNS is retained;
no new auth domain is proposed. Keep provided AuthKit and current issuers.
`nicool.ai`, ownCloud, unrelated records and new junepartner apex/www/apis are
excluded. New www/apis remain subject to assembled release gates; `apis` is
HTTP/site ingress, never SDK/cloud ingress or this Worker.

## Automation boundary

GitHub `scripts/sync-changed-zones.py` selects only `zones/` changes on PR/push;
this directory selects no zones and runs no OctoDNS synchronization. Manual
GitHub dispatch and legacy GitLab master deploy reconcile `production.yaml`,
whose YAML sources are only `zones/general`, `zones/private`, and
`zones/wasc_internal`. Neither reads this candidate. No workflow, provider,
active declaration or deployment command changes in this PR. Do not add this
directory as a provider source or copy the file into `zones/` during preparation.

## Promotion gates (separate coordinated activation)

Re-read the live objects via Executor immediately before any future write.
Require both record IDs, zone, types, names, content, TTL/settings and proxy=false
to match fresh private before snapshots; abort on drift. Rebase this candidate
against the then-current active zone; never overwrite newer TXT/auth changes.
Confirm assembled exact-head June checks and parent release coordination.

Worker must be installed/tested with the private bypass binding, reviewed exact
host routes, fail-closed quota behavior, and disabled public previews/logging.
Private credential transfer remains an unresolved gate; never retrieve secrets
into visible tool output. Prove protected-origin forwarding without a browser
bypass cookie before switching Vercel to all-deployment protection.

Before proxying, verify Cloudflare Full (strict), active edge certificates for
both names, and valid unexpired trusted origin certificates matching the origin
Host/SNI. Test the proposed Worker/private binding/TLS path using an approved
isolated preflight; certificate issuance, binding presence or DNS ownership alone
do not prove it works. Never weaken TLS to Flexible/Full to bypass failure.

Only after those gates may a separate reviewed change promote the two metadata
additions into the active zone. Parent must coordinate the merge because main
push can apply it automatically. Scope any reconciliation to dearjune.ai;
manual full-zone reconciliation is not this release operation. If a release
executor patches DNS directly, patch only `{"proxied":true}` on each guarded ID
and reconcile the active declaration as part of that same coordinated release
so automation cannot undo it. No such action is performed by this candidate.

After activation, verify authoritative and multiple independent recursive
answers plus certificate-verifying HTTPS on both names. TTL `1` means automatic,
not one-second convergence. Capture actual pre-change authoritative TTLs and
allow cached old answers to expire; proxy toggles and edge propagation are not
atomic, and there is no fixed zero-outage guarantee. Mixed old/new resolver
answers can bypass the Worker until convergence. Require Worker denial markers,
unaffected GET/POST, redirects/query preservation, assets, WorkOS callback,
login/refresh/logout/cookies and Convex acceptance before origin lockdown.
Then prove anonymous direct aliases and custom Host/SNI cannot reach the app.

## Exact rollback

Before Vercel all-deployment protection: guarded patches on the two IDs restore
only `{"proxied":false}`, retaining their original type/content/TTL/settings;
remove only newly created Worker route IDs from the activation receipt. Revert
the two active OctoDNS metadata additions (or explicitly declare false) in the
coordinated source rollback, preventing later reconciliation from re-enabling
proxying. Verify readback, DNS/cache convergence and HTTPS on both old targets.
This restores the previous unsafe ingress and is not an accepted withdrawal.

After origin lockdown: retain proxying, routes, Worker denial and Vercel
`ssoProtection.deploymentType=all`. Roll back Worker to its recorded known-good
version/private binding. If unavailable, accept a controlled outage pending the
release owner. Do not automatically unproxy or weaken protection.

Only explicit incident-owner approval acknowledging reopened ingress permits
policy reversal: guard current `all`, restore `all_except_custom_domains`, read
back, then restore the two proxy fields/source declaration to false and delete
only recorded new routes. Restore a retired alias only from its saved snapshot
if required. Revoke a new Worker-only credential only after checking all its
consumers; never revoke the pre-existing credential blindly. Preserve private
before snapshots and returned route/version IDs outside Git; ledger receipts
must contain no credential values.
