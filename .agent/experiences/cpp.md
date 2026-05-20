---
category: experience
status: active
safety: read-only
---

- When rsync --delete copies source to remote, any server-only scripts (stop.sh, start.sh) in the target get deleted. Exclude them or keep them in source.
- C++ struct member renames require updating ALL references across all files — check reader/writer classes, not just the struct definition.
