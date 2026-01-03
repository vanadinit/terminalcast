# Terminalcast

## 1.2.1
* Expose `run_http_server` and `NoChromecastAvailable` for library usage
* Update github workflow

## 1.2.0
* Add progress bar for video conversion when selecting a different audio track
* Add support for custom temporary directory via env var `TERMINALCAST_TMP_DIR` (uses RAM disk by default if available)

## 1.1.0
* Replace paste (deprecated) with waitress as WSGI server
* Update pychromecast and zeroconf dependencies
* Improve logging: cleaner output, correct timezone, user-agent simplification
* Add support for `known_hosts` via CLI argument `--known-hosts` or env var `TERMINALCAST_KNOWN_HOSTS`
* Migrate packaging to `pyproject.toml`

## 1.0.0
* First release
