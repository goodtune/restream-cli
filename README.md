# restream.io CLI

Python command-line tool to interact with the Restream.io API.

## Bootstrapping

Requires [`uv`](https://docs.astral.sh/uv/) installed.

```bash
uv sync
```

## Basic commands

- `restream.io login` - perform OAuth2 login flow (opens browser, listens locally).  
- `restream.io profile` - show user profile.  
- `restream.io channel list` - list channels.  
- `restream.io channel get <id>` - fetch specific channel.  
- `restream.io event list` - list events.  
- `restream.io version` - show dynamic version derived from git tags.

## Development

Run tests:

```bash
uv run pytest
```

## Configuration

Tokens and configuration are stored in the user's config directory. Environment variables can override: `RESTREAM_CLIENT_ID`, `RESTREAM_CLIENT_SECRET`.

## Roadmap

See `AGENTS.md` for AI agent instructions and extension points.
