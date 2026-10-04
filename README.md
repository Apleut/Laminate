<div style="text-align: center;">
    <img src="assets/laminate-logo.svg" alt="Laminate Logo" width="200">

<h1>Laminate</h1>

<h4>
    <a href="https://apleut.dev">My Website</a> · 
    <a href="https://github.com/Apleut/Laminate">GitHub</a> · 
    <a href="https://github.com/Apleut/Laminate/blob/main/CHANGELOG.md">Changelog</a> · 
    <a href="https://github.com/Apleut/Laminate/blob/main/LICENSE">License</a>
</h4>

<hr>

</div>

> [!WARNING]
> Laminate is in **early development**. Its output, CLI, and configuration may change between releases.

A CLI that turns your Git history into **release-ready changelogs using a local LLM**.

Instead of manually sorting hundreds of commits into `Added`, `Changed`, `Fixed`, and other categories, Laminate reads your Git history, interprets the changes, and generates a clean [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) compatible document.

## Features

* **Local LLM processing** — your Git history stays on your machine
* **Release-ready Markdown** — generates structured changelogs
* **Automatic categorization** — sorts changes into standard changelog categories
* **Related-commit grouping** — combines related commits into a single entry
* **No API keys required** — Laminate uses a local GGUF model through `llama-cpp-python`
* **Git-aware filtering** — filter commits by date or Git commit range
* **Release support** — generate either an `[Unreleased]` section or a versioned release

## Installation

### PyPI

Install Laminate with pip:

```bash
pip install laminate-cli
```

> [!NOTE]
> The PyPI package is named `laminate-cli`, while the command and Python package are named `laminate`.

### From source

Clone the repository and install it locally:

```bash
git clone https://github.com/Apleut/Laminate.git
cd Laminate
pip install .
```

For development:

```bash
pip install -e .
```

### Windows

`llama-cpp-python` may require a pre-built CPU wheel on Windows.

Install it first with:

```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

Then install Laminate:

```bash
pip install .
```

## Model

Laminate runs a **local GGUF model** using [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python).

Place exactly one `.gguf` model file in:

```text
models/
└── your-model.gguf
```

[Phi-4-mini-instruct](https://huggingface.co/unsloth/Phi-4-mini-instruct-GGUF) is a good pick, and is the model used for Laminate's development.

Laminate automatically finds and loads the model when it runs.

If the `models/` directory does not exist, or contains zero or multiple `.gguf` files, Laminate will stop and explain what needs to be fixed.

The model is intentionally kept separate from the package because GGUF models can be large and have different licensing requirements.

## Usage

From inside a Git repository:

```bash
laminate
```

Laminate will read the repository's commit history, categorize the changes, and write the result to:

```text
CHANGELOG.md
```

For example:

```text
Reading commits from working directory...
Found 42 commits. Categorizing with the local model...
[categorize] processing batch 1/3 (20 commits)...
[categorize] processing batch 2/3 (20 commits)...
[categorize] processing batch 3/3 (2 commits)...

Done. Changelog written to CHANGELOG.md
```

## Options

### `--repo`

Specify the Git repository to read.

```bash
laminate --repo ./my-project
```

Defaults to the current working directory.

### `--since`

Only include commits after a specific date.

```bash
laminate --since 2026-01-01
```

### `--until`

Only include commits before a specific date.

```bash
laminate --until 2026-10-01
```

### `--range`

Process a specific Git commit range.

```bash
laminate --range v1.0.0..v1.1.0
```

`--range` overrides `--since` and `--until`.

This is particularly useful when generating a changelog for a release.

### `--output`

Choose where the generated changelog should be written.

```bash
laminate --output RELEASE_NOTES.md
```

Defaults to:

```text
CHANGELOG.md
```

### `--batch-size`

Control how many commits are sent to the model at once.

```bash
laminate --batch-size 25
```

Larger batches can provide more context to the model, while smaller batches can reduce the amount of context required for each request.

### `--release`

Generate a versioned release section instead of an `[Unreleased]` section.

```bash
laminate --release 1.1.0
```

The resulting header will look like:

```markdown
## [1.1.0] - 2026-10-03
```

Without `--release`, Laminate generates:

```markdown
## [Unreleased]
```

## Example

Suppose your repository contains commits like:

```text
Add user authentication
Fix crash when configuration is missing
Refactor authentication middleware
Remove deprecated login endpoint
Add password reset flow
```

Instead of producing one entry for every commit, Laminate can turn them into something like:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog
and this project adheres to Semantic Versioning.

## [Unreleased]

### Added

- Added user authentication and password reset functionality.

### Changed

- Refactored the authentication middleware.

### Removed

- Removed the deprecated login endpoint.

### Fixed

- Fixed a crash caused by missing configuration.
```

The exact output depends on the Git history and the model being used.

## Supported Categories

Laminate currently uses the standard Keep a Changelog categories:

* **Added**
* **Changed**
* **Deprecated**
* **Removed**
* **Fixed**
* **Security**

Categories that contain no changes are omitted from the final document.

## Privacy

Laminate is designed around **local processing**.

Your Git history is passed to the LLM running on your own machine. Laminate does not require an OpenAI, Anthropic, or other hosted AI API.

The model you download and use is subject to its own license and terms.

## Contributing

Contributions, bug reports, and ideas are welcome.

If you find a problem with Laminate, please open an issue with:

* What you were trying to do
* The command you ran
* The relevant error message
* Your Python version
* Your operating system

Or email me at [me@apleut.dev](me@apleut.dev).

For changes to Laminate itself, pull requests are welcome.

## License

License information will be added before the first stable release.
