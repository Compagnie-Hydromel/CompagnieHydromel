from libs.exception.music.music_exception import MusicException


class NoPlayingInstanceException(MusicException):
    def __init__(self, message="No music instance is currently playing in this channel."):
        super().__init__(message)
