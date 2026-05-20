---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Code Style And Scripts

Use the repo's local style before inventing new patterns.

1. When editing/reviewing Python, load `.agent/references/style/python_style_reference.md`.
2. When editing/reviewing Rust, load `.agent/references/style/rust_style_reference.md`.
3. When editing/reviewing C++, load `.agent/references/style/cpp_style_reference.md`.
4. Do not load language references for unrelated tasks.
5. Keep non-trivial Python logic in classes or cohesive modules when it has state, configuration, or multiple related operations; keep framework entrypoints thin when applicable.
6. When writing fetch/parse/transform scripts, load `.agent/references/writing/script_progress_logging.md` and include clear progress logging.
7. Prefer structured APIs/parsers over ad hoc strings when available.
8. Keep comments sparse and useful; do not add narration that repeats obvious code.
