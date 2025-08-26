from libs.exception.music.music_exception import MusicException


class NothingLeftInQueueException(MusicException):
    def __init__(self, message="There are no more tracks left in the queue."):
        super().__init__(message)
