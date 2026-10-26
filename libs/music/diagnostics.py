import os
import re
import traceback

from libs.exception.bot_exception import BotException


def safe_music_error(error):
    message = error.message if isinstance(error, BotException) else str(error)
    for key, value in os.environ.items():
        if value and any(part in key.upper() for part in ("TOKEN", "PASSWORD", "SECRET")):
            message = message.replace(value, "[secret]")
    message = re.sub(r"https?://[^\s<>\"']+", "[stream URL]", message)
    message = re.sub(r"(?i)(bearer\s+)\S+", r"\1[secret]", message)
    message = re.sub(r"(?im)(cookie|authorization)\s*:[^\r\n]*", r"\1: [secret]", message)
    return message[:2000]


def music_diagnostic(error, stage):
    # No locals or source lines: only sanitized messages and stack locations.
    frames = traceback.extract_tb(error.__traceback__)
    locations = "\n".join(f"  {frame.filename}:{frame.lineno} in {frame.name}" for frame in frames)
    return f"Music failure [{stage}] {type(error).__name__}: {safe_music_error(error)}\n{locations}"
