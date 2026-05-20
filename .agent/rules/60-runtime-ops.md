---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Runtime Operations

Runtime operations must target the environment actually named by the project or user.

1. Test deployed/runtime bugs from the actual serving environment whenever that environment is known and safe to inspect.
2. Do not substitute a local stack for a remote or production issue unless the user explicitly targets local runtime or local reproduction is the safest available first step.
3. Do not run legacy or inherited runtime workflows unless they match this repository's current runtime or the user explicitly asks for them.
4. For log, incident, or observability tasks, load the repository's current logging and operations references when they exist.
5. Before restarting, redeploying, migrating, reseeding, or otherwise mutating a runtime, state the target, risk, rollback path, and required authorization.
6. After any authorized runtime mutation, verify health, key functionality, and relevant logs before claiming readiness.
7. If no runtime is defined for the repository, say so and limit validation to file, build, test, and documentation checks.
