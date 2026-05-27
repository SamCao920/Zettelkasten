#!/usr/bin/env python3
"""
vault-cleanup.py
================
Run ONCE on each computer (with Obsidian closed) to:
  1. Delete all *-SamsComputer* files everywhere (vault, .obsidian, .git internals)
  2. Delete machine-specific workspace/plugin data files
  3. Delete duplicate/conflict note copies
  4. Remove stale .git/index.lock
  5. Untrack from git index anything that now matches the new .gitignore
  6. Stage the Hormones rename and Free will note move
  7. Install the .githooks/ directory so git auto-cleans after every future sync
  8. Register a Windows Task Scheduler job (runs vault-auto-clean.py on login)
  9. Commit and push

After this, everything is automatic — no manual runs needed.

Usage:
    cd "C:/Users/Fangyuan Cao/OneDrive/Documents/Obsidian/Learning"
    python vault-cleanup.py           # real run
    python vault-cleanup.py --dry-run # preview only
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
        print(f"  [!] exited {result.returncode}")
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
            try:
                path.unlink()
            except OSError as e:
                print(f"  [!] Could not delete: {e}")
        return True
    return False


def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


print(f"Vault: {VAULT}")
if DRY_RUN:
    print("DRY RUN — no files will be touched.\n")


# ── Step 1: Delete ALL *-SamsComputer* files ──────────────────────────────────
section("1. Delete ALL *-SamsComputer* files (vault + .obsidian + .git internals)")

count = 0
for path in sorted(VAULT.rglob("*-SamsComputer*")):
    if path.is_file():
        delete_file(path)
        count += 1
print(f"  Total: {count} file(s)")


# ── Step 2: Delete machine-specific .obsidian / definitions files ─────────────
section("2. Delete machine-specific .obsidian and definitions files")

extra_patterns = [
    ".obsidian/workspace-*.json",
    ".obsidian/community-plugins-*.json",
    ".obsidian/plugins/recent-files-obsidian/data-*.json",
    ".obsidian/plugins/omnisearch/data-*.json",
    ".obsidian/plugins/obsidian-pandoc-reference-list/data-*.json",
    "definitions/dedup_log-*.txt",
]

count = 0
for path in sorted(VAULT.rglob("*")):
    if not path.is_file():
        continue
    try:
        rel = str(path.relative_to(VAULT)).replace("\\", "/")
    except ValueError:
        continue
    if path.exists() and any(fnmatch(rel, p) or fnmatch(path.name, p) for p in extra_patterns):
        delete_file(path, "machine-specific")
        count += 1
print(f"  Total: {count} file(s)")


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


# ── Step 5: Untrack anything still in index that now matches .gitignore ───────
section("5. Untrack gitignored files from git index")

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
    if any(fnmatch(p, pat) or fnmatch(Path(p).name, pat) for pat in untrack_patterns)
]

if to_untrack:
    print(f"  Untracking {len(to_untrack)} file(s)...")
    run(["git", "rm", "--cached", "--ignore-unmatch", "--"] + to_untrack)
else:
    print("  Nothing left to untrack")


# ── Step 6: Stage note renames and moves ─────────────────────────────────────
section("6. Stage note renames and moves")

hormones_old = "6 - Notes/6.a - Claims/Hormones are organic compounds that help an organism maintain homeostasis 2.md"
hormones_new = "6 - Notes/6.a - Claims/Hormones are organic compounds that help an organism maintain homeostasis.md"
if (VAULT / hormones_new).exists():
    print("  Staging Hormones rename...")
    run(["git", "rm", "--cached", "--ignore-unmatch", "--", hormones_old])
    run(["git", "add", "--", hormones_new])
    print("  OK")
else:
    print(f"  [!] {hormones_new} not found")

fw_old = "6 - Notes/6.a - Claims/Free will and responsibility are not mutually exclusive.md"
fw_new = "1 - Unsorted/Free will and responsibility are not mutually exclusive.md"
fw_path = VAULT / fw_new
if fw_path.exists():
    if not DRY_RUN:
        import getpass, subprocess as sp
        sp.run(["icacls", str(fw_path), "/grant", f"{getpass.getuser()}:(F)"],
               capture_output=True)
    print("  Staging Free will note move (6 - Notes -> 1 - Unsorted)...")
    run(["git", "rm", "--cached", "--ignore-unmatch", "--", fw_old])
    run(["git", "add", "--", fw_new])
    print("  OK")
else:
    print(f"  [!] {fw_new} not found — skipping")


# ── Step 7: Install .githooks so future syncs auto-clean ─────────────────────
section("7. Install git hooks (auto-clean after every future sync)")

# Point git at the tracked .githooks/ directory
run(["git", "config", "core.hooksPath", ".githooks"])
print("  git config core.hooksPath .githooks — done")

# Make hook scripts executable (needed on Mac/Linux; harmless on Windows)
for hook in [".githooks/post-merge", ".githooks/post-rewrite"]:
    hook_path = VAULT / hook
    if hook_path.exists() and not DRY_RUN:
        hook_path.chmod(0o755)
    print(f"  chmod +x {hook} — done")

# Also stage the new hook files and auto-clean script
run(["git", "add", "--", ".githooks/post-merge", ".githooks/post-rewrite"])
run(["git", "add", "--", "vault-auto-clean.py"])
print("  Hooks and auto-clean script staged")


# ── Step 8: Register Windows Task Scheduler login job (safety net) ────────────
section("8. Register Windows Task Scheduler login trigger")

task_name = "ObsidianVaultAutoClean"
python_exe = sys.executable
script = str(VAULT / "vault-auto-clean.py")

# Use schtasks (available on all Windows without requiring elevation)
ps_cmd = (
    f'$action = New-ScheduledTaskAction -Execute "{python_exe}" -Argument "{script}"; '
    f'$trigger = New-ScheduledTaskTrigger -AtLogOn; '
    f'$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 2); '
    f'Register-ScheduledTask -TaskName "{task_name}" -Action $action '
    f'-Trigger $trigger -Settings $settings -Force'
)

result = run(
    ["powershell", "-NonInteractive", "-Command", ps_cmd],
    check=False,
)
if not DRY_RUN and result.returncode != 0:
    print("  [!] Task Scheduler registration failed (may need to run as Administrator).")
    print(f"      Task name: {task_name}")
    print(f"      Script:    {script}")
    print("      You can register it manually in Task Scheduler if needed.")
else:
    print(f"  Task '{task_name}' registered — runs vault-auto-clean.py at each login")


# ── Step 9: Stage config changes and commit ───────────────────────────────────
section("9. Stage config changes and commit")

run(["git", "add", "--", ".gitignore"])
run(["git", "add", "--", ".obsidian/plugins/obsidian-git/data.json"])
run([
    "git", "commit", "--allow-empty", "-m",
    "chore: vault cleanup - delete conflict copies, auto-clean hooks, rebase sync",
])
run(["git", "push"])

print("\n" + "="*60)
print("  Done! Auto-clean is now fully set up.")
print("="*60)
print("""
What happens automatically from now on:
  - After every obsidian-git sync: .githooks/post-rewrite fires
    and calls vault-auto-clean.py to delete any *-SamsComputer* files.
  - At every Windows login: Task Scheduler runs vault-auto-clean.py
    as a safety net for anything created between syncs.
  - The .gitignore blocks any stragglers from ever being committed.

On each additional computer: run this script once to install the hooks
and Task Scheduler job on that machine too.
""")
