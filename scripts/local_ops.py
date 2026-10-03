#!/usr/bin/env python3
"""Local Docker pilot tools. No production deployment, credential output or live restore."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
WRITERS = ("backend", "worker", "beat")


def run(args, *, stdin=None, stdout=None, timeout=180):
    input_options = {"stdin": stdin} if hasattr(stdin, "read") else {"input": stdin}
    result = subprocess.run(args, cwd=ROOT, **input_options, stdout=stdout or subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout, check=False)
    if result.returncode:
        # stderr may contain database record values or configuration; do not print it.
        raise RuntimeError(f"Command failed ({result.returncode}): {args[0]} {args[1]}")
    return result.stdout


def compose(*args, **kwargs):
    return run(["docker", "compose", *args], **kwargs)


def services():
    raw = compose("ps", "--all", "--format", "json").decode().strip()
    if not raw:
        return []
    if raw.startswith("["):
        return json.loads(raw)
    return [json.loads(line) for line in raw.splitlines()]


def inventory():
    return json.loads(compose("exec", "-T", "backend", "python", "manage.py", "local_readiness").decode())


def guard_local():
    report = inventory()
    if report["environment"] not in {"development", "test"} or report["database_vendor"] != "postgresql":
        raise RuntimeError("Only this repository's local PostgreSQL development/test stack is supported.")
    if report["pending_migrations"]:
        raise RuntimeError("Pending migrations: review/apply them before a snapshot.")
    return report


def backup_root():
    path = (ROOT / "backups").resolve()
    if not path.is_relative_to(ROOT):
        raise RuntimeError("Backup path must remain within this workspace.")
    path.mkdir(exist_ok=True)
    return path


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pg(script, *args, stdin=None, stdout=None):
    return compose("exec", "-T", "db", "sh", "-c", script, "mrerp-local-ops", *args,
                   stdin=stdin, stdout=stdout)


def table_counts(database=None):
    db = '"$1"' if database else '"$POSTGRES_DB"'
    args = (database,) if database else ()
    tables = pg(f'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d {db} -Atc "SELECT tablename FROM pg_tables WHERE schemaname=\'public\' ORDER BY tablename"', *args).decode().splitlines()
    if not tables or any(not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", table) for table in tables):
        raise RuntimeError("Missing tables or unsupported identifiers.")
    sql = " UNION ALL ".join(f'SELECT \'{table}\', count(*) FROM "{table}"' for table in tables)
    raw = pg(f'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d {db} -At -F "|"', *args, stdin=sql.encode()).decode()
    return {name: int(n) for name, n in (line.split("|") for line in raw.splitlines())}


def snapshot():
    guard_local()
    state = services()
    running = [name for name in WRITERS if any(s["Service"] == name and s.get("State") == "running" for s in state)]
    if "backend" not in running:
        raise RuntimeError("Backend must remain running until the snapshot freeze starts.")
    folder = backup_root() / (datetime.now(timezone.utc).strftime("local-%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8])
    folder.mkdir()
    complete = False
    try:
        # Freeze HTTP writers and background jobs together for DB/media consistency.
        compose("stop", "--timeout", "30", *running)
        if any(s["Service"] in WRITERS and s.get("State") == "running" for s in services()):
            raise RuntimeError("A writer is still running; snapshot refused.")
        counts = table_counts()
        with (folder / "database.dump").open("wb") as output:
            pg('pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom', stdout=output)
        media = folder / "media-copy"
        media.mkdir()
        compose("cp", "backend:/app/media/.", str(media))
        members = list(media.rglob("*"))
        if any(path.is_symlink() for path in members):
            raise RuntimeError("Media symlinks are unsupported; snapshot refused.")
        with tarfile.open(folder / "media.tar.gz", "w:gz") as archive:
            archive.add(media, arcname="media", recursive=True)
        manifest = {
            "format": 1, "scope": "local-development-only", "created_at": datetime.now(timezone.utc).isoformat(),
            "table_counts": counts, "media_files": sum(p.is_file() for p in members),
            "hashes": {name: digest(folder / name) for name in ("database.dump", "media.tar.gz")},
            "writers_frozen": list(WRITERS), "restore_verified": False,
        }
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        complete = True
    finally:
        if running:
            compose("start", *running)
        if not complete:
            (folder / "FAILED.txt").write_text("Incomplete snapshot. Do not restore. Original runtime restart attempted.", encoding="utf-8")
    print(f"Snapshot: {folder.relative_to(ROOT)} (local only; not an off-host backup)")
    return folder


def verified_snapshot(path):
    folder = Path(path).resolve()
    if not folder.is_relative_to(backup_root()) or folder.is_symlink():
        raise RuntimeError("Only workspace backups are accepted.")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("format") != 1 or manifest.get("scope") != "local-development-only" or (folder / "FAILED.txt").exists():
        raise RuntimeError("Unsupported or incomplete snapshot.")
    for name in ("database.dump", "media.tar.gz"):
        artifact = folder / name
        if not artifact.resolve().is_relative_to(folder) or artifact.is_symlink() or digest(artifact) != manifest["hashes"][name]:
            raise RuntimeError("Snapshot checksum/path validation failed.")
    return folder, manifest


def restore_drill(path):
    guard_local()
    folder, manifest = verified_snapshot(path)
    target = "mrerp_drill_" + uuid.uuid4().hex
    drill = backup_root() / "drills" / target
    drill.mkdir(parents=True)
    created = False
    result = {"scope": "local-development-only", "passed": False}
    try:
        pg('createdb -U "$POSTGRES_USER" -- "$1"', target)
        created = True
        with (folder / "database.dump").open("rb") as stream:
            pg('pg_restore -U "$POSTGRES_USER" -d "$1" --no-owner --no-privileges --exit-on-error', target, stdin=stream)
        if table_counts(target) != manifest["table_counts"]:
            raise RuntimeError("Restored row counts do not match the frozen snapshot.")
        with tarfile.open(folder / "media.tar.gz", "r:gz") as archive:
            for member in archive.getmembers():
                if member.name != "media" and not member.name.startswith("media/"):
                    raise RuntimeError("Invalid media archive root.")
                if member.issym() or member.islnk() or not (drill / member.name).resolve().is_relative_to(drill):
                    raise RuntimeError("Unsafe media archive member.")
            archive.extractall(drill, filter="data")
        files = [p for p in (drill / "media").rglob("*") if p.is_file()]
        if len(files) != manifest["media_files"]:
            raise RuntimeError("Restored media file count mismatch.")
        # Use an isolated DB override for checks; never migrate/seed or write into the live DB.
        compose("exec", "-T", "-e", f"POSTGRES_DB={target}", "backend", "python", "manage.py", "check")
        audit = json.loads(compose("exec", "-T", "-e", f"POSTGRES_DB={target}", "backend", "python", "manage.py", "local_readiness").decode())
        if audit["pending_migrations"]:
            raise RuntimeError("Restored schema is not current.")
        result.update(passed=True, tables_checked=len(manifest["table_counts"]), media_files=len(files), application_check=True)
    finally:
        # target is generated here; no caller-supplied DB name reaches deletion.
        if created:
            if not re.fullmatch(r"mrerp_drill_[0-9a-f]{32}", target):
                raise RuntimeError("Invalid isolated drill target.")
            pg('dropdb -U "$POSTGRES_USER" -- "$1"', target)
        (drill / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Restore drill PASS: {len(manifest['table_counts'])} tables, {len(files)} media files. Live DB unchanged.")
    print(f"Evidence: {drill.relative_to(ROOT)}/result.json")


def check():
    report = guard_local()
    report["services"] = [{"name": s["Service"], "state": s.get("State"), "health": s.get("Health")} for s in services()]
    report["workspace_free_bytes"] = __import__("shutil").disk_usage(ROOT).free
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "snapshot", "restore-drill"])
    parser.add_argument("--snapshot", help="Workspace backup folder for an isolated restore drill")
    options = parser.parse_args()
    if options.command == "check":
        check()
    elif options.command == "snapshot":
        snapshot()
    elif not options.snapshot:
        parser.error("restore-drill requires --snapshot")
    else:
        restore_drill(options.snapshot)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired, tarfile.TarError) as error:
        detail = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        print(f"Local operation stopped: {detail}. Check local runtime/artifacts; no credentials are printed.", file=sys.stderr)
        sys.exit(1)
