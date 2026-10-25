from MIWOS.db import migrate

from libs.log import Log


def run():
    migrate()
    Log.info("Migrations completed")
