from libs.format import PythonFormatter
from libs.log import Log


def run():
    formatter = PythonFormatter()
    exit_code = 0
    for file in formatter.check():
        exit_code = 1
        Log.warning(f"Needs formatting: {file}")
    raise SystemExit(exit_code)
