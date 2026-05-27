#!/usr/bin/env python3
"""
vault-cleanup.py
================
Run with Obsidian closed:

    cd "C:/Users/Fangyuan Cao/OneDrive/Documents/Obsidian/Learning"
    python vault-cleanup.py

What it does:
  1. Physically deletes all *-SamsComputerX* files everywhere
     (vault files, .obsidian/ files, and .git/ internal backups)
  2. Physically deletes machine-specific workspace/plugin data files
  3. Deletes duplicate/conflict note copies
  4. Removes stale .git/index.lock
  5. Untracks anything matching the new .gitignore that's still in the index
  6. Stages the Hormones rename and Free will note move
  7. Commits everything
"""

import sys
import subprocess
from pathlib import Path
from fnmatch import fnmatch

VAULT = Path(__file__).parent.resolve()
DRY_RUN = "--dry-run" in sys.argv


def run(cmd, check=True, read_only=False):
    cmd = [str(c) for c in cmd]
    print(f"  $ {' '.join(cmd)}")
    if DRY_RUN and not read_only:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    result = subprocess.run(cmd, cwd=VAULT, capture_output=True, text=True)
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines()[:20]:
            print(f"    {line}")
    if result.stderr.strip():
        print(f"    STDERR: {result.stderr.strip()[:300]}")
    if check and result.returncode != 0:
        print(f"  [!] Command exited {result.returncode}")
    return result


def delete_file(path: Path, reason: str = ""):
    label = f" ({reason})" if reason else ""
    try:
        rel = path.relative_to(VAULT)
    except ValueError:
        rel = path
    if path.exists():
        print(f"  DELETE{label}: {rel}")
        if not DRY_RUN:
            path.unlink()
        return True
    return False


def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


print(f"Vault: {VAULT}")
if DRY_RUN:
    print("DRY RUN — no files will be touched.\n")


# ── Step 1: Physical deletion of ALL *-SamsComputer* files ───────────────────
# Covers: .git/ internals (index-*, ORIG_HEAD-*, COMMIT_EDITMSG-*, FETCH_HEAD-*,
#          logs/HEAD-*, logs/refs/heads/master-*, info/refs-*)
#         .obsidian/ (workspace-*, community-plugins-*, plugin data-*)
#         definitions/ (dedup_log-*, glossary.md-*.bak is left alone per user)
#         vault notes (any *-SamsComputer*.md that shouldn't exist)
section("1. Delete ALL *-SamsComputer* files (vault + .obsidian + .git internals)")

sams_deleted = 0
# Walk the entire vault directory, including .git and .obsidian
for path in sorted(VAULT.rglob("*-SamsComputer*")):
    if path.is_file():
        delete_file(path)
        sams_deleted += 1

print(f"  Total: {sams_deleted} file(s)")


# ── Step 2: Delete machine-specific workspace/plugin data files ───────────────
section("2. Delete machine-specific .obsidian files (all variants)")

# Patterns relative to vault root
delete_patterns = [
    ".obsidian/workspace-*.json",
    ".obsidian/community-plugins-*.json",
    ".obsidian/plugins/recent-files-obsidian/data-*.json",
    ".obsidian/plugins/omnisearch/data-*.json",
    ".obsidian/plugins/obsidian-pandoc-reference-list/data-*.json",
    "definitions/dedup_log-*.txt",
]

extra_deleted = 0
for path in sorted(VAULT.rglob("*")):
    if not path.is_file():
        continue
    try:
        rel = str(path.relative_to(VAULT)).replace("\\", "/")
    except ValueError:
        continue
    for pattern in delete_patterns:
        if fnmatch(rel, pattern):
            # Skip if already deleted in step 1
            if path.exists():
                delete_file(path, "machine-specific")
                extra_deleted += 1
            break

print(f"  Total: {extra_deleted} file(s)")


# ── Step 3: Delete duplicate/conflict note copies ─────────────────────────────
section("3. Delete duplicate and conflict note files")

dupes = [
    VAULT / "6 - Notes/6.a - Claims/Hormones are organic compounds that help an organism maintain homeostasis 2.md",
    VAULT / "6 - Notes/6.a - Claims/The liberal nation state is doomed to fail since it gives people nothing to preserve 1.md",
    VAULT / "6 - Notes/6.a - Claims/Retributive punishment is never justified-SamsComputer2.md",
]
for f in dupes:
    if not delete_file(f, "duplicate"):
        print(f"  Already gone: {f.name}")


# ── Step 4: Remove stale .git/index.lock ─────────────────────────────────────
section("4. Remove stale .git/index.lock")
lock = VAULT / ".git" / "index.lock"
if not delete_file(lock, "stale lock"):
    print("  No lock file (already clean)")


# ── Step 5: Untrack from git index anything still matching new .gitignore ─────
section("5. Untrack files from git index that are now gitignored")

tracked_result = run(["git", "ls-files"], check=False, read_only=True)
all_tracked = tracked_result.stdout.splitlines()

untrack_patterns = [
    "*-SamsComputer*",
    ".obsidian/workspace-*.json",
    ".obsidian/community-plugins-*.json",
    ".obsidian/plugins/recent-files-obsidian/data-*.json",
    ".obsidian/plugins/omnisearch/data-*.json",
    ".obsidian/plugins/obsidian-pandoc-reference-list/data-*.json",
    "definitions/dedup_log-*.txt",
]

to_untrack = [
    p for p in all_tracked
    if any(
        fnmatch(p, pat) or fnmatch(Path(p).name, pat)
        for pat in untrack_patterns
    )
]

if to_untrack:
    print(f"  Untracking {len(to_untrack)} file(s) from index...")
    run(["git", "rm", "--cached", "--ignore-unmatch", "--"] + to_untrack)
else:
    print("  Nothing left to untrack (already clean from previous run)")


# ── Step 6: Stage note renames and moves ─────────────────────────────────────
section("6. Stage note renames and moves")

hormones_old = "6 - Notes/6.a - Claims/Hormones are organic compounds that help an organism maintain homeostasis 2.md"
hormones_new = "6 - Notes/6.a - Claims/Hormones are organic compounds that help an organism maintain homeostasis.md"
if (VAULT / hormones_new).exists():
    print("  Staging Hormones rename...")
    run(["git", "rm", "--cached", "--ignore-unmatch", "--", hormones_old])
    run(["git", "add", "--", hormones_new])

fw_old = "6 - Notes/6.a - Claims/Free will and responsibility are not mutually exclusive.md"
fw_new = "1 - Unsorted/Free will and responsibility are not mutually exclusive.md"
fw_path = VAULT / fw_new
if fw_path.exists():
    print("  Fixing permissions on Free will note...")
    if not DRY_RUN:
        import getpass
        user = getpass.getuser()
        subprocess.run(
            ["icacls", str(fw_path), "/grant", f"{user}:(F)"],
            capture_output=True
        )
    print("  Staging Free will note move (6 - Notes -> 1 - Unsorted)...")
    run(["git", "rm", "--cached", "--ignore-unmatch", "--", fw_old])
    run(["git", "add", "--", fw_new])
else:
    print(f"  [!] {fw_new} not found — skipping")


# ── Step 7: Stage config changes and commit ───────────────────────────────────
section("7. Stage config changes and commit")
run(["git", "add", "--", ".gitignore"])
run(["git", "add", "--", ".obsidian/plugins/obsidian-git/data.json"])
run([
    "git", "commit", "--allow-empty", "-m",
    "chore: vault cleanup - delete conflict copies, fix gitignore, rebase sync",
])

print("\n" + "="*60 + "\n  Done! Run: git push\n" + "="*60)
