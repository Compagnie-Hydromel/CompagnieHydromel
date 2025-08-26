from libs.exception.music.music_exception import MusicException


class NoResultsFoundException(MusicException):
    def __init__(self, message="No results found for the given query."):
        super().__init__(message)
