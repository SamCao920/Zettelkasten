#!/usr/bin/env python3
"""
vault-auto-clean.py
===================
Lightweight cleanup script called automatically by git hooks after every sync.
Also safe to run manually at any time.

Deletes:
  - All *-SamsComputer* files (vault notes, .obsidian/, .git/ internals)
  - Machine-specific workspace/plugin data files (.obsidian/workspace-*.json, etc.)

Does NOT touch notes, .bak files, dedup logs that don't match conflict patterns,
or anything in .trash/.

Run manually:   python vault-auto-clean.py
Dry run:        python vault-auto-clean.py --dry-run
"""

import sys
import logging
from pathlib import Path
from fnmatch import fnmatch
from datetime import datetime

VAULT = Path(__file__).parent.resolve()
DRY_RUN = "--dry-run" in sys.argv

LOG_FILE = VAULT / "definitions" / "auto-clean.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# Patterns for files that should be deleted whenever found
# Matched against both the full relative path and the filename alone
DELETE_PATTERNS = [
    "*-SamsComputer*",          # conflict copies created by obsidian-git
    ".obsidian/workspace-*.json",          # per-machine Obsidian UI state
    ".obsidian/community-plugins-*.json",  # per-machine plugin list
    ".obsidian/plugins/recent-files-obsidian/data-*.json",
    ".obsidian/plugins/omnisearch/data-*.json",
    ".obsidian/plugins/obsidian-pandoc-reference-list/data-*.json",
    "definitions/dedup_log-*.txt",
]

# Directories to skip entirely (these are safe to walk, but not worth touching)
SKIP_DIRS = {".trash"}


def matches_any(rel_path: str) -> bool:
    filename = Path(rel_path).name
    return any(
        fnmatch(rel_path, pat) or fnmatch(filename, pat)
        for pat in DELETE_PATTERNS
    )


def run_cleanup() -> int:
    log.info("=== auto-clean started%s ===", " (DRY RUN)" if DRY_RUN else "")
    deleted = 0

    for path in sorted(VAULT.rglob("*")):
        # Skip non-files and skip-listed directories
        if not path.is_file():
            continue
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue

        try:
            rel = str(path.relative_to(VAULT)).replace("\\", "/")
        except ValueError:
            continue

        if matches_any(rel):
            log.info("DELETE: %s", rel)
            if not DRY_RUN:
                try:
                    path.unlink()
                    deleted += 1
                except OSError as e:
                    log.warning("  could not delete: %s", e)
            else:
                deleted += 1

    if deleted:
        log.info("Removed %d file(s).", deleted)
    else:
        log.info("Nothing to remove.")

    log.info("=== auto-clean done ===\n")
    return deleted


if __name__ == "__main__":
    run_cleanup()
