#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Aggregate structured eval sidecars from ~/.agents/skills/**/evals/*.json.

Tiny operator-facing reporting tool.

Examples:
  python3 ~/.agents/services/evals.py summary
  python3 ~/.agents/services/evals.py summary --skill video-pipeline
  python3 ~/.agents/services/evals.py issues --severity high
  python3 ~/.agents/services/evals.py recommendations --skill youtube-upload
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SKILLS_DIR = Path.home() / ".agents" / "skills"


@dataclass
class EvalRecord:
    path: Path
    data: dict[str, Any]

    @property
    def skill(self) -> str:
        return str(self.data.get("skill") or "unknown")

    @property
    def eval_type(self) -> str:
        return str(self.data.get("eval_type") or "unknown")

    @property
    def outcome(self) -> str:
        return str((self.data.get("summary") or {}).get("outcome") or "unknown")

    @property
    def date(self) -> str:
        return str(self.data.get("date") or "unknown")


def find_eval_files(skills_dir: Path) -> list[Path]:
    return sorted(skills_dir.glob("**/evals/*.json"))


def load_records(skills_dir: Path) -> tuple[list[EvalRecord], list[tuple[Path, str]]]:
    records: list[EvalRecord] = []
    errors: list[tuple[Path, str]] = []
    for path in find_eval_files(skills_dir):
        try:
            data = json.loads(path.read_text())
            if not isinstance(data, dict):
                raise ValueError("root must be a JSON object")
            records.append(EvalRecord(path=path, data=data))
        except Exception as e:  # noqa: BLE001
            errors.append((path, str(e)))
    return records, errors


def filter_records(records: Iterable[EvalRecord], skill: str | None = None, eval_type: str | None = None) -> list[EvalRecord]:
    out = list(records)
    if skill:
        out = [r for r in out if r.skill == skill]
    if eval_type:
        out = [r for r in out if r.eval_type == eval_type]
    return out


def relative_to_home(path: Path) -> str:
    try:
        return str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)


def print_table(rows: list[tuple[str, str]], left_header: str, right_header: str) -> None:
    if not rows:
        print("  (none)")
        return
    left_width = max(len(left_header), *(len(r[0]) for r in rows))
    right_width = max(len(right_header), *(len(r[1]) for r in rows))
    print(f"  {left_header:<{left_width}}  {right_header:>{right_width}}")
    print(f"  {'-' * left_width}  {'-' * right_width}")
    for left, right in rows:
        print(f"  {left:<{left_width}}  {right:>{right_width}}")


def summarize(records: list[EvalRecord], limit: int = 10) -> dict[str, Any]:
    by_skill = Counter(r.skill for r in records)
    by_type = Counter(r.eval_type for r in records)
    by_outcome = Counter(r.outcome for r in records)
    dates = sorted(r.date for r in records if r.date != "unknown")

    issue_categories = Counter()
    high_severity_issue_categories = Counter()
    recommendation_targets = Counter()
    recommendation_actions = Counter()
    deviation_steps = Counter()
    deviation_severities = Counter()
    feedback_categories = Counter()

    for record in records:
        for issue in record.data.get("issues", []):
            if not isinstance(issue, dict):
                continue
            category = str(issue.get("category") or "unknown")
            severity = str(issue.get("severity") or "unknown")
            issue_categories[category] += 1
            if severity == "high":
                high_severity_issue_categories[category] += 1

        for rec in record.data.get("recommendations", []):
            if not isinstance(rec, dict):
                continue
            target = str(rec.get("target") or "unknown")
            action = str(rec.get("action") or "unknown")
            recommendation_targets[target] += 1
            recommendation_actions[action] += 1

        process = record.data.get("process_adherence") or {}
        for dev in process.get("deviations", []):
            if not isinstance(dev, dict):
                continue
            deviation_steps[str(dev.get("step") or "unknown")] += 1
            deviation_severities[str(dev.get("severity") or "unknown")] += 1

        for hook in record.data.get("feedback_hooks", []):
            if not isinstance(hook, dict):
                continue
            feedback_categories[str(hook.get("category") or "unknown")] += 1

    return {
        "total_evals": len(records),
        "skills_covered": len(by_skill),
        "date_range": {
            "first": dates[0] if dates else None,
            "last": dates[-1] if dates else None,
        },
        "by_skill": dict(by_skill.most_common()),
        "by_type": dict(by_type.most_common()),
        "by_outcome": dict(by_outcome.most_common()),
        "top_issue_categories": dict(issue_categories.most_common(limit)),
        "top_high_severity_issue_categories": dict(high_severity_issue_categories.most_common(limit)),
        "top_recommendation_targets": dict(recommendation_targets.most_common(limit)),
        "top_recommendation_actions": dict(recommendation_actions.most_common(limit)),
        "top_deviation_steps": dict(deviation_steps.most_common(limit)),
        "deviation_severities": dict(deviation_severities.most_common()),
        "top_feedback_hook_categories": dict(feedback_categories.most_common(limit)),
        "eval_paths": [relative_to_home(r.path) for r in sorted(records, key=lambda r: (r.date, r.skill, str(r.path)))],
    }


