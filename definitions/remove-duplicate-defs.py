"""
remove-duplicate-defs.py

Cleans a Note Definitions consolidated glossary file.

Fixes:
  1. Multiple *alias* or _alias_ spans (including multiple spans on one line
     like:  _Plural Form_ _alias1, alias2, ..._  ).
  2. Alias values duplicated between the *...* line and the _..._ line.
  3. Duplicate YAML frontmatter blocks (caused by Obsidian auto-updating the
     'updated' property after a script write).
  4. Spurious aliases that look like section headers (e.g. "In X:").
  5. Corrupted fragment lines (e.g. "s*").

Cascade prevention: after every write the script sleeps WRITE_COOLDOWN seconds
so that Obsidian's automatic 'updated' timestamp rewrite does not trigger
another run.

Requirements: pip install psutil
"""

import re
import shutil
import time
import sys
import logging
import psutil
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GLOSSARY_PATH    = Path(r"C:\Users\samca\OneDrive\Documents\Obsidian\Learning\definitions\glossary.md")
INTERVAL_SECONDS = 5 * 60   # periodic fallback interval
POLL_SECONDS     = 10        # how often to poll Obsidian state and file mtime
WRITE_COOLDOWN   = 5         # seconds to wait after writing before re-arming mtime watch
# ---------------------------------------------------------------------------

OBSIDIAN_EXE = "Obsidian.exe"
LOG_PATH     = GLOSSARY_PATH.parent / "dedup_log.txt"

STAR_SPAN_RE  = re.compile(r'\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)')
UNDER_SPAN_RE = re.compile(r'_(?!_)([^_\n]+?)(?<!_)_(?!_)')
SPURIOUS_RE   = re.compile(r'^in\s+.+:s?$', re.IGNORECASE)
YAML_KEY_RE   = re.compile(r'^([\w][\w-]*):\s*(.*)')


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------

def is_obsidian_running() -> bool:
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] == OBSIDIAN_EXE:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def get_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_and_merge_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    """
    Scan from the top of the file and collect ALL consecutive YAML frontmatter
    blocks (separated only by blank lines).  Merge their key-value pairs,
    preferring later values for the same key (so Obsidian's most-recent
    'updated' timestamp wins).

    Returns (merged_props, line_index_of_first_non_frontmatter_line).
    If no frontmatter is found, returns ({}, 0).
    """
    i = 0
    merged: dict[str, str] = {}

    while i < len(lines) and lines[i].strip() == "---":
        i += 1  # skip opening fence
        block: dict[str, str] = {}
        while i < len(lines):
            line = lines[i]
            if line.strip() == "---":
                i += 1  # skip closing fence
                break
            m = YAML_KEY_RE.match(line.strip())
            if m:
                block[m.group(1)] = m.group(2).strip()
            i += 1
        merged.update(block)
        # Skip blank lines between blocks
        while i < len(lines) and not lines[i].strip():
            i += 1
        # If the very next non-blank line is another "---", loop again;
        # otherwise we're done with frontmatter.
        if i >= len(lines) or lines[i].strip() != "---":
            break

    return merged, i


