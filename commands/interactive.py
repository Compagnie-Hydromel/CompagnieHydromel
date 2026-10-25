import code

from libs.databases.bootstrap import load_all_models
from libs.log import Log


def run():
    Log.info("Starting interactive mode")
    code.interact(local=load_all_models())
