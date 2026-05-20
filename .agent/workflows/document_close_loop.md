---
description: Close the loop after any material documentation, report, walkthrough, or session milestone update
category: docs
status: active
safety: writes-local
---

# Documentation Close Loop

Use this workflow after any material documentation event, including:

- report completed
- walkthrough completed
- design note or implementation note finalized
- session milestone reached after commit, push, key decision, bug resolution, or operational change

This workflow turns the documentation rule into an operational close loop:

1. save/update the final document
2. save/update the matching session note when needed
3. refresh Secretary
4. verify the document is indexed

## Step 1 — Choose Final Destination

Use these defaults:

- app-specific durable doc:
  - `<project>/docs/`
- cross-project durable doc:
  - `docs/`
- session milestone note:
  - `<project>/docs/session_notes/YYYY-MM-DD_<topic>.md`

Do not leave the final artifact in chat, a temp path, or an agent-only scratch path.

## Step 2 — Create Or Update The Final Doc

Requirements:

- include a timestamp
- use a dated filename for reports, walkthroughs, and session notes
- keep the project overview in `README.md`, not in a session note

If the output is a session milestone note, use:

- `docs/templates/session_milestone_note.md`

If the same task is continuing on the same day, update the existing session note instead of creating duplicates.

## Step 3 — Re-open And Verify The Final Path

Before reporting completion:

1. re-open the exact saved file
2. confirm the expected sections are present
3. confirm the file is in the correct `docs/` path

## Step 4 — Record Session Milestone When Needed

If the task involved:

- a commit
- a push
- a key design or implementation decision
- a completed report/walkthrough
- a resolved bug/root-cause finding
- a deploy/restart/runtime state change

then also create or update a session note in:

- `<project>/docs/session_notes/`
- or `docs/session_notes/` for cross-project work

The session note should capture:

- timestamp
- topic
- project
- summary of change/decision
- files/interfaces touched
- verification
- git refs when relevant
- follow-up items

## Step 5 — Refresh Secretary

Run:

```bash
bash .agent/skills/secretary/secretary.sh scan --incremental
```

If the new doc still does not appear in the index, run:

```bash
bash .agent/skills/secretary/secretary.sh doctor
bash .agent/skills/secretary/secretary.sh scan
```

## Step 6 — Verify Index Coverage

Check that the new or updated doc path appears in:

- `project_document_index.md`

If it does not, the loop is not closed yet.

## Step 7 — Report Final Paths

In the final user report, include:

- exact saved doc path(s)
- whether a session note was updated
- Secretary reindex status
- index verification result

## Quick Command Reminder

Secretary refresh:

```bash
bash .agent/skills/secretary/secretary.sh scan --incremental
```

Session note template:

```text
docs/templates/session_milestone_note.md
```
