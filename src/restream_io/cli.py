import json
import sys
from importlib.metadata import version

import attrs
import click

from .api import RestreamClient
from .auth import perform_login
from .errors import APIError, AuthenticationError


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


def _get_client():
    """Get a configured RestreamClient instance."""
    try:
        return RestreamClient.from_config()
    except AuthenticationError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        print("Please run 'restream.io login' first.", file=sys.stderr)
        sys.exit(1)


def _handle_api_error(e: APIError):
    """Handle API errors consistently."""
    print(f"API error: {e}", file=sys.stderr)
    sys.exit(1)


@click.pass_context
def _output_result(ctx, data):
    """Output result in the appropriate format."""
    # Convert attrs objects to dict for JSON serialization
    serializable_data = _attrs_to_dict(data)

    # Check if --json flag was passed at the root level
    json_output = ctx.find_root().params.get("json", False)

    if json_output:
        print(json.dumps(serializable_data, indent=2, default=str))
    else:
        print(
            json.dumps(serializable_data, indent=2, default=str)
        )  # For now, always use JSON format


@click.command()
def version_cmd():
    """Show version information."""
    print(version("restream.io"))


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
            print("Login failed", file=sys.stderr)
            sys.exit(1)
    except AuthenticationError as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nLogin cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during login: {e}", file=sys.stderr)
        sys.exit(1)


@click.command()
def profile():
    """Fetch user profile from Restream API."""
    try:
        client = _get_client()
        profile = client.get_profile()
        _output_result(profile)
    except APIError as e:
        _handle_api_error(e)


@click.command("list")
def channel_list():
    """List channels."""
    try:
        client = _get_client()
        channels = client.list_channels()
        _output_result(channels)
    except APIError as e:
        _handle_api_error(e)


@click.command("get")
@click.argument("channel_id", required=True)
def channel_get(channel_id):
    """Get details for a specific channel."""
    try:
        client = _get_client()
        channel = client.get_channel(channel_id)
        _output_result(channel)
    except APIError as e:
        _handle_api_error(e)


@click.command("list")
def event_list():
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
