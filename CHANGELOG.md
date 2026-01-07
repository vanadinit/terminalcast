# Changelog

All notable changes to this project will be documented in this file.

## [1.3.1] - 2026-01-07

### Added
- Add support for specifying a virtual host URL via `--video-url` CLI argument or `TERMINALCAST_VIDEO_URL` environment variable (useful for reverse proxies).

## [1.3.0] - 2026-01-07

### Added
- Add support for specifying a fixed port via `--port` CLI argument or `TERMINALCAST_PORT` environment variable.

## [1.2.2] - 2026-01-03

### Fixed
- Correctly handle audio stream index when creating temporary files.

### Internal
- Add automated CI pipeline for linting, type checking, and testing.
- Introduce development tools (`ruff`, `mypy`, `pytest`, `pre-commit`) and `Makefile` for improved code quality and developer experience.

## [1.2.1] - 2026-01-03

### Added
- Expose `run_http_server` and `NoChromecastAvailable` for library usage.

### Internal
- Update GitHub Actions publish workflow to use trusted publishing.

## [1.2.0] - 2026-01-03

### Added
- Add progress bar for video conversion when selecting a different audio track.
- Add support for custom temporary directory via `TERMINALCAST_TMP_DIR` environment variable.

## [1.1.0] - 2026-01-03

### Added
- Add support for `known_hosts` via CLI argument or environment variable to improve device discovery.
- Improve request logging with a cleaner, more informative format.

### Fixed
- Replace deprecated `paste` server with `waitress` to fix streaming issues and modernize the stack.

### Internal
- Migrate packaging from `setup.py` to `pyproject.toml`.
- Update `pychromecast` and `zeroconf` dependencies.

## [1.0.0] - 2024-01-01

- Initial release.
