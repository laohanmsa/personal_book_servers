# Rust Style Reference

Use this reference only when editing or reviewing Rust code.

## Standards Basis

- Rust API Guidelines
- Rust 2024 style conventions
- `rustfmt`
- `clippy -D warnings`

## Core Rules

### Naming

- Use `UpperCamelCase` for types and enum variants.
- Use `snake_case` for functions, methods, variables, and modules.
- Use `SCREAMING_SNAKE_CASE` for constants and statics.

### Errors

- Do not use `.unwrap()` or `.expect()` in production paths.
- Return `Result<T, E>` for fallible operations and preserve typed errors.
- Prefer domain error enums over stringly-typed failures.

### Ownership And APIs

- Prefer `&str` over `&String` and `&[T]` over `&Vec<T>` for read-only parameters.
- Minimize cloning, especially in hot paths.
- Keep public APIs documented with `///` comments.

### Concurrency

- Do not hold a lock guard across `.await`.
- Prefer clear ownership and scoped locking.
- Use `tokio::spawn` only for truly independent tasks.

### Safety And Size

- Every `unsafe` block needs a `// SAFETY:` justification.
- Keep functions small and focused.
- Extract helpers instead of building deep nested matches or long async blocks.

### Verification

- Run `cargo test`.
- Run `cargo clippy -- -D warnings` when practical.
- For runtime behavior changes, also run the repository's relevant integration or smoke checks when they exist.
