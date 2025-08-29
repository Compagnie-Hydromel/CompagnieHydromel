from libs.exception.music.music_exception import MusicException


class NoMusicPlayingException(MusicException):
    def __init__(self, message="No music is currently playing in this channel."):
        super().__init__(message)
