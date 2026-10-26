import os
import shlex
import subprocess
import threading

import discord

from libs.exception.bot_exception import BotException


class StreamPlaybackError(BotException):
    def __init__(self):
        super().__init__("La source refuse le flux audio ou celui-ci est indisponible (par exemple HTTP 403). Essayez un autre titre ou une autre source.")


def stream_options(headers):
    # yt-dlp's signed URLs may require the same User-Agent/Referer as extraction.
    # Quote as one argv value, and refuse header injection from extractor data.
    lines = []
    for name, value in headers.items():
        if (isinstance(name, str) and isinstance(value, str)
                and name and all(char.isascii() and (char.isalnum() or char == "-") for char in name)
                and not any(char in value for char in ("\r", "\n", "\0"))):
            lines.append(f"{name}: {value}\r\n")
    options = "-nostdin -protocol_whitelist https,http,tcp,tls,crypto -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -rw_timeout 15000000"
    if lines:
        options += " -headers " + shlex.quote("".join(lines))
    return options


class StreamingAudio(discord.FFmpegPCMAudio):
    """Check actual decoded audio before reporting playback as successful."""

    def __init__(self, stream, headers):
        self._cleanup_lock = threading.Lock()
        self._first_frame = None
        # Do not print signed stream URLs (including IPs/tokens) on decoder errors.
        # Pycord expects a file object here, not subprocess.DEVNULL's integer:
        # passing the integer creates a pipe-reader thread that calls int.write.
        self._error_sink = open(os.devnull, "wb")
        try:
            super().__init__(stream, before_options=stream_options(
                headers), options="-vn", stderr=self._error_sink)
        except BaseException:
            self._error_sink.close()
            raise

    def _read_frame(self):
        process = self._process
        frame = super().read()
        if not frame:
            try:
                code = process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                raise StreamPlaybackError() from None
            if code != 0:
                raise StreamPlaybackError()
        return frame

    def prepare(self):
        self._first_frame = self._read_frame()
        if not self._first_frame:
            raise StreamPlaybackError()

    def read(self):
        if self._first_frame is not None:
            frame, self._first_frame = self._first_frame, None
            return frame
        return self._read_frame()

    def cleanup(self):
        # Startup cancellation and Discord's audio thread can both clean up.
        # Avoid communicate(): it competes with the PCM reader for stdout.
        with self._cleanup_lock:
            process = getattr(self, "_process", None)
            try:
                if not process:
                    return
                if process.poll() is None:
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
                process.wait()
                if process.stdout:
                    process.stdout.close()
                self._process = self._stdout = self._stdin = self._stderr = discord.utils.MISSING
            finally:
                sink = getattr(self, "_error_sink", None)
                if sink is not None:
                    sink.close()
