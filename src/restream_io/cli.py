import argparse
import json
import sys
from importlib.metadata import version

import attrs

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


def _output_result(data, json_output=False):
    """Output result in the appropriate format."""
    # Convert attrs objects to dict for JSON serialization
    serializable_data = _attrs_to_dict(data)

    if json_output:
        print(json.dumps(serializable_data, indent=2, default=str))
    else:
        print(
            json.dumps(serializable_data, indent=2, default=str)
        )  # For now, always use JSON format


def cmd_version(args):
    print(version("restream.io"))


def cmd_login(args):
    """Perform OAuth2 login flow."""
    try:
        success = perform_login(redirect_port=args.port)
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


def cmd_profile(args):
    """Fetch user profile from Restream API."""
    try:
        client = _get_client()
        profile = client.get_profile()
        _output_result(profile, getattr(args, "json", False))
    except APIError as e:
        _handle_api_error(e)


def cmd_channel_list(args):
    """List channels."""
    try:
        client = _get_client()
        channels = client.list_channels()
        _output_result(channels, getattr(args, "json", False))
    except APIError as e:
        _handle_api_error(e)


def cmd_channel_get(args):
    """Get details for a specific channel."""
    if not args.id:
        print("channel get requires an ID", file=sys.stderr)
        sys.exit(1)

    try:
        client = _get_client()
        channel = client.get_channel(args.id)
        _output_result(channel, getattr(args, "json", False))
    except APIError as e:
        _handle_api_error(e)


def cmd_event_list(args):
    """List events."""
    try:
        client = _get_client()
        events = client.list_events()
        _output_result(events, getattr(args, "json", False))
    except APIError as e:
        _handle_api_error(e)


def main():
    parser = argparse.ArgumentParser(
        prog="restream.io", description="CLI for Restream.io API"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    sub = parser.add_subparsers(dest="command")

    login_parser = sub.add_parser("login")
    login_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=12000,
        help="Port for local OAuth callback server (default: 12000)",
    )
    login_parser.set_defaults(func=cmd_login)

    profile_parser = sub.add_parser("profile")
    profile_parser.set_defaults(func=cmd_profile)

    channel = sub.add_parser("channel")
    channel_sub = channel.add_subparsers(dest="subcmd")

    channel_list_parser = channel_sub.add_parser("list")
    channel_list_parser.set_defaults(func=cmd_channel_list)

    ch_get = channel_sub.add_parser("get")
    ch_get.add_argument("id", help="Channel ID")
    ch_get.set_defaults(func=cmd_channel_get)

    event = sub.add_parser("event")
    event_sub = event.add_subparsers(dest="subcmd")

    event_list_parser = event_sub.add_parser("list")
    event_list_parser.set_defaults(func=cmd_event_list)

    version_parser = sub.add_parser("version")
    version_parser.set_defaults(func=cmd_version)

    args = parser.parse_args()
    if not hasattr(args, "func") or args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":  # allow direct execution for tests
    main()
