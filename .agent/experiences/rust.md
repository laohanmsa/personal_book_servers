---
category: experience
status: active
safety: read-only
---

- Rust 2024 edition requires inner `unsafe {}` blocks inside `unsafe fn` — even `ptr.add()` and `write_volatile()` need wrapping.
- When adding fields to a Rust enum variant, all `match` arms across the codebase must be updated (use `..` for forward-compatible patterns).
