import json
import logging

from typing import Callable, Literal

from pydantic import BaseModel

from .gitlog import Commit
from .llm import get_llm

logger = logging.getLogger(__name__)

Category = Literal["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]

DEFAULT_BATCH_SIZE = 15

SYSTEM_PROMPT = """You are a precise changelog generator.

You will be given a numbered list of raw git commit subjects.

Your job is to turn these commits into concise, human-readable changelog entries.

Related commits may be GROUPED together when they describe the same user-facing
change, feature, bug fix, or piece of functionality. A group can contain one
or multiple commits.

Do not group unrelated changes merely because they are similar in implementation.

Prefer a small number of meaningful changelog entries over one entry per commit.
Intermediate implementation commits, refactors, tests, and small follow-up fixes
may be grouped with the larger change they belong to.

For each changelog entry, produce:

- "category": exactly one of "Added", "Changed", "Deprecated", "Removed", "Fixed" or "Security"
- "description": a short, human-readable rewrite of the grouped commits,
  written for someone reading a changelog rather than a git log
- "commits": a list of the input commit numbers belonging to this entry

Category definitions:
- Added: a new feature, capability, command, option, or user-facing functionality
- Changed: a modification to existing behavior or functionality
- Deprecated: functionality being phased out or marked for future removal
- Removed: functionality that has been removed
- Fixed: a bug fix or correction to broken behavior
- Security: a security vulnerability fix or security-related change

For descriptions:
- no ticket numbers
- no "fix:" or "feat:" prefixes
- plain sentence case
- describe the user-facing result rather than implementation details

Every input commit number must appear in exactly one group.
Do not omit commits.
Do not duplicate commit numbers.

Respond with ONLY a JSON array.
No markdown fences, no commentary, and no extra text before or after the array.

Example:

[
  {
    "category": "Added",
    "description": "Added user authentication and OAuth support.",
    "commits": [1, 2, 4]
  },
  {
    "category": "Fixed",
    "description": "Fixed authentication callback handling.",
    "commits": [3]
  }
]
"""


class CategorizedEntry(BaseModel):
    category: Category
    description: str


class CategorizeError(Exception):
    """Raised when a batch can't be categorized at all."""

    pass


def _chunk(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def _build_prompt(commits: list[Commit]) -> str:
    lines = [
        f"{i + 1}. {c.subject}"
        for i, c in enumerate(commits)
    ]
    return "\n".join(lines)


def _strip_fences(text: str) -> str:
    """Prevents the model from adding markdown fences around the JSON."""
    text = text.strip()

    if text.startswith("```"):
        newline_idx = text.find("\n")
        if newline_idx != -1:
            text = text[newline_idx + 1:]
        else:
            text = text[3:]

    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return text.strip()


def _fallback_entries(commits: list[Commit]) -> list[CategorizedEntry]:
    return [
        CategorizedEntry(
            category="Changed",
            description=c.subject,
        )
        for c in commits
    ]


def _categorize_batch(
    commits: list[Commit],
    llm,
) -> list[CategorizedEntry]:
    """Categorize and intelligently group a batch of commits."""

    prompt = _build_prompt(commits)

    try:
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        text = response["choices"][0]["message"]["content"]

    except Exception as e:
        logger.warning(f"LLM error: {e}")
        return _fallback_entries(commits)

    text = _strip_fences(text)

    try:
        parsed = json.loads(text)

    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON: {e}")
        return _fallback_entries(commits)

    if not isinstance(parsed, list):
        logger.warning(
            f"Expected list, got {type(parsed).__name__}"
        )
        return _fallback_entries(commits)

    entries: list[CategorizedEntry] = []
    used_commits: set[int] = set()

    for item in parsed:
        try:
            category = item["category"]
            description = item["description"]
            commit_indices = item["commits"]

            if not isinstance(commit_indices, list):
                raise ValueError("commits must be a list")

            if not commit_indices:
                raise ValueError("commits list cannot be empty")

            normalized_indices = []

            for index in commit_indices:
                if not isinstance(index, int):
                    raise ValueError(
                        f"commit index must be an integer, got {index!r}"
                    )

                if not 1 <= index <= len(commits):
                    raise ValueError(
                        f"commit index {index} is out of range"
                    )

                if index in used_commits:
                    raise ValueError(
                        f"commit {index} appears in multiple groups"
                    )

                normalized_indices.append(index)

            entry = CategorizedEntry(
                category=category,
                description=description,
            )

            entries.append(entry)
            used_commits.update(normalized_indices)

        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Invalid grouped entry: {e}")
            continue

    missing_commits = [
        i
        for i in range(1, len(commits) + 1)
        if i not in used_commits
    ]

    if missing_commits:
        logger.info(
            f"Model omitted {len(missing_commits)} commits; "
            "using fallback entries for them"
        )

        for index in missing_commits:
            entries.append(
                CategorizedEntry(
                    category="Changed",
                    description=commits[index - 1].subject,
                )
            )

    if not entries:
        return _fallback_entries(commits)

    return entries


def categorize_commits(
    commits: list[Commit],
    batch_size: int = DEFAULT_BATCH_SIZE,
    on_progress: Callable[[int, int, int], None] | None = None,
) -> list[CategorizedEntry]:
    if not commits:
        return []

    llm = get_llm()
    all_entries: list[CategorizedEntry] = []
    batches = _chunk(commits, batch_size)

    for i, batch in enumerate(batches):
        if on_progress:
            on_progress(
                i + 1,
                len(batches),
                len(batch),
            )

        all_entries.extend(
            _categorize_batch(batch, llm)
        )

    return all_entries

# testing purposes only
if __name__ == "__main__":
    from .gitlog import get_commits

    commits = get_commits()[:15]

    if not commits:
        print("No commits found in current directory.")
    else:
        print(f"Categorizing {len(commits)} commits...\n")
        results = categorize_commits(commits)
        for entry in results:
            print(
                f"[{entry.category}] "
                f"{entry.description}"
            )
