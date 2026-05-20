---
category: experience
status: active
safety: read-only
---

# Bash Experiences

1. macOS BSD `grep` does not support `-P`; use `-E` with POSIX extended regex for cross-platform scripts.
2. `set -u` can fail on empty array expansions. Guard arrays before expanding them.
3. `find ... | sort -z` with `read -d ''` is not portable to default macOS tooling; prefer newline-delimited paths when filenames are controlled.
4. Do not `source` arbitrary `.env` files. Use the application's dotenv loader or parse only required keys.
5. Redact secret-bearing values before teeing or logging command output.
6. For long remote commands, use keepalive options or periodic output so idle connections do not silently drop.
