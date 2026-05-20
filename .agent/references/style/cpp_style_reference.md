# C++ Style Reference

Use this reference only when editing or reviewing C++ code.

## Standards Basis

- C++ Core Guidelines
- Google C++ Style Guide
- LLVM coding conventions
- ISO C++20

## Core Rules

### Naming

- Use `CamelCase` for classes, structs, enums, functions, and methods.
- Use `snake_case` for local variables and parameters.
- Use trailing `_` for member variables.
- Use `kCamelCase` for constants.

### Design

- Favor single-responsibility classes.
- Prefer composition over inheritance.
- Use `explicit` on single-argument constructors.
- Mark read-only methods `const`.
- Use `[[nodiscard]]` where ignored return values would be dangerous.

### Resource Management

- Prefer RAII and stack allocation.
- Use smart pointers instead of raw ownership.
- Never manage raw memory manually without a strong reason.

### Functions

- Keep functions short and focused.
- Prefer clear return values over output parameters.
- Use guard clauses to reduce nesting.

### Concurrency And Safety

- Use `std::lock_guard` or `std::unique_lock`, never manual lock/unlock.
- Do not hold locks while calling external code.
- Document thread-safety assumptions for shared state.

### Formatting

- Prefer 2-space indentation.
- Keep lines readable and rely on `clang-format`.
- Avoid macros unless they are clearly justified.