def collect_issue_rows(records: list[EvalRecord], severity: str | None = None) -> tuple[list[tuple[str, str]], list[dict[str, Any]]]:
    grouped = Counter()
    detailed: list[dict[str, Any]] = []
    for r in records:
        for issue in r.data.get("issues", []):
            if not isinstance(issue, dict):
                continue
            issue_severity = str(issue.get("severity") or "unknown")
            if severity and issue_severity != severity:
                continue
            category = str(issue.get("category") or "unknown")
            grouped[category] += 1
            detailed.append(
                {
                    "skill": r.skill,
                    "date": r.date,
                    "severity": issue_severity,
                    "category": category,
                    "title": issue.get("title") or "(untitled)",
                    "path": relative_to_home(r.path),
                }
            )
    rows = [(k, str(v)) for k, v in grouped.most_common()]
    return rows, detailed


def collect_recommendation_rows(records: list[EvalRecord]) -> tuple[list[tuple[str, str]], list[dict[str, Any]]]:
    grouped = Counter()
    detailed: list[dict[str, Any]] = []
    for r in records:
        for rec in r.data.get("recommendations", []):
            if not isinstance(rec, dict):
                continue
            target = str(rec.get("target") or "unknown")
            action = str(rec.get("action") or "unknown")
            grouped[target] += 1
            detailed.append(
                {
                    "skill": r.skill,
                    "date": r.date,
                    "priority": rec.get("priority") or "?",
                    "scope": rec.get("scope") or "?",
                    "target": target,
                    "action": action,
                    "path": relative_to_home(r.path),
                }
            )
    rows = [(k, str(v)) for k, v in grouped.most_common()]
    return rows, detailed


def cmd_summary(args: argparse.Namespace) -> int:
    records, errors = load_records(Path(args.skills_dir).expanduser())
    records = filter_records(records, skill=args.skill, eval_type=args.eval_type)
    payload = summarize(records, limit=args.limit)

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print("Eval Summary")
    print(f"  total evals:     {payload['total_evals']}")
    print(f"  skills covered:  {payload['skills_covered']}")
    print(f"  date range:      {payload['date_range']['first']} → {payload['date_range']['last']}")
    if args.skill:
        print(f"  filtered skill:  {args.skill}")
    if args.eval_type:
        print(f"  filtered type:   {args.eval_type}")
    if errors:
        print(f"  load errors:     {len(errors)}")

    print("\nBy skill")
    print_table([(k, str(v)) for k, v in payload["by_skill"].items()], "Skill", "Evals")

    print("\nBy eval type")
    print_table([(k, str(v)) for k, v in payload["by_type"].items()], "Type", "Count")

    print("\nBy outcome")
    print_table([(k, str(v)) for k, v in payload["by_outcome"].items()], "Outcome", "Count")

    print("\nTop issue categories")
    print_table([(k, str(v)) for k, v in payload["top_issue_categories"].items()], "Category", "Count")

    print("\nHigh-severity issue categories")
    print_table([(k, str(v)) for k, v in payload["top_high_severity_issue_categories"].items()], "Category", "Count")

    print("\nTop recommendation targets")
    print_table([(k, str(v)) for k, v in payload["top_recommendation_targets"].items()], "Target", "Count")

    print("\nProcess deviation severities")
    print_table([(k, str(v)) for k, v in payload["deviation_severities"].items()], "Severity", "Count")

    print("\nTop feedback-hook categories")
    print_table([(k, str(v)) for k, v in payload["top_feedback_hook_categories"].items()], "Category", "Count")

    if args.show_paths:
        print("\nEval files")
        for path in payload["eval_paths"]:
            print(f"  - {path}")

    return 0


