---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Evidence And Debugging

Use evidence before explanation.

1. For bugs, root cause, inconsistencies, incidents, and verification failures, follow `.agent/workflows/from_the_ground_up.md` and gate conclusions with `.agent/workflows/show_me_evidence.md`.
2. Required debug flow: objective -> hypothesis -> controlled check -> evidence -> conclusion.
3. Terminal debug status must be exactly one of: `Root cause proved`, `Breaking point proved but root cause not yet proved`, or `Inconclusive after safe decisive checks exhausted`.
4. Do not present a plausible midpoint story as root cause.
5. Trace the full relevant chain: source/API/docs -> parser/client -> storage/cache -> runtime object -> outbound payload -> external response/side effect.
6. Use strong identifiers for joins: user id, account id, record id, job id, request id, event id, transaction id, timestamps, host names, process names, or service names.
7. Prefer primary sources for protocol truth: official docs, official SDKs, raw upstream payloads, direct source APIs, and contract reads.
8. Verify non-trivial claims from at least two independent angles; for runtime-sensitive or high-impact work prefer three.
9. Use passive evidence when safe: database rows, logs, raw payloads, public/read-only APIs, configuration, traces, metrics, and runtime state.
10. Never modify production config, thresholds, database rows, caches, queues, or live state just to force test data.
11. Challenge your own narrative; explicitly handle simpler alternatives and contradictions.
12. If reporting an external API call, include owner, domain, method/path/key params, auth, per-user/batch/parallel behavior, freshness, exact field source, and cross-checks when inconsistent.
