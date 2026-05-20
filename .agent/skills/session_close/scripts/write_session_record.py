from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_OUTPUT_ROOT = Path(".agent/user_sessions")
DEFAULT_TIMEZONE = ZoneInfo("Asia/Shanghai")
MAX_ASSISTANT_SUMMARY_CHARS = 240


def slugify_session_name(value: str) -> str:
    normalized = " ".join(str(value).strip().split())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "session"


def shorten_assistant_reply(text: str, max_chars: int = MAX_ASSISTANT_SUMMARY_CHARS) -> str:
    normalized = " ".join(str(text).strip().split())
    if not normalized:
        return "No reply recorded."
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


def yes_no_unknown(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unknown"


class SessionRecordWriter:
    def __init__(self, output_root: Path = DEFAULT_OUTPUT_ROOT) -> None:
        self.output_root = output_root

    def normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")

        generated_at = payload.get("generated_at")
        if generated_at:
            generated_label = str(generated_at)
            session_date = payload.get("session_date") or generated_label[:10]
        else:
            now = datetime.now(DEFAULT_TIMEZONE)
            generated_label = now.isoformat(timespec="seconds")
            session_date = payload.get("session_date") or now.date().isoformat()

        raw_docs = payload.get("docs") if isinstance(payload.get("docs"), dict) else {}
        raw_git = payload.get("git") if isinstance(payload.get("git"), dict) else {}
        session_title = str(
            payload.get("session_name")
            or payload.get("topic")
            or raw_git.get("branch")
            or "session"
        ).strip()
        session_slug = slugify_session_name(session_title)

        raw_messages = payload.get("messages")
        if not isinstance(raw_messages, list) or not raw_messages:
            raise ValueError("payload.messages must be a non-empty list")

        messages: list[dict[str, str]] = []
        for index, raw_message in enumerate(raw_messages, start=1):
            if not isinstance(raw_message, dict):
                raise ValueError(f"message {index} must be an object")

            role = str(raw_message.get("role", "")).strip().lower()
            if role not in {"user", "assistant"}:
                raise ValueError(f"message {index} has unsupported role {role!r}")

            if role == "user":
                content = str(raw_message.get("content", "")).strip()
                if not content:
                    raise ValueError(f"user message {index} must have non-empty content")
                messages.append({"role": "user", "content": content})
                continue

            summary_source = (
                raw_message.get("summary")
                or raw_message.get("brief")
                or raw_message.get("content")
                or ""
            )
            messages.append(
                {
                    "role": "assistant",
                    "summary": shorten_assistant_reply(str(summary_source)),
                }
            )

        doc_paths = raw_docs.get("paths") if isinstance(raw_docs.get("paths"), list) else []

        return {
            "session_title": session_title or session_slug,
            "session_slug": session_slug,
            "session_date": str(session_date),
            "generated_at": generated_label,
            "messages": messages,
            "docs": {
                "status": str(raw_docs.get("status", "not recorded")),
                "paths": [str(path) for path in doc_paths],
                "secretary_reindexed": raw_docs.get("secretary_reindexed"),
                "index_verified": raw_docs.get("index_verified"),
                "note": str(raw_docs.get("note", "")).strip(),
            },
            "git": {
                "branch": str(raw_git.get("branch", "not recorded")).strip() or "not recorded",
                "head": str(raw_git.get("head", "")).strip(),
                "status": str(raw_git.get("status", "not recorded")).strip() or "not recorded",
                "action": str(raw_git.get("action", "")).strip(),
                "blocker": str(raw_git.get("blocker", "")).strip(),
            },
            "closing_note": str(payload.get("closing_note", "")).strip(),
        }

    def render_session_markdown(self, record: dict[str, Any]) -> str:
        lines = [
            f"# User Session: {record['session_title']}",
            "",
            f"> Generated: {record['generated_at']}",
            f"> Session date: {record['session_date']}",
            f"> Session slug: `{record['session_slug']}`",
            "",
            "## Transcript",
            "",
        ]

        for index, message in enumerate(record["messages"], start=1):
            if message["role"] == "user":
                lines.extend(
                    [
                        f"### {index}. User",
                        "",
                        "```text",
                        message["content"],
                        "```",
                        "",
                    ]
                )
                continue

            lines.extend(
                [
                    f"### {index}. Agent",
                    "",
                    f"- Brief reply: {message['summary']}",
                    "",
                ]
            )

        docs = record["docs"]
        lines.extend(
            [
                "## Closure",
                "",
                "### Docs",
                "",
                f"- Status: {docs['status']}",
                f"- Secretary reindexed: {yes_no_unknown(docs['secretary_reindexed'])}",
                f"- Index verified: {yes_no_unknown(docs['index_verified'])}",
            ]
        )
        for path in docs["paths"]:
            lines.append(f"- Path: `{path}`")
        if docs["note"]:
            lines.append(f"- Note: {docs['note']}")

        git = record["git"]
        lines.extend(
            [
                "",
                "### Git",
                "",
                f"- Branch: `{git['branch']}`",
                f"- Status: {git['status']}",
            ]
        )
        if git["head"]:
            lines.append(f"- Head: `{git['head']}`")
        if git["action"]:
            lines.append(f"- Action: {git['action']}")
        if git["blocker"]:
            lines.append(f"- Blocker: {git['blocker']}")

        if record["closing_note"]:
            lines.extend(
                [
                    "",
                    "## Closing Note",
                    "",
                    f"- {record['closing_note']}",
                ]
            )

        return "\n".join(lines).rstrip() + "\n"

    def write(self, payload: dict[str, Any]) -> Path:
        record = self.normalize_payload(payload)
        output_path = build_output_path(
            self.output_root,
            record["session_date"],
            record["session_slug"],
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.render_session_markdown(record), encoding="utf-8")
        return output_path


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return SessionRecordWriter().normalize_payload(payload)


def build_output_path(output_root: Path, session_date: str, session_slug: str) -> Path:
    return output_root / session_date / f"{session_slug}.md"


def render_session_markdown(record: dict[str, Any]) -> str:
    return SessionRecordWriter().render_session_markdown(record)


def write_session_record(payload: dict[str, Any], output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    return SessionRecordWriter(output_root).write(payload)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a close-session archive markdown file.")
    parser.add_argument("--input", required=True, help="Path to the JSON payload.")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root directory for session archives.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output_path = SessionRecordWriter(Path(args.output_root)).write(payload)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
