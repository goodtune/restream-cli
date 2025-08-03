import json
import sys
from importlib.metadata import version

import attrs
import click

from .api import RestreamClient
from .auth import perform_login
from .errors import APIError, AuthenticationError
from .schemas import (
    Channel,
    ChannelMeta,
    ChannelSummary,
    EventsHistoryResponse,
    Platform,
    Profile,
    Server,
    StreamEvent,
    StreamKey,
)


class RestreamCommand(click.Command):
    """Custom command class that adds common options and handles API errors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add --json option to all commands
        self.params.append(
            click.Option(["--json"], is_flag=True, help="Output results in JSON format")
        )

    def invoke(self, ctx, *args, **kwargs):
        """Override invoke to handle common error patterns."""
        try:
            return super().invoke(ctx, *args, **kwargs)
        except APIError as e:
            _handle_api_error(e)
        except AuthenticationError as e:
            click.echo(f"Authentication error: {e}", err=True)
            click.echo("Please run 'restream.io login' first.", err=True)
            sys.exit(1)


def _attrs_to_dict(obj):
    """Convert attrs objects to dict for JSON serialization."""
    if attrs.has(obj):
        return attrs.asdict(obj)
    elif isinstance(obj, list):
        return [_attrs_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _attrs_to_dict(value) for key, value in obj.items()}
    else:
        return obj


def _format_human_readable(data):
    """Format data for human-readable output."""
    if isinstance(
        data,
        (
            Profile,
            Channel,
            ChannelSummary,
            ChannelMeta,
            StreamEvent,
            EventsHistoryResponse,
            Platform,
            Server,
            StreamKey,
        ),
    ):
        click.echo(str(data))
    elif (
        isinstance(data, list)
        and data
        and isinstance(data[0], (StreamEvent, ChannelSummary, Platform, Server))
    ):
        # Handle lists of events or channel summaries
        for i, item in enumerate(data, 1):
            click.echo(f"{i}. {item}")
            if i < len(data):
                click.echo()
    else:
        # Fallback to JSON for other data types
        click.echo(json.dumps(_attrs_to_dict(data), indent=2, default=str))


def _get_client():
    """Get a configured RestreamClient instance."""
    try:
        return RestreamClient.from_config()
    except AuthenticationError as e:
        click.echo(f"Authentication error: {e}", err=True)
        click.echo("Please run 'restream.io login' first.", err=True)
        sys.exit(1)


def _handle_api_error(e: APIError):
    """Handle API errors consistently."""
    click.echo(f"API error: {e}", err=True)
    sys.exit(1)


def _output_result(data, json_output: bool):
    """Output result in the appropriate format."""
    # Convert attrs objects to dict for JSON serialization
    serializable_data = _attrs_to_dict(data)

    if json_output:
        click.echo(json.dumps(serializable_data, indent=2, default=str))
    else:
        # Format data for human-readable output
        _format_human_readable(data)


@click.command()
def version_cmd():
    """Show version information."""
    click.echo(version("restream.io"))


@click.command()
@click.option(
    "-p",
    "--port",
    type=int,
    default=12000,
    help="Port for local OAuth callback server (default: 12000)",
)
def login(port):
    """Perform OAuth2 login flow."""
    try:
        success = perform_login(redirect_port=port)
        if success:
            sys.exit(0)
        else:
            click.echo("Login failed", err=True)
            sys.exit(1)
    except AuthenticationError as e:
        click.echo(f"Login failed: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nLogin cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error during login: {e}", err=True)
        sys.exit(1)


@click.command(cls=RestreamCommand)
def profile(json):
    """Fetch user profile from Restream API."""
    client = _get_client()
    profile_data = client.get_profile()
    _output_result(profile_data, json)


@click.command("list", cls=RestreamCommand)
def channel_list(json):
    """List channels."""
    client = _get_client()
    channels = client.list_channels()
    _output_result(channels, json)


@click.command("get", cls=RestreamCommand)
@click.argument("channel_id", required=True)
def channel_get(channel_id, json):
    """Get details for a specific channel."""
    try:
        client = _get_client()
        channel = client.get_channel(channel_id)
        _output_result(channel, json)
    except APIError as e:
        if e.status_code == 404:
            click.echo(f"Channel not found: {channel_id}", err=True)
            sys.exit(1)
        else:
            raise


@click.command("list", cls=RestreamCommand)
def event_list(json):
    """List events."""
    client = _get_client()
    events = client.list_events()
    _output_result(events, json)


@click.command("get", cls=RestreamCommand)
@click.argument("event_id", required=True)
def event_get(event_id, json):
    """Get details for a specific event."""
    try:
        client = _get_client()
        event = client.get_event(event_id)
        _output_result(event, json)
    except APIError as e:
        if e.status_code == 404:
            click.echo(f"Event not found: {event_id}", err=True)
            sys.exit(1)
        else:
            raise


@click.command("in-progress", cls=RestreamCommand)
def event_in_progress(json):
    """List currently in-progress events."""
    client = _get_client()
    events = client.list_events_in_progress()
    _output_result(events, json)


@click.command("upcoming", cls=RestreamCommand)
@click.option(
    "--source", type=int, help="Filter by source type (1=Studio, 2=Encoder, 3=Video)"
)
@click.option("--scheduled", is_flag=True, help="Show only scheduled events")
def event_upcoming(source, scheduled, json):
    """List upcoming events."""
    client = _get_client()
    events = client.list_events_upcoming(
        source=source, scheduled=scheduled if scheduled else None
    )
    _output_result(events, json)


@click.command("history", cls=RestreamCommand)
@click.option("--page", type=int, default=1, help="Page number (default: 1)")
@click.option(
    "--limit", type=int, default=10, help="Number of events per page (default: 10)"
)
def event_history(page, limit, json):
    """List historical events."""
    client = _get_client()
    response = client.list_events_history(page=page, limit=limit)
    _output_result(response, json)


@click.command("get", cls=RestreamCommand)
def stream_key_get(json):
    """Get user's primary stream key."""
    client = _get_client()
    stream_key = client.get_stream_key()
    _output_result(stream_key, json)


