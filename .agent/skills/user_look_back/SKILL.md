---
name: User Look Back
description: Analyze recent user activity over a configurable lookback window, group inputs by theme, and produce a concise report with open questions and follow-up actions.
category: reflection
status: active
safety: reads-only
---

# User Look Back

Use this skill when the user asks what they have been working on, wants a daily
or weekly retrospective, or needs strategic context before planning.

## Inputs

| Parameter | Default | Description |
| --- | --- | --- |
| `window` | 24h | Lookback window such as `12h`, `24h`, `48h`, or `7d`. |
| `focus` | all | Optional topic filter. |

## Process

1. Determine `window_start` and `window_end` from the current local time.
2. Collect available conversation summaries and current-session user messages.
3. Group sessions into 2-5 themes using names that fit the actual work.
4. For each theme, identify goal, status, accomplishments, blockers, and done signal.
5. Write a report to `docs/user_lookbacks/user_lookback_<YYYY-MM-DD_HH>.md` when the repo has a docs area; otherwise provide the report in chat.
6. Run Secretary indexing after saving a durable report.

## Report Shape

Use:

- session log,
- theme analysis,
- strategic synthesis,
- open questions,
- suggested next steps.

Use repo-relative paths in Markdown links. Do not use local file URI links.

## Rules

1. Use exact user text when available; label summarized prior conversations as summarized.
2. Do not invent outcomes for conversations that only have partial metadata.
3. Make the most important open question visible near the top.
4. Keep recommendations tied to the user's actual stated goals.
