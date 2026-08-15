#!/usr/bin/env python3
"""Static integrity checks for this repository's GitHub Actions workflows.

The checker deliberately focuses on failure modes that have already occurred in
this repository: missing local scripts, stale literal git-add paths, and unsafe
writes to main that can lose races with another Actions job.
"""
from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
STRICT_WRITERS = os.getenv("STRICT_WRITERS", "0") == "1"

LOCAL_SCRIPT_RE = re.compile(r"(?<![A-Za-z0-9_./-])(scripts/[A-Za-z0-9_./-]+\.(?:py|sh))")
GLOB_CHARS = set("*?[")
RETRY_MARKERS = (
    "for attempt in",
    "for i in",
    "until git push",
    "while ! git push",
)


def clean_token(token: str) -> str:
    return token.strip().strip("'\"").rstrip(";|&")


def literal_git_add_paths(text: str) -> list[str]:
    paths: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("git add "):
            continue
        try:
            tokens = shlex.split(line)
        except ValueError:
            continue
        for token in tokens[2:]:
            token = clean_token(token)
            if not token or token.startswith("-") or token in {".", "--"}:
                continue
            if "$" in token or any(ch in token for ch in GLOB_CHARS):
                continue
            paths.append(token)
    return paths


def has_retry_loop(text: str) -> bool:
    return any(marker in text for marker in RETRY_MARKERS)


def writer_is_hardened(text: str) -> bool:
    if "git push" not in text:
        return True
    if has_retry_loop(text):
        return True
    # A shared concurrency group serializes independent workflows that write to main.
    if re.search(r"(?m)^\s*group:\s*main-writers\s*$", text):
        return True
    return False


def writer_has_safe_sync(text: str) -> bool:
    """Accept rebase publishing or deterministic rebuild-on-latest-head publishing."""
    if "git push" not in text:
        return True
    if "git pull --rebase origin main" in text:
        return True
    rebuild_on_head = (
        "git fetch origin main" in text
        and "git reset --hard origin/main" in text
        and has_retry_loop(text)
    )
    return rebuild_on_head


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    workflows = sorted(WORKFLOW_DIR.glob("*.y*ml"))

    if not workflows:
        errors.append("No workflow files found under .github/workflows")

    for workflow in workflows:
        text = workflow.read_text(encoding="utf-8")
        rel = workflow.relative_to(ROOT)

        for script in sorted(set(LOCAL_SCRIPT_RE.findall(text))):
            if any(ch in script for ch in GLOB_CHARS) or "$" in script:
                continue
            if not (ROOT / script).is_file():
                errors.append(f"{rel}: referenced local script does not exist: {script}")

        for path in literal_git_add_paths(text):
            # Outputs already published by a healthy builder should exist in the
            # repository. Missing literal paths catch stale artifact names before
            # the commit step fails with pathspec errors.
            if not (ROOT / path).exists():
                errors.append(f"{rel}: literal git add path does not exist: {path}")

        if "git push" in text and not writer_is_hardened(text):
            warnings.append(
                f"{rel}: writes to main without retry loop or shared main-writers concurrency"
            )

        if "git push" in text and not writer_has_safe_sync(text):
            warnings.append(
                f"{rel}: git push lacks a safe sync strategy (pull --rebase or rebuild on latest origin/main)"
            )

    print(f"workflows_scanned={len(workflows)}")
    print(f"errors={len(errors)}")
    print(f"writer_warnings={len(warnings)}")

    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")

    if errors:
        return 1
    if STRICT_WRITERS and warnings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
