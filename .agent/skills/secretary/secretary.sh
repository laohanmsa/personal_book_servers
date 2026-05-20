#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SECRETARY_PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
export PROJECT_ROOT

python3 - "$@" <<'PY'
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(os.environ["PROJECT_ROOT"]).resolve()
INDEX_MD = ROOT / "project_document_index.md"
INDEX_JSON = ROOT / "project_document_index.json"
INDEX_TSV = ROOT / "project_document_index.tsv"
SNAPSHOT_TSV = ROOT / "project_document_snapshot.tsv"
HEALTH_FILE = ROOT / "project_context_health.md"
DEFAULT_TOP_K = 8

TEXT_EXTS = {".md", ".markdown", ".rst"}
ROOT_DOC_NAMES = {"AGENTS.md", "basicagents.md"}
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "target",
}


@dataclass
class Doc:
    component: str
    path: str
    title: str
    mtime: str
    summary: str
    doc_type: str
    freshness: str
    topic: str
    sha1: str
    size: int


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return clean_inline(match.group(1))
    return Path(fallback).stem.replace("_", " ").replace("-", " ").strip() or fallback


def clean_inline(value: str) -> str:
    value = re.sub(r"[`*_#>|]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def summary_from(text: str) -> str:
    lines: list[str] = []
    in_fm = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "---":
            in_fm = not in_fm
            continue
        if in_fm or not stripped or stripped.startswith("#"):
            continue
        lines.append(clean_inline(stripped))
        if len(" ".join(lines)) >= 220:
            break
    return " ".join(lines)[:240].strip()


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def topic_from(title: str) -> str:
    stop = {
        "readme",
        "guide",
        "reference",
        "report",
        "walkthrough",
        "notes",
        "documentation",
        "doc",
        "skill",
        "workflow",
        "rule",
    }
    words = [w for w in normalize(title).split() if w not in stop]
    return " ".join(words) or normalize(title)


def doc_type(path: str, title: str) -> str:
    haystack = f"{path} {title}".lower()
    if "rule" in haystack:
        return "rule"
    if "skill" in haystack:
        return "skill"
    if "workflow" in haystack:
        return "workflow"
    if "runbook" in haystack or "ops" in haystack:
        return "runbook"
    if "design" in haystack or "architecture" in haystack or "spec" in haystack:
        return "design"
    if "report" in haystack or "analysis" in haystack:
        return "report"
    if "test" in haystack:
        return "test"
    return "doc"


def component_for(path: str) -> str:
    parts = path.split("/")
    if path in ROOT_DOC_NAMES or len(parts) == 1:
        return "Root"
    if parts[:2] == [".agent", "rules"]:
        return "Agent Rules"
    if parts[:2] == [".agent", "workflows"]:
        return "Agent Workflows"
    if parts[:2] == [".agent", "references"]:
        return "Agent References"
    if parts[:2] == [".agent", "experiences"]:
        return "Agent Experiences"
    if parts[:2] == [".agent", "skills"] and len(parts) >= 3:
        return f"Skill: {parts[2]}"
    return parts[0]


def freshness_for(mtime: datetime) -> str:
    age_days = (datetime.now(timezone.utc) - mtime).days
    if age_days <= 30:
        return "fresh"
    if age_days <= 180:
        return "aging"
    return "stale"


def mtime_dt(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def is_doc(path: Path) -> bool:
    if not path.is_file():
        return False
    parts = set(path.relative_to(ROOT).parts)
    if parts & SKIP_DIRS:
        return False
    relative = rel(path)
    if path.name in ROOT_DOC_NAMES or path.name.lower().startswith("readme"):
        return True
    if path.suffix.lower() not in TEXT_EXTS:
        return False
    if relative.startswith((".agent/rules/", ".agent/workflows/", ".agent/references/", ".agent/experiences/")):
        return True
    if relative.startswith(".agent/skills/") and path.name == "SKILL.md":
        return True
    return relative.startswith(("docs/", "document/", "research/"))


def discover_docs() -> list[Doc]:
    docs: list[Doc] = []
    for path in sorted(ROOT.rglob("*")):
        if not is_doc(path):
            continue
        relative = rel(path)
        text = read_text(path)
        title = first_heading(text, relative)
        mtime = mtime_dt(path)
        docs.append(
            Doc(
                component=component_for(relative),
                path=relative,
                title=title,
                mtime=mtime.date().isoformat(),
                summary=summary_from(text),
                doc_type=doc_type(relative, title),
                freshness=freshness_for(mtime),
                topic=topic_from(title),
                sha1=sha1_file(path),
                size=path.stat().st_size,
            )
        )
    return docs


def snapshot_lines(docs: list[Doc]) -> list[str]:
    return [f"{doc.path}\t{doc.mtime}\t{doc.size}\t{doc.sha1}" for doc in docs]


def write_indexes(docs: list[Doc]) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lines = [
        "# Project Document Index",
        "",
        f"> Generated: {now}",
        f"> Documents: {len(docs)}",
        "",
    ]
    current_component = None
    for doc in docs:
        if doc.component != current_component:
            current_component = doc.component
            lines.extend(["", f"## {current_component}", ""])
            lines.append("| Title | Path | Type | Updated | Freshness |")
            lines.append("| --- | --- | --- | --- | --- |")
        lines.append(
            f"| {doc.title} | `{doc.path}` | {doc.doc_type} | {doc.mtime} | {doc.freshness} |"
        )
    INDEX_MD.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    INDEX_JSON.write_text(
        json.dumps(
            {"generated_at": now, "root": str(ROOT), "documents": [asdict(doc) for doc in docs]},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    INDEX_TSV.write_text(
        "component\tpath\ttitle\tmtime\tsummary\tdoc_type\tfreshness\ttopic\tsha1\tsize\n"
        + "\n".join(
            "\t".join(
                [
                    doc.component,
                    doc.path,
                    doc.title,
                    doc.mtime,
                    doc.summary,
                    doc.doc_type,
                    doc.freshness,
                    doc.topic,
                    doc.sha1,
                    str(doc.size),
                ]
            )
            for doc in docs
        )
        + "\n",
        encoding="utf-8",
    )
    SNAPSHOT_TSV.write_text("\n".join(snapshot_lines(docs)) + "\n", encoding="utf-8")


def scan(incremental: bool) -> int:
    docs = discover_docs()
    current = "\n".join(snapshot_lines(docs)) + "\n"
    if incremental and SNAPSHOT_TSV.exists() and SNAPSHOT_TSV.read_text(encoding="utf-8") == current:
        print("Secretary scan: no document changes detected.")
        return 0
    write_indexes(docs)
    print(f"Secretary scan: indexed {len(docs)} documents.")
    return 0


def load_docs() -> list[Doc]:
    if not INDEX_JSON.exists():
        scan(False)
    payload = json.loads(INDEX_JSON.read_text(encoding="utf-8"))
    return [Doc(**item) for item in payload.get("documents", [])]


def query_words(query: str) -> list[str]:
    return [w for w in normalize(query).split() if len(w) > 1]


def score_doc(doc: Doc, words: list[str]) -> tuple[int, str]:
    haystacks = {
        "title": normalize(doc.title),
        "path": normalize(doc.path),
        "summary": normalize(doc.summary),
        "component": normalize(doc.component),
        "type": normalize(doc.doc_type),
        "topic": normalize(doc.topic),
    }
    score = 0
    reasons: list[str] = []
    weights = {"title": 8, "path": 5, "summary": 3, "component": 4, "type": 2, "topic": 6}
    for word in words:
        for field, text in haystacks.items():
            if word in text.split() or word in text:
                score += weights[field]
                reasons.append(f"{word}:{field}")
    if doc.freshness == "fresh":
        score += 2
    elif doc.freshness == "stale":
        score -= 1
    return score, ", ".join(reasons[:8]) or "low lexical match"


def ranked(query: str, top_k: int, component: str | None, doc_type_filter: str | None) -> list[tuple[int, str, Doc]]:
    words = query_words(query)
    results: list[tuple[int, str, Doc]] = []
    for doc in load_docs():
        if component and component.lower() not in doc.component.lower():
            continue
        if doc_type_filter and doc_type_filter.lower() != doc.doc_type.lower():
            continue
        score, reason = score_doc(doc, words)
        if score > 0:
            results.append((score, reason, doc))
    results.sort(key=lambda item: (-item[0], item[2].component, item[2].path))
    return results[:top_k]


def emit_sources_json(query: str, level: str, rows: list[tuple[int, str, Doc]]) -> None:
    print(
        json.dumps(
            {
                "query": query,
                "level": level,
                "summary": f"Found {len(rows)} matching docs for {query!r}.",
                "coverage": "ok" if rows else "none",
                "sources": [
                    {
                        "path": doc.path,
                        "title": doc.title,
                        "score": score,
                        "why_matched": reason,
                        "freshness": doc.freshness,
                        "component": doc.component,
                        "doc_type": doc.doc_type,
                        "mtime": doc.mtime,
                    }
                    for score, reason, doc in rows
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def ask(args: argparse.Namespace) -> int:
    rows = ranked(args.query, args.top_k, args.component, args.type)
    if args.json:
        emit_sources_json(args.query, args.level, rows)
        return 0
    print(f"Secretary ask: {args.query!r} ({args.level})")
    if not rows:
        print("No matching docs found. Run scan or broaden the query.")
        return 1
    for index, (score, reason, doc) in enumerate(rows, start=1):
        print(f"{index}. {doc.title} [{doc.component}/{doc.doc_type}] score={score}")
        print(f"   path: {doc.path}")
        print(f"   why: {reason}")
        if args.level in {"L2", "L3"} and doc.summary:
            print(f"   summary: {doc.summary}")
    return 0


def pack(args: argparse.Namespace) -> int:
    rows = ranked(args.query, args.top_k, args.component, args.type)
    if args.json:
        groups = {
            "must_read": rows[:3],
            "supporting": rows[3:8],
            "historical": rows[8:],
        }
        print(
            json.dumps(
                {
                    "query": args.query,
                    "level": args.level,
                    "groups": {
                        name: [
                            {
                                "path": doc.path,
                                "title": doc.title,
                                "score": score,
                                "why_matched": reason,
                                "component": doc.component,
                                "doc_type": doc.doc_type,
                                "freshness": doc.freshness,
                            }
                            for score, reason, doc in values
                        ]
                        for name, values in groups.items()
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    print(f"Secretary pack: {args.query!r}")
    for name, values in (("must_read", rows[:3]), ("supporting", rows[3:8]), ("historical", rows[8:])):
        print(f"\n## {name}")
        if not values:
            print("- none")
            continue
        for score, reason, doc in values:
            print(f"- {doc.path} | {doc.title} | score={score} | {reason}")
    return 0 if rows else 1


def doctor() -> tuple[int, str]:
    if not INDEX_JSON.exists():
        return 1, "index_status: missing\nrecommendation: run scan\n"
    docs = load_docs()
    missing = [doc.path for doc in docs if not (ROOT / doc.path).exists()]
    stale = [doc for doc in docs if doc.freshness == "stale"]
    status = "ok" if not missing else "warn"
    report = "\n".join(
        [
            f"index_status: {status}",
            f"document_count: {len(docs)}",
            f"stale_count: {len(stale)}",
            f"missing_indexed_paths: {len(missing)}",
            *(f"missing: {path}" for path in missing[:20]),
        ]
    )
    return (0 if not missing else 1), report + "\n"


def maintain(args: argparse.Namespace) -> int:
    scan(True)
    code, report = doctor()
    HEALTH_FILE.write_text("# Project Context Health\n\n```text\n" + report + "```\n", encoding="utf-8")
    print(report, end="")
    print(f"health_file: {HEALTH_FILE.relative_to(ROOT).as_posix()}")
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="secretary.sh")
    sub = parser.add_subparsers(dest="mode")

    scan_p = sub.add_parser("scan")
    scan_p.add_argument("--incremental", action="store_true")

    for name in ("ask", "pack"):
        p = sub.add_parser(name)
        p.add_argument("query")
        p.add_argument("--level", choices=["L0", "L1", "L2", "L3"], default=("L2" if name == "pack" else "L1"))
        p.add_argument("--json", action="store_true")
        p.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
        p.add_argument("--component")
        p.add_argument("--type")

    sub.add_parser("doctor")
    sub.add_parser("maintain")
    return parser


def main(argv: list[str]) -> int:
    if not argv:
        argv = ["scan"]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.mode == "scan":
        return scan(args.incremental)
    if args.mode == "ask":
        return ask(args)
    if args.mode == "pack":
        return pack(args)
    if args.mode == "doctor":
        code, report = doctor()
        print(report, end="")
        return code
    if args.mode == "maintain":
        return maintain(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
PY