@click.command("stream-key", cls=RestreamCommand)
@click.argument("event_id", required=True)
def event_stream_key(event_id, json):
    """Get stream key for a specific event."""
    try:
        client = _get_client()
        stream_key = client.get_event_stream_key(event_id)
        _output_result(stream_key, json)
    except APIError as e:
        if e.status_code == 404:
            click.echo(f"Event not found: {event_id}", err=True)
            sys.exit(1)
        else:
            raise


@click.command(cls=RestreamCommand)
def platforms(json):
    """List all available streaming platforms."""
    client = _get_client()
    platforms_data = client.get_platforms()
    _output_result(platforms_data, json)


@click.command(cls=RestreamCommand)
def servers(json):
    """List all available ingest servers."""
    client = _get_client()
    servers_data = client.get_servers()
    _output_result(servers_data, json)


@click.command("set")
@click.argument("channel_id", required=True)
@click.option("--active/--inactive", default=None, help="Enable or disable the channel")
@click.pass_context
def channel_set(ctx, channel_id, active):
    """Update channel settings."""
    if active is None:
        click.echo("Please specify --active or --inactive", err=True)
        sys.exit(1)

    try:
        client = _get_client()
        client.update_channel(channel_id, active)
        status = "enabled" if active else "disabled"
        click.echo(f"Channel {channel_id} {status} successfully")
    except APIError as e:
        if e.status_code == 404:
            click.echo(f"Channel not found: {channel_id}", err=True)
            sys.exit(1)
        else:
            _handle_api_error(e)


@click.command("get", cls=RestreamCommand)
@click.argument("channel_id", required=True)
def channel_meta_get(channel_id, json):
    """Get channel metadata."""
    try:
        client = _get_client()
        meta = client.get_channel_meta(channel_id)
        _output_result(meta, json)
    except APIError as e:
        if e.status_code == 404:
            click.echo(f"Channel not found: {channel_id}", err=True)
            sys.exit(1)
        else:
            raise


@click.command("set")
@click.argument("channel_id", required=True)
@click.option("--title", required=True, help="Channel title")
@click.option("--description", help="Channel description")
@click.pass_context
def channel_meta_set(ctx, channel_id, title, description):
    """Update channel metadata."""
    try:
        client = _get_client()
        client.update_channel_meta(channel_id, title, description)
        click.echo(f"Channel {channel_id} metadata updated successfully")
    except APIError as e:
        if e.status_code == 404:
            click.echo(f"Channel not found: {channel_id}", err=True)
            sys.exit(1)
        else:
            _handle_api_error(e)


@click.group()
def channel_meta():
    """Channel metadata management commands."""
    pass


@click.group()
def cli():
    """CLI for Restream.io API"""
    pass


@click.group()
def channel():
    """Channel management commands."""
    pass


@click.group()
def event():
    """Event management commands."""
    pass


@click.group()
def stream_key():
    """Stream key management commands."""
    pass


# Add commands to groups
channel.add_command(channel_list)
channel.add_command(channel_get)
channel.add_command(channel_set)
channel_meta.add_command(channel_meta_get)
channel_meta.add_command(channel_meta_set)
channel.add_command(channel_meta, name="meta")
event.add_command(event_list)
event.add_command(event_get)
event.add_command(event_in_progress)
event.add_command(event_upcoming)
event.add_command(event_history)
event.add_command(event_stream_key)
stream_key.add_command(stream_key_get)

# Add commands to main CLI
cli.add_command(login)
cli.add_command(profile)
cli.add_command(platforms)
cli.add_command(servers)
cli.add_command(channel)
cli.add_command(event)
cli.add_command(stream_key)
cli.add_command(version_cmd, name="version")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":  # allow direct execution for tests
    main()
