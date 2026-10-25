import subprocess


def run():
    test_process = subprocess.run(
        ["python3", "-m", "unittest", "discover", "-s", "tests"]
    )
    raise SystemExit(test_process.returncode)
