import os
import subprocess
import sys


class PythonFormatter:
    def __init__(self, directories=["libs", "cogs", "test"]):
        self.directories = directories

    def _get_python_files(self):
        for directory in self.directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        yield os.path.join(root, file)

    def format(self):
        for file_path in self._get_python_files():
            result = subprocess.run(["autopep8", "--in-place", "--exit-code",
                                     file_path], capture_output=True)
            if result.returncode == 2:  # Exit code 2 indicates file was modified
                yield file_path

    def check(self):
        for file_path in self._get_python_files():
            result = subprocess.run(
                ["autopep8", "--diff", file_path], capture_output=True)
            if result.stdout:
                yield file_path


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "format":
        formatter = PythonFormatter()
        for file in formatter.format():
            print(f"Formatted: {file}")
    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        formatter = PythonFormatter()
        exit_code = 0
        for file in formatter.check():
            print(f"Needs formatting: {file}")
            exit_code = 1

        if exit_code == 1:
            sys.exit(exit_code)
    else:
        print("Usage: python format.py [format|check]")
