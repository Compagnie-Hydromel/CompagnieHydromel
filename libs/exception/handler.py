from libs.config import Config
from libs.exception.bot_exception import BotException

class Handler:
    def __init__(self) -> None:
        self.__config = Config()
        
    def response_handler(self, exception: Exception) -> str:
        if isinstance(exception, BotException):
            match(str(exception)):
                case "NotConnectedToVoiceChannelException":
                    pass
                case "NotPlayingMusicException":
                    pass
                case "NothingLeftInPreviousQueueException":
                    return self.__config.value["exception_response"]["not_connected_to_voice_channel"]
                case _:
                    return self.__config.value["exception_response"]["default"]
        else:
            return self.__config.value["exception_response"]["default"]