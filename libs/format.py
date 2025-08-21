import os
import subprocess


class PythonFormatter:
    def __init__(self, directories=["libs", "cogs", "test"], files=["bot.py"]):
        self.directories = directories
        self.files = files

    def _get_python_files(self):
        for directory in self.directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(".py"):
                        yield os.path.join(root, file)

        for file in self.files:
            if os.path.isfile(file) and file.endswith(".py"):
                yield file

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
