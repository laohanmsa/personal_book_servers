---
trigger: always_on
category: rule
status: active
safety: critical
---

# Safety And Authorization

Data, privacy, security, money, and external-system boundaries are hard stops.

1. Never execute actions that spend money, move assets, mutate external systems, contact real users, alter live accounts, or change production state without explicit user authorization.
2. Read-only checks are allowed when safe: logs, configs, source code, public APIs, local fixtures, metrics, traces, and non-sensitive metadata.
3. Ask permission before reading sensitive user-scoped, account-scoped, private, regulated, or production data in tests or writing real identifiers/secrets into test config.
4. Ask permission before any test or command that can mutate user data, production databases, queues, caches, external services, credentials, billing state, access controls, or live runtime state.
5. Before commands with meaningful security, data-loss, database-erasure, privacy, billing, or performance risk, warn clearly and ask permission.
6. Do not expose secrets, private keys, full sensitive URLs, API keys, auth tokens, private user data, or credential-bearing logs.
7. Sensitive or mutating real API tests must be opt-in, skipped by default, and never part of normal CI unless explicitly authorized.
