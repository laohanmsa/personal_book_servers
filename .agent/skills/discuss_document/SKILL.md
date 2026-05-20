---
name: Discuss Document
description: Use Google Docs as the native comment and version-history interface for iterative document review. Trigger when the user wants to discuss, review, comment on, revise, re-version, or collaboratively refine a document, especially repo Markdown, with Google Docs comments, native version history, agent-owned sync back to the repo, and Secretary indexing after every processed round.
category: docs
status: active
safety: user-auth-required-for-google-docs
---

# Discuss Document

Use this skill when the user wants a low-friction review loop for a document. The user should comment in Google Docs normally; they should not need custom Markdown marks.

Core contract:

1. Google Docs is the comment UI.
2. Google Docs is also the rich review surface: it should be readable as a standalone document, with headings, tables, diagrams/images, version tracking, and visible agent responses when comments are processed.
3. Google Docs native version history is the primary version-control surface. Use named Google Docs versions for processed rounds whenever tooling permits; the in-document `Version List` is only a human-readable index to native versions.
4. Repo Markdown remains the clean latest-content copy. It may include the Google Doc link, latest observed revision, asset references, and brief discussion/version history, but not detailed stale text, long comment logs, or per-comment review markup.
5. Every processed comment or rewrite round must update both the Google Doc and the repo Markdown.
6. Every processed round must run Secretary indexing before reporting completion.

---

## User Experience

The intended user flow:

1. User asks to start a document discussion for a source file or existing Google Doc.
2. Agent creates or reuses a Google Doc and returns one edit/comment link.
3. User highlights text in Google Docs and adds normal comments.
4. User says `process comments`.
5. Agent reads unresolved comments, edits the document, adds a visible response/change surface in Google Docs, replies to comments with timestamps when supported, resolves addressed comments when supported, syncs the latest clean content back to repo Markdown, runs Secretary, then reports the round result.
6. User can add another comment round. The same process repeats.

`finalize` is optional. It means archive/close the discussion, not save for the first time. Saving happens every round.

The user may also ask for a rewrite, reversion, cleanup, or readability pass without saying `process comments`. Treat that as a processed round: update the Google Doc, create or reference the native Google Docs version, update the visible version index, sync clean Markdown, update local state, run Secretary, and report completion.

---

## Authorization And Connectors

Before touching Google Drive or Google Docs:

1. Prefer the available Google Drive/Docs connector or plugin.
2. If the connector is missing or unauthenticated, stop and ask the user to authorize/connect Google Drive.
3. Do not create OAuth client files, service-account keys, refresh tokens, or credential JSON inside the repo.
4. Do not store Google auth tokens in local skill state.
5. If the document appears to contain secrets, private keys, API keys, credentials, private user data, or unreleased sensitive data, warn the user before uploading/syncing it to Google Docs.

Required runtime capabilities:

- create or locate Drive folders,
- create or update Google Docs,
- read Google Doc content,
- list unresolved comments,
- reply to comments,
- resolve comments,
- use revision IDs/write controls or Google Docs version history where exposed,
- create/name a native Google Docs version through the connector, Docs UI, or browser automation when available,
- export or otherwise convert the final Google Doc content back to Markdown.

If a capability is unavailable, use the safest fallback and tell the user exactly which part needs manual action.

---

## Drive Folder Layout

Create or reuse this structure:

```text
Google Drive/
  Codex Discuss Documents/
    <project-name>/
      <worktree-name>/
        active/
          <yyyy-mm-dd-doc-slug>/
            <google-doc>
        archived/
```

Example:

```text
Codex Discuss Documents/
  personal_reader/
    personal_reader/
      active/
        2026-05-11-reading-workflow/
```

Inference rules:

1. `worktree-name` is usually `basename "$PWD"`.
2. `project-name` is the repository or repo-family name.
3. If the project name cannot be inferred from repo metadata, existing state, or the user request, ask once and persist the answer in local state.
4. Do not create a flat folder directly under the worktree name; always include both project and worktree layers.

---

## Local State

Store lightweight state outside the repo:

```text
$CODEX_HOME/discuss_document/<project-name>/<worktree-name>/<doc-slug>.json
```

State may include:

