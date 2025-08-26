from libs.exception.music.music_exception import MusicException


class NothingLeftInBackQueueException(MusicException):
    def __init__(self, message="There are no more tracks left in the back queue."):
        super().__init__(message)
