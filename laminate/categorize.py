import json
from typing import Literal
from pydantic import BaseModel

from gitlog import Commit
from llm import generate

Category = Literal["Added", "Changed", "Fixed", "Removed"]

DEFAULT_BATCH_SIZE = 15

SYSTEM_PROMPT = """You are a precise changelog generator. You will be \
given a numbered list of raw git commit subjects. For each one, in the \
same order, produce:
- "category": exactly one of "Added", "Changed", "Fixed", or "Removed"
- "description": a short, human-readable rewrite of the commit, written \
for someone reading a changelog (not a git log) - no ticket numbers, \
no "fix:"/"feat:" prefixes, plain sentence case.

Respond with ONLY a JSON array, one object per commit, in the same \
order as the input. No markdown fences, no commentary, no extra text \
before or after the array."""


class CategorizedEntry(BaseModel):
    category: Category
    description: str
    short_hash: str


class CategorizeError(Exception):
    """Raised when a batch can't be categorized at all (not even with
    the per-commit fallback)."""
    pass


def _chunk(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _build_prompt(commits: list[Commit]) -> str:
    lines = [f"{i + 1}. {c.subject}" for i, c in enumerate(commits)]
    return "\n".join(lines)


def _strip_fences(text: str) -> str:
    """Prevents the model from adding user-focused markdown "fences" to the JSON array."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def _fallback_entries(commits: list[Commit]) -> list[CategorizedEntry]:
    return [
        CategorizedEntry(
            category="Changed",
            description=c.subject,
            short_hash=c.short_hash,
        )
        for c in commits
    ]


def _categorize_batch(commits: list[Commit]) -> list[CategorizedEntry]:
    prompt = _build_prompt(commits)

    try:
        response = generate(prompt, system_prompt=SYSTEM_PROMPT, max_tokens=1024)
    except Exception as e:
        print(f"[categorize] LLM call failed, using fallback for this batch: {e}")
        return _fallback_entries(commits)

    cleaned = _strip_fences(response)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        print("[categorize] model returned invalid JSON, using fallback for this batch")
        return _fallback_entries(commits)

    if not isinstance(parsed, list) or len(parsed) != len(commits):
        print(
            f"[categorize] expected {len(commits)} entries, got "
            f"{len(parsed) if isinstance(parsed, list) else 'non-list'} "
            "- using fallback for this batch"
        )
        return _fallback_entries(commits)

    entries = []
    for commit, item in zip(commits, parsed):
        category = item.get("category")
        description = item.get("description")

        if category not in ("Added", "Changed", "Fixed", "Removed") or not description:
            entries.append(
                CategorizedEntry(
                    category="Changed",
                    description=commit.subject,
                    short_hash=commit.short_hash,
                )
            )
            continue

        entries.append(
            CategorizedEntry(
                category=category,
                description=description,
                short_hash=commit.short_hash,
            )
        )

    return entries


def categorize_commits(
    commits: list[Commit],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[CategorizedEntry]:
    if not commits:
        return []

    all_entries: list[CategorizedEntry] = []
    batches = _chunk(commits, batch_size)

    for i, batch in enumerate(batches):
        print(f"[categorize] processing batch {i + 1}/{len(batches)} ({len(batch)} commits)...")
        all_entries.extend(_categorize_batch(batch))

    return all_entries

# testing purposes only
if __name__ == "__main__":
    from gitlog import get_commits

    commits = get_commits()[:5]
    if not commits:
        print("No commits found in current directory.")
    else:
        print(f"Categorizing {len(commits)} commits...\n")
        results = categorize_commits(commits)
        for entry in results:
            print(f"[{entry.category}] {entry.description}  ({entry.short_hash})")