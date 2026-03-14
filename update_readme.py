#!/usr/bin/env python3
"""
Scan TIL markdown files, generate README.md index and Atom feed.

Usage:
    python update_readme.py --repo https://github.com/USER/TIL [--rewrite]

Without --rewrite, prints README to stdout.
With --rewrite, overwrites README.md and feed.xml in place.
"""

import argparse
import datetime
import os
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parent

SKIP_DIRS = {".git", ".github", "__pycache__"}


def git_dates(filepath: pathlib.Path) -> tuple[str, str]:
    """Return (created, updated) ISO dates from git log."""
    result = subprocess.run(
        ["git", "log", "--format=%aI", "--follow", "--", str(filepath)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    dates = result.stdout.strip().splitlines()
    if not dates:
        # Not yet committed — use file mtime as fallback
        mtime = datetime.datetime.fromtimestamp(
            filepath.stat().st_mtime, tz=datetime.timezone.utc
        )
        iso = mtime.strftime("%Y-%m-%d")
        return iso, iso
    created = dates[-1][:10]  # oldest commit
    updated = dates[0][:10]   # newest commit
    return created, updated


def extract_title(filepath: pathlib.Path) -> str:
    """Extract the first # heading from a markdown file."""
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^#\s+(.+)", line)
            if m:
                return m.group(1).strip()
    return filepath.stem


def collect_tils() -> list[dict]:
    """Walk topic directories and collect TIL entries."""
    tils = []
    for entry in sorted(ROOT.iterdir()):
        if not entry.is_dir() or entry.name in SKIP_DIRS or entry.name.startswith("."):
            continue
        topic = entry.name
        for md in sorted(entry.glob("*.md")):
            title = extract_title(md)
            rel_path = md.relative_to(ROOT)
            created, updated = git_dates(md)
            tils.append(
                {
                    "topic": topic,
                    "title": title,
                    "path": str(rel_path),
                    "created": created,
                    "updated": updated,
                }
            )
    return tils


def build_readme(tils: list[dict]) -> str:
    """Generate README.md content."""
    lines = [
        "# TIL",
        "",
        "> Today I Learned",
        "",
        f"現在 **{len(tils)}** 件の TIL があります。",
        "",
        "---",
        "",
    ]

    by_topic: dict[str, list[dict]] = {}
    for til in tils:
        by_topic.setdefault(til["topic"], []).append(til)

    for topic in sorted(by_topic):
        lines.append(f"## {topic}")
        lines.append("")
        entries = sorted(by_topic[topic], key=lambda t: t["created"], reverse=True)
        for t in entries:
            lines.append(f"- [{t['title']}]({t['path']}) - {t['created']}")
        lines.append("")

    return "\n".join(lines)


def build_atom_feed(tils: list[dict], repo_url: str) -> str:
    """Generate Atom feed XML."""
    repo_url = repo_url.rstrip("/")

    nsmap = "http://www.w3.org/2005/Atom"
    feed = ET.Element("feed", xmlns=nsmap)

    ET.SubElement(feed, "title").text = "TIL"
    ET.SubElement(feed, "id").text = repo_url
    link = ET.SubElement(feed, "link", href=f"{repo_url}/blob/main/feed.xml", rel="self")
    ET.SubElement(feed, "link", href=repo_url, rel="alternate")

    if tils:
        most_recent = max(t["updated"] for t in tils)
        ET.SubElement(feed, "updated").text = most_recent + "T00:00:00Z"

    entries = sorted(tils, key=lambda t: t["updated"], reverse=True)
    for t in entries:
        entry = ET.SubElement(feed, "entry")
        ET.SubElement(entry, "title").text = t["title"]
        entry_url = f"{repo_url}/blob/main/{t['path']}"
        ET.SubElement(entry, "id").text = entry_url
        ET.SubElement(entry, "link", href=entry_url)
        ET.SubElement(entry, "updated").text = t["updated"] + "T00:00:00Z"
        ET.SubElement(entry, "content", type="text").text = f"{t['topic']}: {t['title']}"

    ET.indent(feed, space="  ")
    xml_str = ET.tostring(feed, encoding="unicode", xml_declaration=True)
    return xml_str + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate TIL README and Atom feed")
    parser.add_argument(
        "--repo",
        default="https://github.com/USER/TIL",
        help="GitHub repository URL",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Overwrite README.md and feed.xml in place",
    )
    args = parser.parse_args()

    tils = collect_tils()
    readme = build_readme(tils)
    atom = build_atom_feed(tils, args.repo)

    if args.rewrite:
        (ROOT / "README.md").write_text(readme, encoding="utf-8")
        (ROOT / "feed.xml").write_text(atom, encoding="utf-8")
        print(f"Updated README.md and feed.xml ({len(tils)} TILs)")
    else:
        print(readme)


if __name__ == "__main__":
    main()
