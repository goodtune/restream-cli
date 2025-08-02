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
    ChannelSummary,
    EventsHistoryResponse,
    Profile,
    StreamEvent,
)


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
        data, (Profile, Channel, ChannelSummary, StreamEvent, EventsHistoryResponse)
    ):
        click.echo(str(data))
    elif (
        isinstance(data, list)
        and data
        and isinstance(data[0], (StreamEvent, ChannelSummary))
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


@click.pass_context
def _output_result(ctx, data):
    """Output result in the appropriate format."""
    # Convert attrs objects to dict for JSON serialization
    serializable_data = _attrs_to_dict(data)

    # Check if --json flag was passed at the root level
    json_output = (
        ctx.find_root().obj.get("json", False) if ctx.find_root().obj else False
    )

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


@click.command()
@click.pass_context
def profile(ctx):
    """Fetch user profile from Restream API."""
    try:
        client = _get_client()
        profile_data = client.get_profile()
        _output_result(profile_data)
    except APIError as e:
        _handle_api_error(e)


@click.command("list")
@click.pass_context
def channel_list(ctx):
    """List channels."""
    try:
        client = _get_client()
        channels = client.list_channels()
        _output_result(channels)
    except APIError as e:
        _handle_api_error(e)


@click.command("get")
@click.argument("channel_id", required=True)
@click.pass_context
def channel_get(ctx, channel_id):
    """Get details for a specific channel."""
    try:
        client = _get_client()
        channel = client.get_channel(channel_id)
        _output_result(channel)
    except APIError as e:
        if e.status_code == 404:
            click.echo(f"Channel not found: {channel_id}", err=True)
            sys.exit(1)
        else:
            _handle_api_error(e)


@click.command("list")
@click.pass_context
def event_list(ctx):
    """List events."""
    try:
        client = _get_client()
        events = client.list_events()
        _output_result(events)
    except APIError as e:
        _handle_api_error(e)


@click.group()
@click.option("--json", is_flag=True, help="Output results in JSON format")
@click.pass_context
def cli(ctx, json):
    """CLI for Restream.io API"""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json


@click.group()
def channel():
    """Channel management commands."""
    pass


@click.group()
def event():
    """Event management commands."""
    pass


# Add commands to groups
channel.add_command(channel_list)
channel.add_command(channel_get)
event.add_command(event_list)

# Add commands to main CLI
cli.add_command(login)
cli.add_command(profile)
cli.add_command(channel)
cli.add_command(event)
cli.add_command(version_cmd, name="version")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":  # allow direct execution for tests
    main()