def cmd_issues(args: argparse.Namespace) -> int:
    records, _errors = load_records(Path(args.skills_dir).expanduser())
    records = filter_records(records, skill=args.skill, eval_type=args.eval_type)
    rows, detailed = collect_issue_rows(records, severity=args.severity)

    if args.json:
        print(json.dumps({"grouped": {k: int(v) for k, v in rows}, "issues": detailed}, indent=2))
        return 0

    title = "Issue Categories"
    if args.severity:
        title += f" (severity={args.severity})"
    print(title)
    print_table(rows[: args.limit], "Category", "Count")

    print("\nExamples")
    shown = 0
    for issue in detailed:
        if shown >= args.limit:
            break
        print(f"  - [{issue['severity']}] {issue['category']} — {issue['title']} ({issue['skill']}, {issue['date']})")
        shown += 1
    if shown == 0:
        print("  (none)")
    return 0


def cmd_recommendations(args: argparse.Namespace) -> int:
    records, _errors = load_records(Path(args.skills_dir).expanduser())
    records = filter_records(records, skill=args.skill, eval_type=args.eval_type)
    rows, detailed = collect_recommendation_rows(records)

    if args.json:
        print(json.dumps({"grouped": {k: int(v) for k, v in rows}, "recommendations": detailed}, indent=2))
        return 0

    print("Recommendation Targets")
    print_table(rows[: args.limit], "Target", "Count")

    print("\nExamples")
    shown = 0
    for rec in detailed:
        if shown >= args.limit:
            break
        print(f"  - [{rec['priority']}] {rec['target']} — {rec['action']} ({rec['skill']}, {rec['date']})")
        shown += 1
    if shown == 0:
        print("  (none)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aggregate skill eval sidecars")
    parser.add_argument("--skills-dir", default=str(DEFAULT_SKILLS_DIR), help="skills directory (default: ~/.agents/skills)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="high-level summary of eval sidecars")
    summary.add_argument("--skill", help="filter by skill field")
    summary.add_argument("--eval-type", help="filter by eval_type")
    summary.add_argument("--limit", type=int, default=10, help="max grouped rows to show")
    summary.add_argument("--show-paths", action="store_true", help="show eval file paths")
    summary.add_argument("--json", action="store_true", help="emit JSON")
    summary.set_defaults(func=cmd_summary)

    issues = subparsers.add_parser("issues", help="aggregate issue categories")
    issues.add_argument("--skill", help="filter by skill field")
    issues.add_argument("--eval-type", help="filter by eval_type")
    issues.add_argument("--severity", choices=["low", "medium", "high"], help="filter by severity")
    issues.add_argument("--limit", type=int, default=10, help="max grouped rows/examples to show")
    issues.add_argument("--json", action="store_true", help="emit JSON")
    issues.set_defaults(func=cmd_issues)

    recs = subparsers.add_parser("recommendations", help="aggregate recommendation targets")
    recs.add_argument("--skill", help="filter by skill field")
    recs.add_argument("--eval-type", help="filter by eval_type")
    recs.add_argument("--limit", type=int, default=10, help="max grouped rows/examples to show")
    recs.add_argument("--json", action="store_true", help="emit JSON")
    recs.set_defaults(func=cmd_recommendations)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
