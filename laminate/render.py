

from collections import defaultdict

from laminate.categorize import CategorizedEntry

# Keep a Changelog's standard category order
CATEGORY_ORDER = ["Added", "Changed", "Fixed", "Removed"]


def render_changelog(entries: list[CategorizedEntry]) -> str:
    lines = [
        "# Changelog",
        "",
        "All notable changes to this project will be documented in this file.",
        "",
        "The format is based on Keep a Changelog, and this project "
        "adheres to Semantic Versioning.",
        "",
        "## [Unreleased]",
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


def write_changelog(content: str, output_path: str = "changelog.md") -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


# testing purposes only
if __name__ == "__main__":
    from laminate.gitlog import get_commits
    from laminate.categorize import categorize_commits

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