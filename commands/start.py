import subprocess

from libs.log import Log


def run():
    Log.info("Starting all bots")

    processes = [
        subprocess.Popen(["python3", "bot.py", command])
        for command in ("barman", "menestrel", "archiveuse", "webserver")
    ]

    for process in processes:
        process.wait()
