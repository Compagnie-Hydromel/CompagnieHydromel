from libs.exception.music.music_exception import MusicException


class AlreadyPlayingException(MusicException):
    def __init__(self, message="A track is already playing in this channel."):
        super().__init__(message)
