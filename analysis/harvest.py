"""Flatten harbor job output into one row per trial: analysis/trials.csv.

Walks jobs/<job>/<trial>/result.json and keeps the trial-level fields the
stats need: reward(s), exception status, tokens/cost, timings, and the task's
[metadata] labels from task.toml. Stdlib only.

Usage: python3 analysis/harvest.py [jobs_dir]
"""

import csv
import json
import sys
import tomllib
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = Path(__file__).resolve().parent / "trials.csv"

FIELDS = [
    "job", "trial_name", "task_name", "agent", "model",
    "reward", "all_rewards", "errored", "exception_type",
    "n_input_tokens", "n_cache_tokens", "n_output_tokens", "cost_usd",
    "started_at", "trial_sec", "agent_exec_sec",
    "difficulty", "family",
]


def seconds(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()


def task_metadata(task_path: str | None) -> dict:
    toml_path = REPO_ROOT / (task_path or "") / "task.toml"
    if not toml_path.is_file():
        return {}
    return tomllib.loads(toml_path.read_text()).get("metadata", {})


def trial_row(job: str, result_path: Path) -> dict | None:
    d = json.loads(result_path.read_text())
    if "trial_name" not in d:  # job-level result.json, not a trial
        return None
    usage = d.get("agent_result") or {}
    rewards = (d.get("verifier_result") or {}).get("rewards") or {}
    exception = d.get("exception_info") or {}
    exec_span = d.get("agent_execution") or {}
    meta = task_metadata((d.get("task_id") or {}).get("path"))
    return {
        "job": job,
        "trial_name": d.get("trial_name"),
        "task_name": d.get("task_name"),
        "agent": (d.get("agent_info") or {}).get("name"),
        "model": (d.get("config", {}).get("agent") or {}).get("model_name"),
        "reward": rewards.get("reward"),
        "all_rewards": json.dumps(rewards) if rewards else None,
        "errored": bool(exception),
        "exception_type": exception.get("exception_type"),
        "n_input_tokens": usage.get("n_input_tokens"),
        "n_cache_tokens": usage.get("n_cache_tokens"),
        "n_output_tokens": usage.get("n_output_tokens"),
        "cost_usd": usage.get("cost_usd"),
        "started_at": d.get("started_at"),
        "trial_sec": seconds(d.get("started_at"), d.get("finished_at")),
        "agent_exec_sec": seconds(exec_span.get("started_at"), exec_span.get("finished_at")),
        "difficulty": meta.get("difficulty"),
        "family": meta.get("family"),
    }


def main() -> None:
    jobs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "jobs"
    rows = [
        row
        for path in sorted(jobs_dir.glob("*/*/result.json"))
        if (row := trial_row(path.parent.parent.name, path))
    ]
    if not rows:
        sys.exit(f"no trials found under {jobs_dir}")

    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} trials -> {OUT_PATH}")


if __name__ == "__main__":
    main()
