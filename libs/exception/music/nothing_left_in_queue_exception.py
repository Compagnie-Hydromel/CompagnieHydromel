from libs.exception.music.music_exception import MusicException

class NothingLeftInQueueException(MusicException):
    """Exception raised when there is nothing left in the queue."""

    pass