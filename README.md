# restream.io CLI

Python command-line tool to interact with the Restream.io API.

## Bootstrapping

Requires [`uv`](https://docs.astral.sh/uv/) installed.

```bash
uv sync
```

## Basic commands

### Public endpoints (no authentication required)
- `restream.io platforms` - list available streaming platforms
- `restream.io servers` - list available streaming servers

### Authentication
- `restream.io login` - perform OAuth2 login flow (opens browser, listens locally)

### User profile
- `restream.io profile` - show user profile

### Channel management
- `restream.io channel list` - list channels
- `restream.io channel get <id>` - fetch specific channel
- `restream.io channel set <id>` - update channel settings
- `restream.io channel meta get` - get channel metadata
- `restream.io channel meta set` - update channel metadata

### Event management
- `restream.io event list` - list events

### Utility
- `restream.io version` - show dynamic version derived from git tags

## Configuration

### Storage Location

Tokens and configuration are stored securely in the user's platform-appropriate config directory:
- **Linux/macOS**: `~/.config/restream.io/`
- **Windows**: `%APPDATA%\restream.io\`

The configuration directory location can be overridden using the `RESTREAM_CONFIG_PATH` environment variable.

### Environment Variables

The following environment variables are required for OAuth2 authentication:

- `RESTREAM_CLIENT_ID`: OAuth2 client ID (required)
- `RESTREAM_CLIENT_SECRET`: OAuth2 client secret (required)

Additional optional configuration:

- `RESTREAM_CONFIG_PATH`: Override the default configuration directory path

Before using the login command, ensure both authentication variables are set:

```bash
export RESTREAM_CLIENT_ID="your_client_id_here"
export RESTREAM_CLIENT_SECRET="your_client_secret_here"
restream.io login
```

### Security

- Configuration directory is created with `0o700` permissions (owner read/write/execute only)
- Token files are created with `0o600` permissions (owner read/write only)
- Tokens are stored in JSON format in `tokens.json` within the config directory

## Development

Run tests:

```bash
uv run pytest
```

## Roadmap

See `AGENTS.md` for AI agent instructions and extension points.
