---
category: experience
status: active
safety: read-only
---

# Debugging Experiences

1. Pattern matching to memory is only a starting point. Run the cheapest safe verification before presenting a causal story.
2. A breaking point is not automatically a root cause. Continue tracing until the underlying cause is proved or safe decisive checks are exhausted.
3. Use a control case before testing a hypothesis when one is available; it separates system-wide failure from input-specific failure.
4. Do not use real mutations as diagnostic shortcuts. If a hypothesis needs a live side effect to test, ask for explicit authorization or design a mock/dry-run check.
5. Community references need concrete evidence: links, issue numbers, short quotes, or exact source paths.
6. Progress updates during unresolved incidents should be checkpoints with proof status, not confident narratives.
7. When an investigation stalls, switch evidence dimension: logs, source, raw payloads, state, metrics, or a controlled reproduction.
