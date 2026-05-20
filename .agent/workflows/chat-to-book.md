---
description: Save the previous agent response as a concise walkthrough document
category: docs
status: active
safety: writes-local
---

# Save Last Response As Walkthrough

1. Take the agent's most recent response.
2. Reformat it into a clean walkthrough artifact in the appropriate docs or artifact directory.
3. Preserve key tables, paths, commands, and conclusions.
4. Remove conversational filler and unverified claims.
5. Re-open the saved file and report the path.
6. If the repository uses Secretary, run `bash .agent/skills/secretary/secretary.sh scan --incremental`.