```json
{
  "project_name": "personal_reader",
  "worktree_name": "personal_reader",
  "source_path": "/absolute/path/to/repo/doc.md",
  "google_doc_id": "doc-id",
  "drive_folder_id": "folder-id",
  "doc_url": "https://docs.google.com/document/d/.../edit",
  "last_seen_revision_id": "revision-id-if-available",
  "last_processed_revision_id": "revision-id-if-available",
  "last_named_google_version": "v2.0-rich-rewrite",
  "revision_history": [
    {
      "round": "v2.0-rich-rewrite",
      "label": "v2.0-rich-rewrite",
      "version": "v2.0",
      "processed_at": "2026-05-11T13:07:04+08:00",
      "google_named_version": "v2.0-rich-rewrite",
      "google_named_version_status": "created|automatic-history-only|manual-needed",
      "prewrite_revision_id": "revision-id-if-available",
      "final_revision_id": "revision-id-if-available",
      "notes": "What changed in this round."
    }
  ],
  "processed_comment_ids": ["comment-id"],
  "last_processed_round_at": "2026-05-11T08:45:00+08:00"
}
```

Do not store full credential material. Avoid storing full comment content unless needed to recover or audit a failed round.

---

## Start Or Bind A Discussion

When the user provides a repo Markdown file:

1. Resolve the absolute source path.
2. Create or reuse the Drive folder.
3. Create or reuse a Google Doc in that folder.
4. Import the Markdown content with readable structure.
5. Save state linking the source path and Google Doc ID.
6. Return the Google Doc URL and concise instructions: "Comment in the Doc, then say `process comments`."

When the user provides an existing Google Doc:

1. Bind the Doc to a repo Markdown path if one is clear.
2. If no source path is clear, ask the user for the repo Markdown destination before processing comments.
3. Check Drive capabilities before editing.

---

## Preflight Before Processing Comments

For every `process comments` round:

1. Load local state and confirm the Google Doc and repo source path.
2. Check Drive file capabilities. Require comment read/reply capability and content edit capability.
3. Read the latest Google Doc content and revision ID when available.
4. List unresolved comments with fields equivalent to:
   - `id`
   - `createdTime`
   - `modifiedTime`
   - `resolved`
   - `anchor`
   - `content`
   - `htmlContent`
   - `quotedFileContent`
   - `replies`
   - `author`
5. Select comments that are unresolved and not already fully processed.
6. If there are no actionable comments, still offer to sync if the Doc changed since the last state.

Use comment `id` as the durable pointer. Use `quotedFileContent` or nearest heading as the fallback context when anchors drift.

When Google Docs exposes revision IDs, capture the pre-edit revision ID and use write controls on edits.

---

## Native Version History

Use Google Docs native version history to manage versions.

For every processed comment, rewrite, reversion, or readability round:

1. Capture the pre-edit revision ID when available.
2. Apply the document update with write controls when available.
3. Create or name a native Google Docs version for the completed round, using a stable label such as `v2.0-rich-rewrite` or `2026-05-11 round 2 - rich rewrite`.
4. Prefer the connector if it exposes named-version support.
5. If the connector cannot name versions but browser/UI automation is available in the authenticated Google Docs session, use `File -> Version history -> Name current version`.
6. If no tool can create a named version, rely on Google Docs automatic native version history and mark the round as `automatic-history-only` in local state and the visible version index. Do not present the in-document `Version List` as a replacement for native version history.

The in-document `Version List` is a semantic index for readers. It should mirror native version names/status and explain why the version exists, but Google Docs version history remains the source of truth for diffs, authorship, timestamps, restores, and earlier copies.

---

## Rich Google Doc Standard

The Google Doc should be the easiest place for the user to read and review the document.

For research, architecture, review, or strategy documents:

1. Use a clear title, `Version List`, executive answer, and short numbered sections.
2. Prefer explanatory diagrams, charts, tables, or screenshots when they make the document easier to understand.
3. Use Google Docs-native headings and links when the connector supports them.
4. Store generated image assets in the repo next to the Markdown when the repo needs a durable copy, and insert them into Google Docs as inline images.
5. Remove stale or user-denied recommendations from the main recommendation. If historical context is useful, keep it in a short "What Changed" or version-history note, not as live guidance.
6. Write for the next reader: explain the accepted direction, why old content was removed, and what evidence anchors the current content.

Do not leave raw placeholders such as `[FIGURE]`, conversion artifacts, or long review logs in the final reading surface.

---

## Process Comment Round

A processed round is incomplete until all steps below are done:

1. Build a comment worklist with stable IDs and timestamps.
2. Decide for each comment:
   - `addressed`
   - `partially_addressed`
   - `needs_clarification`
   - `rejected_with_reason`
3. Edit the Google Doc based on addressed comments.
4. Add or update a visible Google Docs response/change surface for the round. It must include:
   - current timestamp,
   - stable comment IDs or grouped comment IDs,
   - `RESPONSE`: what the agent did or decided,
   - `OUTDATED`: the old/replaced document direction or stale wording,
   - `NEW`: the current accepted content direction.
