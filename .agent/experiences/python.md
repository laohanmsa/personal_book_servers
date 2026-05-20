---
category: experience
status: active
safety: read-only
---

# Python Experiences

1. `str | None` union syntax requires Python 3.10+. Use `Optional[str]` or compatible annotations for scripts targeting older runtimes.
2. Never hardcode API keys or sensitive URLs as fallback defaults. Read env vars explicitly and fail closed when required values are missing.
3. Pydantic Settings bool fields parse `false`, `0`, `no`, and `off` as false, but empty or unknown strings can raise validation errors.
4. When renaming an import alias, search the entire file for stale references before running.
5. For resumable JSONL crawls, validate merged output by durable record IDs, not only by run manifests.
6. Chunk large payloads passed through shell commands; oversized argument lists fail before application code runs.
