import traceback
from libs.config import Config
from libs.exception.bot_exception import BotException
from libs.log import Log, LogType

class Handler:
    def __init__(self) -> None:
        self.__config = Config()
        self.__error_exception = self.__config.value["exception_response"]
        
    def response_handler(self, exception: Exception) -> str:
        if isinstance(exception, BotException):
            match(str(exception)):
                case "WallpaperNotExistException":
                    return self.__error_exception["wallpaper_not_exist"]
                case "WallpaperNotPossededException":
                    return self.__error_exception["wallpaper_not_posseded"]
                case "ColorNotCorrectException":
                    return self.__error_exception["color_not_correct"]
                case "NotEnougtSmartpointException":
                    return self.__error_exception["not_enougt_smartpoint"]
                case "WallpaperAlreadyPossededException":
                    return self.__error_exception["wallpaper_already_posseded"]
                case "WallpaperCannotBeBuyedException":
                    return self.__error_exception["wallpaper_cannot_be_buyed"]
                case "WallpaperIsNotDownloadableException":
                    return self.__error_exception["unable_to_download_image"]
                case "WallpaperIsNotDownloadableException":
                    Log(traceback.format_exc(), LogType.ERROR)
                    return self.__error_exception["unable_to_download_image"]
                case _:
                    Log(traceback.format_exc(), LogType.ERROR)
                    return self.__error_exception["default"]
        else:
            return self.__error_exception["default"]