5. Highlight the response/change surface when styling APIs are available. Use distinct visual treatment for response, outdated, and new content. If styling APIs are limited, use explicit labels and place the section near the top or in a clearly titled review section.
6. Reply to every processed comment with:
   - current timestamp,
   - status,
   - short explanation of what changed or why no change was made,
   - pointer to the source path or section changed when useful.
7. Resolve comments only when they are addressed or rejected with a clear reason.
8. Leave comments unresolved when user clarification is needed.
9. Create/name the native Google Docs version for the round when tooling permits.
10. Update the Google Doc `Version List` as a semantic index to the native version history, and update local state revision history.
11. Sync/export the latest accepted content back to the repo Markdown source path, excluding detailed Google Docs review markup except for a latest Doc link, latest observed revision, native version name/status, and brief history.
12. Inspect the repo diff for obvious conversion damage before reporting success.
13. Run:

```bash
bash .agent/skills/secretary/secretary.sh scan --incremental
```

14. Update local state, including processed comment IDs, observed revision IDs, native version name/status, and version label when available.
15. Tell the user:
    - Google Doc updated,
    - repo Markdown path updated,
    - native Google Docs version name/status,
    - number of comments addressed/unresolved,
    - Secretary refreshed,
    - any remaining questions.

---

## Rewrite Or Reversion Round

Use this path when the user asks to rewrite, simplify, re-version, remove outdated content, add graphs, or make the document easier to understand.

A rewrite/reversion round is incomplete until:

1. The Google Doc body reflects the new accepted version.
2. Outdated or user-denied suggestions are removed from the main recommendation.
3. A native Google Docs version is named for the new accepted version when tooling permits.
4. A `Version List` indexes the native version name/status, timestamp, purpose, and short notes for readers.
5. Rich content is added where useful: diagrams, charts, tables, callouts, or section links.
6. Google Docs-native headings/links/images are applied when available.
7. Local Markdown is updated to the latest accepted content only, with Google Doc link, latest revision, native version name/status, and brief history.
8. Local image assets used by Markdown are committed under the relevant docs/assets directory.
9. Local state records native version name/status and prewrite/final revision IDs when available.
10. Secretary indexing is refreshed.

If Google Docs named versions cannot be created by the available tools, say so briefly and rely on Google Docs automatic native version history. The in-document `Version List` and local revision state must point back to native history; they must not be described as the version authority.

---

## Sync Back To Markdown

Prefer the most reliable available path:

1. If the connector can export Google Docs as Markdown with structure preserved, use that.
2. Otherwise export HTML or DOCX and convert to Markdown with a deterministic converter.
3. Strip or exclude Google Docs review-response markup from the repo Markdown except a link to the latest Google Doc, latest observed revision ID, native version name/status, and brief history of processed rounds.
4. If conversion is lossy or includes unresolved comment footnotes, preserve the repo document's existing Markdown conventions by applying a targeted patch rather than replacing the whole file.
5. Always inspect the diff before final response.
6. Never leave the accepted latest content in Google Docs ahead of the repo Markdown after a processed round.

If the source is not Markdown, adapt the export path, but keep the same rule: the local durable artifact must be updated every round.

---

## Revision And Conflict Handling

When the Docs API exposes revision controls, use them:

- use a current revision ID for write control,
- if the revision is stale, reread the Doc and reapply edits,
- do not overwrite user edits blindly.

If a user adds new comments during processing:

1. Finish the current stable worklist.
2. Sync and run Secretary.
3. Report that new comments arrived and ask the user to say `process comments` again, or continue immediately if the user clearly wants continuous processing.

---

## Finalize Or Archive

If the user says `finalize`, `done`, or `archive`:

1. Run one normal process/sync round if unresolved comments or unsynced changes exist.
2. Confirm repo Markdown is current.
3. Run Secretary.
4. Move or label the Drive folder under `archived/` when the connector supports it.
5. Report the archived Doc link and repo path.

Do not wait for `finalize` to save normal comment rounds.

---

## Failure Modes

If Google auth is missing:

- ask the user to connect Google Drive,
- do not create manual token files,
- preserve any local draft work.

If export/sync fails:

- do not claim the round is complete,
- leave comments unresolved unless the user can see the edits in Google Docs and the failure is only repo sync,
- report the exact blocker and the safest next action.

If Secretary fails:

- report that the document was updated but the index is stale,
- include the failed command and high-level error,
- do not hide the failure.

---

## Final Response Shape

After every processed round, include:

- Google Doc link,
- repo Markdown path,
- native Google Docs version name/status and latest observed revision when available,
- comment count addressed and left open,
- Secretary status,
- remaining user action.

Keep the response short. The user should return to the Google Doc, not read a long process report.
