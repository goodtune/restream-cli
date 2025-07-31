import argparse
import sys
from importlib.metadata import version


def cmd_version(args):
    print(version("restream.io"))


def cmd_login(args):
    print(
        "[stub] login called - implement OAuth2 authorization code flow with local redirect listener."
    )


def cmd_profile(args):
    print("[stub] profile called - fetch user profile from Restream API.")


def cmd_channel_list(args):
    print("[stub] channel list called - list channels.")


def cmd_channel_get(args):
    if not args.id:
        print("channel get requires an ID", file=sys.stderr)
        sys.exit(1)
    print(f"[stub] channel get called for id={args.id}")


def cmd_event_list(args):
    print("[stub] event list called - list events.")


def main():
    parser = argparse.ArgumentParser(
        prog="restream.io", description="CLI for Restream.io API"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("login").set_defaults(func=cmd_login)
    sub.add_parser("profile").set_defaults(func=cmd_profile)

    channel = sub.add_parser("channel")
    channel_sub = channel.add_subparsers(dest="subcmd")
    channel_sub.add_parser("list").set_defaults(func=cmd_channel_list)
    ch_get = channel_sub.add_parser("get")
    ch_get.add_argument("id", help="Channel ID")
    ch_get.set_defaults(func=cmd_channel_get)

    event = sub.add_parser("event")
    event_sub = event.add_subparsers(dest="subcmd")
    event_sub.add_parser("list").set_defaults(func=cmd_event_list)

    sub.add_parser("version").set_defaults(func=cmd_version)

    args = parser.parse_args()
    if not hasattr(args, "func") or args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":  # allow direct execution for tests
    main()
