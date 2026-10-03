from collections import defaultdict
from datetime import date

from .categorize import CategorizedEntry

CATEGORY_ORDER = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]


def render_changelog(entries: list[CategorizedEntry], version: str | None = None) -> str:
    """
    Renders categorized entries into Keep a Changelog formatted
    markdown.

    version: if given, the header becomes "## [version] - today's date"
        (for cutting an actual release). If omitted, defaults to the
        standard "## [Unreleased]" header.
    """
    if version:
        header = f"## [{version}] - {date.today().isoformat()}"
    else:
        header = "## [Unreleased]"

    lines = [
        "# Changelog",
        "",
        "All notable changes to this project will be documented in this file.",
        "",
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), "
        "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
        "",
        header,
        "",
    ]

    by_category: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        by_category[entry.category].append(entry.description)

    for category in CATEGORY_ORDER:
        if category not in by_category:
            continue
        lines.append(f"### {category}")
        for desc in by_category[category]:
            lines.append(f"- {desc}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_changelog(content: str, output_path: str = "CHANGELOG.md") -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

# testing purposes only
if __name__ == "__main__":
    
    from .gitlog import get_commits
    from .categorize import categorize_commits

    commits = get_commits()[:10]

    if not commits:
        print("No commits found in current directory.")
    else:
        print(f"Categorizing {len(commits)} commits...\n")
        entries = categorize_commits(commits)
        changelog = render_changelog(entries)

        print(changelog)
        write_changelog(changelog)
        print("Wrote changelog.md")