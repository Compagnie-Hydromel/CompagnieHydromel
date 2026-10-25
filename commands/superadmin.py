import argparse
import re
import sys

from libs.databases.models.user import User
from libs.log import Log


def discord_id(value):
    if not re.fullmatch(r"[1-9][0-9]{16,19}", value) or int(value) > 2 ** 64 - 1:
        raise argparse.ArgumentTypeError("Provide a valid Discord user ID")
    return value


def run():
    parser = argparse.ArgumentParser(
        prog="python3 bot.py superadmin",
        description="Manage global application super administrators by Discord ID.")
    actions = parser.add_subparsers(dest="action", required=True)
    for action in ("add", "remove"):
        command = actions.add_parser(action)
        command.add_argument("discord_id", type=discord_id)
    actions.add_parser("list")
    arguments = parser.parse_args(sys.argv[2:])

    if arguments.action == "list":
        users = list(User.where(is_superadmin=True))
        if not users:
            print("No super administrators configured.")
        for user in users:
            print(user.discord_id)
        return

    user = User.whereFirst(discord_id=arguments.discord_id)
    enabled = arguments.action == "add"
    if user is None:
        if not enabled:
            print(f"User {arguments.discord_id} is not a super administrator.")
            return
        user = User(discord_id=arguments.discord_id)

    if bool(user.is_superadmin) == enabled:
        print(f"User {arguments.discord_id} is already " +
              ("a super administrator." if enabled else "not a super administrator."))
        return

    user.is_superadmin = enabled
    user.saveOrFail()
    Log.info(
        f"Super administrator {'added' if enabled else 'removed'}: {arguments.discord_id}")
