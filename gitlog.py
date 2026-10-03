import subprocess
from pydantic import BaseModel


FIELD_SEP = "\x1f"
RECORD_SEP = "\x1e"


class Commit(BaseModel):
    hash: str
    short_hash: str
    author: str
    date: str  # ISO 8601, e.g. 2026-09-30T14:22:01-05:00
    subject: str

class GitLogError(Exception):
    pass

def get_commits(
    repo_path: str = ".",
    since: str | None = None,
    until: str | None = None,
    commit_range: str | None = None,
) -> list[Commit]:
    """
    Returns commits from the given repo, newest first.

    repo_path: path to the git repository (defaults to current directory)
    since / until: date bounds, e.g. since="2026-01-01"
    commit_range: a git revision range, e.g. "v1.0.0..v1.1.0" - if given,
        this takes priority over since/until

    Raises GitLogError if the path isn't a git repo, the range is
    invalid, or git itself isn't installed/on PATH.
    """
    pretty_format = FIELD_SEP.join(["%H", "%h", "%an", "%aI", "%s"]) + RECORD_SEP

    cmd = ["git", "-C", repo_path, "log", f"--pretty=format:{pretty_format}"]

    if commit_range:
        cmd.append(commit_range)
    else:
        if since:
            cmd.append(f"--since={since}")
        if until:
            cmd.append(f"--until={until}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise GitLogError(
            "git doesn't appear to be installed, or isn't on your PATH."
        )
    except subprocess.CalledProcessError as e:
        raise GitLogError(
            f"git log failed (is '{repo_path}' a git repo, and is the "
            f"commit range valid?): {e.stderr.strip()}"
        )

    raw_output = result.stdout
    if not raw_output.strip():
        return []

    commits = []
    for record in raw_output.split(RECORD_SEP):
        record = record.strip()
        if not record:
            continue

        fields = record.split(FIELD_SEP)
        if len(fields) != 5:
            continue

        full_hash, short_hash, author, date, subject = fields
        commits.append(
            Commit(
                hash=full_hash,
                short_hash=short_hash,
                author=author,
                date=date,
                subject=subject,
            )
        )

    return commits


if __name__ == "__main__":
    commits = get_commits()
    print(f"Found {len(commits)} commits:\n")
    for c in commits[:10]:
        print(f"{c.short_hash}  {c.date}  {c.author}: {c.subject}")
    if len(commits) > 10:
        print(f"... and {len(commits) - 10} more")