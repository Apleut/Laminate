import typer

from concurrent.futures import ThreadPoolExecutor

from rich.console import Console

from .gitlog import get_commits, GitLogError
from .categorize import categorize_commits
from .llm import LLMError
from .render import render_changelog, write_changelog

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def generate(
    repo: str = typer.Option(".", help="Path to the git repository."),
    since: str = typer.Option(None, help="Only include commits after this date, e.g. 2026-01-01."),
    until: str = typer.Option(None, help="Only include commits before this date, e.g. 2026-01-01."),
    commit_range: str = typer.Option(None, "--range", help="A git commit range, e.g. v1.0.0..v1.1.0. Overrides --since/--until."),
    output: str = typer.Option("changelog.md", help="Path to write the generated changelog to."),
    batch_size: int = typer.Option(15, help="Number of commits sent to the LLM per batch."),
    release: str = typer.Option(None, "--release", help="Version number for this release, e.g. 1.1.0. If omitted, the changelog is headed [Unreleased]."),
):
    if repo != ".":
        typer.echo(f"Reading commits from '{repo}'...")
    else:
        typer.echo("Reading commits from working directory...")


    try:
        commits = get_commits(
            repo_path=repo,
            since=since,
            until=until,
            commit_range=commit_range,
        )
    except GitLogError as e:
        typer.echo(f"Error reading git log: {e}", err=True)
        raise typer.Exit(code=1)

    if not commits:
        typer.echo("No commits found for the given range - nothing to do.")
        raise typer.Exit(code=0)

    console.print(f"Found {len(commits)} commits.")

    status = None

    try:
        with console.status(
            "Categorizing commits with the local model...",
            spinner="dots",
        ) as status:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    categorize_commits,
                    commits,
                    batch_size=batch_size,
                    on_progress=lambda current, total, count: status.update(
                        f"Categorizing commits... batch {current}/{total} ({count} commits)"
                    ),
                )
                entries = future.result()
    except LLMError as e:
        typer.echo(
            f"Error loading or running the local model: {e}",
            err=True,
        )
        raise typer.Exit(code=1)

    changelog = render_changelog(entries, version=release)
    write_changelog(changelog, output)

    typer.echo(f"\nDone. Changelog written to {output}")


if __name__ == "__main__":
    app()