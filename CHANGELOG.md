# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2026-10-08

### Added
- Added an `--append` option to prepend new contents to the top of the changelog.

### Changed
- Updated the README with info about `--append` and remove the note about `--range` since it was just a result of me not testing properly.

# [0.1.5] – 2026-10-07

### Changed
- Fixed some minor grammatical errors in README and added a note about the `--range` option.

## [0.1.4] - 2026-10-05

### Added
- Added `--version` option to view the installed package version.

### Changed
- Updated the README to inform you where the `models/` folder should actually go when installing via pip.

### Fixed
- Fixed an issue with Laminate not telling you where the `models/` folder actually goes when it can't find a model.

## [0.1.3]

- Changes were not logged (oops)

## [0.1.2] - 2026-10-03

### Added
- Added GitHub, License, and a proper changelog link to README.

### Changed
- Changed license from GPL to MIT license.

## [0.1.1] - 2026-10-03

### Changed
- Updated README with useful instructions.

## [0.1.0] - 2026-10-03

### Added
- Added new configuration file for publishing, created python-publish.yml, and integrated full CLI pipeline.
- Added Laminate branding to README and logo.
- Added dependencies and scripts for Laminate project structure.

### Changed
- Updated .gitignore, pyproject.toml, and renamed --batch_size to --batch-size.
- Added commit grouping.
- Changed cli.py to use a better interface.
- Added package installation to gitignore.
- Added models folder contents to gitignore.

### Fixed
- Removed unused variable from cli.py and corrected default output value.
