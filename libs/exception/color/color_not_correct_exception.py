from libs.exception.bot_exception import BotException


class ColorNotCorrectException(BotException):
    def __init__(self, message="Color is not correct. Please use a valid color code."):
        super().__init__(message)
