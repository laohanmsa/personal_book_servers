---
category: experience
status: active
safety: read-only
---

# Django Development Experiences

1. Verify external payload fields against model fields before assuming sync behavior.
2. Avoid slow count queries on large joined list views; use estimated counts or bounded exact counts when the product can tolerate it.
3. Keep views, tasks, and signal handlers thin. Put business logic in service classes or cohesive modules.
4. Long-running management commands should close stale database connections before ORM work and retry transient connection failures.
5. Use `transaction.on_commit(...)` for side effects that depend on committed rows.
6. Bulk operations bypass `save()`, `auto_now`, validation, and signals; set required fields explicitly.
7. Avoid absolute count assertions in reused test databases. Use unique test markers or before/after deltas.
8. If an app has both `tests.py` and a `tests/` package, verify the intended tests are actually discovered.
