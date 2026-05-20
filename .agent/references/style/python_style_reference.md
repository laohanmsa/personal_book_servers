# Python Style Reference

Use this reference only when editing or reviewing Python code.

## Standards Basis

- PEP 8
- Google Python Style Guide
- Ruff and Black
- Django coding patterns used in this repo

## Core Rules

### Structure

- All non-trivial Python logic belongs in a class.
- `__init__` stores config only. No I/O, DB access, or side effects there.
- Django views and Celery tasks should be thin dispatchers that call a service or manager class.

### Naming And Types

- Use `snake_case` for functions, methods, variables, and modules.
- Use `PascalCase` for classes.
- Fully annotate function signatures, including return types.
- Prefer modern union syntax when the runtime allows it; otherwise use the compatible form required by the target Python version.

### Imports

- Keep imports at module level unless a lazy import is required to break a proven circular import.
- When using a lazy import, explain why with an inline comment.
- Never use wildcard imports.

### Functions And Methods

- Keep functions and methods small and single-purpose.
- Prefer guard clauses and the happy path over deep nesting.
- Split multi-step logic into private helpers on the owning class.

### Errors And Logging

- Do not swallow exceptions silently.
- Use specific exception types where possible.
- Log before returning from a handled failure path.
- Use `logger`, not `print()`, in production code.

### Django-Specific

- Keep raw SQL out of views and tasks.
- Avoid N+1 queries with `select_related` and `prefetch_related`.
- Use `.values()` and `.values_list()` when only fields are needed.
- Prefer bulk operations over per-row `update_or_create()` loops where safe.

### Common Pitfalls

- Do not use mutable default arguments.
- Do not hide config in default function arguments.
- Do not keep global mutable state for request or task logic.
- Do not leave business logic in Celery tasks or Django views.
