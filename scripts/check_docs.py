#!/usr/bin/env python3
"""Validate the Phase 0 documentation and repository hygiene."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

MAIN_GUIDES = [
    "01-tong-quan-san-pham.md",
    "02-yeu-cau-san-pham.md",
    "03-thiet-ke-ky-thuat.md",
    "04-tieu-chi-nghiem-thu.md",
    "05-huong-dan-va-van-hanh.md",
    "06-ke-hoach-trien-khai.md",
]

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / ".gitignore",
    ROOT / ".gitattributes",
    ROOT / ".github" / "pull_request_template.md",
    ROOT / ".github" / "workflows" / "repository-quality.yml",
    DOCS / "README.md",
    DOCS / "glossary.md",
    DOCS / "decisions" / "open-decisions.md",
]

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+.+$")
OPEN_DECISION_RE = re.compile(r"^\|\s*(OD-\d{2})\s*\|")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")

PRIVATE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".jks", ".keystore"}
BACKUP_SUFFIXES = {".pgdump", ".dump", ".bak", ".backup"}
IGNORED_DIRECTORY_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRECTORY_NAMES for part in path.relative_to(ROOT).parts)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def tracked_files(errors: list[str]) -> list[Path]:
    command = [
        "git",
        "-c",
        f"safe.directory={ROOT.as_posix()}",
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "-z",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"Cannot read tracked files from Git: {exc}")
        return []

    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def check_required_files(errors: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"Missing required file: {relative(path)}")

    actual_guides = sorted(path.name for path in DOCS.glob("[0-9][0-9]-*.md"))
    if actual_guides != MAIN_GUIDES:
        errors.append(
            "Main reading path must contain exactly 01-06: "
            + ", ".join(actual_guides)
        )


def check_markdown(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if is_ignored(path):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Markdown is not UTF-8: {relative(path)}")
            continue

        headings: dict[str, int] = {}
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip(" \t") != line:
                errors.append(f"Trailing whitespace: {relative(path)}:{line_number}")

            if HEADING_RE.match(line):
                normalized = line.strip()
                if normalized in headings:
                    errors.append(
                        f"Duplicate heading: {relative(path)}:{line_number} "
                        f"(first at {headings[normalized]})"
                    )
                else:
                    headings[normalized] = line_number

        for match in LINK_RE.finditer(text):
            target = match.group(1).strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue

            file_target = unquote(target.split("#", 1)[0])
            resolved = (path.parent / file_target).resolve()
            if not resolved.exists():
                errors.append(f"Broken relative link: {relative(path)} -> {target}")


def check_open_decisions(errors: list[str]) -> None:
    path = DOCS / "decisions" / "open-decisions.md"
    if not path.is_file():
        return

    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = OPEN_DECISION_RE.match(line)
        if match:
            ids.append(match.group(1))

    if not ids:
        errors.append("No open-decision IDs found")
        return

    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("Duplicate open-decision IDs: " + ", ".join(duplicates))

def is_example_secret(path: Path) -> bool:
    name = path.name.lower()
    return ".example." in name or name.endswith(".example")


def check_secret_hygiene(errors: list[str]) -> None:
    for path in tracked_files(errors):
        name = path.name.lower()

        is_environment_file = (
            name == ".env"
            or name == ".envrc"
            or name.endswith(".env")
            or ".env." in name
        )
        if is_environment_file and not name.endswith(".example"):
            errors.append(f"Tracked environment file is not an example: {relative(path)}")

        if path.suffix.lower() in PRIVATE_SUFFIXES and not is_example_secret(path):
            errors.append(f"Tracked key/certificate container: {relative(path)}")

        if path.suffix.lower() in BACKUP_SUFFIXES:
            errors.append(f"Tracked database backup: {relative(path)}")

        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        if PRIVATE_KEY_RE.search(text):
            errors.append(f"Private-key marker found: {relative(path)}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_markdown(errors)
    check_open_decisions(errors)
    check_secret_hygiene(errors)

    if errors:
        print("Repository quality checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    markdown_count = sum(1 for path in ROOT.rglob("*.md") if not is_ignored(path))
    print(f"Repository quality checks passed ({markdown_count} Markdown files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
