from libs.exception.bot_exception import BotException


class MusicException(BotException):
    def __init__(self, message="An error occurred in the music module."):
        super().__init__(message)
