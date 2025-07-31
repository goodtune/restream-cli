# AGENTS.md

## Project intent
Build and evolve a Python CLI named `restream.io` to interact with the Restream.io REST API. Initial implemented surface: OAuth2 login, profile retrieval, channel listing/getting, event listing, and version reporting. The tool must be easily extensible with new endpoints, safe for local development, and automatable via AI agents.

## Language & ecosystem
- Primary language: **Python 3.11+**.
- Use `uv` as the project/virtual environment & dependency manager. Bootstrap with `uv init`, add deps with `uv add`, sync with `uv sync`, and run via `uv run restream.io <subcommand>`.
- Source layout: package code lives under `src/restream_io` to prevent accidental local imports. `pyproject.toml` is configured to discover packages under `src`.

## Versioning
- **Dynamic versioning** via `setuptools_scm`. No hardcoded `__version__` in source. Versions are derived from git tags (e.g., `v0.1.0` → version `0.1.0`). Additional commits result in dev/local suffixes.  
- At runtime, use `importlib.metadata.version("restream.io")` to get the installed version. If the package is not installed (development environment), fallback to calling `setuptools_scm.get_version(...)` with appropriate `root`/`relative_to` so the version still reflects git state. Provide a safe fallback of `0.0.0+unknown` on failure.

## Dependencies
- Must use `requests` for all HTTP interactions.  
- Instantiate and reuse a single `requests.Session` per invocation to benefit from connection pooling and consistent headers.  
- Use `responses` in test suites to mock HTTP endpoints; **no real network calls** in unit tests.  

## Authentication
- OAuth2 Authorization Code flow is required.  
- Implement local redirect URI listener on `localhost` to capture authorization code.  
- Use `state` parameter to mitigate CSRF attacks.  
- Optional: support PKCE (code verifier/challenge) to future-proof and avoid requiring a client secret for local flows.  
- Tokens (access + refresh) must be stored securely in user config (e.g., `~/.config/restream.io/`), with file permissions restricted.  
- Before each API request, validate token expiry and use refresh token when necessary to obtain a new access token.  

## CLI conventions
- Use the standard library (`argparse`) for argument parsing to minimize dependencies unless a justified migration to richer CLI frameworks (like `click`/`typer`) is proposed.  
- Command hierarchy:  
  - `restream.io login`  
  - `restream.io profile`  
  - `restream.io channel list`  
  - `restream.io channel get <id>`  
  - `restream.io event list`  
  - `restream.io version`  
- Support `--json` for machine-readable output.  
- Support verbosity flags (`-v`/`--verbose`) for debugging details.  
- Exit codes should be meaningful (0 success, non-zero for errors).  

## Error handling
- Wrap API errors into user-friendly messages.  
- Retry transient failures (network / 5xx) with exponential backoff.  
- Clear differentiation between authentication issues, not-found, and rate limits.  

## Testing
- All new functionality must be accompanied by tests.  
- Use `pytest`.  
- Mock all external HTTP calls using `responses`.  
- Provide fixtures for repeated patterns (tokens, sample API payloads).  
- Cover positive, negative, and edge cases.  
- Ensure version command can be tested in both installed and source environments.  

## Style & quality
- Follow PEP 8; functions should be small and focused.  
- No global mutable state except where explicitly documented (e.g., shared session per invocation).  
- Docstrings required for public functions explaining intent, not just signatures.  
- Avoid leaking secrets in logs; mask tokens if logged.  

## Extensibility
- New API endpoints are added in `restream_io/api.py` with corresponding CLI subcommands.  
- Tests must be added in parallel.  
- Configuration schema evolution should be backward compatible; migrations must be explicit.  

## Security
- Do not commit client secrets or access/refresh tokens into version control.  
- Prefer environment variables for volatile secrets in CI contexts.  

## Commit conventions
- Use imperative commit messages: e.g., "Add channel get command" not "Added" or "Adding".  
- Update changelog or release notes when bumping versions.  

## Release
- Tag releases in git with a `v` prefix (e.g., `v1.2.3`).  
- Ensure CI fetches tags so `setuptools_scm` can compute version.  

## Developer workflow
1. Bootstrap: `uv init && uv add requests responses pytest setuptools_scm && uv sync`.  
2. (Optional) Install editable: `uv run python -m pip install -e .`.  
3. Run tests: `uv run pytest`.  
4. Add new command: extend `restream_io/api.py` + CLI + tests.  
5. Commit, tag, push.  

## Local development fallbacks
- If `importlib.metadata.version` fails because the package isn’t installed, use `setuptools_scm.get_version` with `relative_to=__file__` to compute version from git state.  
