from libs.exception.bot_exception import BotException


class ImageNotDownloadable(BotException):
    def __init__(self, message="The image could not be downloaded. Please check the URL."):
        super().__init__(message)
