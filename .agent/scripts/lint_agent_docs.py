#!/usr/bin/env python3
"""Lint repo-local .agent docs/scripts for reusable harness quality.

The linter is non-invasive: it reads files, prints findings, and exits non-zero
on errors.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


STALE_TOOL_NAMES = [
    "notify_user",
    "view_file",
    "list_dir",
    "read_url_content",
    "search_web",
    "render_diffs",
    "replace_file_content",
    "run_command",
]

TEXT_EXTS = {".md", ".sh", ".py", ".txt", ".yaml", ".yml"}
FILE_URI_RE = re.compile(r"file://")
ABS_USER_PATH_RE = re.compile(r"/Users/[^\\s`'\"<>]+")
SELF_SCRIPT = Path(__file__).resolve()


@dataclass
class Finding:
    level: str
    file: Path
    line: int
    message: str

    def render(self, root: Path) -> str:
        return f"[{self.level}] {self.file.relative_to(root)}:{self.line}: {self.message}"


def iter_agent_files(agent_dir: Path) -> Iterable[Path]:
    for path in agent_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTS:
            yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    frontmatter: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    return frontmatter


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def lint_stale_tools(agent_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    pattern = re.compile(r"\b(" + "|".join(re.escape(name) for name in STALE_TOOL_NAMES) + r")\b")
    for path in iter_agent_files(agent_dir):
        if path.resolve() == SELF_SCRIPT:
            continue
        text = read_text(path)
        for match in pattern.finditer(text):
            findings.append(
                Finding("ERROR", path, line_for_offset(text, match.start()), f"stale tool reference `{match.group(1)}`")
            )
    return findings


def lint_file_uris(agent_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_agent_files(agent_dir):
        if path.resolve() == SELF_SCRIPT:
            continue
        text = read_text(path)
        for match in FILE_URI_RE.finditer(text):
            findings.append(Finding("ERROR", path, line_for_offset(text, match.start()), "avoid file:// links; use repo-relative paths"))
    return findings


def lint_absolute_user_paths(agent_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_agent_files(agent_dir):
        if path.resolve() == SELF_SCRIPT:
            continue
        text = read_text(path)
        for match in ABS_USER_PATH_RE.finditer(text):
            findings.append(
                Finding("WARN", path, line_for_offset(text, match.start()), f"absolute user path `{match.group(0)}` reduces portability")
            )
    return findings


def lint_frontmatter(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    checks = [
        (root / ".agent" / "workflows", "*.md", {"description", "category", "status", "safety"}),
        (root / ".agent" / "rules", "*.md", {"category", "status", "safety"}),
        (root / ".agent" / "experiences", "*.md", {"category", "status", "safety"}),
    ]
    for directory, glob, required in checks:
        if not directory.exists():
            continue
        for path in sorted(directory.glob(glob)):
            fm = parse_frontmatter(read_text(path))
            if fm is None:
                findings.append(Finding("ERROR", path, 1, "missing or malformed frontmatter"))
                continue
            for key in sorted(required - set(fm)):
                findings.append(Finding("ERROR", path, 1, f"frontmatter missing `{key}`"))

    skills_dir = root / ".agent" / "skills"
    if skills_dir.exists():
        for path in sorted(skills_dir.glob("*/SKILL.md")):
            fm = parse_frontmatter(read_text(path))
            if fm is None:
                findings.append(Finding("ERROR", path, 1, "missing or malformed frontmatter"))
                continue
            for key in sorted({"name", "description", "category", "status", "safety"} - set(fm)):
                findings.append(Finding("ERROR", path, 1, f"frontmatter missing `{key}`"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint .agent harness files")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--strict-warnings", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    agent_dir = root / ".agent"
    if not agent_dir.exists():
        print(f"ERROR: .agent directory not found under {root}", file=sys.stderr)
        return 2

    checks = [
        ("stale tools", lint_stale_tools(agent_dir)),
        ("file uris", lint_file_uris(agent_dir)),
        ("absolute user paths", lint_absolute_user_paths(agent_dir)),
        ("frontmatter", lint_frontmatter(root)),
    ]

    errors = 0
    warnings = 0
    for name, findings in checks:
        if not findings:
            print(f"[OK] {name}")
            continue
        print(f"[FAIL] {name} ({len(findings)})")
        for finding in findings:
            print("  " + finding.render(root))
            if finding.level == "ERROR":
                errors += 1
            else:
                warnings += 1

    print(f"Summary: {errors} error(s), {warnings} warning(s)")
    if errors or (warnings and args.strict_warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
