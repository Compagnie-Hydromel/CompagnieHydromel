import importlib
import sys

from dotenv import load_dotenv

from libs.databases.bootstrap import init, load_all_models
from libs.log import Log


COMMANDS = {
    "webserver": "webserver",
    "barman": "barman",
    "menestrel": "menestrel",
    "archiveuse": "archiveuse",
    "interactive": "interactive",
    "migrate": "migrate",
    "rollback": "rollback",
    "format": "format",
    "check-format": "check_format",
    "test": "test",
    "superadmin": "superadmin",
    "localize-images": "localize_images",
}


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        from commands.start import run

        run()
        return

    init()
    load_all_models()

    module_name = COMMANDS.get(sys.argv[1])
    if module_name is None:
        Log.error("Subcommand not found")
        return

    command = importlib.import_module(f"commands.{module_name}")
    command.run()
