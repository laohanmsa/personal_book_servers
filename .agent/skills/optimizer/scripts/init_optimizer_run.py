#!/usr/bin/env python3
"""Create optimizer run scaffolding with stable tables and templates."""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


LOG_FORMAT = "%(levelname)s %(message)s"


@dataclass(frozen=True)
class OptimizerRunConfig:
    slug: str
    target: str
    goal: str
    primary_metric: str
    guard_metrics: List[str]
    secondary_metrics: List[str]
    benchmark_command: str
    verify_command: str
    rounds: int
    root: Path
    output_dir: Optional[Path]
    force: bool


class OptimizerRunInitializer:
    """Create the standard optimizer run files without overwriting by default."""

    def __init__(self, config: OptimizerRunConfig) -> None:
        self.config = config
        self.created_files: List[Path] = []
        self.skipped_files: List[Path] = []

    def run(self) -> Path:
        run_dir = self._run_dir()
        logging.info("Creating optimizer run scaffold at %s", run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)

        self._write_file(run_dir / "optimizer_brief.md", self._brief_content(run_dir))
        self._write_file(run_dir / "ideas.tsv", self._ideas_content())
        self._write_file(run_dir / "results.tsv", self._results_content())
        self._write_file(run_dir / "report.md", self._report_content())

        logging.info(
            "Optimizer scaffold complete: created=%d skipped=%d",
            len(self.created_files),
            len(self.skipped_files),
        )
        return run_dir

    def _run_dir(self) -> Path:
        if self.config.output_dir is not None:
            return self.config.output_dir.expanduser().resolve()

        today = dt.datetime.now(dt.timezone.utc).date().isoformat()
        return (self.config.root / "docs" / "optimizer_runs" / f"{today}_{self.config.slug}").resolve()

    def _write_file(self, path: Path, content: str) -> None:
        if path.exists() and not self.config.force:
            logging.info("Keeping existing file: %s", path)
            self.skipped_files.append(path)
            return

        path.write_text(content, encoding="utf-8")
        self.created_files.append(path)
        logging.info("Wrote %s", path)

    def _brief_content(self, run_dir: Path) -> str:
        timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
        guard_metrics = format_list(self.config.guard_metrics)
        secondary_metrics = format_list(self.config.secondary_metrics)
        return f"""# Optimizer Brief: {self.config.slug}

> Timestamp: {timestamp}
> Run directory: `{run_dir}`

## Goal

{self.config.goal}

## Target

- `{self.config.target}`

## Scope

### In Scope

- Optimize the target implementation.
- Preserve the benchmark, oracle, fixtures, labels, and metric extraction unless the user explicitly authorizes harness work.

### Out Of Scope

- Production data mutation.
- Live external mutations, production data changes, account changes, billing actions, or credential changes without explicit authorization.
- Unrelated refactors outside the target and required call sites.

## Metrics

- **Primary**: {self.config.primary_metric}
- **Guards**:
{guard_metrics}
- **Secondary**:
{secondary_metrics}

## Baseline Plan

- **Benchmark command**: `{self.config.benchmark_command}`
- **Verify command**: `{self.config.verify_command}`
- **Baseline experiment id**: `baseline`
- **Noise rule**: repeat enough times to distinguish real improvement from run-to-run noise.

## Round Plan

- **Default rounds**: {self.config.rounds}
- **Experiment rule**: one idea per experiment.
- **Acceptance rule**: guards pass, primary metric improves beyond the noise rule, and secondary regressions stay within accepted limits.

## Review Path

- Check for hidden harness changes.
- Check raw metrics before accepting any result.
- Use subagent review only when current tool policy and user authorization allow it.
"""

    def _ideas_content(self) -> str:
        return (
            "idea_id\tround\tstatus\thypothesis\texpected_metric_effect\t"
            "risk\ttouched_paths\tnotes\n"
        )

    def _results_content(self) -> str:
        return (
            "experiment_id\tround\tidea_id\tstatus\tguard_status\tprimary_metric\t"
            "secondary_metrics\tbenchmark_command\tverify_command\tevidence_path\tdecision\tnotes\n"
            f"baseline\t0\tbaseline\tpending\tpending\t\t\t{self.config.benchmark_command}\t"
            f"{self.config.verify_command}\t\tbaseline\tCapture current implementation before edits.\n"
        )

    def _report_content(self) -> str:
        return f"""# Optimizer Report: {self.config.slug}

## Objective

{self.config.goal}

## Target

- `{self.config.target}`

## Baseline

Pending.

## Best Result

Pending.

## Result Table

Populate from `results.tsv`.

## Kept Changes

Pending.

## Discarded Experiments

Pending.

## Algorithm Explanation

Pending.

## Validation Evidence

- Benchmark command: `{self.config.benchmark_command}`
- Verify command: `{self.config.verify_command}`

## Risks And Mitigations

Pending.

## Next Ideas

Pending.
"""


def normalize_slug(value: str) -> str:
    lowered = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "-", lowered)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-_")
    if not normalized:
        raise ValueError("slug must contain at least one letter or digit")
    return normalized


def format_list(values: Iterable[str]) -> str:
    items = [value.strip() for value in values if value.strip()]
    if not items:
        return "- None specified yet."
    return "\n".join(f"- {item}" for item in items)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create optimizer run scaffolding.")
    parser.add_argument("--slug", required=True, help="Short run slug; normalized to safe lowercase.")
    parser.add_argument("--target", required=True, help="Function, module, path, or symbol to optimize.")
    parser.add_argument("--goal", required=True, help="User-facing optimization objective.")
    parser.add_argument("--primary-metric", required=True, help="Primary metric and direction.")
    parser.add_argument("--guard-metric", action="append", default=[], help="Guard metric; repeatable.")
    parser.add_argument("--secondary-metric", action="append", default=[], help="Secondary metric; repeatable.")
    parser.add_argument("--benchmark-command", default="TODO", help="Command that measures optimization metrics.")
    parser.add_argument("--verify-command", default="TODO", help="Command that proves correctness.")
    parser.add_argument("--rounds", type=int, default=3, help="Planned optimization rounds.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--output-dir", help="Explicit output directory. Overrides default docs path.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files.")
    return parser


def parse_args(argv: Optional[List[str]] = None) -> OptimizerRunConfig:
    args = build_parser().parse_args(argv)
    if args.rounds < 1:
        raise ValueError("--rounds must be at least 1")

    root = Path(args.root).expanduser().resolve()
    output_dir = Path(args.output_dir) if args.output_dir else None
    return OptimizerRunConfig(
        slug=normalize_slug(args.slug),
        target=args.target,
        goal=args.goal,
        primary_metric=args.primary_metric,
        guard_metrics=args.guard_metric,
        secondary_metrics=args.secondary_metric,
        benchmark_command=args.benchmark_command,
        verify_command=args.verify_command,
        rounds=args.rounds,
        root=root,
        output_dir=output_dir,
        force=args.force,
    )


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    try:
        config = parse_args(argv)
        run_dir = OptimizerRunInitializer(config).run()
    except ValueError as exc:
        logging.error("%s", exc)
        return 2

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
