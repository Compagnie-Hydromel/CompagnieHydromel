import sys

from MIWOS.db import rollback

from libs.log import Log


def run():
    rollback(depth=int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    Log.info("Rollback completed")
