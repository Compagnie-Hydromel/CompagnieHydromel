from libs.format import PythonFormatter
from libs.log import Log


def run():
    formatter = PythonFormatter()
    exit_code = 0
    for file in formatter.format():
        exit_code = 1
        Log.warning(f"Formatted: {file}")
    raise SystemExit(exit_code)
