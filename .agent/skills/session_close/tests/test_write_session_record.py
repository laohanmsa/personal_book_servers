from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "write_session_record.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("session_close_writer", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_write_session_record_creates_dated_markdown(tmp_path):
    module = load_module()
    payload = {
        "session_name": "Debug Parser Skill",
        "generated_at": "2026-03-26T13:52:00+08:00",
        "messages": [
            {"role": "user", "content": "run parser verification now"},
            {"role": "assistant", "summary": "ran the focused parser verification"},
        ],
        "docs": {
            "status": "reindexed",
            "paths": ["docs/task_briefs/2026-03-26_session-close-skill.md"],
            "secretary_reindexed": True,
            "index_verified": True,
        },
        "git": {
            "branch": "codex/session-close-skill",
            "head": "abc1234",
            "status": "dirty",
            "action": "left changes on the task branch for review",
        },
        "closing_note": "close loop completed",
    }
    input_path = tmp_path / "payload.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = module.main(
        [
            "--input",
            str(input_path),
            "--output-root",
            str(tmp_path / "user_sessions"),
        ]
    )

    assert exit_code == 0
    output_path = tmp_path / "user_sessions" / "2026-03-26" / "debug-parser-skill.md"
    assert output_path.exists()

    text = output_path.read_text(encoding="utf-8")
    assert "# User Session: Debug Parser Skill" in text
    assert "```text\nrun parser verification now\n```" in text
    assert "- Brief reply: ran the focused parser verification" in text
    assert "- Path: `docs/task_briefs/2026-03-26_session-close-skill.md`" in text
    assert "- Branch: `codex/session-close-skill`" in text
    assert "- Head: `abc1234`" in text
    assert "- close loop completed" in text


def test_assistant_content_falls_back_to_short_summary():
    module = load_module()
    long_reply = "Detailed explanation " * 40
    record = module.normalize_payload(
        {
            "session_name": "Long Reply Session",
            "generated_at": "2026-03-26T13:52:00+08:00",
            "messages": [
                {"role": "user", "content": "close session"},
                {"role": "assistant", "content": long_reply},
            ],
        }
    )

    text = module.render_session_markdown(record)

    assert "close session" in text
    assert "- Brief reply: Detailed explanation" in text
    assert long_reply not in text
    assert "..." in text


def test_normalize_payload_rejects_empty_user_message():
    module = load_module()

    with pytest.raises(ValueError, match="non-empty content"):
        module.normalize_payload(
            {
                "session_name": "bad session",
                "messages": [{"role": "user", "content": "   "}],
            }
        )
