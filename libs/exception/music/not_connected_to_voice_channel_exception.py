from libs.exception.music.music_exception import MusicException


class NotConnectedToVoiceChannelException(MusicException):
    def __init__(self, message="You must be connected to a voice channel to use this command."):
        super().__init__(message)
