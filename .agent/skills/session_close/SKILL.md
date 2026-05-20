---
name: Session Close
description: Close the current session when the user explicitly asks. Creates a dated archive under .agent/user_sessions, records full user messages plus short agent replies, checks docs and git closure, and then exits with a minimal farewell.
category: ops
status: active
safety: writes-local
---

# Session Close

Use this skill when the user explicitly says `close session`, `close this session`, `end session`, or equivalent.

This skill owns the close loop. Do not reply with a farewell until the archive file exists and the doc/git closure checks are done.

The writer script is:

- `.agent/skills/session_close/scripts/write_session_record.py`

## Steps

### 1. Pick The Session Name

- Prefer an explicit user-supplied name.
- Else use the active task brief slug.
- Else use the current branch name without the `codex/` prefix.
- Else infer a short hyphenated topic from the dominant task in the thread.

### 2. Close Docs

- Ensure the current task brief, note, or durable doc reflects the finished state of the work.
- If this session materially changed docs, rules, skills, or scripts, run:

```bash
bash .agent/skills/secretary/secretary.sh scan --incremental
```

- Verify the updated path appears in `project_document_index.md`.

### 3. Close Git Safely

- Treat `close session` as delegated ownership of routine git closure for this session.
- Inspect `git status --short --branch`.
- If the current task produced a coherent completed change and the path is safe, handle commit/merge/push according to the repo git rules without pushing that routine work back to the user.
- If there is nothing to ship, record that the branch is clean or note the remaining local edits.
- If there is a risky blocker such as conflicts, ambiguity, or a destructive step, do not guess. Record the blocker in the session archive.

### 4. Build The Session Payload

Prepare a JSON payload for the writer script with:

- `session_name`
- `generated_at`
- `messages`
- `docs`
- `git`
- optional `closing_note`

Rules for the payload:

- include every user message in full
- include one brief summary for each agent reply
- do not paste full assistant replies into the archive
- include the final doc and git status that was observed, not a guess

### 5. Run The Writer Script

Example:

```bash
python3 .agent/skills/session_close/scripts/write_session_record.py \
  --input /tmp/session_close_payload.json \
  --output-root .agent/user_sessions
```

Use any project Python with standard library support.

### 6. Re-open And Verify

Before replying to the user:

- re-open the exact saved file
- verify the path is `.agent/user_sessions/{date}/{session_name}.md`
- verify full user messages are present
- verify agent entries are short
- verify docs and git sections are present

### 7. Final User Reply

- After successful verification, reply `Bye`.
- If the user explicitly wants the thread ended, append:

```text
::archive{reason="User requested session close"}
```

## Rules

1. Do not skip the session archive file.
2. Do not store full assistant replies in the archive.
3. Do not leave the archive in a temp path.
4. `.agent/user_sessions/` is local session memory and should stay ignored by git.
5. If doc or git closure is blocked, record the blocker in the archive before the farewell.
