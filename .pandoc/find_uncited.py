"""
find_uncited.py

Compares your Zotero .bib file against all Markdown notes in your Obsidian vault.
Outputs every source that has never been cited in any note.

Usage:
    python find_uncited.py

Edit the two paths below before running.
"""

import re
import os
from pathlib import Path

# ── CONFIGURE THESE TWO PATHS ────────────────────────────────────────────────
BIB_FILE = r"C:\Users\samca\OneDrive\Documents\Obsidian\Learning\.pandoc\ReThink.bib"
VAULT_DIR = r"C:\Users\samca\OneDrive\Documents\Obsidian\Learning"
# ─────────────────────────────────────────────────────────────────────────────


def parse_bib(bib_path):
    """Extract {citekey: {title, author}} from a .bib file."""
    text = Path(bib_path).read_text(encoding="utf-8", errors="ignore")

    entries = {}
    # Match @type{citekey, ... }
    entry_pattern = re.compile(r"@\w+\{([^,]+),([^@]*?)(?=\n@|\Z)", re.DOTALL)

    for match in entry_pattern.finditer(text):
        citekey = match.group(1).strip()
        body = match.group(2)

        title = re.search(r"title\s*=\s*\{(.+?)\}", body, re.DOTALL)
        author = re.search(r"author\s*=\s*\{(.+?)\}", body, re.DOTALL)
        year = re.search(r"(?:date|year)\s*=\s*\{(\d{4})", body)

        entries[citekey] = {
            "title": title.group(1).replace("\n", " ").strip() if title else "(no title)",
            "author": author.group(1).split(",")[0].strip() if author else "(no author)",
            "year": year.group(1) if year else "",
        }

    return entries


def find_cited_keys(vault_path):
    """Scan all .md files for [@citekey...] patterns and return the set of citekeys."""
    cited = set()
    pattern = re.compile(r"\[@([^\]@,;\s]+)")

    for md_file in Path(vault_path).rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8", errors="ignore")
            for match in pattern.finditer(text):
                cited.add(match.group(1).strip())
        except Exception:
            continue

    return cited


def main():
    print("Reading bibliography...")
    all_entries = parse_bib(BIB_FILE)
    print(f"  {len(all_entries)} entries found in .bib file\n")

    print("Scanning vault for citations...")
    cited_keys = find_cited_keys(VAULT_DIR)
    print(f"  {len(cited_keys)} unique citekeys used across all notes\n")

    uncited = {k: v for k, v in all_entries.items() if k not in cited_keys}

    print(f"{'─' * 72}")
    print(f"  {len(uncited)} UNCITED SOURCES  ({len(all_entries) - len(uncited)} cited)")
    print(f"{'─' * 72}\n")

    # Sort by author then year
    sorted_uncited = sorted(uncited.items(), key=lambda x: (x[1]["author"].lower(), x[1]["year"]))

    for citekey, info in sorted_uncited:
        year = f" ({info['year']})" if info["year"] else ""
        print(f"  [{citekey}]")
        print(f"    {info['author']}{year} — {info['title'][:80]}")
        print()

    # Also write to a text file next to the script
    out_path = Path(__file__).parent / "uncited_sources.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"UNCITED SOURCES ({len(uncited)} of {len(all_entries)})\n")
        f.write("=" * 72 + "\n\n")
        for citekey, info in sorted_uncited:
            year = f" ({info['year']})" if info["year"] else ""
            f.write(f"[{citekey}]\n")
            f.write(f"  {info['author']}{year} — {info['title']}\n\n")

    print(f"Results also saved to: {out_path}")


if __name__ == "__main__":
    main()