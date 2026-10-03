# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-03

### Added
- Added Deprecated and Security categories, corrected the category order, and changed the changelog filename to adhere to Keep a Changelog conventions.
- Implemented full CLI pipeline in cli.py.
- Created `__init__.py` for the package.
- Added package installation instructions to gitignore.
- Included the rich library in the project dependencies.
- Added the laminate logo and updated the README with Laminate branding.
- Created categorize.py for organizing commits.
- Added a note about installing dependencies in the README file.
- Created llm.py for description functionality.
- Added new project files and dependencies including llama-cpp-python and typer.
- Added commit grouping to prevent needless changelog entries.
- Generated this changelog using Laminate!

### Changed
- Removed an unnecessary variable from cli.py and corrected the default output value.
- Updated cli.py to use a more efficient interface.
- Changed the `--batch_size` flag to `--batch-size`

### Removed
- Removed the original changelog file used for testing purposes.
- Excluded models folder from git tracking.

### Fixed
- Resolved import errors caused by changes in folder structure.
- Fixed import errors resulting from folder restructuring