def build_frontmatter(props: dict[str, str]) -> str:
    """
    Serialise merged properties back into a single YAML frontmatter block.
    Ensures 'def-type: consolidated' is always present.
    """
    props.setdefault("def-type", "consolidated")
    lines = ["---\n"]
    for k, v in props.items():
        lines.append(f"{k}: {v}\n")
    lines.append("---\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# Alias line helpers
# ---------------------------------------------------------------------------

def is_phrase_line(line: str) -> bool:
    return line.startswith("# ")


def is_alias_line(line: str) -> bool:
    """
    A line is an alias line if, after removing every *...* and _..._ span,
    only whitespace remains -- meaning the entire line is composed of italic
    spans with no other text.
    Also rejects: lines with leading whitespace, bold markers, bullet syntax.
    """
    if line.startswith((" ", "\t")):
        return False
    s = line.strip()
    if not s:
        return False
    if s.startswith("**") or s.startswith("* "):
        return False
    remainder = STAR_SPAN_RE.sub("", s)
    remainder = UNDER_SPAN_RE.sub("", remainder).strip()
    if remainder:
        return False
    return bool(re.search(r"[a-zA-Z\u0080-\uFFFF]", s))


def is_fragment_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if len(s) <= 4 and (s.endswith("*") or s.endswith("_")):
        if not re.search(r"[a-zA-Z\u0080-\uFFFF]", s):
            return True
    return False


def is_spurious(value: str) -> bool:
    return bool(SPURIOUS_RE.match(value.strip()))


def extract_all_values(line: str) -> list[str]:
    """Extract every comma-separated value from every *...* and _..._ span."""
    values: list[str] = []
    for m in STAR_SPAN_RE.finditer(line):
        for v in m.group(1).split(","):
            v = v.strip()
            if v:
                values.append(v)
    for m in UNDER_SPAN_RE.finditer(line):
        for v in m.group(1).split(","):
            v = v.strip()
            if v:
                values.append(v)
    return values


# ---------------------------------------------------------------------------
# Main deduplication
# ---------------------------------------------------------------------------

def deduplicate(path: Path) -> int:
    text  = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    result: list[str] = []
    fixes = 0

    # --- Step 1: parse and merge all frontmatter blocks at the top ---
    props, body_start = parse_and_merge_frontmatter(lines)

    if props:
        new_header = build_frontmatter(props)
        # Count as a fix if there were multiple frontmatter blocks
        original_header = "".join(lines[:body_start])
        if original_header.count("---") > 2:  # more than one open+close pair
            fixes += 1
        result.append(new_header)
    else:
        # No frontmatter at all — ensure def-type is written
        result.append("---\ndef-type: consolidated\n---\n")
        fixes += 1

    i = body_start

    # --- Step 2: clean definition blocks ---
    while i < len(lines):
        line = lines[i]

        if not is_phrase_line(line):
            result.append(line)
            i += 1
            continue

        result.append(line)
        i += 1

        # Collect all alias lines following this phrase header,
        # skipping blank lines and discarding fragment lines.
        alias_lines: list[str] = []
        j = i
        while j < len(lines):
            nxt = lines[j]
            if not nxt.strip():
                j += 1
                continue
            if is_fragment_line(nxt):
                fixes += 1
                j += 1
                continue
            if is_alias_line(nxt):
                alias_lines.append(nxt)
                j += 1
                continue
            break
        i = j

        if not alias_lines:
            result.append("\n")
            continue

        # Extract all values from ALL spans on ALL alias lines into one merged list.
        seen:      set[str]  = set()
        all_vals: list[str]  = []

        for al in alias_lines:
            for m in STAR_SPAN_RE.finditer(al):
                for v in m.group(1).split(","):
                    v = v.strip(); k = v.lower()
                    if v and k not in seen and not is_spurious(v):
                        seen.add(k); all_vals.append(v)
            for m in UNDER_SPAN_RE.finditer(al):
                for v in m.group(1).split(","):
                    v = v.strip(); k = v.lower()
                    if v and k not in seen and not is_spurious(v):
                        seen.add(k); all_vals.append(v)

        # Write a single *...* line with all unique values
        original     = "".join(alias_lines).strip()
        new_combined = f"*{', '.join(all_vals)}*" if all_vals else ""
        if new_combined != original:
            fixes += 1

        result.append("\n")
        if all_vals:
            result.append(f"*{', '.join(all_vals)}*\n")
        result.append("\n")

    if fixes > 0:
        backup = path.with_suffix(".md.bak")
        shutil.copy2(path, backup)
        path.write_text("".join(result), encoding="utf-8")
        logging.info(f"Fixed {fixes} issue(s). Backup: {backup.name}")
    else:
        logging.info("Scan complete — no issues found.")

    return fixes


# ---------------------------------------------------------------------------
# Watcher loop
# ---------------------------------------------------------------------------

def run_once(reason: str) -> bool:
    """Returns True if the file was modified."""
    logging.info(f"Running deduplication ({reason}).")
    try:
        return deduplicate(GLOSSARY_PATH) > 0
    except Exception as exc:
        logging.error(f"Error: {exc}")
        return False


def main():
    if not GLOSSARY_PATH.exists():
        print(f"ERROR: File not found: {GLOSSARY_PATH}", file=sys.stderr)
        sys.exit(1)

    setup_logging()
    logging.info("=== Deduplicator started ===")
    logging.info(f"Watching: {GLOSSARY_PATH}")
    logging.info(f"Interval: {INTERVAL_SECONDS // 60} min | Poll: {POLL_SECONDS}s | Cooldown: {WRITE_COOLDOWN}s")

    obsidian_was_open = is_obsidian_running()
    last_periodic     = time.monotonic()

    if obsidian_was_open:
        modified = run_once("Obsidian already open at startup")
        if modified:
            time.sleep(WRITE_COOLDOWN)
        last_periodic = time.monotonic()

    last_mtime = get_mtime(GLOSSARY_PATH)

    while True:
        time.sleep(POLL_SECONDS)
        obsidian_is_open = is_obsidian_running()
        current_mtime    = get_mtime(GLOSSARY_PATH)
        now              = time.monotonic()

        if obsidian_is_open and not obsidian_was_open:
            modified = run_once("Obsidian opened")
            if modified:
                time.sleep(WRITE_COOLDOWN)
            last_mtime    = get_mtime(GLOSSARY_PATH)
            last_periodic = now

        elif not obsidian_is_open and obsidian_was_open:
            modified = run_once("Obsidian closed")
            if modified:
                time.sleep(WRITE_COOLDOWN)
            last_mtime = get_mtime(GLOSSARY_PATH)

        elif obsidian_is_open and current_mtime != last_mtime:
            modified = run_once("file modified")
            if modified:
                time.sleep(WRITE_COOLDOWN)
            last_mtime    = get_mtime(GLOSSARY_PATH)
            last_periodic = now

        elif obsidian_is_open and (now - last_periodic >= INTERVAL_SECONDS):
            modified = run_once("periodic check")
            if modified:
                time.sleep(WRITE_COOLDOWN)
            last_mtime    = get_mtime(GLOSSARY_PATH)
            last_periodic = now

        obsidian_was_open = obsidian_is_open


if __name__ == "__main__":
    main()